# Lesson Block Schema

Every lesson's `blocks` field is a JSON array of typed block objects.
Blocks are rendered top-to-bottom by the lesson viewer.

Inline math within any `text` field: wrap in `$...$`
Example: `"Numărul $x^2 + 1$ este întotdeauna pozitiv."`

---

## Block Types

### `paragraph`
Plain text paragraph with optional inline math.
```json
{
  "type": "paragraph",
  "text": "Numerele naturale sunt $0, 1, 2, 3, ...$"
}
```

---

### `definition_box`
Formal definition — bordered, visually distinct.
```json
{
  "type": "definition_box",
  "title": "Definiție",
  "text": "Mulțimea numerelor naturale este $\\mathbb{N} = \\{0, 1, 2, 3, ...\\}$"
}
```
`title` is optional, defaults to "Definiție".

---

### `observation_box`
Secondary info, tips, edge cases — "Observații".
```json
{
  "type": "observation_box",
  "title": "Observație",
  "text": "Numărul $0$ este cel mai mic număr natural."
}
```
`title` is optional, defaults to "Observație".

---

### `formula_card`
Prominent formula display — visually memorable.
```json
{
  "type": "formula_card",
  "title": "Suma lui Gauss",
  "latex": "S = \\frac{n(n+1)}{2}"
}
```
`title` is optional.

---

### `real_world_box`
Opening hook connecting math to real life.
```json
{
  "type": "real_world_box",
  "text": "Dacă școala ta are 1204 elevi, poți spune că are aproximativ 1000 de elevi."
}
```

---

### `warning_box`
Common mistakes — red/orange accent.
```json
{
  "type": "warning_box",
  "title": "Atenție!",
  "text": "Nu confunda $a^0 = 1$ cu $0^0$, care este o formă nedeterminată."
}
```
`title` is optional, defaults to "Atenție!".

---

### `block_equation`
Standalone centered KaTeX expression.
```json
{
  "type": "block_equation",
  "latex": "a = b \\cdot c + r, \\quad 0 \\leq r < b"
}
```

---

### `worked_example`
Problem with step-by-step solution (single method).
```json
{
  "type": "worked_example",
  "problem": "Calculează suma $1 + 2 + 3 + ... + 100$.",
  "steps": [
    {
      "explanation": "Folosim formula lui Gauss cu $n = 100$:",
      "latex": "S = \\frac{n(n+1)}{2} = \\frac{100 \\cdot 101}{2}"
    },
    {
      "explanation": "Calculăm:",
      "latex": "S = \\frac{10100}{2} = 5050"
    }
  ]
}
```
Each step has `explanation` (text with optional inline math) and optional `latex` (block equation for that step).

---

### `worked_example_multi`
Same problem solved two ways — tabbed display.
```json
{
  "type": "worked_example_multi",
  "problem": "Calculează $3 \\times (4 + 5)$.",
  "methods": [
    {
      "title": "Metoda 1 — paranteze mai întâi",
      "steps": [
        { "explanation": "Calculăm paranteza:", "latex": "4 + 5 = 9" },
        { "explanation": "Înmulțim:", "latex": "3 \\times 9 = 27" }
      ]
    },
    {
      "title": "Metoda 2 — distributivitate",
      "steps": [
        { "explanation": "Aplicăm proprietatea distributivă:", "latex": "3 \\times 4 + 3 \\times 5" },
        { "explanation": "Calculăm:", "latex": "12 + 15 = 27" }
      ]
    }
  ]
}
```

---

### `properties_list`
Named properties with symbolic form and numeric examples.
```json
{
  "type": "properties_list",
  "title": "Proprietățile adunării",
  "properties": [
    {
      "name": "Comutativitate",
      "symbolic": "a + b = b + a",
      "example": "$3 + 5 = 5 + 3 = 8$"
    },
    {
      "name": "Asociativitate",
      "symbolic": "(a + b) + c = a + (b + c)",
      "example": "$(1 + 2) + 3 = 1 + (2 + 3) = 6$"
    }
  ]
}
```
`title` is optional.

