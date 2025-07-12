import React, { useState } from 'react';
import {
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
  Button,
  Spinner
} from '@heroui/react';
import { Upload, X } from 'lucide-react';
import { ProductCreateRequest, AvailabilityType, Category, ProductImageCreate, ImageType } from '@/types/product';
import { uploadImage, validateImageFile } from '@/lib/storage';

interface AddProductProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  categories: Category[];
  onProductAdded: () => void;
}

const AddProduct: React.FC<AddProductProps> = ({ isOpen, onOpenChange, categories, onProductAdded }) => {
  const [formData, setFormData] = useState<ProductCreateRequest>({
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
  const [submitting, setSubmitting] = useState(false);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;
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
      URL.revokeObjectURL(prev[index]);
      return newUrls;
    });
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
      let imageUrls: ProductImageCreate[] = [];
      if (selectedFiles.length > 0) {
        setUploadingImages(true);
        try {
          const uploadPromises = selectedFiles.map(file => uploadImage(file, 'products'));
          const urls = await Promise.all(uploadPromises);
          imageUrls = urls.map(url => ({ image_url: url, image_type: ImageType.OFFICIAL }));
        } catch (uploadError) {
          setError('Failed to upload images');
          return;
        } finally {
          setUploadingImages(false);
        }
      }
      const productData = { ...formData, images: imageUrls };
      const token = await (await import('@/lib/api')).ApiClient.getToken();
      const response = await fetch('/api/v1/products/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(productData)
      });
      if (response.ok) {
        onProductAdded();
        onOpenChange(false);
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
        setSelectedFiles([]);
        setPreviewUrls([]);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create product');
      }
    } catch (err) {
      setError('Failed to create product');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onOpenChange={(open) => {
        if (!open) {
          previewUrls.forEach(url => URL.revokeObjectURL(url));
          setPreviewUrls([]);
          setSelectedFiles([]);
          setError(null);
        }
        onOpenChange(open);
      }}
      size="3xl"
      className="bg-white"
    >
      <ModalContent className="bg-white">
        {(onClose) => (
          <>
            <ModalHeader className="flex flex-col gap-1 bg-white text-gray-900">
              Add New Product
            </ModalHeader>
            <ModalBody className="bg-white">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Product Name"
                    placeholder="Enter product name"
                    value={formData.name}
                    onValueChange={(value) => setFormData({ ...formData, name: value })}
                    isRequired
                  />
                  <Select
                    label="Category"
                    placeholder="Select category"
                    selectedKeys={[formData.category_id.toString()]}
                    onSelectionChange={(keys) => {
                      const selectedKey = Array.from(keys)[0] as string;
                      setFormData({ ...formData, category_id: parseInt(selectedKey) });
                    }}
                    isRequired
                  >
                    {categories.map((category) => (
                      <SelectItem key={category.id}>{category.name}</SelectItem>
                    ))}
                  </Select>
                </div>
                <Textarea
                  label="Description"
                  placeholder="Enter product description"
                  value={formData.description || ''}
                  onValueChange={(value) => setFormData({ ...formData, description: value })}
                />
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Product Images (Max 5)
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                      <input
                        type="file"
                        multiple
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="hidden"
                        id="image-upload"
                      />
                      <label
                        htmlFor="image-upload"
                        className="cursor-pointer flex flex-col items-center space-y-2"
                      >
                        <Upload className="h-8 w-8 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          Click to upload or drag and drop
                        </span>
                        <span className="text-xs text-gray-500">
                          PNG, JPG, WebP up to 5MB each
                        </span>
                      </label>
                    </div>
                  </div>
                  {previewUrls.length > 0 && (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                      {previewUrls.map((url, index) => (
                        <div key={index} className="relative group">
                          <img
                            src={url}
                            alt={`Preview ${index + 1}`}
                            className="w-full h-20 object-cover rounded-lg border border-gray-200"
                          />
                          <button
                            type="button"
                            onClick={() => removeImage(index)}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    type="number"
                    label="Price"
                    placeholder="0.00"
                    value={formData.price.toString()}
                    onValueChange={(value) => setFormData({ ...formData, price: parseFloat(value) || 0 })}
                    startContent={<span className="text-gray-500">$</span>}
                    isRequired
                  />
                  <Input
                    type="number"
                    label="Stock Quantity"
                    placeholder="0"
                    value={formData.stock_quantity.toString()}
                    onValueChange={(value) => setFormData({ ...formData, stock_quantity: parseInt(value) || 0 })}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Select
                    label="Availability Type"
                    selectedKeys={[formData.availability_type]}
                    onSelectionChange={(keys) => {
                      const selectedKey = Array.from(keys)[0] as AvailabilityType;
                      setFormData({ ...formData, availability_type: selectedKey });
                    }}
                  >
                    <SelectItem key={AvailabilityType.IN_STOCK}>In Stock</SelectItem>
                    <SelectItem key={AvailabilityType.PRE_ORDER}>Pre-Order</SelectItem>
                    <SelectItem key={AvailabilityType.DISCONTINUED}>Discontinued</SelectItem>
                  </Select>
                  <div className="flex items-center justify-between">
                    <Switch
                      isSelected={formData.is_active}
                      onValueChange={(value) => setFormData({ ...formData, is_active: value })}
                    >
                      Active Product
                    </Switch>
                  </div>
                </div>
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                    <p className="text-red-700">{error}</p>
                  </div>
                )}
              </form>
            </ModalBody>
            <ModalFooter className="bg-white">
              <Button color="danger" variant="light" onPress={() => onOpenChange(false)} className="text-red-600">
                Cancel
              </Button>
              <Button
                color="primary"
                onPress={createProduct}
                isLoading={submitting || uploadingImages}
                className="bg-blue-600 text-white"
              >
                {uploadingImages ? 'Uploading Images...' : submitting ? 'Creating...' : 'Create Product'}
              </Button>
            </ModalFooter>
          </>
        )}
      </ModalContent>
    </Modal>
  );
};

export default AddProduct; 