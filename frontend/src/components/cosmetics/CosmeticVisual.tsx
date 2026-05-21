/**
 * Per-cosmetic visual tile, shared by the wardrobe modal grid and the
 * unlock toast.
 *
 * Each cosmetic type has its own tile shape:
 *   - frame         → empty circle wearing the frame's ring + decoration
 *   - profile_theme → multi-stripe palette swatch
 *   - avatar        → tinted circle with the preset's icon
 *
 * The size knob accepts a small set of Tailwind size pairs so the same
 * component can render at "modal grid" (~56px) or "toast" (~40px)
 * without callers having to know the underlying classes.
 */
import {
  avatarStyleFor,
  frameStyleFor,
  themeStyleFor,
} from "./assetRegistry";

import type { CosmeticType } from "@/types/cosmetics";

export type CosmeticVisualSize = "sm" | "md";

interface CosmeticVisualProps {
  type: CosmeticType;
  assetRef: string;
  size?: CosmeticVisualSize;
}

const SIZE_CLASS: Record<
  CosmeticVisualSize,
  { circle: string; inner: string; iconBox: string; themeHeight: string }
> = {
  sm: {
    circle: "h-10 w-10",
    inner: "h-8 w-8",
    iconBox: "h-5 w-5",
    themeHeight: "h-10",
  },
  md: {
    circle: "h-14 w-14",
    inner: "h-12 w-12",
    iconBox: "h-7 w-7",
    themeHeight: "h-14",
  },
};

export default function CosmeticVisual({
  type,
  assetRef,
  size = "md",
}: CosmeticVisualProps) {
  const sizes = SIZE_CLASS[size];

  if (type === "frame") {
    const style = frameStyleFor(assetRef);
    return (
      <div
        className={`relative inline-flex rounded-full ${style.wrapperClass}`}
      >
        <div className={`${sizes.inner} rounded-full bg-gray-100`} />
        {style.decoration}
      </div>
    );
  }

  if (type === "profile_theme") {
    const style = themeStyleFor(assetRef);
    return (
      <div
        className={`${sizes.themeHeight} w-full rounded-lg overflow-hidden border border-black/5 flex`}
      >
        {style.swatch.map((bg, i) => (
          <div key={i} className={`flex-1 ${bg}`} />
        ))}
      </div>
    );
  }

  const style = avatarStyleFor(assetRef);
  return (
    <div
      className={`${sizes.circle} rounded-full flex items-center justify-center ${style.bgClass}`}
    >
      <div className={sizes.iconBox}>{style.icon}</div>
    </div>
  );
}
