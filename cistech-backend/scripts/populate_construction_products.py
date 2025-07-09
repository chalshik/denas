import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.product.product import Product
from app.models.product.characteristic import CharacteristicType, ProductCharacteristic
from app.services.product_service import ProductService
from app.schemas.product import ProductCreateComplete, CharacteristicInput, ProductImageInput

# Продукты с использованием существующих ID категорий и фильтров
CONSTRUCTION_PRODUCTS = [
    {
        "name": "Экскаватор гусеничный XCMG XE215C",
        "description": "Гусеничный экскаватор массой 21 тонна с ковшом 1.0 м³. Двигатель Isuzu мощностью 129 кВт. Отличная производительность для строительных работ.",
        "category_id": 67,  # Спецтехника
        "price_range": (2500000, 3500000),
        "main_image_url": "https://api.xcmg-rf.ru/uploads/images/photo-2025-03-26-17-35-26_1.jpg",
        "characteristics": [
            {"type_name": "Масса", "value_options": ["21000 кг", "21500 кг", "22000 кг"]},
            {"type_name": "Мощность двигателя", "value_options": ["129 кВт", "132 кВт", "135 кВт"]},
            {"type_name": "Объем ковша", "value_options": ["1.0 м³", "1.1 м³", "1.2 м³"]},
            {"type_name": "Глубина копания", "value_options": ["6.5 м", "6.7 м", "6.9 м"]}
        ],
        "filter_option_ids": [469, 482, 490, 493, 496]  # Экскаватор, XCMG, Новый, Дизельный, Сейчас
    },
    {
        "name": "Цемент М400 ПЦ",
        "description": "Портландцемент марки М400 для строительных работ. Соответствует ГОСТ 31108-2003. Упаковка 50 кг.",
        "category_id": 71,  # Стройматериалы
        "price_range": (350, 450),
        "main_image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR5APHRsRM3_ooo7hVqN39JyMYQVrbCiq2dMA&s",
        "characteristics": [
            {"type_name": "Марка", "value_options": ["М400", "М450", "М500"]},
            {"type_name": "Упаковка", "value_options": ["50 кг", "25 кг", "1000 кг"]},
            {"type_name": "Время схватывания", "value_options": ["45 мин", "50 мин", "60 мин"]},
            {"type_name": "Прочность", "value_options": ["40 МПа", "42 МПа", "45 МПа"]}
        ],
        "filter_option_ids": [568, 574, 576, 578]  # Бетон и растворы, Прочее, ГОСТ, Сейчас
    },
    {
        "name": "Дрель ударная Bosch GSB 13 RE",
        "description": "Ударная дрель мощностью 600 Вт с реверсом. Максимальный диаметр сверления в металле 13 мм, в дереве 30 мм.",
        "category_id": 72,  # Инструменты
        "price_range": (4500, 6500),
        "main_image_url": "https://www.kivano.kg/images/product/55543/55543_full.jpg",
        "characteristics": [
            {"type_name": "Мощность", "value_options": ["600 Вт", "650 Вт", "700 Вт"]},
            {"type_name": "Макс. диаметр сверления в металле", "value_options": ["13 мм", "15 мм", "16 мм"]},
            {"type_name": "Макс. диаметр сверления в дереве", "value_options": ["30 мм", "32 мм", "35 мм"]},
            {"type_name": "Частота ударов", "value_options": ["44000 уд/мин", "45000 уд/мин", "46000 уд/мин"]}
        ],
        "filter_option_ids": [582, 590, 593]  # Электроинструмент, ЕАЭС, Сейчас
    },
    {
        "name": "Балка двутавровая 20Б1",
        "description": "Стальная двутавровая балка по ГОСТ 26020-83. Высота 200 мм, ширина полки 100 мм. Длина 6-12 метров.",
        "category_id": 70,  # Металлоконструкции
        "price_range": (45000, 65000),
        "main_image_url": "https://metallobazav.ru/upload/resize_cache/webp/iblock/ede/7htn7urgmdl92xjf9mz15n2iyea0wuiu.webp",
        "characteristics": [
            {"type_name": "Высота", "value_options": ["200 мм", "220 мм", "240 мм"]},
            {"type_name": "Ширина полки", "value_options": ["100 мм", "110 мм", "120 мм"]},
            {"type_name": "Длина", "value_options": ["6 м", "9 м", "12 м"]},
            {"type_name": "Масса погонного метра", "value_options": ["21 кг/м", "23 кг/m", "25 кг/m"]}
        ],
        "filter_option_ids": [553, 555, 560, 562, 565]  # Балки, Сталь, Прочее, ГОСТ, 1-3 дня
    },
    {
        "name": "Светодиодный прожектор 50Вт IP65",
        "description": "Светодиодный прожектор для наружного освещения строительных площадок. Мощность 50Вт, световой поток 4500 лм.",
        "category_id": 73,  # Электрика и свет
        "price_range": (1200, 2200),
        "main_image_url": "https://topdiod.ru/upload/iblock/75c/75c36af9d91b503128c01c3751c5c576.jpg",
        "characteristics": [
            {"type_name": "Мощность", "value_options": ["50 Вт", "60 Вт", "70 Вт"]},
            {"type_name": "Световой поток", "value_options": ["4500 лм", "5000 лм", "5500 лм"]},
            {"type_name": "Цветовая температура", "value_options": ["4000K", "5000K", "6000K"]},
            {"type_name": "Степень защиты", "value_options": ["IP65", "IP66", "IP67"]}
        ],
        "filter_option_ids": [598, 626]  # Прожекторы, Сейчас
    }
]

