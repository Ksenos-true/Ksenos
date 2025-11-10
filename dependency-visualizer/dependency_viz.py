#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей пакетов Maven
Этап 1: Минимальный прототип с конфигурацией
"""

import argparse
import sys
from typing import Dict, Any

class DependencyVisualizer:
    def __init__(self):
        self.config = {}
        
    def setup_arg_parser(self) -> argparse.ArgumentParser:
        """Настройка парсера аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей Maven',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования:
  python dependency_viz.py --package com.example:my-app --url http://repo.maven.apache.org/maven2
  python dependency_viz.py --package org.springframework:spring-core --test-repo ./test-repo --max-depth 3
  python dependency_viz.py --package com.company:project --filter "spring" --tree
            """
        )
        
        # Обязательные параметры
        parser.add_argument(
            '--package',
            type=str,
            required=True,
            help='Имя анализируемого пакета (формат: groupId:artifactId)'
        )
        
        # Источник данных (взаимоисключающие опции)
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument(
            '--url',
            type=str,
            help='URL-адрес Maven репозитория'
        )
        source_group.add_argument(
            '--test-repo',
            type=str,
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
            type=str,
            help='Подстрока для фильтрации пакетов'
        )
        
        return parser
    
    def validate_arguments(self, args: argparse.Namespace) -> bool:
        """Валидация аргументов командной строки"""
        try:
            # Валидация имени пакета
            if not args.package or ':' not in args.package:
                raise ValueError("Имя пакета должно быть в формате groupId:artifactId")
            
            parts = args.package.split(':')
            if len(parts) != 2 or not all(parts):
                raise ValueError("Некорректный формат имени пакета. Ожидается: groupId:artifactId")
            
            # Валидация URL
            if args.url:
                if not args.url.startswith(('http://', 'https://')):
                    raise ValueError("URL должен начинаться с http:// или https://")
                if not args.url.strip():
                    raise ValueError("URL не может быть пустым")
            
            # Валидация пути к тестовому репозиторию
            if args.test_repo and not args.test_repo.strip():
                raise ValueError("Путь к тестовому репозиторию не может быть пустым")
            
            # Валидация максимальной глубины
            if args.max_depth <= 0:
                raise ValueError("Максимальная глубина должна быть положительным числом")
            if args.max_depth > 100:
                print("Предупреждение: очень большая глубина анализа может привести к длительному выполнению", 
                      file=sys.stderr)
            
            # Валидация фильтра
            if args.filter and not args.filter.strip():
                raise ValueError("Фильтр не может быть пустой строкой")
                
            return True
            
        except ValueError as e:
            print(f"Ошибка валидации параметров: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Неожиданная ошибка при валидации: {e}", file=sys.stderr)
            return False
    
    def parse_arguments(self) -> Dict[str, Any]:
        """Парсинг и валидация аргументов командной строки"""
        parser = self.setup_arg_parser()
        
        try:
            args = parser.parse_args()
            
            if not self.validate_arguments(args):
                sys.exit(1)
            
            # Определение режима работы
            mode = 'test' if args.test_repo else 'remote'
            repository_source = args.test_repo if args.test_repo else args.url
            
            # Сохранение конфигурации
            self.config = {
                'package_name': args.package,
                'repository_source': repository_source,
                'mode': mode,
                'output_tree': args.tree,
                'max_depth': args.max_depth,
                'filter_substring': args.filter
            }
            
            return self.config
            
        except argparse.ArgumentError as e:
            print(f"Ошибка в аргументах командной строки: {e}", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
        except SystemExit:
            # Перехват системного выхода от argparse для корректной обработки
            raise
        except Exception as e:
            print(f"Неожиданная ошибка при парсинге аргументов: {e}", file=sys.stderr)
            sys.exit(1)
    
    def display_configuration(self):
        """Вывод всех параметров в формате ключ-значение"""
        if not self.config:
            print("Конфигурация не загружена", file=sys.stderr)
            return
        
        print("=" * 50)
        print("КОНФИГУРАЦИЯ ПАРАМЕТРОВ")
        print("=" * 50)
        
        config_display = {
            'Анализируемый пакет': self.config['package_name'],
            'Источник данных': self.config['repository_source'],
            'Режим работы': 'Тестовый репозиторий' if self.config['mode'] == 'test' else 'Удаленный репозиторий',
            'Формат вывода': 'ASCII-дерево' if self.config['output_tree'] else 'Список',
            'Максимальная глубина': self.config['max_depth'],
            'Фильтр пакетов': self.config['filter_substring'] or 'Не задан'
        }
        
        for key, value in config_display.items():
            print(f"{key:<25}: {value}")
        
        print("=" * 50)
    
    def run(self):
        """Основной метод запуска приложения"""
        try:
            print("Запуск инструмента визуализации зависимостей...")
            print("Парсинг параметров командной строки...")
            
            config = self.parse_arguments()
            
            print("\nПараметры успешно загружены!")
            self.display_configuration()
            
            # Здесь будет основная логика анализа зависимостей на следующих этапах
            print("\nГотово к анализу зависимостей!")
            print(f"Будет анализироваться пакет: {config['package_name']}")
            
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем", file=sys.stderr)
            sys.exit(130)
        except Exception as e:
            print(f"Критическая ошибка: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    """Точка входа в приложение"""
    visualizer = DependencyVisualizer()
    visualizer.run()

if __name__ == "__main__":
    main()