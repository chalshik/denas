import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { storage } from './firebase';

/**
 * Upload an image to Firebase Storage
 * @param file - The image file to upload
 * @param folder - The folder path (e.g., 'products')
 * @returns Promise<string> - The download URL of the uploaded image
 */
export const uploadImage = async (file: File, folder: string = 'products'): Promise<string> => {
  try {
    // Create a unique filename with timestamp
    const timestamp = Date.now();
    const fileName = `${timestamp}_${file.name}`;
    const filePath = `${folder}/${fileName}`;
    
    // Create a reference to the file location
    const storageRef = ref(storage, filePath);
    
    // Upload the file
    const snapshot = await uploadBytes(storageRef, file);
    
    // Get the download URL
    const downloadURL = await getDownloadURL(snapshot.ref);
    
    return downloadURL;
  } catch (error) {
    console.error('Error uploading image:', error);
    throw new Error('Failed to upload image');
  }
};

/**
 * Validate image file
 * @param file - The file to validate
 * @returns boolean - True if valid image file
 */
export const validateImageFile = (file: File): { isValid: boolean; error?: string } => {
  // Check file type
  if (!file.type.startsWith('image/')) {
    return { isValid: false, error: 'Please select an image file' };
  }
  
  // Check file size (max 5MB)
  const maxSizeInBytes = 5 * 1024 * 1024;
  if (file.size > maxSizeInBytes) {
    return { isValid: false, error: 'Image must be less than 5MB' };
  }
  
  // Check supported formats
  const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  if (!supportedTypes.includes(file.type)) {
    return { isValid: false, error: 'Supported formats: JPEG, PNG, WebP' };
  }
  
  return { isValid: true };
}; 