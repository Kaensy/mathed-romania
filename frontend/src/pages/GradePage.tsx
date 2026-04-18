import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  BookOpen,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  ClipboardList,
  Lock,
  PenLine,
  Shield,
  Sparkles,
} from "lucide-react";
import api from "@/api/client";
import type {
  GradeDetail,
  LessonListItem,
  MasteryTier,
  TestInfo,
  TopicListItem,
} from "@/types/lesson";

export default function GradePage() {
  const { gradeNumber } = useParams<{ gradeNumber: string }>();
  const [grade, setGrade] = useState<GradeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedTopics, setExpandedTopics] = useState<Set<number>>(new Set());

  useEffect(() => {
    api
      .get<GradeDetail>(`/content/grades/${gradeNumber}/`)
      .then((res) => setGrade(res.data))
      .catch(() => setError("Nu am putut încărca conținutul."))
      .finally(() => setLoading(false));
  }, [gradeNumber]);

  const toggleTopic = (topicId: number) => {
    setExpandedTopics((prev) => {
      const next = new Set(prev);
      if (next.has(topicId)) next.delete(topicId);
      else next.add(topicId);
      return next;
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !grade) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">{error ?? "Eroare necunoscută."}</p>
      </div>
    );
  }

  // Sequential topic index across all units (1, 2, 3, ...)
  let topicCounter = 0;
  const topicIndexMap = new Map<number, number>();
  for (const unit of grade.units) {
    for (const topic of unit.topics) {
      topicCounter++;
      topicIndexMap.set(topic.id, topicCounter);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 py-6">
          <Link
            to="/dashboard"
            className="flex items-center gap-1 text-gray-400 hover:text-gray-600 text-sm mb-3 transition-colors w-fit"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Dashboard</span>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">{grade.name}</h1>
        </div>
      </div>

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-8">
        {grade.units.map((unit) => (
          <div key={unit.id} className="space-y-8">
            <section>
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                {unit.title}
              </h2>

              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm divide-y divide-gray-100">
                {unit.topics.length === 0 && (
                  <div className="px-5 py-4 flex items-center gap-2 text-gray-400 text-sm">
                    <Lock className="w-4 h-4" />
                    <span>Lecțiile acestei unități sunt în curs de elaborare.</span>
                  </div>
                )}

                {unit.topics.length > 0 && isUnitLocked(unit) ? (
                  <div className="px-5 py-6 flex items-center gap-3 text-gray-400">
                    <Lock className="w-5 h-5" />
                    <div>
                      <p className="text-sm font-medium">Unitate blocată</p>
                      <p className="text-xs mt-0.5">
                        Promovează testul unității anterioare pentru a debloca.
                      </p>
                    </div>
                  </div>
                ) : (
                  unit.topics.map((topic) => (
                    <TopicRow
                      key={topic.id}
                      topic={topic}
                      topicIndex={topicIndexMap.get(topic.id) ?? topic.order}
                      isExpanded={expandedTopics.has(topic.id)}
                      onToggle={() => toggleTopic(topic.id)}
                    />
                  ))
                )}
              </div>
            </section>

            {unit.test && <UnitTestCard test={unit.test} unitTitle={unit.title} />}
          </div>
        ))}
      </main>
    </div>
  );
}

// ─── TopicRow ─────────────────────────────────────────────────────────────────

interface TopicRowProps {
  topic: TopicListItem;
  topicIndex: number;
  isExpanded: boolean;
  onToggle: () => void;
}

