// src/hooks/usePlans.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getPlans, createPlan, updatePlan, deletePlan } from "@/services/plan";
import { toast } from "sonner";

export const usePlans = () => {
  const queryClient = useQueryClient();

  const plansQuery = useQuery({ queryKey: ["plans"], queryFn: getPlans });

  const createMutation = useMutation({
    mutationFn: createPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plans"] });
      toast.success("Plan created successfully.");
    },
    onError: () => toast.error("Failed to create plan."),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: PlanUpdate }) => updatePlan(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plans"] });
      toast.success("Plan updated successfully.");
    },
    onError: () => toast.error("Failed to update plan."),
  });

  const deleteMutation = useMutation({
    mutationFn: deletePlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plans"] });
      toast.success("Plan deleted successfully.");
    },
    onError: () => toast.error("Failed to delete plan."),
  });

  return { plansQuery, createMutation, updateMutation, deleteMutation };
};
