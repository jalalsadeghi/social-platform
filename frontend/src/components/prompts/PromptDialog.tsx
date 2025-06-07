// src/components/prompts/PromptDialog.tsx
import React, { useState, useEffect } from "react";
import { 
  usePrompts, 
  useLanguages, 
  usePromptSample,
} from "@/hooks/usePrompts";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { 
  Select, 
  SelectTrigger, 
  SelectContent, 
  SelectItem, 
  SelectValue,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select";

interface Props {
  promptId?: string;
  initialData?: {
    prompt_name: string;
    prompt_content: string;
    language: string;
    expertise: string;
    promt_type: string;
  };
  open: boolean;
  onClose: () => void;
}

export const PromptDialog: React.FC<Props> = ({
  promptId,
  initialData,
  open,
  onClose,
}) => {
  const { createMutation, updateMutation } = usePrompts();

  const { data: languages } = useLanguages();
  const { data: prompt_sample } = usePromptSample();
  
  const [formData, setFormData] = useState({
    prompt_name: "",
    prompt_content: "",
    language: "",
    expertise: "",
    promt_type: "",
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const resetForm = () => {
    setFormData({
      prompt_name: "",
      prompt_content: "",
      language: "",
      expertise: "",
      promt_type: "",
    });
  };

  const handleLanguageChange = (value: string) => {
    const selectedPrompt = prompt_sample?.find((p) => p.name === languages?.find(l => l.value === value)?.name);
    setFormData((prev) => ({
      ...prev,
      language: value,
      prompt_content: selectedPrompt ? selectedPrompt.value : prev.prompt_content,
    }));
  };

  const handleSubmit = async () => {
    if (!formData.prompt_name || !formData.prompt_content) {
      toast.error("Name and Content are required.");
      return;
    }

    promptId
      ? updateMutation.mutate({ id: promptId, data: formData })
      : createMutation.mutate(formData);

    onClose();
    resetForm();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="space-y-4 max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>{promptId ? "Edit Prompt" : "Add New Prompt"}</DialogTitle>
        </DialogHeader>

        <Input
          value={formData.prompt_name}
          onChange={(e) => setFormData({ ...formData, prompt_name: e.target.value })}
          placeholder="Prompt Name"
        />

        {/* <Select
          value={formData.promt_type}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select Prompt Type" />
          </SelectTrigger>
          <SelectContent>
            {prompt_type?.map((type) => (
              <SelectItem value={type.value}>{type.name}</SelectItem>
            ))}
          </SelectContent>
        </Select> */}

        <Select
          value={formData.promt_type}
          onValueChange={(value) => setFormData({ ...formData, promt_type: value })}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select a type" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Types</SelectLabel>
              <SelectItem value="caption_prompt">Caption</SelectItem>
              <SelectItem value="comment_prompt">Comment</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>

        <Select
          value={formData.language}
          onValueChange={handleLanguageChange}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select Language" />
          </SelectTrigger>
          <SelectContent>
            {languages?.map((lang) => (
              <SelectItem key={lang.value} value={lang.value}>
                {lang.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Textarea
          value={formData.prompt_content}
          onChange={(e) => setFormData({ ...formData, prompt_content: e.target.value })}
          placeholder="Prompt Content"
        />

        <Input
          value={formData.expertise}
          onChange={(e) => setFormData({ ...formData, expertise: e.target.value })}
          placeholder="Expertise"
        />

        <Button onClick={handleSubmit}>
          {promptId ? "Save Changes" : "Add"}
        </Button>
      </DialogContent>
    </Dialog>
  );
};
