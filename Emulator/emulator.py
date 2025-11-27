import argparse
import os
import sys
from script_runner import run_script

def main():
    # 1. Парсинг параметров командной строки
    parser = argparse.ArgumentParser(description='Эмулятор файловой системы')
    parser.add_argument('-v', '--vfs-path', required=True, 
                       help='Путь к физическому расположению VFS')
    parser.add_argument('-s', '--script-path', required=True,
                       help='Путь к стартовому скрипту')
    
    args = parser.parse_args()
    
    # 2. Отладочный вывод всех параметров
    print("=== КОНФИГУРАЦИЯ ЭМУЛЯТОРА ===")
    print(f"Путь к VFS: {args.vfs_path}")
    print(f"Путь к скрипту: {args.script_path}")
    print("===============================")
    
    # 3. Проверка существования путей
    if not os.path.exists(args.vfs_path):
        print(f"ОШИБКА: Путь VFS не существует: {args.vfs_path}")
        sys.exit(1)
        
    if not os.path.exists(args.script_path):
        print(f"ОШИБКА: Файл скрипта не существует: {args.script_path}")
        sys.exit(1)
    
    # 4. Запуск скрипта
    print("\n=== ЗАПУСК СКРИПТА ===")
    run_script(args.script_path, args.vfs_path)

if __name__ == "__main__":
    main()