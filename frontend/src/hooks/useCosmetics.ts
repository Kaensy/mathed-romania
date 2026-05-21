/**
 * Cosmetic data hook — a thin alias for the shared context.
 *
 * State, load timing, equip/upload/changeSource mutations, and the
 * unlock-version refetch trigger all live in `CosmeticsProvider`. This
 * hook is a single-line read so existing call sites
 * (`useCosmetics().state`, `useCosmetics().equip`) keep working while
 * every consumer renders off one source of truth — equipping in the
 * wardrobe modal now propagates through React to the profile page's
 * theme + avatar+frame display without a page reload.
 */
export { useCosmeticsContext as useCosmetics } from "@/contexts/CosmeticsContext";