def create_random_product_data(product_template: dict) -> dict:
    """Создать случайные данные для продукта на основе шаблона"""
    # Случайная цена в диапазоне
    price = random.uniform(product_template["price_range"][0], product_template["price_range"][1])
    
    # Случайные характеристики
    characteristics = []
    for char_template in product_template["characteristics"]:
        char = CharacteristicInput(
            type_name=char_template["type_name"],
            value=random.choice(char_template["value_options"])
        )
        characteristics.append(char)
    
    # Случайные изображения (1-3 изображения)
    num_images = random.randint(1, 3)
    images = []
    for i in range(num_images):
        image = ProductImageInput(
            url=f"{product_template['main_image_url']}?v={random.randint(1, 1000)}",
            alt_text=f"{product_template['name']} - изображение {i+1}",
            order=i
        )
        images.append(image)
    
    # Случайное количество
    quantity = random.randint(1, 50)
    
    # Добавить небольшую вариацию к названию
    name_variations = [
        product_template["name"],
        f"{product_template['name']} (Стандарт)",
        f"{product_template['name']} Про",
        f"{product_template['name']} Плюс",
        f"{product_template['name']} Эконом"
    ]
    
    # Случайно выбрать несколько ID фильтров из доступных
    available_filter_ids = product_template["filter_option_ids"]
    num_filters = random.randint(2, len(available_filter_ids))
    selected_filter_ids = random.sample(available_filter_ids, num_filters)
    
    return {
        "name": random.choice(name_variations),
        "description": product_template["description"],
        "price": round(price, 2),
        "quantity": quantity,
        "category_id": product_template["category_id"],
        "main_image_url": product_template["main_image_url"],
        "characteristics": characteristics,
        "images": images,
        "filter_option_ids": selected_filter_ids
    }

def populate_construction_products():
    """Основная функция для заполнения базы данных"""
    db = SessionLocal()
    product_service = ProductService(db)
    
    try:
        print("Начинаем заполнение базы данных строительными продуктами...")
        
        # Предполагаем, что vendor_profile_id = 4 существует
        vendor_profile_id = "4"
        
        total_products = 0
        
        for i in range(100):  # 100 итераций
            print(f"Итерация {i+1}/100")
            
            for product_template in CONSTRUCTION_PRODUCTS:  # 5 продуктов в каждой итерации
                try:
                    # Создать случайные данные продукта
                    product_data = create_random_product_data(product_template)
                    
                    # Создать схему продукта
                    product_schema = ProductCreateComplete(
                        name=product_data["name"],
                        description=product_data["description"],
                        price=product_data["price"],
                        quantity=product_data["quantity"],
                        category_id=product_data["category_id"],
                        main_image_url=product_data["main_image_url"],
                        characteristics=product_data["characteristics"],
                        images=product_data["images"],
                        filter_option_ids=product_data["filter_option_ids"],
                        status='approved'  # Явно устанавливаем статус approved
                    )
                    
                    # Создать продукт через сервис
                    product = product_service.create_complete(product_schema, vendor_profile_id)
                    total_products += 1
                    
                    if total_products % 50 == 0:
                        print(f"Создано {total_products} продуктов...")
                        
                except Exception as e:
                    print(f"Ошибка при создании продукта '{product_template['name']}': {str(e)}")
                    continue
        
        print(f"Успешно создано {total_products} строительных продуктов!")
        
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        db.rollback()
    finally:
        db.close()

def simple_populate_direct():
    """Упрощенная версия без использования сервиса"""
    db = SessionLocal()
    
    try:
        print("Создание 500 строительных продуктов (прямое создание)...")
        vendor_profile_id = 4
        created_count = 0
        
        for iteration in range(100):
            print(f"Итерация {iteration + 1}/100")
            
            for product_template in CONSTRUCTION_PRODUCTS:
                try:
                    # Создать случайные данные продукта
                    product_data = create_random_product_data(product_template)
                    
                    # Прямое создание продукта
                    product = Product(
                        name=product_data["name"],
                        description=product_data["description"],
                        category_id=product_data["category_id"],
                        price=product_data["price"],
                        quantity=product_data["quantity"],
                        vendor_profile_id=vendor_profile_id,
                        main_image_url=product_data["main_image_url"],
                        status='approved'  # Явно устанавливаем статус approved
                    )
                    
                    db.add(product)
                    db.flush()
                    
                    # Добавить характеристики
                    for char in product_data["characteristics"]:
                        # Получить или создать тип характеристики
                        char_type = db.query(CharacteristicType).filter(
                            CharacteristicType.name == char.type_name
                        ).first()
                        if not char_type:
                            char_type = CharacteristicType(name=char.type_name)
                            db.add(char_type)
                            db.flush()
                        
                        # Создать характеристику
                        product_char = ProductCharacteristic(
                            product_id=product.id,
                            characteristic_type_id=char_type.id,
                            value=char.value
                        )
                        db.add(product_char)
                    
                    # Добавить связи с фильтрами
                    from app.models.product.filter import product_filters
                    from sqlalchemy import insert
                    
                    for filter_option_id in product_data["filter_option_ids"]:
                        db.execute(insert(product_filters).values(
                            product_id=product.id,
                            filter_option_id=filter_option_id
                        ))
                    
                    created_count += 1
                    
                    if created_count % 50 == 0:
                        db.commit()
                        print(f"Создано {created_count} продуктов")
                        
                except Exception as e:
                    print(f"Ошибка создания продукта: {e}")
                    db.rollback()
                    continue
        
        db.commit()
        print(f"Успешно создано {created_count} продуктов!")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Попробовать сначала через сервис, если не работает - прямое создание
    try:
        populate_construction_products()
    except Exception as e:
        print(f"Сервис не работает, пробуем прямое создание: {e}")
        simple_populate_direct()