#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для Maven пакетов
Этап 1: Минимальный прототип с конфигурацией
"""

import argparse
import sys
import os
from typing import Dict, Any


class DependencyGraphVisualizer:
    def __init__(self):
        self.config = {}
        self.parser = self._setup_parser()
    
    def _setup_parser(self) -> argparse.ArgumentParser:
        """Настройка парсера аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='Визуализатор графа зависимостей для Maven пакетов',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования:
  python depgraph.py --package com.example:my-app --url http://repo.maven.apache.org/maven2
  python depgraph.py --package org.springframework:spring-core --test-repo ./test-repo --max-depth 2
  python depgraph.py --package junit:junit --filter "test" --tree
            """
        )
        
        # Обязательные параметры
        parser.add_argument(
            '--package',
            required=True,
            help='Имя анализируемого пакета (формат: groupId:artifactId)'
        )
        
        # Источник данных (взаимоисключающие опции)
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument(
            '--url',
            help='URL-адрес Maven репозитория'
        )
        source_group.add_argument(
            '--test-repo',
            help='Путь к файлу тестового репозитория'
        )
        
        # Дополнительные параметры
        parser.add_argument(
            '--tree',
            action='store_true',
            help='Режим вывода зависимостей в формате ASCII-дерева'
        )
        
        parser.add_argument(
            '--max-depth',
            type=int,
            default=10,
            help='Максимальная глубина анализа зависимостей (по умолчанию: 10)'
        )
        
        parser.add_argument(
            '--filter',
            help='Подстрока для фильтрации пакетов'
        )
        
        return parser
    
    def _validate_arguments(self, args: argparse.Namespace) -> bool:
        """Валидация аргументов командной строки"""
        errors = []
        
        # Проверка формата имени пакета
        if ':' not in args.package:
            errors.append(f"Неверный формат пакета: '{args.package}'. Ожидается: groupId:artifactId")
        
        # Проверка максимальной глубины
        if args.max_depth <= 0:
            errors.append("Максимальная глубина должна быть положительным числом")
        
        # Проверка URL
        if args.url and not (args.url.startswith('http://') or args.url.startswith('https://')):
            errors.append(f"Некорректный URL: {args.url}")
        
        # Проверка пути к тестовому репозиторию
        if args.test_repo and not os.path.exists(args.test_repo):
            errors.append(f"Файл тестового репозитория не существует: {args.test_repo}")
        
        # Вывод ошибок
        if errors:
            print("Ошибки в параметрах:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return False
        
        return True
    
    def _convert_args_to_config(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Конвертация аргументов в конфигурацию"""
        config = {
            'package_name': args.package,
            'tree_output': args.tree,
            'max_depth': args.max_depth,
            'filter_substring': args.filter,
            'mode': 'test' if args.test_repo else 'remote'
        }
        
        if args.test_repo:
            config['repository_path'] = args.test_repo
        else:
            config['repository_url'] = args.url
        
        return config
    
    def print_config(self):
        """Вывод конфигурации в формате ключ-значение"""
        print("Текущая конфигурация:")
        print("-" * 40)
        for key, value in self.config.items():
            print(f"{key:20} : {value}")
        print("-" * 40)
    
    def run(self):
        """Основной метод запуска приложения"""
        try:
            # Парсинг аргументов
            args = self.parser.parse_args()
            
            # Валидация
            if not self._validate_arguments(args):
                sys.exit(1)
            
            # Конвертация в конфигурацию
            self.config = self._convert_args_to_config(args)
            
            # Вывод конфигурации (требование этапа 1)
            self.print_config()
            
            print("\nКонфигурация успешно загружена. Готов к анализу зависимостей!")
            
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Точка входа в приложение"""
    visualizer = DependencyGraphVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()