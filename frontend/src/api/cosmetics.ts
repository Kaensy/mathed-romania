import api from "@/api/client";
import type {
  AvatarSource,
  AvatarStateResponse,
  CosmeticEquipResponse,
  CosmeticState,
} from "@/types/cosmetics";

/**
 * GET /api/v1/progress/cosmetics/ — full catalog annotated with the
 * student's owned + equipped state, plus equipped snapshot and avatar
 * block. Single read the wardrobe modal depends on.
 */
export async function getCosmetics(): Promise<CosmeticState> {
  const res = await api.get<CosmeticState>("/progress/cosmetics/");
  return res.data;
}

/**
 * POST /api/v1/progress/cosmetics/<slug>/equip/ — equip an owned
 * cosmetic. Returns the post-equip snapshot (equipped map + avatar
 * block) the caller patches into local state. Equipping an avatar-type
 * cosmetic also flips `avatar_source` to PRESET (the backend does this
 * atomically with the equip).
 */
export async function equipCosmetic(
  slug: string,
): Promise<CosmeticEquipResponse> {
  const res = await api.post<CosmeticEquipResponse>(
    `/progress/cosmetics/${slug}/equip/`,
  );
  return res.data;
}

/**
 * POST /api/v1/progress/avatar/upload/ (multipart, field `avatar`) —
 * validate + normalise the uploaded file (Pillow, 256×256 JPEG, metadata
 * stripped). On success the source is flipped to UPLOAD; returns the
 * post-upload avatar block.
 */
export async function uploadAvatar(
  file: File,
): Promise<AvatarStateResponse> {
  const formData = new FormData();
  formData.append("avatar", file);
  const res = await api.post<AvatarStateResponse>(
    "/progress/avatar/upload/",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return res.data;
}

/**
 * POST /api/v1/progress/avatar/source/ — switch which of the three
 * sources resolves the displayed avatar. MONOGRAM is always reachable;
 * UPLOAD requires a stored image; PRESET requires an equipped avatar.
 */
export async function setAvatarSource(
  source: AvatarSource,
): Promise<AvatarStateResponse> {
  const res = await api.post<AvatarStateResponse>(
    "/progress/avatar/source/",
    { source },
  );
  return res.data;
}
