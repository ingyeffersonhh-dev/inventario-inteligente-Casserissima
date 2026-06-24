"use client";
import { createContext, useContext, useState, ReactNode, useCallback } from "react";

interface ScenarioContextValue {
  refreshKey: number;
  triggerRefresh: () => void;
}

const ScenarioContext = createContext<ScenarioContextValue>({
  refreshKey: 0,
  triggerRefresh: () => {},
});

export function ScenarioProvider({ children }: { children: ReactNode }) {
  const [refreshKey, setRefreshKey] = useState(0);
  const triggerRefresh = useCallback(() => setRefreshKey((k) => k + 1), []);
  return (
    <ScenarioContext.Provider value={{ refreshKey, triggerRefresh }}>
      {children}
    </ScenarioContext.Provider>
  );
}

export function useScenario() {
  return useContext(ScenarioContext);
}