// src/components/products/ProductDialog.tsx
import React, { useState, useEffect } from "react";
import { useProducts } from "@/hooks/useProducts";
import { useUserSocialAccounts } from '@/hooks/useUserSocialAccounts';
import { uploadFile } from "@/services/upload";
import { ProductMediaUploader, generateVideoThumbnail,} from "./ProductMediaUploader";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { scrapeProduct } from "@/services/scraping";
import { toast } from "sonner";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
// import { MultiSelector } from '@/components/ui/multi-select';
import { Checkbox } from "@/components/ui/checkbox";

interface Media {
  id?: string;
  media_url: string;
  local_path?: string;
  media_type: "image" | "video";
}

interface Props {
  productId?: string;
  initialData?: {
    title: string;
    product_url?: string;
    description?: string;
    ai_content?: string;
    media?: Media[];
    status?: "pending" | "ready" | "processing" | "posted" | "failed";
    priority?: number;
    scheduled_time?: string;
    social_account_ids?: string[];
  };
  open: boolean;
  onClose: () => void;
}

const isValidUrl = (url: string) => {
  try {
    return Boolean(new URL(url));
  } catch {
    return false;
  }
};

export const ProductDialog: React.FC<Props> = ({
  productId,
  initialData,
  open,
  onClose,
}) => {
  const { createMutation, updateMutation } = useProducts();
  const { data: socialAccounts } = useUserSocialAccounts();
  useEffect(() => {
    console.log('socialAccounts:', socialAccounts);
  }, [socialAccounts]);


  const [formData, setFormData] = useState({
    title: "",
    product_url: "",
    description: "",
    ai_content: "",
  });

  const [existingMedia, setExistingMedia] = useState<Media[]>([]);
  const [newMediaFiles, setNewMediaFiles] = useState<File[]>([]);
  const [urlError, setUrlError] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [priority, setPriority] = useState(0);
  const [scheduledTime, setScheduledTime] = useState<Date | null>(null);
  const [selectedAccounts, setSelectedAccounts] = useState<string[]>([]);



  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title || "",
        product_url: initialData.product_url || "",
        description: initialData.description || "",
        ai_content: initialData.ai_content || "",
      });

      setExistingMedia(initialData.media || []);
      setIsReady(initialData.status === "ready");
      setPriority(initialData.priority || 0);
      setScheduledTime(initialData.scheduled_time ? new Date(initialData.scheduled_time) : null);

      if (initialData.social_account_ids) {
      setSelectedAccounts(initialData.social_account_ids);
      }
    }
  }, [initialData]);

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setFormData((prev) => ({ ...prev, product_url: url }));
    setUrlError(url.length > 0 && !isValidUrl(url));
  };

  const resetForm = () => {
    setFormData({
      title: "",
      product_url: "",
      description: "",
      ai_content: "",
    });
    setExistingMedia([]);
    setNewMediaFiles([]);
    setIsReady(false);
    setPriority(0);
  };

  const handleSubmit = async () => {
    const uploadedMedia = await Promise.all(
      newMediaFiles.map(async (file) => {
        // 1. آپلود فایل اصلی
        const { url, local_path } = await uploadFile(file);

        // اگر ویدئو باشد thumbnail را آپلود می‌کنیم
        if (file.type.startsWith("video")) {
          const thumbnailBlobUrl = await generateVideoThumbnail(file);
          const thumbnailFile = await fetch(thumbnailBlobUrl).then(r => r.blob()).then(blob => new File([blob], "thumbnail.png", { type: "image/png" }));
          const { local_path: thumbnailPath } = await uploadFile(thumbnailFile);

          return {
            media_url: url,               // URL ویدیو
            media_type: "video" as const,
            local_path: thumbnailPath,    // thumbnail URL
          };
        }

        return {
          media_url: url,                     // URL تصویر
          media_type: "image" as const,
          local_path: local_path,
        };
      })
    );

    const updatedPriority = isReady ? 1 : priority;

    const cleanedExistingMedia = existingMedia.map((media) => ({
      media_url: media.media_url,
      media_type: media.media_type,
      local_path: media.local_path,
    }));

    const productData = {
      ...formData,
      media: [...cleanedExistingMedia, ...uploadedMedia],
      status: isReady ? "ready" : "pending",
      priority: updatedPriority,
      scheduled_time: scheduledTime?.toISOString(),
      social_account_ids: selectedAccounts,
    };
    
    console.log("productData:", productData);
    productId
      ? updateMutation.mutate({ id: productId, data: productData })
      : createMutation.mutate(productData);

    onClose();
    resetForm();
  };

  const handleScrape = async () => {
    if (!formData.product_url || !isValidUrl(formData.product_url)) {
      setUrlError(true);
      return;
    }

    setIsScraping(true);
    try {
      const scrapedData = await scrapeProduct(formData.product_url);

      setFormData(prev => ({
        ...prev,
        title: scrapedData.title || prev.title,
        description: scrapedData.description || prev.description,
        ai_content: scrapedData.ai_content || prev.ai_content,
      }));

      const fetchedMediaFiles = await Promise.all(
        scrapedData.media_urls.map(async (url) => {
          const response = await fetch(url);
          const blob = await response.blob();

          const mimeType = blob.type || "image/jpeg"; 
          const filenameExtension = mimeType.split('/')[1] || 'jpg';
          const filename = `image_${Date.now()}.${filenameExtension}`;

          const file = new File([blob], filename, { type: mimeType });
          
          if(!scrapedData.local_path) {
            const { url: uploadedUrl, local_path } = await uploadFile(file);

            return {
              media_url: uploadedUrl,
              media_type: mimeType.startsWith("video") ? "video" as const : "image" as const,
              local_path,
            };
          }else{
            return {
              media_url: url,
              media_type: mimeType.startsWith("video") ? "video" as const : "image" as const,
              local_path: scrapedData.local_path,
            };
          }
        })
      );

      setExistingMedia(prev => [...prev, ...fetchedMediaFiles]);
      toast.success("Scraping completed and media uploaded successfully.");
    } catch (error) {
      toast.error(`Scraping failed: ${error}`);
    } finally {
      setIsScraping(false);
    }
  };

  const handleRemoveExistingMedia = (media_url: string) => {
    setExistingMedia((prev) => prev.filter((media) => media.media_url !== media_url));
  };

  const isAddButtonDisabled = urlError || !formData.title;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="space-y-4 max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>
            {productId ? "Edit Product" : "Add New Product"}
          </DialogTitle>
        </DialogHeader>

        <div className="flex gap-2">
          <Input
            value={formData.product_url}
            onChange={handleUrlChange}
            placeholder="Product URL (optional)"
            className={urlError ? "border-2 border-red-500" : ""}
          />
          {!productId && (
            <Button onClick={handleScrape} disabled={isScraping}>
              {isScraping ? "Scraping..." : "Scrape"}
            </Button>
          )}
        </div>
        <Input
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Title"
        />
        <Textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Description"
        />
        <Textarea
          value={formData.ai_content}
          onChange={(e) => setFormData({ ...formData, ai_content: e.target.value })}
          placeholder="AI Content"
        />

        {/* وضعیت ready */}
        <div className="flex items-center space-x-2">
          <Switch 
            id="status-ready"
            checked={isReady}
            onCheckedChange={(checked) => {
              setIsReady(checked);
              setPriority(checked ? 1 : priority);
              setScheduledTime(checked ? new Date() : null);
            }}
            className="data-[state=checked]:!bg-gray-900 data-[state=unchecked]:!bg-gray-200 w-9 h-6 rounded-full"
          />
          <Label htmlFor="status-ready">Set Status to {isReady ? "Ready" : "Pending"}</Label>
        </div>
        
        {/* {socialAccounts && (
          <MultiSelector
            options={socialAccounts.map(acc => ({
              label: acc.account_identifier,
              value: acc.id,
            }))}
            value={selectedAccounts
              .map(id => socialAccounts.find(acc => acc.id === id))
              .filter(Boolean)
              .map(acc => ({
                label: acc!.account_identifier,
                value: acc!.id,
              }))}
            onChange={(selected) => setSelectedAccounts(selected.map(item => item.value))}
            placeholder="Select Social Accounts"
          />
        )} */}
        <div className="space-y-2">
          <Label className="font-semibold">Select Social Accounts:</Label>
          {socialAccounts?.map((account) => (
            <div key={account.id} className="flex items-center space-x-2">
              <Checkbox
                id={account.id}
                checked={selectedAccounts.includes(account.id)}
                onCheckedChange={(checked) => {
                  setSelectedAccounts((prev) => {
                    if (checked) {
                      return [...prev, account.id];
                    } else {
                      return prev.filter((id) => id !== account.id);
                    }
                  });
                }}
              />
              <Label htmlFor={account.id}>
                {account.account_identifier} ({account.platform})
              </Label>
            </div>
          ))}
        </div>

        <ProductMediaUploader
          existingMedia={existingMedia}
          onRemoveExisting={handleRemoveExistingMedia}
          onFilesSelected={(files) => setNewMediaFiles(files)}
        />

        <Button onClick={handleSubmit} disabled={isAddButtonDisabled}>
          {productId ? "Save Changes" : "Add"}
        </Button>
      </DialogContent>
    </Dialog>
  );
};
