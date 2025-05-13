// src/main.tsx

import './index.css'
import App from './App.tsx'
import React from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider } from "@/context/AuthContext";
import { BrowserRouter } from "react-router-dom";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);