FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 下载并安装 kepubify
RUN wget https://github.com/pgaskin/kepubify/releases/download/v4.3.7/kepubify_linux_amd64.zip \
    && unzip kepubify_linux_amd64.zip \
    && chmod +x kepubify

# 下载并安装 kindlegen
RUN wget https://archive.org/download/kindlegen/kindlegen_linux_2.6_i386_v2_9.tar.gz \
    && tar -xzf kindlegen_linux_2.6_i386_v2_9.tar.gz \
    && chmod +x kindlegen

# 创建输入输出目录
RUN mkdir -p /app/input /app/output

# 设置环境变量
ENV PATH="/app:${PATH}"

# 默认命令 - 启动自动监控
CMD ["python", "auto_converter.py"]
