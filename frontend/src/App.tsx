// src/App.tsx
import { Routes, Route } from "react-router-dom";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import ProductPage from '@/pages/dashboard/ProductPage';
import RolesPage from '@/pages/dashboard/RolesPage';
import PlanPage from '@/pages/dashboard/PlanPage';

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
