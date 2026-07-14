/**
 * AEGON Auth — Enterprise Evaluation Mode
 * ========================================
 * This repository ships as an Enterprise Evaluation Edition.
 * Authentication is intentionally disabled so that any reviewer —
 * recruiters, executives, academics — can experience the full platform
 * without creating an account.
 *
 * Production deployments support Clerk, Azure AD, Okta, Auth0, and SAML.
 * See the README > Enterprise Authentication Roadmap for details.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AegonUser {
  email: string;
  name: string;
  role: string;
  department: string | null;
  initials: string;
  clerkUserId: string | null;
}

// ---------------------------------------------------------------------------
// Static Demo User — Enterprise Evaluation Edition
// ---------------------------------------------------------------------------

export const DEMO_USER: AegonUser = {
  email: "evaluation@aegon-platform.io",
  name: "Enterprise Evaluation User",
  role: "Super Administrator",
  department: "Executive Operations",
  initials: "EE",
  clerkUserId: null,
};

// ---------------------------------------------------------------------------
// Hooks — always return the demo user immediately, no network calls
// ---------------------------------------------------------------------------

export function useAegonUser(): {
  user: AegonUser;
  isLoading: boolean;
  isError: boolean;
} {
  return { user: DEMO_USER, isLoading: false, isError: false };
}

export function useAegonAuth() {
  return {
    isLoaded: true,
    isSignedIn: true,
    signOut: () => {},
  };
}

/**
 * Legacy compatibility shim — keeps all existing `useAuth` import sites working.
 */
export function useAuth() {
  return {
    user: DEMO_USER,
    isReady: true,
    logout: () => {},
  };
}
