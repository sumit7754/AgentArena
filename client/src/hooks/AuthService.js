import { useState, useEffect } from 'react';

const authChangeEvent = new Event('authChange');

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));

  useEffect(() => {
    const updateAuthState = () => {
      setIsLoggedIn(!!localStorage.getItem('access_token'));
    };

    window.addEventListener('authChange', updateAuthState);
    return () => {
      window.removeEventListener('authChange', updateAuthState);
    };
  }, []);

  return isLoggedIn;
};

export const useCheckRole = () => {
  const [userRole, setUserRole] = useState(localStorage.getItem('role') || null);

  useEffect(() => {
    const updateRoleState = () => {
      setUserRole(localStorage.getItem('role'));
    };

    window.addEventListener('authChange', updateRoleState);
    return () => {
      window.removeEventListener('authChange', updateRoleState);
    };
  }, []);

  return userRole;
};

export const triggerAuthChange = () => {
  window.dispatchEvent(authChangeEvent);
};
