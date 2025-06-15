// src/services/content.ts
import api from "@/services/api";

export interface ContentScraperRequest {
  url: string;
  prompt_id: string;
  tip?: string;
}

export interface ContentScraperResponse {
  ai_title: string;
  ai_caption: string;
  ai_content: string;
  video_filename: string;
  thumb_filename: string;
}

export interface ContentPlatformStatus {
  platform_id: string;
  platform_name?: string; 
  status: string; 
  priority: number;
}

export interface ContentCreate {
  ai_title: string;
  ai_caption: string;
  ai_content: string;
  platforms_id: string[];
  content_url: string;
  video_filename: string;
  thumb_filename: string;
  remove_audio?: boolean;
  music_id?: string | null;
}

export interface ContentUpdate extends Partial<ContentCreate> {}

export interface Content {
  id: string;
  user_id: string;
  user_name?: string;
  ai_title: string;
  ai_caption: string;
  ai_content: string;
  content_url: string;
  video_filename: string;
  thumb_filename: string;
  remove_audio: boolean;
  music_id?: string | null;
  status: string;
  platforms_status: ContentPlatformStatus[];
  scheduled_time?: string;
  created_at: string;
  updated_at: string;
}

export interface MusicFile {
  id: string;
  filename: string;
  original_name?: string;
  created_at: string;
}

// Scrape content from provided URL
export const scrapeContent = async (data: ContentScraperRequest): Promise<ContentScraperResponse> => {
  const response = await api.post("/contents/scrape/", data);
  return response.data;
};

// Create new content
export const createContent = async (data: ContentCreate): Promise<Content> => {
  try {
    const response = await api.post("/contents/", data);
    console.log("CreateContent response:", response.data); // برای بررسی پاسخ دقیق سرور
    return response.data;
  } catch (error) {
    console.error("CreateContent error detail:", error);
    throw error;
  }
};

// Fetch contents (list with pagination)
export const getContents = async (skip = 0, limit = 30): Promise<Content[]> => {
  const response = await api.get(`/contents?skip=${skip}&limit=${limit}`);
  
  return response.data;
};

// Fetch single content by ID
export const getContentById = async (id: string): Promise<Content> => {
  const response = await api.get(`/contents/${id}`);
  return response.data;
};

// Update content by ID
export const updateContent = async (id: string, data: ContentUpdate): Promise<Content> => {
  const response = await api.put(`/contents/${id}`, data);
  return response.data;
};

// Delete content by ID
export const deleteContent = async (id: string): Promise<{ detail: string }> => {
  const response = await api.delete(`/contents/${id}`);
  return response.data;
};

// Get user's music files
export const getMusicFiles = async (skip = 0, limit = 30): Promise<MusicFile[]> => {
  const response = await api.get(`/contents/music/?skip=${skip}&limit=${limit}`);
  return response.data;
};

// Current progress video
export const getCurrentVideoProgress = async (): Promise<{ progress: number | string }> => {
  const response = await api.get(`/contents/status/progress`);
  return response.data;
};