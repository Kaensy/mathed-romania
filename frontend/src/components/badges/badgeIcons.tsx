import type { ComponentType } from "react";
import {
  GiBookCover,
  GiCalendar,
  GiCometSpark,
  GiCompass,
  GiCrown,
  GiCrossedSwords,
  GiCutDiamond,
  GiFlame,
  GiFootprint,
  GiMedal,
  GiScrollUnfurled,
  GiStarsStack,
  GiTrophy,
} from "react-icons/gi";
import type { IconBaseProps } from "react-icons";

import type { BadgeFamily } from "@/types/badges";

type IconComponent = ComponentType<IconBaseProps>;

const ICON_MAP: Record<string, IconComponent> = {
  footprint: GiFootprint,
  medal: GiMedal,
  scroll: GiScrollUnfurled,
  star: GiStarsStack,
  crown: GiCrown,
  trophy: GiTrophy,
  gem: GiCutDiamond,
  sword: GiCrossedSwords,
  flame: GiFlame,
  calendar: GiCalendar,
  comet: GiCometSpark,
  compass: GiCompass,
  book: GiBookCover,
};

export function getBadgeIcon(slug: string | null | undefined): IconComponent {
  if (!slug) return GiTrophy;
  return ICON_MAP[slug] ?? GiTrophy;
}

export const FAMILY_COLORS: Record<BadgeFamily, string> = {
  progress: "indigo",
  mastery: "amber",
  consistency: "orange",
  discovery: "teal",
};
