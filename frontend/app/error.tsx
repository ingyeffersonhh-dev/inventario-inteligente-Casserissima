"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service if needed
    console.error("Global Error Boundary Caught:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#0D0F14] flex items-center justify-center p-4 text-[#E8EAF0]">
      <div className="max-w-md w-full bg-[#161B27] border border-[#2A3347] rounded-xl p-8 flex flex-col items-center text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center">
          <AlertTriangle className="w-8 h-8 text-red-400" />
        </div>
        
        <div className="space-y-2">
          <h2 className="text-xl font-bold">Algo salió mal</h2>
          <p className="text-sm text-[#5E6C84]">
            Hubo un problema inesperado en el motor predictivo o en la interfaz. 
            El equipo ha sido notificado (si los logs están habilitados).
          </p>
        </div>

        <button
          onClick={() => reset()}
          className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-[#C9A84C] hover:bg-[#b09341] text-[#0D0F14] font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-[#C9A84C] focus:ring-offset-2 focus:ring-offset-[#161B27]"
        >
          <RefreshCcw className="w-4 h-4" />
          Intentar nuevamente
        </button>
      </div>
    </div>
  );
}
