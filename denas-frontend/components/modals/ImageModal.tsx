"use client";

import React from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@heroui/modal";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import Image from "next/image";

interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  imageAlt: string;
  imageType?: string;
  productName?: string;
  imageIndex?: number;
  totalImages?: number;
  onPrevious?: () => void;
  onNext?: () => void;
}

export default function ImageModal({
  isOpen,
  onClose,
  imageUrl,
  imageAlt,
  imageType,
  productName,
  imageIndex,
  totalImages,
  onPrevious,
  onNext,
}: ImageModalProps) {
  const downloadImage = () => {
    const a = document.createElement("a");

    a.href = imageUrl;
    a.download = imageAlt.replace(/[^a-z0-9]/gi, "_").toLowerCase() + ".jpg";
    a.target = "_blank";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (!isOpen) return;

    if (e.key === "Escape") {
      onClose();
    } else if (e.key === "ArrowLeft" && onPrevious) {
      onPrevious();
    } else if (e.key === "ArrowRight" && onNext) {
      onNext();
    }
  };

  React.useEffect(() => {
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);

      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, onPrevious, onNext]);

  return (
    <Modal
      classNames={{
        base: "bg-black/90",
        backdrop: "bg-black/50",
      }}
      isOpen={isOpen}
      scrollBehavior="inside"
      size="5xl"
      onClose={onClose}
    >
      <ModalContent className="bg-black text-white">
        <ModalHeader className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">
              {productName ? `${productName} - Image` : "Image Viewer"}
            </h3>
            {totalImages && imageIndex !== undefined && (
              <p className="text-sm text-gray-300">
                {imageIndex + 1} of {totalImages}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            {imageType && (
              <Chip
                className="text-xs"
                color="primary"
                size="sm"
                variant="solid"
              >
                {imageType}
              </Chip>
            )}
          </div>
        </ModalHeader>

        <ModalBody className="flex items-center justify-center p-0 relative">
          {/* Navigation Arrows */}
          {onPrevious && totalImages && totalImages > 1 && (
            <Button
              isIconOnly
              className="absolute left-4 z-10 bg-black/50 backdrop-blur-sm border border-white/20"
              size="lg"
              title="Previous image (←)"
              variant="solid"
              onPress={onPrevious}
            >
              <svg
                className="w-6 h-6"
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
            </Button>
          )}

          {/* Main Image */}
          <div className="w-full h-full flex items-center justify-center min-h-[60vh] max-h-[80vh]">
            <Image
              alt={imageAlt}
              className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
              height={1000}
              src={imageUrl}
              style={{ maxHeight: "80vh" }}
              width={1000}
            />
          </div>

          {onNext && totalImages && totalImages > 1 && (
            <Button
              isIconOnly
              className="absolute right-4 z-10 bg-black/50 backdrop-blur-sm border border-white/20"
              size="lg"
              title="Next image (→)"
              variant="solid"
              onPress={onNext}
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  d="M9 5l7 7-7 7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                />
              </svg>
            </Button>
          )}
        </ModalBody>

        <ModalFooter className="flex justify-between">
          <div className="flex gap-2">
            <Button
              color="primary"
              startContent={
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
              }
              variant="flat"
              onPress={downloadImage}
            >
              Download
            </Button>
          </div>

          <Button variant="flat" onPress={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
