// src/hooks/usePlatform.ts
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { InfiniteData } from "@tanstack/react-query";
import {
  getPlatforms,
  createPlatform,
  updatePlatform,
  deletePlatform,
  getPlatform
} from "@/services/platform";
import type {
  Platform,
  PlatformCreate,
  PlatformUpdate,
} from "@/services/platform";
import { toast } from "sonner";

export const usePlatform = () => {
  const queryClient = useQueryClient();

  const platformsQuery = useInfiniteQuery<Platform[], Error, InfiniteData<Platform[]>, ["platforms"], number>({
    queryKey: ["platforms"],
    queryFn: async ({ pageParam }: { pageParam: number }) => {
      const data = await getPlatforms(pageParam);
      // console.log("Fetched platforms data:", data);
      return data;
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) =>
        lastPage.length === 100 ? allPages.length * 100 : undefined,
  });

  const createMutation = useMutation({
    mutationFn: (data: PlatformCreate) => createPlatform(data),
    onSuccess: (data) => {
      // console.log("Created platform data:", data);
      queryClient.invalidateQueries({ queryKey: ["platforms"] });
      toast.success("Platform created successfully.");
    },
    onError: (error) => {
      console.error("Failed to create platform:", error);
      toast.error("Failed to create platform.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: PlatformUpdate }) =>
      updatePlatform(id, data),
    onSuccess: (data) => {
      // console.log("Updated platform data:", data);
      queryClient.invalidateQueries({ queryKey: ["platforms"] });
      toast.success("Platform updated successfully.");
    },
    onError: (error) => {
      console.error("Failed to update platform:", error);
      toast.error("Failed to update platform.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deletePlatform(id),
    onSuccess: () => {
      // console.log("Deleted platform with id:", id);
      queryClient.invalidateQueries({ queryKey: ["platforms"] });
      toast.success("Platform deleted successfully.");
    },
    onError: (error) => {
      console.error("Failed to delete platform:", error);
      toast.error("Failed to delete platform.");
    },
  });

  return {
    platformsQuery,
    createMutation,
    updateMutation,
    deleteMutation,
  };
};

export const useSinglePlatform = (id: string) => {
  return useQuery({
    queryKey: ["platform", id],
    queryFn: async () => {
      const data = await getPlatform(id);
      // console.log("Fetched single platform data:", data);
      return data;
    },
    enabled: !!id,
  });
};