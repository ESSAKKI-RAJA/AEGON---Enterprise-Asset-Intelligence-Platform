/**
 * AEGON Vision Intelligence — Frontend Service Layer
 * TanStack Query hooks + axios calls for all Vision Intelligence endpoints.
 */
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import type {
  Composite360Response,
  InspectionHistoryItem,
  UploadViewResponse,
  VisionStatistics,
  VisionViewType,
} from "@/types/vision";

const BASE = "/vision";

// ---------------------------------------------------------------------------
// Upload + Analyse a view
// ---------------------------------------------------------------------------

interface UploadViewParams {
  viewType: VisionViewType;
  file?: File;
  sessionId: string;
  assetName?: string;
  operator?: string;
}

export function useUploadView(onSuccess?: (data: UploadViewResponse) => void) {
  return useMutation<UploadViewResponse, Error, UploadViewParams>({
    mutationFn: async ({ viewType, file, sessionId, assetName, operator }) => {
      const form = new FormData();
      form.append("session_id", sessionId);
      form.append("asset_name", assetName || "Enterprise Asset");
      form.append("operator", operator || "System");
      if (file) {
        form.append("file", file);
      }

      const response = await apiClient.post<any>(
        `${BASE}/upload/${viewType}`,
        form,
        { headers: { "Content-Type": "multipart/form-data" } },
      );
      // apiClient interceptor unwraps { data: ... }
      return response as unknown as UploadViewResponse;
    },
    onSuccess,
  });
}

// ---------------------------------------------------------------------------
// 360° Composite
// ---------------------------------------------------------------------------

interface Generate360Params {
  sessionId: string;
}

export function useGenerate360(onSuccess?: (data: Composite360Response) => void) {
  return useMutation<Composite360Response, Error, Generate360Params>({
    mutationFn: async ({ sessionId }) => {
      const response = await apiClient.post(`${BASE}/360`, {
        session_id: sessionId,
      });
      return response as unknown as Composite360Response;
    },
    onSuccess,
  });
}

// ---------------------------------------------------------------------------
// Report Generation
// ---------------------------------------------------------------------------

export function useGenerateReport() {
  return useMutation<any, Error, { sessionId: string }>({
    mutationFn: async ({ sessionId }) => {
      const response = await apiClient.post(`${BASE}/report`, {
        session_id: sessionId,
      });
      return response;
    },
  });
}

// ---------------------------------------------------------------------------
// Inspection History
// ---------------------------------------------------------------------------

export function useInspectionHistory(limit = 20, offset = 0) {
  return useQuery<{ items: InspectionHistoryItem[]; total: number }>({
    queryKey: ["visionHistory", limit, offset],
    queryFn: async () => {
      const response = await apiClient.get(`${BASE}/history`, {
        params: { limit, offset },
      });
      return response as unknown as { items: InspectionHistoryItem[]; total: number };
    },
    staleTime: 30_000,
  });
}

// ---------------------------------------------------------------------------
// Statistics
// ---------------------------------------------------------------------------

export function useVisionStatistics() {
  return useQuery<VisionStatistics>({
    queryKey: ["visionStatistics"],
    queryFn: async () => {
      const response = await apiClient.get(`${BASE}/statistics`);
      return response as unknown as VisionStatistics;
    },
    staleTime: 60_000,
  });
}
