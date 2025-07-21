"use client";

import React, { useState, useEffect } from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@heroui/modal";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Select, SelectItem } from "@heroui/select";
import { Switch } from "@heroui/switch";

import { useForm } from "@/hooks/useForm";
import { useProducts } from "@/hooks/useProducts";
import { useCategories } from "@/hooks/useCategories";
import { AvailabilityType } from "@/types";
import { api } from "@/lib/api";

interface CreateProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function CreateProductModal({
  isOpen,
  onClose,
  onSuccess,
}: CreateProductModalProps) {
  const { createProduct, loading } = useProducts();
  const { categories = [], fetchCategories } = useCategories();

  const { form, setForm, handleInput, resetForm } = useForm({
    name: "",
    description: "",
    price: 1,
    stock_quantity: 0,
    availability_type: "IN_STOCK",
    preorder_day: "",
    preorder_month: "",
    preorder_year: "",
    is_active: true,
    category_id: "",
  });

  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const availabilityOptions = [
    { label: "In Stock", value: "IN_STOCK" },
    { label: "Pre-order", value: "PRE_ORDER" },
  ];

  // Generate days (1-31)
  const dayOptions = Array.from({ length: 31 }, (_, i) => ({
    label: String(i + 1),
    value: String(i + 1),
  }));

  // Generate months
  const monthOptions = [
    { label: "January", value: "1" },
    { label: "February", value: "2" },
    { label: "March", value: "3" },
    { label: "April", value: "4" },
    { label: "May", value: "5" },
    { label: "June", value: "6" },
    { label: "July", value: "7" },
    { label: "August", value: "8" },
    { label: "September", value: "9" },
    { label: "October", value: "10" },
    { label: "November", value: "11" },
    { label: "December", value: "12" },
  ];

  // Generate years (current year + 5 years forward)
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 6 }, (_, i) => ({
    label: String(currentYear + i),
    value: String(currentYear + i),
  }));

  useEffect(() => {
    fetchCategories();
  }, []);

  const validateAndAddImages = (files: File[]) => {
    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    const maxSize = 10 * 1024 * 1024; // 10MB

    const validFiles = files.filter((file) => {
      if (!allowedTypes.includes(file.type)) {
        alert(
          `File ${file.name} is not a valid image type. Only JPEG, PNG, and WebP are allowed.`,
        );

        return false;
      }
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);

        return false;
      }

      return true;
    });

    if (validFiles.length === 0) return;

    // Check total count after adding new files
    const totalAfterAdding = selectedImages.length + validFiles.length;

    if (totalAfterAdding > 5) {
      const canAdd = 5 - selectedImages.length;

      if (canAdd > 0) {
        alert(
          `You can only add ${canAdd} more images. Total limit is 5 images.`,
        );
        validFiles.splice(canAdd);
      } else {
        alert("Maximum 5 images allowed. Please remove some images first.");

        return;
      }
    }

    // Add new files to existing ones
    const newImages = [...selectedImages, ...validFiles];

    setSelectedImages(newImages);

    // Generate previews for new files and add to existing previews
    Promise.all(
      validFiles.map((file) => {
        return new Promise<string>((resolve) => {
          const reader = new FileReader();

          reader.onload = (ev) => resolve(ev.target?.result as string);
          reader.readAsDataURL(file);
        });
      }),
    ).then((newPreviews) => {
      setImagePreviews((prev) => [...prev, ...newPreviews]);
    });
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);

      validateAndAddImages(files);
      // Reset input value to allow same files to be selected again
      e.target.value = "";
    }
  };

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files);

      validateAndAddImages(files);
    }
  };

  const removeImage = (index: number) => {
    const newImages = selectedImages.filter((_, i) => i !== index);
    const newPreviews = imagePreviews.filter((_, i) => i !== index);

    setSelectedImages(newImages);
    setImagePreviews(newPreviews);
  };

  const downloadImage = (index: number) => {
    const file = selectedImages[index];
    const url = URL.createObjectURL(file);
    const a = document.createElement("a");

    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const clearAllImages = () => {
    if (
      selectedImages.length > 0 &&
      confirm("Are you sure you want to remove all images?")
    ) {
      setSelectedImages([]);
      setImagePreviews([]);
    }
  };

  const uploadImagesToSupabase = async (files: File[]): Promise<string[]> => {
    if (files.length === 0) return [];

    setUploadingImages(true);
    try {
      const response = await api.uploadProductImages(files);

      return response.image_urls;
    } catch (error) {
      console.error("Failed to upload images:", error);
      throw error;
    } finally {
      setUploadingImages(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Upload images first if any selected
      let imageUrls: string[] = [];

      if (selectedImages.length > 0) {
        imageUrls = await uploadImagesToSupabase(selectedImages);
      }

      // Form date from separate fields
      const preorderDate =
        form.preorder_day && form.preorder_month && form.preorder_year
          ? `${form.preorder_year}-${form.preorder_month.padStart(2, "0")}-${form.preorder_day.padStart(2, "0")}`
          : undefined;

      const submitData = {
        name: form.name,
        description: form.description,
        price: parseFloat(String(form.price)),
        category_id: parseInt(form.category_id) || 0,
        stock_quantity: parseInt(String(form.stock_quantity)) || 0,
        availability_type: form.availability_type as AvailabilityType,
        preorder_available_date: preorderDate,
        is_active: form.is_active,
        image_urls: imageUrls, // Send URLs instead of File objects
      };

      await createProduct(submitData);
      handleClose();
      onSuccess?.();
    } catch (error) {
      console.error("Failed to create product:", error);
      alert("Failed to create product. Please try again.");
    }
  };

  const handleClose = () => {
    resetForm();
    setSelectedImages([]);
    setImagePreviews([]);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      scrollBehavior="inside"
      size="2xl"
      onClose={handleClose}
    >
      <ModalContent>
        <form onSubmit={handleSubmit}>
          <ModalHeader>Add New Product</ModalHeader>

          <ModalBody>
            <div className="space-y-4">
              <Input
                isRequired
                label="Product Name"
                name="name"
                value={form.name}
                onChange={handleInput}
              />

              <Input
                label="Description"
                name="description"
                value={form.description}
                onChange={handleInput}
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  isRequired
                  label="Price"
                  min={0.01}
                  name="price"
                  startContent="$"
                  step={0.01}
                  type="number"
                  value={String(form.price)}
                  onChange={handleInput}
                />

                <Input
                  isRequired
                  label="Stock Quantity"
                  min={0}
                  name="stock_quantity"
                  type="number"
                  value={String(form.stock_quantity)}
                  onChange={handleInput}
                />
              </div>

              <Select
                label="Availability Type"
                name="availability_type"
                selectedKeys={[form.availability_type]}
                onSelectionChange={(keys) =>
                  handleInput({
                    target: {
                      name: "availability_type",
                      value: Array.from(keys)[0],
                    },
                  } as any)
                }
              >
                {availabilityOptions.map((opt) => (
                  <SelectItem key={opt.value}>{opt.label}</SelectItem>
                ))}
              </Select>

              {/* Only show preorder date when PRE_ORDER is selected */}
              {form.availability_type === "PRE_ORDER" && (
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Preorder Available Date
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    <Select
                      placeholder="Day"
                      selectedKeys={[form.preorder_day]}
                      size="sm"
                      onSelectionChange={(keys) =>
                        handleInput({
                          target: {
                            name: "preorder_day",
                            value: Array.from(keys)[0],
                          },
                        } as any)
                      }
                    >
                      {dayOptions.map((opt) => (
                        <SelectItem key={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </Select>

                    <Select
                      placeholder="Month"
                      selectedKeys={[form.preorder_month]}
                      size="sm"
                      onSelectionChange={(keys) =>
                        handleInput({
                          target: {
                            name: "preorder_month",
                            value: Array.from(keys)[0],
                          },
                        } as any)
                      }
                    >
                      {monthOptions.map((opt) => (
                        <SelectItem key={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </Select>

                    <Select
                      placeholder="Year"
                      selectedKeys={[form.preorder_year]}
                      size="sm"
                      onSelectionChange={(keys) =>
                        handleInput({
                          target: {
                            name: "preorder_year",
                            value: Array.from(keys)[0],
                          },
                        } as any)
                      }
                    >
                      {yearOptions.map((opt) => (
                        <SelectItem key={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </Select>
                  </div>
                </div>
              )}

              <Select
                isRequired
                label="Category"
                name="category_id"
                selectedKeys={[form.category_id]}
                onSelectionChange={(keys) =>
                  handleInput({
                    target: { name: "category_id", value: Array.from(keys)[0] },
                  } as any)
                }
              >
                {[
                  <SelectItem key="">Select category</SelectItem>,
                  ...categories.map((cat) => (
                    <SelectItem key={String(cat.id)}>{cat.name}</SelectItem>
                  )),
                ]}
              </Select>

              <div>
                <label className="text-sm font-medium mb-3 block">
                  Product Images ({selectedImages.length}/5)
                </label>

                {/* Drag & Drop Upload Zone */}
                <div
                  className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                    dragActive
                      ? "border-blue-500 bg-blue-50"
                      : selectedImages.length >= 5
                        ? "border-gray-300 bg-gray-50 cursor-not-allowed"
                        : "border-gray-300 hover:border-blue-400 hover:bg-gray-50 cursor-pointer"
                  }`}
                  onClick={() => {
                    if (selectedImages.length < 5) {
                      document.getElementById("image-upload-input")?.click();
                    }
                  }}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <Input
                    multiple
                    accept="image/jpeg,image/png,image/webp"
                    className="hidden"
                    id="image-upload-input"
                    type="file"
                    onChange={handleImageChange}
                  />

                  {dragActive ? (
                    <div className="text-blue-600">
                      <div className="text-3xl mb-2">📎</div>
                      <p className="text-lg font-medium">Drop images here</p>
                    </div>
                  ) : selectedImages.length >= 5 ? (
                    <div className="text-gray-400">
                      <div className="text-3xl mb-2">📸</div>
                      <p className="text-lg font-medium">
                        Maximum 5 images reached
                      </p>
                      <p className="text-sm">Remove some images to add more</p>
                    </div>
                  ) : (
                    <div className="text-gray-600">
                      <div className="text-3xl mb-2">📷</div>
                      <p className="text-lg font-medium">
                        Drag & drop images here or click to browse
                      </p>
                      <p className="text-sm mt-1">
                        Supports JPEG, PNG, WebP • Max 10MB per file • Up to 5
                        images
                      </p>
                      <Button
                        className="mt-3"
                        color="primary"
                        size="sm"
                        variant="flat"
                        onPress={() => {
                          document
                            .getElementById("image-upload-input")
                            ?.click();
                        }}
                      >
                        Choose Files
                      </Button>
                    </div>
                  )}
                </div>
              </div>

              {/* Image Gallery */}
              {selectedImages.length > 0 && (
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <label className="text-sm font-medium">
                      Selected Images ({selectedImages.length})
                    </label>
                    <Button
                      color="danger"
                      size="sm"
                      variant="flat"
                      onPress={clearAllImages}
                    >
                      Clear All
                    </Button>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {imagePreviews.map((src, i) => (
                      <div key={i} className="relative group">
                        <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200">
                          <img
                            alt={`Preview ${i + 1}`}
                            className="w-full h-full object-cover"
                            src={src}
                          />
                        </div>

                        {/* Image Controls Overlay */}
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100">
                          <div className="flex gap-2">
                            <Button
                              className="min-w-0 w-10 h-10 p-0"
                              color="primary"
                              size="sm"
                              title="Download image"
                              variant="solid"
                              onPress={() => downloadImage(i)}
                            >
                              <svg
                                className="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                />
                              </svg>
                            </Button>
                            <Button
                              className="min-w-0 w-10 h-10 p-0"
                              color="danger"
                              size="sm"
                              title="Remove image"
                              variant="solid"
                              onPress={() => removeImage(i)}
                            >
                              <svg
                                className="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                />
                              </svg>
                            </Button>
                          </div>
                        </div>

                        {/* Image Info */}
                        <div className="mt-2 px-1">
                          <p
                            className="text-xs text-gray-600 truncate"
                            title={selectedImages[i]?.name}
                          >
                            {selectedImages[i]?.name}
                          </p>
                          <p className="text-xs text-gray-400">
                            {(selectedImages[i]?.size / 1024 / 1024).toFixed(2)}{" "}
                            MB
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <Switch
                isSelected={form.is_active}
                onValueChange={(val) =>
                  handleInput({
                    target: {
                      name: "is_active",
                      type: "checkbox",
                      checked: val,
                    },
                  } as any)
                }
              >
                Active Product
              </Switch>
            </div>
          </ModalBody>

          <ModalFooter>
            <Button variant="flat" onPress={handleClose}>
              Cancel
            </Button>
            <Button
              color="primary"
              isDisabled={uploadingImages}
              isLoading={loading || uploadingImages}
              type="submit"
            >
              {uploadingImages ? "Uploading Images..." : "Create Product"}
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
}
