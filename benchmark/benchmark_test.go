package benchmark

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"GopherAI/common/redis"
	"GopherAI/config"
	"GopherAI/router"
)

var testCtx = context.Background()

// 初始化测试环境
func init() {
	config.GetConfig()
	redis.Init()
}

// BenchmarkGetUserSessions 测试获取用户会话列表接口性能
func BenchmarkGetUserSessions(b *testing.B) {
	ginRouter := router.InitRouter()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/AI/chat/sessions", nil)
		req.Header.Set("Authorization", "Bearer test_token")
		ginRouter.ServeHTTP(w, req)
	}
}

// BenchmarkRedisSet 测试Redis写入性能
func BenchmarkRedisSet(b *testing.B) {
	redis.Init()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("benchmark:key:%d", i)
		redis.Rdb.Set(testCtx, key, "test_value", time.Minute)
	}
}

// BenchmarkRedisGet 测试Redis读取性能
func BenchmarkRedisGet(b *testing.B) {
	redis.Init()
	// 预先设置一些数据
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("benchmark:key:%d", i)
		redis.Rdb.Set(testCtx, key, "test_value", time.Minute)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("benchmark:key:%d", i%1000)
		redis.Rdb.Get(testCtx, key)
	}
}

// BenchmarkRedisCaptcha 测试验证码缓存性能
func BenchmarkRedisCaptcha(b *testing.B) {
	redis.Init()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		email := fmt.Sprintf("test%d@example.com", i)
		redis.SetCaptchaForEmail(email, "123456")
	}
}

// BenchmarkConcurrentRequests 测试并发请求性能
func BenchmarkConcurrentRequests(b *testing.B) {
	ginRouter := router.InitRouter()

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/api/v1/AI/chat/sessions", nil)
			req.Header.Set("Authorization", "Bearer test_token")
			ginRouter.ServeHTTP(w, req)
		}
	})
}

// 性能测试报告结构
type BenchmarkReport struct {
	TestName       string        `json:"test_name"`
	Iterations     int           `json:"iterations"`
	Duration       time.Duration `json:"duration"`
	NsPerOperation int64         `json:"ns_per_operation"`
	AllocPerOp     int64         `json:"alloc_per_op"`
	AllocsPerOp    int64         `json:"allocs_per_op"`
	QPS            float64       `json:"qps"`
}

// 生成测试报告
func GenerateReport(b *testing.B) BenchmarkReport {
	return BenchmarkReport{
		TestName:       b.Name(),
		Iterations:     b.N,
		Duration:       b.Elapsed(),
		NsPerOperation: b.Elapsed().Nanoseconds() / int64(b.N),
		QPS:            float64(b.N) / b.Elapsed().Seconds(),
	}
}

// PrintReport 打印测试报告
func PrintReport(report BenchmarkReport) {
	fmt.Printf("\n========== 性能测试报告 ==========\n")
	fmt.Printf("测试项目: %s\n", report.TestName)
	fmt.Printf("执行次数: %d\n", report.Iterations)
	fmt.Printf("总耗时: %v\n", report.Duration)
	fmt.Printf("单次操作耗时: %d ns (%.3f ms)\n", report.NsPerOperation, float64(report.NsPerOperation)/1e6)
	fmt.Printf("QPS: %.2f\n", report.QPS)
	fmt.Printf("==================================\n\n")
}

// 模拟用户登录请求
func BenchmarkUserLogin(b *testing.B) {
	ginRouter := router.InitRouter()

	loginData := map[string]string{
		"email":    "test@example.com",
		"password": "test123",
	}
	jsonData, _ := json.Marshal(loginData)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/api/v1/user/login", bytes.NewBuffer(jsonData))
		req.Header.Set("Content-Type", "application/json")
		ginRouter.ServeHTTP(w, req)
	}
}

// 模拟获取聊天历史请求
func BenchmarkChatHistory(b *testing.B) {
	ginRouter := router.InitRouter()

	historyData := map[string]string{
		"sessionId": "test-session-id",
	}
	jsonData, _ := json.Marshal(historyData)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/api/v1/AI/chat/history", bytes.NewBuffer(jsonData))
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer test_token")
		ginRouter.ServeHTTP(w, req)
	}
}
