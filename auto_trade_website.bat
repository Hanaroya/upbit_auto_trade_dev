@echo off
cd /d C:\Users\ASUS\Documents\GitHub\upbit_auto_trade_dev
start gunicorn -w 4 -b 0.0.0.0:5000 main_flask_server:app
timeout /t 5
start http://localhost:5000