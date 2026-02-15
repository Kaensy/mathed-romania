import { Routes, Route } from "react-router-dom";

function HomePage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-primary-900">
          MathEd Romania
        </h1>
        <p className="mt-3 text-lg text-primary-700">
          Platformă educațională de matematică pentru clasele 5–8
        </p>
        <p className="mt-6 text-sm text-gray-500">Phase 0 — Foundation ✓</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      {/* Phase 1: Auth routes */}
      {/* Phase 3: Lesson routes */}
    </Routes>
  );
}
