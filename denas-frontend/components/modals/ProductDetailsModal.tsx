'use client';

import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  ModalContent, 
  ModalHeader, 
  ModalBody, 
  ModalFooter 
} from '@heroui/modal';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Select, SelectItem } from '@heroui/select';
import { Switch } from '@heroui/switch';
import { Image } from '@heroui/image';
import { Chip } from '@heroui/chip';
import { Divider } from '@heroui/divider';
import { Spinner } from '@heroui/spinner';
import { useProducts } from '@/hooks/useProducts';
import { useCategories } from '@/hooks/useCategories';
import { useForm } from '@/hooks/useForm';
import { ProductWithDetails, AvailabilityType } from '@/types';

interface ProductDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  productId: number | null;
}

export default function ProductDetailsModal({ 
  isOpen, 
  onClose, 
  productId 
}: ProductDetailsModalProps) {
  const { updateProduct, getProductDetails, loading: updateLoading } = useProducts();
  const { categories = [], fetchCategories } = useCategories();
  const [product, setProduct] = useState<ProductWithDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [imageFiles, setImageFiles] = useState<File[]>([]);

  const { form, setForm, handleInput, resetForm } = useForm({
    name: '',
    description: '',
    price: 0,
    stock_quantity: 0,
    availability_type: AvailabilityType.IN_STOCK,
    preorder_day: '',
    preorder_month: '',
    preorder_year: '',
    is_active: true,
    category_id: 0,
  });

  const availabilityOptions = [
    { label: 'In Stock', value: 'IN_STOCK' },
    { label: 'Pre-order', value: 'PRE_ORDER' },
    { label: 'Discontinued', value: 'DISCONTINUED' },
  ];

  // Generate day/month/year options
  const dayOptions = Array.from({ length: 31 }, (_, i) => ({
    label: String(i + 1),
    value: String(i + 1)
  }));

  const monthOptions = [
    { label: 'January', value: '1' },
    { label: 'February', value: '2' },
    { label: 'March', value: '3' },
    { label: 'April', value: '4' },
    { label: 'May', value: '5' },
    { label: 'June', value: '6' },
    { label: 'July', value: '7' },
    { label: 'August', value: '8' },
    { label: 'September', value: '9' },
    { label: 'October', value: '10' },
    { label: 'November', value: '11' },
    { label: 'December', value: '12' }
  ];

  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 6 }, (_, i) => ({
    label: String(currentYear + i),
    value: String(currentYear + i)
  }));

  // Fetch product details
  const fetchProductDetails = async (id: number) => {
    setLoading(true);
    try {
      const productDetails = await getProductDetails(id);
      setProduct(productDetails);
      
      // Populate form with current product data
      const preorderDate = productDetails.preorder_available_date 
        ? new Date(productDetails.preorder_available_date) 
        : null;
      
      setForm({
        name: productDetails.name,
        description: productDetails.description || '',
        price: productDetails.price,
        stock_quantity: productDetails.stock_quantity || 0,
        availability_type: productDetails.availability_type || AvailabilityType.IN_STOCK,
        preorder_day: preorderDate ? String(preorderDate.getDate()) : '',
        preorder_month: preorderDate ? String(preorderDate.getMonth() + 1) : '',
        preorder_year: preorderDate ? String(preorderDate.getFullYear()) : '',
        is_active: productDetails.is_active ?? true,
        category_id: productDetails.category_id,
      });
    } catch (error) {
      console.error('Failed to fetch product details:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && productId) {
      fetchProductDetails(productId);
      fetchCategories();
    }
  }, [isOpen, productId]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setImageFiles(Array.from(e.target.files));
    }
  };

  const handleSave = async () => {
    if (!product) return;

    try {
      // Form date from separate fields
      const preorderDate = form.preorder_day && form.preorder_month && form.preorder_year
        ? `${form.preorder_year}-${form.preorder_month.padStart(2, '0')}-${form.preorder_day.padStart(2, '0')}`
        : undefined;

      const updateData = {
        name: form.name,
        description: form.description,
        price: parseFloat(String(form.price)),
        category_id: parseInt(String(form.category_id)),
        stock_quantity: parseInt(String(form.stock_quantity)),
        availability_type: form.availability_type,
        preorder_available_date: preorderDate,
        is_active: form.is_active,
        images: imageFiles.length > 0 ? imageFiles : undefined,
      };

      await updateProduct(product.id, updateData);
      setIsEditing(false);
      await fetchProductDetails(product.id); // Refresh data
    } catch (error) {
      console.error('Failed to update product:', error);
    }
  };

  const handleClose = () => {
    setProduct(null);
    setIsEditing(false);
    resetForm();
    setImageFiles([]);
    onClose();
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getAvailabilityColor = (availability: string) => {
    switch (availability) {
      case 'IN_STOCK':
        return 'success';
      case 'PRE_ORDER':
        return 'warning';
      case 'DISCONTINUED':
        return 'danger';
      default:
        return 'default';
    }
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose}
      size="4xl"
      scrollBehavior="inside"
    >
      <ModalContent>
        <ModalHeader>
          {loading ? 'Loading Product...' : isEditing ? 'Edit Product' : 'Product Details'}
        </ModalHeader>
        
        <ModalBody>
          {loading ? (
            <div className="flex justify-center py-8">
              <Spinner size="lg" />
            </div>
          ) : product ? (
            <div className="space-y-6">
              {/* Product Images */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Images</h3>
                {product.images && product.images.length > 0 ? (
                  <div className="grid grid-cols-4 gap-4">
                    {product.images.map((image, index) => (
                      <div key={image.id} className="relative">
                        <Image
                          src={image.image_url}
                          alt={`${product.name} - Image ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg"
                        />
                        <Chip
                          size="sm"
                          variant="flat"
                          className="absolute top-2 right-2"
                        >
                          {image.image_type}
                        </Chip>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No images available</p>
                )}
              </div>

              <Divider />

              {/* Product Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  {isEditing ? (
                    <Input
                      label="Product Name"
                      name="name"
                      value={form.name}
                      onChange={handleInput}
                      isRequired
                    />
                  ) : (
                    <div>
                      <label className="text-sm font-medium">Product Name</label>
                      <p className="text-lg font-semibold">{product.name}</p>
                    </div>
                  )}

                  {isEditing ? (
                    <Input
                      label="Description"
                      name="description"
                      value={form.description}
                      onChange={handleInput}
                    />
                  ) : (
                    <div>
                      <label className="text-sm font-medium">Description</label>
                      <p>{product.description || 'No description'}</p>
                    </div>
                  )}

                  {isEditing ? (
                    <Input
                      label="Price"
                      name="price"
                      type="number"
                      value={String(form.price)}
                      onChange={handleInput}
                      isRequired
                      min={0.01}
                      step={0.01}
                      startContent="$"
                    />
                  ) : (
                    <div>
                      <label className="text-sm font-medium">Price</label>
                      <p className="text-xl font-bold text-green-600">{formatPrice(product.price)}</p>
                    </div>
                  )}

                  {isEditing ? (
                    <Input
                      label="Stock Quantity"
                      name="stock_quantity"
                      type="number"
                      value={String(form.stock_quantity)}
                      onChange={handleInput}
                      min={0}
                    />
                  ) : (
                    <div>
                      <label className="text-sm font-medium">Stock Quantity</label>
                      <p>{product.stock_quantity || 0}</p>
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Category</label>
                    {isEditing ? (
                      <Select
                        label="Category"
                        name="category_id"
                        selectedKeys={[String(form.category_id)]}
                        onSelectionChange={keys => handleInput({ target: { name: 'category_id', value: Array.from(keys)[0] } } as any)}
                        isRequired
                      >
                        {categories.map(cat => (
                          <SelectItem key={String(cat.id)}>
                            {cat.name}
                          </SelectItem>
                        ))}
                      </Select>
                    ) : (
                      <p>{product.category?.name || `Category ${product.category_id}`}</p>
                    )}
                  </div>

                  <div>
                    <label className="text-sm font-medium">Availability</label>
                    {isEditing ? (
                      <Select
                        label="Availability Type"
                        name="availability_type"
                        selectedKeys={[form.availability_type]}
                        onSelectionChange={keys => handleInput({ target: { name: 'availability_type', value: Array.from(keys)[0] } } as any)}
                      >
                        {availabilityOptions.map(opt => (
                          <SelectItem key={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </Select>
                    ) : (
                      <Chip
                        color={getAvailabilityColor(product.availability_type || 'IN_STOCK')}
                        variant="flat"
                      >
                        {(product.availability_type || 'IN_STOCK').replace('_', ' ')}
                      </Chip>
                    )}
                  </div>

                  {isEditing && form.availability_type === 'PRE_ORDER' && (
                    <div>
                      <label className="text-sm font-medium mb-2 block">Preorder Available Date</label>
                      <div className="grid grid-cols-3 gap-2">
                        <Select
                          placeholder="Day"
                          selectedKeys={[form.preorder_day]}
                          onSelectionChange={keys => handleInput({ target: { name: 'preorder_day', value: Array.from(keys)[0] } } as any)}
                          size="sm"
                        >
                          {dayOptions.map(opt => (
                            <SelectItem key={opt.value}>
                              {opt.label}
                            </SelectItem>
                          ))}
                        </Select>
                        
                        <Select
                          placeholder="Month"
                          selectedKeys={[form.preorder_month]}
                          onSelectionChange={keys => handleInput({ target: { name: 'preorder_month', value: Array.from(keys)[0] } } as any)}
                          size="sm"
                        >
                          {monthOptions.map(opt => (
                            <SelectItem key={opt.value}>
                              {opt.label}
                            </SelectItem>
                          ))}
                        </Select>
                        
                        <Select
                          placeholder="Year"
                          selectedKeys={[form.preorder_year]}
                          onSelectionChange={keys => handleInput({ target: { name: 'preorder_year', value: Array.from(keys)[0] } } as any)}
                          size="sm"
                        >
                          {yearOptions.map(opt => (
                            <SelectItem key={opt.value}>
                              {opt.label}
                            </SelectItem>
                          ))}
                        </Select>
                      </div>
                    </div>
                  )}

                  {!isEditing && product.preorder_available_date && (
                    <div>
                      <label className="text-sm font-medium">Preorder Available Date</label>
                      <p>
                        {new Date(product.preorder_available_date).toLocaleDateString()}
                      </p>
                    </div>
                  )}

                  <div>
                    <label className="text-sm font-medium">Status</label>
                    {isEditing ? (
                      <Switch
                        isSelected={form.is_active}
                        onValueChange={val => handleInput({ target: { name: 'is_active', type: 'checkbox', checked: val } } as any)}
                      >
                        Active Product
                      </Switch>
                    ) : (
                      <Chip
                        color={product.is_active ? 'success' : 'danger'}
                        variant="flat"
                      >
                        {product.is_active ? 'Active' : 'Inactive'}
                      </Chip>
                    )}
                  </div>

                  {isEditing && (
                    <Input
                      label="Add New Images"
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleImageChange}
                    />
                  )}
                </div>
              </div>

              {/* Metadata */}
              <Divider />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Product ID:</span> #{product.id}
                </div>
                <div>
                  <span className="font-medium">Created:</span> {
                    product.created_at ? new Date(product.created_at).toLocaleDateString() : 'N/A'
                  }
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p>Product not found</p>
            </div>
          )}
        </ModalBody>
        
        <ModalFooter>
          <Button variant="flat" onPress={handleClose}>
            Close
          </Button>
          {product && !loading && (
            <>
              {isEditing ? (
                <>
                  <Button
                    variant="flat"
                    onPress={() => setIsEditing(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    color="primary"
                    onPress={handleSave}
                    isLoading={updateLoading}
                  >
                    Save Changes
                  </Button>
                </>
              ) : (
                <Button
                  color="primary"
                  onPress={() => setIsEditing(true)}
                >
                  Edit Product
                </Button>
              )}
            </>
          )}
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
} 