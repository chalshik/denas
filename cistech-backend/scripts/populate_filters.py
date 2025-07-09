import json
import sys
import os
from pathlib import Path

# Добавляем корневую папку проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.product.category import Category
from app.models.product.filter import FilterType, FilterOption

def load_filters_from_json(json_file_path):
    """Загрузка фильтров из JSON файла"""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def populate_database():
    """Заполнение базы данных категориями и фильтрами"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Путь к JSON файлу с фильтрами
        json_file_path = project_root / ".." / "cistech-frontend" / "components" / "catalog" / "filter.json"
        
        if not json_file_path.exists():
            print(f"Файл {json_file_path} не найден!")
            return
        
        # Загружаем данные из JSON
        filters_data = load_filters_from_json(json_file_path)
        
        print("Начинаем заполнение базы данных...")
        
        # Добавляем категории
        categories_added = 0
        for category_name in filters_data.keys():
            # Проверяем, существует ли уже такая категория
            existing_category = db.query(Category).filter(Category.name == category_name).first()
            if not existing_category:
                category = Category(name=category_name)
                db.add(category)
                categories_added += 1
                print(f"Добавлена категория: {category_name}")
        
        # Сохраняем категории
        db.commit()
        print(f"Добавлено категорий: {categories_added}")
        
        # Добавляем типы фильтров и их опции
        filter_types_added = 0
        filter_options_added = 0
        
        for category_name, filters in filters_data.items():
            print(f"\nОбрабатываем фильтры для категории: {category_name}")
            
            # Получаем категорию
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                print(f"Категория {category_name} не найдена!")
                continue
            
            for filter_type_name, options in filters.items():
                # Проверяем, существует ли уже такой тип фильтра для данной категории
                existing_filter_type = db.query(FilterType).filter(
                    FilterType.name == filter_type_name,
                    FilterType.category_id == category.id
                ).first()
                
                if not existing_filter_type:
                    filter_type = FilterType(
                        name=filter_type_name,
                        category_id=category.id
                    )
                    db.add(filter_type)
                    db.flush()  # Получаем ID для нового типа фильтра
                    filter_types_added += 1
                    print(f"  Добавлен тип фильтра: {filter_type_name}")
                else:
                    filter_type = existing_filter_type
                    print(f"  Тип фильтра уже существует: {filter_type_name}")
                
                # Добавляем опции для этого типа фильтра
                for option_value in options:
                    # Проверяем, существует ли уже такая опция для данного типа фильтра
                    existing_option = db.query(FilterOption).filter(
                        FilterOption.filter_type_id == filter_type.id,
                        FilterOption.value == option_value
                    ).first()
                    
                    if not existing_option:
                        filter_option = FilterOption(
                            filter_type_id=filter_type.id,
                            value=option_value
                        )
                        db.add(filter_option)
                        filter_options_added += 1
                        print(f"    Добавлена опция: {option_value}")
        
        # Сохраняем все изменения
        db.commit()
        
        print(f"\n{'='*50}")
        print("РЕЗУЛЬТАТЫ ЗАПОЛНЕНИЯ:")
        print(f"{'='*50}")
        print(f"Добавлено категорий: {categories_added}")
        print(f"Добавлено типов фильтров: {filter_types_added}")
        print(f"Добавлено опций фильтров: {filter_options_added}")
        print("Заполнение базы данных завершено успешно!")
        
    except Exception as e:
        print(f"Ошибка при заполнении базы данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()