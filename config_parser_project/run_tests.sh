#!/bin/bash

echo "========================================"
echo "Тестирование парсера конфигураций"
echo "Вариант 19"
echo "========================================"

echo ""
echo "1. Установка зависимостей..."
pip install -r requirements.txt

echo ""
echo "2. Запуск тестов..."
python test_parser.py

echo ""
echo "3. Тестирование примеров..."
echo ""
echo "Пример 1: Веб-сервер"
python config_parser.py -o test1.yaml < examples/web_server.conf
if [ -f test1.yaml ]; then
    echo "Файл создан: test1.yaml"
    cat test1.yaml
    rm test1.yaml
fi

echo ""
echo "Пример 2: Игровая конфигурация"
python config_parser.py -o test2.yaml < examples/game_config.conf
if [ -f test2.yaml ]; then
    echo "Файл создан: test2.yaml"
    cat test2.yaml
    rm test2.yaml
fi

echo ""
echo "Пример 3: Научный эксперимент"
python config_parser.py -o test3.yaml < examples/experiment.conf
if [ -f test3.yaml ]; then
    echo "Файл создан: test3.yaml"
    cat test3.yaml
    rm test3.yaml
fi

echo ""
echo "========================================"
echo "Тестирование завершено!"