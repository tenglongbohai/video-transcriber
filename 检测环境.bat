@echo off
chcp 65001 >nul
echo ========================================
echo     视频转文字工具 - 环境检测
echo ========================================
echo.

set PYTHON_OK=0
set FFMPEG_OK=0
set DEPS_OK=0

:: 检查 Python
echo [1/4] 检查 Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✓ Python 已安装
    set PYTHON_OK=1
) else (
    echo     ✗ Python 未安装
)

:: 检查 ffmpeg
echo [2/4] 检查 ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✓ ffmpeg 已安装
    set FFMPEG_OK=1
) else (
    echo     ✗ ffmpeg 未安装
)

:: 检查 Python 依赖
echo [3/4] 检查 Python 依赖...
python -c "import flask, psutil, faster_whisper, docx" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✓ 所有依赖已安装
    set DEPS_OK=1
) else (
    echo     ○ 部分依赖缺失
)

:: 安装 Python
if %PYTHON_OK% equ 0 (
    echo.
    echo ========================================
    echo  Python 未安装！
    echo ========================================
    echo.
    choice /c YN /m "是否自动下载安装 Python？(Y/N): "
    if errorlevel 2 goto skip_python
    echo.
    echo ○ 正在下载 Python 3.11.9...
    powershell -Command "Invoke-WebRequest -Uri 'https://registry.npmmirror.com/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    if errorlevel 1 (
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    )
    echo     ✓ 下载完成！
    echo.
    echo ○ 正在启动安装程序...
    echo   请在安装向导中务必勾选: "Add Python to PATH"
    echo.
    start python-installer.exe
    echo.
    echo 安装完成后请重新运行此脚本
    echo.
    :skip_python
)

:: 安装 ffmpeg
if %FFMPEG_OK% equ 0 (
    echo.
    echo ========================================
    echo  ffmpeg 未安装！
    echo ========================================
    echo.
    choice /c YN /m "是否自动下载安装 ffmpeg？(Y/N): "
    if errorlevel 2 goto skip_ffmpeg
    echo.
    echo ○ 正在下载 ffmpeg...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
    echo     ✓ 下载完成！
    echo.
    echo ○ 正在解压配置...
    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"
    powershell -Command "if (Test-Path 'ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe') { Copy-Item 'ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe' '.'; Copy-Item 'ffmpeg-master-latest-win64-gpl\\bin\\ffplay.exe' '.'; Copy-Item 'ffmpeg-master-latest-win64-gpl\\bin\\ffprobe.exe' '.' }"
    setx PATH "%PATH%;%CD%" /M >nul
    echo     ✓ ffmpeg 安装完成（已添加到系统PATH）
    echo.
    :skip_ffmpeg
)

:: 安装 Python 依赖
if %DEPS_OK% equ 0 (
    echo.
    echo ========================================
    echo  正在安装 Python 依赖...
    echo ========================================
    echo.
    pip install flask psutil faster-whisper python-docx -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet
    echo.
    echo     ✓ 依赖安装完成！
)

:: 最终检查
echo.
echo [4/4] 最终检查...
echo.
set FINAL_OK=1
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo     ✗ Python: 未安装
    set FINAL_OK=0
) else (
    echo     ✓ Python: 已安装
)

ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo     ✗ ffmpeg: 未安装
    set FINAL_OK=0
) else (
    echo     ✓ ffmpeg: 已安装
)

python -c "import flask, psutil, faster_whisper, docx" >nul 2>&1
if %errorlevel% neq 0 (
    echo     ✗ Python依赖: 部分缺失
    set FINAL_OK=0
) else (
    echo     ✓ Python依赖: 已安装
)

echo.
echo ========================================
if %FINAL_OK% equ 1 (
    echo  ✓ 环境检测通过！
    echo.
    echo  现在可以双击 [点击运行.bat] 启动服务
) else (
    echo  ○ 部分环境未配置完成
    echo.
    echo  请根据上方提示安装缺失组件
    echo  完成后重新运行此脚本
)
echo ========================================

pause
