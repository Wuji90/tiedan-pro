# 使用官方轻量级 Python
FROM python:3.9-slim

# 安装音频解码必须的底层库 (一次性装全)
RUN apt-get update && \
    apt-get install -y ffmpeg libopus-dev portaudio19-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
