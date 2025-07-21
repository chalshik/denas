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
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from '@heroui/table';
import { useForm } from '@/hooks/useForm';
import { useCategories } from '@/hooks/useCategories';
import { Category, CategoryWithMetadata } from '@/types';

interface CategoryManagementModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function CategoryManagementModal({ 
  isOpen, 
  onClose,
  onSuccess
}: CategoryManagementModalProps) {
  const { 
    loading, 
    fetchCategoriesWithMetadata, 
    createCategory, 
    deleteCategory 
  } = useCategories();
  
  const [categories, setCategories] = useState<CategoryWithMetadata[]>([]);
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set());
  const [creating, setCreating] = useState(false);
  
  const { form, handleInput, resetForm } = useForm({
    name: '',
  });

  // Fetch categories when modal opens
  useEffect(() => {
    if (isOpen) {
      loadCategories();
    }
  }, [isOpen]);

  const loadCategories = async () => {
    try {
      const categoriesWithMetadata = await fetchCategoriesWithMetadata();
      setCategories(categoriesWithMetadata);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const handleCreateCategory = async () => {
    if (!form.name.trim()) {
      return;
    }

    setCreating(true);
    try {
      await createCategory({
        name: form.name.trim(),
      });
      resetForm();
      await loadCategories(); // Refresh the list
      onSuccess?.();
    } catch (error) {
      console.error('Failed to create category:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteCategory = async (categoryId: number, categoryName: string, canDelete: boolean) => {
    if (!canDelete) {
      return; // Should not be called for non-deletable categories
    }

    if (window.confirm(`Are you sure you want to delete the category "${categoryName}"? This action cannot be undone.`)) {
      setDeletingIds(prev => new Set(prev).add(categoryId));
      try {
        await deleteCategory(categoryId);
        await loadCategories(); // Refresh the list
        onSuccess?.();
      } catch (error) {
        console.error('Failed to delete category:', error);
        // Show user-friendly error message
        alert(error instanceof Error ? error.message : 'Failed to delete category');
      } finally {
        setDeletingIds(prev => {
          const newSet = new Set(prev);
          newSet.delete(categoryId);
          return newSet;
        });
      }
    }
  };

  const handleClose = () => {
    resetForm();
    setDeletingIds(new Set());
    onClose();
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose}
      size="3xl"
      scrollBehavior="inside"
      placement="center"
    >
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h2 className="text-xl font-semibold">Manage Categories</h2>
          <p className="text-sm text-gray-500">Add new categories or remove existing ones</p>
        </ModalHeader>
        
        <ModalBody className="py-6">
          {/* Add New Category Section */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Category</h3>
            <div className="space-y-4">
              <Input
                label="Category Name"
                placeholder="Enter category name"
                name="name"
                value={form.name}
                onChange={handleInput}
                variant="bordered"
                isRequired
              />
              <Button
                color="primary"
                onPress={handleCreateCategory}
                isLoading={creating}
                isDisabled={!form.name.trim() || creating}
                className="w-full"
              >
                {creating ? 'Creating...' : 'Add Category'}
              </Button>
            </div>
          </div>

          {/* Existing Categories Section */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Existing Categories</h3>
            
            {loading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="mt-2 text-gray-500">Loading categories...</p>
              </div>
            ) : categories.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No categories found. Create your first category above.</p>
              </div>
            ) : (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <Table 
                  aria-label="Categories table"
                  removeWrapper
                  classNames={{
                    th: "bg-gray-100 text-left text-xs font-medium text-gray-700 uppercase tracking-wider px-4 py-3 border-b border-gray-200",
                    td: "px-4 py-3 text-sm text-gray-900 border-b border-gray-100",
                    tbody: "bg-white"
                  }}
                >
                  <TableHeader>
                    <TableColumn>Name</TableColumn>
                    <TableColumn>Products</TableColumn>
                    <TableColumn width={100}>Actions</TableColumn>
                  </TableHeader>
                  <TableBody>
                    {categories.map((category: CategoryWithMetadata) => (
                      <TableRow key={category.id}>
                        <TableCell>
                          <div className="font-medium text-gray-900">
                            {category.name}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-gray-600">
                            {category.product_count !== undefined ? 
                              `${category.product_count} product${category.product_count !== 1 ? 's' : ''}` : 
                              '-'
                            }
                            {!category.can_delete && category.product_count && category.product_count > 0 && (
                              <div className="text-xs text-amber-600 mt-1">
                                Cannot delete - has products
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            color="danger"
                            variant="flat"
                            onPress={() => handleDeleteCategory(category.id, category.name, category.can_delete)}
                            isLoading={deletingIds.has(category.id)}
                            isDisabled={deletingIds.has(category.id) || !category.can_delete}
                            title={!category.can_delete ? 'Cannot delete category with products' : 'Delete category'}
                          >
                            {deletingIds.has(category.id) ? 'Deleting...' : 'Delete'}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        </ModalBody>
        
        <ModalFooter>
          <Button 
            color="default" 
            variant="flat" 
            onPress={handleClose}
          >
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
} 