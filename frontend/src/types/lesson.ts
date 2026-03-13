// Lesson block type definitions
// Mirrors BLOCK_SCHEMA.md exactly — keep in sync.

export interface WorkedExampleStep {
  explanation: string; // text with optional inline $math$
  latex?: string;      // optional block equation for this step
}

export interface WorkedExampleMethod {
  title: string;
  steps: WorkedExampleStep[];
}

export interface Property {
  name: string;
  symbolic: string; // KaTeX expression
  example: string;  // text with inline $math$
}

export interface MergedTable {
   type: "merged_table";
   title?: string;
   column_groups: { label: string; columns: number }[];
   subheaders: string[];
   rows: string[][];
   footer_groups?: { label: string; columns: number }[];
 }

// ─── Block types ────────────────────────────────────────────────────────────

export interface ParagraphBlock {
  type: "paragraph";
  text: string;
}

export interface DefinitionBox {
  type: "definition_box";
  title?: string; // defaults to "Definiție"
  text: string;
}

export interface ObservationBox {
  type: "observation_box";
  title?: string; // defaults to "Observație"
  text: string;
}

export interface FormulaCard {
  type: "formula_card";
  title?: string;
  latex: string;
}

export interface RealWorldBox {
  type: "real_world_box";
  text: string;
}

export interface WarningBox {
  type: "warning_box";
  title?: string; // defaults to "Atenție!"
  text: string;
}

export interface BlockEquation {
  type: "block_equation";
  latex: string;
}

export interface WorkedExample {
  type: "worked_example";
  problem: string;
  steps: WorkedExampleStep[];
}

export interface WorkedExampleMulti {
  type: "worked_example_multi";
  problem: string;
  methods: WorkedExampleMethod[];
}

export interface PropertiesList {
  type: "properties_list";
  title?: string;
  properties: Property[];
}

export interface SummaryTable {
  type: "summary_table";
  title?: string;
  headers: string[];
  rows: string[][];
}

export interface CollapsibleSection {
  type: "collapsible";
  title: string;
  // Nested blocks — any type except another collapsible
  blocks: Exclude<LessonBlock, CollapsibleSection>[];
}

export interface InteractiveComponent {
  type: "interactive";
  component:
    | "column_arithmetic"
    | "long_division"
    | "number_line"
    | "expression_evaluator"
    | "base_converter"
    | "place_value_table"
    | "last_digit_explorer"
    | "comparison_sorter";
  config: Record<string, unknown>;
}

// ─── Union type ──────────────────────────────────────────────────────────────

export type LessonBlock =
  | ParagraphBlock
  | DefinitionBox
  | ObservationBox
  | FormulaCard
  | RealWorldBox
  | WarningBox
  | BlockEquation
  | WorkedExample
  | WorkedExampleMulti
  | PropertiesList
  | SummaryTable
  | CollapsibleSection
  | InteractiveComponent
  | MergedTable;

// ─── Lesson API types ────────────────────────────────────────────────────────

export interface LessonListItem {
  id: number;
  order: number;
  title: string;
  summary: string;
  practice_minimum: number;
  exercise_count: number;
}

export interface LessonDetail {
  id: number;
  order: number;
  title: string;
  summary: string;
  blocks: LessonBlock[];
  practice_minimum: number;
  unit_id: number;
  unit_title: string;
  unit_order: number;
  grade_number: number;
  prev_lesson_id: number | null;
  next_lesson_id: number | null;
  exercises: Exercise[];
  glossary_terms: GlossaryTerm[];
  updated_at: string;
}

export interface Exercise {
  id: number;
  exercise_type: string;
  difficulty: "easy" | "medium" | "hard";
  template: Record<string, unknown>;
}

export interface GlossaryTerm {
  id: number;
  term: string;
  definition: string;
}

export interface UnitDetail {
  id: number;
  order: number;
  title: string;
  description: string;
  recommended_unlock_date: string | null;
  lesson_count: number;
  lessons: LessonListItem[];
  test: {
    id: number;
    pass_threshold: number;
    time_limit_minutes: number | null;
    exercise_count: number;
  } | null;
}
