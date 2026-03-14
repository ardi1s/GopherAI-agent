package session

import (
	"GopherAI/common/aihelper"
	"GopherAI/common/code"
	"context"
	"fmt"
	"log"
	"net/http"
	"strings"
)

// callRAGSearch 调用 RAG 检索方法
func callRAGSearch(helper *aihelper.AIHelper, ctx context.Context, query string) (string, error) {
	if helper == nil {
		return "", fmt.Errorf("helper is nil")
	}
	
	log.Printf("[RAG] Calling Search method, modelType: %s", (*helper).GetModelType())
	
	// 现在可以直接调用 AIHelper 的 Search 方法
	// AIHelper 会通过类型断言委托给底层模型
	return (*helper).Search(ctx, query)
}

// callMCPCallTool 调用 MCP 工具方法
func callMCPCallTool(helper *aihelper.AIHelper, ctx context.Context, toolName string, args map[string]interface{}) (string, error) {
	if helper == nil {
		return "", fmt.Errorf("helper is nil")
	}
	
	log.Printf("[MCP] Calling CallTool method, modelType: %s", (*helper).GetModelType())
	
	// 现在可以直接调用 AIHelper 的 CallTool 方法
	// AIHelper 会通过类型断言委托给底层模型
	return (*helper).CallTool(ctx, toolName, args)
}

// executeRAGMCPWorkflow 执行 RAG + MCP 联动工作流
func executeRAGMCPWorkflow(userName, sessionID, userQuestion, modelType string, writer http.ResponseWriter, flusher http.Flusher) code.Code {
	log.Printf("[Workflow] Executing RAG+MCP workflow for: %s", userQuestion)
	
	manager := aihelper.GetGlobalManager()
	config := map[string]interface{}{
		"apiKey":   "your-api-key",
		"username": userName,
	}
	
	ctx := context.Background()
	
	// 1. RAG 检索
	log.Printf("[Workflow] Step 1: RAG retrieval...")
	ragHelper, err := manager.GetOrCreateAIHelper(userName, sessionID, "2", config)
	if err != nil {
		log.Println("[Workflow] Create RAG helper error:", err)
		return code.AIModelFail
	}
	
	// 调用 RAG Search 方法
	ragResult, err := callRAGSearch(ragHelper, ctx, userQuestion)
	if err != nil {
		log.Printf("[Workflow] RAG search error: %v", err)
		ragResult = "[RAG 检索失败]"
	} else {
		log.Printf("[Workflow] RAG search completed, result length: %d", len(ragResult))
	}
	
	// 2. MCP 调用工具
	log.Printf("[Workflow] Step 2: MCP tool calling...")
	mcpHelper, err := manager.GetOrCreateAIHelper(userName, sessionID, "3", config)
	if err != nil {
		log.Println("[Workflow] Create MCP helper error:", err)
		return code.AIModelFail
	}
	
	// 判断用什么 MCP 工具
	toolName := "get_weather"
	toolArgs := map[string]interface{}{"city": "北京"} // 默认北京
	
	if strings.Contains(userQuestion, "上海") {
		toolArgs["city"] = "上海"
	} else if strings.Contains(userQuestion, "广州") {
		toolArgs["city"] = "广州"
	} else if strings.Contains(userQuestion, "深圳") {
		toolArgs["city"] = "深圳"
	}
	
	mcpResult, err := callMCPCallTool(mcpHelper, ctx, toolName, toolArgs)
	if err != nil {
		log.Printf("[Workflow] MCP tool call error: %v", err)
		mcpResult = "[MCP 工具调用失败]"
	} else {
		log.Printf("[Workflow] MCP tool call completed, result: %s", mcpResult)
	}
	
	// 3. 综合 RAG + MCP 结果，用普通模型生成回答
	log.Printf("[Workflow] Step 3: Generating final response...")
	chatHelper, err := manager.GetOrCreateAIHelper(userName, sessionID, "1", config)
	if err != nil {
		log.Println("[Workflow] Create Chat helper error:", err)
		return code.AIModelFail
	}
	
	// 4. 构造增强的 prompt
	enhancedPrompt := fmt.Sprintf(`请基于以下信息回答用户问题：

【相关知识】（从文档库检索）
%s

【工具执行结果】
%s

【用户问题】
%s

请综合以上信息，给出准确、有用的回答。如果 RAG 检索结果或工具结果与问题无关，请忽略无关部分，直接回答用户问题。`, ragResult, mcpResult, userQuestion)
	
	// 5. 流式输出
	cb := func(msg string) {
		log.Printf("[SSE] Sending chunk: %s (len=%d)\n", msg, len(msg))
		_, err := writer.Write([]byte("data: " + msg + "\n\n"))
		if err != nil {
			log.Println("[SSE] Write error:", err)
			return
		}
		flusher.Flush()
		log.Println("[SSE] Flushed")
	}
	
	_, err_ := chatHelper.StreamResponse(userName, ctx, cb, enhancedPrompt)
	if err_ != nil {
		log.Println("executeRAGMCPWorkflow StreamResponse error:", err_)
		return code.AIModelFail
	}
	
	_, err = writer.Write([]byte("data: [DONE]\n\n"))
	if err != nil {
		log.Println("executeRAGMCPWorkflow write DONE error:", err)
		return code.AIModelFail
	}
	flusher.Flush()
	
	log.Println("[Workflow] RAG+MCP workflow completed")
	return code.CodeSuccess
}
