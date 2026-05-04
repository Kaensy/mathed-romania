// ═══════════════════════════════════════════════════════════════════════════
// ExerciseHubPage.tsx  —  route: /topic/:topicId/exercises
// ═══════════════════════════════════════════════════════════════════════════
import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { ArrowLeft, Lock, Star } from "lucide-react";
import api from "@/api/client";
import { CATEGORY_LABELS } from "@/constants/categoryLabels";
import type { TopicCategoriesResponse, CategoryInfo, Difficulty } from "@/types/progress";

const DIFFICULTY_LABEL: Record<Difficulty, string> = {
  easy: "Ușor",
  medium: "Mediu",
  hard: "Greu",
};

const DIFFICULTY_COLOR: Record<Difficulty, string> = {
  easy: "bg-green-100 text-green-700 hover:bg-green-200",
  medium: "bg-yellow-100 text-yellow-700 hover:bg-yellow-200",
  hard: "bg-red-100 text-red-700 hover:bg-red-200",
};

export default function ExerciseHubPage() {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [data, setData] = useState<TopicCategoriesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Back-navigation: lesson passes { from: "/lesson/123" } via state
  const backTo = (location.state as { from?: string } | null)?.from ?? "/exercises";
  const backLabel = backTo.startsWith("/lesson/") ? "Lecție" : "Exerciții";


  useEffect(() => {
    api
      .get<TopicCategoriesResponse>(`/progress/topics/${topicId}/categories/`)
      .then((res) => setData(res.data))
      .catch(() => setError("Nu am putut încărca exercițiile."))
      .finally(() => setLoading(false));
  }, [topicId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">{error ?? "Eroare."}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-4">
          <button
            onClick={() => navigate(backTo)}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{backLabel}</span>
          </button>
          <span className="text-gray-300">|</span>
          <span className="text-sm font-medium text-gray-700 truncate">{data.topic_title}</span>
        </div>
      </div>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-xl font-bold text-gray-900 mb-6">{data.topic_title}</h1>

        {data.categories.length === 0 && (
          <p className="text-gray-400 text-center py-12">Nicio categorie disponibilă.</p>
        )}

        <div className="space-y-4">
          {data.categories.map((cat) => (
            <CategoryCard
              key={cat.category}
              category={cat}
              topicId={topicId!}
              origin={backTo}
            />
          ))}
        </div>
      </main>
    </div>
  );
}

function CategoryCard({
  category,
  topicId,
  origin,
}: {
  category: CategoryInfo;
  topicId: string;
  origin: string;
}) {
  const navigate = useNavigate();
  const label = CATEGORY_LABELS[category.category] ?? category.category;

  const startPractice = (difficulty: Difficulty) => {
    navigate(`/topic/${topicId}/practice`, {
      state: { category: category.category, difficulty, from: origin },
    });
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">{label}</h3>
        <div className="text-xs text-gray-400">
          {category.exercises_attempted} încercări · {category.perfect_batches} perfecte
        </div>
      </div>

      <div className="flex gap-2">
        {(["easy", "medium", "hard"] as Difficulty[]).map((diff) => {
          const tier = category.tiers[diff];
          if (!tier.available) {
            return (
              <div
                key={diff}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-gray-100 text-gray-400 text-sm cursor-not-allowed"
              >
                <Lock className="w-3 h-3" />
                <span>{DIFFICULTY_LABEL[diff]}</span>
              </div>
            );
          }
          return (
            <button
              key={diff}
              onClick={() => startPractice(diff)}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${DIFFICULTY_COLOR[diff]} ${
                tier.cleared ? "ring-2 ring-offset-1 ring-current" : ""
              }`}
            >
              {tier.cleared && <Star className="w-3 h-3 fill-current" />}
              <span>{DIFFICULTY_LABEL[diff]}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
