# 构建阶段
FROM golang:1.24-alpine AS builder

# 设置工作目录
WORKDIR /app

# 配置 Go 使用国内代理
ENV GOPROXY=https://goproxy.cn,direct
ENV GO111MODULE=on

# 安装构建依赖
RUN apk add --no-cache git gcc musl-dev

# 复制 go.mod 和 go.sum
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用（启用 CGO）
RUN go build -ldflags="-w -s" -o gopherai main.go

# 运行阶段
FROM alpine:latest

# 安装运行时依赖
RUN apk add --no-cache ca-certificates

WORKDIR /root/

# 从构建阶段复制二进制文件
COPY --from=builder /app/gopherai .

# 创建配置目录
RUN mkdir -p /root/config

# 暴露端口
EXPOSE 9090

# 启动应用
CMD ["./gopherai"]
