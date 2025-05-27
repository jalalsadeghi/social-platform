// frontend/src/pages/dashboard/DashboardPage.tsx
import { AppSidebar } from "@/components/layout/app-sidebar"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

export default function DashboardPage() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <h3>test Dashboard</h3>
      </SidebarInset>
    </SidebarProvider>
  )
}
