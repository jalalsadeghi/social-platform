// src/hooks/usePlatformContent.ts
import { useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getPlatformContents,
  deletePlatformContent,
  type PlatformContent,
} from "@/services/platformContent";
import { updateContentPriorities } from "@/services/platformContent";
import type { UpdatePriority } from "@/services/platformContent";
import { toast } from "sonner";

export const usePlatformContent = (platformId: string) => {
  return useInfiniteQuery<PlatformContent[], Error>({
    queryKey: ["platformContents", platformId],
    queryFn: ({ pageParam = 0 }) =>
      getPlatformContents(platformId, pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) =>
      lastPage.length === 30 ? allPages.length * 30 : undefined,
  });
};

export const useDeletePlatformContent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contentPlatformId: string) =>
      deletePlatformContent(contentPlatformId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["platformContents"] });
      toast.success("Content deleted successfully.");
    },
    onError: () => toast.error("Failed to delete content."),
  });
};

export const useUpdateContentPriorities = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (priorities: UpdatePriority[]) => updateContentPriorities(priorities),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["platformContents"] });
      toast.success("Priorities updated successfully.");
    },
    onError: () => {
      toast.error("Failed to update priorities.");
    },
  });
};
