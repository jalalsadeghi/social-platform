// src/services/product.ts
import api from "@/services/api";

export interface Product {
  id: string;
  product_url?: string;
  title: string;
  description?: string;
  ai_content?: string;
  status: string;
  priority: number;
  scheduled_time?: string;
  created_at: string;
  updated_at: string;
  media: {
    id: string;
    media_url: string;
    media_type: 'image' | 'video';
    created_at: string;
  }[];
  instagram_stats?: {
    views: number;
    likes: number;
    comments: number;
    last_checked_at: string;
  };
}

export interface ProductCreate {
  product_url?: string;
  title: string;
  description?: string;
  ai_content?: string;
  media: { media_url: string; media_type: 'image' | 'video' }[];
}

export interface ProductUpdate extends Partial<ProductCreate> {}

export const getProducts = async (skip = 0, limit = 30): Promise<Product[]> => {
  const response = await api.get(`/products?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const createProduct = async (product: ProductCreate): Promise<Product> => {
  const response = await api.post("/products", product);
  return response.data;
};

export const updateProduct = async (id: string, product: ProductUpdate): Promise<Product> => {
  const response = await api.put(`/products/${id}`, product);
  return response.data;
};

export const deleteProduct = async (id: string): Promise<void> => {
  await api.delete(`/products/${id}`);
};
