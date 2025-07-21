"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Card, CardBody } from "@heroui/card";
import { Button } from "@heroui/button";
import { Spinner } from "@heroui/spinner";
import { Divider } from "@heroui/divider";
import { Chip } from "@heroui/chip";

import { useAuth } from "@/hooks/useAuth";
import { useFavorites } from "@/hooks/useFavorites";
import { useProducts } from "@/hooks/useProducts";
import { ProductWithDetails } from "@/types";

export default function ProductDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const productId = parseInt(params.id as string);

  const { getProductDetails, loading } = useProducts();
  const { toggleFavorite, checkIsFavorited } = useFavorites();
  const { user } = useAuth();

  const [product, setProduct] = useState<ProductWithDetails | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPhoneNumber, setShowPhoneNumber] = useState(false);

  useEffect(() => {
    const loadProduct = async () => {
      try {
        const productData = await getProductDetails(productId);

        setProduct(productData);

        // Check if favorited
        if (user) {
          const favoriteStatus = await checkIsFavorited(productId);

          setIsFavorited(favoriteStatus.is_favorited);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load product");
      }
    };

    if (productId) {
      loadProduct();
    }
  }, [productId]);

  const handleFavoriteToggle = async () => {
    if (!user) {
      // Could show login modal
      return;
    }

    setFavoriteLoading(true);
    try {
      const newFavoriteState = await toggleFavorite(productId);

      setIsFavorited(newFavoriteState);
    } catch (error) {
      console.error("Failed to toggle favorite:", error);
    } finally {
      setFavoriteLoading(false);
    }
  };

  const handleAddToCart = () => {
    // TODO: Implement add to cart functionality
    console.log("Add to cart:", productId);
  };

  const handleBuyNow = () => {
    setShowPhoneNumber(true);
  };

  const handleCopyPhoneNumber = () => {
    navigator.clipboard.writeText("0773160307");
    // You might want to show a toast notification here
    alert("Phone number copied to clipboard!");
  };

  if (loading || !product) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Spinner size="lg" />
            <p className="mt-4 text-gray-600">Loading product details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-6xl mb-4">😕</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Product Not Found
          </h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Button
            color="primary"
            onPress={() => router.push("/client/catalog")}
          >
            Back to Catalog
          </Button>
        </div>
      </div>
    );
  }

  const availabilityColor =
    product.availability_type === "IN_STOCK"
      ? "success"
      : product.availability_type === "PRE_ORDER"
        ? "warning"
        : "default";

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Back Button */}
      <div className="mb-6">
        <Button
          startContent={
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M15 19l-7-7 7-7"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
              />
            </svg>
          }
          variant="light"
          onPress={() => router.push("/client/catalog")}
        >
          Back to Catalog
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Product Images */}
        <div className="space-y-4">
          {/* Main Image */}
          <Card className="overflow-hidden">
            <CardBody className="p-0">
              <div className="aspect-square bg-gray-100 flex items-center justify-center">
                {product.images && product.images.length > 0 ? (
                  <img
                    alt={product.name}
                    className="w-full h-full object-cover"
                    src={product.images[selectedImageIndex]?.image_url}
                  />
                ) : (
                  <div className="text-8xl">📦</div>
                )}
              </div>
            </CardBody>
          </Card>

          {/* Image Thumbnails */}
          {product.images && product.images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto">
              {product.images.map((image, index) => (
                <Card
                  key={image.id}
                  isPressable
                  className={`flex-shrink-0 cursor-pointer border-2 ${
                    index === selectedImageIndex
                      ? "border-blue-500"
                      : "border-transparent hover:border-gray-300"
                  }`}
                  onPress={() => setSelectedImageIndex(index)}
                >
                  <CardBody className="p-0">
                    <div className="w-20 h-20 bg-gray-100">
                      <img
                        alt={`${product.name} ${index + 1}`}
                        className="w-full h-full object-cover"
                        src={image.image_url}
                      />
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <div className="flex justify-between items-start mb-2">
              <h1 className="text-3xl font-bold text-gray-900">
                {product.name}
              </h1>

              {/* Favorite Button */}
              {user && (
                <Button
                  isIconOnly
                  className="text-2xl"
                  isLoading={favoriteLoading}
                  size="lg"
                  variant="light"
                  onPress={handleFavoriteToggle}
                >
                  {favoriteLoading ? (
                    <Spinner size="sm" />
                  ) : (
                    <svg
                      className={`w-6 h-6 transition-colors ${
                        isFavorited
                          ? "text-red-500 fill-current"
                          : "text-gray-400 hover:text-red-400"
                      }`}
                      fill={isFavorited ? "currentColor" : "none"}
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                      />
                    </svg>
                  )}
                </Button>
              )}
            </div>

            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl font-bold text-green-600">
                ${parseFloat(product.price.toString()).toFixed(2)}
              </span>
              <Chip color={availabilityColor} size="sm" variant="flat">
                {product.availability_type?.replace("_", " ") || "IN STOCK"}
              </Chip>
            </div>

            {product.category && (
              <p className="text-gray-600 mb-4">
                Category:{" "}
                <span className="font-medium">{product.category.name}</span>
              </p>
            )}
          </div>

          <Divider />

          {/* Description */}
          {product.description && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Description
              </h3>
              <p className="text-gray-700 leading-relaxed">
                {product.description}
              </p>
            </div>
          )}

          <Divider />

          {/* Product Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Product Details
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Stock Quantity:</span>
                <span className="font-medium">
                  {product.stock_quantity || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span
                  className={`font-medium ${product.is_active ? "text-green-600" : "text-red-600"}`}
                >
                  {product.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              {product.preorder_available_date && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Available Date:</span>
                  <span className="font-medium">
                    {new Date(
                      product.preorder_available_date,
                    ).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          <Divider />

          {/* Action Buttons */}
          <div className="space-y-3">
            {showPhoneNumber ? (
              <div className="flex items-center gap-2 p-4 bg-blue-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm text-gray-600">
                    Call this number to complete your purchase:
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <a
                      className="text-lg font-semibold hover:underline"
                      href="tel:0773160307"
                    >
                      0773160307
                    </a>
                    <Button
                      size="sm"
                      variant="flat"
                      onPress={handleCopyPhoneNumber}
                    >
                      Copy
                    </Button>
                  </div>
                </div>
                <Button
                  isIconOnly
                  size="sm"
                  variant="light"
                  onPress={() => setShowPhoneNumber(false)}
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      d="M6 18L18 6M6 6l12 12"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                    />
                  </svg>
                </Button>
              </div>
            ) : (
              <Button
                className="w-full"
                color="primary"
                size="lg"
                onPress={handleBuyNow}
              >
                Buy Now
              </Button>
            )}
            <Button
              className="w-full"
              color="primary"
              size="lg"
              variant="bordered"
              onPress={handleAddToCart}
            >
              Add to Cart
            </Button>
          </div>

          {/* Additional Info */}
          {product.availability_type === "PRE_ORDER" && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-medium text-yellow-800 mb-1">
                Pre-Order Information
              </h4>
              <p className="text-sm text-yellow-700">
                This item is available for pre-order.
                {product.preorder_available_date && (
                  <span>
                    {" "}
                    Expected availability:{" "}
                    {new Date(
                      product.preorder_available_date,
                    ).toLocaleDateString()}
                  </span>
                )}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
