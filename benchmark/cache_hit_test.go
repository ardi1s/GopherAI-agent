package benchmark

import (
	"fmt"
	"math/rand"
	"testing"
	"time"

	"GopherAI/common/redis"
)

// TestCacheHitRate 测试不同场景下的缓存命中率
func TestCacheHitRate(t *testing.T) {
	redis.Init()

	testCases := []struct {
		name        string
		totalKeys   int
		hotKeyRatio float32 // 热点数据比例
		accessCount int
	}{
		{"High Hit Rate (90%)", 1000, 0.9, 10000},
		{"Medium Hit Rate (70%)", 1000, 0.7, 10000},
		{"Low Hit Rate (50%)", 1000, 0.5, 10000},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// 准备数据
			for i := 0; i < tc.totalKeys; i++ {
				key := fmt.Sprintf("cache:%s:key:%d", tc.name, i)
				if float32(i) < float32(tc.totalKeys)*tc.hotKeyRatio {
					// 热点数据预先写入缓存
					redis.Rdb.Set(testCtx, key, "hot_value", time.Minute*10)
				}
			}

			hitCount := 0
			missCount := 0

			// 模拟访问
			for i := 0; i < tc.accessCount; i++ {
				var key string
				if rand.Float32() < tc.hotKeyRatio {
					// 访问热点数据
					keyIndex := rand.Intn(int(float32(tc.totalKeys) * tc.hotKeyRatio))
					key = fmt.Sprintf("cache:%s:key:%d", tc.name, keyIndex)
				} else {
					// 访问冷数据
					keyIndex := int(float32(tc.totalKeys)*tc.hotKeyRatio) + rand.Intn(int(float32(tc.totalKeys)*(1-tc.hotKeyRatio)))
					key = fmt.Sprintf("cache:%s:key:%d", tc.name, keyIndex)
				}

				_, err := redis.Rdb.Get(testCtx, key).Result()
				if err == nil {
					hitCount++
				} else {
					missCount++
					// 回源并写入缓存
					redis.Rdb.Set(testCtx, key, "cached_value", time.Minute*10)
				}
			}

			hitRate := float64(hitCount) / float64(hitCount+missCount) * 100
			t.Logf("%s: Hit Rate = %.2f%% (Hits: %d, Misses: %d)", tc.name, hitRate, hitCount, missCount)
		})
	}
}

// BenchmarkCacheVsDB 对比缓存和数据库查询性能
func BenchmarkCacheVsDB(b *testing.B) {
	redis.Init()

	key := "perf:test:key"
	value := "test_value"

	b.Run("RedisGet", func(b *testing.B) {
		// 先写入
		redis.Rdb.Set(testCtx, key, value, time.Minute)
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			redis.Rdb.Get(testCtx, key)
		}
	})

	// 注意：这里模拟数据库查询，实际项目中需要连接MySQL
	b.Run("SimulatedDBQuery", func(b *testing.B) {
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			// 模拟数据库查询延迟（约5-10ms）
			time.Sleep(5 * time.Millisecond)
		}
	})
}
