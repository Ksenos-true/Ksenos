@echo off
echo ========================================
echo Тестирование парсера конфигураций
echo Вариант 19
echo ========================================

echo.
echo 1. Установка зависимостей...
pip install -r requirements.txt

echo.
echo 2. Запуск тестов...
python test_parser.py

echo.
echo 3. Тестирование примеров...
echo.
echo Пример 1: Веб-сервер
python config_parser.py -o test1.yaml < examples/web_server.conf
if exist test1.yaml (
    echo Файл создан: test1.yaml
    type test1.yaml
    del test1.yaml
)

echo.
echo Пример 2: Игровая конфигурация
python config_parser.py -o test2.yaml < examples/game_config.conf
if exist test2.yaml (
    echo Файл создан: test2.yaml
    type test2.yaml
    del test2.yaml
)

echo.
echo Пример 3: Научный эксперимент
python config_parser.py -o test3.yaml < examples/experiment.conf
if exist test3.yaml (
    echo Файл создан: test3.yaml
    type test3.yaml
    del test3.yaml
)

echo.
echo ========================================
echo Тестирование завершено!
pause