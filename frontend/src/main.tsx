// src/main.tsx
import './index.css';
import App from './App';
import React from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider } from "@/context/AuthContext";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";

// ایجاد یک نمونه از QueryClient
const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <App />
          <Toaster />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
