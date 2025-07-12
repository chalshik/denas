'use client';

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Modal, 
  ModalContent, 
  ModalHeader, 
  ModalBody, 
  ModalFooter,
  Input,
  Textarea,
  Select,
  SelectItem,
  Switch,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Spinner,
  useDisclosure
} from '@heroui/react';
import { Plus, Edit, Trash2, Package, Upload, X, Image as ImageIcon } from 'lucide-react';
import { useRole } from '@/hooks/useRole';
import { ApiClient } from '@/lib/api';
import { 
  ProductCatalog, 
  ProductCreateRequest, 
  AvailabilityType, 
  Category,
  ProductImageCreate,
  ImageType
} from '@/types/product';
import { uploadImage, validateImageFile } from '@/lib/storage';
import AddProduct from './add-product';

export const ProductsManagement: React.FC = () => {
  const { canAccess } = useRole();
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  
  const [products, setProducts] = useState<ProductCatalog[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  
  // Form state
  const [formData, setFormData] = useState<ProductCreateRequest>({
    name: '',
    description: '',
    price: 0,
    stock_quantity: 0,
    availability_type: AvailabilityType.IN_STOCK,
    preorder_available_date: null,
    is_active: true,
    category_id: 1,
    images: []
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = await ApiClient.getToken();
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Fetch products
      const productsResponse = await fetch('/api/v1/products/', {
        headers
      });
      if (productsResponse.ok) {
        const productsData = await productsResponse.json();
        setProducts(productsData);
      }

      // Fetch categories
      const categoriesResponse = await fetch('/api/v1/categories/', {
        headers
      });
      if (categoriesResponse.ok) {
        const categoriesData = await categoriesResponse.json();
        setCategories(categoriesData);
      }


    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createProduct();
  };

  const createProduct = async () => {
    if (!formData.name || !formData.price || !formData.category_id) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      // Upload images first if any are selected
      let imageUrls: ProductImageCreate[] = [];
      if (selectedFiles.length > 0) {
        setUploadingImages(true);
        try {
          const uploadPromises = selectedFiles.map(file => uploadImage(file, 'products'));
          const urls = await Promise.all(uploadPromises);
          imageUrls = urls.map(url => ({
            image_url: url,
            image_type: ImageType.OFFICIAL
          }));
        } catch (uploadError) {
          console.error('Error uploading images:', uploadError);
          setError('Failed to upload images');
          return;
        } finally {
          setUploadingImages(false);
        }
      }

      // Create product with image URLs
      const productData = {
        ...formData,
        images: imageUrls
      };
      
      const token = await ApiClient.getToken();
      const response = await fetch('/api/v1/products/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(productData)
      });

      if (response.ok) {
        await fetchData(); // Refresh data
        onOpenChange(); // Close modal
        
        // Reset form
        setFormData({
          name: '',
          description: '',
          price: 0,
          stock_quantity: 0,
          availability_type: AvailabilityType.IN_STOCK,
          preorder_available_date: null,
          is_active: true,
          category_id: categories[0]?.id || 1,
          images: []
        });
        
        // Reset image state
        setSelectedFiles([]);
        setPreviewUrls([]);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create product');
      }
    } catch (err) {
      console.error('Error creating product:', err);
      setError('Failed to create product');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    
    if (files.length === 0) return;

    // Validate each file
    const validFiles: File[] = [];
    const newPreviewUrls: string[] = [];
    
    for (const file of files) {
      const validation = validateImageFile(file);
      if (validation.isValid) {
        validFiles.push(file);
        newPreviewUrls.push(URL.createObjectURL(file));
      } else {
        setError(validation.error || 'Invalid file');
        return;
      }
    }

    // Add to existing files (max 5 images)
    const totalFiles = selectedFiles.length + validFiles.length;
    if (totalFiles > 5) {
      setError('Maximum 5 images allowed');
      return;
    }

    setSelectedFiles(prev => [...prev, ...validFiles]);
    setPreviewUrls(prev => [...prev, ...newPreviewUrls]);
    setError(null);
  };

  const removeImage = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setPreviewUrls(prev => {
      const newUrls = prev.filter((_, i) => i !== index);
      // Clean up the removed URL
      URL.revokeObjectURL(prev[index]);
      return newUrls;
    });
  };

  const getAvailabilityColor = (availability: AvailabilityType) => {
    switch (availability) {
      case AvailabilityType.IN_STOCK:
        return 'success';
      case AvailabilityType.PRE_ORDER:
        return 'warning';
      case AvailabilityType.DISCONTINUED:
        return 'danger';
      default:
        return 'default';
    }
  };

  const getAvailabilityLabel = (availability: AvailabilityType) => {
    switch (availability) {
      case AvailabilityType.IN_STOCK:
        return 'In Stock';
      case AvailabilityType.PRE_ORDER:
        return 'Pre-Order';
      case AvailabilityType.DISCONTINUED:
        return 'Discontinued';
      default:
        return availability;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96 bg-gray-50">
        <Spinner color="primary" size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen p-6">
      {/* Header */}
      <div className="flex justify-end items-center">
        <Button
          color="primary"
          startContent={<Plus className="h-4 w-4" />}
          onPress={onOpen}
          className="bg-blue-600 text-white"
        >
          Add Product
        </Button>
      </div>

      {/* Products Table */}
      <Card className="bg-white">
        <CardBody className="bg-white p-0">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-red-700">{error}</p>
            </div>
          )}
          
          {products.length > 0 ? (
            <Table aria-label="Products table" className="bg-white">
              <TableHeader>
                <TableColumn className="bg-gray-50 text-gray-900 font-semibold">Photo</TableColumn>
                <TableColumn className="bg-gray-50 text-gray-900 font-semibold">Name</TableColumn>
                <TableColumn className="bg-gray-50 text-gray-900 font-semibold">Price</TableColumn>
                <TableColumn className="bg-gray-50 text-gray-900 font-semibold">Is Active</TableColumn>
                <TableColumn className="bg-gray-50 text-gray-900 font-semibold">Date</TableColumn>
                <TableColumn className="bg-gray-50 text-gray-900 font-semibold">Actions</TableColumn>
              </TableHeader>
              <TableBody>
                {products.map((product) => (
                  <TableRow key={product.id} className="bg-white hover:bg-gray-50">
                    <TableCell className="bg-white">
                      <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                        {product.primary_image ? (
                          <img 
                            src={product.primary_image.image_url} 
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <Package className="h-6 w-6 text-gray-400" />
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="font-medium text-gray-900 bg-white">
                      <div>
                        <div className="font-medium">{product.name}</div>
                        <div className="text-sm text-gray-500">#{product.id}</div>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium text-gray-900 bg-white">
                      ${product.price}
                    </TableCell>
                    <TableCell className="bg-white">
                      <Chip
                        color={product.is_active ? 'success' : 'danger'}
                        size="sm"
                        variant="flat"
                      >
                        {product.is_active ? 'Active' : 'Inactive'}
                      </Chip>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600 bg-white">
                      {new Date().toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </TableCell>
                    <TableCell className="bg-white">
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="light"
                          color="primary"
                          startContent={<Edit className="h-3 w-3" />}
                          className="text-blue-600"
                        >
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="light"
                          color="danger"
                          startContent={<Trash2 className="h-3 w-3" />}
                          className="text-red-600"
                        >
                          Delete
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 bg-white">
              <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-700 font-medium">No products found</p>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Add Product Modal */}
      <AddProduct
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        categories={categories}
        onProductAdded={fetchData}
      />
    </div>
  );
};

export default ProductsManagement; 