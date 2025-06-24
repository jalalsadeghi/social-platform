// src/components/platforms/PlatformContentTable.tsx
import React, { useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { usePlatformContent, useDeletePlatformContent } from "@/hooks/usePlatformContent";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableCaption,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Trash } from "lucide-react";
import api from "@/services/api";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import type { PlatformContent } from "@/services/platformContent";

interface PlatformContentTableProps {
  platformId: string;
}

const statuses = ["pending", "ready", "posting", "posted", "failed"];

export const PlatformContentTable: React.FC<PlatformContentTableProps> = ({ platformId }) => {
  const queryClient = useQueryClient();
  const { data, fetchNextPage, hasNextPage, isLoading } = usePlatformContent(platformId);
  const deleteMutation = useDeletePlatformContent();

  const [selectedStatus, setSelectedStatus] = useState("ready");
  const [contents, setContents] = useState<PlatformContent[]>([]);

  useEffect(() => {
    const allContents = data?.pages.flat() || [];
    let filteredContents = allContents.filter(content => content.status === selectedStatus);

    if (selectedStatus === "ready") {
      filteredContents = filteredContents.sort((a, b) => a.priority - b.priority);
    } else {
      // مرتب کردن بر اساس آخرین آپدیت
      filteredContents = filteredContents.sort(
        (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      );
    }

    setContents(filteredContents);
  }, [data, selectedStatus]);

  const handleDelete = (id: string) => deleteMutation.mutate(id);

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    const reorderedItems = Array.from(contents);
    const [removed] = reorderedItems.splice(result.source.index, 1);
    reorderedItems.splice(result.destination.index, 0, removed);

    setContents(reorderedItems);

    const priorityUpdates = reorderedItems.map((item, index) => ({
      content_platform_id: item.id,
      priority: index + 1,
    }));

    api.put("/contents/priority/update", { priorities: priorityUpdates })
      .then(() => queryClient.invalidateQueries({ queryKey: ["platformContents", platformId] }))
      .catch(err => console.error(err));
  };

  if (isLoading) return <Skeleton className="w-full h-12" />;

  return (
    <>
      <div className="mb-4">
        {statuses.map(status => (
          <Button key={status} onClick={() => setSelectedStatus(status)} variant={selectedStatus === status ? "default" : "outline"}>
            {status}
          </Button>
        ))}
      </div>

      <InfiniteScroll dataLength={contents.length} next={fetchNextPage} hasMore={!!hasNextPage} loader={<Skeleton className="w-full h-12" />}>
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="contents">
            {(provided) => (
              <Table {...provided.droppableProps} ref={provided.innerRef}>
                <TableCaption>A list of platform contents.</TableCaption>
                <TableHeader>
                  <TableRow>
                    <TableHead>#</TableHead>
                    <TableHead>Thumbnail</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Send Time</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contents.map((content, index) => (
                    <Draggable draggableId={content.id} index={index} key={content.id} isDragDisabled={selectedStatus !== "ready"}>
                      {(provided) => (
                        <TableRow ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}>
                          <TableCell>{index + 1}</TableCell>
                          <TableCell>
                            <img src={`${api.defaults.baseURL}/${content.thumb_filename}`} alt={content.title} className="w-12 h-12 rounded object-cover cursor-pointer" onClick={() => window.open(`${api.defaults.baseURL}/${content.video_filename}`, "_blank")} />
                          </TableCell>
                          <TableCell>
                            {content.status === "posted" && content.url ? (
                              <a
                                href={`https://www.instagram.com/p/${content.url}/`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline"
                              >
                                {content.title}
                              </a>
                            ) : (
                              <span>{content.title}</span>
                            )}
                          </TableCell>
                          <TableCell>{content.send_time || "Not Scheduled"}</TableCell>
                          <TableCell>{content.status}</TableCell>
                          <TableCell className="text-right">
                            <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-700" onClick={() => handleDelete(content.id)}>
                              <Trash size={16} />
                            </Button>
                          </TableCell>
                        </TableRow>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </TableBody>
              </Table>
            )}
          </Droppable>
        </DragDropContext>
      </InfiniteScroll>
    </>
  );
};