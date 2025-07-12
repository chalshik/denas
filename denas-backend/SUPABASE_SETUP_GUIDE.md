# Supabase Integration Setup Guide

## Overview
This guide will help you set up and test Supabase integration for both database and storage functionality.

## ✅ Current Configuration Status

### What's Already Configured:
- ✅ Multi-environment configuration system
- ✅ Supabase PostgreSQL database connection
- ✅ Firebase authentication
- ✅ Supabase storage service
- ✅ File upload endpoints
- ✅ Docker setup with environment switching

## 🚀 Quick Start

### 1. Start with Supabase Configuration
```bash
cd denas-backend
./scripts/start-supabase.sh
```

### 2. Alternative: Manual Start
```bash
# Set environment
export DB_ENV=supabase

# Start services
docker-compose up --build -d
```

## 🔧 Environment Configuration

### Current Environment Files:
- `env/.env.local` - Local PostgreSQL (Docker)
- `env/.env.supabase` - Supabase database + storage
- `env/.env.production` - Production Supabase

### Supabase Configuration (env/.env.supabase):
```env
# Database
POSTGRES_USER=postgres.celfpkvwoqfzponqsdcc
POSTGRES_PASSWORD=denas_ali_beki
POSTGRES_DB=postgres
POSTGRES_HOST=aws-0-eu-north-1.pooler.supabase.com
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres.celfpkvwoqfzponqsdcc:denas_ali_beki@aws-0-eu-north-1.pooler.supabase.com:5432/postgres

# Storage
SUPABASE_URL=https://celfpkvwoqfzponqsdcc.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_STORAGE_BUCKET=product-images

ENVIRONMENT=development
```

## 🧪 Testing File Uploads

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Test Authentication (Register User)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'
```

### 3. Test Single File Upload
```bash
curl -X POST "http://localhost:8000/api/v1/uploads/single" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -F "file=@/path/to/your/image.jpg" \
  -F "folder=test-uploads"
```

### 4. Test Product Image Upload (Admin Only)
```bash
curl -X POST "http://localhost:8000/api/v1/uploads/product-images" \
  -H "Authorization: Bearer YOUR_ADMIN_FIREBASE_TOKEN" \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/image2.jpg"
```

### 5. Test Multiple File Upload
```bash
curl -X POST "http://localhost:8000/api/v1/uploads/multiple" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/image2.jpg" \
  -F "folder=gallery"
```

## 📱 Frontend Integration

### Upload Component Example:
```javascript
// Upload single file
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('folder', 'uploads');
  
  const response = await fetch('/api/v1/uploads/single', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${firebaseToken}`
    },
    body: formData
  });
  
  return response.json();
};

// Upload product images
const uploadProductImages = async (files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  
  const response = await fetch('/api/v1/uploads/product-images', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminFirebaseToken}`
    },
    body: formData
  });
  
  return response.json();
};
```

## 🔍 Troubleshooting

### Common Issues:

#### 1. "Supabase storage is not configured"
**Solution:** Check environment variables in your `.env.supabase` file:
```bash
# Check if variables are loaded
curl http://localhost:8000/health
```

#### 2. Database connection issues
**Solution:** Verify Supabase database credentials:
```bash
# Test database connection
docker-compose exec app python -c "from app.core.config import settings; print(settings.database_url)"
```

#### 3. Storage bucket not found
**Solution:** 
1. Check if bucket exists in Supabase dashboard
2. Verify bucket name in environment file
3. Check bucket permissions (public access for product images)

#### 4. File upload fails
**Solution:**
1. Check file size (max 5MB for regular uploads, 10MB for product images)
2. Verify file type (JPEG, PNG, WebP, GIF)
3. Check authentication token

### Debug Commands:
```bash
# Check container logs
docker-compose logs app

# Check environment variables
docker-compose exec app env | grep SUPABASE

# Test storage service
docker-compose exec app python -c "
from app.services.supabase_storage import get_supabase_storage
try:
    storage = get_supabase_storage()
    print('✅ Storage service initialized successfully')
except Exception as e:
    print(f'❌ Storage service error: {e}')
"
```

## 🎯 Testing Workflow

### Complete Testing Sequence:

1. **Start Services**
   ```bash
   ./scripts/start-supabase.sh
   ```

2. **Check Health**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Register User** (Get Firebase token first)
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"phone": "+1234567890"}'
   ```

4. **Upload Test Image**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/uploads/single" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@test-image.jpg"
   ```

5. **Create Product with Images** (Admin only)
   ```bash
   # First upload images
   curl -X POST "http://localhost:8000/api/v1/uploads/product-images" \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -F "files=@product1.jpg"
   
   # Then create product using returned URLs
   curl -X POST "http://localhost:8000/api/v1/products/" \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Product",
       "description": "Test Description",
       "price": 29.99,
       "category_id": 1,
       "images": [
         {"image_url": "UPLOADED_IMAGE_URL", "image_type": "official"}
       ]
     }'
   ```

## 📊 API Endpoints

### Upload Endpoints:
- `POST /api/v1/uploads/single` - Upload single file
- `POST /api/v1/uploads/multiple` - Upload multiple files
- `POST /api/v1/uploads/product-images` - Upload product images (admin)

### Product Endpoints:
- `GET /api/v1/products/` - List products with images
- `POST /api/v1/products/` - Create product with images (admin)
- `GET /api/v1/product-images/` - List product images

## 🎉 Success Indicators

### You'll know it's working when:
1. ✅ Health check returns Supabase database host
2. ✅ File uploads return Supabase storage URLs
3. ✅ Images are visible in Supabase dashboard
4. ✅ Product creation includes image URLs
5. ✅ Frontend can display uploaded images

## 🚦 Next Steps

1. **Test with your frontend** - Use the upload endpoints
2. **Set up proper CORS** - Configure for your frontend domain
3. **Add image optimization** - Consider resizing/compression
4. **Set up CDN** - For better performance
5. **Add image validation** - More strict file type checking 