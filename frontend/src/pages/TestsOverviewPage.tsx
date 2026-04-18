import { useEffect, useMemo, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  ClipboardList,
  Clock,
  Lock,
  Trophy,
  XCircle,
} from "lucide-react";
import api from "@/api/client";
import type {
  TestsOverviewResponse,
  TopicTestSummary,
  UnitTestSummary,
} from "@/types/progress";

export default function TestsOverviewPage() {
  const navigate = useNavigate();
  const [tests, setTests] = useState<TopicTestSummary[]>([]);
  const [unitTests, setUnitTests] = useState<UnitTestSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [collapsedUnits, setCollapsedUnits] = useState<Set<string>>(new Set());

  useEffect(() => {
    api
      .get<TestsOverviewResponse>("/progress/tests-overview/")
      .then((res) => {
        setTests(res.data.tests);
        setUnitTests(res.data.unit_tests ?? []);
      })
      .catch(() => setError("Nu am putut încărca testele."))
      .finally(() => setLoading(false));
  }, []);

  const byUnit = useMemo(() => groupByUnit(tests), [tests]);
  const unitTestByTitle = useMemo(() => {
    const map = new Map<string, UnitTestSummary>();
    for (const ut of unitTests) map.set(ut.unit_title, ut);
    return map;
  }, [unitTests]);
  const passedCount = tests.filter((t) => t.passed === true).length;
  const attemptedCount = tests.filter((t) => t.passed !== null).length;

  const toggleUnit = (unitTitle: string) => {
    setCollapsedUnits((prev) => {
      const next = new Set(prev);
      if (next.has(unitTitle)) next.delete(unitTitle);
      else next.add(unitTitle);
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center gap-4">
          <Link
            to="/dashboard"
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Dashboard</span>
          </Link>
          <span className="text-gray-300">|</span>
          <span className="text-sm font-medium text-gray-700">Teste</span>
        </div>
      </div>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Teste</h1>
        <p className="text-sm text-gray-500 mb-6">Un test per temă — promovează pentru a debloca lecția următoare</p>

        {/* Summary stats */}
        {tests.length > 0 && (
          <div className="flex items-center gap-6 mb-8 text-sm text-gray-600">
            <span>
              <strong className="text-gray-900">{passedCount}</strong> / {tests.length} promovate
            </span>
            {attemptedCount > 0 && (
              <span>
                <strong className="text-gray-900">{attemptedCount}</strong> susținute
              </span>
            )}
          </div>
        )}

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        {tests.length === 0 && !loading && (
          <p className="text-gray-400 text-center py-16">Niciun test disponibil momentan.</p>
        )}

        <div className="space-y-8">
          {byUnit.map(({ unitTitle, unitTests: unitTopicTests }) => {
            const isCollapsed = collapsedUnits.has(unitTitle);
            const unitTest = unitTestByTitle.get(unitTitle) ?? null;
            return (
              <div key={unitTitle} className="space-y-8">
                <section>
                  <button
                    onClick={() => toggleUnit(unitTitle)}
                    className="w-full flex items-center justify-between mb-3 group"
                  >
                    <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider group-hover:text-gray-600 transition-colors">
                      {unitTitle}
                    </h2>
                    <span className="text-gray-400 group-hover:text-gray-600 transition-colors">
                      {isCollapsed ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronUp className="w-4 h-4" />
                      )}
                    </span>
                  </button>

                  {!isCollapsed && (
                    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm divide-y divide-gray-100">
                      {unitTopicTests.map((test) => {
                        const globalIndex = tests.indexOf(test) + 1;
                        return (
                          <TestRow
                            key={test.test_id}
                            test={test}
                            index={globalIndex}
                            onNavigate={() => navigate(`/test/${test.test_id}`)}
                          />
                        );
                      })}
                    </div>
                  )}
                </section>

                {unitTest && (
                  <UnitTestCard
                    test={unitTest}
                    onNavigate={() => navigate(`/test/${unitTest.test_id}`)}
                  />
                )}
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}

// ─── TestRow ──────────────────────────────────────────────────────────────────

function TestRow({
  test,
  index,
  onNavigate,
}: {
  test: TopicTestSummary;
  index: number;
  onNavigate: () => void;
}) {
  if (test.is_locked) {
    return (
      <div className="w-full flex items-center gap-4 px-5 py-4 opacity-50 cursor-not-allowed">
        <div className="shrink-0 w-8 h-8 rounded-full bg-gray-100 text-gray-400 font-semibold text-sm flex items-center justify-center">
          <Lock className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-500 truncate">{test.topic_title}</p>
          <p className="text-xs text-gray-400 mt-0.5">
            Promovează testul anterior pentru a debloca.
          </p>
        </div>
      </div>
    );
  }

  const statusIcon =
    test.passed === true ? (
      <CheckCircle className="w-5 h-5 text-green-500" />
    ) : test.passed === false ? (
      <XCircle className="w-5 h-5 text-red-400" />
    ) : null;

  return (
    <button
      onClick={onNavigate}
      className="w-full flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-colors text-left"
    >
      {/* Index */}
      <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-50 text-indigo-600 font-semibold text-sm flex items-center justify-center">
        {index}
      </div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 truncate">{test.topic_title}</p>
        <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
          <span>Prag: {test.pass_threshold}%</span>
          {test.time_limit_minutes && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {test.time_limit_minutes} min
            </span>
          )}
          {test.best_score !== null && (
            <span className="flex items-center gap-1">
              <Trophy className="w-3 h-3" />
              {Math.round(test.best_score)}%
            </span>
          )}
          {test.attempts_count > 0 && (
            <span>{test.attempts_count} {test.attempts_count === 1 ? "încercare" : "încercări"}</span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {statusIcon}
        <ChevronRight className="w-4 h-4 text-gray-300" />
      </div>
    </button>
  );
}

// ─── UnitTestCard ─────────────────────────────────────────────────────────────

function UnitTestCard({
  test,
  onNavigate,
}: {
  test: UnitTestSummary;
  onNavigate: () => void;
}) {
  const labelBlock = (
    <div className="flex-1 min-w-0">
      <p className="text-xs font-semibold text-indigo-500 uppercase tracking-wider">
        Test de unitate
      </p>
      <p className="font-medium text-gray-900 truncate mt-0.5">{test.unit_title}</p>
      <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
        <span>Prag: {test.pass_threshold}%</span>
        {test.time_limit_minutes && (
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {test.time_limit_minutes} min
          </span>
        )}
        {test.best_score !== null && (
          <span className="flex items-center gap-1">
            <Trophy className="w-3 h-3" />
            {Math.round(test.best_score)}%
          </span>
        )}
        {test.attempts_count > 0 && (
          <span>
            {test.attempts_count} {test.attempts_count === 1 ? "încercare" : "încercări"}
          </span>
        )}
      </div>
    </div>
  );

  if (test.is_locked) {
    return (
      <div className="bg-indigo-50/40 rounded-2xl border border-indigo-100 shadow-sm px-5 py-4 flex items-center gap-4 opacity-60 cursor-not-allowed">
        <div className="shrink-0 w-10 h-10 rounded-full bg-gray-100 text-gray-400 flex items-center justify-center">
          <Lock className="w-5 h-5" />
        </div>
        {labelBlock}
      </div>
    );
  }

  const statusIcon =
    test.passed === true ? (
      <CheckCircle className="w-5 h-5 text-green-500" />
    ) : test.passed === false ? (
      <XCircle className="w-5 h-5 text-red-400" />
    ) : null;

  return (
    <button
      onClick={onNavigate}
      className="w-full bg-indigo-50/40 rounded-2xl border border-indigo-100 shadow-sm px-5 py-4 flex items-center gap-4 hover:bg-indigo-50 hover:border-indigo-200 transition-colors text-left group"
    >
      <div className="shrink-0 w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 group-hover:bg-indigo-200 transition-colors flex items-center justify-center">
        <ClipboardList className="w-5 h-5" />
      </div>
      {labelBlock}
      <div className="flex items-center gap-2 shrink-0">
        {statusIcon}
        <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-indigo-400 transition-colors" />
      </div>
    </button>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function groupByUnit(tests: TopicTestSummary[]) {
  const map = new Map<string, TopicTestSummary[]>();
  for (const test of tests) {
    const key = test.unit_title;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(test);
  }
  return Array.from(map.entries()).map(([unitTitle, unitTests]) => ({
    unitTitle,
    unitTests,
  }));
}
