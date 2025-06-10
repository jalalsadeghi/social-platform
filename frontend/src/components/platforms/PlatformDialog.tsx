// src/components/platforms/PlatformDialog.tsx
import React, { useState, useEffect } from "react";
import { usePlatform } from "@/hooks/usePlatform";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";

interface Props {
  platformId?: string;
  initialData?: {
    platform: "instagram" | "youtube" | "tiktok";
    username?: string;
    cookies?: string;
  };
  open: boolean;
  onClose: () => void;
}

export const PlatformDialog: React.FC<Props> = ({ platformId, initialData, open, onClose }) => {
  const { createMutation, updateMutation } = usePlatform();

  const [formData, setFormData] = useState({
    platform: "instagram",
    username: "",
    password: "",
    cookies: "",
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        platform: initialData.platform,
        username: initialData.username || "",
        password: "",
        cookies: initialData.cookies || "",
      });
    }
  }, [initialData]);

  const resetForm = () => {
    setFormData({
      platform: "instagram",
      username: "",
      password: "",
      cookies: "",
    });
  };

  const handleSubmit = async () => {
    if (!platformId && (!formData.username || !formData.password)) {
      toast.error("Username and Password are required.");
      return;
    }

    if (platformId) {
      updateMutation.mutate({
        id: platformId,
        data: {
          platform: formData.platform,
          password: formData.password || undefined,
          cookies: formData.cookies,
        },
      });
    } else {
      createMutation.mutate(formData);
    }

    onClose();
    resetForm();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="space-y-4 max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>{platformId ? "Edit Platform" : "Add New Platform"}</DialogTitle>
        </DialogHeader>

        <Select
          value={formData.platform}
          onValueChange={(value) => setFormData({ ...formData, platform: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select Platform" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="instagram">Instagram</SelectItem>
            <SelectItem value="youtube">YouTube</SelectItem>
            <SelectItem value="tiktok">TikTok</SelectItem>
          </SelectContent>
        </Select>

        {!platformId && (
          <Input
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            placeholder="Username"
          />
        )}

        <Input
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          placeholder={platformId ? "New Password (leave blank to keep current)" : "Password"}
        />

        <Textarea
          value={formData.cookies}
          onChange={(e) => setFormData({ ...formData, cookies: e.target.value })}
          placeholder="Cookies (optional)"
        />

        <Button onClick={handleSubmit}>
          {platformId ? "Save Changes" : "Add"}
        </Button>
      </DialogContent>
    </Dialog>
  );
};