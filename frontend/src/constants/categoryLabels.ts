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
  // 1.1 — Mulțimea numerelor naturale
  number_to_words:    "Scriere în cuvinte",
  words_to_number:    "Scriere în cifre",
  counting_interval:  "Numărare în interval",
  digit_rules:        "Determinare cifre după reguli",
  canonical_form:     "Formă canonică",

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

    // 1.8 - Puteri
   power_notation:             "Notația puterii",
   power_compute:              "Calcul cu puteri",
   power_rules_simplify:       "Scriere ca o singură putere",
   power_common_factor:        "Factor comun cu puteri",
   find_x_powers:              "Aflarea necunoscutei (puteri)",
   power_last_digit:           "Ultima cifră a unei puteri",
   power_sum_telescope:        "Sume de puteri consecutive",
   power_compare:              "Compararea puterilor",
   power_order:                "Ordonarea puterilor",
   perfect_square_identify:    "Pătrate perfecte — recunoaștere",
   perfect_square_between:     "Pătrate perfecte consecutive",

    // 1.9 - Baze de numerație
    convert_to_base10:    "Conversie spre baza 10",
    convert_from_base10:  "Conversie din baza 10",
    mixed_base_compute:   "Calcul cu baze diferite",

  // 1.10 - Ordinea operatiilor
    order_of_ops_basic:   "Ordinea operațiilor — fără paranteze",
    order_of_ops_parens:  "Ordinea operațiilor — cu paranteze",
    order_of_ops_nested:  "Ordinea operațiilor — paranteze imbricate",
};
