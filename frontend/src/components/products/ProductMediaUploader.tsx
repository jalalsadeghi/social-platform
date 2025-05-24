// ProductMediaUploader.tsx
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import api from "@/services/api";

interface Media {
  id?: string;
  media_url: string;
  local_path?: string;
  media_type: "image" | "video";
  thumbnail?: string;
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
  const [previewMedia, setPreviewMedia] = useState<Media[]>([]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    onFilesSelected(files);

    const previews: Media[] = await Promise.all(files.map(async (file) => {
      if (file.type.startsWith("video")) {
        const thumbnail = await generateVideoThumbnail(file);
        return {
          media_url: URL.createObjectURL(file),
          media_type: "video",
          thumbnail,
        };
      } else {
        return {
          media_url: URL.createObjectURL(file),
          media_type: "image",
        };
      }
    }));

    setPreviewMedia(previews);
  };

  useEffect(() => {
    return () => {
      previewMedia.forEach(media => {
        URL.revokeObjectURL(media.media_url);
        if (media.thumbnail) URL.revokeObjectURL(media.thumbnail);
      });
    };
  }, [previewMedia]);

  const baseURL = api.defaults.baseURL;

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
              <video
                src={media.local_path ? `${baseURL}/${media.local_path}` : media.media_url}
                className="h-20 w-auto"
                controls
              />
            ) : (
              <img
                src={media.local_path ? `${baseURL}/${media.local_path}` : media.media_url}
                className="h-20 w-auto"
              />
            )}
            <button
              type="button"
              className="absolute top-0 right-0 bg-red-500 text-white rounded-full w-5 h-5"
              onClick={() => onRemoveExisting?.(media.media_url)}
            >
              &times;
            </button>
          </div>
        ))}

        {previewMedia.map((media, index) => (
          <div key={index} className="relative">
            {media.media_type === "video" ? (
              <img src={media.thumbnail} className="h-20 w-auto opacity-70" />
            ) : (
              <img src={media.media_url} className="h-20 w-auto opacity-70" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// تابع تولید Thumbnail
export const generateVideoThumbnail = (file: File, seekTo = 3): Promise<string> => {
  return new Promise((resolve, reject) => {
    const videoPlayer = document.createElement('video');
    videoPlayer.src = URL.createObjectURL(file);
    videoPlayer.crossOrigin = 'anonymous';
    videoPlayer.load();
    videoPlayer.addEventListener('error', (error) => reject(error));

    videoPlayer.addEventListener('loadedmetadata', () => {
      if (videoPlayer.duration < seekTo) {
        seekTo = 0;
      }
      videoPlayer.currentTime = seekTo;
    });

    videoPlayer.addEventListener('seeked', () => {
      const canvas = document.createElement('canvas');
      canvas.width = videoPlayer.videoWidth;
      canvas.height = videoPlayer.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(videoPlayer, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(videoPlayer.src);
      canvas.toBlob((blob) => {
        if (blob) {
          const imgUrl = URL.createObjectURL(blob);
          resolve(imgUrl);
        } else {
          reject(new Error('Canvas is empty'));
        }
      }, 'image/png');
    });
  });
};
