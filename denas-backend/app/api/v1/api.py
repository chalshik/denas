from fastapi import APIRouter
from app.api.v1.endpoints import (
    users, favorites, categories, auth, products, orders, 
    shopping_cart, payments, product_images
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(product_images.router, prefix="/product-images", tags=["product-images"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(shopping_cart.router, prefix="/cart", tags=["shopping-cart"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"]) 