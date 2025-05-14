// src/services/upload.ts
import api from "@/services/api";

export const uploadFile = async (file: File): Promise<string> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<{ url: string }>("/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data.url;
};
