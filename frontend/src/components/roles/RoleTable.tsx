// src/components/roles/RoleTable.tsx
import { useState } from "react";
import { useRoles } from "@/hooks/useRoles";
import { RoleDialog } from "./RoleDialog";
import { Button } from "@/components/ui/button";

export const RoleTable = () => {
  const { rolesQuery, deleteMutation } = useRoles();
  const [selectedRole, setSelectedRole] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setDialogOpen(true)}>Add New Role</Button>
      <table className="w-full table-auto">
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rolesQuery.data?.map((role) => (
            <tr key={role.id}>
              <td>{role.name}</td>
              <td>{role.description}</td>
              <td>
                <button onClick={() => { setSelectedRole(role); setDialogOpen(true); }}>Edit</button>
                <button onClick={() => deleteMutation.mutate(role.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {dialogOpen && (
        <RoleDialog
          roleId={selectedRole?.id}
          initialData={selectedRole}
          open={dialogOpen}
          onClose={() => { setSelectedRole(null); setDialogOpen(false); }}
        />
      )}
    </>
  );
};
