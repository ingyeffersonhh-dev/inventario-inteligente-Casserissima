"use client";
import { ReactNode, useEffect, useState } from "react";
import Sidebar, { SidebarProvider } from "@/components/layout/Sidebar";
import ScenarioSwitcher from "@/components/layout/ScenarioSwitcher";
import ThemeToggle from "@/components/layout/ThemeToggle";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ScenarioProvider, useScenario } from "@/lib/scenarioContext";

interface AppShellProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

function ApiStatusDot() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch("/api/v1/scenarios", { signal: AbortSignal.timeout(3000) });
        setOnline(res.ok);
      } catch {
        setOnline(false);
      }
    };
    check();
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, []);

  if (online === null) return null;

  return (
    <div className="flex items-center gap-1.5">
      <span
        className={`w-1.5 h-1.5 rounded-full ${online ? "pulse-glow" : ""}`}
        style={{ background: online ? "var(--success)" : "var(--danger)" }}
      />
      <span
        className="text-[10px] font-mono hidden sm:inline"
        style={{ color: online ? "var(--success)" : "var(--danger)", fontFamily: "var(--font-mono)" }}
      >
        {online ? "Motor conectado" : "Sin conexión"}
      </span>
    </div>
  );
}

function ShellInner({ children, title, subtitle }: AppShellProps) {
  const router = useRouter();
  const { triggerRefresh } = useScenario();

  return (
    <div className="flex min-h-screen" style={{ background: "var(--bg-base)" }}>
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        {/* TopBar */}
        <header
          className="sticky top-0 z-30 flex items-center justify-between px-6 py-3 glass"
          style={{ borderBottom: "1px solid var(--bg-border)" }}
        >
          <motion.div
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h1
              className="text-base font-semibold leading-tight"
              style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
            >
              {title}
            </h1>
            {subtitle && (
              <p className="text-[11px] mt-0.5" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                {subtitle}
              </p>
            )}
          </motion.div>

          <div className="flex items-center gap-3">
            <ApiStatusDot />
            <div style={{ width: "1px", height: "20px", background: "var(--bg-border)" }} />
            <ThemeToggle />
            <ScenarioSwitcher onScenarioChange={() => { triggerRefresh(); router.refresh(); }} />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-5 overflow-auto">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
}

export default function AppShell(props: AppShellProps) {
  return (
    <SidebarProvider>
      <ScenarioProvider>
        <ShellInner {...props} />
      </ScenarioProvider>
    </SidebarProvider>
  );
}
