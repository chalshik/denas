# Denas Backend API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

The API uses Firebase JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <firebase_jwt_token>
```

### User Roles
- **Customer**: Default user role, can manage their own data
- **Admin**: Full access to all endpoints and user management
- **Manager**: Similar to Admin (specific permissions may vary)

---

## 🔐 Authentication Endpoints

### POST `/auth/register`
Register a new user with Firebase UID.

**Authentication**: Required (Firebase token)

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "uid": "firebase_uid_here",
  "email": "user@example.com",
  "role": "Customer",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### GET `/auth/me`
Get current user's profile.

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "id": 1,
  "uid": "firebase_uid_here",
  "email": "user@example.com",
  "role": "Customer",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### GET `/auth/me/or-create`
Get current user or prompt for registration if user doesn't exist.

**Authentication**: Required (Firebase token)

**Response**: `200 OK` (if user exists) or `404 Not Found` (if user needs to register)

### GET `/auth/admin/users` (Admin Only)
Get all users with pagination and filtering.

**Authentication**: Required (Admin)

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 100)
- `role_filter`: Filter by user role

**Response**: `200 OK`
```json
{
  "users": [
    {
      "id": 1,
      "uid": "firebase_uid_here",
      "email": "user@example.com",
      "role": "Customer",
      "is_active": true,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total_count": 100,
  "page": 1,
  "limit": 50,
  "has_next": true,
  "has_previous": false
}
```

### GET `/auth/admin/stats` (Admin Only)
Get user statistics.

**Authentication**: Required (Admin)

**Response**: `200 OK`
```json
{
  "total_users": 100,
  "active_users": 95,
  "admin_users": 2,
  "customer_users": 98
}
```

### PUT `/auth/admin/users/{user_id}/role` (Admin Only)
Update user role.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "new_role": "Admin"
}
```

**Response**: `200 OK` (User object)

### DELETE `/auth/admin/users/{user_id}` (Admin Only)
Delete a user.

**Authentication**: Required (Admin)

**Response**: `204 No Content`

---

## 👤 User Management Endpoints

### GET `/users/me`
Get current user's basic profile.

**Authentication**: Required

**Response**: `200 OK` (User object)

### GET `/users/me/details`
Get current user's detailed profile.

**Authentication**: Required

**Response**: `200 OK` (UserWithDetails object)

### PUT `/users/me`
Update current user's profile (limited fields).

**Authentication**: Required

**Request Body**:
```json
{
  "email": "newemail@example.com"
}
```

**Response**: `200 OK` (Updated User object)

### GET `/users/` (Admin Only)
Get all users with pagination.

**Authentication**: Required (Admin)

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)

**Response**: `200 OK` (List of User objects)

### GET `/users/{user_id}` (Admin Only)
Get specific user by ID.

**Authentication**: Required (Admin)

**Response**: `200 OK` (UserWithDetails object)

### PUT `/users/{user_id}` (Admin Only)
Update any user's profile.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "email": "updated@example.com",
  "role": "Admin",
  "is_active": false
}
```

**Response**: `200 OK` (Updated User object)

### DELETE `/users/{user_id}` (Admin Only)
Delete a user.

**Authentication**: Required (Admin)

**Response**: `204 No Content`

### GET `/users/search` (Admin Only)
Search users by query.

**Authentication**: Required (Admin)

**Query Parameters**:
- `q`: Search query (required)
- `limit`: Max results (default: 20)

**Response**: `200 OK` (List of User objects)

---

## 📦 Product Endpoints

### GET `/products/`
Get all products with filtering and pagination (public).

**Authentication**: Optional

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50, max: 100)
- `category_id`: Filter by category ID
- `availability_type`: Filter by availability ("in_stock", "pre_order", "discontinued")
- `is_active`: Filter by active status
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": 29.99,
    "stock_quantity": 100,
    "availability_type": "in_stock",
    "preorder_available_date": null,
    "is_active": true,
    "category_id": 1,
    "created_at": "2024-01-01T12:00:00Z",
    "category": {
      "id": 1,
      "name": "Category Name",
      "description": "Category description"
    }
  }
]
```

