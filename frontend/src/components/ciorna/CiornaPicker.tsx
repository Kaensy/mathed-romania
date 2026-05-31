/**
 * Ciornă picker — grid of registered components.
 *
 * Lives inside the canvas's "+" palette (Phase 3a). Selecting a card adds a
 * placed component to the canvas. The Phase-2 placeholder smart-scan input
 * was removed in Phase 4 — smart scan now runs against the cell-text layer
 * on Enter, so the palette is just the explicit-pick path.
 */
import { useEffect, useRef } from "react";

import { CIORNA_COMPONENTS, type CiornaComponent } from "./registry";

interface Props {
  /** Fired with the registered component's id when a card is selected. */
  onSelect: (id: string) => void;
}

export default function CiornaPicker({ onSelect }: Props) {
  const firstCardRef = useRef<HTMLButtonElement>(null);

  // Focus the first card whenever the picker mounts — covers the palette
  // popover opening each time, so keyboard users land on a focusable target.
  useEffect(() => {
    firstCardRef.current?.focus();
  }, []);

  return (
    <div>
      <p className="mb-2 text-xs font-medium text-amber-900/70">
        Adaugă o componentă
      </p>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {CIORNA_COMPONENTS.map((c, i) => (
          <PickerCard
            key={c.id}
            component={c}
            onSelect={() => onSelect(c.id)}
            buttonRef={i === 0 ? firstCardRef : undefined}
          />
        ))}
      </div>
    </div>
  );
}

function PickerCard({
  component,
  onSelect,
  buttonRef,
}: {
  component: CiornaComponent;
  onSelect: () => void;
  buttonRef?: React.RefObject<HTMLButtonElement | null>;
}) {
  const Icon = component.icon;
  return (
    <button
      ref={buttonRef}
      type="button"
      onClick={onSelect}
      className="flex min-h-[88px] flex-col items-center justify-center gap-2
        rounded-xl border-2 border-amber-200 bg-amber-50/60 p-3 text-amber-900
        transition-colors hover:border-amber-400 hover:bg-amber-100
        focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-1"
    >
      <Icon className="h-6 w-6" aria-hidden="true" />
      <span className="text-sm font-medium">{component.label}</span>
    </button>
  );
}
