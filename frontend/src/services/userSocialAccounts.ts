// src/services/userSocialAccounts.ts
import api from "@/services/api";

export interface SocialAccount {
  id: string;
  platform: string;
  account_identifier: string;
  lang: string;
  created_at: string;
  updated_at: string;
}

export const getUserSocialAccounts = async (): Promise<SocialAccount[]> => {
  const response = await api.get("/users/user/social-accounts");
  return response.data;
};