// src/App.tsx
import { Routes, Route } from "react-router-dom";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import ProductPage from '@/pages/dashboard/ProductPage';
import ContentPage from '@/pages/dashboard/ContentPage';
import RolesPage from '@/pages/dashboard/RolesPage';
import PlanPage from '@/pages/dashboard/PlanPage';
import PromptPage from '@/pages/dashboard/PromptPage';
import PlatformPage from '@/pages/dashboard/PlatformPage';

function App() {
  return (
    <Routes>
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>

        <Route element={<DashboardLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route element={<ProtectedRoute module="product" action="read" />}>
            <Route path="/products" element={<ProductPage />} />
          </Route>
          <Route element={<ProtectedRoute module="content" action="read" />}>
            <Route path="/contents" element={<ContentPage />} />
          </Route>
          <Route element={<ProtectedRoute module="prompt" action="read" />}>
            <Route path="/prompts" element={<PromptPage />} />
          </Route>
          <Route element={<ProtectedRoute module="platform" action="read" />}>
            <Route path="/platforms" element={<PlatformPage />} />
          </Route>
          <Route element={<ProtectedRoute module="role" action="read" />}>
            <Route path="/roles" element={<RolesPage />} />
          </Route>
          <Route element={<ProtectedRoute module="plan" action="read" />}>
            <Route path="/plans" element={<PlanPage />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
