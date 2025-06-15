// src/hooks/useContent.ts
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  scrapeContent,
  createContent,
  getContents,
  getContentById,
  updateContent,
  deleteContent,
  getMusicFiles,
  getCurrentVideoProgress, 
} from "@/services/content";
import type {
  ContentCreate,
  ContentScraperRequest,
  ContentUpdate,
  Content,
  MusicFile,
} from "@/services/content";
// import { getCurrentVideoProgress } from "@/services/content";

import { toast } from "sonner";

export const useContent = () => {
  const queryClient = useQueryClient();

  // Scrape Mutation
  const scrapeMutation = useMutation({
    mutationFn: (data: ContentScraperRequest) => scrapeContent(data),
    onSuccess: () => toast.success("Scraping completed successfully."),
    onError: () => toast.error("Scraping failed."),
  });

  // Create Mutation
  const createMutation = useMutation({
    mutationFn: (data: ContentCreate) => createContent(data),
    onSuccess: (data) => { // داده‌های پاسخ را می‌توانید لاگ کنید و مطمئن شوید کامل است
      console.log("Mutation success data:", data);
      queryClient.invalidateQueries({ queryKey: ["contents"] });
      toast.success("Content created successfully.");
    },
    onError: (error) => {
      console.error("Create content mutation error:", error);
      toast.error("Failed to create content.");
    },
  });

  // Update Mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ContentUpdate }) =>
      updateContent(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contents"] });
      toast.success("Content updated successfully.");
    },
    onError: () => toast.error("Failed to update content."),
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteContent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contents"] });
      toast.success("Content deleted successfully.");
    },
    onError: () => toast.error("Failed to delete content."),
  });

  return {
    scrapeMutation,
    createMutation,
    updateMutation,
    deleteMutation,
  };
};

// Get Contents List (Infinite Query)
export const useContents = () => {
  return useInfiniteQuery<Content[], Error>({
    queryKey: ["contents"],
    queryFn: ({ pageParam = 0 }) => getContents(pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) =>
      lastPage.length === 30 ? allPages.length * 30 : undefined,
  });
};

// Get Single Content by ID
export const useContentById = (id: string) => {
  return useQuery<Content, Error>({
    queryKey: ["content", id],
    queryFn: () => getContentById(id),
    enabled: !!id,
  });
};

// Get user's music files
export const useMusicFiles = () => {
  return useQuery<MusicFile[], Error>({
    queryKey: ["musicFiles"],
    queryFn: () => getMusicFiles(),
  });
};

export const useCurrentVideoProgress = () => {
  return useQuery<{ progress: number | string }, Error>({
    queryKey: ["currentVideoProgress"],
    queryFn: getCurrentVideoProgress,
    refetchInterval: 5000, // هر 5 ثانیه وضعیت به‌روز شود
  });
};