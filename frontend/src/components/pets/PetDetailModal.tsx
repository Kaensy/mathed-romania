import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { AxiosError } from "axios";

import { fetchXpLedger, renamePet } from "@/api/pets";
import type { PetMe, XPLedgerEntry } from "@/types/pets";
import PetSprite from "./petIcons";

interface Props {
  pet: PetMe;
  onClose: () => void;
  onPetUpdated: (pet: PetMe) => void;
}

export default function PetDetailModal({ pet, onClose, onPetUpdated }: Props) {
  const [name, setName] = useState(pet.name);
  const [renaming, setRenaming] = useState(false);
  const [renameError, setRenameError] = useState<string | null>(null);

  const [entries, setEntries] = useState<XPLedgerEntry[] | null>(null);
  const [ledgerError, setLedgerError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchXpLedger({ grade: pet.grade_number })
      .then((res) => {
        if (!cancelled) setEntries(res.results.slice(0, 10));
      })
      .catch(() => {
        if (!cancelled) setLedgerError(true);
      });
    return () => {
      cancelled = true;
    };
  }, [pet.grade_number]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setRenaming(true);
    setRenameError(null);
    try {
      const updated = await renamePet(name);
      onPetUpdated(updated);
      // Mirror the canonical name back into the input (server may have
      // stripped whitespace).
      setName(updated.name);
    } catch (err) {
      const ax = err as AxiosError<{ name?: string[] }>;
      const msg = ax.response?.data?.name?.[0] ?? "Numele nu a putut fi salvat.";
      setRenameError(msg);
    } finally {
      setRenaming(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-[1100] flex items-center justify-center bg-slate-900/40 p-4"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        className="relative max-h-[90vh] w-full max-w-md overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Închide"
          className="absolute right-3 top-3 rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-4">
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
            <PetSprite kind={pet.pet_kind} size={56} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              {pet.display_name}
            </h2>
            <p className="text-sm text-slate-500">
              Nivel {pet.level} · {pet.kind_display}
            </p>
          </div>
        </div>

        <form onSubmit={submit} className="mt-6">
          <label htmlFor="pet-name" className="text-sm font-medium text-slate-700">
            Schimbă numele
          </label>
          <div className="mt-2 flex gap-2">
            <input
              id="pet-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={30}
              placeholder={pet.display_name}
              className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={renaming}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-60"
            >
              Salvează
            </button>
          </div>
          {renameError && (
            <p className="mt-1.5 text-xs text-red-600">{renameError}</p>
          )}
        </form>

        <section className="mt-6">
          <h3 className="text-sm font-semibold text-slate-700">
            Activitate XP recentă
          </h3>
          {ledgerError ? (
            <p className="mt-2 text-sm text-slate-500">
              Istoricul nu a putut fi încărcat.
            </p>
          ) : entries === null ? (
            <ul className="mt-2 space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <li
                  key={i}
                  className="h-10 rounded-lg bg-slate-100 animate-pulse"
                />
              ))}
            </ul>
          ) : entries.length === 0 ? (
            <p className="mt-2 text-sm text-slate-500">
              Niciun XP înregistrat încă.
            </p>
          ) : (
            <ul className="mt-2 divide-y divide-slate-100 rounded-lg border border-slate-100">
              {entries.map((entry, idx) => (
                <li
                  key={`${entry.granted_at}-${idx}`}
                  className="flex items-center justify-between gap-3 px-3 py-2 text-sm"
                >
                  <div className="min-w-0">
                    <p className="truncate text-slate-800">
                      {entry.source_display}
                    </p>
                    <p className="text-xs text-slate-400">
                      Acum {formatRelative(entry.granted_at)}
                    </p>
                  </div>
                  <span className="shrink-0 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">
                    +{entry.amount} XP
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

function formatRelative(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "—";
  const seconds = Math.max(0, Math.round((Date.now() - then) / 1000));
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.round(hours / 24);
  if (days < 30) return `${days} zile`;
  const months = Math.round(days / 30);
  if (months < 12) return `${months} luni`;
  const years = Math.round(months / 12);
  return `${years} ani`;
}
