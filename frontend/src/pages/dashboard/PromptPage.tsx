// src/pages/dashboard/PromptPage.tsx
import { PromptTable } from "@/components/prompts/PromptTable";
import { PromptDialog } from "@/components/prompts/PromptDialog";

const PromptPage = () => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <PromptDialog open={false} onClose={() => {}} />
        <input
          placeholder="Search prompts..."
          className="border rounded p-2"
        />
      </div>
      <PromptTable />
    </div>
  );
};

export default PromptPage;
