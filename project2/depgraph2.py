#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для Maven пакетов
Этап 1 + 2: Конфигурация и сбор данных о зависимостях
"""

import argparse
import sys
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
import urllib.request
import urllib.error


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
  python depgraph2.py --package junit:junit --url https://repo1.maven.org/maven2
  python depgraph2.py --package org.springframework:spring-core --test-repo
  python depgraph2.py --package com.example:my-app --filter "test" --tree
            """
        )
        
        # Обязательные параметры
        parser.add_argument(
            '--package',
            required=True,
            help='Имя анализируемого пакета (формат: groupId:artifactId)'
        )
        
        # Источник данных (взаимоисключающие опции)
        source_group = parser.add_mutually_exclusive_group(required=False)
        source_group.add_argument(
            '--url',
            help='URL-адрес Maven репозитория'
        )
        source_group.add_argument(
            '--test-repo',
            action='store_true',
            help='Использовать тестовый режим (по умолчанию)'
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
        
        # Если не указан ни url, ни test-repo, используем тестовый режим по умолчанию
        if not args.url and not args.test_repo:
            args.test_repo = True
        
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
            config['repository_path'] = None  # Тестовый режим не требует пути
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
    
    def _download_pom_file(self, group_id: str, artifact_id: str, version: str = "latest") -> str:
        """Загрузка POM файла из Maven репозитория"""
        base_url = self.config['repository_url']
        
        # Формируем URL для POM файла
        group_path = group_id.replace('.', '/')
        if version == "latest":
            # Для получения latest версии сначала получаем метаданные
            metadata_url = f"{base_url}/{group_path}/{artifact_id}/maven-metadata.xml"
            try:
                with urllib.request.urlopen(metadata_url) as response:
                    metadata_content = response.read().decode('utf-8')
                version = self._parse_latest_version(metadata_content)
                if not version:
                    raise Exception(f"Не удалось определить latest версию для {group_id}:{artifact_id}")
                print(f"Используется версия: {version}")
            except urllib.error.HTTPError as e:
                raise Exception(f"Ошибка загрузки метаданных: {e.code} {e.reason}")
            except urllib.error.URLError as e:
                raise Exception(f"Ошибка подключения: {e.reason}")
        
        pom_url = f"{base_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
        print(f"Загрузка POM: {pom_url}")
        
        try:
            with urllib.request.urlopen(pom_url) as response:
                pom_content = response.read().decode('utf-8')
            return pom_content
        except urllib.error.HTTPError as e:
            raise Exception(f"Ошибка загрузки POM: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"Ошибка подключения: {e.reason}")
    
    def _parse_latest_version(self, metadata_content: str) -> str:
        """Парсинг latest версии из maven-metadata.xml"""
        try:
            root = ET.fromstring(metadata_content)
            versioning = root.find('versioning')
            if versioning is not None:
                latest = versioning.find('latest')
                if latest is not None:
                    return latest.text
                
                release = versioning.find('release')
                if release is not None:
                    return release.text
                
                # Если нет latest, берем последнюю из versions
                versions = versioning.find('versions')
                if versions is not None:
                    version_list = [v.text for v in versions.findall('version')]
                    if version_list:
                        # Фильтруем только стабильные версии (без SNAPSHOT)
                        stable_versions = [v for v in version_list if 'SNAPSHOT' not in v]
                        if stable_versions:
                            return max(stable_versions)
                        return max(version_list)
        except ET.ParseError:
            pass
        return None
    
    def _parse_dependencies_from_pom(self, pom_content: str) -> List[Dict[str, str]]:
        """Парсинг зависимостей из POM файла"""
        dependencies = []
        
        try:
            root = ET.fromstring(pom_content)
            
            # Находим секцию dependencies
            namespaces = {'maven': 'http://maven.apache.org/POM/4.0.0'}
            
            # Пробуем разные варианты поиска dependencies
            dependencies_elem = root.find('.//dependencies')
            if dependencies_elem is None:
                dependencies_elem = root.find('.//maven:dependencies', namespaces)
            if dependencies_elem is None:
                return dependencies
            
            # Парсим каждую зависимость
            for dep_elem in dependencies_elem.findall('dependency'):
                group_id_elem = dep_elem.find('groupId')
                artifact_id_elem = dep_elem.find('artifactId')
                version_elem = dep_elem.find('version')
                
                if group_id_elem is not None and artifact_id_elem is not None:
                    dependency = {
                        'groupId': group_id_elem.text,
                        'artifactId': artifact_id_elem.text,
                        'version': version_elem.text if version_elem is not None else 'unknown'
                    }
                    dependencies.append(dependency)
                    
        except ET.ParseError as e:
            raise Exception(f"Ошибка парсинга POM файла: {e}")
        
        return dependencies
    
    def _apply_filter(self, dependencies: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Применение фильтра к зависимостям"""
        if not self.config['filter_substring']:
            return dependencies
        
        filter_str = self.config['filter_substring'].lower()
        filtered = []
        
        for dep in dependencies:
            dep_str = f"{dep['groupId']}:{dep['artifactId']}:{dep['version']}".lower()
            if filter_str in dep_str:
                filtered.append(dep)
        
        return filtered
    
    def get_dependencies(self) -> List[Dict[str, str]]:
        """Получение прямых зависимостей пакета"""
        package_parts = self.config['package_name'].split(':')
        if len(package_parts) != 2:
            raise Exception("Неверный формат имени пакета")
        
        group_id, artifact_id = package_parts
        
        print(f"\nПолучение зависимостей для: {group_id}:{artifact_id}")
        
        if self.config['mode'] == 'remote':
            # Режим работы с удаленным репозиторием
            pom_content = self._download_pom_file(group_id, artifact_id)
            print("POM файл успешно загружен")
            
            # Парсим зависимости из POM
            dependencies = self._parse_dependencies_from_pom(pom_content)
            
        else:
            # Тестовый режим - используем демонстрационные данные
            print("Используется тестовый режим")
            dependencies = self._get_test_dependencies(group_id, artifact_id)
        
        # Применяем фильтр если задан
        dependencies = self._apply_filter(dependencies)
        
        return dependencies
    
    def _get_test_dependencies(self, group_id: str, artifact_id: str) -> List[Dict[str, str]]:
        """Генерация тестовых зависимостей для демонстрации"""
        # Разные наборы тестовых зависимостей для разных пакетов
        test_dependencies = {
            'junit:junit': [
                {'groupId': 'org.hamcrest', 'artifactId': 'hamcrest-core', 'version': '2.2'},
                {'groupId': 'org.hamcrest', 'artifactId': 'hamcrest-library', 'version': '2.2'},
            ],
            'org.springframework:spring-core': [
                {'groupId': 'commons-logging', 'artifactId': 'commons-logging', 'version': '1.2'},
                {'groupId': 'org.springframework', 'artifactId': 'spring-jcl', 'version': '5.3.23'},
                {'groupId': 'org.springframework', 'artifactId': 'spring-test', 'version': '5.3.23'},
            ],
            'com.example:my-app': [
                {'groupId': 'junit', 'artifactId': 'junit', 'version': '4.13.2'},
                {'groupId': 'org.mockito', 'artifactId': 'mockito-core', 'version': '4.5.1'},
                {'groupId': 'com.google.guava', 'artifactId': 'guava', 'version': '31.1-jre'},
                {'groupId': 'org.slf4j', 'artifactId': 'slf4j-api', 'version': '1.7.36'},
                {'groupId': 'org.springframework', 'artifactId': 'spring-context', 'version': '5.3.23'},
            ],
            'default': [
                {'groupId': 'junit', 'artifactId': 'junit', 'version': '4.13.2'},
                {'groupId': 'org.slf4j', 'artifactId': 'slf4j-api', 'version': '1.7.36'},
                {'groupId': 'com.fasterxml.jackson.core', 'artifactId': 'jackson-databind', 'version': '2.14.1'},
            ]
        }
        
        package_key = f"{group_id}:{artifact_id}"
        return test_dependencies.get(package_key, test_dependencies['default'])
    
    def print_dependencies(self, dependencies: List[Dict[str, str]]):
        """Вывод зависимостей на экран (требование этапа 2)"""
        if not dependencies:
            print("Прямые зависимости не найдены")
            return
        
        print(f"\nПрямые зависимости ({len(dependencies)}):")
        print("-" * 60)
        for i, dep in enumerate(dependencies, 1):
            print(f"{i:2}. {dep['groupId']}:{dep['artifactId']}:{dep['version']}")
        print("-" * 60)
    
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
            
            # Получение и вывод зависимостей (требование этапа 2)
            dependencies = self.get_dependencies()
            self.print_dependencies(dependencies)
            
            print("\nАнализ зависимостей завершен успешно!")
            
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            sys.exit(1)
        except Exception as e:
            print(f"\nОшибка: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Точка входа в приложение"""
    visualizer = DependencyGraphVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()