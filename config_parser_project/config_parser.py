#!/usr/bin/env python3
"""
Парсер учебного конфигурационного языка (Вариант 19)
Преобразует входной формат в YAML
"""

import sys
import argparse
from typing import Any
import yaml
from lark import Lark, Transformer, LarkError


GRAMMAR = r"""
start: (declaration | dictionary)*

declaration: "var" NAME value -> var_decl
constant_expr: "?(" expr ")" -> const_expr

expr: term
    | expr "+" term -> add
    | expr "-" term -> sub

term: atom
    | "chr(" expr ")" -> chr_func
    | "mod(" expr "," expr ")" -> mod_func

atom: NUMBER -> number_atom
    | NAME -> var_ref
    | constant_expr
    | "(" expr ")"

dictionary: "{" [pair ("," pair)*] "}" -> make_dict

pair: NAME "=>" value

value: NUMBER -> number_value
     | STRING -> string_value
     | dictionary -> dict_value
     | constant_expr -> const_value

NUMBER: /[+-]?\d+\.\d+/
STRING: /\[\[(?:[^\]\[]|\[\[](?!\])|\](?!\]))*(?:\]\])?/
NAME: /[a-zA-Z][_a-zA-Z0-9]*/
COMMENT: /--[^\n]*/

%ignore COMMENT
%ignore /[ \t\r\n\f]+/
"""


class ConfigTransformer(Transformer):
    """Трансформер для преобразования AST в Python-структуры"""
    
    def __init__(self):
        super().__init__()
        self.constants = {}
    
    def string_value(self, items):
        """Обработка строк [[...]]"""
        token = items[0]
        content = token.value
        # Убираем [[ и ]]
        if content.startswith('[[') and content.endswith(']]'):
            return content[2:-2]
        return content[2:]  # Если закрывающих скобок нет
    
    def number_value(self, items):
        """Обработка чисел"""
        token = items[0]
        return float(token.value)
    
    def const_value(self, items):
        """Обработка константных выражений"""
        return items[0]
    
    def dict_value(self, items):
        """Обработка словарей как значений"""
        return items[0]
    
    def make_dict(self, items):
        """Создание словаря"""
        if items and items[0] is not None:
            return dict(items)
        return {}
    
    def pair(self, items):
        """Обработка пары ключ-значение"""
        name_token, value = items
        return (str(name_token), value)
    
    def var_decl(self, items):
        """Обработка объявления константы var"""
        name_token, value = items
        name = str(name_token)
        self.constants[name] = value
        return None  # Объявления не попадают в результат
    
    def const_expr(self, items):
        """Обработка выражения ?(...)"""
        return items[0]
    
    def var_ref(self, items):
        """Обработка ссылки на константу"""
        name = str(items[0])
        if name not in self.constants:
            raise ValueError(f"Неизвестная константа: {name}")
        return self.constants[name]
    
    def number_atom(self, items):
        """Обработка числа в выражении"""
        token = items[0]
        return float(token.value)
    
    def add(self, items):
        """Обработка сложения"""
        left, right = items
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        raise ValueError("Несовместимые типы для сложения")
    
    def sub(self, items):
        """Обработка вычитания"""
        left, right = items
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left - right
        raise ValueError("Несовместимые типы для вычитания")
    
    def chr_func(self, items):
        """Обработка функции chr()"""
        arg = items[0]
        if isinstance(arg, (int, float)):
            code = int(arg)
            if 0 <= code <= 0x10FFFF:
                return chr(code)
        raise ValueError(f"Недопустимый аргумент для chr(): {arg}")
    
    def mod_func(self, items):
        """Обработка функции mod()"""
        a, b = items
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if b == 0:
                raise ValueError("Деление на ноль в mod()")
            return a % b
        raise ValueError("Несовместимые типы для mod()")
    
    def start(self, items):
        """Формирование конечного результата"""
        result = {}
        for item in items:
            if item is not None and isinstance(item, dict):
                result.update(item)
        return result


def parse_config(input_text: str) -> Any:
    """Парсит конфигурацию из текста"""
    parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
    try:
        return parser.parse(input_text)
    except LarkError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка вычисления: {e}", file=sys.stderr)
        sys.exit(1)


def convert_to_yaml(data: Any) -> str:
    """Конвертирует данные в YAML"""
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)


def main():
    """Основная функция командной строки"""
    parser = argparse.ArgumentParser(
        description='Конвертер учебного конфигурационного языка в YAML\nВариант 19',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python config_parser.py -o output.yaml < config.txt
  type config.txt | python config_parser.py -o output.yaml
  python config_parser.py -o result.yaml (ввести текст, Ctrl+Z+Enter)
        """
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Путь к выходному YAML файлу'
    )
    
    args = parser.parse_args()
    
    # Чтение из стандартного ввода
    input_text = sys.stdin.read()
    
    if not input_text.strip():
        print("Ошибка: входные данные не предоставлены", file=sys.stderr)
        print("Используйте: python config_parser.py -o файл.yaml < входной_файл.conf", file=sys.stderr)
        sys.exit(1)
    
    # Парсинг и преобразование
    config_data = parse_config(input_text)
    yaml_output = convert_to_yaml(config_data)
    
    # Запись в файл
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(yaml_output)
        print(f"✅ Конфигурация успешно сохранена в {args.output}", file=sys.stderr)
    except IOError as e:
        print(f"❌ Ошибка записи в файл: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()