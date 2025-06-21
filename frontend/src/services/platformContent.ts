// src/services/platformContent.ts
import api from "@/services/api";

export interface PlatformContent {
  id: string;
  content_id: string;
  title: string;
  video_filename: string;
  thumb_filename: string;
  status: string;
  priority: number;
  send_time?: string;
}

export interface UpdatePriority {
  content_platform_id: string;
  priority: number;
}

// Fetch contents by platform ID with pagination
export const getPlatformContents = async (
  platformId: string,
  skip = 0,
  limit = 50
): Promise<PlatformContent[]> => {
  const response = await api.get(
    `/contents/platform/${platformId}/contents?skip=${skip}&limit=${limit}`
  );
  console.log("/contents/platform/:", response.data);
  return response.data;
};

// Delete a specific content from a platform
export const deletePlatformContent = async (
  contentPlatformId: string
): Promise<{ detail: string }> => {
  const response = await api.delete(
    `/contents/content_platform/${contentPlatformId}`
  );
  return response.data;
};

export const updateContentPriorities = async (
  priorities: UpdatePriority[]
): Promise<{ detail: string }> => {
  const response = await api.put("/contents/priority/update", {
    priorities,
  });
  return response.data;
};
