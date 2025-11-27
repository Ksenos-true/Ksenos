import os
import sys

def run_script(script_path, vfs_path):
    """
    Выполняет стартовый скрипт с имитацией диалога
    Останавливается при первой ошибке
    """
    try:
        with open(script_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue
                
            # Имитируем диалог: показываем ввод
            print(f"[Строка {line_num}] > {line}")
            
            # Обрабатываем команду
            result = execute_command(line, vfs_path)
            
            # Показываем вывод
            if result:
                print(f"       < {result}")
            
            print()  # пустая строка для читаемости
            
    except Exception as e:
        print(f"ОШИБКА выполнения скрипта: {e}")
        sys.exit(1)

def execute_command(command, vfs_path):
    """
    Выполняет одну команду эмулятора
    В реальном эмуляторе здесь будет логика команд
    """
    cmd_parts = command.split()
    if not cmd_parts:
        return ""
    
    cmd_name = cmd_parts[0].lower()
    
    # Эмуляция различных команд
    if cmd_name == "echo":
        return " ".join(cmd_parts[1:])
    elif cmd_name == "vfs_info":
        return f"VFS расположена в: {vfs_path}"
    elif cmd_name == "list":
        return "file1.txt file2.doc directory/"
    elif cmd_name == "error":
        print("ОШИБКА: Искусственная ошибка по команде 'error'")
        sys.exit(1)
    elif cmd_name == "help":
        return "Доступные команды: echo, vfs_info, list, help, error"
    else:
        print(f"ОШИБКА: Неизвестная команда '{cmd_name}'")
        sys.exit(1)