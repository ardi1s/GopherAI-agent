package benchmark

import (
	"fmt"
	"testing"
	"time"
)

// TestMain 主测试入口
func TestMain(m *testing.M) {
	fmt.Println("开始性能测试...")
	m.Run()
}

// TestBenchmarkAll 运行所有基准测试
func TestBenchmarkAll(t *testing.T) {
	fmt.Println("========== 开始基准测试 ==========")
	
	// 运行Redis性能测试
	t.Run("Redis性能测试", func(t *testing.T) {
		testRedisPerformance(t)
	})
	
	// 运行API性能测试
	t.Run("API性能测试", func(t *testing.T) {
		testAPIPerformance(t)
	})
}

// testRedisPerformance 测试Redis性能
func testRedisPerformance(t *testing.T) {
	fmt.Println("\n----- Redis性能测试 -----")
	
	// 测试Redis写入性能
	result := testing.Benchmark(func(b *testing.B) {
		BenchmarkRedisSet(b)
	})
	
	fmt.Printf("Redis写入性能:\n")
	fmt.Printf("  执行次数: %d\n", result.N)
	fmt.Printf("  单次操作耗时: %d ns (%.3f ms)\n", 
		result.NsPerOp(), float64(result.NsPerOp())/1e6)
	fmt.Printf("  QPS: %.2f\n", float64(1e9)/float64(result.NsPerOp()))
	
	// 测试Redis读取性能
	result = testing.Benchmark(func(b *testing.B) {
		BenchmarkRedisGet(b)
	})
	
	fmt.Printf("\nRedis读取性能:\n")
	fmt.Printf("  执行次数: %d\n", result.N)
	fmt.Printf("  单次操作耗时: %d ns (%.3f ms)\n", 
		result.NsPerOp(), float64(result.NsPerOp())/1e6)
	fmt.Printf("  QPS: %.2f\n", float64(1e9)/float64(result.NsPerOp()))
	
	// 测试验证码缓存性能
	result = testing.Benchmark(func(b *testing.B) {
		BenchmarkRedisCaptcha(b)
	})
	
	fmt.Printf("\n验证码缓存性能:\n")
	fmt.Printf("  执行次数: %d\n", result.N)
	fmt.Printf("  单次操作耗时: %d ns (%.3f ms)\n", 
		result.NsPerOp(), float64(result.NsPerOp())/1e6)
	fmt.Printf("  QPS: %.2f\n", float64(1e9)/float64(result.NsPerOp()))
}

// testAPIPerformance 测试API性能
func testAPIPerformance(t *testing.T) {
	fmt.Println("\n----- API性能测试 -----")
	
	// 测试用户登录接口
	result := testing.Benchmark(func(b *testing.B) {
		BenchmarkUserLogin(b)
	})
	
	fmt.Printf("用户登录接口性能:\n")
	fmt.Printf("  执行次数: %d\n", result.N)
	fmt.Printf("  单次操作耗时: %d ns (%.3f ms)\n", 
		result.NsPerOp(), float64(result.NsPerOp())/1e6)
	fmt.Printf("  QPS: %.2f\n", float64(1e9)/float64(result.NsPerOp()))
	
	// 测试获取会话列表接口
	result = testing.Benchmark(func(b *testing.B) {
		BenchmarkGetUserSessions(b)
	})
	
	fmt.Printf("\n获取会话列表接口性能:\n")
	fmt.Printf("  执行次数: %d\n", result.N)
	fmt.Printf("  单次操作耗时: %d ns (%.3f ms)\n", 
		result.NsPerOp(), float64(result.NsPerOp())/1e6)
	fmt.Printf("  QPS: %.2f\n", float64(1e9)/float64(result.NsPerOp()))
	
	// 测试获取聊天历史接口
	result = testing.Benchmark(func(b *testing.B) {
		BenchmarkChatHistory(b)
	})
	
	fmt.Printf("\n获取聊天历史接口性能:\n")
	fmt.Printf("  执行次数: %d\n", result.N)
	fmt.Printf("  单次操作耗时: %d ns (%.3f ms)\n", 
		result.NsPerOp(), float64(result.NsPerOp())/1e6)
	fmt.Printf("  QPS: %.2f\n", float64(1e9)/float64(result.NsPerOp()))
	
	// 测试并发请求性能
	result = testing.Benchmark(func(b *testing.B) {
		BenchmarkConcurrentRequests(b)
	})
	
	fmt.Printf("\n并发请求性能:\n")
	fmt.Printf("  执行次数: %d\n", result.N)
	fmt.Printf("  单次操作耗时: %d ns (%.3f ms)\n", 
		result.NsPerOp(), float64(result.NsPerOp())/1e6)
	fmt.Printf("  QPS: %.2f\n", float64(1e9)/float64(result.NsPerOp()))
}

