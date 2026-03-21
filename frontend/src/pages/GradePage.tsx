import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ChevronRight, Lock, BookOpen, ChevronDown, ChevronUp, ArrowLeft } from "lucide-react";
import api from "@/api/client";
import type { GradeDetail, TopicListItem, LessonListItem } from "@/types/lesson";

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
          <section key={unit.id}>
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

              {unit.topics.map((topic) => (
                <TopicRow
                  key={topic.id}
                  topic={topic}
                  topicIndex={topicIndexMap.get(topic.id) ?? topic.order}
                  isExpanded={expandedTopics.has(topic.id)}
                  onToggle={() => toggleTopic(topic.id)}
                />
              ))}
            </div>
          </section>
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

  // Single-lesson topic — direct link
  if (!isMultiLesson) {
    return (
      <LessonRow
        lesson={firstLesson}
        label={String(topicIndex)}
        exerciseCount={topic.exercise_count}
      />
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

        <div className="flex items-center gap-2 text-gray-400">
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
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
              indented
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── LessonRow ────────────────────────────────────────────────────────────────

interface LessonRowProps {
  lesson: LessonListItem;
  label: string;        // "4" for single topics, "4.1" / "4.2" for multi
  exerciseCount: number;
  indented?: boolean;
}

function LessonRow({ lesson, label, exerciseCount, indented = false }: LessonRowProps) {
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