
import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'; import './styles/tokens.css'
import App from './App'
import Home from './pages/Home'
import Guide from './pages/Guide'
import Workbench from './pages/Workbench'
import Dashboard from './pages/Dashboard'
import Marketplace from './pages/Marketplace'
import Pricing from './pages/Pricing'
import FAQ from './pages/FAQ'

const router = createBrowserRouter([{
  path: '/', element: <App/>,
  children: [
    { index: true, element: <Home/> },
    { path: 'guide', element: <Guide/> },
    { path: 'workbench', element: <Workbench/> },
    { path: 'dashboard', element: <Dashboard/> },
    { path: 'marketplace', element: <Marketplace/> },
    { path: 'pricing', element: <Pricing/> },
    { path: 'faq', element: <FAQ/> },
  ]
}])

createRoot(document.getElementById('root')!).render(
  <React.StrictMode><RouterProvider router={router}/></React.StrictMode>
)
