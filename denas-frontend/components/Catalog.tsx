"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Spinner } from "@heroui/spinner";
import { Divider } from "@heroui/divider";

import { useAuth } from "@/hooks/useAuth";
import { useFavorites } from "@/hooks/useFavorites";
import { useProducts } from "@/hooks/useProducts";
import { useCategories } from "@/hooks/useCategories";
import { Category, ProductCatalog, ProductFilters } from "@/types";

// Skeleton Card Component
const ProductSkeleton = () => (
  <Card className="animate-pulse">
    <CardBody className="p-0">
      {/* Image Skeleton */}
      <div className="w-full h-48 bg-gray-300 rounded-t-lg" />

      {/* Content Skeleton */}
      <div className="p-4 space-y-3">
        <div className="h-4 bg-gray-300 rounded w-3/4" />
        <div className="h-4 bg-gray-300 rounded w-1/2" />
        <div className="flex justify-between items-center">
          <div className="h-6 bg-gray-300 rounded w-20" />
          <div className="h-5 bg-gray-300 rounded w-16" />
        </div>
      </div>
    </CardBody>
  </Card>
);

// Favorite Button Component
const FavoriteButton = ({
  productId,
  isAuthenticated,
  initialIsFavorited = false,
  className = "",
}: {
  productId: number;
  isAuthenticated: boolean;
  initialIsFavorited?: boolean;
  className?: string;
}) => {
  const { toggleFavorite } = useFavorites();
  const [isFavorited, setIsFavorited] = useState(initialIsFavorited);
  const [isLoading, setIsLoading] = useState(false);

  // Update state when initial value changes (e.g., when products refresh)
  useEffect(() => {
    setIsFavorited(initialIsFavorited);
  }, [initialIsFavorited]);

  const handleToggleFavorite = async () => {
    // Button press event doesn't need to stop propagation

    if (!isAuthenticated) {
      // Could show login modal or redirect to login
      console.log("User must be logged in to favorite products");

      return;
    }

    setIsLoading(true);
    try {
      const newFavoriteState = await toggleFavorite(productId);

      setIsFavorited(newFavoriteState);
    } catch (error) {
      console.error("Failed to toggle favorite:", error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div
        aria-disabled="true"
        aria-label="Login to add favorites"
        className={`absolute top-2 right-2 z-10 w-8 h-8 rounded-md bg-white/60 backdrop-blur-sm opacity-50 cursor-not-allowed flex items-center justify-center ${className}`}
        role="button"
        title="Login to add favorites"
      >
        <svg
          className="w-4 h-4 text-gray-300"
          fill="none"
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
      </div>
    );
  }

  return (
    <div
      aria-label={isFavorited ? "Remove from favorites" : "Add to favorites"}
      className={`absolute top-2 right-2 z-10 w-8 h-8 rounded-md bg-white/80 backdrop-blur-sm hover:bg-white/90 cursor-pointer flex items-center justify-center transition-all duration-200 ${
        isLoading ? "opacity-70 cursor-not-allowed" : "hover:scale-105"
      } ${className}`}
      role="button"
      tabIndex={0}
      onClick={(e) => {
        e.stopPropagation();
        if (!isLoading) handleToggleFavorite();
      }}
      onKeyDown={(e) => {
        if ((e.key === "Enter" || e.key === " ") && !isLoading) {
          e.preventDefault();
          e.stopPropagation();
          handleToggleFavorite();
        }
      }}
    >
      {isLoading ? (
        <Spinner size="sm" />
      ) : (
        <svg
          className={`w-4 h-4 transition-all duration-200 ${
            isFavorited
              ? "text-red-500 fill-current scale-110"
              : "text-gray-400 hover:text-red-400 hover:scale-105"
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
    </div>
  );
};

// Product Image Component with Loading State
const ProductImage = ({
  src,
  alt,
  className,
}: {
  src?: string;
  alt: string;
  className?: string;
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Handle case when there's no image src - immediately set loading to false
  useEffect(() => {
    if (!src || src.trim() === "") {
      setIsLoading(false);
      console.log(
        `ProductImage: No src provided for ${alt}, setting loading to false`,
      );
    } else {
      setIsLoading(true);
      setHasError(false);
      console.log(`ProductImage: Starting to load image for ${alt}: ${src}`);

      // Set a timeout to prevent infinite loading (10 seconds)
      timeoutRef.current = setTimeout(() => {
        console.warn(`ProductImage: Timeout loading image for ${alt}: ${src}`);
        setIsLoading(false);
        setHasError(true);
      }, 10000);
    }

    // Cleanup timeout on unmount or src change
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [src, alt]);

  const handleLoad = () => {
    console.log(`ProductImage: Successfully loaded image for ${alt}`);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsLoading(false);
  };

  const handleError = () => {
    console.warn(`ProductImage: Failed to load image for ${alt}: ${src}`);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsLoading(false);
    setHasError(true);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Loading Skeleton */}
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded-t-lg flex items-center justify-center">
          <div className="w-8 h-8">
            <Spinner size="sm" />
          </div>
        </div>
      )}

      {/* Actual Image */}
      {src && src.trim() && !hasError ? (
        <img
          alt={alt}
          className={`w-full h-full object-cover rounded-t-lg transition-opacity duration-300 ${
            isLoading ? "opacity-0" : "opacity-100"
          }`}
          src={src}
          onError={handleError}
          onLoad={handleLoad}
        />
      ) : (
        <div
          className={`w-full h-full bg-gray-100 rounded-t-lg flex items-center justify-center transition-opacity duration-300 ${
            isLoading ? "opacity-0" : "opacity-100"
          }`}
        >
          <div className="text-4xl">📦</div>
        </div>
      )}
    </div>
  );
};

export default function Catalog() {
  const router = useRouter();
  const {
    categories,
    loading: categoriesLoading,
    error: categoriesError,
    fetchCategories,
  } = useCategories();
  const { fetchProductsCatalog, loading: productsLoading } = useProducts();
  const { user } = useAuth();

  // State management
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(
    null,
  );
  const [products, setProducts] = useState<ProductCatalog[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Debounce refs
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const priceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Intersection observer ref for infinite scroll
  const observerRef = useRef<HTMLDivElement | null>(null);

  // Load initial data
  useEffect(() => {
    fetchCategories();
    loadProducts(true); // Initial load
  }, []);

  // Load products with current filters
  const loadProducts = useCallback(
    async (reset: boolean = false) => {
      if (!reset && isLoadingMore) return;

      try {
        if (reset) {
          setIsTransitioning(true);
        } else {
          setIsLoadingMore(true);
        }

        const filters: ProductFilters = {
          page: reset ? 1 : currentPage,
          size: 20,
        };

        if (selectedCategory) {
          filters.category_id = selectedCategory.id;
        }
        if (searchTerm.trim()) {
          filters.search = searchTerm.trim();
        }
        if (minPrice && parseFloat(minPrice) > 0) {
          filters.min_price = parseFloat(minPrice);
        }
        if (maxPrice && parseFloat(maxPrice) > 0) {
          filters.max_price = parseFloat(maxPrice);
        }

        const response = await fetchProductsCatalog(filters);

        // Add a small delay for smoother transition when resetting
        if (reset) {
          await new Promise((resolve) => setTimeout(resolve, 200));
        }

        if (reset) {
          setProducts(response.items);
          setCurrentPage(2);
        } else {
          setProducts((prev) => [...prev, ...response.items]);
          setCurrentPage((prev) => prev + 1);
        }

        setHasMore(response.has_next || false);
      } catch (error) {
        console.error("Failed to load products:", error);
      } finally {
        setIsLoadingMore(false);
        setIsTransitioning(false);
      }
    },
    [
      selectedCategory,
      searchTerm,
      minPrice,
      maxPrice,
      currentPage,
      isLoadingMore,
      fetchProductsCatalog,
    ],
  );

  // Debounced search
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(() => {
      loadProducts(true);
    }, 500);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchTerm]);

  // Debounced price filters
  useEffect(() => {
    if (priceTimeoutRef.current) {
      clearTimeout(priceTimeoutRef.current);
    }

    priceTimeoutRef.current = setTimeout(() => {
      loadProducts(true);
    }, 800);

    return () => {
      if (priceTimeoutRef.current) {
        clearTimeout(priceTimeoutRef.current);
      }
    };
  }, [minPrice, maxPrice]);

  // Category change
  useEffect(() => {
    loadProducts(true);
  }, [selectedCategory]);

  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (
          entries[0].isIntersecting &&
          hasMore &&
          !isLoadingMore &&
          !productsLoading
        ) {
          loadProducts(false);
        }
      },
      { threshold: 0.1 },
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => {
      if (observerRef.current) {
        observer.unobserve(observerRef.current);
      }
    };
  }, [hasMore, isLoadingMore, productsLoading, loadProducts]);

  const handleCategorySelect = (category: Category | null) => {
    setSelectedCategory(category);
  };

  const clearFilters = () => {
    setSearchTerm("");
    setMinPrice("");
    setMaxPrice("");
    setSelectedCategory(null);
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters Header */}
      <Card>
        <CardBody className="p-4">
          <div className="flex flex-col lg:flex-row gap-4 items-end">
            <div className="flex-1">
              <Input
                label="Search Products"
                placeholder="Search for products..."
                startContent={
                  isTransitioning ? (
                    <Spinner size="sm" />
                  ) : (
                    <svg
                      className="w-4 h-4 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                      />
                    </svg>
                  )
                }
                value={searchTerm}
                variant="bordered"
                onValueChange={setSearchTerm}
              />
            </div>
            <div className="flex gap-2">
              <Input
                className="w-32"
                label="Min Price"
                min="0"
                placeholder="0"
                startContent={<span className="text-gray-400">$</span>}
                step="0.01"
                type="number"
                value={minPrice}
                variant="bordered"
                onValueChange={setMinPrice}
              />
              <Input
                className="w-32"
                label="Max Price"
                min="0"
                placeholder="∞"
                startContent={<span className="text-gray-400">$</span>}
                step="0.01"
                type="number"
                value={maxPrice}
                variant="bordered"
                onValueChange={setMaxPrice}
              />
            </div>
            <Button className="h-10" variant="bordered" onPress={clearFilters}>
              Clear Filters
            </Button>
          </div>
        </CardBody>
      </Card>

      <div className="flex gap-6 min-h-[600px]">
        {/* Left Sidebar - Categories */}
        <div className="w-64 flex-shrink-0">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <h3 className="text-lg font-semibold text-gray-900">
                Categories
              </h3>
            </CardHeader>
            <Divider />
            <CardBody className="pt-3">
              {categoriesLoading ? (
                <div className="flex flex-col items-center py-8">
                  <Spinner size="sm" />
                  <p className="text-sm text-gray-500 mt-2">
                    Loading categories...
                  </p>
                </div>
              ) : categoriesError ? (
                <div className="text-center py-8">
                  <p className="text-sm text-red-500 mb-3">{categoriesError}</p>
                  <Button
                    size="sm"
                    variant="bordered"
                    onPress={() => fetchCategories()}
                  >
                    Retry
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  {/* All Categories Option */}
                  <Button
                    className="w-full justify-start"
                    color={selectedCategory === null ? "primary" : "default"}
                    size="sm"
                    variant={selectedCategory === null ? "solid" : "light"}
                    onPress={() => handleCategorySelect(null)}
                  >
                    All Categories
                  </Button>

                  {/* Individual Categories */}
                  {categories.length > 0 ? (
                    categories.map((category) => (
                      <Button
                        key={category.id}
                        className="w-full justify-start"
                        color={
                          selectedCategory?.id === category.id
                            ? "primary"
                            : "default"
                        }
                        size="sm"
                        variant={
                          selectedCategory?.id === category.id
                            ? "solid"
                            : "light"
                        }
                        onPress={() => handleCategorySelect(category)}
                      >
                        {category.name}
                      </Button>
                    ))
                  ) : (
                    <div className="text-center py-4">
                      <p className="text-sm text-gray-500">
                        No categories available
                      </p>
                    </div>
                  )}
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Right Side - Products */}
        <div className="flex-1">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-center w-full">
                <h3 className="text-lg font-semibold text-gray-900">
                  {selectedCategory ? selectedCategory.name : "All Products"}
                </h3>
                <div className="text-sm text-gray-500">
                  {products.length} product{products.length !== 1 ? "s" : ""}
                </div>
              </div>
            </CardHeader>
            <Divider />
            <CardBody className="pt-6">
              {/* Products Grid */}
              <div className="space-y-6">
                {/* Products Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {/* Show skeleton cards while loading initial products or transitioning */}
                  {(productsLoading && products.length === 0) ||
                  isTransitioning ? (
                    Array.from({ length: 8 }).map((_, index) => (
                      <ProductSkeleton key={`skeleton-${index}`} />
                    ))
                  ) : products.length === 0 ? (
                    // No products found state
                    <div className="col-span-full text-center py-16">
                      <div className="text-6xl mb-4">🔍</div>
                      <h4 className="text-xl font-semibold text-gray-900 mb-2">
                        No Products Found
                      </h4>
                      <p className="text-gray-600 mb-6">
                        {searchTerm || minPrice || maxPrice || selectedCategory
                          ? "Try adjusting your search criteria or filters."
                          : "No products are available at the moment."}
                      </p>
                      {(searchTerm ||
                        minPrice ||
                        maxPrice ||
                        selectedCategory) && (
                        <Button color="primary" onPress={clearFilters}>
                          Clear All Filters
                        </Button>
                      )}
                    </div>
                  ) : (
                    // Actual products with staggered animation
                    products.map((product, index) => (
                      <Card
                        key={product.id}
                        isPressable
                        className="cursor-pointer hover:shadow-lg transition-all duration-300 hover:scale-105 animate-in fade-in-0 slide-in-from-bottom-4 group"
                        style={{
                          animationDelay: `${Math.min(index * 50, 400)}ms`,
                          animationDuration: "600ms",
                          animationFillMode: "both",
                        }}
                        onPress={() =>
                          router.push(`/client/product/${product.id}`)
                        }
                      >
                        <CardBody className="p-0">
                          {/* Product Image with Favorite Button */}
                          <div className="relative">
                            <ProductImage
                              alt={product.name}
                              className="w-full h-48"
                              src={product.image_url}
                            />
                            {/* Favorite Button */}
                            <FavoriteButton
                              initialIsFavorited={product.is_favorited || false}
                              isAuthenticated={!!user}
                              productId={product.id}
                            />
                          </div>

                          {/* Product Info */}
                          <div className="p-4">
                            <h4 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                              {product.name}
                            </h4>
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-xl font-bold text-green-600">
                                $
                                {parseFloat(product.price.toString()).toFixed(
                                  2,
                                )}
                              </span>
                              <span
                                className={`text-xs px-2 py-1 rounded-full transition-colors ${
                                  product.availability_type === "IN_STOCK"
                                    ? "bg-green-100 text-green-800"
                                    : "bg-yellow-100 text-yellow-800"
                                }`}
                              >
                                {product.availability_type?.replace("_", " ") ||
                                  "IN STOCK"}
                              </span>
                            </div>
                            <div className="text-xs text-gray-500 opacity-70 group-hover:opacity-100 transition-opacity">
                              Click to view details
                            </div>
                          </div>
                        </CardBody>
                      </Card>
                    ))
                  )}

                  {/* Loading more skeleton cards during infinite scroll */}
                  {isLoadingMore &&
                    products.length > 0 &&
                    Array.from({ length: 4 }).map((_, index) => (
                      <ProductSkeleton key={`loading-skeleton-${index}`} />
                    ))}
                </div>

                {/* Infinite Scroll Loading Indicator */}
                {hasMore && !isLoadingMore && products.length > 0 && (
                  <div ref={observerRef} className="flex justify-center py-8">
                    <div className="text-gray-400 text-sm animate-pulse">
                      Scroll down for more products
                    </div>
                  </div>
                )}

                {/* End of catalog indicator */}
                {!hasMore && products.length > 0 && (
                  <div className="flex justify-center py-8">
                    <div className="text-center">
                      <div className="text-2xl mb-2">🎉</div>
                      <div className="text-gray-500 text-sm">
                        You ve seen all {products.length} products
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
