'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from '@heroui/table';
import { Card, CardBody } from '@heroui/card';
import { Select, SelectItem } from '@heroui/select';
import { Switch } from '@heroui/switch';
import { Form } from '@heroui/form';
import { useModal } from '@/app/hooks/useModal';
import { useForm } from '@/app/hooks/useForm';
import { useFetch } from '@/app/hooks/useFetch';

export default function AdminProductsPage() {
  const { data: products = [], loading: loadingProducts, refetch: refetchProducts } = useFetch<any[]>('/api/v1/products');
  const { data: categories = [] } = useFetch<any[]>('/api/v1/categories');
  const [searchTerm, setSearchTerm] = useState('');
  const modal = useModal();
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
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const availabilityOptions = [
    { label: 'In Stock', value: 'in_stock' },
    { label: 'Pre-order', value: 'pre_order' },
    { label: 'Discontinued', value: 'discontinued' },
  ];
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);

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

  const handleUploadImages = async () => {
    if (!form.images.length) return [];
    const formData = new FormData();
    form.images.forEach(file => formData.append('files', file));
    const res = await fetch('/api/v1/uploads/product-images', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });
    const data = await res.json();
    return data.image_urls || [];
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const image_urls = await handleUploadImages();
      const payload = {
        ...form,
        price: Number(form.price),
        stock_quantity: Number(form.stock_quantity),
        category_id: Number(form.category_id),
        images: (image_urls as string[]).map((url: string) => ({ url })),
      };
      const res = await fetch('/api/v1/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Failed to create product');
      modal.close();
      resetForm();
      refetchProducts();
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = (products || []).filter(product =>
    (product.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
    ((product.category?.name || '').toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Products Management</h1>
          <p className="text-gray-600 mt-2">Manage your product catalog</p>
        </div>
        <Button color="primary" onPress={modal.open}>
          Add New Product
        </Button>
      </div>

      {/* Modal через Hero UI Card + Tailwind overlay */}
      {modal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/25">
          <Card className="w-full max-w-lg p-6">
            <Form onSubmit={handleSubmit} className="space-y-4">
              <h2 className="text-xl font-bold mb-2">Add New Product</h2>
              <Input label="Name" name="name" value={form.name} onChange={handleInput} required />
              <Input label="Description" name="description" value={form.description} onChange={handleInput} required />
              <Input label="Price" name="price" type="number" value={String(form.price)} onChange={handleInput} required min={0.01} step={0.01} />
              <Input label="Stock Quantity" name="stock_quantity" type="number" value={String(form.stock_quantity)} onChange={handleInput} required min={0} />
              <Select
                label="Availability Type"
                selectedKeys={[form.availability_type]}
                onSelectionChange={keys => handleInput({ target: { name: 'availability_type', value: Array.from(keys)[0] } } as any)}
              >
                <>
                  {availabilityOptions.map(opt => (
                    <SelectItem key={opt.value}>{opt.label}</SelectItem>
                  ))}
                </>
              </Select>
              <Input label="Preorder Available Date" name="preorder_available_date" type="datetime-local" value={form.preorder_available_date} onChange={handleInput} />
              <Select
                label="Category"
                selectedKeys={[form.category_id]}
                onSelectionChange={keys => handleInput({ target: { name: 'category_id', value: Array.from(keys)[0] } } as any)}
                required
              >
                <>
                  <SelectItem key="">Select category</SelectItem>
                  {(categories || []).map(cat => <SelectItem key={String(cat.id)}>{cat.name}</SelectItem>)}
                </>
              </Select>
              <Input label="Images" name="images" type="file" multiple accept="image/*" onChange={handleImageChange} />
              {imagePreviews.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {imagePreviews.map((src, i) => (
                    <img key={i} src={src} alt={`preview-${i}`} className="w-20 h-20 object-cover rounded border" />
                  ))}
                </div>
              )}
              <Switch isSelected={form.is_active} onValueChange={val => handleInput({ target: { name: 'is_active', type: 'checkbox', checked: val } } as any)}>
                Active
              </Switch>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="light" onPress={modal.close}>
                  Cancel
                </Button>
                <Button type="submit" color="primary" isLoading={loading}>
                  Create Product
                </Button>
              </div>
            </Form>
          </Card>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <Input
            placeholder="Search products..."
            value={searchTerm}
            onValueChange={setSearchTerm}
            className="max-w-md"
          />
        </div>

        <Table aria-label="Products table">
          <TableHeader>
            <TableColumn>ID</TableColumn>
            <TableColumn>NAME</TableColumn>
            <TableColumn>PRICE</TableColumn>
            <TableColumn>CATEGORY</TableColumn>
            <TableColumn>STATUS</TableColumn>
            <TableColumn>ACTIONS</TableColumn>
          </TableHeader>
          <TableBody>
            {filteredProducts.map((product) => (
              <TableRow key={product.id}>
                <TableCell>{product.id}</TableCell>
                <TableCell>{product.name}</TableCell>
                <TableCell>${product.price}</TableCell>
                <TableCell>{product.category?.name || '-'}</TableCell>
                <TableCell>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    product.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {product.is_active ? 'Active' : 'Inactive'}
                  </span>
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button size="sm" variant="bordered">
                      Edit
                    </Button>
                    <Button size="sm" color="danger" variant="bordered">
                      Delete
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
