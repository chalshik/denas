'use client';

import React, { useState } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Card, CardBody } from '@heroui/card';
import { Select, SelectItem } from '@heroui/select';
import { Switch } from '@heroui/switch';
import { Form } from '@heroui/form';
import { useModal } from '@/hooks/useModal';
import { useForm } from '@/hooks/useForm';
import { Category } from '@/types';

interface CreateProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  categories: Category[];
  loading: boolean;
}

export default function CreateProductModal({ 
  isOpen, 
  onClose, 
  onSubmit, 
  categories, 
  loading 
}: CreateProductModalProps) {
  const { form, setForm, handleInput, resetForm } = useForm({
    name: '',
    description: '',
    price: 1,
    stock_quantity: 0,
    availability_type: 'in_stock',
    preorder_available_date: '',
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
    await onSubmit(form);
    resetForm();
    setImagePreviews([]);
  };

  const handleClose = () => {
    resetForm();
    setImagePreviews([]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/25">
      <Card className="w-full max-w-lg p-6">
        <Form onSubmit={handleSubmit} className="space-y-4">
          <h2 className="text-xl font-bold mb-2">Add New Product</h2>
          
          <div>
            <label className="block text-sm font-medium text-black mb-1">Name</label>
            <Input 
              name="name" 
              value={form.name} 
              onChange={handleInput} 
              required 
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-black mb-1">Description</label>
            <Input 
              name="description" 
              value={form.description} 
              onChange={handleInput} 
              required 
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-black mb-1">Price</label>
            <Input 
              name="price" 
              type="number" 
              value={String(form.price)} 
              onChange={handleInput} 
              required 
              min={0.01} 
              step={0.01} 
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-black mb-1">Stock Quantity</label>
            <Input 
              name="stock_quantity" 
              type="number" 
              value={String(form.stock_quantity)} 
              onChange={handleInput} 
              required 
              min={0} 
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-black mb-1">Availability Type</label>
            <Select
              selectedKeys={[form.availability_type]}
              onSelectionChange={keys => handleInput({ target: { name: 'availability_type', value: Array.from(keys)[0] } } as any)}
            >
              <>
                {availabilityOptions.map(opt => (
                  <SelectItem key={opt.value}>{opt.label}</SelectItem>
                ))}
              </>
            </Select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-black mb-1">Preorder Available Date</label>
            <Input 
              name="preorder_available_date" 
              type="datetime-local" 
              value={form.preorder_available_date} 
              onChange={handleInput} 
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-black mb-1">Category</label>
            <Select
              selectedKeys={[form.category_id]}
              onSelectionChange={keys => handleInput({ target: { name: 'category_id', value: Array.from(keys)[0] } } as any)}
              required
            >
              <>
                <SelectItem key="">Select category</SelectItem>
                {categories.map(cat => <SelectItem key={String(cat.id)}>{cat.name}</SelectItem>)}
              </>
            </Select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-black mb-1">Images</label>
            <Input 
              name="images" 
              type="file" 
              multiple 
              accept="image/*" 
              onChange={handleImageChange} 
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
              Create Product
            </Button>
          </div>
        </Form>
      </Card>
    </div>
  );
}