// src/hooks/useUserSocialAccounts.ts
import { useQuery } from "@tanstack/react-query";
import { getUserSocialAccounts } from "@/services/userSocialAccounts";
import type { SocialAccount } from "@/services/userSocialAccounts";
import { toast } from "sonner";

export const useUserSocialAccounts = () => {
  const query = useQuery<SocialAccount[], Error>({
    queryKey: ["userSocialAccounts"],
    queryFn: getUserSocialAccounts,
  });

  if (query.isError) {
    toast.error("Failed to load social accounts.");
  }

  return query;
};

