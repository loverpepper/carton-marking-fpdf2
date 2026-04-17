# 锁定 Python 3.12.12 精简版镜像，避免因基础镜像更新导致环境漂移
FROM python:3.12.12-slim

# 安装 git 和 dos2unix（洗衣机买好了）
RUN apt-get update && apt-get install -y git dos2unix && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

# 🚨 就是漏了这极其关键的一行！把脚本放进洗衣机里洗掉 Windows 的回车符！
RUN dos2unix /app/start.sh

# 赋予执行权限
RUN chmod +x /app/start.sh

EXPOSE 8501

CMD ["/app/start.sh"]