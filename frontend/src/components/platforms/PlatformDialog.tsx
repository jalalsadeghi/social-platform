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
    language?: "English" | "German" | "Persian";
    posts_per_day?: number;
    cookies?: string;
    schedule?: Record<string, Record<string, string>>;
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
    language: "English",
    posts_per_day: 0,
    cookies: "",
  });
  const [schedule, setSchedule] = useState<string>("");

  useEffect(() => {
    if (initialData) {
      setFormData({
        platform: initialData.platform,
        username: initialData.username || "",
        password: "",
        language: initialData.language ?? "English",
        posts_per_day: initialData.posts_per_day ?? 0,
        cookies: initialData.cookies ? JSON.stringify(initialData.cookies, null, 2) : "",
      });
      if (initialData.schedule) {
        setSchedule(JSON.stringify(initialData.schedule, null, 2));
      }
    }
  }, [initialData]);

  const resetForm = () => {
    setFormData({
      platform: "instagram",
      username: "",
      password: "",
      language: "",
      posts_per_day: 0,
      cookies: "",
    });
  };

// در handleSubmit:
  const handleSubmit = async () => {
    if (!platformId && (!formData.username || !formData.password)) {
      toast.error("Username and Password are required.");
      return;
    }

    let parsedCookies: Cookie[] | undefined;

    if (formData.cookies) {
      try {
        parsedCookies = JSON.parse(formData.cookies);
        if (!Array.isArray(parsedCookies)) {
          throw new Error();
        }
      } catch {
        toast.error("Invalid cookies format. Please provide valid JSON array.");
        return;
      }
    }

    let scheduleData: Record<string, Record<string, string>> | undefined;

    if (platformId && schedule) {
      try {
        scheduleData = JSON.parse(schedule);
      } catch {
        toast.error("Invalid schedule format. Please provide valid JSON.");
        return;
      }
    }

    const payload = {
      platform: formData.platform,
      username: formData.username,
      password: formData.password || undefined,
      language: formData.language,
      posts_per_day: formData.posts_per_day,
      cookies: parsedCookies,
      schedule: scheduleData,
    };

    if (platformId) {
      updateMutation.mutate({ id: platformId, data: payload });
    } else {
      createMutation.mutate(payload);
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

        <Select
          value={formData.language}
          onValueChange={(value) => setFormData({ ...formData, language: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select Language" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="English">English</SelectItem>
            <SelectItem value="German">German</SelectItem>
            <SelectItem value="Persian">Persian</SelectItem>
          </SelectContent>
        </Select>

        <Input
          type="number"
          value={formData.posts_per_day}
          onChange={(e) => setFormData({ ...formData, posts_per_day: Number(e.target.value) })}
          placeholder="Posts per day"
        />

        {platformId && (
          <>
            <Textarea
              value={schedule}
              onChange={(e) => setSchedule(e.target.value)}
              placeholder={`{
  "Fri": {
    "send01": "06:00",
    "send02": "12:00",
    "send03": "15:00"
  },
  "Mon": {
    "send01": "06:00",
    "send02": "12:00",
    "send03": "15:00"
  }
}`
}
              className="font-mono"
              rows={10}
            />
          </>
        )}

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