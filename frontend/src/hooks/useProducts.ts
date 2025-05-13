// src/hooks/useProducts.ts
import { useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { InfiniteData } from "@tanstack/react-query";
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from "@/services/product";
import type {
  Product,
  ProductCreate,
  ProductUpdate,
} from "@/services/product";
import { toast } from "sonner";

export const useProducts = () => {
  const queryClient = useQueryClient();

  const productsQuery = useInfiniteQuery<Product[], Error, InfiniteData<Product[]>, ["products"], number>({
    queryKey: ["products"],
    queryFn: ({ pageParam }: { pageParam: number }) => getProducts(pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) =>
        lastPage.length === 30 ? allPages.length * 30 : undefined,
  });   

  const createMutation = useMutation({
    mutationFn: (data: ProductCreate) => createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      toast.success("Product created successfully.");
    },
    onError: () => {
      toast.error("Failed to create product.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProductUpdate }) =>
      updateProduct(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      toast.success("Product updated successfully.");
    },
    onError: () => {
      toast.error("Failed to update product.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      toast.success("Product deleted successfully.");
    },
    onError: () => {
      toast.error("Failed to delete product.");
    },
  });

  return {
    productsQuery,
    createMutation,
    updateMutation,
    deleteMutation,
  };
};
