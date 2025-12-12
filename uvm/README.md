Ассемблируем
py assembler.py simple_test2.json simple2.bin --test
Запускаем интерпретатор
py interpreter.py simple2.bin --dump memory.xml --range 0:50
запускаем тесты
py test.py