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
import { useForm } from '@/hooks/useForm';
import { useProducts } from '@/hooks/useProducts';
import { useCategories } from '@/hooks/useCategories';

interface CreateProductModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CreateProductModal({ 
  isOpen, 
  onClose
}: CreateProductModalProps) {
  const { createProduct, loading } = useProducts();
  const { categories = [], fetchCategories } = useCategories();
  
  const { form, setForm, handleInput, resetForm } = useForm({
    name: '',
    description: '',
    price: 1,
    stock_quantity: 0,
    availability_type: 'IN_STOCK',
    preorder_day: '',
    preorder_month: '',
    preorder_year: '',
    is_active: true,
    category_id: '',
    images: [] as File[],
  });

  const [imagePreviews, setImagePreviews] = useState<string[]>([]);

  const availabilityOptions = [
    { label: 'In Stock', value: 'IN_STOCK' },
    { label: 'Pre-order', value: 'PRE_ORDER' },
    { label: 'Discontinued', value: 'DISCONTINUED' },
  ];

  // Generate days (1-31)
  const dayOptions = Array.from({ length: 31 }, (_, i) => ({
    label: String(i + 1),
    value: String(i + 1)
  }));

  // Generate months
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

  // Generate years (current year + 5 years forward)
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 6 }, (_, i) => ({
    label: String(currentYear + i),
    value: String(currentYear + i)
  }));

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files!);
      setForm(f => ({ ...f, images: files }));
      // Generate previews
      Promise.all(files.map(file => {
        return new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onload = (ev) => resolve(ev.target?.result as string);
          reader.readAsDataURL(file);
        });
      })).then(setImagePreviews);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // Form date from separate fields
      const preorderDate = form.preorder_day && form.preorder_month && form.preorder_year
        ? `${form.preorder_year}-${form.preorder_month.padStart(2, '0')}-${form.preorder_day.padStart(2, '0')}`
        : undefined;
      
      const submitData = {
        name: form.name,
        description: form.description,
        price: parseFloat(String(form.price)),
        category_id: parseInt(form.category_id) || 0,
        stock_quantity: parseInt(String(form.stock_quantity)) || 0,
        availability_type: form.availability_type as any,
        preorder_available_date: preorderDate,
        is_active: form.is_active,
        images: form.images
      };
      
      await createProduct(submitData);
      resetForm();
      setImagePreviews([]);
      onClose();
    } catch (error) {
      console.error('Failed to create product:', error);
    }
  };

  const handleClose = () => {
    resetForm();
    setImagePreviews([]);
    onClose();
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose}
      size="2xl"
      scrollBehavior="inside"
    >
      <ModalContent>
        <form onSubmit={handleSubmit}>
          <ModalHeader>
            Add New Product
          </ModalHeader>
          
          <ModalBody>
            <div className="space-y-4">
              <Input 
                name="name" 
                label="Product Name"
                value={form.name} 
                onChange={handleInput} 
                isRequired
              />
              
              <Input 
                name="description" 
                label="Description"
                value={form.description} 
                onChange={handleInput}
              />
              
              <div className="grid grid-cols-2 gap-4">
                <Input 
                  name="price" 
                  label="Price"
                  type="number" 
                  value={String(form.price)} 
                  onChange={handleInput} 
                  isRequired 
                  min={0.01} 
                  step={0.01}
                  startContent="$"
                />
                
                <Input 
                  name="stock_quantity" 
                  label="Stock Quantity"
                  type="number" 
                  value={String(form.stock_quantity)} 
                  onChange={handleInput} 
                  isRequired 
                  min={0}
                />
              </div>
              
              <Select
                name="availability_type"
                label="Availability Type"
                selectedKeys={[form.availability_type]}
                onSelectionChange={keys => handleInput({ target: { name: 'availability_type', value: Array.from(keys)[0] } } as any)}
              >
                {availabilityOptions.map(opt => (
                  <SelectItem key={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </Select>
              
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
              
              <Select
                name="category_id"
                label="Category"
                selectedKeys={[form.category_id]}
                onSelectionChange={keys => handleInput({ target: { name: 'category_id', value: Array.from(keys)[0] } } as any)}
                isRequired
              >
                {[
                  <SelectItem key="">Select category</SelectItem>,
                  ...categories.map(cat => (
                    <SelectItem key={String(cat.id)}>
                      {cat.name}
                    </SelectItem>
                  ))
                ]}
              </Select>
              
              <Input 
                name="images" 
                label="Product Images"
                type="file" 
                multiple 
                accept="image/*" 
                onChange={handleImageChange}
              />
              
              {imagePreviews.length > 0 && (
                <div className="grid grid-cols-4 gap-2">
                  {imagePreviews.map((src, i) => (
                    <img 
                      key={i} 
                      src={src} 
                      alt={`Preview ${i + 1}`}
                      className="w-full h-20 object-cover rounded"
                    />
                  ))}
                </div>
              )}
              
              <Switch 
                isSelected={form.is_active} 
                onValueChange={val => handleInput({ target: { name: 'is_active', type: 'checkbox', checked: val } } as any)}
              >
                Active Product
              </Switch>
            </div>
          </ModalBody>
          
          <ModalFooter>
            <Button 
              variant="flat" 
              onPress={handleClose}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              color="primary" 
              isLoading={loading}
            >
              Create Product
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
}