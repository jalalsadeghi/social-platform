// src/services/plan.ts
import api from "@/services/api";

export interface Plan {
  id: string;
  name: string;
  price: number;
  description?: string;
  features: Record<string, string>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PlanCreate {
  name: string;
  price: number;
  description?: string;
  features: Record<string, string>;
  is_active?: boolean;
}

export interface PlanUpdate extends Partial<PlanCreate> {}

export const getPlans = async (): Promise<Plan[]> => {
  const response = await api.get("/plans");
  return response.data;
};

export const createPlan = async (data: PlanCreate): Promise<Plan> => {
  const response = await api.post("/plans", data);
  return response.data;
};

export const updatePlan = async (id: string, data: PlanUpdate): Promise<Plan> => {
  const response = await api.put(`/plans/${id}`, data);
  return response.data;
};

export const deletePlan = async (id: string): Promise<void> => {
  await api.delete(`/plans/${id}`);
};
