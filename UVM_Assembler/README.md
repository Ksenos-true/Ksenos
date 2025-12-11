# UVM Assembler and Interpreter

## Запуск проекта:

```bash
# 1. Проверяем наличие .NET 8.0
dotnet --version

# 2. Собираем проект
dotnet build

# 3. Запускаем тесты из спецификации
dotnet run -- test

# 4. Ассемблируем программу
dotnet run -- assemble program.json program.bin

# 5. Выполняем программу
dotnet run -- interpret program.bin result.xml 0 100

# 6. Смотрим результат
cat result.xml