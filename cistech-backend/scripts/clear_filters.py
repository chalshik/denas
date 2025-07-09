import sys
from pathlib import Path

# Добавляем корневую папку проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.product.category import Category
from app.models.product.filter import FilterType, FilterOption

def clear_database():
    """Очистка данных фильтров и категорий"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("ВНИМАНИЕ! Этот скрипт удалит ВСЕ категории и фильтры!")
        print("Это действие необратимо!")
        print("-" * 50)
        
        # Показываем текущее состояние
        categories_count = db.query(Category).count()
        filter_types_count = db.query(FilterType).count()
        filter_options_count = db.query(FilterOption).count()
        
        print(f"Текущее состояние базы данных:")
        print(f"  - Категорий: {categories_count}")
        print(f"  - Типов фильтров: {filter_types_count}")
        print(f"  - Опций фильтров: {filter_options_count}")
        print("-" * 50)
        
        if categories_count == 0 and filter_types_count == 0 and filter_options_count == 0:
            print("База данных уже пуста!")
            return
        
        confirm = input("Вы уверены? Введите 'DELETE' для подтверждения: ")
        
        if confirm != 'DELETE':
            print("Операция отменена.")
            return
        
        print("\nНачинаем очистку...")
        
        # Удаляем в правильном порядке (сначала дочерние, потом родительские)
        print("Удаляем опции фильтров...")
        options_deleted = db.query(FilterOption).delete()
        print(f"  Удалено опций: {options_deleted}")
        
        print("Удаляем типы фильтров...")
        types_deleted = db.query(FilterType).delete()
        print(f"  Удалено типов фильтров: {types_deleted}")
        
        print("Удаляем категории...")
        categories_deleted = db.query(Category).delete()
        print(f"  Удалено категорий: {categories_deleted}")
        
        # Подтверждаем изменения
        db.commit()
        
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ ОЧИСТКИ:")
        print("=" * 50)
        print(f"Удалено опций фильтров: {options_deleted}")
        print(f"Удалено типов фильтров: {types_deleted}")
        print(f"Удалено категорий: {categories_deleted}")
        print("Очистка завершена успешно!")
        
        # Проверяем, что база действительно очищена
        final_categories = db.query(Category).count()
        final_types = db.query(FilterType).count()
        final_options = db.query(FilterOption).count()
        
        if final_categories == 0 and final_types == 0 and final_options == 0:
            print("✓ Проверка: База данных полностью очищена")
        else:
            print("⚠ Внимание: Остались неудаленные записи!")
            print(f"  Категорий: {final_categories}")
            print(f"  Типов фильтров: {final_types}")
            print(f"  Опций фильтров: {final_options}")
        
    except Exception as e:
        print(f"\n❌ Ошибка при очистке базы данных: {e}")
        print("Выполняется откат изменений...")
        db.rollback()
        print("Откат выполнен. Данные не были изменены.")
        raise
    finally:
        db.close()

def clear_only_filters():
    """Очистка только фильтров (оставляем категории)"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Очистка только фильтров (категории останутся)")
        print("-" * 50)
        
        filter_types_count = db.query(FilterType).count()
        filter_options_count = db.query(FilterOption).count()
        
        print(f"К удалению:")
        print(f"  - Типов фильтров: {filter_types_count}")
        print(f"  - Опций фильтров: {filter_options_count}")
        
        if filter_types_count == 0 and filter_options_count == 0:
            print("Фильтры уже отсутствуют!")
            return
        
        confirm = input("Продолжить? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Операция отменена.")
            return
        
        print("Удаляем опции фильтров...")
        options_deleted = db.query(FilterOption).delete()
        
        print("Удаляем типы фильтров...")
        types_deleted = db.query(FilterType).delete()
        
        db.commit()
        
        print(f"\nУдалено:")
        print(f"  - Опций фильтров: {options_deleted}")
        print(f"  - Типов фильтров: {types_deleted}")
        print("Очистка фильтров завершена!")
        
    except Exception as e:
        print(f"Ошибка при очистке фильтров: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Главная функция с выбором типа очистки"""
    print("СКРИПТ ОЧИСТКИ БАЗЫ ДАННЫХ")
    print("=" * 50)
    print("Выберите действие:")
    print("1. Очистить всё (категории + фильтры)")
    print("2. Очистить только фильтры")
    print("3. Отмена")
    
    choice = input("\nВведите номер действия (1-3): ").strip()
    
    if choice == "1":
        clear_database()
    elif choice == "2":
        clear_only_filters()
    elif choice == "3":
        print("Операция отменена.")
    else:
        print("Неверный выбор. Операция отменена.")

if __name__ == "__main__":
    main()