// TestLoadTest 运行负载测试
func TestLoadTest(t *testing.T) {
	fmt.Println("========== 开始负载测试 ==========")
	
	config := LoadTestConfig{
		BaseURL:         "http://localhost:9090",
		ConcurrentUsers: 100,
		Duration:        30 * time.Second,
		RampUpTime:      5 * time.Second,
	}
	
	// 测试用户登录接口
	fmt.Println("\n----- 用户登录接口负载测试 -----")
	result := RunLoadTest(config, LoadTestUserLogin)
	PrintLoadTestResult(result)
	
	// 测试获取会话列表接口
	fmt.Println("\n----- 获取会话列表接口负载测试 -----")
	result = RunLoadTest(config, LoadTestGetSessions)
	PrintLoadTestResult(result)
}

// TestGenerateReport 生成测试报告
func TestGenerateReport(t *testing.T) {
	fmt.Println("========== 生成性能测试报告 ==========")
	
	report := generatePerformanceReport()
	printPerformanceReport(report)
}

// PerformanceReport 性能测试报告
type PerformanceReport struct {
	TestTime        time.Time              `json:"test_time"`
	RedisResults    map[string]TestResult  `json:"redis_results"`
	APIResults      map[string]TestResult  `json:"api_results"`
	LoadTestResults map[string]LoadResult  `json:"load_test_results"`
}

// TestResult 单个测试结果
type TestResult struct {
	Iterations     int     `json:"iterations"`
	NsPerOp        int64   `json:"ns_per_op"`
	QPS            float64 `json:"qps"`
	AvgTimeMs      float64 `json:"avg_time_ms"`
}

// LoadResult 负载测试结果
type LoadResult struct {
	TotalRequests   int64   `json:"total_requests"`
	SuccessRate     float64 `json:"success_rate"`
	AvgResponseTime float64 `json:"avg_response_time_ms"`
	QPS             float64 `json:"qps"`
}

// generatePerformanceReport 生成性能测试报告
func generatePerformanceReport() PerformanceReport {
	report := PerformanceReport{
		TestTime:        time.Now(),
		RedisResults:    make(map[string]TestResult),
		APIResults:      make(map[string]TestResult),
		LoadTestResults: make(map[string]LoadResult),
	}
	
	// Redis测试结果
	redisWriteResult := testing.Benchmark(func(b *testing.B) {
		BenchmarkRedisSet(b)
	})
	report.RedisResults["write"] = TestResult{
		Iterations: redisWriteResult.N,
		NsPerOp:    redisWriteResult.NsPerOp(),
		QPS:        float64(1e9) / float64(redisWriteResult.NsPerOp()),
		AvgTimeMs:  float64(redisWriteResult.NsPerOp()) / 1e6,
	}
	
	redisReadResult := testing.Benchmark(func(b *testing.B) {
		BenchmarkRedisGet(b)
	})
	report.RedisResults["read"] = TestResult{
		Iterations: redisReadResult.N,
		NsPerOp:    redisReadResult.NsPerOp(),
		QPS:        float64(1e9) / float64(redisReadResult.NsPerOp()),
		AvgTimeMs:  float64(redisReadResult.NsPerOp()) / 1e6,
	}
	
	// API测试结果
	loginResult := testing.Benchmark(func(b *testing.B) {
		BenchmarkUserLogin(b)
	})
	report.APIResults["login"] = TestResult{
		Iterations: loginResult.N,
		NsPerOp:    loginResult.NsPerOp(),
		QPS:        float64(1e9) / float64(loginResult.NsPerOp()),
		AvgTimeMs:  float64(loginResult.NsPerOp()) / 1e6,
	}
	
	sessionsResult := testing.Benchmark(func(b *testing.B) {
		BenchmarkGetUserSessions(b)
	})
	report.APIResults["get_sessions"] = TestResult{
		Iterations: sessionsResult.N,
		NsPerOp:    sessionsResult.NsPerOp(),
		QPS:        float64(1e9) / float64(sessionsResult.NsPerOp()),
		AvgTimeMs:  float64(sessionsResult.NsPerOp()) / 1e6,
	}
	
	return report
}

// printPerformanceReport 打印性能测试报告
func printPerformanceReport(report PerformanceReport) {
	fmt.Printf("\n========== 性能测试报告 ==========\n")
	fmt.Printf("测试时间: %s\n\n", report.TestTime.Format("2006-01-02 15:04:05"))
	
	fmt.Printf("----- Redis性能 -----\n")
	for name, result := range report.RedisResults {
		fmt.Printf("%s:\n", name)
		fmt.Printf("  执行次数: %d\n", result.Iterations)
		fmt.Printf("  单次耗时: %.3f ms\n", result.AvgTimeMs)
		fmt.Printf("  QPS: %.2f\n", result.QPS)
	}
	
	fmt.Printf("\n----- API性能 -----\n")
	for name, result := range report.APIResults {
		fmt.Printf("%s:\n", name)
		fmt.Printf("  执行次数: %d\n", result.Iterations)
		fmt.Printf("  单次耗时: %.3f ms\n", result.AvgTimeMs)
		fmt.Printf("  QPS: %.2f\n", result.QPS)
	}
	
	fmt.Printf("\n==================================\n")
}
