import React, { useState } from "react";
import { Button } from "@/components/ui/button";

interface Props {
  onFilesSelected: (files: File[]) => void;
}

export const ProductMediaUploader: React.FC<Props> = ({ onFilesSelected }) => {
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files ? Array.from(event.target.files) : [];
    onFilesSelected(files);

    const urls = files.map(file => URL.createObjectURL(file));
    setPreviewUrls(urls);
  };

  const removeMedia = (index: number) => {
    setPreviewUrls(urls => urls.filter((_, i) => i !== index));
  };

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
        {previewUrls.map((url, index) => (
          <div key={index} className="relative">
            {url.includes("video") ? (
              <video src={url} className="h-20 w-auto" controls />
            ) : (
              <img src={url} className="h-20 w-auto" alt={`media-${index}`} />
            )}
            <button
              className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-5 h-5 flex justify-center items-center text-xs"
              onClick={() => removeMedia(index)}
            >
              &times;
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
