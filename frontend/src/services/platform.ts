// src/services/platform.ts
import api from "@/services/api";

export interface Platform {
  id: string;
  user_id: string;
  platform: "instagram" | "youtube" | "tiktok";
  username: string;
  language: "English" | "German" | "Persian";
  posts_per_day: number;
  password?: string;
  cookies?: string;
  is_oauth: boolean;
  created_at: string;
  updated_at: string;
}

export interface PlatformCreate {
  platform: "instagram" | "youtube" | "tiktok";
  username: string;
  password: string;
  language: "English" | "German" | "Persian";
  posts_per_day: number;
  cookies?: string;
}

// export interface PlatformUpdate {
//   platform?: "instagram" | "youtube" | "tiktok";
//   password?: string;
//   language?: "English" | "German" | "Persian";
//   posts_per_day?: number;
//   cookies?: string;
// }

export interface PlatformUpdate extends Partial<PlatformCreate> {}

export const getPlatforms = async (skip = 0, limit = 100): Promise<Platform[]> => {
  const response = await api.get(`/platforms?skip=${skip}&limit=${limit}`);
  // console.log("getPlatforms response:", response.data);
  return response.data;
};

export const getPlatform = async (id: string): Promise<Platform> => {
  const response = await api.get(`/platforms/${id}`);
  // console.log(`getPlatform (${id}) response:`, response.data);
  return response.data;
};

export const createPlatform = async (data: PlatformCreate): Promise<Platform> => {
  // console.log("createPlatform data:", data);
  const response = await api.post(`/platforms`, data);
  // console.log("createPlatform response:", response.data);
  return response.data;
};

export const updatePlatform = async (id: string, data: PlatformUpdate): Promise<Platform> => {
  // console.log(`updatePlatform (${id}) data:`, data);
  const response = await api.put(`/platforms/${id}`, data);
  // console.log(`updatePlatform (${id}) response:`, response.data);
  return response.data;
};

export const deletePlatform = async (id: string): Promise<void> => {
  // console.log(`deletePlatform (${id}) called`);
  await api.delete(`/platforms/${id}`);
  // // console.log(`deletePlatform (${id}) completed`);
};
