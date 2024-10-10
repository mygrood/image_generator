@echo off


if not exist "venv\" (
    echo Виртуальное окружение не найдено. Устанавливаю зависимости...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    echo Установка зависимостей завершена.
) else (
    echo Виртуальное окружение найдено. Активирую...
    call venv\Scripts\activate
)

python main.py
