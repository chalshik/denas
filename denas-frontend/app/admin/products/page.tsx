'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from '@heroui/table';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
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

      <Transition appear show={modal.isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={modal.close}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
            leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
                leave="ease-in duration-200" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-lg transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <Dialog.Title as="h2" className="text-xl font-bold mb-2">Add New Product</Dialog.Title>
                    <Input label="Name" name="name" value={form.name} onChange={handleInput} required />
                    <Input label="Description" name="description" value={form.description} onChange={handleInput} required />
                    <Input label="Price" name="price" type="number" value={String(form.price)} onChange={handleInput} required min={0.01} step={0.01} />
                    <Input label="Stock Quantity" name="stock_quantity" type="number" value={String(form.stock_quantity)} onChange={handleInput} required min={0} />
                    <label className="block">Availability Type
                      <select name="availability_type" value={form.availability_type} onChange={handleInput} className="block w-full mt-1 border rounded px-2 py-1">
                        {availabilityOptions.map(opt => (
                          <option key={opt.value} value={opt.value}>{opt.label}</option>
                        ))}
                      </select>
                    </label>
                    <Input label="Preorder Available Date" name="preorder_available_date" type="datetime-local" value={form.preorder_available_date} onChange={handleInput} />
                    <label className="block">Category
                      <select name="category_id" value={form.category_id} onChange={handleInput} className="block w-full mt-1 border rounded px-2 py-1" required>
                        <option value="">Select category</option>
                        {(categories || []).map(cat => <option key={cat.id} value={String(cat.id)}>{cat.name}</option>)}
                      </select>
                    </label>
                    <label className="block">Images
                      <input type="file" name="images" multiple accept="image/*" onChange={handleImageChange} className="block mt-1" />
                      {imagePreviews.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {imagePreviews.map((src, i) => (
                            <img key={i} src={src} alt={`preview-${i}`} className="w-20 h-20 object-cover rounded border" />
                          ))}
                        </div>
                      )}
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleInput} /> Active
                    </label>
                    <Button type="submit" color="primary" isLoading={loading}>
                      Create Product
                    </Button>
                  </form>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>

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
