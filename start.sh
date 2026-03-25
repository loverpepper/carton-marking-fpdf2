#!/bin/bash

echo "🔄 正在拉取 main 分支的最新代码..."
git fetch --all
git reset --hard origin/main
git pull origin main

echo "📦 检查并安装新依赖..."
# 换成阿里云的加速源，稳如老狗！
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

echo "🚀 启动箱唛生成器..."
exec streamlit run app_v2.py --server.port=8501 --server.address=0.0.0.0