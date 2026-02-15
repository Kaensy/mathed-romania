import api from "./client";
import type {
  AuthResponse,
  LoginData,
  StudentRegistrationData,
  TeacherRegistrationData,
  User,
} from "@/types/auth";

export const authApi = {
  registerStudent: (data: StudentRegistrationData) =>
    api.post<AuthResponse>("/auth/register/student/", data),

  registerTeacher: (data: TeacherRegistrationData) =>
    api.post<AuthResponse>("/auth/register/teacher/", data),

  login: (data: LoginData) =>
    api.post<AuthResponse>("/auth/login/", data),

  logout: () =>
    api.post("/auth/logout/"),

  getProfile: () =>
    api.get<User>("/auth/me/"),

  refreshToken: () =>
    api.post("/auth/token/refresh/"),

  requestPasswordReset: (email: string) =>
    api.post("/auth/password-reset/", { email }),

  confirmPasswordReset: (data: {
    uid: string;
    token: string;
    new_password: string;
    new_password_confirm: string;
  }) => api.post("/auth/password-reset/confirm/", data),

  approveConsent: (uid: string, token: string) =>
    api.post("/auth/consent/approve/", { uid, token }),
};
