/**
 * Wardrobe modal — opens from the avatar on /profile.
 *
 * Three tabs (Frame / Avatar / Theme). A persistent preview circle at
 * the top reflects the live avatar+frame combo and updates on equip.
 * Themes have no in-modal preview — equipping one restyles the profile
 * page visible behind the dim, which is the preview.
 *
 * Constraints from Phase 5:
 * - The avatar tab manages all three sources together: a Monogram
 *   chip (always selectable), an Upload row (file input + current
 *   image), and a grid of preset avatars (click owned to equip → flips
 *   source to preset).
 * - Locked items show the unlock requirement the API already provides.
 * - Outside-click, X, and ESC close the modal; the URL state survives
 *   back/refresh (the parent owns the `open` prop and is responsible
 *   for the URL plumbing).
 */
import {
  type ChangeEvent,
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";
import { Upload, UserRound, X } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { useCosmetics } from "@/hooks/useCosmetics";
import type { AvatarSource, CosmeticEntry, CosmeticType } from "@/types/cosmetics";

import AvatarPreview, { buildPreviewSelection } from "./AvatarPreview";
import CosmeticVisual from "./CosmeticVisual";
import { iconForType, Lock } from "./assetRegistry";

interface WardrobeModalProps {
  open: boolean;
  onClose: () => void;
}

type TabKey = CosmeticType;

const TAB_LABELS: Record<TabKey, string> = {
  frame: "Rame",
  avatar: "Avataruri",
  profile_theme: "Teme",
};

const TAB_ORDER: TabKey[] = ["frame", "avatar", "profile_theme"];

const SOURCE_LABELS: Record<AvatarSource, string> = {
  monogram: "Inițiale",
  upload: "Imagine încărcată",
  preset: "Avatar echipat",
};

export default function WardrobeModal({ open, onClose }: WardrobeModalProps) {
  const { user } = useAuth();
  const { state, loading, equip, upload, changeSource } = useCosmetics();
  const [tab, setTab] = useState<TabKey>("frame");
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Close on ESC.
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  // Reset transient UI state every time the modal opens — stale errors
  // from the previous session should not greet the user.
  useEffect(() => {
    if (open) {
      setActionError(null);
      setTab("frame");
    }
  }, [open]);

  const initials = useMemo(() => {
    if (!user) return "?";
    return `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`;
  }, [user]);

  const preview = useMemo(() => {
    if (!state) return null;
    return buildPreviewSelection(
      state.cosmetics,
      state.equipped,
      state.avatar_source,
      state.avatar_image_url,
    );
  }, [state]);

  const handleEquip = useCallback(
    async (slug: string) => {
      if (busy) return;
      setBusy(true);
      setActionError(null);
      try {
        await equip(slug);
      } catch (err: unknown) {
        const e = err as { response?: { data?: { error?: string } } };
        setActionError(
          e.response?.data?.error ?? "Nu am putut echipa cosmeticul.",
        );
      } finally {
        setBusy(false);
      }
    },
    [busy, equip],
  );

  const handleSourceChange = useCallback(
    async (source: AvatarSource) => {
      if (busy) return;
      setBusy(true);
      setActionError(null);
      try {
        await changeSource(source);
      } catch (err: unknown) {
        const e = err as { response?: { data?: { error?: string } } };
        setActionError(
          e.response?.data?.error ?? "Nu am putut schimba sursa avatarului.",
        );
      } finally {
        setBusy(false);
      }
    },
    [busy, changeSource],
  );

  const handleFileChange = useCallback(
    async (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      // Reset the input so the same file can be re-uploaded after an
      // error (the change event won't fire again for an identical
      // selection otherwise).
      e.target.value = "";
      if (!file || busy) return;
      setBusy(true);
      setActionError(null);
      try {
        await upload(file);
      } catch (err: unknown) {
        const ex = err as { response?: { data?: { error?: string } } };
        setActionError(
          ex.response?.data?.error ?? "Nu am putut încărca imaginea.",
        );
      } finally {
        setBusy(false);
      }
    },
    [busy, upload],
  );

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-6"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Dressing — alege-ți cosmeticele"
    >
      <div
        className="relative w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-2xl bg-white shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
          aria-label="Închide"
        >
          <X className="h-5 w-5" />
        </button>

        {/* ── Preview ──────────────────────────────────────────────── */}
        <div className="flex flex-col items-center px-6 pt-8 pb-4">
          {preview ? (
            <AvatarPreview
              size="lg"
              avatarSource={preview.avatarSource}
              avatarImageUrl={preview.avatarImageUrl}
              presetAssetRef={preview.presetAssetRef}
              frameAssetRef={preview.frameAssetRef}
              initials={initials}
            />
          ) : (
            <div className="h-24 w-24 rounded-full bg-gray-100 animate-pulse" />
          )}
          <p className="mt-3 text-sm text-gray-500">
            {state?.avatar_source
              ? `Sursă: ${SOURCE_LABELS[state.avatar_source]}`
              : "—"}
          </p>
        </div>

        {/* ── Tabs ─────────────────────────────────────────────────── */}
        <div className="flex gap-1 border-b border-gray-200 px-6">
          {TAB_ORDER.map((key) => (
            <TabButton
              key={key}
              active={tab === key}
              onClick={() => setTab(key)}
              icon={iconForType(key)}
              label={TAB_LABELS[key]}
              count={state ? countOwned(state.cosmetics, key) : null}
              total={
                state ? countOfType(state.cosmetics, key) : null
              }
            />
          ))}
        </div>

        {actionError && (
          <div className="mx-6 mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-2 text-sm text-rose-700">
            {actionError}
          </div>
        )}

        {/* ── Tab content ──────────────────────────────────────────── */}
        {/* Generous bottom padding so unlock tooltips on bottom-row
            cards have somewhere to render without being clipped by
            the scroll container. */}
        <div className="flex-1 overflow-y-auto px-6 pt-4 pb-20">
          {loading || !state ? (
            <ContentSkeleton />
          ) : (
            <>
              {tab === "avatar" && (
                <AvatarTab
                  state={state}
                  busy={busy}
                  onEquip={handleEquip}
                  onSourceChange={handleSourceChange}
                  onPickFile={() => fileInputRef.current?.click()}
                />
              )}
              {tab === "frame" && (
                <GridTab
                  entries={state.cosmetics.filter((c) => c.type === "frame")}
                  busy={busy}
                  onEquip={handleEquip}
                  renderItem={(c) => <FrameTile entry={c} />}
                />
              )}
              {tab === "profile_theme" && (
                <GridTab
                  entries={state.cosmetics.filter(
                    (c) => c.type === "profile_theme",
                  )}
                  busy={busy}
                  onEquip={handleEquip}
                  renderItem={(c) => <ThemeTile entry={c} />}
                />
              )}
            </>
          )}
        </div>

        {/* Hidden file input — shared by the Upload row regardless of
            which tab is showing. */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileChange}
        />
      </div>
    </div>
  );
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────

function TabButton({
  active,
  onClick,
  icon,
  label,
  count,
  total,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  count: number | null;
  total: number | null;
}) {
  const base =
    "flex items-center gap-2 border-b-2 px-3 py-3 text-sm font-medium transition-colors";
  const activeClasses = "border-indigo-500 text-indigo-700";
  const inactiveClasses =
    "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-200";
  return (
    <button
      onClick={onClick}
      className={`${base} ${active ? activeClasses : inactiveClasses}`}
    >
      {icon}
      <span>{label}</span>
      {count !== null && total !== null && (
        <span className="text-xs text-gray-400">
          {count}/{total}
        </span>
      )}
    </button>
  );
}

// ─── Avatar tab ───────────────────────────────────────────────────────────────

interface AvatarTabProps {
  state: NonNullable<ReturnType<typeof useCosmetics>["state"]>;
  busy: boolean;
  onEquip: (slug: string) => void;
  onSourceChange: (source: AvatarSource) => void;
  onPickFile: () => void;
}

function AvatarTab({
  state,
  busy,
  onEquip,
  onSourceChange,
  onPickFile,
}: AvatarTabProps) {
  const avatars = state.cosmetics.filter((c) => c.type === "avatar");
  const source = state.avatar_source;
  const hasUpload = Boolean(state.avatar_image_url);

  return (
    <div className="space-y-6">
      {/* Source switchers + upload row. The three sources live together
          on this tab so the student manages "what is my avatar showing
          right now" in one place. */}
      <div>
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          Sursă avatar
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <SourceChip
            active={source === "monogram"}
            disabled={busy}
            onClick={() => onSourceChange("monogram")}
            label="Inițiale"
            description="Implicit"
            icon={<UserRound className="h-4 w-4" aria-hidden />}
          />
          <UploadChip
            active={source === "upload"}
            disabled={busy}
            hasUpload={hasUpload}
            onSwitch={() => onSourceChange("upload")}
            onPickFile={onPickFile}
            imageUrl={state.avatar_image_url}
          />
        </div>
      </div>

      {/* Preset grid */}
      <div>
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          Avataruri preset
        </h4>
        <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
          {avatars.map((entry) => (
            <CosmeticCard
              key={entry.slug}
              entry={entry}
              busy={busy}
              onEquip={onEquip}
              renderVisual={() => <AvatarTile entry={entry} />}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function SourceChip({
  active,
  disabled,
  onClick,
  label,
  description,
  icon,
}: {
  active: boolean;
  disabled: boolean;
  onClick: () => void;
  label: string;
  description: string;
  icon: React.ReactNode;
}) {
  const base =
    "flex items-center gap-3 rounded-xl border px-4 py-3 text-left transition-all";
  const activeClasses = "border-indigo-400 bg-indigo-50";
  const inactiveClasses = "border-gray-200 hover:border-gray-300";
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${active ? activeClasses : inactiveClasses} disabled:opacity-60`}
    >
      <span className={active ? "text-indigo-600" : "text-gray-400"}>
        {icon}
      </span>
      <span className="flex-1">
        <span className="block text-sm font-medium text-gray-900">{label}</span>
        <span className="block text-xs text-gray-500">{description}</span>
      </span>
      {active && <ActiveDot />}
    </button>
  );
}

function UploadChip({
  active,
  disabled,
  hasUpload,
  onSwitch,
  onPickFile,
  imageUrl,
}: {
  active: boolean;
  disabled: boolean;
  hasUpload: boolean;
  onSwitch: () => void;
  onPickFile: () => void;
  imageUrl: string | null;
}) {
  const base =
    "flex items-center gap-3 rounded-xl border px-4 py-3 text-left transition-all";
  const activeClasses = "border-indigo-400 bg-indigo-50";
  const inactiveClasses = "border-gray-200 hover:border-gray-300";

  return (
    <div className={`${base} ${active ? activeClasses : inactiveClasses}`}>
      {hasUpload && imageUrl ? (
        <img
          src={imageUrl}
          alt=""
          className="h-9 w-9 rounded-full object-cover"
        />
      ) : (
        <span className="h-9 w-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-400">
          <Upload className="h-4 w-4" aria-hidden />
        </span>
      )}
      <div className="flex-1 min-w-0">
        <span className="block text-sm font-medium text-gray-900">
          {hasUpload ? "Imagine încărcată" : "Încarcă o imagine"}
        </span>
        <div className="flex flex-wrap gap-2 mt-1">
          {hasUpload && !active && (
            <button
              onClick={onSwitch}
              disabled={disabled}
              className="text-xs font-medium text-indigo-600 hover:text-indigo-700 disabled:opacity-60"
            >
              Folosește
            </button>
          )}
          <button
            onClick={onPickFile}
            disabled={disabled}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-700 disabled:opacity-60"
          >
            {hasUpload ? "Schimbă" : "Selectează fișier"}
          </button>
        </div>
      </div>
      {active && <ActiveDot />}
    </div>
  );
}

function ActiveDot() {
  return (
    <span
      className="h-2.5 w-2.5 rounded-full bg-indigo-500"
      aria-label="Activ"
    />
  );
}

// ─── Grid tab (frames + themes) ───────────────────────────────────────────────

interface GridTabProps {
  entries: CosmeticEntry[];
  busy: boolean;
  onEquip: (slug: string) => void;
  renderItem: (entry: CosmeticEntry) => React.ReactNode;
}

function GridTab({ entries, busy, onEquip, renderItem }: GridTabProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      {entries.map((entry) => (
        <CosmeticCard
          key={entry.slug}
          entry={entry}
          busy={busy}
          onEquip={onEquip}
          renderVisual={() => renderItem(entry)}
        />
      ))}
    </div>
  );
}

// ─── Cosmetic card (shared by all tabs) ───────────────────────────────────────

interface CosmeticCardProps {
  entry: CosmeticEntry;
  busy: boolean;
  onEquip: (slug: string) => void;
  renderVisual: () => React.ReactNode;
}

function CosmeticCard({
  entry,
  busy,
  onEquip,
  renderVisual,
}: CosmeticCardProps) {
  const locked = !entry.owned;
  const equipped = entry.equipped;
  const clickable = entry.owned && !equipped && !busy;
  const tooltipId = useId();
  // Tap-toggle for touch devices that lack hover. Hover on desktop uses
  // group-hover instead, so this state only matters on touch + the
  // accessibility focus path.
  const [revealed, setRevealed] = useState(false);

  const handleClick = () => {
    if (locked) {
      setRevealed((v) => !v);
      return;
    }
    if (clickable) onEquip(entry.slug);
  };

  const base =
    "group relative rounded-xl border p-3 flex flex-col items-center gap-2 transition-all focus:outline-none focus:ring-2 focus:ring-indigo-300";
  const stateClasses = equipped
    ? "border-indigo-400 bg-indigo-50 ring-1 ring-indigo-300 cursor-default"
    : locked
      ? "border-gray-200 opacity-80 cursor-help"
      : "border-gray-200 hover:border-indigo-300 hover:shadow-sm cursor-pointer";

  // A locked card is still interactive — tap to reveal the tooltip on
  // touch — but a card whose cosmetic is already equipped has nothing to
  // do. Disabling that one (and only that one) keeps screen readers
  // honest about which surface accepts input.
  const interactive = clickable || locked;

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={!interactive}
      className={`${base} ${stateClasses}`}
      aria-describedby={locked ? tooltipId : undefined}
      aria-expanded={locked ? revealed : undefined}
    >
      <div className="relative">
        {renderVisual()}
        {locked && (
          <span className="absolute inset-0 flex items-center justify-center rounded-full bg-white/70">
            <Lock className="h-4 w-4 text-gray-500" aria-hidden />
          </span>
        )}
      </div>
      <span className="text-xs font-medium text-gray-800 text-center line-clamp-2">
        {entry.display_name}
      </span>
      {locked ? (
        <span className="text-[10px] text-gray-500 text-center">
          {unlockLabel(entry)}
        </span>
      ) : equipped ? (
        <span className="text-[10px] font-semibold text-indigo-600 uppercase tracking-wider">
          Echipat
        </span>
      ) : (
        <span className="text-[10px] text-gray-400 uppercase tracking-wider">
          Click pentru a echipa
        </span>
      )}
      {locked && entry.unlock && (
        <UnlockTooltip id={tooltipId} entry={entry} revealed={revealed} />
      )}
    </button>
  );
}

/**
 * Hover/tap popup carrying the fuller unlock instruction.
 *
 * - Hover: visible via `group-hover` (the card is the `group`).
 * - Keyboard focus: visible via `group-focus` so a Tab-only user sees it.
 * - Touch: parent flips `revealed` on tap so the popup appears without
 *   needing hover semantics.
 *
 * Positioned below the card with absolute placement. The modal's
 * content region is `overflow-y-auto`, not `overflow-hidden`, so a
 * tooltip extending past the visible viewport remains reachable by
 * scrolling rather than being clipped.
 */
function UnlockTooltip({
  id,
  entry,
  revealed,
}: {
  id: string;
  entry: CosmeticEntry;
  revealed: boolean;
}) {
  const u = entry.unlock;
  if (!u) return null;
  const description = u.description;
  const visibility = revealed
    ? "opacity-100"
    : "opacity-0 group-hover:opacity-100 group-focus:opacity-100";
  return (
    <div
      id={id}
      role="tooltip"
      className={`pointer-events-none absolute left-1/2 top-full z-30 mt-2 w-52 -translate-x-1/2 rounded-lg bg-gray-900 px-3 py-2 text-left text-xs text-white shadow-lg transition-opacity ${visibility}`}
    >
      <p className="font-semibold leading-snug">{unlockLabel(entry)}</p>
      {description && (
        <p className="mt-1 text-gray-200 leading-snug">{description}</p>
      )}
      <span
        aria-hidden
        className="absolute left-1/2 -top-1 h-2 w-2 -translate-x-1/2 rotate-45 bg-gray-900"
      />
    </div>
  );
}

function unlockLabel(entry: CosmeticEntry): string {
  const u = entry.unlock;
  if (!u) return "Blocat";
  if (u.kind === "xp_threshold") return `${u.xp.toLocaleString("ro-RO")} XP`;
  if (u.kind === "achievement") return `Insignă: ${u.label}`;
  if (u.kind === "quest_reward") return `Misiune: ${u.label}`;
  return "Blocat";
}

// Per-tab tile renderers — thin wrappers around the shared CosmeticVisual
// so the modal grid and the unlock toast stay visually aligned.

function FrameTile({ entry }: { entry: CosmeticEntry }) {
  return <CosmeticVisual type="frame" assetRef={entry.asset_ref} size="md" />;
}

function ThemeTile({ entry }: { entry: CosmeticEntry }) {
  return (
    <CosmeticVisual type="profile_theme" assetRef={entry.asset_ref} size="md" />
  );
}

function AvatarTile({ entry }: { entry: CosmeticEntry }) {
  return <CosmeticVisual type="avatar" assetRef={entry.asset_ref} size="md" />;
}

// ─── Misc ─────────────────────────────────────────────────────────────────────

function ContentSkeleton() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="rounded-xl border border-gray-200 p-3 h-32 animate-pulse bg-gray-50"
        />
      ))}
    </div>
  );
}

function countOwned(cosmetics: CosmeticEntry[], type: CosmeticType): number {
  return cosmetics.filter((c) => c.type === type && c.owned).length;
}

function countOfType(cosmetics: CosmeticEntry[], type: CosmeticType): number {
  return cosmetics.filter((c) => c.type === type).length;
}
