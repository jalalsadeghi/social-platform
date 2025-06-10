// src/pages/dashboard/PlatformPage.tsx
import { PlatformTable } from "@/components/platforms/PlatformTable";
import { PlatformDialog } from "@/components/platforms/PlatformDialog";

const PlatformPage = () => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <PlatformDialog open={false} onClose={() => {}} />
        <input
          placeholder="Search platforms..."
          className="border rounded p-2"
        />
      </div>
      <PlatformTable />
    </div>
  );
};

export default PlatformPage;
