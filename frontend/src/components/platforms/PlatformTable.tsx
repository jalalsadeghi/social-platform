// src/components/platforms/PlatformTable.tsx
import { useState } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { usePlatform } from "@/hooks/usePlatform";
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
import { PlatformDialog } from "./PlatformDialog";
import { Button } from "@/components/ui/button";

export const PlatformTable = () => {
  const { platformsQuery, deleteMutation } = usePlatform();
  const { data, fetchNextPage, hasNextPage, isLoading } = platformsQuery;
  
  const [selectedPlatform, setSelectedPlatform] = useState<any>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  

  const handleEditClick = (platform: any) => {
    setSelectedPlatform({
      ...platform,
      schedule: platform.schedule,
    });
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setSelectedPlatform(null);
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

  const sortedPlatforms = data?.pages.flat();
  
  return (
    <>
      <div className="flex justify-end items-center mb-4">
        <Button onClick={() => setAddDialogOpen(true)}>Add New Platform</Button>
      </div>

      <InfiniteScroll
        dataLength={sortedPlatforms?.length || 0}
        next={fetchNextPage}
        hasMore={!!hasNextPage}
        loader={<Skeleton className="w-full h-12" />}
      >
        <Table>
          <TableCaption>A list of your platforms.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>#</TableHead>
              <TableHead>Platform</TableHead>
              <TableHead>Account Identifier</TableHead>
              <TableHead>OAuth</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedPlatforms?.map((platform, index) => (
              <TableRow key={platform.id}>
                <TableCell>{index + 1}</TableCell>
                <TableCell>{platform.platform}</TableCell>
                <TableCell>{platform.username}</TableCell>
                <TableCell>{platform.is_oauth ? "Yes" : "No"}</TableCell>
                <TableCell className="text-right space-x-2">
                  <button
                    onClick={() => handleEditClick(platform)}
                    className="text-blue-500 hover:underline"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(platform.id)}
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
            
      {dialogOpen && selectedPlatform && (
        <PlatformDialog
          platformId={selectedPlatform.id}
          initialData={{
            platform: selectedPlatform.platform,
            // account_identifier: selectedPlatform.username,
            username: selectedPlatform.username,
            password: selectedPlatform.password,
            credentials: selectedPlatform.credentials,
            language: selectedPlatform.language,
            posts_per_day: selectedPlatform.posts_per_day,
            cookies: selectedPlatform.cookies,
            is_oauth: selectedPlatform.is_oauth,
            schedule: selectedPlatform.schedule,
          }}
          open={dialogOpen}
          onClose={handleCloseDialog}
        />
      )}

      <PlatformDialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} />
    </>
  );
};
