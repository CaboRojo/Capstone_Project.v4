import React, { lazy } from 'react';
import { Routes, Route } from 'react-router-dom';

// Loadable utility to dynamically load components with loading fallbacks
import Loadable from 'ui-component/Loadable';

// Dynamic imports for components
const DashboardDefault = Loadable(lazy(() => import('views/dashboard/Default')));
const UtilsTypography = Loadable(lazy(() => import('views/utilities/Typography')));
const UtilsColor = Loadable(lazy(() => import('views/utilities/Color')));
const UtilsShadow = Loadable(lazy(() => import('views/utilities/Shadow')));
const UtilsMaterialIcons = Loadable(lazy(() => import('views/utilities/MaterialIcons')));
const UtilsTablerIcons = Loadable(lazy(() => import('views/utilities/TablerIcons')));
const SamplePage = Loadable(lazy(() => import('views/sample-page')));
const AssetDetailsPage = Loadable(lazy(() => import('views/details')));

// Authentication pages
const Login3 = Loadable(lazy(() => import('views/pages/authentication/authentication3/Login3')));
const Register3 = Loadable(lazy(() => import('views/pages/authentication/authentication3/Register3')));

// Layout components
const MainLayout = Loadable(lazy(() => import('layout/MainLayout')));

// Authentication check function
const isAuthenticated = () => !!localStorage.getItem('token');

// Main Routes Component
const MainRoutes = () => (
  <Routes>
    <Route path="/" element={<MainLayout />}>
      <Route index element={isAuthenticated() ? <DashboardDefault /> : <Login3 />} />
      <Route path="dashboard/default" element={<DashboardDefault />} />
      <Route path="utils/typography" element={<UtilsTypography />} />
      <Route path="utils/color" element={<UtilsColor />} />
      <Route path="utils/shadow" element={<UtilsShadow />} />
      <Route path="icons/material-icons" element={<UtilsMaterialIcons />} />
      <Route path="icons/tabler-icons" element={<UtilsTablerIcons />} />
      <Route path="sample-page" element={<SamplePage />} />
      <Route path="details/:symbol" element={<AssetDetailsPage />} />
      {/* The login and register routes are nested within MainLayout */}
      <Route path="login" element={<Login3 />} />
      <Route path="register" element={<Register3 />} />
    </Route>
  </Routes>
);

export default MainRoutes;
