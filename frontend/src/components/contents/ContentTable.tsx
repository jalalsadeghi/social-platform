// src/components/content/ContentTable.tsx
import { useState } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { useContents, useContent } from "@/hooks/useContents";
import { useCurrentVideoProgress } from "@/hooks/useContents";
import { ContentDialog } from "./ContentDialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import {
  Table, TableBody, TableCell, TableHead, TableHeader,
  TableRow, TableCaption,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Pencil, Trash } from "lucide-react";
import api from "@/services/api";
import { toast } from "sonner";
import { usePlatform } from "@/hooks/usePlatform";

export const ContentTable = () => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedContent, setSelectedContent] = useState(null);
  const { deleteMutation } = useContent();
  const { data: currentProgress } = useCurrentVideoProgress();
  const { data, fetchNextPage, hasNextPage, isLoading } = useContents();
  const { platformsQuery } = usePlatform();

  const platforms = platformsQuery.data?.pages.flat() || [];

  const getPlatformNameById = (ps) => {
    const platform = platforms.find(p => p.id === ps.platform_id);
    return platform ? `${platform.platform} (${platform.username})` : "Unknown";
  };

  const contents = data?.pages.flat().sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) || [];

  const baseURL = api.defaults.baseURL;

  const handleEditClick = (content) => {
    setSelectedContent(content);
    setDialogOpen(true);
  };

  const handleDeleteClick = (id) => {
    deleteMutation.mutate(id, {
      onSuccess: () => toast.success("Content deleted successfully"),
      onError: () => toast.error("Failed to delete content"),
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="w-full h-12" />
        <Skeleton className="w-full h-12" />
        <Skeleton className="w-full h-12" />
      </div>
    );
  }

  return (
    <>
      <div className="flex justify-end mb-4">
        <Button onClick={() => setDialogOpen(true)}>Add New Content</Button>
      </div>

      <InfiniteScroll
        dataLength={contents.length}
        next={fetchNextPage}
        hasMore={!!hasNextPage}
        loader={<Skeleton className="w-full h-12" />}
      >
        <Table>
          <TableCaption>A list of your contents.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>#</TableHead>
              <TableHead>Thumbnail</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contents.map((content, index) => (
              <>
                <TableRow key={content.id}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>
                    <img
                      src={`${baseURL}/${content.thumb_filename}`}
                      alt={content.ai_title}
                      className="w-12 h-12 rounded object-cover cursor-pointer"
                      onClick={() => window.open(`${baseURL}/${content.thumb_filename}`, "_blank")}
                    />
                  </TableCell>
                  <TableCell>{content.ai_title}</TableCell>
                  <TableCell>
                    {content.status === 'processing' && currentProgress?.progress !== undefined ? (
                      typeof currentProgress.progress === 'number' ? (
                        <Progress value={currentProgress.progress} className="w-32" />
                      ) : currentProgress.progress
                    ) : content.status}
                  </TableCell>
                  <TableCell>{new Date(content.created_at).toLocaleString()}</TableCell>
                  <TableCell className="text-right space-x-2">
                    <button onClick={() => handleEditClick(content)} className="text-blue-500 hover:text-blue-700">
                      <Pencil size={16} />
                    </button>
                    <button onClick={() => handleDeleteClick(content.id)} className="text-red-500 hover:text-red-700">
                      <Trash size={16} />
                    </button>
                  </TableCell>
                </TableRow>
                {content.platforms_status.map((ps) => (
                  <TableRow key={ps.platform_id}>
                    <TableCell></TableCell>
                    <TableCell colSpan={2} className="pl-20 text-sm text-gray-600">
                      {getPlatformNameById(ps)}
                    </TableCell>
                    <TableCell colSpan={2} className="text-sm text-gray-600">
                      <span className="capitalize font-semibold">{ps.status}</span>
                    </TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                ))}
              </>
            ))}
          </TableBody>
        </Table>
      </InfiniteScroll>

      {dialogOpen && (
        <ContentDialog
          contentId={selectedContent?.id}
          initialData={selectedContent || undefined}
          open={dialogOpen}
          onClose={() => {
            setDialogOpen(false);
            setSelectedContent(null);
          }}
        />
      )}
    </>
  );
};
