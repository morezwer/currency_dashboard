@echo off
echo Создание виртуальной среды через conda...
conda env create -f environment.yml

echo Активация среды и запуск приложения... Если conda не активируется, запустите скрипт в Anaconda Prompt
call conda activate currency_dashboard_env
python app\main.py
pause
