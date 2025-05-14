// src/components/products/ProductMediaUploader.tsx
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

interface Media {
  id?: string;
  media_url: string;
  media_type: "image" | "video";
}

interface Props {
  existingMedia?: Media[];
  onFilesSelected: (files: File[]) => void;
  onRemoveExisting?: (url: string) => void;
}

export const ProductMediaUploader: React.FC<Props> = ({
  existingMedia = [],
  onFilesSelected,
  onRemoveExisting,
}) => {
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    onFilesSelected(files);
    setPreviewUrls(files.map((file) => URL.createObjectURL(file)));
  };

  useEffect(() => {
    // Clean up memory leaks
    return () => previewUrls.forEach(URL.revokeObjectURL);
  }, [previewUrls]);

  return (
    <div className="space-y-4">
      <input
        type="file"
        multiple
        accept="image/*,video/*"
        onChange={handleFileChange}
        className="hidden"
        id="media-upload"
      />
      <Button asChild>
        <label htmlFor="media-upload">Browse Media</label>
      </Button>

      <div className="flex gap-2 flex-wrap">
        {existingMedia.map((media) => (
          <div key={media.media_url} className="relative">
            {media.media_type === "video" ? (
              <video src={media.media_url} className="h-20 w-auto" controls />
            ) : (
              <img src={media.media_url} className="h-20 w-auto" />
            )}
            <button
              type="button"
              className="absolute top-0 right-0 bg-red-500 text-white rounded-full w-5 h-5 xdelete"
              onClick={() => onRemoveExisting?.(media.media_url)}
            >
              &times;
            </button>
          </div>
        ))}

        {previewUrls.map((url) => (
          <img key={url} src={url} className="h-20 w-auto opacity-70" />
        ))}
      </div>
    </div>
  );
};