### GET `/products/{product_id}`
Get specific product with full details (public).

**Authentication**: Optional

**Response**: `200 OK`
```json
{
  "id": 1,
  "name": "Product Name",
  "description": "Product description",
  "price": 29.99,
  "stock_quantity": 100,
  "availability_type": "in_stock",
  "preorder_available_date": null,
  "is_active": true,
  "category_id": 1,
  "created_at": "2024-01-01T12:00:00Z",
  "category": {
    "id": 1,
    "name": "Category Name"
  },
  "images": [
    {
      "id": 1,
      "product_id": 1,
      "image_url": "https://example.com/image.jpg",
      "image_type": "official"
    }
  ],
  "favorites_count": 5
}
```

### GET `/products/search/{search_term}`
Search products by name or description (public).

**Authentication**: Optional

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)

**Response**: `200 OK` (List of ProductWithCategory objects)

### GET `/products/category/{category_id}/products`
Get products by category (public).

**Authentication**: Optional

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)

**Response**: `200 OK` (List of Product objects)

### POST `/products/` (Admin Only)
Create a new product.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "name": "New Product",
  "description": "Product description",
  "price": 29.99,
  "stock_quantity": 100,
  "availability_type": "in_stock",
  "preorder_available_date": null,
  "is_active": true,
  "category_id": 1
}
```

**Response**: `201 Created` (Product object)

### PUT `/products/{product_id}` (Admin Only)
Update a product.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "name": "Updated Product Name",
  "price": 39.99,
  "stock_quantity": 150
}
```

**Response**: `200 OK` (Updated Product object)

### DELETE `/products/{product_id}` (Admin Only)
Delete a product.

**Authentication**: Required (Admin)

**Response**: `204 No Content`

---

## 🏷️ Category Endpoints

### GET `/categories/`
Get all categories (public).

**Authentication**: Optional

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and accessories",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### GET `/categories/{category_id}`
Get specific category (public).

**Authentication**: Optional

**Response**: `200 OK` (Category object)

### POST `/categories/` (Admin Only)
Create a new category.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "name": "New Category",
  "description": "Category description",
  "is_active": true
}
```

**Response**: `201 Created` (Category object)

### PUT `/categories/{category_id}` (Admin Only)
Update a category.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "name": "Updated Category",
  "description": "Updated description"
}
```

**Response**: `200 OK` (Updated Category object)

### DELETE `/categories/{category_id}` (Admin Only)
Delete a category.

**Authentication**: Required (Admin)

**Response**: `204 No Content`

---

## 🛒 Shopping Cart Endpoints

### GET `/cart/`
Get current user's shopping cart.

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "created_at": "2024-01-01T12:00:00Z",
  "cart_items": [
    {
      "id": 1,
      "cart_id": 1,
      "product_id": 1,
      "quantity": 2,
      "created_at": "2024-01-01T12:00:00Z",
      "product": {
        "id": 1,
        "name": "Product Name",
        "price": 29.99
      }
    }
  ]
}
```

### POST `/cart/items`
Add item to shopping cart.

**Authentication**: Required

**Request Body**:
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response**: `201 Created`
```json
{
  "success": true,
  "message": "Item added to cart",
  "item_id": 1,
  "quantity": 2
}
```

### PUT `/cart/items/{item_id}`
Update cart item quantity.

**Authentication**: Required

**Request Body**:
```json
{
  "quantity": 3
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Cart item updated",
  "item_id": 1,
  "old_quantity": 2,
  "new_quantity": 3
}
```

### DELETE `/cart/items/{item_id}`
Remove item from cart.

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Item removed from cart"
}
```

### DELETE `/cart/clear`
Clear entire cart.

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Cart cleared",
  "items_removed": 3
}
```

### GET `/cart/summary`
Get cart summary with totals.

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "cart_id": 1,
  "total_items": 3,
  "total_quantity": 8,
  "total_price": 119.96,
  "items": [
    {
      "product_name": "Product Name",
      "quantity": 2,
      "unit_price": 29.99,
      "total_price": 59.98
    }
  ]
}
```

