@echo off

cd /d C:\Sistema\sistema-chamados

call venv\Scripts\activate

python manage.py runserver 0.0.0.0:8000