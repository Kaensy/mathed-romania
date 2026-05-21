export type UserType = "student" | "teacher" | "admin";

export interface StudentProfile {
  grade: number;
  birth_date: string;
  consent_status: "pending" | "approved" | "denied";
  total_xp: number;
  account_level: number;
  xp_into_level: number;
  xp_for_next_level: number;
  xp_to_next_level: number;
}

export interface TeacherProfile {
  referral_code: string;
  school_name: string;
  commission_rate: number;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  user_type: UserType;
  profile: StudentProfile | TeacherProfile | null;
  created_at: string;
}

export interface StudentRegistrationData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  grade: number;
  birth_date: string;
  parent_email?: string;
}

export interface TeacherRegistrationData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  school_name?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  message: string;
  user?: User;
  requires_consent?: boolean;
}

export interface ApiError {
  [key: string]: string | string[];
}
