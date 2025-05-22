// src/components/plans/PlanTable.tsx
import { usePlans } from "@/hooks/usePlans";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { PlanDialog } from "./PlanDialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export const PlanTable = () => {
  const { plansQuery, deleteMutation } = usePlans();
  const { data: plans = [], isLoading } = plansQuery;

  const [selectedPlan, setSelectedPlan] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleEdit = (plan) => {
    setSelectedPlan(plan);
    setDialogOpen(true);
  };

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Plans</h2>
        <Button onClick={() => { setSelectedPlan(null); setDialogOpen(true); }}>
          Add Plan
        </Button>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Price</TableHead>
            <TableHead>Active</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {plans.map(plan => (
            <TableRow key={plan.id}>
              <TableCell>{plan.name}</TableCell>
              <TableCell>${plan.price}</TableCell>
              <TableCell>{plan.is_active ? "Yes" : "No"}</TableCell>
              <TableCell className="text-right">
                <Button variant="link" onClick={() => handleEdit(plan)}>Edit</Button>
                <Button variant="link" className="text-red-500" onClick={() => deleteMutation.mutate(plan.id)}>Delete</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {dialogOpen && (
        <PlanDialog
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          initialData={selectedPlan}
        />
      )}
    </>
  );
};
