@echo off
echo 安装打包工具...
pip install pyinstaller

echo.
echo 开始打包...
pyinstaller --onefile --noconsole --name "视频转文字工具" --add-data "web;web" --hidden-import flask --hidden-import faster_whisper --hidden-import docx --hidden-import anthropic --hidden-import psutil --hidden-import nltk web_server.py

echo.
echo 打包完成！输出目录: dist\
pause
