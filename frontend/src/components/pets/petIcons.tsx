/**
 * Pet sprite registry — placeholder Game-Icons.net-style SVGs themed
 * via CSS (`currentColor`). Real per-species art lands later, likely
 * alongside Block 12 cosmetics.
 *
 * To swap in real art later: replace the JSX path with the new SVG
 * markup. Keep `viewBox="0 0 512 512"` so consumers don't need to
 * re-do sizing logic. The icons render with `currentColor` so callers
 * can theme via Tailwind text utilities, mirroring badge icons.
 */
import type { ComponentType, SVGProps } from "react";

interface PetSpriteProps extends SVGProps<SVGSVGElement> {
  kind: string;
  size?: number;
}

function WolfPup(props: SVGProps<SVGSVGElement>) {
  // Stylized wolf-pup silhouette. Placeholder; swap with a real
  // Game-Icons.net "wolf head" path (e.g. lorc/wolf-head.svg) when
  // licensing is finalized.
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 512 512"
      fill="currentColor"
      aria-hidden
      {...props}
    >
      <path d="M256 64L120 168l32 24-24 80 56-16 16 64 56-32 56 32 16-64 56 16-24-80 32-24z" />
      <circle cx="208" cy="232" r="14" fill="#fff" />
      <circle cx="304" cy="232" r="14" fill="#fff" />
      <path d="M232 304q24 24 48 0" stroke="#fff" strokeWidth="10" strokeLinecap="round" fill="none" />
      <path d="M256 360v60" stroke="currentColor" strokeWidth="32" strokeLinecap="round" />
    </svg>
  );
}

const SPRITES: Record<string, ComponentType<SVGProps<SVGSVGElement>>> = {
  pui_de_lup: WolfPup,
};

export default function PetSprite({ kind, size = 96, ...rest }: PetSpriteProps) {
  const Sprite = SPRITES[kind] ?? WolfPup;
  return <Sprite width={size} height={size} {...rest} />;
}
