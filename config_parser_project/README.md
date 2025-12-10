# Для Windows
run_tests.bat

# Для Linux/Mac
chmod +x run_tests.sh
./run_tests.sh

# Способ 1: Чтение из файла
python config_parser.py -o output.yaml < input.conf

# Способ 2: Прямой ввод (завершить Ctrl+D или Ctrl+Z)
python config_parser.py -o output.yaml
{ key => [[value]] }

# Способ 3: Через pipe
echo '{ test => 123.0 }' | python config_parser.py -o result.yaml