// src/services/upload.ts
import api from "@/services/api";

export interface UploadedFile {
  url: string;
  local_path: string;
}

export const uploadFile = async (file: File): Promise<UploadedFile> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<UploadedFile>("/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
};