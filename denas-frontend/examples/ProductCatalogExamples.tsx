// Example usage of the new hooks and types

import React, { useEffect, useState } from 'react';
import { useProductCatalog } from '../hooks/useProductCatalog';
import { useCategories } from '../hooks/useCategories';
import { useProducts } from '../hooks/useProducts';
import { AvailabilityType, ProductFilters, ProductCatalog } from '../types';

export function ProductCatalogExample() {
  const { 
    loading, 
    error, 
    products, 
    pagination,
    fetchCatalog,
    fetchFeaturedProducts,
    searchProducts,
    createFilters,
    clearError
  } = useProductCatalog();
  
  const { categories, fetchCategories } = useCategories();
  
  const [filters, setFilters] = useState<ProductFilters>({
    page: 1,
    size: 20,
    sort_by: 'created_at',
    sort_order: 'desc'
  });
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [priceRange, setPriceRange] = useState({ min: 0, max: 1000 });

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    const searchFilters = createFilters({
      page: filters.page,
      size: filters.size,
      categoryId: selectedCategory || undefined,
      priceRange: { min: priceRange.min, max: priceRange.max },
      search: searchQuery || undefined,
      sortBy: filters.sort_by as any,
      sortOrder: filters.sort_order as any,
      activeOnly: true
    });
    
    fetchCatalog(searchFilters);
  }, [filters, selectedCategory, priceRange, searchQuery]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setFilters(prev => ({ ...prev, page: 1 }));
  };

  const handleCategoryChange = (categoryId: number | null) => {
    setSelectedCategory(categoryId);
    setFilters(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  const handleSortChange = (sortBy: string, sortOrder: string) => {
    setFilters(prev => ({ ...prev, sort_by: sortBy, sort_order: sortOrder, page: 1 }));
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="product-catalog">
      <h1>Product Catalog</h1>
      
      {/* Search */}
      <div className="search-section">
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
        />
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="category-filter">
          <label>Category:</label>
          <select 
            value={selectedCategory || ''} 
            onChange={(e) => handleCategoryChange(e.target.value ? parseInt(e.target.value) : null)}
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>

        <div className="price-filter">
          <label>Price Range:</label>
          <input
            type="range"
            min="0"
            max="1000"
            value={priceRange.min}
            onChange={(e) => setPriceRange(prev => ({ ...prev, min: parseInt(e.target.value) }))}
          />
          <span>${priceRange.min}</span>
          <input
            type="range"
            min="0"
            max="1000"
            value={priceRange.max}
            onChange={(e) => setPriceRange(prev => ({ ...prev, max: parseInt(e.target.value) }))}
          />
          <span>${priceRange.max}</span>
        </div>

        <div className="sort-filter">
          <label>Sort by:</label>
          <select 
            value={filters.sort_by} 
            onChange={(e) => handleSortChange(e.target.value, filters.sort_order || 'desc')}
          >
            <option value="created_at">Date Created</option>
            <option value="name">Name</option>
            <option value="price">Price</option>
          </select>
          <select 
            value={filters.sort_order} 
            onChange={(e) => handleSortChange(filters.sort_by || 'created_at', e.target.value)}
          >
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>
      </div>

      {/* Products Grid */}
      <div className="products-grid">
        {products.map(product => (
          <div key={product.id} className="product-card">
            <img src={product.image_url || '/placeholder.jpg'} alt={product.name} />
            <h3>{product.name}</h3>
            <p>${product.price}</p>
            <p>Status: {product.availability_type.replace('_', ' ')}</p>
            <button>View Details</button>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {pagination && (
        <div className="pagination">
          <button 
            disabled={!pagination.hasPrevious}
            onClick={() => handlePageChange(pagination.page - 1)}
          >
            Previous
          </button>
          <span>
            Page {pagination.page} of {Math.ceil(pagination.total / pagination.size)}
          </span>
          <button 
            disabled={!pagination.hasNext}
            onClick={() => handlePageChange(pagination.page + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export function FeaturedProductsExample() {
  const { fetchFeaturedProducts } = useProductCatalog();
  const [featuredProducts, setFeaturedProducts] = useState<ProductCatalog[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadFeatured = async () => {
      setLoading(true);
      try {
        const products = await fetchFeaturedProducts(10);
        setFeaturedProducts(products);
      } catch (error) {
        console.error('Failed to load featured products:', error);
      } finally {
        setLoading(false);
      }
    };

    loadFeatured();
  }, []);

  if (loading) return <div>Loading featured products...</div>;

  return (
    <div className="featured-products">
      <h2>Featured Products</h2>
      <div className="products-carousel">
        {featuredProducts.map(product => (
          <div key={product.id} className="featured-product-card">
            <img src={product.image_url || '/placeholder.jpg'} alt={product.name} />
            <h4>{product.name}</h4>
            <p>${product.price}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AdminProductManagementExample() {
  const { createProduct, updateProduct, deleteProduct } = useProducts();
  const [productData, setProductData] = useState({
    name: '',
    description: '',
    price: 0,
    category_id: 1,
    image_urls: [''],
    stock_quantity: 0,
    availability_type: AvailabilityType.IN_STOCK,
    is_active: true
  });

  const handleCreateProduct = async () => {
    try {
      await createProduct(productData);
      alert('Product created successfully!');
      // Reset form
      setProductData({
        name: '',
        description: '',
        price: 0,
        category_id: 1,
        image_urls: [''],
        stock_quantity: 0,
        availability_type: AvailabilityType.IN_STOCK,
        is_active: true
      });
    } catch (error) {
      alert('Failed to create product');
    }
  };

  return (
    <div className="admin-product-form">
      <h2>Create New Product</h2>
      <form onSubmit={(e) => { e.preventDefault(); handleCreateProduct(); }}>
        <div>
          <label>Product Name:</label>
          <input
            type="text"
            value={productData.name}
            onChange={(e) => setProductData(prev => ({ ...prev, name: e.target.value }))}
            required
          />
        </div>

        <div>
          <label>Description:</label>
          <textarea
            value={productData.description}
            onChange={(e) => setProductData(prev => ({ ...prev, description: e.target.value }))}
          />
        </div>

        <div>
          <label>Price:</label>
          <input
            type="number"
            step="0.01"
            value={productData.price}
            onChange={(e) => setProductData(prev => ({ ...prev, price: parseFloat(e.target.value) }))}
            required
          />
        </div>

        <div>
          <label>Stock Quantity:</label>
          <input
            type="number"
            value={productData.stock_quantity}
            onChange={(e) => setProductData(prev => ({ ...prev, stock_quantity: parseInt(e.target.value) }))}
          />
        </div>

        <div>
          <label>Availability:</label>
          <select
            value={productData.availability_type}
            onChange={(e) => setProductData(prev => ({ ...prev, availability_type: e.target.value as AvailabilityType }))}
          >
            <option value={AvailabilityType.IN_STOCK}>In Stock</option>
            <option value={AvailabilityType.PRE_ORDER}>Pre-order</option>
            <option value={AvailabilityType.DISCONTINUED}>Discontinued</option>
          </select>
        </div>

        <div>
          <label>Image URLs (comma-separated):</label>
          <input
            type="text"
            value={productData.image_urls.join(', ')}
            onChange={(e) => setProductData(prev => ({ 
              ...prev, 
              image_urls: e.target.value.split(',').map(url => url.trim()) 
            }))}
          />
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              checked={productData.is_active}
              onChange={(e) => setProductData(prev => ({ ...prev, is_active: e.target.checked }))}
            />
            Active
          </label>
        </div>

        <button type="submit">Create Product</button>
      </form>
    </div>
  );
}
