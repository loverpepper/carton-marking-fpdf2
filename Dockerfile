# 锁定 Python 3.12.12 精简版镜像
FROM python:3.12.12-slim

# 1. 【新增】极速换源：将 Debian 的 apt 源改为腾讯云内网源
# 注意：python:3.12-slim 基于 Debian 12 (bookworm)，其源配置文件在 /etc/apt/sources.list.d/debian.sources
RUN sed -i 's/deb.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list.d/debian.sources

# 2. 安装系统依赖
RUN apt-get update && apt-get install -y git dos2unix && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. 【优化】利用 Docker 缓存机制：先拷贝 requirements.txt
# 这样如果代码变了但依赖没变，就不需要重新安装 Python 包
COPY requirements.txt .

# 4. 【新增】Pip 换源：使用清华源或腾讯源加速依赖安装
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

COPY . /app

# 🚨 洗掉 Windows 的回车符
RUN dos2unix /app/start.sh

# 赋予执行权限
RUN chmod +x /app/start.sh

EXPOSE 8501

CMD ["/app/start.sh"]