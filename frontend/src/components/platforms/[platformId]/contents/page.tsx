// app/platforms/[platformId]/contents/page.tsx
"use client";

import { useParams } from "react-router-dom";
import { PlatformContentTable } from "@/components/platforms/PlatformContentTable";
import { Skeleton } from "@/components/ui/skeleton";
import { useSinglePlatform } from "@/hooks/usePlatform";

export default function PlatformContentPage() {
  const { platformId } = useParams<{ platformId: string }>();

  const { data: platform, isLoading } = useSinglePlatform(platformId);

  if (isLoading || !platform) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">
        Contents for {platform.username} ({platform.platform})
      </h1>
      <PlatformContentTable platformId={platformId} />
    </div>
  );
}
