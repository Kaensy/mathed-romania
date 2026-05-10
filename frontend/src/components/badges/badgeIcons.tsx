import type { ComponentType } from "react";
import {
  GiBookCover,
  GiCalendar,
  GiCometSpark,
  GiCompass,
  GiCrown,
  GiCrossedSwords,
  GiCrystalGrowth,
  GiCutDiamond,
  GiFlame,
  GiFootprint,
  GiMedal,
  GiPawPrint,
  GiScrollUnfurled,
  GiSparkles,
  GiStarsStack,
  GiTrophy,
  GiWolfHead,
  GiWolfHowl,
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
  paw: GiPawPrint,
  wolf_howl: GiWolfHowl,
  wolf_head: GiWolfHead,
  sparkles: GiSparkles,
  crystal_growth: GiCrystalGrowth,
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
