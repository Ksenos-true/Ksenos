import os
import sys
from vfs_manager import VFSManager

def execute_command(command, vfs_path, vfs_manager):
    """
    Выполняет одну команду эмулятора с поддержкой VFS
    """
    cmd_parts = command.split()
    if not cmd_parts:
        return ""
    
    cmd_name = cmd_parts[0].lower()
    
    # Команды работы с VFS
    if cmd_name == "echo":
        return " ".join(cmd_parts[1:])
    
    elif cmd_name == "vfs_info":
        return vfs_manager.get_vfs_info()
    
    elif cmd_name == "vfs_load":
        if len(cmd_parts) < 2:
            return "ОШИБКА: Укажите путь к VFS файлу"
        try:
            vfs_manager.load_vfs(cmd_parts[1])
            return f"VFS загружена из: {cmd_parts[1]}"
        except Exception as e:
            return f"ОШИБКА загрузки VFS: {e}"
    
    elif cmd_name == "ls":
        path = cmd_parts[1] if len(cmd_parts) > 1 else ""
        try:
            items = vfs_manager.list_directory(path)
            if items is None:
                return f"ОШИБКА: Директория не найдена: {path}"
            
            if not items:
                return "Директория пуста"
            
            result = []
            for item in items:
                type_char = '/' if item['type'] == 'directory' else ''
                size = f" ({item['size']}b)" if item['type'] == 'file' else ''
                result.append(f"{item['name']}{type_char}{size}")
            return "\n".join(result)
        except Exception as e:
            return f"ОШИБКА: {e}"
    
    elif cmd_name == "cat":
        if len(cmd_parts) < 2:
            return "ОШИБКА: Укажите путь к файлу"
        try:
            content = vfs_manager.get_file_content(cmd_parts[1])
            if content is None:
                return f"ОШИБКА: Файл не найден: {cmd_parts[1]}"
            return content
        except Exception as e:
            return f"ОШИБКА чтения файла: {e}"
    
    elif cmd_name == "pwd":
        return "/"
    
    elif cmd_name == "help":
        return """Доступные команды:
echo [текст] - вывод текста
vfs_load [путь] - загрузить VFS
vfs_info - информация о VFS
ls [путь] - список файлов
cat [файл] - показать содержимое файла
pwd - текущая директория
help - эта справка
error - тестовая ошибка"""
    
    elif cmd_name == "error":
        return "ОШИБКА: Искусственная ошибка по команде 'error'"
    
    else:
        return f"ОШИБКА: Неизвестная команда '{cmd_name}'"

def run_script(script_path, vfs_path):
    """
    Выполняет стартовый скрипт с поддержкой VFS
    """
    vfs_manager = VFSManager()
    
    # Автозагрузка VFS если указан путь
    if vfs_path and os.path.exists(vfs_path):
        try:
            vfs_manager.load_vfs(vfs_path)
            print("✓ VFS загружена автоматически при запуске")
        except Exception as e:
            print(f"⚠ Не удалось загрузить VFS при запуске: {e}")
    
    try:
        with open(script_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
                
            print(f"[Строка {line_num}] > {line}")
            
            result = execute_command(line, vfs_path, vfs_manager)
            
            # Проверяем на ошибки (команды, начинающиеся с "ОШИБКА")
            if result.startswith("ОШИБКА:"):
                print(f"       < {result}")
                print("⛔ Выполнение скрипта остановлено из-за ошибки")
                sys.exit(1)
            else:
                if result:
                    print(f"       < {result}")
            
            print()
            
    except Exception as e:
        print(f"ОШИБКА выполнения скрипта: {e}")
        sys.exit(1)