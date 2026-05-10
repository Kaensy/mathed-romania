// ─── Pet types ────────────────────────────────────────────────────────────────

/** Output of GET /api/v1/pets/me/. Mirrors backend PetSerializer. */
export interface PetMe {
  id: number;
  pet_kind: string;
  kind_display: string;
  name: string;
  display_name: string;
  pet_xp: number;
  level: number;
  xp_to_next_level: number;
  grade_number: number;
  total_xp: number;
}

/** Validation error shape for PATCH /api/v1/pets/me/. */
export interface PetRenameError {
  name?: string[];
}

// ─── XP ledger types ──────────────────────────────────────────────────────────

export interface XPLedgerEntry {
  source: string;
  source_display: string;
  amount: number;
  granted_at: string; // ISO 8601
  grade_number: number;
}

/** DRF PageNumberPagination envelope around XPLedgerEntry rows. */
export interface XPLedgerResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: XPLedgerEntry[];
}
