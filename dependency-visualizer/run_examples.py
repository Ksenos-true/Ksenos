#!/usr/bin/env python3
"""
Примеры запуска для тестирования функциональности
"""

import subprocess
import sys

def run_example(description, command):
    """Запуск примера команды"""
    print(f"\n{'='*60}")
    print(f"Пример: {description}")
    print(f"{'='*60}")
    print(f"Команда: {' '.join(command)}")
    print()
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Код возврата: {result.returncode}")
    except Exception as e:
        print(f"Ошибка при выполнении: {e}")

def main():
    examples = [
        {
            "description": "Корректный запуск с URL",
            "command": [
                sys.executable, "dependency_viz.py",
                "--package", "org.springframework:spring-core",
                "--url", "http://repo.maven.apache.org/maven2"
            ]
        },
        {
            "description": "Корректный запуск с тестовым репозиторием",
            "command": [
                sys.executable, "dependency_viz.py", 
                "--package", "com.example:test-app",
                "--test-repo", "./test-data",
                "--tree",
                "--max-depth", "3"
            ]
        },
        {
            "description": "Ошибка: отсутствует обязательный параметр --package",
            "command": [
                sys.executable, "dependency_viz.py",
                "--url", "http://repo.maven.apache.org/maven2"
            ]
        },
        {
            "description": "Ошибка: некорректный формат пакета",
            "command": [
                sys.executable, "dependency_viz.py",
                "--package", "invalid-package-format",
                "--url", "http://repo.maven.apache.org/maven2"
            ]
        },
        {
            "description": "Ошибка: отрицательная глубина анализа",
            "command": [
                sys.executable, "dependency_viz.py",
                "--package", "org.springframework:spring-core", 
                "--url", "http://repo.maven.apache.org/maven2",
                "--max-depth", "-1"
            ]
        }
    ]
    
    print("ЗАПУСК ТЕСТОВЫХ ПРИМЕРОВ")
    print("Демонстрация функциональности этапа 1")
    
    for example in examples:
        run_example(example["description"], example["command"])

if __name__ == "__main__":
    main()