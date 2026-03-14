package intent

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"github.com/sashabaranov/go-openai"
)

type IntentType string

const (
	IntentChat IntentType = "chat"
	IntentRAG  IntentType = "rag"
	IntentMCP  IntentType = "mcp"
)

type MCPTool string

const (
	ToolWeather MCPTool = "weather"
	ToolTime    MCPTool = "time"
	ToolNone    MCPTool = "none"
)

type IntentResult struct {
	Type IntentType `json:"type"`
	Tool MCPTool    `json:"tool,omitempty"`
}

// IntentRecognizer 意图识别器
type IntentRecognizer struct {
	client *openai.Client
	model  string
}

// NewIntentRecognizer 创建意图识别器
func NewIntentRecognizer(apiKey, baseURL, model string) *IntentRecognizer {
	config := openai.DefaultConfig(apiKey)
	if baseURL != "" {
		config.BaseURL = baseURL
	}
	
	client := openai.NewClientWithConfig(config)
	
	return &IntentRecognizer{
		client: client,
		model:  model,
	}
}

// Recognize 识别用户意图
func (r *IntentRecognizer) Recognize(ctx context.Context, question string) (*IntentResult, error) {
	// 简单规则匹配，减少 LLM 调用
	intent := r.matchByRules(question)
	if intent != nil {
		return intent, nil
	}
	
	// 规则匹配不到，用 LLM 识别
	return r.recognizeWithLLM(ctx, question)
}

// matchByRules 通过规则快速匹配常见意图
func (r *IntentRecognizer) matchByRules(question string) *IntentResult {
	question = strings.ToLower(question)
	
	// RAG 相关关键词
	ragKeywords := []string{"文档", "文件", "上传", "知识库", "资料", "文章", "pdf", "word", "txt", "md"}
	for _, keyword := range ragKeywords {
		if strings.Contains(question, keyword) {
			return &IntentResult{Type: IntentRAG}
		}
	}
	
	// 天气相关
	weatherKeywords := []string{"天气", "气温", "下雨", "晴天", "阴天", "下雪", "刮风"}
	for _, keyword := range weatherKeywords {
		if strings.Contains(question, keyword) {
			return &IntentResult{Type: IntentMCP, Tool: ToolWeather}
		}
	}
	
	// 时间相关
	timeKeywords := []string{"几点", "时间", "日期", "星期", "号", "年", "月"}
	for _, keyword := range timeKeywords {
		if strings.Contains(question, keyword) {
			return &IntentResult{Type: IntentMCP, Tool: ToolTime}
		}
	}
	
	return nil
}

// recognizeWithLLM 使用 LLM 识别意图
func (r *IntentRecognizer) recognizeWithLLM(ctx context.Context, question string) (*IntentResult, error) {
	prompt := fmt.Sprintf(`你是一个意图识别助手。请分析用户问题，判断需要什么服务。

可选服务类型：
- chat: 普通聊天、问答、创作、翻译、写代码等
- rag: 查询文档、文件内容、知识库、资料等
- mcp: 查询实时信息（天气、时间、日期、新闻等）

如果是 mcp 类型，请识别需要什么工具：
- weather: 天气相关
- time: 时间、日期相关
- none: 其他

只返回 JSON 格式，不要其他内容：
{"type": "chat|rag|mcp", "tool": "weather|time|none"}

用户问题：%s

意图：`, question)

	resp, err := r.client.CreateChatCompletion(ctx, openai.ChatCompletionRequest{
		Model: r.model,
		Messages: []openai.ChatCompletionMessage{
			{
				Role:    openai.ChatMessageRoleUser,
				Content: prompt,
			},
		},
		MaxTokens:   50,
		Temperature: 0.1, // 低温度，让输出更稳定
	})
	
	if err != nil {
		log.Printf("IntentRecognizer LLM error: %v", err)
		// LLM 调用失败，降级为 chat
		return &IntentResult{Type: IntentChat}, nil
	}
	
	if len(resp.Choices) == 0 {
		return &IntentResult{Type: IntentChat}, nil
	}
	
	content := resp.Choices[0].Message.Content
	return r.parseIntent(content)
}

// parseIntent 解析 LLM 返回的意图
func (r *IntentRecognizer) parseIntent(content string) (*IntentResult, error) {
	// 清理可能的 markdown 标记
	content = strings.TrimSpace(content)
	content = strings.TrimPrefix(content, "```json")
	content = strings.TrimPrefix(content, "```")
	content = strings.TrimSuffix(content, "```")
	content = strings.TrimSpace(content)
	
	var result IntentResult
	err := json.Unmarshal([]byte(content), &result)
	if err != nil {
		log.Printf("Parse intent JSON error: %v, content: %s", err, content)
		// 解析失败，降级为 chat
		return &IntentResult{Type: IntentChat}, nil
	}
	
	// 验证意图类型
	if result.Type == "" {
		result.Type = IntentChat
	}
	
	// 验证 tool 字段
	if result.Type != IntentMCP {
		result.Tool = ToolNone
	} else if result.Tool == "" {
		result.Tool = ToolNone
	}
	
	return &result, nil
}
