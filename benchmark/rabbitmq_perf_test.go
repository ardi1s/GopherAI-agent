package benchmark

import (
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/streadway/amqp"
)

// TestRabbitMQThroughput 测试RabbitMQ消息吞吐量
func TestRabbitMQThroughput(t *testing.T) {
	// 直接连接RabbitMQ
	conn, err := amqp.Dial("amqp://guest:guest@127.0.0.1:5672/")
	if err != nil {
		t.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		t.Fatalf("Failed to open channel: %v", err)
	}
	defer ch.Close()

	// 声明队列
	q, err := ch.QueueDeclare(
		"benchmark_queue", // name
		false,             // durable
		true,              // delete when unused
		false,             // exclusive
		false,             // no-wait
		nil,               // arguments
	)
	if err != nil {
		t.Fatalf("Failed to declare queue: %v", err)
	}

	messageSize := 1024 // 1KB
	duration := 5 * time.Second
	concurrent := 10

	message := make([]byte, messageSize)
	for i := range message {
		message[i] = byte(i % 256)
	}

	var sentCount int64
	var wg sync.WaitGroup

	start := time.Now()

	// 启动多个生产者
	for i := 0; i < concurrent; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			
			// 每个goroutine创建自己的channel
			chLocal, err := conn.Channel()
			if err != nil {
				return
			}
			defer chLocal.Close()

			localCount := 0
			for time.Since(start) < duration {
				err := chLocal.Publish(
					"",     // exchange
					q.Name, // routing key
					false,  // mandatory
					false,  // immediate
					amqp.Publishing{
						ContentType: "text/plain",
						Body:        message,
					},
				)
				if err == nil {
					localCount++
				}
			}
			atomic.AddInt64(&sentCount, int64(localCount))
		}(i)
	}

	wg.Wait()
	actualDuration := time.Since(start)
	throughput := float64(sentCount) / actualDuration.Seconds()

	t.Logf("RabbitMQ Throughput: %.2f messages/second", throughput)
	t.Logf("Total Sent: %d, Duration: %v", sentCount, actualDuration)
}

// TestRabbitMQLatency 测试RabbitMQ消息延迟
func TestRabbitMQLatency(t *testing.T) {
	conn, err := amqp.Dial("amqp://guest:guest@127.0.0.1:5672/")
	if err != nil {
		t.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		t.Fatalf("Failed to open channel: %v", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"latency_queue",
		false,
		true,
		false,
		false,
		nil,
	)
	if err != nil {
		t.Fatalf("Failed to declare queue: %v", err)
	}

	const testCount = 100
	latencies := make([]time.Duration, 0, testCount)

	for i := 0; i < testCount; i++ {
		start := time.Now()
		err := ch.Publish(
			"",
			q.Name,
			false,
			false,
			amqp.Publishing{
				ContentType: "text/plain",
				Body:        []byte("test message"),
			},
		)
		if err == nil {
			latency := time.Since(start)
			latencies = append(latencies, latency)
		}
		time.Sleep(time.Millisecond * 5)
	}

	var totalLatency time.Duration
	for _, lat := range latencies {
		totalLatency += lat
	}
	avgLatency := totalLatency / time.Duration(len(latencies))

	t.Logf("RabbitMQ Latency: Avg = %v (%.3f ms), Count = %d", 
		avgLatency, float64(avgLatency.Nanoseconds())/1e6, len(latencies))
}

// BenchmarkRabbitMQPublish 基准测试RabbitMQ发布性能
func BenchmarkRabbitMQPublish(b *testing.B) {
	conn, err := amqp.Dial("amqp://guest:guest@127.0.0.1:5672/")
	if err != nil {
		b.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		b.Fatalf("Failed to open channel: %v", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"benchmark_publish",
		false,
		true,
		false,
		false,
		nil,
	)
	if err != nil {
		b.Fatalf("Failed to declare queue: %v", err)
	}

	message := make([]byte, 1024)
	for i := range message {
		message[i] = byte(i % 256)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ch.Publish(
			"",
			q.Name,
			false,
			false,
			amqp.Publishing{
				ContentType: "text/plain",
				Body:        message,
			},
		)
	}
}