---

## 📋 Order Endpoints

### GET `/orders/my-orders`
Get current user's orders.

**Authentication**: Required

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 20)
- `status_filter`: Filter by order status

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "status": "pending",
    "total_price": 59.98,
    "created_at": "2024-01-01T12:00:00Z",
    "order_items": [
      {
        "id": 1,
        "order_id": 1,
        "product_id": 1,
        "quantity": 2,
        "price": 29.99,
        "product": {
          "id": 1,
          "name": "Product Name"
        }
      }
    ]
  }
]
```

### GET `/orders/{order_id}`
Get specific order (own orders only, admins can see all).

**Authentication**: Required

**Response**: `200 OK` (OrderWithItems object)

### POST `/orders/`
Create a new order.

**Authentication**: Required

**Request Body**:
```json
{
  "order_items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "status": "pending",
  "total_price": 89.97,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### PUT `/orders/{order_id}/status`
Update order status.

**Authentication**: Required

**Request Body**:
```json
{
  "new_status": "cancelled"
}
```

**Note**: 
- Users can only cancel their own pending orders
- Admins can update any order to any status

**Response**: `200 OK` (Updated Order object)

### GET `/orders/` (Admin Only)
Get all orders with filtering.

**Authentication**: Required (Admin)

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)
- `status_filter`: Filter by order status
- `user_id`: Filter by user ID

**Response**: `200 OK` (List of OrderWithItems objects)

### GET `/orders/stats/summary` (Admin Only)
Get order statistics.

**Authentication**: Required (Admin)

**Response**: `200 OK`
```json
{
  "total_orders": 150,
  "pending_orders": 25,
  "completed_orders": 100,
  "cancelled_orders": 25,
  "total_revenue": 15000.00,
  "average_order_value": 100.00
}
```

### DELETE `/orders/{order_id}` (Admin Only)
Delete an order (only cancelled orders).

**Authentication**: Required (Admin)

**Response**: `204 No Content`

---

## 💳 Payment Endpoints

### GET `/payments/my-payments`
Get current user's payments.

**Authentication**: Required

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 20)
- `status_filter`: Filter by payment status

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "order_id": 1,
    "amount": 59.98,
    "status": "pending",
    "payment_method": "credit_card",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### GET `/payments/{payment_id}`
Get specific payment (own payments only, admins can see all).

**Authentication**: Required

**Response**: `200 OK` (PaymentWithOrder object)

### POST `/payments/`
Create a new payment.

**Authentication**: Required

**Request Body**:
```json
{
  "order_id": 1,
  "amount": 59.98,
  "payment_method": "credit_card"
}
```

**Response**: `201 Created` (Payment object)

### PUT `/payments/{payment_id}/status`
Update payment status.

**Authentication**: Required

**Request Body**:
```json
{
  "new_status": "completed"
}
```

**Note**: 
- Users have limited status update permissions
- Admins can update to any status

**Response**: `200 OK` (Updated Payment object)

### GET `/payments/` (Admin Only)
Get all payments.

**Authentication**: Required (Admin)

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)
- `status_filter`: Filter by payment status
- `order_id`: Filter by order ID

**Response**: `200 OK` (List of PaymentWithOrder objects)

### GET `/payments/stats/summary` (Admin Only)
Get payment statistics.

**Authentication**: Required (Admin)

**Response**: `200 OK`
```json
{
  "total_payments": 120,
  "completed_payments": 100,
  "pending_payments": 15,
  "failed_payments": 5,
  "total_amount": 12000.00
}
```

### DELETE `/payments/{payment_id}` (Admin Only)
Delete a payment (only failed payments).

**Authentication**: Required (Admin)

**Response**: `204 No Content`

---

## 🖼️ Product Images Endpoints

### GET `/product-images/`
Get all product images with filtering (public).

