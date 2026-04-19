/**
 * Lesson block components — one component per block type.
 * All static block types for Phase 3.
 * Interactive blocks render a stub placeholder until Phase 4.
 */
import { useState } from "react";
import { ChevronDown, ChevronRight, Lightbulb, AlertTriangle, Globe, BookOpen, Cpu } from "lucide-react";
import { BlockMath, InlineMath } from "@/lib/math";
import type {
  ParagraphBlock,
  DefinitionBox,
  ObservationBox,
  FormulaCard,
  RealWorldBox,
  WarningBox,
  BlockEquation,
  WorkedExample,
  WorkedExampleMulti,
  PropertiesList,
  SummaryTable,
  SymbolReference,
  CollapsibleSection,
  InteractiveComponent,
  LessonBlock,
} from "@/types/lesson";

// ─── Paragraph ────────────────────────────────────────────────────────────────

export function ParagraphBlockComponent({ block }: { block: ParagraphBlock }) {
  return (
    <p className="text-gray-800 leading-relaxed text-base my-4">
      <InlineMath text={block.text} />
    </p>
  );
}

// ─── Definition Box ───────────────────────────────────────────────────────────

export function DefinitionBoxComponent({ block }: { block: DefinitionBox }) {
  return (
    <div className="my-5 border-l-4 border-blue-500 bg-blue-50 rounded-r-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <BookOpen className="w-4 h-4 text-blue-600 shrink-0" />
        <span className="text-blue-700 font-semibold text-sm uppercase tracking-wide">
          <InlineMath text={block.title ?? "Definiție"} />
        </span>
      </div>
      <p className="text-gray-800 leading-relaxed">
        <InlineMath text={block.text} />
      </p>
    </div>
  );
}

// ─── Observation Box ──────────────────────────────────────────────────────────

export function ObservationBoxComponent({ block }: { block: ObservationBox }) {
  return (
    <div className="my-5 border border-amber-200 bg-amber-50 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <Lightbulb className="w-4 h-4 text-amber-600 shrink-0" />
        <span className="text-amber-700 font-semibold text-sm uppercase tracking-wide">
          <InlineMath text={block.title ?? "Observație"} />
        </span>
      </div>
      <p className="text-gray-700 leading-relaxed">
        <InlineMath text={block.text} />
      </p>
    </div>
  );
}

// ─── Formula Card ─────────────────────────────────────────────────────────────

export function FormulaCardComponent({ block }: { block: FormulaCard }) {
  return (
    <div className="my-6 border-2 border-indigo-300 bg-indigo-50 rounded-xl p-5 text-center shadow-sm">
      {block.title && (
        <p className="text-indigo-600 font-semibold text-sm uppercase tracking-wider mb-3">
          <InlineMath text={block.title} />
        </p>
      )}
      <BlockMath latex={block.latex} className="text-lg" />
    </div>
  );
}

// ─── Real World Box ───────────────────────────────────────────────────────────

export function RealWorldBoxComponent({ block }: { block: RealWorldBox }) {
  return (
    <div className="my-5 border border-green-200 bg-green-50 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <Globe className="w-4 h-4 text-green-600 shrink-0" />
        <span className="text-green-700 font-semibold text-sm uppercase tracking-wide">
          Matematica în viața reală
        </span>
      </div>
      <p className="text-gray-700 leading-relaxed">
        <InlineMath text={block.text} />
      </p>
    </div>
  );
}

// ─── Warning Box ──────────────────────────────────────────────────────────────

export function WarningBoxComponent({ block }: { block: WarningBox }) {
  return (
    <div className="my-5 border-l-4 border-red-400 bg-red-50 rounded-r-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle className="w-4 h-4 text-red-500 shrink-0" />
        <span className="text-red-600 font-semibold text-sm uppercase tracking-wide">
          <InlineMath text={block.title ?? "Atenție!"} />
        </span>
      </div>
      <p className="text-gray-700 leading-relaxed">
        <InlineMath text={block.text} />
      </p>
    </div>
  );
}

// ─── Block Equation ───────────────────────────────────────────────────────────

export function BlockEquationComponent({ block }: { block: BlockEquation }) {
  return (
    <div className="my-5 py-3 overflow-x-auto">
      <BlockMath latex={block.latex} className="text-center" />
    </div>
  );
}

