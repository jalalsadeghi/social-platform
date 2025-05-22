// src/components/roles/RoleDialog.tsx
import React, { useState, useEffect } from "react";
import { useRoles } from "@/hooks/useRoles";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

interface Props {
  roleId?: string;
  initialData?: {
    name: string;
    description?: string;
    permissions: Record<string, Record<string, boolean>>;
  };
  open: boolean;
  onClose: () => void;
}

export const RoleDialog: React.FC<Props> = ({ roleId, initialData, open, onClose }) => {
  const { createMutation, updateMutation } = useRoles();
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    permissions: "{}",
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name,
        description: initialData.description || "",
        permissions: JSON.stringify(initialData.permissions, null, 2),
      });
    }
  }, [initialData]);

  const handleSubmit = () => {
    try {
      const permissions = JSON.parse(formData.permissions);
      const data = { ...formData, permissions };
      roleId ? updateMutation.mutate({ id: roleId, data }) : createMutation.mutate(data);
      onClose();
    } catch (error) {
      toast.error("Invalid JSON in permissions");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{roleId ? "Edit Role" : "Add New Role"}</DialogTitle>
        </DialogHeader>
        <Input
          placeholder="Role Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
        <Textarea
          placeholder="Description (optional)"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />
        <Textarea
          placeholder="Permissions (JSON format)"
          value={formData.permissions}
          onChange={(e) => setFormData({ ...formData, permissions: e.target.value })}
          rows={8}
        />
        <Button onClick={handleSubmit}>{roleId ? "Save Changes" : "Add Role"}</Button>
      </DialogContent>
    </Dialog>
  );
};
