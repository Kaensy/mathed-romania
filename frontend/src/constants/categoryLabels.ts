/**
 * Maps exercise category slugs (stored in DB) to Romanian display labels.
 *
 * Used by ExerciseHubPage, future overview pages, and any other UI that
 * needs to present category names to students.
 *
 * Fallback: if a slug is missing from this map, the raw slug or backend
 * label is displayed instead.
 */

export const CATEGORY_LABELS: Record<string, string> = {
  // ── Lesson 1.1 — Mulțimea numerelor naturale ──────────────────────────────
  number_to_words:    "Scriere în cuvinte",
  words_to_number:    "Scriere în cifre",
  counting_interval:  "Numărare în interval",
  digit_rules:        "Determinare cifre după reguli",
  canonical_form:     "Formă canonică",

  // ── Add further lessons below as their exercises are entered ──────────────
  // 1.2
  comparing_numbers:  "Comparare numere",
  ordering_numbers:   "Ordonare numere",

  // 1.3
  rounding:           "Rotunjire",

  // 1.4
  addition:           "Adunare",
  arithmetic_sequence:"Șir aritmetic",

  // 1.5
  subtraction:        "Scădere",

  // 1.6
  multiplication:     "Înmulțire",
  last_digit:         "Ultima cifră",
  distributivity:     "Distributivitate",
  multiplication_compute: "Calcul cu înmulțiri",
  find_x_multiplication: "Aflarea necunoscutei",
  common_factor: "Factor comun",

  // 1.7
  division_exact:     "Împărțire exactă",
  division_remainder: "Împărțire cu rest",
  division_compute: "Calcul cu împărțiri",
  find_x_division: "Aflarea necunoscutei (împărțire)",
  division_remainder_compute: "Calcul cu rest",
  find_from_division_theorem: "Teorema împărțirii cu rest",

  // 1.8
  powers:             "Puteri",
  power_rules:        "Reguli de calcul puteri",
  perfect_squares:    "Pătrate perfecte",

  // 1.9
  base_conversion:    "Conversie baze",
  binary:             "Binar",

  // 1.10
  order_of_operations: "Ordinea operațiilor",
};