**Authentication**: Optional

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)
- `product_id`: Filter by product ID
- `image_type`: Filter by image type ("official", "received", "other")

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "product_id": 1,
    "image_url": "https://example.com/image.jpg",
    "image_type": "official",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### GET `/product-images/{image_id}`
Get specific product image (public).

**Authentication**: Optional

**Response**: `200 OK` (ProductImageWithProduct object)

### GET `/product-images/product/{product_id}`
Get all images for a specific product (public).

**Authentication**: Optional

**Response**: `200 OK` (List of ProductImage objects)

### POST `/product-images/` (Admin Only)
Create a new product image.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "product_id": 1,
  "image_url": "https://example.com/new-image.jpg",
  "image_type": "official"
}
```

**Response**: `201 Created` (ProductImage object)

### POST `/product-images/bulk` (Admin Only)
Create multiple product images at once.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "images": [
    {
      "product_id": 1,
      "image_url": "https://example.com/image1.jpg",
      "image_type": "official"
    },
    {
      "product_id": 1,
      "image_url": "https://example.com/image2.jpg",
      "image_type": "received"
    }
  ]
}
```

**Response**: `201 Created`
```json
{
  "success": true,
  "message": "2 images created successfully",
  "created_count": 2,
  "image_ids": [1, 2]
}
```

### PUT `/product-images/{image_id}` (Admin Only)
Update a product image.

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "image_url": "https://example.com/updated-image.jpg",
  "image_type": "received"
}
```

**Response**: `200 OK` (Updated ProductImage object)

### DELETE `/product-images/{image_id}` (Admin Only)
Delete a product image.

**Authentication**: Required (Admin)

**Response**: `204 No Content`

### DELETE `/product-images/product/{product_id}/all` (Admin Only)
Delete all images for a product.

**Authentication**: Required (Admin)

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "All images deleted for product",
  "deleted_count": 3
}
```

---

## ⭐ Favorites Endpoints

### GET `/favorites/my-favorites`
Get current user's favorite products.

**Authentication**: Required

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "product_id": 1,
    "created_at": "2024-01-01T12:00:00Z",
    "product": {
      "id": 1,
      "name": "Product Name",
      "price": 29.99
    }
  }
]
```

### POST `/favorites/`
Add product to favorites.

**Authentication**: Required

**Request Body**:
```json
{
  "product_id": 1
}
```

**Response**: `201 Created` (Favorite object)

### DELETE `/favorites/{favorite_id}`
Remove product from favorites.

**Authentication**: Required

**Response**: `204 No Content`

### GET `/favorites/product/{product_id}/check`
Check if product is in user's favorites.

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "is_favorite": true,
  "favorite_id": 1
}
```

### GET `/favorites/` (Admin Only)
Get all favorites with filtering.

**Authentication**: Required (Admin)

**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Items per page (default: 50)
- `user_id`: Filter by user ID
- `product_id`: Filter by product ID

**Response**: `200 OK` (List of FavoriteWithProduct objects)

---

## 🚫 Error Responses

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Resource deleted successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "field is required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🔍 Pagination

Most list endpoints support pagination with these query parameters:

- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (varies by endpoint)

Paginated responses include:
- `total_count`: Total number of items
- `page`: Current page number
- `limit`: Items per page
- `has_next`: Whether there are more pages
- `has_previous`: Whether there are previous pages

---

## 🎯 Quick Start

1. **Authentication**: Register or authenticate via Firebase
2. **Browse Products**: Use `/products/` to view available products
3. **Manage Cart**: Add items to cart via `/cart/items`
4. **Place Order**: Create orders via `/orders/`
5. **Process Payment**: Handle payments via `/payments/`

For admin operations, ensure your user has Admin role and use admin-specific endpoints.

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Prices are stored as decimal values
- Image URLs should be absolute URLs
- Stock quantities are automatically managed during order creation
- Users can only access their own data (orders, cart, favorites) unless they have admin privileges
- Admin users have full access to all endpoints and data 