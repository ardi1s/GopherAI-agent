package benchmark

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"
)

// LoadTestConfig 压测配置
type LoadTestConfig struct {
	BaseURL         string
	ConcurrentUsers int
	Duration        time.Duration
	RampUpTime      time.Duration
}

// LoadTestResult 压测结果
type LoadTestResult struct {
	TotalRequests      int64
	SuccessRequests    int64
	FailedRequests     int64
	TotalDuration      time.Duration
	AvgResponseTime    time.Duration
	MinResponseTime    time.Duration
	MaxResponseTime    time.Duration
	RequestsPerSecond  float64
	ResponseTimes      []time.Duration
	StatusCodeCounts   map[int]int64
}

// HTTPClient HTTP客户端
type HTTPClient struct {
	client    *http.Client
	baseURL   string
	jwtToken  string
}

// NewHTTPClient 创建新的HTTP客户端
func NewHTTPClient(baseURL string) *HTTPClient {
	return &HTTPClient{
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
		baseURL: baseURL,
	}
}

// SetJWTToken 设置JWT Token
func (c *HTTPClient) SetJWTToken(token string) {
	c.jwtToken = token
}

// DoRequest 发送HTTP请求
func (c *HTTPClient) DoRequest(method, path string, body []byte) (*http.Response, time.Duration, error) {
	url := c.baseURL + path
	
	var bodyReader io.Reader
	if body != nil {
		bodyReader = bytes.NewReader(body)
	}
	
	req, err := http.NewRequest(method, url, bodyReader)
	if err != nil {
		return nil, 0, err
	}
	
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	
	if c.jwtToken != "" {
		req.Header.Set("Authorization", "Bearer "+c.jwtToken)
	}
	
	start := time.Now()
	resp, err := c.client.Do(req)
	duration := time.Since(start)
	
	if err != nil {
		return nil, duration, err
	}
	
	return resp, duration, nil
}

// RunLoadTest 执行压测
func RunLoadTest(config LoadTestConfig, testFunc func(*HTTPClient) error) *LoadTestResult {
	result := &LoadTestResult{
		MinResponseTime:  time.Hour,
		MaxResponseTime:  0,
		StatusCodeCounts: make(map[int]int64),
		ResponseTimes:    make([]time.Duration, 0),
	}
	
	var wg sync.WaitGroup
	requestChan := make(chan struct{}, config.ConcurrentUsers)
	resultChan := make(chan struct {
		success        bool
		duration       time.Duration
		statusCode     int
	}, config.ConcurrentUsers*100)
	
	// 启动结果收集器
	go func() {
		for r := range resultChan {
			result.TotalRequests++
			if r.success {
				result.SuccessRequests++
				result.ResponseTimes = append(result.ResponseTimes, r.duration)
				
				if r.duration < result.MinResponseTime {
					result.MinResponseTime = r.duration
				}
				if r.duration > result.MaxResponseTime {
					result.MaxResponseTime = r.duration
				}
			} else {
				result.FailedRequests++
			}
			result.StatusCodeCounts[r.statusCode]++
		}
	}()
	
	// 启动并发用户
	startTime := time.Now()
	for i := 0; i < config.ConcurrentUsers; i++ {
		wg.Add(1)
		go func(userID int) {
			defer wg.Done()
			
			client := NewHTTPClient(config.BaseURL)
			
			for {
				select {
				case <-time.After(config.Duration):
					return
				case requestChan <- struct{}{}:
					start := time.Now()
					err := testFunc(client)
					duration := time.Since(start)
					
					statusCode := 200
					success := err == nil
					if !success {
						statusCode = 0
					}
					
					resultChan <- struct {
						success    bool
						duration   time.Duration
						statusCode int
					}{success, duration, statusCode}
					
					<-requestChan
				}
				
				if time.Since(startTime) >= config.Duration {
					return
				}
			}
		}(i)
		
		// 渐进式增加并发用户
		if config.RampUpTime > 0 {
			time.Sleep(config.RampUpTime / time.Duration(config.ConcurrentUsers))
		}
	}
	
	wg.Wait()
	close(resultChan)
	time.Sleep(100 * time.Millisecond) // 等待结果收集完成
	
	result.TotalDuration = time.Since(startTime)
	
	// 计算平均响应时间
	if len(result.ResponseTimes) > 0 {
		var totalDuration time.Duration
		for _, d := range result.ResponseTimes {
			totalDuration += d
		}
		result.AvgResponseTime = totalDuration / time.Duration(len(result.ResponseTimes))
	}
	
	result.RequestsPerSecond = float64(result.TotalRequests) / result.TotalDuration.Seconds()
	
	return result
}

// PrintLoadTestResult 打印压测结果
func PrintLoadTestResult(result *LoadTestResult) {
	fmt.Printf("\n========== 压测结果报告 ==========\n")
	fmt.Printf("总请求数: %d\n", result.TotalRequests)
	fmt.Printf("成功请求: %d\n", result.SuccessRequests)
	fmt.Printf("失败请求: %d\n", result.FailedRequests)
	fmt.Printf("成功率: %.2f%%\n", float64(result.SuccessRequests)/float64(result.TotalRequests)*100)
	fmt.Printf("\n响应时间统计:\n")
	fmt.Printf("  平均响应时间: %v\n", result.AvgResponseTime)
	fmt.Printf("  最小响应时间: %v\n", result.MinResponseTime)
	fmt.Printf("  最大响应时间: %v\n", result.MaxResponseTime)
	fmt.Printf("\n吞吐量:\n")
	fmt.Printf("  QPS: %.2f\n", result.RequestsPerSecond)
	fmt.Printf("\n状态码分布:\n")
	for code, count := range result.StatusCodeCounts {
		fmt.Printf("  %d: %d (%.2f%%)\n", code, count, float64(count)/float64(result.TotalRequests)*100)
	}
	fmt.Printf("==================================\n\n")
}

// LoadTestUserLogin 测试用户登录接口
func LoadTestUserLogin(client *HTTPClient) error {
	loginData := map[string]string{
		"email":    "test@example.com",
		"password": "test123",
	}
	jsonData, _ := json.Marshal(loginData)
	
	resp, _, err := client.DoRequest("POST", "/api/v1/user/login", jsonData)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	
	return nil
}

// LoadTestGetSessions 测试获取会话列表接口
func LoadTestGetSessions(client *HTTPClient) error {
	resp, _, err := client.DoRequest("GET", "/api/v1/AI/chat/sessions", nil)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusUnauthorized {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	
	return nil
}

// LoadTestChatHistory 测试获取聊天历史接口
func LoadTestChatHistory(client *HTTPClient) error {
	historyData := map[string]string{
		"sessionId": "test-session-id",
	}
	jsonData, _ := json.Marshal(historyData)
	
	resp, _, err := client.DoRequest("POST", "/api/v1/AI/chat/history", jsonData)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusUnauthorized {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	
	return nil
}
