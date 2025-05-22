// src/components/plans/PlanDialog.tsx
import { useState, useEffect } from "react";
import { usePlans } from "@/hooks/usePlans";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

export const PlanDialog = ({ open, onClose, initialData }) => {
  const { createMutation, updateMutation } = usePlans();

  const [formData, setFormData] = useState({
    name: "",
    price: 0,
    description: "",
    is_active: true,
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    } else {
      setFormData({ name: "", price: 0, description: "", is_active: true });
    }
  }, [initialData]);

  const handleSubmit = () => {
    initialData
      ? updateMutation.mutate({ id: initialData.id, data: formData })
      : createMutation.mutate(formData);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{initialData ? "Edit Plan" : "Create Plan"}</DialogTitle>
        </DialogHeader>
        <Input placeholder="Name" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} />
        <Input type="number" placeholder="Price" value={formData.price} onChange={e => setFormData({ ...formData, price: +e.target.value })} />
        <Textarea placeholder="Description" value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} />

        <div className="flex items-center gap-2">
          <Switch checked={formData.is_active} onCheckedChange={val => setFormData({ ...formData, is_active: val })} />
          <Label>Active</Label>
        </div>

        <Button onClick={handleSubmit}>Save</Button>
      </DialogContent>
    </Dialog>
  );
};
