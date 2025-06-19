// src/components/layout/nav-main.tsx
"use client";

import { type LucideIcon } from "lucide-react";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

interface NavItem {
  title: string;
  url: string;
  icon?: LucideIcon;
  isActive?: boolean;
  children?: { title: string; url: string }[];
}

export function NavMain({ items }: { items: NavItem[] }) {
  return (
    <SidebarMenu>
      {items.map((item) => (
        <div key={item.title}>
          <SidebarMenuItem>
            <SidebarMenuButton asChild isActive={item.isActive}>
              <a href={item.url}>
                {item.icon && <item.icon />}
                <span>{item.title}</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
          {item.children &&
            item.children.map((child) => (
              <SidebarMenuItem key={child.title} className="pl-6">
                <SidebarMenuButton asChild>
                  <a href={child.url}>
                    <span>{child.title}</span>
                  </a>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
        </div>
      ))}
    </SidebarMenu>
  );
}
