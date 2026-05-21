/**
 * Renderer registry for cosmetic asset refs.
 *
 * The backend ships an opaque `asset_ref` like `"frame/iron"` or
 * `"avatar/squire"`. The wardrobe modal needs to turn each ref into
 * something visible — Phase 5 uses placeholder visuals (Tailwind ring
 * gradients, lucide icons) because the production art lands later.
 * Keeping the lookup in one module means swapping a placeholder for a
 * real asset is a one-line change.
 *
 * The maps are keyed by the full `asset_ref` so an off-by-one (legacy
 * "iron" vs "frame/iron") fails loudly with the fallback rather than
 * silently picking the wrong visual.
 */
import {
  BookOpenText,
  Crown,
  Flame,
  Leaf,
  Lock,
  Mountain,
  Shield,
  Sparkles,
  Star,
  Sword,
  Swords,
  Target,
  TreeDeciduous,
  UserCog,
  UserRound,
  UserRoundSearch,
} from "lucide-react";
import type { ReactNode } from "react";

import type { CosmeticType } from "@/types/cosmetics";

// ─── Frames ─────────────────────────────────────────────────────────────────
// Rendered as a ring around the avatar circle. We pick `ring` classes
// (rather than `border`) so the ring lives outside the box and never
// shifts the avatar's content area. The bg-clip gradients on the
// premium frames are applied to a wrapper div behind the avatar.

interface FrameStyle {
  /** Tailwind classes for the outer wrapper (ring / gradient / etc). */
  wrapperClass: string;
  /** Optional small badge anchored to the top of the frame. */
  decoration?: ReactNode;
}

const FRAME_STYLES: Record<string, FrameStyle> = {
  "frame/plain": {
    wrapperClass: "ring-1 ring-gray-300",
  },
  "frame/rounded": {
    wrapperClass: "ring-2 ring-gray-400",
  },
  "frame/dotted": {
    wrapperClass: "ring-2 ring-dotted ring-gray-400",
  },
  "frame/iron": {
    wrapperClass: "ring-4 ring-slate-400 shadow-inner",
  },
  "frame/bronze": {
    wrapperClass: "ring-4 ring-amber-700",
  },
  "frame/silver": {
    wrapperClass:
      "ring-4 ring-slate-300 shadow-[0_0_0_2px_white,0_0_0_6px_rgb(148,163,184)]",
  },
  "frame/gold": {
    wrapperClass:
      "ring-4 ring-yellow-400 shadow-[0_0_0_2px_white,0_0_0_6px_rgb(202,138,4)]",
  },
  "frame/ornate": {
    wrapperClass:
      "ring-[6px] ring-yellow-500 shadow-[0_0_0_3px_white,0_0_0_8px_rgb(202,138,4),0_0_12px_2px_rgb(250,204,21)]",
    decoration: (
      <Sparkles
        className="absolute -top-3 left-1/2 -translate-x-1/2 h-5 w-5 text-yellow-500"
        aria-hidden
      />
    ),
  },
  "frame/laurel": {
    wrapperClass: "ring-4 ring-emerald-400",
    decoration: (
      <Leaf
        className="absolute -top-2 -left-2 h-5 w-5 text-emerald-600 rotate-[-30deg]"
        aria-hidden
      />
    ),
  },
  "frame/crown": {
    wrapperClass: "ring-4 ring-yellow-300",
    decoration: (
      <Crown
        className="absolute -top-4 left-1/2 -translate-x-1/2 h-5 w-5 text-yellow-500"
        aria-hidden
      />
    ),
  },
  "frame/crossed_swords": {
    wrapperClass: "ring-4 ring-rose-500",
    decoration: (
      <Swords
        className="absolute -top-3 left-1/2 -translate-x-1/2 h-5 w-5 text-rose-600"
        aria-hidden
      />
    ),
  },
  "frame/quest_hunter": {
    wrapperClass: "ring-4 ring-purple-500",
    decoration: (
      <Target
        className="absolute -top-3 left-1/2 -translate-x-1/2 h-5 w-5 text-purple-600"
        aria-hidden
      />
    ),
  },
  "frame/whetstone": {
    wrapperClass: "ring-4 ring-stone-500",
    decoration: (
      <Mountain
        className="absolute -top-3 left-1/2 -translate-x-1/2 h-5 w-5 text-stone-600"
        aria-hidden
      />
    ),
  },
};

const FRAME_FALLBACK: FrameStyle = { wrapperClass: "ring-1 ring-gray-200" };

export function frameStyleFor(assetRef: string | null | undefined): FrameStyle {
  if (!assetRef) return FRAME_FALLBACK;
  return FRAME_STYLES[assetRef] ?? FRAME_FALLBACK;
}

// ─── Themes ─────────────────────────────────────────────────────────────────
// A theme has two jobs:
//   (1) Drive the actual profile-page surface when equipped — that
//       background is the live preview, visible through the modal dim.
//       The `pageClass` therefore picks saturated enough gradients that
//       a 40% black dim still leaves the family unambiguously visible.
//   (2) Render a meaningful card preview inside the wardrobe — a real
//       multi-swatch palette block, not a single neutral line, so the
//       student can tell the six themes apart at a glance even when
//       only one of them is equipped at a time.

