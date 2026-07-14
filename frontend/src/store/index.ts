import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UIState {
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    { name: "AEGON-ui" },
  ),
);

interface FilterState {
  globalDateRange: "7d" | "30d" | "90d" | "1y" | "ytd" | "all";
  setGlobalDateRange: (range: "7d" | "30d" | "90d" | "1y" | "ytd" | "all") => void;
  selectedDepartments: string[];
  toggleDepartment: (dept: string) => void;
  clearFilters: () => void;
}

export const useFilterStore = create<FilterState>()(
  persist(
    (set) => ({
      globalDateRange: "30d",
      setGlobalDateRange: (range) => set({ globalDateRange: range }),
      selectedDepartments: [],
      toggleDepartment: (dept) =>
        set((state) => ({
          selectedDepartments: state.selectedDepartments.includes(dept)
            ? state.selectedDepartments.filter((d) => d !== dept)
            : [...state.selectedDepartments, dept],
        })),
      clearFilters: () => set({ globalDateRange: "30d", selectedDepartments: [] }),
    }),
    { name: "AEGON-filters" },
  ),
);
