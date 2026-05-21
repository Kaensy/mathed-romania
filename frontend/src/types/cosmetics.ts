/**
 * Cosmetic-system types.
 *
 * Mirrors the backend's `build_catalog_state` / equip / avatar shapes so
 * the wardrobe modal can render every catalog entry annotated with the
 * student's owned + equipped state, plus the active avatar/frame/theme
 * combo. The `asset_ref` is an opaque, backend-defined key; renderers
 * pick a visual treatment from it. Locked entries carry a displayable
 * `unlock` requirement so the modal can show "needs 5000 XP" / "needs
 * badge X" without a second API call.
 */

export type CosmeticType = "frame" | "profile_theme" | "avatar";

export type UnlockKind = "xp_threshold" | "achievement" | "quest_reward";

/**
 * Locked-cosmetic unlock requirement. Each non-starter variant carries
 * both a compact `label` (the at-a-glance identifier on the card) and a
 * fuller `description` (the hover/tap tooltip text). For xp_threshold
 * the backend composes the description locally; for achievement and
 * quest_reward it pulls the description from the badge / quest catalog
 * so the wording stays in lockstep with the rest of the UI.
 */
export type UnlockRequirement =
  | { kind: "xp_threshold"; xp: number; description: string }
  | {
      kind: "achievement";
      badge_key: string;
      label: string;
      description: string;
    }
  | {
      kind: "quest_reward";
      quest_slug: string;
      label: string;
      description: string;
    };

export interface CosmeticEntry {
  slug: string;
  type: CosmeticType;
  display_name: string;
  asset_ref: string;
  collection: string;
  owned: boolean;
  equipped: boolean;
  /** Null for owned entries and for starters (nothing to display). */
  unlock: UnlockRequirement | null;
}

export type AvatarSource = "monogram" | "upload" | "preset";

export interface EquippedSnapshot {
  frame: string | null;
  profile_theme: string | null;
  avatar: string | null;
}

/**
 * Full state returned by GET /api/v1/progress/cosmetics/.
 */
export interface CosmeticState {
  cosmetics: CosmeticEntry[];
  equipped: EquippedSnapshot;
  avatar_source: AvatarSource | null;
  avatar_image_url: string | null;
}

/**
 * Returned by POST .../cosmetics/<slug>/equip/ — the post-equip snapshot
 * the client patches into local state. Same avatar fields as the list
 * endpoint so a single helper handles both.
 */
export interface CosmeticEquipResponse {
  equipped: EquippedSnapshot;
  avatar_source: AvatarSource | null;
  avatar_image_url: string | null;
}

/**
 * Returned by POST .../avatar/upload/ and POST .../avatar/source/.
 * Shape is identical for both — `_avatar_state` on the backend.
 */
export interface AvatarStateResponse {
  avatar_source: AvatarSource | null;
  avatar_image_url: string | null;
}

/**
 * Compact display dict surfaced in every endpoint's
 * `newly_unlocked_cosmetics` array — what the toast (Phase 6) will
 * render. Matches `serialize_cosmetics` on the backend.
 */
export interface CosmeticUnlock {
  slug: string;
  type: CosmeticType;
  display_name: string;
  asset_ref: string;
  collection: string;
}
