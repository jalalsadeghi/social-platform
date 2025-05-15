// src/components/products/ProductDialog.tsx
import React, { useState, useEffect } from "react";
import { useProducts } from "@/hooks/useProducts";
import { uploadFile } from "@/services/upload";
import { ProductMediaUploader } from "./ProductMediaUploader";
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

interface Media {
  id?: string;
  media_url: string;
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

  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title || "",
        product_url: initialData.product_url || "",
        description: initialData.description || "",
        ai_content: initialData.ai_content || "",
      });

      setExistingMedia(initialData.media || []);
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
  };

  const handleSubmit = async () => {
    if (formData.product_url && !isValidUrl(formData.product_url)) {
      setUrlError(true);
      return;
    }

    const uploadedMedia = await Promise.all(
      newMediaFiles.map(async (file) => {
        const media_url = await uploadFile(file);
        return {
          media_url,
          media_type: file.type.startsWith("video") ? "video" as const : "image" as const,
        };
      })
    );

    const productData = {
      ...formData,
      media: [...existingMedia, ...uploadedMedia],
    };

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

      const fetchedMedia = scrapedData.media_urls.map((url) => ({
        media_url: url,
        media_type: url.match(/\.(mp4|mov)$/i) ? "video" as const : "image" as const,
      }));

      setExistingMedia(prev => [...prev, ...fetchedMedia]);

      toast.success("Scraping completed successfully.");
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
      <DialogContent className="space-y-4">
        <DialogHeader>
          <DialogTitle>
            {productId ? "Edit Product" : "Add New Product"}
          </DialogTitle>
        </DialogHeader>

        {/* <Input
          value={formData.product_url}
          onChange={handleUrlChange}
          placeholder="Product URL (optional)"
          className={urlError ? "border-2 border-red-500" : ""}
        /> */}
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
