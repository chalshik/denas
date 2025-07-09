import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.product_service import ProductService
from app.schemas.product import ProductCreateComplete, CharacteristicInput, ProductImageInput, VariationInput, VariationImageInput
from scripts.date import CONSTRUCTION_PRODUCTS

def create_product_from_template(product_template: dict) -> ProductCreateComplete:
    """Создать ProductCreateComplete из шаблона продукта"""
    
    # Создаем основные характеристики
    characteristics = []
    for char in product_template.get("characteristics", []):
        characteristics.append(CharacteristicInput(
            type_name=char["type_name"],
            value=char["value"]
        ))
    
    # Создаем основные изображения
    images = []
    for img in product_template.get("images", []):
        images.append(ProductImageInput(
            url=img["url"],
            alt_text=img["alt_text"],
            order=img["order"]
        ))
    
    # Создаем вариации
    variations = []
    for var in product_template.get("variations", []):
        # Характеристики вариации
        var_characteristics = []
        for char in var.get("characteristics", []):
            var_characteristics.append(CharacteristicInput(
                type_name=char["type_name"],
                value=char["value"]
            ))
        
        # Изображения вариации
        var_images = []
        for img in var.get("images", []):
            var_images.append(VariationImageInput(
                url=img["url"],
                alt_text=img["alt_text"],
                order=img["order"]
            ))
        
        # Создаем вариацию
        variations.append(VariationInput(
            name=var["name"],
            price=var["price"],
            quantity=var["quantity"],
            characteristics=var_characteristics,
            images=var_images
        ))
    
    # Создаем полный продукт
    return ProductCreateComplete(
        name=product_template["name"],
        description=product_template["description"],
        category_id=product_template["category_id"],
        price=product_template["price"],
        quantity=product_template["quantity"],
        main_image_url=product_template["main_image_url"],
        filter_option_ids=product_template.get("filter_option_ids", []),
        images=images,
        characteristics=characteristics,
        variations=variations,
        status='approved'  # Явно устанавливаем статус approved
    )

def populate_100_products():
    """Добавить 100 случайных товаров из списка"""
    db = SessionLocal()
    product_service = ProductService(db)
    
    try:
        print("Начинаем добавление 100 случайных товаров...")
        
        # ID поставщика (предполагаем, что существует)
        vendor_profile_id = "20"
        
        created_count = 0
        failed_count = 0
        
        for i in range(100):
            try:
                # Выбираем случайный продукт из списка
                random_product = random.choice(CONSTRUCTION_PRODUCTS)
                
                # Добавляем небольшую вариацию к названию для уникальности
                variations = [
                    f"{random_product['name']} #{i+1}",
                    f"{random_product['name']} (Копия {i+1})",
                    f"{random_product['name']} - Вариант {i+1}",
                    f"{random_product['name']} Серия {i+1}"
                ]
                
                # Создаем копию продукта с измененным названием
                product_copy = random_product.copy()
                product_copy["name"] = random.choice(variations)
                
                # Добавляем небольшую вариацию к цене (±10%)
                price_variation = random.uniform(0.9, 1.1)
                product_copy["price"] = round(product_copy["price"] * price_variation, 2)
                
                # Добавляем вариацию к количеству (±50%)
                quantity_variation = random.uniform(0.5, 1.5)
                product_copy["quantity"] = max(1, int(product_copy["quantity"] * quantity_variation))
                
                # Создаем схему продукта
                product_schema = create_product_from_template(product_copy)
                
                # Создаем продукт через сервис
                product = product_service.create_complete(product_schema, vendor_profile_id)
                created_count += 1
                
                print(f"✅ [{created_count}/100] Создан продукт: {product_copy['name']}")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Ошибка при создании продукта #{i+1}: {str(e)}")
                continue
        
        print(f"\n🎉 Завершено!")
        print(f"✅ Успешно создано: {created_count} продуктов")
        print(f"❌ Не удалось создать: {failed_count} продуктов")
        
    except Exception as e:
        print(f"💥 Критическая ошибка: {str(e)}")
        db.rollback()
    finally:
        db.close()

