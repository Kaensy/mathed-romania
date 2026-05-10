import { useLevelUp } from "@/contexts/LevelUpContext";
import PetSprite from "./petIcons";

interface Props {
  /** Pet display name (e.g. "Lupul"). Falls back to a generic phrase. */
  displayName?: string;
  /** Pet kind slug for sprite selection. */
  kind?: string;
}

/**
 * Full-screen level-up celebration. Reads the active level from
 * LevelUpContext; auto-dismisses on a 3.5s timer the provider owns.
 * Click anywhere on the backdrop to dismiss early.
 */
export default function LevelUpCelebration({ displayName, kind }: Props) {
  const { newLevel, dismiss } = useLevelUp();
  if (newLevel === null) return null;

  const subline = displayName
    ? `${displayName} a crescut!`
    : "Companion-ul tău a crescut!";

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Nivel ${newLevel}`}
      onClick={dismiss}
      className="fixed inset-0 z-[1200] flex cursor-pointer items-center justify-center bg-slate-900/60 animate-level-up-backdrop"
    >
      <div className="flex flex-col items-center gap-4 px-6 text-center animate-level-up-pop">
        <div className="flex h-32 w-32 items-center justify-center rounded-full bg-amber-100 text-amber-600 shadow-2xl ring-4 ring-amber-300">
          <PetSprite kind={kind ?? "pui_de_lup"} size={80} />
        </div>
        <div className="rounded-full bg-amber-500 px-6 py-2 text-2xl font-bold text-white shadow-lg ring-2 ring-amber-300">
          Nivel {newLevel}!
        </div>
        <p className="text-lg font-medium text-white drop-shadow-md">
          {subline}
        </p>
      </div>
    </div>
  );
}
