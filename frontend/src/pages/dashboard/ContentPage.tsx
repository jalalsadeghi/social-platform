// src/pages/ContentPage.tsx
import { ContentTable } from "@/components/contents/ContentTable";
import { ContentDialog } from "@/components/contents/ContentDialog";

const ContentPage = () => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <ContentDialog open={false} onClose={() => {}} />
        <input placeholder="Search..." className="border rounded p-2" />
      </div>
      <ContentTable />
    </div>
  );
};

export default ContentPage;
