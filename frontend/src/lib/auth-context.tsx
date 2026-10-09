import React, { createContext, useContext, useState, useEffect } from "react";

export interface AuthContextType {
  isAuthenticated: boolean;
  operatorEmail: string;
  login: (token?: string, email?: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  operatorEmail: "",
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [operatorEmail, setOperatorEmail] = useState<string>("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("erakshak_jwt");
      const email = localStorage.getItem("erakshak_operator_email") || "";
      if (token) {
        setIsAuthenticated(true);
        setOperatorEmail(email);
      }
    }
  }, []);

  const login = (token?: string, email?: string) => {
    if (typeof window !== "undefined") {
      if (token) localStorage.setItem("erakshak_jwt", token);
      if (email) localStorage.setItem("erakshak_operator_email", email);
    }
    if (email) setOperatorEmail(email);
    setIsAuthenticated(true);
  };

  const logout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("erakshak_jwt");
      localStorage.removeItem("erakshak_operator_email");
    }
    setOperatorEmail("");
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, operatorEmail, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
