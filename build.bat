@echo off
echo Компіляція C++ модуля для Windows...

g++ -shared -fPIC order_processor.cpp -o order_processor.dll

if %errorlevel% equ 0 (
    echo Успішно! Створено order_processor.dll
) else (
    echo Помилка компіляції
    pause
)
