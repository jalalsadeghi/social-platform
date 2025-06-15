// src/components/content/ContentDialog.tsx
import React, { useState, useEffect } from "react";
import { useContent, useMusicFiles  } from "@/hooks/useContents";
import { usePrompts } from "@/hooks/usePrompts";
import { usePlatform } from "@/hooks/usePlatform";
import { uploadFile } from "@/services/upload";
import api from "@/services/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

interface Props {
  open: boolean;
  onClose: () => void;
  initialData?: any;
}

export const ContentDialog: React.FC<Props> = ({ open, onClose, initialData }) => {
  const { scrapeMutation, createMutation, updateMutation } = useContent();
  const { promptsQuery } = usePrompts();
  const { platformsQuery } = usePlatform();
  const { data: musicFiles = [] } = useMusicFiles();

  const prompts = promptsQuery.data?.pages.flat() || [];
  const platforms = platformsQuery.data?.pages.flat() || [];

  const [selectedPrompt, setSelectedPrompt] = useState(initialData?.prompt_id || "");
  const [url, setUrl] = useState(initialData?.content_url || "");
  const [tip, setTip] = useState("");
  const [removeAudio, setRemoveAudio] = useState<boolean>(initialData?.remove_audio ?? false);
  const [selectedMusicId, setSelectedMusicId] = useState<string | null>(initialData?.music_id || null);
  const [priorityZero, setPriorityZero] = useState<boolean>(false);

  const [scrapedData, setScrapedData] = useState({
    ai_title: initialData?.ai_title || "",
    ai_caption: initialData?.ai_caption || "",
    ai_content: initialData?.ai_content || "",
    video_filename: initialData?.video_filename || "",
    thumb_filename: initialData?.thumb_filename || "",
  });

  // const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(initialData?.platforms_id || []);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(
    initialData?.platforms_status?.map((ps: { platform_id: string }) => ps.platform_id) || []
  );
  const [thumbnail, setThumbnail] = useState<File | null>(null);
  const [thumbnailPreview, setThumbnailPreview] = useState(
    initialData ? `${api.defaults.baseURL}/${initialData.thumb_filename}` : ""
  );

  const handleScrape = async () => {
    if (!selectedPrompt || !url) {
      toast.error("Prompt and URL are required.");
      return;
    }

    scrapeMutation.mutate(
      { url, prompt_id: selectedPrompt, tip },
      {
        onSuccess: (data) => {
          setScrapedData(data);
          setThumbnailPreview(`${api.defaults.baseURL}/${data.thumb_filename}`);
        },
      }
    );
  };

  const handleThumbnailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setThumbnail(file);
      setThumbnailPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async () => {
    let finalThumb = scrapedData.thumb_filename;

    if (thumbnail) {
      const uploadRes = await uploadFile(thumbnail);
      finalThumb = uploadRes.local_path;
    }

    const payload = {
      ai_title: scrapedData.ai_title,
      ai_caption: scrapedData.ai_caption,
      ai_content: scrapedData.ai_content,
      platforms_id: selectedPlatforms,
      content_url: url,
      video_filename: scrapedData.video_filename,
      thumb_filename: finalThumb,
      remove_audio: removeAudio,
      music_id: selectedMusicId,
      priority_zero: priorityZero,
    };

    if (initialData?.id) {
      updateMutation.mutate({ id: initialData.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }

    onClose();
  };

  const shouldShowScrapeButton = !scrapedData.ai_title && !initialData;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-h-[90vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>{initialData ? "Edit Content" : "Add New Content"}</DialogTitle>
        </DialogHeader>

        {!initialData && !scrapedData.ai_title && (
          <>
            <Select value={selectedPrompt} onValueChange={setSelectedPrompt}>
              <SelectTrigger>
                <SelectValue placeholder="Select a prompt" />
              </SelectTrigger>
              <SelectContent>
                {prompts.map((prompt) => (
                  <SelectItem key={prompt.id} value={prompt.id}>{prompt.prompt_name}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Input placeholder="URL" value={url} onChange={(e) => setUrl(e.target.value)} />

            <Textarea placeholder="Tip (optional)" value={tip} onChange={(e) => setTip(e.target.value)} />
          </>
        )}

        {shouldShowScrapeButton && (
          <Button onClick={handleScrape} disabled={scrapeMutation.isPending}>
            {scrapeMutation.isPending ? "Scraping..." : "Scrape"}
          </Button>
        )}

        {(scrapedData.ai_title || initialData) && (
          <>
            <Input
              value={scrapedData.ai_title}
              onChange={(e) => setScrapedData(prev => ({ ...prev, ai_title: e.target.value }))}
              placeholder="AI Title"
            />
            <Textarea
              value={scrapedData.ai_caption}
              onChange={(e) => setScrapedData(prev => ({ ...prev, ai_caption: e.target.value }))}
              placeholder="AI Caption"
            />
            <Textarea
              value={scrapedData.ai_content}
              onChange={(e) => setScrapedData(prev => ({ ...prev, ai_content: e.target.value }))}
              placeholder="AI Content"
            />

            <div>
              <Label>Select Platforms:</Label>
              {platforms.map((platform) => (
                <div key={platform.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={platform.id}
                    checked={selectedPlatforms.includes(platform.id)}
                    onCheckedChange={(checked) => {
                      setSelectedPlatforms(prev =>
                        checked ? [...prev, platform.id] : prev.filter(id => id !== platform.id)
                      );
                    }}
                  />
                  <Label htmlFor={platform.id}>
                    {platform.username} ({platform.platform})
                  </Label>
                </div>
              ))}
            </div>

            {!initialData && (
            <div className="flex items-center space-x-2 mt-4">
              <Checkbox
                id="priority-zero"
                checked={priorityZero}
                onCheckedChange={(checked) => setPriorityZero(!!checked)}
              />
              <Label htmlFor="priority-zero">Set Priority of Platforms to Zero</Label>
            </div>
            )}

            {/* <div className="mt-4"> */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="remove-audio"
                checked={removeAudio}
                onCheckedChange={(checked) => setRemoveAudio(!!checked)}
              />
              <Label htmlFor="remove-audio">Remove Audio from Video</Label>
            </div>

            <div className="mt-4">
              <Label htmlFor="music-select">Select Music:</Label>
              <Select
                value={selectedMusicId || "none"}
                onValueChange={(value) => setSelectedMusicId(value !== "none" ? value : null)}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select a music file (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {musicFiles.map((music) => (
                    <SelectItem key={music.id} value={music.id}>
                      {music.original_name || music.filename}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {/* </div> */}

            <input type="file" accept="image/*" onChange={handleThumbnailChange} />
            {thumbnailPreview && (
              <img
                src={thumbnailPreview}
                alt="Thumbnail"
                className="w-32 cursor-pointer"
                onClick={() => window.open(`${api.defaults.baseURL}/${scrapedData.video_filename}`)}
              />
            )}

            <Button onClick={handleSubmit}>
              {initialData ? "Update" : "Add"}
            </Button>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};
