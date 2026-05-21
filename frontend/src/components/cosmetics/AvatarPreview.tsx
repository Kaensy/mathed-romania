/**
 * Composite avatar renderer — one circle, one frame.
 *
 * Resolves the three avatar sources (monogram initials, uploaded
 * image, equipped preset) into a single visual and overlays the
 * equipped frame as a ring around it. Reused for the profile-page
 * avatar entry and the wardrobe modal's persistent preview.
 *
 * Phase 5 keeps the renderer here — Phase 6 wires it into the
 * dashboard and other surfaces, at which point this component is the
 * single source of truth.
 */
import { avatarStyleFor, frameStyleFor } from "./assetRegistry";

import type { AvatarSource, CosmeticEntry } from "@/types/cosmetics";

interface AvatarPreviewProps {
  size?: "sm" | "md" | "lg";
  /** Source the displayed avatar resolves from. */
  avatarSource: AvatarSource | null;
  /** URL of the stored upload, or null. Required when source is "upload". */
  avatarImageUrl: string | null;
  /** asset_ref of the equipped preset avatar, or null. Required for "preset". */
  presetAssetRef: string | null;
  /** asset_ref of the equipped frame, or null for no frame. */
  frameAssetRef: string | null;
  /** Initials for the monogram fallback. */
  initials: string;
}

const SIZE_CLASS = {
  sm: "h-10 w-10 text-xs",
  md: "h-14 w-14 text-base",
  lg: "h-24 w-24 text-2xl",
} as const;

const ICON_SIZE_CLASS = {
  sm: "h-6 w-6",
  md: "h-8 w-8",
  lg: "h-12 w-12",
} as const;

export default function AvatarPreview({
  size = "md",
  avatarSource,
  avatarImageUrl,
  presetAssetRef,
  frameAssetRef,
  initials,
}: AvatarPreviewProps) {
  const frame = frameStyleFor(frameAssetRef);
  const sizeClass = SIZE_CLASS[size];
  const iconClass = ICON_SIZE_CLASS[size];

  // Resolve the inner circle by source. Falling back to the monogram
  // when the source declares an upload/preset but the data is missing
  // keeps the surface stable when state lags by a tick.
  let inner;
  if (avatarSource === "upload" && avatarImageUrl) {
    inner = (
      <img
        src={avatarImageUrl}
        alt="Avatar"
        className={`${sizeClass} rounded-full object-cover`}
      />
    );
  } else if (avatarSource === "preset" && presetAssetRef) {
    const style = avatarStyleFor(presetAssetRef);
    inner = (
      <div
        className={`${sizeClass} rounded-full flex items-center justify-center ${style.bgClass}`}
      >
        <div className={iconClass}>{style.icon}</div>
      </div>
    );
  } else {
    inner = (
      <div
        className={`${sizeClass} rounded-full bg-indigo-100 flex items-center justify-center`}
      >
        <span className="font-bold text-indigo-700">{initials}</span>
      </div>
    );
  }

  return (
    <div className={`relative inline-flex ${frame.wrapperClass} rounded-full`}>
      {inner}
      {frame.decoration}
    </div>
  );
}

// ─── Convenience: build preview props from a cosmetic state snapshot ─────────

export interface PreviewSelection {
  avatarSource: AvatarSource | null;
  avatarImageUrl: string | null;
  presetAssetRef: string | null;
  frameAssetRef: string | null;
}

/**
 * Derive the four preview props from the cosmetic-state catalog + the
 * equipped map. Keeps the resolution logic (slug → asset_ref) in one
 * place so multiple call sites can't drift.
 */
export function buildPreviewSelection(
  cosmetics: CosmeticEntry[],
  equipped: { frame: string | null; profile_theme: string | null; avatar: string | null },
  avatarSource: AvatarSource | null,
  avatarImageUrl: string | null,
): PreviewSelection {
  const assetRefFor = (slug: string | null): string | null => {
    if (!slug) return null;
    const entry = cosmetics.find((c) => c.slug === slug);
    return entry?.asset_ref ?? null;
  };
  return {
    avatarSource,
    avatarImageUrl,
    presetAssetRef: assetRefFor(equipped.avatar),
    frameAssetRef: assetRefFor(equipped.frame),
  };
}
