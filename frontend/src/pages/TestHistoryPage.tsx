/**
 * TestHistoryPage — chronological list of completed test attempts.
 *
 * Route: /test-history
 *
 * Each card navigates to /test/:testId?review=true, which renders
 * TestResultScreen in read-only review mode.
 */
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  FileText,
  Clock,
} from "lucide-react";
import api from "@/api/client";
import type { TestHistoryAttempt, TestHistoryResponse } from "@/types/test";

export default function TestHistoryPage() {
  const navigate = useNavigate();
  const [attempts, setAttempts] = useState<TestHistoryAttempt[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<TestHistoryResponse>("/progress/test-history/?limit=20")
      .then((res) => setAttempts(res.data.attempts))
      .catch(() => setError("Nu am putut încărca istoricul testelor."));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 border-b bg-white">
        <div className="mx-auto flex max-w-3xl items-center gap-4 px-6 py-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Înapoi</span>
          </button>
          <h1 className="text-base font-semibold text-gray-800">Istoricul testelor</h1>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8">
        {error && (
          <p className="text-sm text-red-500 text-center">{error}</p>
        )}

        {attempts === null && !error && (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="rounded-xl border bg-white p-5 animate-pulse h-24"
              />
            ))}
          </div>
        )}

        {attempts !== null && attempts.length === 0 && !error && (
          <div className="rounded-xl border border-dashed border-gray-200 bg-white px-5 py-10 text-center">
            <FileText className="w-7 h-7 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">
              Nu ai finalizat niciun test încă.
            </p>
          </div>
        )}

        {attempts !== null && attempts.length > 0 && (
          <div className="space-y-3">
            {attempts.map((a) => (
              <AttemptCard key={a.attempt_id} attempt={a} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function AttemptCard({ attempt }: { attempt: TestHistoryAttempt }) {
  const navigate = useNavigate();
  const scoreInt = attempt.score !== null ? Math.round(attempt.score) : null;
  const romanianGrade =
    scoreInt !== null ? Math.round((scoreInt / 100) * 9 + 1) : null;
  const scopeLabel =
    attempt.test_scope === "topic" ? "Test de temă" : "Test de unitate";

  return (
    <button
      onClick={() =>
        navigate(`/test/${attempt.test_id}?review=true`, {
          state: { from: "/test-history" },
        })
      }
      className="w-full text-left bg-white rounded-xl border border-gray-200 px-5 py-4
        hover:border-indigo-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-center gap-4">
        <div
          className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
            attempt.passed
              ? "bg-green-100 text-green-600"
              : "bg-red-100 text-red-500"
          }`}
        >
          {attempt.passed ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <XCircle className="w-5 h-5" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="font-semibold text-gray-900 truncate" title={attempt.test_title}>
              {attempt.test_title || "Test"}
            </p>
            <span className="rounded-full bg-gray-100 text-gray-600 px-2 py-0.5 text-xs font-medium">
              {scopeLabel}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-500 mt-1 flex-wrap">
            <span className="inline-flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatAttemptDate(attempt.finished_at)}
            </span>
            <span>·</span>
            <span>
              {attempt.exercise_count}{" "}
              {attempt.exercise_count === 1 ? "exercițiu" : "exerciții"}
            </span>
          </div>
        </div>

        <div className="shrink-0 text-right">
          {romanianGrade !== null ? (
            <>
              <p className="text-lg font-bold text-indigo-600">
                {romanianGrade}
                <span className="text-gray-400 text-sm font-medium">/10</span>
              </p>
              <p className="text-xs text-gray-400">{scoreInt}%</p>
            </>
          ) : (
            <p className="text-sm text-gray-400">—</p>
          )}
        </div>
      </div>
    </button>
  );
}

function formatAttemptDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfThen = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const diffDays = Math.round(
    (startOfToday.getTime() - startOfThen.getTime()) / (1000 * 60 * 60 * 24),
  );

  const time = d.toLocaleTimeString("ro-RO", { hour: "2-digit", minute: "2-digit" });

  if (diffDays <= 0) return `astăzi, ${time}`;
  if (diffDays === 1) return `ieri, ${time}`;
  if (diffDays < 7) return `acum ${diffDays} zile`;
  return d.toLocaleDateString("ro-RO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}
