// ─── Block types ─────────────────────────────────────────────────────────────

export interface ParagraphBlock {
  type: "paragraph";
  text: string;
}

export interface DefinitionBox {
  type: "definition_box";
  title?: string;
  text: string;
}

export interface ObservationBox {
  type: "observation_box";
  title?: string;
  text: string;
}

export interface FormulaCard {
  type: "formula_card";
  title?: string;
  latex: string;
  explanation?: string;
}

export interface RealWorldBox {
  type: "real_world_box";
  text: string;
}

export interface WarningBox {
  type: "warning_box";
  title?: string;
  text: string;
}

export interface BlockEquation {
  type: "block_equation";
  latex: string;
}

export interface WorkedExampleStep {
  explanation: string;
  latex?: string;
}

export interface WorkedExample {
  type: "worked_example";
  problem: string;
  steps: WorkedExampleStep[];
}

export interface WorkedExampleMethod {
  title: string;
  steps: WorkedExampleStep[];
}

export interface WorkedExampleMulti {
  type: "worked_example_multi";
  problem: string;
  methods: WorkedExampleMethod[];
}

export interface Property {
  name: string;
  latex?: string;
  example?: string;
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

export interface MergedTable {
  type: "merged_table";
  title?: string;
  headers: string[];
  rows: (string | { text: string; colspan?: number; rowspan?: number })[][];
}

export interface CollapsibleSection {
  type: "collapsible";
  title: string;
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
  | MergedTable
  | CollapsibleSection
  | InteractiveComponent;

// ─── API types ────────────────────────────────────────────────────────────────

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

export interface TestInfo {
  id: number;
  scope: string;
  pass_threshold: number;
  time_limit_minutes: number | null;
  composition: unknown[];
}

// ─── Lesson ───────────────────────────────────────────────────────────────────

export interface LessonListItem {
  id: number;
  order: number;
  title: string;
  summary: string;
  topic_id: number;
  topic_test_id: number | null;
  is_locked: boolean;
}

export interface LessonDetail {
  id: number;
  order: number;
  title: string;
  summary: string;
  blocks: LessonBlock[];
  // Topic context
  topic_id: number;
  topic_title: string;
  topic_order: number;
  topic_test_id: number | null;
  topic_exercise_count: number;
  // Unit / grade context
  unit_id: number;
  unit_title: string;
  unit_order: number;
  grade_number: number;
  // Navigation
  prev_lesson_id: number | null;
  next_lesson_id: number | null;
  glossary_terms: GlossaryTerm[];
  updated_at: string;
}

// ─── Topic ────────────────────────────────────────────────────────────────────

export interface TopicListItem {
  id: number;
  order: number;
  title: string;
  description: string;
  is_published: boolean;
  practice_minimum: number;
  exercise_count: number;
  lessons: LessonListItem[];
  test: TestInfo | null;
}

// ─── Unit ─────────────────────────────────────────────────────────────────────

export interface UnitDetail {
  id: number;
  order: number;
  title: string;
  description: string;
  recommended_unlock_date: string | null;
  topic_count: number;
  topics: TopicListItem[];
  test: TestInfo | null;
}

// ─── Grade ────────────────────────────────────────────────────────────────────

export interface GradeDetail {
  id: number;
  number: number;
  name: string;
  units: UnitDetail[];
}

export interface GradeListItem {
  id: number;
  number: number;
  name: string;
  unit_count: number;
}
