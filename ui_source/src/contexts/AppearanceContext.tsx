import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

type AppearanceContextValue = {
  isDark: boolean;
  setIsDark: (value: boolean) => void;
};

const AppearanceContext = createContext<AppearanceContextValue | undefined>(
  undefined
);

const readPreference = (key: string, fallback: boolean) => {
  if (typeof window === "undefined") return fallback;
  const stored = window.localStorage.getItem(key);
  return stored === null ? fallback : stored === "true";
};

export const AppearanceProvider = ({ children }: { children: ReactNode }) => {
  const [isDark, setIsDark] = useState(() =>
    readPreference("mathmentor-dark", true)
  );

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("light", !isDark);
    root.classList.toggle("dark", isDark);
    root.classList.remove("normal-mode", "focus-mode", "cool-mode", "simple-mode");
    window.localStorage.setItem("mathmentor-dark", String(isDark));
    window.localStorage.removeItem("mathmentor-normal");
    window.localStorage.removeItem("mathmentor-cool");
  }, [isDark]);

  const value = useMemo(
    () => ({ isDark, setIsDark }),
    [isDark]
  );

  return (
    <AppearanceContext.Provider value={value}>
      {children}
    </AppearanceContext.Provider>
  );
};

export const useAppearance = () => {
  const context = useContext(AppearanceContext);
  if (!context) {
    throw new Error("useAppearance must be used within AppearanceProvider");
  }
  return context;
};