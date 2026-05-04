import { FAMILY_COLORS, getBadgeIcon } from "./badgeIcons";
import type { BadgeFamily } from "@/types/badges";

interface BadgeIconProps {
  iconName: string | null | undefined;
  family: BadgeFamily;
  size?: number;
  muted?: boolean;
}

const FAMILY_TEXT_CLASS: Record<BadgeFamily, string> = {
  progress: "text-indigo-500",
  mastery: "text-amber-500",
  consistency: "text-orange-500",
  discovery: "text-teal-500",
};

export default function BadgeIcon({
  iconName,
  family,
  size = 32,
  muted = false,
}: BadgeIconProps) {
  const Icon = getBadgeIcon(iconName);
  const colorClass = muted ? "text-slate-400" : FAMILY_TEXT_CLASS[family];
  return (
    <Icon
      size={size}
      className={colorClass}
      aria-hidden
      data-family={family}
      data-color={FAMILY_COLORS[family]}
    />
  );
}
