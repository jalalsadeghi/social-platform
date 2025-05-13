// src/components/products/ProductDialog.tsx
import React, { useState, useEffect } from "react";
import { useProducts } from "@/hooks/useProducts";
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

interface Props {
  productId?: string;
  initialData?: {
    title: string;
    product_url?: string;
    description?: string;
    ai_content?: string;
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
    media: [] as File[],
  });

  const [urlError, setUrlError] = useState(false);

  useEffect(() => {
    if (initialData) setFormData((prev) => ({ ...prev, ...initialData }));
  }, [initialData]);

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const url = e.target.value;
  setFormData((prev) => ({ ...prev, product_url: url }));

  if (url.length > 0 && !isValidUrl(url)) {
    setUrlError(true);
  } else {
    setUrlError(false);
  }
};

const handleSubmit = () => {
  if (formData.product_url && !isValidUrl(formData.product_url)) {
    setUrlError(true);
    return;
  }

  const productData = {
    ...formData,
    media: [],
  };

  productId
    ? updateMutation.mutate({ id: productId, data: productData })
    : createMutation.mutate(productData);

  onClose();
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

        <Input
          value={formData.product_url}
          onChange={handleUrlChange}
          placeholder="Product URL (optional)"
          className={urlError ? "border-2 border-red-500 focus-visible:ring-0 focus-visible:ring-offset-0" : ""}
        />


        <Input
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Title"
        />

        <Textarea
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          placeholder="Description"
        />

        <Textarea
          value={formData.ai_content}
          onChange={(e) =>
            setFormData({ ...formData, ai_content: e.target.value })
          }
          placeholder="AI Content"
        />

        <ProductMediaUploader
          onFilesSelected={(files) =>
            setFormData({ ...formData, media: files })
          }
        />

        <Button onClick={handleSubmit} disabled={isAddButtonDisabled}>
          {productId ? "Save Changes" : "Add"}
        </Button>
      </DialogContent>
    </Dialog>
  );
};
