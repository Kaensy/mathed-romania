import api from "@/api/client";
import type { PetMe, XPLedgerResponse } from "@/types/pets";

/** GET /api/v1/pets/me/ — current-grade pet for the authenticated student. */
export async function fetchPetMe(): Promise<PetMe> {
  const res = await api.get<PetMe>("/pets/me/");
  return res.data;
}

/**
 * PATCH /api/v1/pets/me/ — set or clear the pet's custom name.
 *
 * Backend trims whitespace and validates: max 30 Unicode letters,
 * spaces, and hyphens. A blank string clears to the species default.
 */
export async function renamePet(name: string): Promise<PetMe> {
  const res = await api.patch<PetMe>("/pets/me/", { name });
  return res.data;
}

interface FetchLedgerArgs {
  page?: number;
  /** Grade number (5-8); omit for all grades. */
  grade?: number;
}

/**
 * GET /api/v1/progress/xp/ledger/?page=N&grade=N — paginated XP grant
 * history, newest first, page size 50.
 */
export async function fetchXpLedger(
  args: FetchLedgerArgs = {},
): Promise<XPLedgerResponse> {
  const params: Record<string, string | number> = {};
  if (args.page !== undefined) params.page = args.page;
  if (args.grade !== undefined) params.grade = args.grade;
  const res = await api.get<XPLedgerResponse>("/progress/xp/ledger/", { params });
  return res.data;
}
