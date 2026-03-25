@echo off
:: 强制使用 UTF-8 编码，防止中文乱码
chcp 65001 >nul

echo ===================================================
echo     🚀 正在为 Mcombo 箱唛生成器配置超光速网络...
echo ===================================================
echo.

:: 检查并创建 Windows 用户的 Docker 配置文件夹
if not exist "%USERPROFILE%\.docker" mkdir "%USERPROFILE%\.docker"

:: 强行把我们的加速配置文件覆盖过去
copy /y daemon.json "%USERPROFILE%\.docker\daemon.json" >nul

echo ✅ 镜像加速节点已注入成功！
echo.
echo ⚠️  【极其重要】：如果你的右下角任务栏里已经开着一艘“小鲸鱼”(Docker Desktop)，
echo      请现在立刻右键它，点击 "Quit Docker Desktop" 退出，然后再重新打开它。
echo      （如果没开，请直接无视这句话）。
echo.
pause

echo.
echo 🔄 正在组装并启动服务器，请稍候...
echo.

:: 执行我们熟悉的魔咒
docker-compose up -d --build

echo.
echo ===================================================
echo  🎉 恭喜！服务器已在后台狂奔！
echo  请等待 1~2 分钟下载依赖后，在浏览器输入：
echo  http://localhost:8501
echo ===================================================
echo.
pause