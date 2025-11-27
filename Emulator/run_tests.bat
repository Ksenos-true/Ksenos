@echo off
echo Запуск тестов эмулятора...
echo.

echo === Тест 1: Корректные параметры ===
python emulator.py -v "C:\temp\vfs" -s "test_script1.txt"
echo.

echo === Тест 2: Скрипт с ошибкой ===
python emulator.py -v "C:\temp\vfs" -s "test_script2.txt"
echo.

echo === Тест 3: Несуществующий путь VFS ===
python emulator.py -v "C:\fake\path" -s "test_script1.txt"
echo.

echo === Тест 4: Несуществующий скрипт ===
python emulator.py -v "C:\temp\vfs" -s "fake_script.txt"
echo.

echo Тестирование завершено.
pause