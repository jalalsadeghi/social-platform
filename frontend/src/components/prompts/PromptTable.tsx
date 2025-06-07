// src/components/prompts/PromptTable.tsx
import { useState } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { usePrompts } from "@/hooks/usePrompts";
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
import { PromptDialog } from "./PromptDialog";
import { Button } from "@/components/ui/button";
import api from "@/services/api";

export const PromptTable = () => {
  const { promptsQuery, deleteMutation } = usePrompts();
  const { data, fetchNextPage, hasNextPage, isLoading } = promptsQuery;

  const [selectedPrompt, setSelectedPrompt] = useState<any>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [addDialogOpen, setAddDialogOpen] = useState(false);

  const handleEditClick = (prompt: any) => {
    setSelectedPrompt(prompt);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setSelectedPrompt(null);
    setDialogOpen(false);
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

  const sortedPrompts = data?.pages.flat();

  return (
    <>
      <div className="flex justify-end items-center mb-4">
        <Button onClick={() => setAddDialogOpen(true)}>Add New Prompt</Button>
      </div>

      <InfiniteScroll
        dataLength={sortedPrompts?.length || 0}
        next={fetchNextPage}
        hasMore={!!hasNextPage}
        loader={<Skeleton className="w-full h-12" />}
      >
        <Table>
          <TableCaption>A list of your prompts.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>#</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Language</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedPrompts?.map((prompt, index) => (
              <TableRow key={prompt.id}>
                <TableCell>{index + 1}</TableCell>
                <TableCell>{prompt.prompt_name}</TableCell>
                <TableCell>{prompt.language}</TableCell>
                <TableCell className="text-right space-x-2">
                  <button
                    onClick={() => handleEditClick(prompt)}
                    className="text-blue-500 hover:underline"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(prompt.id)}
                    className="text-red-500 hover:underline"
                  >
                    Delete
                  </button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </InfiniteScroll>

      {dialogOpen && selectedPrompt && (
        <PromptDialog
          promptId={selectedPrompt.id}
          initialData={{
            prompt_name: selectedPrompt.prompt_name,
            prompt_content: selectedPrompt.prompt_content,
            language: selectedPrompt.language,
            expertise: selectedPrompt.expertise,
            promt_type: selectedPrompt.promt_type,
          }}
          open={dialogOpen}
          onClose={handleCloseDialog}
        />
      )}

      <PromptDialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} />
    </>
  );
};