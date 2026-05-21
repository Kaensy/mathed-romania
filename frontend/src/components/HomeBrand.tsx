import { Link } from "react-router-dom";
import { Hexagon } from "lucide-react";

/**
 * Top-left home affordance shown in every authenticated page's header.
 * Click routes to /dashboard (the post-login landing route).
 */
export default function HomeBrand({ className = "" }: { className?: string }) {
  return (
    <Link
      to="/dashboard"
      aria-label="Mergi la pagina principală"
      title="Acasă"
      className={`inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300 ${className}`}
    >
      <Hexagon className="h-5 w-5" strokeWidth={2.25} />
    </Link>
  );
}