interface ThemeStyle {
  /** Background classes applied to the page surface when equipped. */
  pageClass: string;
  /** Accent color for theme-tinted UI (e.g. the modal header). */
  accentClass: string;
  /**
   * 3-stop palette swatch shown in the wardrobe card. Each entry is a
   * Tailwind background class; the swatch renders them as adjacent
   * vertical stripes (left → right). Three is enough to distinguish
   * "warm cream + tan", "warm orange + rose + amber", etc. without
   * crowding a 60×60 card tile.
   */
  swatch: [string, string, string];
}

const THEME_STYLES: Record<string, ThemeStyle> = {
  "theme/parchment": {
    pageClass: "bg-gradient-to-b from-amber-100 to-amber-200",
    accentClass: "text-amber-700",
    swatch: ["bg-amber-50", "bg-amber-200", "bg-amber-400"],
  },
  "theme/castle_stone": {
    pageClass: "bg-gradient-to-b from-slate-300 to-slate-400",
    accentClass: "text-slate-700",
    swatch: ["bg-slate-200", "bg-slate-400", "bg-slate-600"],
  },
  "theme/old_library": {
    pageClass: "bg-gradient-to-b from-amber-300 via-amber-500 to-amber-700",
    accentClass: "text-amber-900",
    swatch: ["bg-amber-200", "bg-amber-600", "bg-amber-900"],
  },
  "theme/campfire": {
    pageClass:
      "bg-gradient-to-b from-orange-300 via-orange-500 to-red-600",
    accentClass: "text-orange-700",
    swatch: ["bg-amber-300", "bg-orange-500", "bg-red-600"],
  },
  "theme/companions_den": {
    pageClass:
      "bg-gradient-to-b from-emerald-300 via-emerald-500 to-teal-700",
    accentClass: "text-emerald-700",
    swatch: ["bg-lime-300", "bg-emerald-500", "bg-stone-700"],
  },
  "theme/throne_room": {
    pageClass:
      "bg-gradient-to-br from-purple-400 via-purple-600 to-yellow-500",
    accentClass: "text-purple-700",
    swatch: ["bg-purple-400", "bg-purple-700", "bg-yellow-400"],
  },
};

const THEME_FALLBACK: ThemeStyle = {
  pageClass: "bg-gray-50",
  accentClass: "text-indigo-700",
  swatch: ["bg-gray-100", "bg-gray-200", "bg-gray-300"],
};

export function themeStyleFor(assetRef: string | null | undefined): ThemeStyle {
  if (!assetRef) return THEME_FALLBACK;
  return THEME_STYLES[assetRef] ?? THEME_FALLBACK;
}

// ─── Avatars ────────────────────────────────────────────────────────────────
// One placeholder lucide icon + tinted background per preset avatar.
// The renderer below paints the icon inside the existing avatar circle
// so the frame + avatar composite layout stays consistent across the
// three avatar sources (monogram, upload, preset).

interface AvatarStyle {
  icon: ReactNode;
  bgClass: string;
}

const AVATAR_STYLES: Record<string, AvatarStyle> = {
  "avatar/apprentice_boy": {
    icon: <UserRound aria-hidden />,
    bgClass: "bg-blue-100 text-blue-700",
  },
  "avatar/apprentice_girl": {
    icon: <UserRound aria-hidden />,
    bgClass: "bg-pink-100 text-pink-700",
  },
  "avatar/squire": {
    icon: <Shield aria-hidden />,
    bgClass: "bg-slate-200 text-slate-700",
  },
  "avatar/ranger": {
    icon: <TreeDeciduous aria-hidden />,
    bgClass: "bg-emerald-100 text-emerald-700",
  },
  "avatar/champion": {
    icon: <Star aria-hidden />,
    bgClass: "bg-amber-100 text-amber-700",
  },
  "avatar/beast_tamer": {
    icon: <Flame aria-hidden />,
    bgClass: "bg-orange-100 text-orange-700",
  },
  "avatar/steady_learner": {
    icon: <BookOpenText aria-hidden />,
    bgClass: "bg-indigo-100 text-indigo-700",
  },
  "avatar/test_collector": {
    icon: <Sword aria-hidden />,
    bgClass: "bg-rose-100 text-rose-700",
  },
};

const AVATAR_FALLBACK: AvatarStyle = {
  icon: <UserCog aria-hidden />,
  bgClass: "bg-gray-100 text-gray-600",
};

export function avatarStyleFor(
  assetRef: string | null | undefined,
): AvatarStyle {
  if (!assetRef) return AVATAR_FALLBACK;
  return AVATAR_STYLES[assetRef] ?? AVATAR_FALLBACK;
}

// ─── Per-tab icon (used in tab headers and lock overlays) ───────────────────

const TYPE_ICONS: Record<CosmeticType, ReactNode> = {
  frame: <UserRoundSearch className="h-4 w-4" aria-hidden />,
  profile_theme: <Sparkles className="h-4 w-4" aria-hidden />,
  avatar: <UserRound className="h-4 w-4" aria-hidden />,
};

export function iconForType(type: CosmeticType): ReactNode {
  return TYPE_ICONS[type];
}

export { Lock };