def simple_populate_100():
    """Упрощенная версия без использования сервиса (прямое создание в БД)"""
    from app.models.product.product import Product, ProductVariation
    from app.models.product.characteristic import CharacteristicType, ProductCharacteristic, VariationCharacteristic
    from app.models.product.image import ProductImage, VariationImage
    from app.models.product.filter import product_filters
    from sqlalchemy import insert
    
    db = SessionLocal()
    
    try:
        print("Начинаем добавление 100 товаров (прямое создание в БД)...")
        vendor_profile_id = 20
        created_count = 0
        
        for i in range(100):
            try:
                # Выбираем случайный продукт
                random_product = random.choice(CONSTRUCTION_PRODUCTS)
                
                # Создаем уникальное название
                unique_name = f"{random_product['name']} #{i+1}"
                
                # Создаем основной продукт
                product = Product(
                    name=unique_name,
                    description=random_product["description"],
                    category_id=random_product["category_id"],
                    price=round(random_product["price"] * random.uniform(0.9, 1.1), 2),
                    quantity=max(1, int(random_product["quantity"] * random.uniform(0.5, 1.5))),
                    vendor_profile_id=vendor_profile_id,
                    main_image_url=random_product["main_image_url"],
                    status='approved'  # Явно устанавливаем статус approved
                )
                
                db.add(product)
                db.flush()  # Получаем ID продукта
                
                # Добавляем характеристики продукта
                for char in random_product.get("characteristics", []):
                    # Получить или создать тип характеристики
                    char_type = db.query(CharacteristicType).filter(
                        CharacteristicType.name == char["type_name"]
                    ).first()
                    if not char_type:
                        char_type = CharacteristicType(name=char["type_name"])
                        db.add(char_type)
                        db.flush()
                    
                    # Создать характеристику продукта
                    product_char = ProductCharacteristic(
                        product_id=product.id,
                        characteristic_type_id=char_type.id,
                        value=char["value"]
                    )
                    db.add(product_char)
                
                # Добавляем изображения продукта
                for img in random_product.get("images", []):
                    product_image = ProductImage(
                        product_id=product.id,
                        url=img["url"],
                        alt_text=img["alt_text"],
                        order=img["order"]
                    )
                    db.add(product_image)
                
                # Добавляем вариации
                for var in random_product.get("variations", []):
                    variation = ProductVariation(
                        product_id=product.id,
                        name=var["name"],
                        price=round(var["price"] * random.uniform(0.9, 1.1), 2),
                        quantity=max(1, int(var["quantity"] * random.uniform(0.5, 1.5))),
                        status='approved'  # Явно устанавливаем статус approved
                    )
                    db.add(variation)
                    db.flush()  # Получаем ID вариации
                    
                    # Добавляем характеристики вариации
                    for char in var.get("characteristics", []):
                        char_type = db.query(CharacteristicType).filter(
                            CharacteristicType.name == char["type_name"]
                        ).first()
                        if not char_type:
                            char_type = CharacteristicType(name=char["type_name"])
                            db.add(char_type)
                            db.flush()
                        
                        var_char = VariationCharacteristic(
                            variation_id=variation.id,
                            characteristic_type_id=char_type.id,
                            value=char["value"]
                        )
                        db.add(var_char)
                    
                    # Добавляем изображения вариации
                    for img in var.get("images", []):
                        var_image = VariationImage(
                            variation_id=variation.id,
                            url=img["url"],
                            alt_text=img["alt_text"],
                            order=img["order"]
                        )
                        db.add(var_image)
                
                # Добавляем связи с фильтрами
                for filter_option_id in random_product.get("filter_option_ids", []):
                    db.execute(insert(product_filters).values(
                        product_id=product.id,
                        filter_option_id=filter_option_id
                    ))
                
                created_count += 1
                print(f"✅ [{created_count}/100] Создан продукт: {unique_name}")
                
                # Коммитим каждые 10 продуктов
                if created_count % 10 == 0:
                    db.commit()
                    print(f"💾 Сохранено {created_count} продуктов")
                
            except Exception as e:
                print(f"❌ Ошибка создания продукта #{i+1}: {e}")
                db.rollback()
                continue
        
        db.commit()
        print(f"\n🎉 Успешно создано {created_count} продуктов!")
        
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Выберите метод создания продуктов:")
    print("1. Через ProductService (рекомендуется)")
    print("2. Прямое создание в БД")
    
    choice = input("Введите номер (1 или 2): ").strip()
    
    if choice == "1":
        populate_100_products()
    elif choice == "2":
        simple_populate_100()
    else:
        print("Неверный выбор. Используем метод через ProductService...")
        populate_100_products()