// ─── Worked Example ───────────────────────────────────────────────────────────

export function WorkedExampleComponent({ block }: { block: WorkedExample }) {
  const [visibleSteps, setVisibleSteps] = useState(0);
  const allVisible = visibleSteps >= block.steps.length;

  return (
    <div className="my-6 border border-gray-200 rounded-xl overflow-hidden shadow-sm">
      {/* Header */}
      <div className="bg-gray-50 border-b border-gray-200 px-5 py-3">
        <span className="text-gray-500 font-semibold text-xs uppercase tracking-wider">
          Exemplu rezolvat
        </span>
      </div>

      {/* Problem */}
      <div className="px-5 py-4 bg-white border-b border-gray-100">
        <p className="font-semibold text-gray-800">
          <InlineMath text={block.problem} />
        </p>
      </div>

      {/* Steps */}
      <div className="px-5 py-4 space-y-4 bg-white">
        {block.steps.slice(0, visibleSteps).map((step, i) => (
          <div key={i} className="flex gap-3">
            <div className="shrink-0 w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 font-bold text-xs flex items-center justify-center mt-0.5">
              {i + 1}
            </div>
            <div className="flex-1 space-y-2">
              {step.explanation && (
                <p className="text-gray-700">
                  <InlineMath text={step.explanation} />
                </p>
              )}
              {step.latex && (
                <div className="bg-gray-50 rounded-lg p-3 overflow-x-auto">
                  <BlockMath latex={step.latex} />
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Controls */}
        <div className="flex gap-3 pt-2">
          {!allVisible && (
            <button
              onClick={() => setVisibleSteps((v) => v + 1)}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
            >
              {visibleSteps === 0 ? "Arată rezolvarea" : "Pasul următor →"}
            </button>
          )}
          {visibleSteps > 0 && !allVisible && (
            <button
              onClick={() => setVisibleSteps(block.steps.length)}
              className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
            >
              Arată tot
            </button>
          )}
          {visibleSteps > 0 && (
            <button
              onClick={() => setVisibleSteps(0)}
              className="text-sm text-gray-400 hover:text-gray-600 transition-colors ml-auto"
            >
              Resetează
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Worked Example Multi ─────────────────────────────────────────────────────

export function WorkedExampleMultiComponent({ block }: { block: WorkedExampleMulti }) {
  const [activeMethod, setActiveMethod] = useState(0);
  const [visibleSteps, setVisibleSteps] = useState(0);
  const method = block.methods[activeMethod];
    if (!method) return null;
    const allVisible = visibleSteps >= method.steps.length;


  const handleMethodChange = (index: number) => {
    setActiveMethod(index);
    setVisibleSteps(0);
  };

  return (
    <div className="my-6 border border-gray-200 rounded-xl overflow-hidden shadow-sm">
      {/* Header */}
      <div className="bg-gray-50 border-b border-gray-200 px-5 py-3">
        <span className="text-gray-500 font-semibold text-xs uppercase tracking-wider">
          Exemplu rezolvat — metode multiple
        </span>
      </div>

      {/* Problem */}
      <div className="px-5 py-4 bg-white border-b border-gray-100">
        <p className="font-semibold text-gray-800">
          <InlineMath text={block.problem} />
        </p>
      </div>

      {/* Method tabs */}
      <div className="flex border-b border-gray-200 bg-gray-50">
        {block.methods.map((m, i) => (
          <button
            key={i}
            onClick={() => handleMethodChange(i)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              i === activeMethod
                ? "border-indigo-500 text-indigo-600 bg-white"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {m.title}
          </button>
        ))}
      </div>

      {/* Steps */}
      <div className="px-5 py-4 space-y-4 bg-white">
        {method.steps.slice(0, visibleSteps).map((step, i) => (
          <div key={i} className="flex gap-3">
            <div className="shrink-0 w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 font-bold text-xs flex items-center justify-center mt-0.5">
              {i + 1}
            </div>
            <div className="flex-1 space-y-2">
              {step.explanation && (
                <p className="text-gray-700">
                  <InlineMath text={step.explanation} />
                </p>
              )}
              {step.latex && (
                <div className="bg-gray-50 rounded-lg p-3 overflow-x-auto">
                  <BlockMath latex={step.latex} />
                </div>
              )}
            </div>
          </div>
        ))}

        <div className="flex gap-3 pt-2">
          {!allVisible && (
            <button
              onClick={() => setVisibleSteps((v) => v + 1)}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
            >
              {visibleSteps === 0 ? "Arată rezolvarea" : "Pasul următor →"}
            </button>
          )}
          {visibleSteps > 0 && !allVisible && (
            <button
              onClick={() => setVisibleSteps(method.steps.length)}
              className="text-sm text-gray-400 hover:text-gray-600"
            >
              Arată tot
            </button>
          )}
          {visibleSteps > 0 && (
            <button
              onClick={() => setVisibleSteps(0)}
              className="text-sm text-gray-400 hover:text-gray-600 ml-auto"
            >
              Resetează
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Properties List ──────────────────────────────────────────────────────────

export function PropertiesListComponent({ block }: { block: PropertiesList }) {
  return (
    <div className="my-5">
      {block.title && (
        <h4 className="font-semibold text-gray-700 mb-3">
          <InlineMath text={block.title} />
        </h4>
      )}
      <div className="border border-gray-200 rounded-lg overflow-hidden divide-y divide-gray-100">
        {block.properties.map((prop, i) => (
          <div key={i} className="grid grid-cols-3 text-sm">
            <div className="px-4 py-3 font-medium text-gray-700 bg-gray-50">
              <InlineMath text={prop.name} />
            </div>
            <div className="px-4 py-3 text-center overflow-x-auto">
              <BlockMath latex={prop.symbolic} />
            </div>
            <div className="px-4 py-3 text-gray-600">
              <InlineMath text={prop.example} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Summary Table ────────────────────────────────────────────────────────────

export function SummaryTableComponent({ block }: { block: SummaryTable }) {
  return (
    <div className="my-5 overflow-x-auto">
      {block.title && (
        <p className="text-sm font-semibold text-gray-600 mb-2">
          <InlineMath text={block.title} />
        </p>
      )}
      <table className="w-full text-sm border-collapse border border-gray-200 rounded-lg overflow-hidden">
        <thead>
          <tr className="bg-gray-100">
            {block.headers.map((header, i) => (
              <th key={i} className="px-4 py-2 text-left font-semibold text-gray-700 border border-gray-200">
                <InlineMath text={header} />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {block.rows.map((row, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              {row.map((cell, j) => (
                <td key={j} className="px-4 py-2 text-gray-700 border border-gray-200">
                  <InlineMath text={cell} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Symbol Reference ─────────────────────────────────────────────────────────

export function SymbolReferenceComponent({ block }: { block: SymbolReference }) {
  return (
    <div className="my-5 border border-gray-200 bg-gray-50 rounded-lg p-4">
      {block.title && (
        <h4 className="text-sm font-semibold text-gray-700 mb-3">
          <InlineMath text={block.title} />
        </h4>
      )}
      <div className="flex flex-wrap gap-3">
        {block.symbols.map((entry, i) => (
          <div
            key={i}
            className="min-w-[100px] flex-1 flex flex-col items-center justify-center text-center bg-white border border-gray-200 rounded-md px-3 py-2"
          >
            <BlockMath latex={entry.symbol} className="text-lg" />
            <div className="text-xs text-gray-500 mt-1">
              <InlineMath text={entry.name} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Collapsible Section ──────────────────────────────────────────────────────

export function CollapsibleSectionComponent({ block }: { block: CollapsibleSection }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="my-5 border border-purple-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 bg-purple-50 hover:bg-purple-100 transition-colors text-left"
      >
        {open ? (
          <ChevronDown className="w-4 h-4 text-purple-500 shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 text-purple-500 shrink-0" />
        )}
        <span className="text-purple-700 font-medium text-sm">
          <InlineMath text={block.title} />
        </span>
      </button>
      {open && (
        <div className="px-5 py-4 bg-white border-t border-purple-100 space-y-2">
          {block.blocks.map((nested, i) => (
            <BlockRenderer key={i} block={nested as LessonBlock} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Interactive Placeholder ──────────────────────────────────────────────────

const COMPONENT_LABELS: Record<string, string> = {
  column_arithmetic: "Aritmetică în coloană",
  long_division: "Împărțire în coloană",
  number_line: "Axă numerică",
  expression_evaluator: "Evaluator de expresii",
  base_converter: "Convertor de baze",
  place_value_table: "Tabel valori poziționale",
  last_digit_explorer: "Explorer ultima cifră",
  comparison_sorter: "Ordonare prin comparație",
  rounding: "Rotunjire interactivă",
};

export function InteractiveComponentPlaceholder({ block }: { block: InteractiveComponent }) {
  const label = COMPONENT_LABELS[block.component] ?? block.component;
  return (
    <div className="my-5 border-2 border-dashed border-gray-300 rounded-xl p-6 text-center bg-gray-50">
      <Cpu className="w-8 h-8 text-gray-400 mx-auto mb-2" />
      <p className="text-gray-500 font-medium text-sm">{label}</p>
      <p className="text-gray-400 text-xs mt-1">Componentă interactivă — în curând</p>
    </div>
  );
}

// ─── Merged Table ──────────────────────────────────────────────────────────────

export function MergedTableComponent({ block }: {
  block: {
    type: "merged_table";
    title?: string;
    column_groups: { label: string; columns: number }[];
    subheaders: string[];
    rows: string[][];
    footer_groups?: { label: string; columns: number }[];
  }
}) {
  return (
    <div className="my-5 overflow-x-auto">
      {block.title && (
        <p className="text-sm font-semibold text-gray-600 mb-2">{block.title}</p>
      )}
      <table className="text-sm border-collapse border border-gray-300 rounded-lg overflow-hidden min-w-full">
        <thead>
          <tr className="bg-indigo-50">
            {block.column_groups.map((group, i) => (
              <th
                key={i}
                colSpan={group.columns}
                className="px-3 py-2 text-center font-semibold text-indigo-700 border border-gray-300 text-xs"
              >
                {group.label}
              </th>
            ))}
          </tr>
          <tr className="bg-gray-100">
            {block.subheaders.map((header, i) => (
              <th
                key={i}
                className="px-3 py-2 text-center font-medium text-gray-600 border border-gray-300 text-xs"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {block.rows.map((row, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              {row.map((cell, j) => (
                <td
                  key={j}
                  className="px-3 py-2 text-center text-gray-700 border border-gray-300 font-mono"
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
        {block.footer_groups && (
          <tfoot>
            <tr className="bg-blue-50">
              {block.footer_groups.map((group, i) => (
                <td
                  key={i}
                  colSpan={group.columns}
                  className="px-3 py-2 text-center text-blue-700 border border-gray-300 text-xs italic"
                >
                  {group.label}
                </td>
              ))}
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  );
}

// ─── Block Renderer (dispatcher) ─────────────────────────────────────────────

export function BlockRenderer({ block }: { block: LessonBlock }) {
  switch (block.type) {
    case "paragraph":
      return <ParagraphBlockComponent block={block} />;
    case "definition_box":
      return <DefinitionBoxComponent block={block} />;
    case "observation_box":
      return <ObservationBoxComponent block={block} />;
    case "formula_card":
      return <FormulaCardComponent block={block} />;
    case "real_world_box":
      return <RealWorldBoxComponent block={block} />;
    case "warning_box":
      return <WarningBoxComponent block={block} />;
    case "block_equation":
      return <BlockEquationComponent block={block} />;
    case "worked_example":
      return <WorkedExampleComponent block={block} />;
    case "worked_example_multi":
      return <WorkedExampleMultiComponent block={block} />;
    case "properties_list":
      return <PropertiesListComponent block={block} />;
    case "summary_table":
      return <SummaryTableComponent block={block} />;
    case "symbol_reference":
      return <SymbolReferenceComponent block={block} />;
    case "collapsible":
      return <CollapsibleSectionComponent block={block} />;
    case "interactive":
      return <InteractiveComponentPlaceholder block={block} />;
    case "merged_table":
      return <MergedTableComponent block={block as any} />;
    default:
      return (
        <div className="text-red-500 text-xs font-mono p-2 bg-red-50 rounded my-2">
          Unknown block type: {(block as { type: string }).type}
        </div>
      );
  }
}
