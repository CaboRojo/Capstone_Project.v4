import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import AuthCardWrapper from './AuthCardWrapper';
import AuthLogin from './auth-forms/AuthLogin';
import AuthRegister from './auth-forms/AuthRegister';

// Use useLocation to get the current path
const AuthWrapper1 = () => {
  const location = useLocation();
  const loginPath = '/login';

  return (
    <AuthCardWrapper>
      {location.pathname === loginPath ? <AuthLogin /> : <AuthRegister />}
      <div className="mt-6 text-center">
        <Link to={loginPath} className="text-blue-600 hover:text-blue-800">
          Login
        </Link>
      </div>
    </AuthCardWrapper>
  );
};

export default AuthWrapper1;
