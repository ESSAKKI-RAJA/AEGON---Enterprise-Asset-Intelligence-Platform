import { apiClient } from "@/lib/api";

export interface AssetKPIs {
  label: string;
  value: string;
  delta: string;
  deltaTone: "positive" | "negative" | "neutral" | "critical";
  deltaPositive: boolean;
}

export interface AssetRegistryResponse {
  items: any[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const assetService = {
  getKPIs: async () => {
    return apiClient.get("/assets/kpis/global");
  },

  getAssets: async (
    query: string = "",
    page: number = 1,
    pageSize: number = 50,
  ): Promise<AssetRegistryResponse> => {
    return apiClient.get(`/assets/?query=${query}&page=${page}&page_size=${pageSize}`);
  },
};
