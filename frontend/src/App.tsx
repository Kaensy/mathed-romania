import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/hooks/useAuth";
import ProtectedRoute from "@/components/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import ForgotPasswordPage from "@/pages/ForgotPasswordPage";
import ResetPasswordPage from "@/pages/ResetPasswordPage";
import ConsentApprovePage from "@/pages/ConsentApprovePage";
import LessonViewer from "@/components/lesson/LessonViewer";
import GradePage from "@/pages/GradePage";
import PracticePage from "@/pages/PracticePage"
import TestPage from "@/pages/TestPage";
import DailyTestPage from "@/pages/DailyTestPage";
import ExerciseHubPage from "@/pages/ExerciseHubPage";
import ExercisesOverviewPage from "@/pages/ExercisesOverviewPage";
import TestsOverviewPage from "@/pages/TestsOverviewPage";
import AdminPreviewPage from "@/pages/AdminPreviewPage";
import ProfilePage from "@/pages/ProfilePage";
import TestHistoryPage from "@/pages/TestHistoryPage";

/**
 * Redirects authenticated users away from auth pages (login, register).
 */
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
    return (
    <Routes>
      {/* Public routes — redirect to dashboard if already logged in */}
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/consent/approve" element={<ConsentApprovePage />} />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
            />
      <Route path="/lesson/:lessonId" element={ <ProtectedRoute> <LessonViewer /> </ProtectedRoute> } />
      <Route path="/grade/:gradeNumber" element={ <ProtectedRoute> <GradePage /> </ProtectedRoute> } />
      <Route path="/test/:testId" element={<ProtectedRoute><TestPage /></ProtectedRoute>} />
      <Route path="/daily" element={<ProtectedRoute allowedTypes={["student"]}><DailyTestPage /></ProtectedRoute>} />
      <Route path="/exercises" element={<ProtectedRoute><ExercisesOverviewPage /></ProtectedRoute>} />
      <Route path="/tests" element={<ProtectedRoute><TestsOverviewPage /></ProtectedRoute>} />
      <Route path="/admin-preview/exercise/:exerciseId" element={<ProtectedRoute><AdminPreviewPage /></ProtectedRoute>} />
      <Route path="/topic/:topicId/exercises" element={<ExerciseHubPage />} />
      <Route path="/topic/:topicId/practice"  element={<PracticePage />} />
      <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="/test-history" element={<ProtectedRoute><TestHistoryPage /></ProtectedRoute>} />


      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
