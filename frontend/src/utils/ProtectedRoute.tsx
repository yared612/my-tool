import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';

interface ProtectedRouteProps {
  children: JSX.Element;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { authenticated } = useContext(AuthContext);
  console.log('ProtectedRoute: authenticated =', authenticated);

  if (!authenticated) {
    console.log('ProtectedRoute: Redirecting to /login');
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
