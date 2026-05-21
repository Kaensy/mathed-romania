/**
 * Cosmetics state context — single source of truth for the wardrobe.
 *
 * Why a context, not just a hook: the wardrobe modal and the profile
 * page both read the equipped frame, theme, and avatar. With a stateful
 * `useCosmetics` hook each consumer held its own local copy, and an
 * equip action in the modal couldn't push the new state into the
 * profile's copy — only a remount/reload would refresh it. Lifting the
 * state into a provider means every consumer re-renders the moment the
 * equip response patches the shared state.
 *
 * The provider only fetches when the authenticated user is a student
 * (the endpoint 403s for everyone else). It re-fetches whenever the
 * cosmetic-notification context's `unlockVersion` increments, so a
 * cosmetic surfaced by any other API response (exercise attempt, test
 * finish, quest claim) appears in the wardrobe without manual reload.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  equipCosmetic as apiEquipCosmetic,
  getCosmetics,
  setAvatarSource as apiSetAvatarSource,
  uploadAvatar as apiUploadAvatar,
} from "@/api/cosmetics";
import { useCosmeticNotifications } from "@/contexts/CosmeticNotificationContext";
import { useAuth } from "@/hooks/useAuth";
import type {
  AvatarSource,
  AvatarStateResponse,
  CosmeticEquipResponse,
  CosmeticState,
} from "@/types/cosmetics";

interface CosmeticsContextType {
  state: CosmeticState | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  equip: (slug: string) => Promise<CosmeticEquipResponse>;
  upload: (file: File) => Promise<AvatarStateResponse>;
  changeSource: (source: AvatarSource) => Promise<AvatarStateResponse>;
}

const CosmeticsContext = createContext<CosmeticsContextType | null>(null);

export function CosmeticsProvider({ children }: { children: ReactNode }) {
  const { user, isLoading: authLoading } = useAuth();
  const { unlockVersion } = useCosmeticNotifications();

  // Only students have cosmetics. For everyone else (teacher, admin,
  // anonymous) we never call the endpoint at all — the backend would
  // 403, which would surface as a useless error in this context.
  const isStudent = !authLoading && user?.user_type === "student";

  // Mirror loading behaviour: while auth is resolving, we say `loading`
  // so consumers don't flash a "no cosmetics" empty state before the
  // first real fetch fires.
  const [state, setState] = useState<CosmeticState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!isStudent) {
      setState(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setState(await getCosmetics());
    } catch {
      setError("Nu am putut încărca cosmeticele.");
    } finally {
      setLoading(false);
    }
  }, [isStudent]);

  // Fetch on every student-auth resolution and on every fresh unlock
  // surfaced by some other request. `unlockVersion` starts at 0, so a
  // student auth + zero unlocks still triggers exactly one initial
  // fetch.
  useEffect(() => {
    load();
  }, [load, unlockVersion]);

  // Local-state patcher shared by `equip`. Updates the equipped map,
  // avatar block, and the per-entry `equipped` flag so subscribers see
  // a coherent post-equip snapshot without a refetch.
  const applyEquipResponse = useCallback(
    (prev: CosmeticState, res: CosmeticEquipResponse): CosmeticState => {
      const newlyEquipped = new Set(
        Object.values(res.equipped).filter(
          (s): s is string => typeof s === "string",
        ),
      );
      return {
        ...prev,
        equipped: res.equipped,
        avatar_source: res.avatar_source,
        avatar_image_url: res.avatar_image_url,
        cosmetics: prev.cosmetics.map((c) => ({
          ...c,
          equipped: newlyEquipped.has(c.slug),
        })),
      };
    },
    [],
  );

  const equip = useCallback(
    async (slug: string): Promise<CosmeticEquipResponse> => {
      const res = await apiEquipCosmetic(slug);
      setState((prev) => (prev ? applyEquipResponse(prev, res) : prev));
      return res;
    },
    [applyEquipResponse],
  );

  const upload = useCallback(
    async (file: File): Promise<AvatarStateResponse> => {
      const res = await apiUploadAvatar(file);
      setState((prev) =>
        prev
          ? {
              ...prev,
              avatar_source: res.avatar_source,
              avatar_image_url: res.avatar_image_url,
            }
          : prev,
      );
      return res;
    },
    [],
  );

  const changeSource = useCallback(
    async (source: AvatarSource): Promise<AvatarStateResponse> => {
      const res = await apiSetAvatarSource(source);
      setState((prev) =>
        prev
          ? {
              ...prev,
              avatar_source: res.avatar_source,
              avatar_image_url: res.avatar_image_url,
            }
          : prev,
      );
      return res;
    },
    [],
  );

  const value = useMemo(
    () => ({ state, loading, error, refetch: load, equip, upload, changeSource }),
    [state, loading, error, load, equip, upload, changeSource],
  );

  return (
    <CosmeticsContext.Provider value={value}>
      {children}
    </CosmeticsContext.Provider>
  );
}

/**
 * Subscribe to the shared cosmetic state. Must be mounted under
 * <CosmeticsProvider /> — App.tsx wires that for every authenticated
 * route. Non-student users get `state: null` without any API traffic.
 */
export function useCosmeticsContext(): CosmeticsContextType {
  const ctx = useContext(CosmeticsContext);
  if (!ctx) {
    throw new Error(
      "useCosmeticsContext must be used within a CosmeticsProvider",
    );
  }
  return ctx;
}
