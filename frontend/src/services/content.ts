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

export interface ContentCreate {
  ai_title: string;
  ai_caption: string;
  ai_content: string;
  platforms_id: string[];
  content_url: string;
  video_filename: string;
  thumb_filename: string;
}

export interface ContentUpdate extends Partial<ContentCreate> {}

export interface Content {
  id: string;
  user_id: string;
  ai_title: string;
  ai_caption: string;
  ai_content: string;
  platforms_id: string[];
  content_url: string;
  video_filename: string;
  thumb_filename: string;
  status: string;
  priority: number;
  scheduled_time?: string;
  created_at: string;
  updated_at: string;
}

// Scrape content from provided URL
export const scrapeContent = async (data: ContentScraperRequest): Promise<ContentScraperResponse> => {
  const response = await api.post("/contents/scrape/", data);
  return response.data;
};

// Create new content
export const createContent = async (data: ContentCreate): Promise<Content> => {
  const response = await api.post("/contents/", data);
  return response.data;
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
