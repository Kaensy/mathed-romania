import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import api from "@/api/client";
import { useAuth } from "@/hooks/useAuth";
import type { GlossaryTerm } from "@/types/glossary";

interface GlossaryContextType {
  terms: GlossaryTerm[];
  isReady: boolean;
}

const GlossaryContext = createContext<GlossaryContextType | null>(null);

export function GlossaryProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      // Reset on logout so a subsequent login triggers a fresh fetch.
      setTerms([]);
      setIsReady(false);
      return;
    }

    let cancelled = false;
    api
      .get<GlossaryTerm[]>("/content/glossary/")
      .then((res) => {
        if (!cancelled) setTerms(res.data);
      })
      .catch(() => {
        // Fail open: leave terms empty so consumers fall back to plain text.
      })
      .finally(() => {
        if (!cancelled) setIsReady(true);
      });

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  const value = useMemo(() => ({ terms, isReady }), [terms, isReady]);

  return (
    <GlossaryContext.Provider value={value}>{children}</GlossaryContext.Provider>
  );
}

export function useGlossary(): GlossaryContextType {
  const context = useContext(GlossaryContext);
  if (!context) {
    throw new Error("useGlossary must be used within a GlossaryProvider");
  }
  return context;
}
