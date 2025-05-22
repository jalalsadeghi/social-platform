// src/services/role.ts
import api from "@/services/api";

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions: Record<string, Record<string, boolean>>;
  created_at: string;
  updated_at: string;
}

export interface RoleCreate {
  name: string;
  description?: string;
  permissions: Record<string, Record<string, boolean>>;
}

export interface RoleUpdate extends Partial<RoleCreate> {}

export const getRoles = async (): Promise<Role[]> => {
  const response = await api.get("/admin/roles");
  return response.data;
};

export const createRole = async (role: RoleCreate): Promise<Role> => {
  const response = await api.post("/admin/roles", role);
  return response.data;
};

export const updateRole = async (id: string, role: RoleUpdate): Promise<Role> => {
  const response = await api.put(`/admin/roles/${id}`, role);
  return response.data;
};

export const deleteRole = async (id: string): Promise<void> => {
  await api.delete(`/admin/roles/${id}`);
};