function TopicRow({ topic, topicIndex, isExpanded, onToggle }: TopicRowProps) {
  const isMultiLesson = topic.lessons.length > 1;
  const firstLesson = topic.lessons[0];

  if (!firstLesson) return null;

  // Single-lesson topic — direct link + inline status row below
  if (!isMultiLesson) {
    const hasStatus = topic.has_practiced || topic.test !== null;
    return (
      <div>
        <LessonRow
          lesson={firstLesson}
          label={String(topicIndex)}
          exerciseCount={topic.exercise_count}
          masteryTier={topic.mastery_tier}
        />
        {hasStatus && (
          <div className="flex items-center gap-3 px-5 pb-3 -mt-1 pl-[4.25rem]">
            {topic.has_practiced && (
              <span className="flex items-center gap-1 text-xs text-indigo-400">
                <PenLine className="w-3.5 h-3.5" />
                <span>Exersat</span>
              </span>
            )}
            <TopicTestBadge test={topic.test} />
          </div>
        )}
      </div>
    );
  }

  // Multi-lesson topic — collapsible group
  return (
    <div>
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-colors text-left"
      >
        <div className="shrink-0 w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-semibold text-sm flex items-center justify-center">
          {topicIndex}
        </div>

        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 truncate">{topic.title}</p>
          <p className="text-sm text-gray-400 mt-0.5">
            {topic.lessons.length} lecții
            {topic.exercise_count > 0 && ` · ${topic.exercise_count} exerciții`}
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {topic.has_practiced && (
            <PenLine className="w-3.5 h-3.5 text-indigo-400" />
          )}
          <MasteryBadge tier={topic.mastery_tier} />
          <TopicTestBadge test={topic.test} />
          <span className="text-gray-400">
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </span>
        </div>
      </button>

      {isExpanded && (
        <div className="border-t border-gray-100 bg-gray-50/50">
          {topic.lessons.map((lesson) => (
            <LessonRow
              key={lesson.id}
              lesson={lesson}
              label={`${topicIndex}.${lesson.order}`}
              exerciseCount={0}
              masteryTier={lesson.mastery_tier}
              indented
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── TopicTestBadge ───────────────────────────────────────────────────────────

function UnitTestCard({ test, unitTitle }: { test: TestInfo; unitTitle: string }) {
  const scoreBadge =
    test.best_score !== null ? (
      <span
        className={`flex items-center gap-1 text-xs font-medium ${
          test.passed ? "text-green-600" : "text-amber-600"
        }`}
      >
        {test.passed && <CheckCircle className="w-3.5 h-3.5" />}
        <span>{Math.round(test.best_score)}%</span>
      </span>
    ) : null;

  const labelBlock = (
    <div className="flex-1 min-w-0">
      <p className="text-xs font-semibold text-indigo-500 uppercase tracking-wider">
        Test de unitate
      </p>
      <p className="font-medium text-gray-900 truncate mt-0.5">{unitTitle}</p>
      <p className="text-xs text-gray-500 mt-0.5">
        Prag: {test.pass_threshold}%
        {test.time_limit_minutes ? ` · ${test.time_limit_minutes} min` : ""}
      </p>
    </div>
  );

  if (test.is_locked) {
    return (
      <div className="bg-indigo-50/40 rounded-2xl border border-indigo-100 shadow-sm px-5 py-4 flex items-center gap-4 opacity-60 cursor-not-allowed">
        <div className="shrink-0 w-10 h-10 rounded-full bg-gray-100 text-gray-400 flex items-center justify-center">
          <Lock className="w-5 h-5" />
        </div>
        {labelBlock}
        <span className="flex items-center gap-1 text-xs text-gray-400">
          <Lock className="w-3.5 h-3.5" />
          <span>Blocat</span>
        </span>
      </div>
    );
  }

  return (
    <Link
      to={`/test/${test.id}`}
      className="bg-indigo-50/40 rounded-2xl border border-indigo-100 shadow-sm px-5 py-4 flex items-center gap-4 hover:bg-indigo-50 hover:border-indigo-200 transition-colors group"
    >
      <div className="shrink-0 w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 group-hover:bg-indigo-200 transition-colors flex items-center justify-center">
        <ClipboardList className="w-5 h-5" />
      </div>
      {labelBlock}
      <div className="flex items-center gap-3 shrink-0">
        {scoreBadge}
        <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-indigo-400 transition-colors" />
      </div>
    </Link>
  );
}

function TopicTestBadge({ test }: { test: TestInfo | null }) {
  if (!test) return null;

  if (test.is_locked) {
    return (
      <span className="flex items-center gap-1 text-xs text-gray-400">
        <Lock className="w-3.5 h-3.5" />
        <span>Test</span>
      </span>
    );
  }

  if (test.attempts_count === 0) {
    return <span className="text-xs text-gray-400">Test disponibil</span>;
  }

  return null;
}

// ─── MasteryBadge ─────────────────────────────────────────────────────────────

function MasteryBadge({ tier }: { tier: MasteryTier }) {
  if (tier === "none") return null;

  if (tier === "deschisa") {
    return (
      <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 font-medium">
        Deschisă
      </span>
    );
  }

  if (tier === "promovat") {
    return (
      <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-green-50 text-green-700 font-medium">
        <CheckCircle className="w-3 h-3" />
        Promovat
      </span>
    );
  }

  if (tier === "stapanit") {
    return (
      <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-medium">
        <Shield className="w-3 h-3" />
        Stăpânit
      </span>
    );
  }

  // perfect
  return (
    <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 font-medium">
      <Sparkles className="w-3 h-3" />
      Perfect
    </span>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function isUnitLocked(unit: { topics: TopicListItem[] }): boolean {
  const allLessons = unit.topics.flatMap((t) => t.lessons);
  if (allLessons.length === 0) return false;
  return allLessons.every((l) => l.is_locked);
}

// ─── LessonRow ────────────────────────────────────────────────────────────────

interface LessonRowProps {
  lesson: LessonListItem;
  label: string;        // "4" for single topics, "4.1" / "4.2" for multi
  exerciseCount: number;
  masteryTier: MasteryTier;
  indented?: boolean;
}

function LessonRow({ lesson, label, exerciseCount, masteryTier, indented = false }: LessonRowProps) {
  const isSubLabel = label.includes(".");

  if (lesson.is_locked) {
    return (
      <div className={`flex items-center gap-4 px-5 py-4 opacity-50 cursor-not-allowed ${indented ? "pl-10" : ""}`}>
        <div className="shrink-0 w-8 h-8 rounded-full bg-gray-100 text-gray-400 font-semibold text-sm flex items-center justify-center">
          <Lock className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-500 truncate">{lesson.title}</p>
          {lesson.summary && (
            <p className="text-sm text-gray-400 mt-0.5 truncate">{lesson.summary}</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <Link
      to={`/lesson/${lesson.id}`}
      className={`flex items-center gap-4 px-5 py-4 hover:bg-primary-50 transition-colors group ${indented ? "pl-10" : ""}`}
    >
      <div className={`shrink-0 w-8 h-8 rounded-full bg-primary-100 text-primary-600 group-hover:bg-primary-200 transition-colors font-semibold flex items-center justify-center ${isSubLabel ? "text-xs" : "text-sm"}`}>
        {label}
      </div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 truncate">{lesson.title}</p>
        {lesson.summary && (
          <p className="text-sm text-gray-500 mt-0.5 truncate">{lesson.summary}</p>
        )}
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <MasteryBadge tier={masteryTier} />
        {exerciseCount > 0 && (
          <span className="flex items-center gap-1 text-xs text-gray-400">
            <BookOpen className="w-3.5 h-3.5" />
            {exerciseCount}
          </span>
        )}
        <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-indigo-400 transition-colors" />
      </div>
    </Link>
  );
}