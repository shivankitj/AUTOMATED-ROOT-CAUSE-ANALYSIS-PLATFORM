import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Anomalies from './pages/Anomalies'
import RCAReports from './pages/RCAReports'
import Alerts from './pages/Alerts'
import SystemHealth from './pages/SystemHealth'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/anomalies" element={<Anomalies />} />
            <Route path="/rca-reports" element={<RCAReports />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/system-health" element={<SystemHealth />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