---

### `summary_table`
Pre-filled reference table.
```json
{
  "type": "summary_table",
  "title": "Tabla cifrelor de la puterea 2",
  "headers": ["Cifra $a$", "Ultimele cifre ale puterilor lui $a$", "Perioada"],
  "rows": [
    ["0", "0", "1"],
    ["1", "1", "1"],
    ["2", "2, 4, 8, 6", "4"]
  ]
}
```
`title` is optional. All cell values are strings (can contain inline `$...$`).

---

### `symbol_reference`
Compact icon-forward reference panel showing math symbols with Romanian names. Reusable for comparison symbols, operations, set notation, etc.
```json
{
  "type": "symbol_reference",
  "title": "Simboluri de comparare",
  "symbols": [
    { "symbol": "<", "name": "mai mic decât" },
    { "symbol": "\\leq", "name": "mai mic sau egal" },
    { "symbol": ">", "name": "mai mare decât" },
    { "symbol": "\\geq", "name": "mai mare sau egal" },
    { "symbol": "=", "name": "egal" },
    { "symbol": "\\neq", "name": "diferit de" }
  ]
}
```
`title` is optional. Each entry has `symbol` (raw LaTeX — NOT `$`-wrapped, passed directly to `BlockMath`) and `name` (Romanian label, supports inline `$...$`).

---

### `collapsible`
Expandable "want to know why?" section for advanced proofs.
```json
{
  "type": "collapsible",
  "title": "Vrei să știi de ce funcționează formula lui Gauss?",
  "blocks": [
    {
      "type": "paragraph",
      "text": "Scriem suma de două ori, o dată în ordine crescătoare și o dată în ordine descrescătoare..."
    },
    {
      "type": "block_equation",
      "latex": "2S = n(n+1) \\Rightarrow S = \\frac{n(n+1)}{2}"
    }
  ]
}
```
`blocks` is a nested array of any block types (except another `collapsible`).

---

### `interactive`
Placeholder for future interactive components. Renders a stub during Phase 3.
```json
{
  "type": "interactive",
  "component": "column_arithmetic",
  "config": {
    "operation": "addition",
    "operands": [3475, 2619]
  }
}
```

Available `component` values (to be implemented in Phase 4+):
- `column_arithmetic` — animated carrying/borrowing
- `long_division` — step-by-step division layout
- `number_line` — zoomable with point placement
- `expression_evaluator` — order of operations interactive
- `base_converter` — base 10 ↔ base 2
- `place_value_table` — interactive digit decomposition
- `last_digit_explorer` — power cycle animation
- `comparison_sorter` — drag-to-order numbers

---

## Full Example — Lesson 1.1 (excerpt)

```json
[
  {
    "type": "real_world_box",
    "text": "Știai că în România sunt peste 19.000.000 de locuitori? Cum scriem și citim un număr atât de mare?"
  },
  {
    "type": "paragraph",
    "text": "Pentru a scrie și citi numerele naturale mari, le grupăm cifrele în clase."
  },
  {
    "type": "definition_box",
    "title": "Definiție",
    "text": "O clasă este un grup de trei cifre consecutive, numărând de la dreapta spre stânga."
  },
  {
    "type": "interactive",
    "component": "place_value_table",
    "config": { "number": 19234567 }
  },
  {
    "type": "worked_example",
    "problem": "Scrie în cifre numărul: douăsprezece milioane trei sute patruzeci și cinci de mii șase sute șaptezeci și opt.",
    "steps": [
      { "explanation": "Identificăm clasa milioanelor: doisprezece milioane", "latex": "12 \\cdot 10^6" },
      { "explanation": "Clasa miilor: trei sute patruzeci și cinci de mii", "latex": "345 \\cdot 10^3" },
      { "explanation": "Clasa unităților: șase sute șaptezeci și opt", "latex": "678" },
      { "explanation": "Scriem numărul complet:", "latex": "12\\,345\\,678" }
    ]
  }
]
```
