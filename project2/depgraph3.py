#!/usr/bin/env python3

import argparse
import sys
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Set
import urllib.request
import urllib.error
import subprocess
from collections import deque


class DependencyGraphVisualizer:
    def __init__(self):
        self.config = {}
        self.parser = self._setup_parser()
        self.dependency_graph = {}
        self.visited_packages = set()
    
    def _setup_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description='Визуализатор графа зависимостей для Maven пакетов',
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        
        parser.add_argument(
            '--package',
            required=True,
            help='Имя анализируемого пакета (формат: groupId:artifactId)'
        )
        
        source_group = parser.add_mutually_exclusive_group(required=False)
        source_group.add_argument(
            '--url',
            help='URL-адрес Maven репозитория'
        )
        source_group.add_argument(
            '--test-repo',
            action='store_true',
            help='Использовать тестовый режим'
        )
        
        parser.add_argument(
            '--tree',
            action='store_true',
            help='Режим вывода зависимостей в формате ASCII-дерева'
        )
        
        parser.add_argument(
            '--max-depth',
            type=int,
            default=3,
            help='Максимальная глубина анализа зависимостей'
        )
        
        parser.add_argument(
            '--filter',
            help='Подстрока для фильтрации пакетов'
        )
        
        parser.add_argument(
            '--visualize',
            action='store_true',
            help='Создать визуализацию графа в формате D2'
        )
        
        return parser
    
    def _validate_arguments(self, args: argparse.Namespace) -> bool:
        errors = []
        
        if ':' not in args.package:
            errors.append(f"Неверный формат пакета: '{args.package}'. Ожидается: groupId:artifactId")
        
        if args.max_depth <= 0:
            errors.append("Максимальная глубина должна быть положительным числом")
        
        if args.url and not (args.url.startswith('http://') or args.url.startswith('https://')):
            errors.append(f"Некорректный URL: {args.url}")
        
        if not args.url and not args.test_repo:
            args.test_repo = True
        
        if errors:
            print("Ошибки в параметрах:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return False
        
        return True
    
    def _convert_args_to_config(self, args: argparse.Namespace) -> Dict[str, Any]:
        config = {
            'package_name': args.package,
            'tree_output': args.tree,
            'max_depth': args.max_depth,
            'filter_substring': args.filter,
            'visualize': args.visualize,
            'mode': 'test' if args.test_repo else 'remote'
        }
        
        if args.test_repo:
            config['repository_path'] = None
        else:
            config['repository_url'] = args.url
        
        return config
    
    def print_config(self):
        print("Текущая конфигурация:")
        print("-" * 40)
        for key, value in self.config.items():
            print(f"{key:20} : {value}")
        print("-" * 40)
    
    def _download_pom_file(self, group_id: str, artifact_id: str, version: str = "latest") -> str:
        base_url = self.config['repository_url']
        
        group_path = group_id.replace('.', '/')
        if version == "latest":
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
                
                versions = versioning.find('versions')
                if versions is not None:
                    version_list = [v.text for v in versions.findall('version')]
                    if version_list:
                        stable_versions = [v for v in version_list if 'SNAPSHOT' not in v]
                        if stable_versions:
                            return max(stable_versions)
                        return max(version_list)
        except ET.ParseError:
            pass
        return None
    
    def _parse_dependencies_from_pom(self, pom_content: str) -> List[Dict[str, str]]:
        dependencies = []
        
        try:
            root = ET.fromstring(pom_content)
            
            namespaces = {'maven': 'http://maven.apache.org/POM/4.0.0'}
            
            dependencies_elem = root.find('.//dependencies')
            if dependencies_elem is None:
                dependencies_elem = root.find('.//maven:dependencies', namespaces)
            if dependencies_elem is None:
                return dependencies
            
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
        if not self.config['filter_substring']:
            return dependencies
        
        filter_str = self.config['filter_substring'].lower()
        filtered = []
        
        for dep in dependencies:
            dep_str = f"{dep['groupId']}:{dep['artifactId']}:{dep['version']}".lower()
            if filter_str in dep_str:
                filtered.append(dep)
        
        return filtered
    
    def get_package_dependencies(self, package: str, current_depth: int = 0) -> List[Dict[str, str]]:
        if current_depth >= self.config['max_depth']:
            return []
        
        package_parts = package.split(':')
        if len(package_parts) != 2:
            return []
        
        group_id, artifact_id = package_parts
        
        if self.config['mode'] == 'remote':
            try:
                pom_content = self._download_pom_file(group_id, artifact_id)
                dependencies = self._parse_dependencies_from_pom(pom_content)
            except Exception as e:
                print(f"Ошибка получения зависимостей для {package}: {e}")
                return []
        else:
            dependencies = self._get_test_dependencies(group_id, artifact_id)
        
        return dependencies
    
    def build_dependency_graph(self):
        root_package = self.config['package_name']
        print(f"\nПостроение графа зависимостей для: {root_package}")
        print(f"Максимальная глубина: {self.config['max_depth']}")
        
        queue = deque([(root_package, 0)])
        self.dependency_graph = {}
        self.visited_packages = set()
        
        while queue:
            current_package, depth = queue.popleft()
            
            if current_package in self.visited_packages:
                continue
                
            self.visited_packages.add(current_package)
            
            print(f"Анализ пакета ({depth} уровень): {current_package}")
            dependencies = self.get_package_dependencies(current_package, depth)
            
            dependencies = self._apply_filter(dependencies)
            
            self.dependency_graph[current_package] = dependencies
            
            if depth + 1 < self.config['max_depth']:
                for dep in dependencies:
                    dep_key = f"{dep['groupId']}:{dep['artifactId']}"
                    if dep_key not in self.visited_packages:
                        queue.append((dep_key, depth + 1))
        
        print(f"Граф построен. Всего пакетов: {len(self.dependency_graph)}")
    
    def _get_test_dependencies(self, group_id: str, artifact_id: str) -> List[Dict[str, str]]:
        test_dependencies = {
            'junit:junit': [
                {'groupId': 'org.hamcrest', 'artifactId': 'hamcrest-core', 'version': '2.2'},
            ],
            'org.springframework:spring-core': [
                {'groupId': 'commons-logging', 'artifactId': 'commons-logging', 'version': '1.2'},
                {'groupId': 'org.springframework', 'artifactId': 'spring-jcl', 'version': '5.3.23'},
            ],
            'org.springframework:spring-jcl': [
                {'groupId': 'org.slf4j', 'artifactId': 'slf4j-api', 'version': '1.7.36'},
            ],
            'org.hamcrest:hamcrest-core': [
                {'groupId': 'org.hamcrest', 'artifactId': 'hamcrest-library', 'version': '2.2'},
            ],
            'org.hamcrest:hamcrest-library': [
                {'groupId': 'junit', 'artifactId': 'junit', 'version': '4.13.2'},
            ],
            'com.example:my-app': [
                {'groupId': 'junit', 'artifactId': 'junit', 'version': '4.13.2'},
                {'groupId': 'org.springframework', 'artifactId': 'spring-core', 'version': '5.3.23'},
                {'groupId': 'com.google.guava', 'artifactId': 'guava', 'version': '31.1-jre'},
            ],
            'com.google.guava:guava': [
                {'groupId': 'com.google.guava', 'artifactId': 'failureaccess', 'version': '1.0.1'},
                {'groupId': 'com.google.guava', 'artifactId': 'listenablefuture', 'version': '9999.0-empty-to-avoid-conflict-with-guava'},
            ],
            'default': [
                {'groupId': 'junit', 'artifactId': 'junit', 'version': '4.13.2'},
                {'groupId': 'org.slf4j', 'artifactId': 'slf4j-api', 'version': '1.7.36'},
            ]
        }
        
        package_key = f"{group_id}:{artifact_id}"
        return test_dependencies.get(package_key, test_dependencies['default'])
    
    def print_direct_dependencies(self):
        root_package = self.config['package_name']
        if root_package not in self.dependency_graph:
            print("Прямые зависимости не найдены")
            return
        
        dependencies = self.dependency_graph[root_package]
        if not dependencies:
            print("Прямые зависимости не найдены")
            return
        
        print(f"\nПрямые зависимости ({len(dependencies)}):")
        print("-" * 60)
        for i, dep in enumerate(dependencies, 1):
            print(f"{i:2}. {dep['groupId']}:{dep['artifactId']}:{dep['version']}")
        print("-" * 60)
    
    def print_ascii_tree(self):
        if not self.dependency_graph:
            print("Граф зависимостей пуст")
            return
        
        root_package = self.config['package_name']
        print(f"\nДерево зависимостей для: {root_package}")
        print("=" * 50)
        
        self._print_tree_node(root_package, 0, set())
    
    def _print_tree_node(self, package: str, level: int, visited: Set[str]):
        if package in visited:
            indent = "  " * level
            print(f"{indent}└── {package} (циклическая зависимость)")
            return
        
        visited.add(package)
        indent = "  " * level
        connector = "└── " if level > 0 else ""
        
        print(f"{indent}{connector}{package}")
        
        if package in self.dependency_graph:
            dependencies = self.dependency_graph[package]
            for i, dep in enumerate(dependencies):
                dep_key = f"{dep['groupId']}:{dep['artifactId']}"
                is_last = i == len(dependencies) - 1
                new_indent = "  " * (level + 1)
                connector = "└── " if is_last else "├── "
                
                if level + 1 < self.config['max_depth']:
                    self._print_tree_node(dep_key, level + 1, visited.copy())
                else:
                    print(f"{new_indent}{connector}{dep_key} (глубина ограничена)")
        
        visited.remove(package)
    
    def generate_d2_diagram(self) -> str:
        d2_content = "# Граф зависимостей Maven\n\n"
        d2_content += "direction: right\n"
        d2_content += "classes: {\n  style: {\n    stroke: green\n    fill: lightgreen\n  }\n}\n\n"
        
        # Добавляем все узлы
        for package in self.dependency_graph:
            d2_content += f'"{package}"\n'
        
        # Добавляем связи
        for package, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                dep_key = f"{dep['groupId']}:{dep['artifactId']}"
                d2_content += f'"{package}" -> "{dep_key}"\n'
        
        return d2_content
    
    def visualize_graph(self):
        if not self.dependency_graph:
            print("Нет данных для визуализации")
            return
        
        d2_content = self.generate_d2_diagram()
        
        print("\n" + "="*60)
        print("D2 ДИАГРАММА ГРАФА ЗАВИСИМОСТЕЙ")
        print("="*60)
        print(d2_content)
        print("="*60)
        
        d2_filename = f"dependency_graph_{self.config['package_name'].replace(':', '_')}.d2"
        with open(d2_filename, 'w', encoding='utf-8') as f:
            f.write(d2_content)
        print(f"D2 диаграмма сохранена в файл: {d2_filename}")
        
        try:
            output_png = f"dependency_graph_{self.config['package_name'].replace(':', '_')}.png"
            result = subprocess.run(['d2', d2_filename, output_png], check=True, capture_output=True, text=True)
            print(f"Визуализация сохранена в файл: {output_png}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Для создания PNG визуализации установите D2: https://d2lang.com/")
    
    def compare_with_maven(self):
        print("\n" + "="*60)
        print("СРАВНЕНИЕ С ИНСТРУМЕНТАМИ MAVEN")
        print("="*60)
        
        print("""
Расхождения с штатными инструментами Maven могут возникать по причинам:

1. Упрощенный анализ - наш инструмент не учитывает:
   - Dependency Management из родительских POM
   - Профили Maven (profiles)
   - Свойства (properties) и их разрешение
   - Scope зависимостей (compile, test, provided, runtime)
   - Опциональные зависимости
   - Исключения зависимостей (exclusions)

2. Ограниченная глубина - анализируется только указанная глубина

3. Тестовый режим - использует демонстрационные данные вместо реальных

4. Отсутствие разрешения конфликтов версий

Для точного анализа рекомендуется использовать:
   mvn dependency:tree
   mvn dependency:analyze
        """)
    
    def demonstrate_examples(self):
        print("\n" + "="*60)
        print("ДЕМОНСТРАЦИЯ ПРИМЕРОВ ВИЗУАЛИЗАЦИИ")
        print("="*60)
        
        examples = [
            "junit:junit",
            "org.springframework:spring-core", 
            "com.example:my-app"
        ]
        
        for example in examples:
            print(f"\nПример: {example}")
            print("-" * 40)
            
            original_package = self.config['package_name']
            self.config['package_name'] = example
            
            self.build_dependency_graph()
            
            total_deps = sum(len(deps) for deps in self.dependency_graph.values())
            print(f"Всего зависимостей: {total_deps}")
            print(f"Узлов в графе: {len(self.dependency_graph)}")
            
            self.config['package_name'] = original_package
            self.dependency_graph = {}
    
    def run(self):
        try:
            args = self.parser.parse_args()
            
            if not self._validate_arguments(args):
                sys.exit(1)
            
            self.config = self._convert_args_to_config(args)
            
            self.print_config()
            
            self.build_dependency_graph()
            
            self.print_direct_dependencies()
            
            if self.config['tree_output']:
                self.print_ascii_tree()
            
            if self.config['visualize']:
                self.visualize_graph()
            
            self.demonstrate_examples()
            
            self.compare_with_maven()
            
            print("\nАнализ зависимостей завершен успешно!")
            
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            sys.exit(1)
        except Exception as e:
            print(f"\nОшибка: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    visualizer = DependencyGraphVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()