import json
import base64
import os

class VFSManager:
    def __init__(self):
        self.vfs_data = None
        self.vfs_path = None
    
    def load_vfs(self, vfs_path):
        """Загружает VFS из JSON файла"""
        self.vfs_path = vfs_path
        
        try:
            # Проверяем существование файла
            if not os.path.exists(vfs_path):
                raise FileNotFoundError(f"VFS файл не найден: {vfs_path}")
            
            # Читаем и парсим JSON
            with open(vfs_path, 'r', encoding='utf-8') as f:
                self.vfs_data = json.load(f)
            
            # Проверяем структуру VFS
            if not isinstance(self.vfs_data, dict):
                raise ValueError("VFS должен быть объектом JSON")
            
            print(f"✓ VFS успешно загружена из: {vfs_path}")
            print(f"  Корневая папка: {self.vfs_data.get('name', 'root')}")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Неверный формат JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки VFS: {e}")
    
    def get_file_content(self, file_path):
        """Получает содержимое файла из VFS"""
        if not self.vfs_data:
            raise RuntimeError("VFS не загружена")
        
        # Разбиваем путь на части
        parts = [p for p in file_path.split('/') if p]
        current = self.vfs_data
        
        try:
            # Проходим по пути
            for part in parts:
                if 'children' not in current:
                    return None
                found = False
                for child in current['children']:
                    if child['name'] == part:
                        current = child
                        found = True
                        break
                if not found:
                    return None
            
            # Проверяем что это файл
            if current.get('type') != 'file':
                return None
            
            # Декодируем содержимое
            content = current.get('content', '')
            if current.get('encoding') == 'base64':
                return base64.b64decode(content).decode('utf-8')
            else:
                return content
                
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения файла {file_path}: {e}")
    
    def list_directory(self, dir_path=''):
        """Список содержимого директории"""
        if not self.vfs_data:
            raise RuntimeError("VFS не загружена")
        
        parts = [p for p in dir_path.split('/') if p]
        current = self.vfs_data
        
        try:
            # Проходим по пути
            for part in parts:
                if 'children' not in current:
                    return None  # ИСПРАВЛЕНО: возвращаем None если нет children
                found = False
                for child in current['children']:
                    if child['name'] == part and child.get('type') == 'directory':
                        current = child
                        found = True
                        break
                if not found:
                    return None  # ИСПРАВЛЕНО: возвращаем None если путь не найден
            
            # Возвращаем список детей
            if 'children' not in current:
                return []
            
            result = []
            for child in current['children']:
                result.append({
                    'name': child['name'],
                    'type': child.get('type', 'unknown'),
                    'size': len(child.get('content', '')) if child.get('type') == 'file' else 0
                })
            return result
            
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения директории {dir_path}: {e}")
    
    def get_vfs_info(self):
        """Возвращает информацию о VFS"""
        if not self.vfs_data:
            return "VFS не загружена"
        
        def count_items(node):
            if node.get('type') == 'file':
                return 1, 0
            files = 0
            folders = 1
            for child in node.get('children', []):
                f, d = count_items(child)
                files += f
                folders += d
            return files, folders
        
        files, folders = count_items(self.vfs_data)
        return f"VFS: {self.vfs_data.get('name', 'root')} | Файлов: {files} | Папок: {folders}"