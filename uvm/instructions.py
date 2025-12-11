"""Определения команд УВМ"""

class Instruction:
    """Базовый класс для инструкций"""
    def __init__(self, opcode, name, description, fields=None):
        self.opcode = opcode
        self.name = name
        self.description = description
        self.fields = fields or {}
    
    def encode(self, **kwargs):
        """Кодирование инструкции в бинарный формат"""
        raise NotImplementedError
    
    def decode(self, data):
        """Декодирование инструкции из бинарного формата"""
        raise NotImplementedError

# Определения команд согласно спецификации
INSTRUCTIONS = {
    'LOAD_CONST': Instruction(
        opcode=43,
        name='LOAD_CONST',
        description='Загрузка константы на стек',
        fields={'B': 'Константа (10 бит)'}
    ),
    'READ_MEM': Instruction(
        opcode=120,
        name='READ_MEM',
        description='Чтение значения из памяти',
        fields={'B': 'Смещение (10 бит)'}
    ),
    'WRITE_MEM': Instruction(
        opcode=72,
        name='WRITE_MEM',
        description='Запись значения в память',
        fields={}
    ),
    'DIV': Instruction(
        opcode=121,
        name='DIV',
        description='Деление',
        fields={'B': 'Адрес (19 бит)'}
    )
}

def get_instruction_by_opcode(opcode):
    """Получить инструкцию по коду операции"""
    for instr in INSTRUCTIONS.values():
        if instr.opcode == opcode:
            return instr
    return None

def get_instruction_by_name(name):
    """Получить инструкцию по имени"""
    return INSTRUCTIONS.get(name.upper())