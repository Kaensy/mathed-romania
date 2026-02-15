import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi } from "@/api/auth";
import { useAuth } from "@/hooks/useAuth";
import type { ApiError } from "@/types/auth";

type AccountType = "student" | "teacher";

export default function RegisterPage() {
  const [accountType, setAccountType] = useState<AccountType>("student");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<ApiError>({});
  const [consentMessage, setConsentMessage] = useState("");

  // Shared fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  // Student-only fields
  const [grade, setGrade] = useState(5);
  const [birthDate, setBirthDate] = useState("");
  const [parentEmail, setParentEmail] = useState("");

  // Teacher-only fields
  const [schoolName, setSchoolName] = useState("");

  const { setUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setConsentMessage("");
    setIsSubmitting(true);

    try {
      if (accountType === "student") {
        const response = await authApi.registerStudent({
          email,
          password,
          password_confirm: passwordConfirm,
          first_name: firstName,
          last_name: lastName,
          grade,
          birth_date: birthDate,
          parent_email: parentEmail || undefined,
        });

        if (response.data.requires_consent) {
          setConsentMessage(response.data.message);
          setIsSubmitting(false);
          return;
        }

        if (response.data.user) {
          setUser(response.data.user);
          navigate("/dashboard", { replace: true });
        }
      } else {
        const response = await authApi.registerTeacher({
          email,
          password,
          password_confirm: passwordConfirm,
          first_name: firstName,
          last_name: lastName,
          school_name: schoolName || undefined,
        });

        if (response.data.user) {
          setUser(response.data.user);
          navigate("/dashboard", { replace: true });
        }
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: ApiError } };
      if (error.response?.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: "A apărut o eroare. Încearcă din nou." });
      }
      setIsSubmitting(false);
    }
  };

  const getFieldError = (field: string): string => {
    const err = errors[field];
    if (!err) return "";
    return Array.isArray(err) ? err[0] : err;
  };

  // If consent was needed, show success message
  if (consentMessage) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900">Verifică email-ul părintelui</h2>
          <p className="mt-3 text-sm text-gray-600">{consentMessage}</p>
          <Link
            to="/login"
            className="mt-6 inline-block text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            Mergi la autentificare
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4 py-8">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Înregistrare</h1>
          <p className="mt-2 text-sm text-gray-500">Creează-ți un cont MathEd Romania</p>
        </div>

        {/* Account type toggle */}
        <div className="mb-6 flex rounded-lg bg-gray-100 p-1">
          <button
            type="button"
            onClick={() => setAccountType("student")}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition ${
              accountType === "student"
                ? "bg-white text-primary-700 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Elev
          </button>
          <button
            type="button"
            onClick={() => setAccountType("teacher")}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition ${
              accountType === "teacher"
                ? "bg-white text-primary-700 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Profesor
          </button>
        </div>

        {/* General errors */}
        {(errors.general || errors.non_field_errors) && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            {getFieldError("general") || getFieldError("non_field_errors")}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="firstName" className="mb-1 block text-sm font-medium text-gray-700">
                Prenume
              </label>
              <input
                id="firstName"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              />
              {getFieldError("first_name") && (
                <p className="mt-1 text-xs text-red-600">{getFieldError("first_name")}</p>
              )}
            </div>
            <div>
              <label htmlFor="lastName" className="mb-1 block text-sm font-medium text-gray-700">
                Nume
              </label>
              <input
                id="lastName"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              />
              {getFieldError("last_name") && (
                <p className="mt-1 text-xs text-red-600">{getFieldError("last_name")}</p>
              )}
            </div>
          </div>

          {/* Email */}
          <div>
            <label htmlFor="regEmail" className="mb-1 block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="regEmail"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              placeholder="exemplu@email.com"
            />
            {getFieldError("email") && (
              <p className="mt-1 text-xs text-red-600">{getFieldError("email")}</p>
            )}
          </div>

          {/* Password */}
          <div>
            <label htmlFor="regPassword" className="mb-1 block text-sm font-medium text-gray-700">
              Parolă
            </label>
            <input
              id="regPassword"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              placeholder="Minim 8 caractere"
            />
            {getFieldError("password") && (
              <p className="mt-1 text-xs text-red-600">{getFieldError("password")}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label htmlFor="regPasswordConfirm" className="mb-1 block text-sm font-medium text-gray-700">
              Confirmă parola
            </label>
            <input
              id="regPasswordConfirm"
              type="password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              required
              minLength={8}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              placeholder="••••••••"
            />
            {getFieldError("password_confirm") && (
              <p className="mt-1 text-xs text-red-600">{getFieldError("password_confirm")}</p>
            )}
          </div>

          {/* Student-only fields */}
          {accountType === "student" && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="grade" className="mb-1 block text-sm font-medium text-gray-700">
                    Clasa
                  </label>
                  <select
                    id="grade"
                    value={grade}
                    onChange={(e) => setGrade(Number(e.target.value))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
                  >
                    <option value={5}>Clasa a V-a</option>
                    <option value={6}>Clasa a VI-a</option>
                    <option value={7}>Clasa a VII-a</option>
                    <option value={8}>Clasa a VIII-a</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="birthDate" className="mb-1 block text-sm font-medium text-gray-700">
                    Data nașterii
                  </label>
                  <input
                    id="birthDate"
                    type="date"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    required
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
                  />
                  {getFieldError("birth_date") && (
                    <p className="mt-1 text-xs text-red-600">{getFieldError("birth_date")}</p>
                  )}
                </div>
              </div>

              <div>
                <label htmlFor="parentEmail" className="mb-1 block text-sm font-medium text-gray-700">
                  Email-ul părintelui
                  <span className="ml-1 font-normal text-gray-400">(obligatoriu sub 16 ani)</span>
                </label>
                <input
                  id="parentEmail"
                  type="email"
                  value={parentEmail}
                  onChange={(e) => setParentEmail(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
                  placeholder="parinte@email.com"
                />
                {getFieldError("parent_email") && (
                  <p className="mt-1 text-xs text-red-600">{getFieldError("parent_email")}</p>
                )}
              </div>
            </>
          )}

          {/* Teacher-only fields */}
          {accountType === "teacher" && (
            <div>
              <label htmlFor="schoolName" className="mb-1 block text-sm font-medium text-gray-700">
                Școala
                <span className="ml-1 font-normal text-gray-400">(opțional)</span>
              </label>
              <input
                id="schoolName"
                type="text"
                value={schoolName}
                onChange={(e) => setSchoolName(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
                placeholder="Colegiul Național..."
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-primary-600 py-2.5 text-sm font-semibold text-white transition hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? "Se creează contul..." : "Creează cont"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          Ai deja un cont?{" "}
          <Link to="/login" className="font-medium text-primary-600 hover:text-primary-700">
            Autentifică-te
          </Link>
        </p>
      </div>
    </div>
  );
}
