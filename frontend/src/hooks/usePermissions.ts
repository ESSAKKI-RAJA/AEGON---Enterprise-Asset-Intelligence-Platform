import { useAegonUser } from "@/lib/auth";

// Permission matrix for the 5 AEGON roles.
// In a fully dynamic system, these come from the backend payload.
const rolePermissions: Record<string, string[]> = {
  "Super Admin": ["*"],
  Admin: [
    "dashboard:read",
    "assets:read",
    "assets:write",
    "assets:delete",
    "maintenance:read",
    "maintenance:write",
    "inventory:read",
    "inventory:write",
    "procurement:read",
    "procurement:write",
    "finance:read",
    "finance:write",
    "analytics:read",
    "reports:read",
    "users:read",
    "users:write",
    "settings:read",
    "settings:write",
  ],
  Manager: [
    "dashboard:read",
    "assets:read",
    "assets:write",
    "maintenance:read",
    "maintenance:write",
    "inventory:read",
    "inventory:write",
    "procurement:read",
    "finance:read",
    "analytics:read",
    "reports:read",
  ],
  Technician: [
    "dashboard:read",
    "assets:read",
    "maintenance:read",
    "maintenance:write",
    "maintenance:update_status",
    "inventory:read",
  ],
  Viewer: ["dashboard:read", "assets:read", "reports:read"],
};

export function usePermissions() {
  const { user, isLoading } = useAegonUser();

  const hasPermission = (permission: string): boolean => {
    if (isLoading || !user) return false;

    const permissions = rolePermissions[user.role] ?? [];
    if (permissions.includes("*")) return true;
    return permissions.includes(permission);
  };

  const hasRole = (roles: string[]): boolean => {
    if (isLoading || !user) return false;
    return roles.includes(user.role);
  };

  return { hasPermission, hasRole, isLoading };
}
