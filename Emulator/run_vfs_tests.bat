@echo off
echo Запуск тестов VFS эмулятора...
echo.

echo === Тест 1: Минимальная VFS ===
python emulator.py -v "test_vfs_minimal.json" -s "test_comprehensive.txt"
echo.

echo === Тест 2: Средняя VFS ===  
python emulator.py -v "test_vfs_medium.json" -s "test_comprehensive.txt"
echo.

echo === Тест 3: Многоуровневая VFS ===
python emulator.py -v "test_vfs_large.json" -s "test_comprehensive.txt"
echo.

echo === Тест 4: Ошибка загрузки VFS ===
python emulator.py -v "nonexistent.json" -s "test_script1.txt"
echo.

echo === Тест 5: Неверный формат VFS ===
echo {"invalid": json > broken.json
python emulator.py -v "broken.json" -s "test_script1.txt"
if exist broken.json del broken.json
echo.

echo Тестирование VFS завершено.
pause