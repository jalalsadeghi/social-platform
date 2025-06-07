// src/hooks/usePrompts.ts
import { useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { InfiniteData } from "@tanstack/react-query";
import {
  getPrompts,
  createPrompt,
  updatePrompt,
  deletePrompt,
} from "@/services/prompt";
import type {
  Prompt,
  PromptCreate,
  PromptUpdate,
} from "@/services/prompt";
import { getLanguages } from "@/services/prompt";
import { getPromptSample } from "@/services/prompt";
import { toast } from "sonner";

import { useQuery } from "@tanstack/react-query";

export const usePrompts = () => {
  const queryClient = useQueryClient();

  const promptsQuery = useInfiniteQuery<Prompt[], Error, InfiniteData<Prompt[]>, ["prompts"], number>({
    queryKey: ["prompts"],
    queryFn: ({ pageParam }: { pageParam: number }) => getPrompts(pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) =>
        lastPage.length === 30 ? allPages.length * 30 : undefined,
  });

  const createMutation = useMutation({
    mutationFn: (data: PromptCreate) => createPrompt(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prompts"] });
      toast.success("Prompt created successfully.");
    },
    onError: () => {
      toast.error("Failed to create prompt.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: PromptUpdate }) =>
      updatePrompt(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prompts"] });
      toast.success("Prompt updated successfully.");
    },
    onError: () => {
      toast.error("Failed to update prompt.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deletePrompt(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prompts"] });
      toast.success("Prompt deleted successfully.");
    },
    onError: () => {
      toast.error("Failed to delete prompt.");
    },
  });

  return {
    promptsQuery,
    createMutation,
    updateMutation,
    deleteMutation,
  };
};

export const useLanguages = () => {
  return useQuery({
    queryKey: ["languages"],
    queryFn: getLanguages,
  });
};

export const usePromptSample = () => {
  return useQuery({
    queryKey: ["prompt_sample"],
    queryFn: getPromptSample,
  });
};
