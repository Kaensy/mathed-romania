import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { authApi } from "@/api/auth";

export default function ConsentApprovePage() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const uid = searchParams.get("uid");
    const token = searchParams.get("token");

    if (!uid || !token) {
      setStatus("error");
      setMessage("Link invalid. Parametrii lipsesc.");
      return;
    }

    const approve = async () => {
      try {
        const response = await authApi.approveConsent(uid, token);
        setStatus("success");
        setMessage(response.data.message);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { error?: string } } };
        setStatus("error");
        setMessage(error.response?.data?.error || "A apărut o eroare.");
      }
    };

    approve();
  }, [searchParams]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
        {status === "loading" && (
          <>
            <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
            <p className="text-gray-600">Se procesează aprobarea...</p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
              <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-gray-900">Consimțământ aprobat</h2>
            <p className="mt-3 text-sm text-gray-600">{message}</p>
            <p className="mt-2 text-sm text-gray-600">
              Elevul se poate autentifica acum pe platformă.
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
              <svg className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-gray-900">Eroare</h2>
            <p className="mt-3 text-sm text-gray-600">{message}</p>
          </>
        )}

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
