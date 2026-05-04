export type BadgeFamily = "progress" | "mastery" | "consistency" | "discovery";

export interface Badge {
  key: string;
  name: string | null;
  description: string | null;
  icon_name: string | null;
  family: BadgeFamily;
  secret: boolean;
  earned?: boolean;
  earned_at?: string | null;
}

export interface AchievementListResponse {
  achievements: Badge[];
}
