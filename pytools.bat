::1.2
::net=1
@echo off
title pytools
@chcp 65001
setlocal enabledelayedexpansion
set python_path=""

set ENV_PATH=%PATH%
@echo %ENV_PATH% | findstr /c:"Python3">nul
if %errorlevel% == 1 (
    @echo %%ENV_PATH%% | findstr /c:"python3">nul
    if %errorlevel% == 1 (
        if %python_path% neq "" (
            %python_path% tool_manager.py #
            exit
        )
        color 04
        echo python environment error
        echo 1.still starting
        echo 2.input python path and start
        echo other quit
        goto chouse
    ) else (
        goto normal_start
    )
) else (
    goto normal_start
)

::选择默认启动还是输入环境
:chouse
set /p choice=
if %choice%==1 goto normal_start
if %choice%==2 goto input_start
exit

:normal_start
python tool_manager.py
exit

:input_start
set /p tp=path:
%tp% tool_manager.py %tp%
exit