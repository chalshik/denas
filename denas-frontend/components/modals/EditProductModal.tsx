'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Card, CardBody } from '@heroui/card';
import { Select, SelectItem } from '@heroui/select';
import { Switch } from '@heroui/switch';
import { Form } from '@heroui/form';
import { useForm } from '@/hooks/useForm';
import { useProducts } from '@/hooks/useProducts';
import { useCategories } from '@/hooks/useCategories';
import { Product } from '@/types';

interface EditProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: Product | null;
}

export default function EditProductModal({ 
  isOpen, 
  onClose, 
  product
}: EditProductModalProps) {
  const { updateProduct, loading } = useProducts();
  const { categories = [], fetchCategories } = useCategories();
  
  const { form, setForm, handleInput, resetForm } = useForm({
    name: '',
    description: '',
    price: 1,
    stock_quantity: 0,
    availability_type: 'in_stock',
    preorder_day: '',
    preorder_month: '',
    preorder_year: '',
    is_active: true,
    category_id: '',
    images: [] as File[],
  });

  const [imagePreviews, setImagePreviews] = useState<string[]>([]);

  const availabilityOptions = [
    { label: 'In Stock', value: 'in_stock' },
    { label: 'Pre-order', value: 'pre_order' },
    { label: 'Discontinued', value: 'discontinued' },
  ];

  // Генерируем дни (1-31)
  const dayOptions = Array.from({ length: 31 }, (_, i) => ({
    label: String(i + 1),
    value: String(i + 1)
  }));

  // Генерируем месяцы
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

  // Генерируем годы (текущий год + 5 лет вперед)
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 6 }, (_, i) => ({
    label: String(currentYear + i),
    value: String(currentYear + i)
  }));

  useEffect(() => {
    fetchCategories();
  }, []);

  // Pre-fill form when product changes
  useEffect(() => {
    if (product) {
      // Разбираем дату preorder_available_date на компоненты
      let preorderDay = '';
      let preorderMonth = '';
      let preorderYear = '';
      
      if (product.preorder_available_date) {
        const date = new Date(product.preorder_available_date);
        preorderDay = String(date.getDate());
        preorderMonth = String(date.getMonth() + 1);
        preorderYear = String(date.getFullYear());
      }
      
      setForm({
        name: product.name || '',
        description: product.description || '',
        price: product.price || 1,
        stock_quantity: product.stock_quantity || 0,
        availability_type: product.availability_type || 'in_stock',
        preorder_day: preorderDay,
        preorder_month: preorderMonth,
        preorder_year: preorderYear,
        is_active: product.is_active ?? true,
        category_id: product.category_id?.toString() || '',
        images: [],
      });
    }
  }, [product, setForm]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files!);
      setForm(f => ({ ...f, images: files }));
      // Генерируем превью
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
    if (!product) return;
    
    // Формируем дату из отдельных полей
    const preorderDate = form.preorder_day && form.preorder_month && form.preorder_year
      ? `${form.preorder_year}-${form.preorder_month.padStart(2, '0')}-${form.preorder_day.padStart(2, '0')}`
      : '';
    
    const submitData = {
      ...form,
      category_id: parseInt(form.category_id) || undefined,
      availability_type: form.availability_type as any,
      preorder_available_date: preorderDate
    };
    
    await updateProduct(product.id, submitData);
    resetForm();
    setImagePreviews([]);
    onClose();
  };

  const handleClose = () => {
    resetForm();
    setImagePreviews([]);
    onClose();
  };

  if (!isOpen || !product) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/25">
      <Card className="w-full max-w-lg p-6">
        <Form onSubmit={handleSubmit} className="space-y-4">
          <h2 className="text-xl font-bold mb-2">Edit Product</h2>
          
          <div className="w-full">
            <label className="block text-sm font-medium text-black mb-1">Name</label>
            <Input 
              name="name" 
              value={form.name} 
              onChange={handleInput} 
              required 
              fullWidth
              classNames={{
                base: "w-full",
                mainWrapper: "w-full",
                input: "w-full",
                inputWrapper: "w-full"
              }}
            />
          </div>
          
          <div className="w-full">
            <label className="block text-sm font-medium text-black mb-1">Description</label>
            <Input 
              name="description" 
              value={form.description} 
              onChange={handleInput} 
              required 
              fullWidth
              classNames={{
                base: "w-full",
                mainWrapper: "w-full",
                input: "w-full",
                inputWrapper: "w-full"
              }}
            />
          </div>
          
          <div className="w-full">
            <label className="block text-sm font-medium text-black mb-1">Price</label>
            <Input 
              name="price" 
              type="number" 
              value={String(form.price)} 
              onChange={handleInput} 
              required 
              min={0.01} 
              step={0.01}
              fullWidth
              classNames={{
                base: "w-full",
                mainWrapper: "w-full",
                input: "w-full",
                inputWrapper: "w-full"
              }}
            />
          </div>
          
          <div className="w-full">
            <label className="block text-sm font-medium text-black mb-1">Stock Quantity</label>
            <Input 
              name="stock_quantity" 
              type="number" 
              value={String(form.stock_quantity)} 
              onChange={handleInput} 
              required 
              min={0}
              fullWidth
              classNames={{
                base: "w-full",
                mainWrapper: "w-full",
                input: "w-full",
                inputWrapper: "w-full"
              }}
            />
          </div>
          
          <div className="w-full">
            <label className="block text-sm font-medium text-black mb-1">Availability Type</label>
            <Select
              selectedKeys={[form.availability_type]}
              onSelectionChange={keys => handleInput({ target: { name: 'availability_type', value: Array.from(keys)[0] } } as any)}
              fullWidth
              classNames={{
                base: "w-full",
                mainWrapper: "w-full",
                trigger: "w-full"
              }}
            >
              <>
                {availabilityOptions.map(opt => (
                  <SelectItem key={opt.value}>{opt.label}</SelectItem>
                ))}
              </>
            </Select>
          </div>
          
          <div className="w-full">
            <label className="block text-sm font-medium text-black mb-1">Preorder Available Date</label>
            <div className="flex gap-2">
              <Select
                selectedKeys={[form.preorder_day]}
                onSelectionChange={keys => handleInput({ target: { name: 'preorder_day', value: Array.from(keys)[0] } } as any)}
                placeholder="Day"
                classNames={{
                  base: "flex-1",
                  mainWrapper: "w-full",
                  trigger: "w-full"
                }}
              >
                <>
                  {dayOptions.map(opt => (
                    <SelectItem key={opt.value}>{opt.label}</SelectItem>
                  ))}
                </>
              </Select>
              
              <Select
                selectedKeys={[form.preorder_month]}
                onSelectionChange={keys => handleInput({ target: { name: 'preorder_month', value: Array.from(keys)[0] } } as any)}
                placeholder="Month"
                classNames={{
                  base: "flex-1",
                  mainWrapper: "w-full",
                  trigger: "w-full"
                }}
              >
                <>
                  {monthOptions.map(opt => (
                    <SelectItem key={opt.value}>{opt.label}</SelectItem>
                  ))}
                </>
              </Select>
              
              <Select
                selectedKeys={[form.preorder_year]}
                onSelectionChange={keys => handleInput({ target: { name: 'preorder_year', value: Array.from(keys)[0] } } as any)}
                placeholder="Year"
                classNames={{
                  base: "flex-1",
                  mainWrapper: "w-full",
                  trigger: "w-full"
                }}
              >
                <>
                  {yearOptions.map(opt => (
                    <SelectItem key={opt.value}>{opt.label}</SelectItem>
                  ))}
                </>
              </Select>
            </div>
          </div>
          
          <div className="w-full">
            <label className="block text-sm font-medium text-black mb-1">Category</label>
            <Select
              selectedKeys={[form.category_id]}
              onSelectionChange={keys => handleInput({ target: { name: 'category_id', value: Array.from(keys)[0] } } as any)}
              required
              fullWidth
              classNames={{
                base: "w-full",
                mainWrapper: "w-full",
                trigger: "w-full"
              }}
            >
              <>
                <SelectItem key="">Select category</SelectItem>
                {categories.map(cat => <SelectItem key={String(cat.id)}>{cat.name}</SelectItem>)}
              </>
            </Select>
          </div>
          
          <div className="w-full">
            <label className="block text-sm font-medium text-black mb-1">Images</label>
            <Input 
              name="images" 
              type="file" 
              multiple 
              accept="image/*" 
              onChange={handleImageChange}
              fullWidth
              classNames={{
                base: "w-full",
                mainWrapper: "w-full",
                input: "w-full",
                inputWrapper: "w-full"
              }}
            />
          </div>
          
          {imagePreviews.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {imagePreviews.map((src, i) => (
                <img key={i} src={src} alt={`preview-${i}`} className="w-20 h-20 object-cover rounded border" />
              ))}
            </div>
          )}
          
          <Switch 
            isSelected={form.is_active} 
            onValueChange={val => handleInput({ target: { name: 'is_active', type: 'checkbox', checked: val } } as any)}
          >
            Active
          </Switch>
          
          <div className="flex gap-2 justify-end">
            <Button type="button" variant="light" onPress={handleClose}>
              Cancel
            </Button>
            <Button type="submit" color="primary" isLoading={loading}>
              Update Product
            </Button>
          </div>
        </Form>
      </Card>
    </div>
  );
} 