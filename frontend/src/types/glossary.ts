export type GlossaryCategory = "definition" | "notation" | "property" | "other";

export interface GlossaryUnit {
  id: number;
  grade_number: number;
  order: number;
  title: string;
}

export interface GlossaryTerm {
  id: number;
  term: string;
  aliases: string[];
  definition: string;
  category: GlossaryCategory;
  examples: string[];
  unit: GlossaryUnit;
}
