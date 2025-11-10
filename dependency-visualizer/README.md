# Инструмент визуализации графа зависимостей Maven

## Описание
CLI-инструмент для анализа и визуализации зависимостей пакетов Maven без использования готовых менеджеров пакетов.

## Этап 1: Минимальный прототип с конфигурацией

### Функциональность
- Парсинг параметров командной строки
- Валидация входных параметров
- Вывод конфигурации в формате ключ-значение
- Обработка ошибок

### Использование
```bash
python dependency_viz.py --package groupId:artifactId --url http://repo.maven.apache.org/maven2
python dependency_viz.py --package groupId:artifactId --test-repo ./repo --max-depth 5 --tree --filter "spring"