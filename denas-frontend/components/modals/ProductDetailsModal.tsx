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
import { Chip } from "@heroui/chip";
import { Spinner } from "@heroui/spinner";
import { Label } from "@headlessui/react";

import ImageModal from "./ImageModal";

import { useProducts } from "@/hooks/useProducts";
import { useCategories } from "@/hooks/useCategories";
import { useForm } from "@/hooks/useForm";
import { ProductWithDetails, AvailabilityType } from "@/types";
import { api } from "@/lib/api";

interface ProductDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  productId: number | null;
  onSuccess?: () => void;
}

export default function ProductDetailsModal({
  isOpen,
  onClose,
  productId,
  onSuccess,
}: ProductDetailsModalProps) {
  const {
    updateProduct,
    getProductDetails,
    loading: updateLoading,
  } = useProducts();
  const { categories = [], fetchCategories } = useCategories();
  const [product, setProduct] = useState<ProductWithDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [imageFiles, setImageFiles] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [deletedExistingImages, setDeletedExistingImages] = useState<string[]>(
    [],
  );

  const { form, setForm, handleInput, resetForm } = useForm({
    name: "",
    description: "",
    price: 0,
    stock_quantity: 0,
    availability_type: "IN_STOCK", // Use string instead of enum
    preorder_day: "",
    preorder_month: "",
    preorder_year: "",
    is_active: true,
    category_id: 0,
  });

  const availabilityOptions = [
    { label: "In Stock", value: "IN_STOCK" },
    { label: "Pre-order", value: "PRE_ORDER" },
  ];

  // Generate day/month/year options
  const dayOptions = Array.from({ length: 31 }, (_, i) => ({
    label: String(i + 1),
    value: String(i + 1),
  }));

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

  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 6 }, (_, i) => ({
    label: String(currentYear + i),
    value: String(currentYear + i),
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
        description: productDetails.description || "",
        price: productDetails.price,
        stock_quantity: productDetails.stock_quantity || 0,
        availability_type: productDetails.availability_type || "IN_STOCK", // Use string instead of enum
        preorder_day: preorderDate ? String(preorderDate.getDate()) : "",
        preorder_month: preorderDate ? String(preorderDate.getMonth() + 1) : "",
        preorder_year: preorderDate ? String(preorderDate.getFullYear()) : "",
        is_active: productDetails.is_active ?? true,
        category_id: productDetails.category_id,
      });
    } catch (error) {
      console.error("Failed to fetch product details:", error);
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

    // Check total count after adding new files (including existing not deleted)
    const totalAfterAdding = totalCurrentImages + validFiles.length;

    if (totalAfterAdding > 5) {
      const canAdd = 5 - totalCurrentImages;

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
    const newImages = [...imageFiles, ...validFiles];

    setImageFiles(newImages);

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
    const newImages = imageFiles.filter((_, i) => i !== index);
    const newPreviews = imagePreviews.filter((_, i) => i !== index);

    setImageFiles(newImages);
    setImagePreviews(newPreviews);
  };

  const downloadImage = (index: number) => {
    const file = imageFiles[index];
    const url = URL.createObjectURL(file);
    const a = document.createElement("a");

    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const removeExistingImage = (imageUrl: string) => {
    setDeletedExistingImages((prev) => [...prev, imageUrl]);
  };

  const restoreExistingImage = (imageUrl: string) => {
    setDeletedExistingImages((prev) => prev.filter((url) => url !== imageUrl));
  };

  const downloadExistingImage = (imageUrl: string, index: number) => {
    const a = document.createElement("a");

    a.href = imageUrl;
    a.download = `product-image-${index + 1}`;
    a.target = "_blank";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const clearAllImages = () => {
    const hasExisting = product?.images && product.images.length > 0;
    const hasNew = imageFiles.length > 0;

    if (
      (hasExisting || hasNew) &&
      confirm("Are you sure you want to remove all images?")
    ) {
      // Mark all existing images for deletion
      if (product?.images) {
        setDeletedExistingImages(product.images.map((img) => img.image_url));
      }
      // Clear new images
      setImageFiles([]);
      setImagePreviews([]);
      setDragActive(false);
    }
  };

  // Calculate total images (existing not deleted + new)
  const activeExistingImages =
    product?.images?.filter(
      (img) => !deletedExistingImages.includes(img.image_url),
    ) || [];
  const totalCurrentImages = activeExistingImages.length + imageFiles.length;

  // Image modal functions
  const openImageModal = (index: number, type: "existing" | "new") => {
    setCurrentImageIndex(index);
    setViewingImageType(type);
    setImageModalOpen(true);
  };

  const closeImageModal = () => {
    setImageModalOpen(false);
  };

  const goToPreviousImage = () => {
    const totalImages =
      viewingImageType === "existing"
        ? activeExistingImages.length
        : imageFiles.length;

    setCurrentImageIndex((prev) => (prev - 1 + totalImages) % totalImages);
  };

  const goToNextImage = () => {
    const totalImages =
      viewingImageType === "existing"
        ? activeExistingImages.length
        : imageFiles.length;

    setCurrentImageIndex((prev) => (prev + 1) % totalImages);
  };

  // Get current image data for modal
  const getCurrentImageData = () => {
    if (viewingImageType === "existing") {
      const image = activeExistingImages[currentImageIndex];

      return image
        ? {
            url: image.image_url,
            alt: `${product?.name} - Image ${currentImageIndex + 1}`,
            type: image.image_type,
            totalImages: activeExistingImages.length,
          }
        : null;
    } else {
      const preview = imagePreviews[currentImageIndex];
      const file = imageFiles[currentImageIndex];

      return preview && file
        ? {
            url: preview,
            alt: `Preview ${currentImageIndex + 1}`,
            type: "New",
            totalImages: imageFiles.length,
          }
        : null;
    }
  };

  const [uploadingImages, setUploadingImages] = useState(false);

  // Image modal state
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [viewingImageType, setViewingImageType] = useState<"existing" | "new">(
    "existing",
  );

  // Upload images to Supabase and get URLs
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

  const handleSave = async () => {
    if (!product) return;

    try {
      // Form date from separate fields
      const preorderDate =
        form.preorder_day && form.preorder_month && form.preorder_year
          ? `${form.preorder_year}-${form.preorder_month.padStart(2, "0")}-${form.preorder_day.padStart(2, "0")}`
          : undefined;

      // Upload new images first if any selected (like CreateProductModal does)
      let newImageUrls: string[] = [];

      if (imageFiles.length > 0) {
        newImageUrls = await uploadImagesToSupabase(imageFiles);
      }

      // Combine existing images (not deleted) with newly uploaded image URLs
      const existingImageUrls =
        product.images
          ?.filter((img) => !deletedExistingImages.includes(img.image_url))
          .map((img) => img.image_url) || [];

      const allImageUrls = [...existingImageUrls, ...newImageUrls];

      const updateData = {
        name: form.name,
        description: form.description,
        price: parseFloat(String(form.price)),
        category_id: parseInt(String(form.category_id)),
        stock_quantity: parseInt(String(form.stock_quantity)),
        availability_type: form.availability_type as AvailabilityType,
        preorder_available_date: preorderDate,
        is_active: form.is_active,
        // Send only URLs, no raw File objects
        image_urls: allImageUrls,
      };

      await updateProduct(product.id, updateData);
      setIsEditing(false);
      setImageFiles([]); // Clear uploaded files
      setImagePreviews([]); // Clear previews
      setDragActive(false); // Reset drag state
      setDeletedExistingImages([]); // Reset deleted images
      await fetchProductDetails(product.id); // Refresh data
      onSuccess?.(); // Call onSuccess prop
    } catch (error) {
      console.error("Failed to update product:", error);
    }
  };

  const handleClose = () => {
    setProduct(null);
    setIsEditing(false);
    resetForm();
    setImageFiles([]);
    setImagePreviews([]);
    setDragActive(false);
    setDeletedExistingImages([]);
    // Reset image modal state
    setImageModalOpen(false);
    setCurrentImageIndex(0);
    setViewingImageType("existing");
    onClose();
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(price);
  };

  const getAvailabilityColor = (availability: string) => {
    switch (availability) {
      case "IN_STOCK":
        return "success";
      case "PRE_ORDER":
        return "warning";
      default:
        return "default";
    }
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        scrollBehavior="inside"
        size="4xl"
        onClose={handleClose}
      >
        <ModalContent>
          <ModalHeader>
            {loading
              ? "Loading Product..."
              : isEditing
                ? "Edit Product"
                : "Product Details"}
          </ModalHeader>

          <ModalBody>
            {loading ? (
              <div className="flex justify-center py-8">
                <Spinner size="lg" />
              </div>
            ) : product ? (
              <div className="space-y-8">
                {/* Header Section with Title and Quick Actions */}
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 pb-4 border-b border-gray-200">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      {product.name}
                    </h2>
                    <p className="text-lg font-semibold text-green-600 mt-1">
                      {formatPrice(product.price)}
                    </p>
                    <div className="flex flex-wrap gap-2 mt-3">
                      <Chip
                        color={product.is_active ? "success" : "danger"}
                        size="sm"
                        variant="flat"
                      >
                        {product.is_active ? "Active" : "Inactive"}
                      </Chip>
                      <Chip
                        color={getAvailabilityColor(
                          product.availability_type || "IN_STOCK",
                        )}
                        size="sm"
                        variant="flat"
                      >
                        {(product.availability_type || "IN_STOCK").replace(
                          "_",
                          " ",
                        )}
                      </Chip>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500 text-right">
                    <div>Product ID: #{product.id}</div>
                    <div>
                      Created:{" "}
                      {product.created_at
                        ? new Date(product.created_at).toLocaleDateString()
                        : "N/A"}
                    </div>
                  </div>
                </div>

                {/* Unified Product Images Management */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      Product Images
                    </h3>
                    {isEditing && totalCurrentImages > 0 && (
                      <Button
                        color="danger"
                        size="sm"
                        variant="flat"
                        onPress={clearAllImages}
                      >
                        Clear All
                      </Button>
                    )}
                  </div>

                  {/* Upload Zone - Only in Edit Mode */}
                  {isEditing && (
                    <div className="mb-6">
                      <label
                        className="text-sm font-medium mb-3 block"
                        htmlFor="UploadImages"
                      >
                        Upload Images ({totalCurrentImages}/5)
                      </label>

                      <div
                        aria-disabled={totalCurrentImages >= 5}
                        aria-label={
                          totalCurrentImages >= 5
                            ? "Maximum 5 images reached"
                            : "Upload image area, drag and drop or click to browse files"
                        }
                        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                          dragActive
                            ? "border-blue-500 bg-blue-50"
                            : totalCurrentImages >= 5
                              ? "border-gray-300 bg-gray-50 cursor-not-allowed"
                              : "border-gray-300 hover:border-blue-400 hover:bg-gray-50 cursor-pointer"
                        }`}
                        role="button"
                        tabIndex={0}
                        onClick={() => {
                          if (totalCurrentImages < 5) {
                            document
                              .getElementById("edit-image-upload-input")
                              ?.click();
                          }
                        }}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onKeyDown={(e) => {
                          if (
                            (e.key === "Enter" || e.key === " ") &&
                            totalCurrentImages < 5
                          ) {
                            e.preventDefault();
                            document
                              .getElementById("edit-image-upload-input")
                              ?.click();
                          }
                        }}
                      >
                        <Input
                          multiple
                          accept="image/jpeg,image/png,image/webp"
                          className="hidden"
                          id="edit-image-upload-input"
                          type="file"
                          onChange={handleImageChange}
                        />

                        {dragActive ? (
                          <div className="text-blue-600">
                            <div aria-hidden="true" className="text-3xl mb-2">
                              📎
                            </div>
                            <p className="text-lg font-medium">
                              Drop images here
                            </p>
                          </div>
                        ) : totalCurrentImages >= 5 ? (
                          <div className="text-gray-400">
                            <div aria-hidden="true" className="text-3xl mb-2">
                              📸
                            </div>
                            <p className="text-lg font-medium">
                              Maximum 5 images reached
                            </p>
                            <p className="text-sm">
                              Remove some images to add more
                            </p>
                          </div>
                        ) : (
                          <div className="text-gray-600">
                            <div aria-hidden="true" className="text-3xl mb-2">
                              📷
                            </div>
                            <p className="text-lg font-medium">
                              Drag & drop images here or click to browse
                            </p>
                            <p className="text-sm mt-1">
                              Supports JPEG, PNG, WebP • Max 10MB per file • Up
                              to 5 images
                            </p>
                            <Button
                              className="mt-3"
                              color="primary"
                              size="sm"
                              variant="flat"
                              onPress={() => {
                                document
                                  .getElementById("edit-image-upload-input")
                                  ?.click();
                              }}
                            >
                              Choose Files
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Unified Images Gallery */}
                  {(product.images && product.images.length > 0) ||
                  imageFiles.length > 0 ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                      {/* Existing Images */}
                      {product.images?.map((image, index) => (
                        <div
                          key={`existing-${image.id}`}
                          className="relative group"
                        >
                          <button
                            aria-label={`View ${product.name} image ${index + 1}`}
                            className={`w-full aspect-square rounded-lg overflow-hidden border-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                              deletedExistingImages.includes(image.image_url)
                                ? "border-red-300 bg-red-50"
                                : "border-gray-200"
                            }`}
                            type="button"
                            onClick={() => openImageModal(index, "existing")}
                          >
                            <img
                              alt="" // Empty alt as the button has aria-label
                              aria-hidden="true" // Hide from screen readers as button handles the label
                              className={`w-full h-full object-cover transition-all duration-200 ${
                                deletedExistingImages.includes(image.image_url)
                                  ? "opacity-50 grayscale"
                                  : ""
                              }`}
                              src={image.image_url}
                            />
                          </button>

                          {/* Controls Overlay - Only in Edit Mode */}
                          {isEditing && (
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                              {/* Existing Images */}
                              {product.images?.map((image, index) => (
                                <div
                                  key={`existing-${image.id}`}
                                  className="relative group"
                                >
                                  <button
                                    aria-label={`View ${product.name} image ${index + 1}`}
                                    className={`w-full aspect-square rounded-lg overflow-hidden border-2 ${
                                      deletedExistingImages.includes(
                                        image.image_url,
                                      )
                                        ? "border-red-300 bg-red-50"
                                        : "border-gray-200"
                                    }`}
                                    onClick={() =>
                                      openImageModal(index, "existing")
                                    }
                                  >
                                    <img
                                      alt={`${product.name}`}
                                      className={`w-full h-full object-cover transition-all duration-200 ${
                                        deletedExistingImages.includes(
                                          image.image_url,
                                        )
                                          ? "opacity-50 grayscale"
                                          : ""
                                      }`}
                                      src={image.image_url}
                                    />
                                  </button>

                                  {/* Controls Overlay - Only in Edit Mode */}
                                  {isEditing && (
                                    <div
                                      aria-label="Image actions"
                                      className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100"
                                      role="group" // Add role for screen readers
                                    >
                                      <div className="flex gap-2">
                                        {!deletedExistingImages.includes(
                                          image.image_url,
                                        ) && (
                                          <Button
                                            aria-label="Download image"
                                            className="min-w-0 w-10 h-10 p-0"
                                            color="primary"
                                            size="sm"
                                            variant="solid"
                                            onPress={() =>
                                              downloadExistingImage(
                                                image.image_url,
                                                index,
                                              )
                                            }
                                          >
                                            <svg
                                              aria-hidden="true" // Hide from screen readers since button has label
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
                                        )}

                                        {deletedExistingImages.includes(
                                          image.image_url,
                                        ) ? (
                                          <Button
                                            aria-label="Restore image"
                                            className="min-w-0 w-10 h-10 p-0"
                                            color="success"
                                            size="sm"
                                            variant="solid"
                                            onPress={() =>
                                              restoreExistingImage(
                                                image.image_url,
                                              )
                                            }
                                          >
                                            <svg
                                              aria-hidden="true"
                                              className="w-4 h-4"
                                              fill="none"
                                              stroke="currentColor"
                                              viewBox="0 0 24 24"
                                            >
                                              <path
                                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                              />
                                            </svg>
                                          </Button>
                                        ) : (
                                          <Button
                                            aria-label="Remove image"
                                            className="min-w-0 w-10 h-10 p-0"
                                            color="danger"
                                            size="sm"
                                            variant="solid"
                                            onPress={() =>
                                              removeExistingImage(
                                                image.image_url,
                                              )
                                            }
                                          >
                                            <svg
                                              aria-hidden="true"
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
                                        )}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Image Type Badge - Always Show */}
                          <Chip
                            className="absolute top-2 right-2 text-xs"
                            color={
                              deletedExistingImages.includes(image.image_url)
                                ? "danger"
                                : "primary"
                            }
                            size="sm"
                            variant="solid"
                          >
                            {deletedExistingImages.includes(image.image_url)
                              ? "Will Delete"
                              : image.image_type}
                          </Chip>
                        </div>
                      ))}

                      {/* New Images */}
                      {imagePreviews.map((src, i) => (
                        <div key={`new-${i}`} className="relative group">
                          <button
                            aria-label={`View preview image ${i + 1}`}
                            className="aspect-square rounded-lg overflow-hidden border-2 border-blue-200 bg-blue-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                            type="button"
                            onClick={() => openImageModal(i, "new")}
                          >
                            <img
                              alt={`Preview ${i + 1}`}
                              className="w-full h-full object-cover"
                              src={src}
                            />
                          </button>

                          {/* Controls Overlay */}
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

                          {/* New Image Badge */}
                          <Chip
                            className="absolute top-2 right-2 text-xs"
                            color="secondary"
                            size="sm"
                            variant="solid"
                          >
                            New
                          </Chip>

                          {/* File Info */}
                          <div className="absolute bottom-2 left-2 right-2">
                            <div className="bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded truncate">
                              {imageFiles[i]?.name}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-32 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300">
                      <div className="text-center">
                        <svg
                          className="w-12 h-12 text-gray-400 mx-auto mb-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2 2v12a2 2 0 002 2z"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                          />
                        </svg>
                        <p className="text-gray-500">No images available</p>
                        {isEditing && (
                          <p className="text-gray-400 text-sm mt-1">
                            Upload images using the area above
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Product Information */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 text-gray-900">
                    Product Information
                  </h3>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Column */}
                    <div className="space-y-6">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-900 mb-3">
                          Basic Details
                        </h4>
                        <div className="space-y-4">
                          {isEditing ? (
                            <Input
                              isRequired
                              label="Product Name"
                              name="name"
                              value={form.name}
                              variant="bordered"
                              onChange={handleInput}
                            />
                          ) : (
                            <div>
                              <label className="text-sm font-medium text-gray-700">
                                Product Name
                              </label>
                              <p className="text-gray-900 mt-1">
                                {product.name}
                              </p>
                            </div>
                          )}

                          {isEditing ? (
                            <Input
                              label="Description"
                              name="description"
                              value={form.description}
                              variant="bordered"
                              onChange={handleInput}
                            />
                          ) : (
                            <div>
                              <label
                                className="text-sm font-medium text-gray-700"
                                htmlFor="escription"
                              >
                                Description
                              </label>
                              <p className="text-gray-900 mt-1">
                                {product.description ||
                                  "No description available"}
                              </p>
                            </div>
                          )}

                          {isEditing ? (
                            <Input
                              isRequired
                              label="Price"
                              min={0.01}
                              name="price"
                              startContent="$"
                              step={0.01}
                              type="number"
                              value={String(form.price)}
                              variant="bordered"
                              onChange={handleInput}
                            />
                          ) : (
                            <div>
                              <label
                                className="text-sm font-medium text-gray-700"
                                htmlFor="Price "
                              >
                                Price
                              </label>
                              <p className="text-2xl font-bold text-green-600 mt-1">
                                {formatPrice(product.price)}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-900 mb-3">
                          Inventory
                        </h4>
                        <div className="space-y-4">
                          {isEditing ? (
                            <Input
                              label="Stock Quantity"
                              min={0}
                              name="stock_quantity"
                              type="number"
                              value={String(form.stock_quantity)}
                              variant="bordered"
                              onChange={handleInput}
                            />
                          ) : (
                            <div>
                              <label
                                className="text-sm font-medium text-gray-700"
                                htmlFor="stockquantity"
                              >
                                Stock Quantity
                              </label>
                              <p className="text-gray-900 mt-1">
                                {product.stock_quantity || 0} units
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Right Column */}
                    <div className="space-y-6">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-900 mb-3">
                          Category & Availability
                        </h4>
                        <div className="space-y-4">
                          <div>
                            <label
                              className="text-sm font-medium text-gray-700"
                              htmlFor="forcategory"
                            >
                              Category
                            </label>
                            {isEditing ? (
                              <Select
                                isRequired
                                className="mt-1"
                                label="Category"
                                name="category_id"
                                selectedKeys={[String(form.category_id)]}
                                variant="bordered"
                                onSelectionChange={(keys) =>
                                  handleInput({
                                    target: {
                                      name: "category_id",
                                      value: Array.from(keys)[0],
                                    },
                                  } as any)
                                }
                              >
                                {categories.map((cat) => (
                                  <SelectItem key={String(cat.id)}>
                                    {cat.name}
                                  </SelectItem>
                                ))}
                              </Select>
                            ) : (
                              <p className="text-gray-900 mt-1">
                                {product.category?.name ||
                                  `Category ${product.category_id}`}
                              </p>
                            )}
                          </div>

                          <div>
                            <label
                              className="text-sm font-medium text-gray-700"
                              htmlFor="availablity"
                            >
                              Availability
                            </label>
                            {isEditing ? (
                              <Select
                                className="mt-1"
                                label="Availability Type"
                                name="availability_type"
                                selectedKeys={[form.availability_type]}
                                variant="bordered"
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
                                  <SelectItem key={opt.value}>
                                    {opt.label}
                                  </SelectItem>
                                ))}
                              </Select>
                            ) : (
                              <div className="mt-1">
                                <Chip
                                  color={getAvailabilityColor(
                                    product.availability_type || "IN_STOCK",
                                  )}
                                  variant="flat"
                                >
                                  {(
                                    product.availability_type || "IN_STOCK"
                                  ).replace("_", " ")}
                                </Chip>
                              </div>
                            )}
                          </div>

                          {isEditing &&
                            form.availability_type === "PRE_ORDER" && (
                              <div>
                                <label
                                  className="text-sm font-medium text-gray-700 mb-2 block"
                                  htmlFor="available"
                                >
                                  Preorder Available Date
                                </label>
                                <div className="grid grid-cols-3 gap-2">
                                  <Select
                                    placeholder="Day"
                                    selectedKeys={[form.preorder_day]}
                                    size="sm"
                                    variant="bordered"
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
                                      <SelectItem key={opt.value}>
                                        {opt.label}
                                      </SelectItem>
                                    ))}
                                  </Select>

                                  <Select
                                    placeholder="Month"
                                    selectedKeys={[form.preorder_month]}
                                    size="sm"
                                    variant="bordered"
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
                                      <SelectItem key={opt.value}>
                                        {opt.label}
                                      </SelectItem>
                                    ))}
                                  </Select>

                                  <Select
                                    placeholder="Year"
                                    selectedKeys={[form.preorder_year]}
                                    size="sm"
                                    variant="bordered"
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
                                      <SelectItem key={opt.value}>
                                        {opt.label}
                                      </SelectItem>
                                    ))}
                                  </Select>
                                </div>
                              </div>
                            )}

                          {!isEditing &&
                            product.availability_type === "PRE_ORDER" &&
                            product.preorder_available_date && (
                              <div>
                                <label
                                  className="text-sm font-medium text-gray-700"
                                  htmlFor="preorder"
                                >
                                  Preorder Available Date
                                </label>
                                <p className="text-gray-900 mt-1">
                                  {new Date(
                                    product.preorder_available_date,
                                  ).toLocaleDateString()}
                                </p>
                              </div>
                            )}

                          <div>
                            <label
                              className="text-sm font-medium text-gray-700"
                              htmlFor="status"
                            >
                              Status
                            </label>
                            {isEditing ? (
                              <div className="mt-2">
                                <Switch
                                  color="success"
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
                            ) : (
                              <div className="mt-1">
                                <Chip
                                  color={
                                    product.is_active ? "success" : "danger"
                                  }
                                  variant="flat"
                                >
                                  {product.is_active ? "Active" : "Inactive"}
                                </Chip>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <svg
                  className="w-16 h-16 text-gray-400 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                  />
                </svg>
                <p className="text-lg text-gray-500">Product not found</p>
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
                      onPress={() => {
                        setIsEditing(false);
                        setImageFiles([]);
                        setImagePreviews([]);
                        setDragActive(false);
                        setDeletedExistingImages([]);
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      color="primary"
                      isDisabled={uploadingImages}
                      isLoading={updateLoading || uploadingImages}
                      onPress={handleSave}
                    >
                      {uploadingImages ? "Uploading Images..." : "Save Changes"}
                    </Button>
                  </>
                ) : (
                  <Button
                    color="primary"
                    onPress={() => {
                      setIsEditing(true);
                      setImageFiles([]);
                      setImagePreviews([]);
                      setDragActive(false);
                      setDeletedExistingImages([]);
                    }}
                  >
                    Edit Product
                  </Button>
                )}
              </>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Image Viewer Modal */}
      {getCurrentImageData() && (
        <ImageModal
          imageAlt={getCurrentImageData()!.alt}
          imageIndex={currentImageIndex}
          imageType={getCurrentImageData()!.type}
          imageUrl={getCurrentImageData()!.url}
          isOpen={imageModalOpen}
          productName={product?.name}
          totalImages={getCurrentImageData()!.totalImages}
          onClose={closeImageModal}
          onNext={
            getCurrentImageData()!.totalImages > 1 ? goToNextImage : undefined
          }
          onPrevious={
            getCurrentImageData()!.totalImages > 1
              ? goToPreviousImage
              : undefined
          }
        />
      )}
    </>
  );
}
