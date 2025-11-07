import React, { lazy } from "react";
import { Navigate } from "react-router-dom";
import { PrivateRoute } from "./PrivateRoute.jsx";

const Landing = lazy(() => import("../pages/Landing.jsx"));
const Login = lazy(() => import("../pages/Login.jsx"));
const Dashboard = lazy(() => import("../pages/Dashboard.jsx"));
const Users = lazy(() => import("../pages/Users.jsx"));
const Profile = lazy(() => import("../pages/Profile.jsx"));
const ComplianceTrends = lazy(() => import("../pages/ComplianceTrends.jsx"));
const Notifications = lazy(() => import("../pages/Notifications.jsx"));
const Persistence = lazy(() => import("../pages/Persistence.jsx"));
const ProcessMonitoring = lazy(() => import("../pages/ProcessMonitoring.jsx"));
const Integrity = lazy(() => import("../pages/Integrity.jsx"));
const ThreatIntel = lazy(() => import("../pages/ThreatIntel.jsx"));
const ComplianceMatrix = lazy(() => import("../pages/ComplianceMatrix.jsx"));
const RetentionExports = lazy(() => import("../pages/RetentionExports.jsx"));
const Billing = lazy(() => import("../pages/Billing.jsx"));
const ScanOrchestration = lazy(() => import("../pages/ScanOrchestration.jsx"));
const NotificationHistory = lazy(() => import("../pages/NotificationHistory.jsx"));
const ModuleCatalog = lazy(() => import("../pages/ModuleCatalog.jsx"));
const CloudDiscovery = lazy(() => import("../pages/CloudDiscovery.jsx"));
const Discovery = lazy(() => import("../pages/Discovery.jsx"));
const Onboarding = lazy(() => import("../pages/Onboarding.jsx"));
const FeatureFlags = lazy(() => import("../pages/FeatureFlags.jsx"));
const AlertSettings = lazy(() => import("../pages/AlertSettings.jsx"));
const ObservabilitySetup = lazy(() => import("../pages/ObservabilitySetup.jsx"));
const Metrics = lazy(() => import("../pages/Metrics.jsx"));
const FAQ = lazy(() => import("../pages/FAQ.jsx"));
const AuditLogs = lazy(() => import("../pages/AuditLogs.jsx"));
const Search = lazy(() => import("../pages/Search.jsx"));
const ShellLayout = lazy(() => import("../layouts/Shell.jsx"));
const AdminSettings = lazy(() => import("../pages/AdminSettings.jsx"));

export const routeConfig = [
  {
    path: "/marketing",
    element: <Landing />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/",
    element: (
      <PrivateRoute>
        <ShellLayout />
      </PrivateRoute>
    ),
    children: [
      { index: true, element: <Navigate to="dashboard" replace /> },
      { path: "dashboard", element: <Dashboard /> },
      { path: "profile", element: <Profile /> },
      { path: "compliance-trends", element: <ComplianceTrends /> },
      { path: "compliance-matrix", element: <ComplianceMatrix /> },
      { path: "notifications", element: <Notifications /> },
      { path: "metrics", element: <Metrics /> },
      { path: "persistence", element: <Persistence /> },
      { path: "process-monitoring", element: <ProcessMonitoring /> },
      { path: "integrity", element: <Integrity /> },
      {
        path: "threat-intel",
        element: (
          <PrivateRoute requireAdmin>
            <ThreatIntel />
          </PrivateRoute>
        ),
      },
      { path: "retention", element: <RetentionExports /> },
      { path: "billing", element: <Billing /> },
      { path: "scans", element: <ScanOrchestration /> },
      { path: "modules", element: <ModuleCatalog /> },
      { path: "notification-history", element: <NotificationHistory /> },
      { path: "cloud", element: <CloudDiscovery /> },
      { path: "discovery", element: <Discovery /> },
      { path: "search", element: <Search /> },
      { path: "onboarding", element: <Onboarding /> },
      {
        path: "faq",
        element: (
          <PrivateRoute>
            <FAQ />
          </PrivateRoute>
        ),
      },
      {
        path: "observability-setup",
        element: (
          <PrivateRoute requireAdmin>
            <ObservabilitySetup />
          </PrivateRoute>
        ),
      },
      {
        path: "users",
        element: (
          <PrivateRoute requireAdmin>
            <Users />
          </PrivateRoute>
        ),
      },
      {
        path: "admin-settings",
        element: (
          <PrivateRoute requireAdmin>
            <AdminSettings />
          </PrivateRoute>
        ),
      },
      {
        path: "feature-flags",
        element: (
          <PrivateRoute requireAdmin>
            <FeatureFlags />
          </PrivateRoute>
        ),
      },
      {
        path: "alert-settings",
        element: (
          <PrivateRoute requireAdmin>
            <AlertSettings />
          </PrivateRoute>
        ),
      },
      {
        path: "audit-logs",
        element: (
          <PrivateRoute requireAdmin>
            <AuditLogs />
          </PrivateRoute>
        ),
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/login" replace />,
  },
];
