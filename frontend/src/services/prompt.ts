// src/services/prompt.ts
import api from "@/services/api";

export interface Prompt {
  id: string;
  user_id: string;
  prompt_name: string;
  prompt_content: string;
  language: string;
  expertise: string;
  promt_type: string;
  created_at: string;
  updated_at: string;
}

export interface PromptCreate {
  prompt_name: string;
  prompt_content: string;
  language: string;
  expertise: string;
  promt_type: string;
}

export interface LanguageOption {
  name: string;
  value: string;
}

export interface PromptSampleOption {
  name: string;
  value: string;
}


export interface PromptUpdate extends Partial<PromptCreate> {}

export const getPrompts = async (skip = 0, limit = 30): Promise<Prompt[]> => {
  const response = await api.get(`/ai-prompts?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const createPrompt = async (prompt: PromptCreate): Promise<Prompt> => {
  const response = await api.post(`/ai-prompts/`, prompt);
  return response.data;
};

export const updatePrompt = async (id: string, prompt: PromptUpdate): Promise<Prompt> => {
  const response = await api.put(`/ai-prompts/${id}/`, prompt);
  return response.data;
};

export const deletePrompt = async (id: string): Promise<void> => {
  await api.delete(`/ai-prompts/${id}/`);
};

export const getLanguages = async (): Promise<LanguageOption[]> => {
  const response = await api.get(`/ai-prompts/language/`);
  return response.data;
};

export const getPromptSample = async (): Promise<PromptSampleOption[]> => {
  const response = await api.get(`/ai-prompts/parompt_sample/`);
  return response.data;
};

