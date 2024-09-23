import React, { useEffect, useState } from "react";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import './App.css';
import Login from './components/login/Login';
import Navbar from "./components/navbar/Navbar";
import Sidebar from "./components/sidebar/Sidebar";
import CalendarPage from "./pages/calendar/CalendarPage";
import { AuthProvider } from './utils/AuthContext';
import ProtectedRoute from './utils/ProtectedRoute';

export interface PageUser {
  name: string;
  email: string;
}

const App: React.FC = () => {
  const userName = "John Doe";
  const userEmail = "john.doe@example.com";

  // Controller sidebar state
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [user, setUser] = useState<PageUser | null>(null);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await fetch("http://localhost:5000/auth/line");
        if (response.ok) {
          const data = await response.json();
          console.log('Auth data: ', data)
          setUser(data);
        } else {
          console.error("Failed to fetch user data.");
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };

    fetchUserData();
  }, []);

  // Switch sidebar state
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <AuthProvider>
      <Router>
        {/* Navbar. Provide toggleSidebar function */}
        <Navbar user={user} toggleSidebar={toggleSidebar} />

        {/* Main-layout. Decording sidebar state to render sidebar */}
        <div className="main-layout">
          {isSidebarOpen && <Sidebar />}
          {user ? (
            <div className={isSidebarOpen ? "content sidebar-open" : "content sidebar-closed"}>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <CalendarPage />
                    </ProtectedRoute>
                  }
                />
                <Route path="/calendar" element={<CalendarPage />} />
              </Routes>
            </div>
          ) : (
            <p style={{marginRight: "32px"}}>Loading user info...</p>
          )}
        </div>
      </Router>
    </AuthProvider>
    
  );
};

export default App;
