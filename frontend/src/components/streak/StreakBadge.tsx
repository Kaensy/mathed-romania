import { Flame } from "lucide-react";

interface StreakBadgeProps {
  count: number;
  onClick: () => void;
}

export default function StreakBadge({ count, onClick }: StreakBadgeProps) {
  const isActive = count > 0;

  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold transition-colors ${
        isActive
          ? "bg-orange-100 text-orange-700 hover:bg-orange-200"
          : "bg-gray-100 text-gray-400 hover:bg-gray-200"
      }`}
      title="Streak"
    >
      <Flame className={`w-4 h-4 ${isActive ? "text-orange-500" : "text-gray-400"}`} />
      <span>{count}</span>
    </button>
  );
}
