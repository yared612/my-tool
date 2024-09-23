import React, { useContext, useEffect } from 'react';
import { AuthContext } from '../../utils/AuthContext';

const Login: React.FC = () => {
  const { login } = useContext(AuthContext);

  useEffect(() => {
    console.log('Login component mounted. Triggering login...');
    login();
  }, [login]);

  return <div>Redirecting to LINE Login...</div>;
};

export default Login;
