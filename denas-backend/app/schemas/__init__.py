from .user import User, UserCreate, UserUpdate, UserInDB, UserWithDetails, UserRole
from .product import (
    Product, ProductCreate, ProductUpdate, ProductInDB, 
    ProductWithDetails, ProductCatalog, ProductListResponse, ProductResponse, AvailabilityType
)
from .category import Category, CategoryCreate, CategoryUpdate, CategoryInDB, CategoryWithProducts
from .product_image import ProductImage, ProductImageCreate, ProductImageUpdate, ProductImageInDB, ImageType
from .order import Order, OrderCreate, OrderUpdate, OrderInDB, OrderWithItems, OrderWithUser, OrderStatus
from .order_item import OrderItem, OrderItemCreate, OrderItemUpdate, OrderItemInDB, OrderItemWithProduct, OrderItemWithOrder
from .shopping_cart import (
    ShoppingCart, ShoppingCartCreate, ShoppingCartUpdate, ShoppingCartInDB, 
    ShoppingCartResponse, ShoppingCartSummary, ShoppingCartItemResponse,
    CartActionResponse, CartClearResponse
)
from .shopping_cart_item import (
    ShoppingCartItem, ShoppingCartItemCreate, ShoppingCartItemUpdate, 
    ShoppingCartItemInDB, ShoppingCartItemWithProduct
)
from .payment import Payment, PaymentCreate, PaymentUpdate, PaymentInDB, PaymentWithOrder, PaymentStatus
from .favorite import Favorite, FavoriteCreate, FavoriteUpdate, FavoriteInDB, FavoriteWithProduct, FavoriteWithUser

# Rebuild models to resolve forward references
ProductWithDetails.model_rebuild()
CategoryWithProducts.model_rebuild()

__all__ = [
    # User schemas
    "User", "UserCreate", "UserUpdate", "UserInDB", "UserWithDetails", "UserRole",
    # Product schemas
    "Product", "ProductCreate", "ProductUpdate", "ProductInDB", 
    "ProductWithDetails", "ProductCatalog", "ProductListResponse", "ProductResponse", "AvailabilityType",
    # Category schemas
    "Category", "CategoryCreate", "CategoryUpdate", "CategoryInDB", "CategoryWithProducts",
    # Product image schemas
    "ProductImage", "ProductImageCreate", "ProductImageUpdate", "ProductImageInDB", "ImageType",
    # Order schemas
    "Order", "OrderCreate", "OrderUpdate", "OrderInDB", "OrderWithItems", "OrderWithUser", "OrderStatus",
    # Order item schemas
    "OrderItem", "OrderItemCreate", "OrderItemUpdate", "OrderItemInDB", "OrderItemWithProduct", "OrderItemWithOrder",
    # Shopping cart schemas
    "ShoppingCart", "ShoppingCartCreate", "ShoppingCartUpdate", "ShoppingCartInDB", 
    "ShoppingCartResponse", "ShoppingCartSummary", "ShoppingCartItemResponse",
    "CartActionResponse", "CartClearResponse",
    # Shopping cart item schemas
    "ShoppingCartItem", "ShoppingCartItemCreate", "ShoppingCartItemUpdate", 
    "ShoppingCartItemInDB", "ShoppingCartItemWithProduct",
    # Payment schemas
    "Payment", "PaymentCreate", "PaymentUpdate", "PaymentInDB", "PaymentWithOrder", "PaymentStatus",
    # Favorite schemas
    "Favorite", "FavoriteCreate", "FavoriteUpdate", "FavoriteInDB", "FavoriteWithProduct", "FavoriteWithUser",
] 