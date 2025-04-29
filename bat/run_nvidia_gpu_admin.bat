@echo off
:: 检查是否已经是管理员
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' (
    goto :got_admin
) else (
    goto :UACPrompt
)

:UACPrompt
    echo 请求管理员权限...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "cmd", "/c cd /d ""%~dp0"" && ""%~f0""", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:got_admin
    if exist "%temp%\getadmin.vbs" (
        del "%temp%\getadmin.vbs"
    )
    cd /d "%~dp0"

:: 运行 Python 命令
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build

pause