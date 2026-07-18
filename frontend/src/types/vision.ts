/**
 * AEGON Vision Intelligence — TypeScript Types
 * Mirrors the backend Pydantic schemas for strict end-to-end typing.
 */

export type VisionViewType = "top" | "bottom" | "front" | "rear" | "left" | "right" | "360";

export type DefectSeverity = "critical" | "high" | "medium" | "low" | "none";

export type InspectionStatus = "idle" | "uploading" | "analyzing" | "complete" | "failed";

export type MaintenancePriority =
  | "immediate"
  | "within_7_days"
  | "within_30_days"
  | "within_90_days"
  | "scheduled"
  | "none_required";

export interface BoundingBoxMock {
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  confidence: number;
}

export interface DefectFinding {
  finding_id: string;
  defect_type: string;
  severity: DefectSeverity;
  confidence: number; // 0.0-1.0
  description: string;
  recommended_action: string;
  bounding_box?: BoundingBoxMock;
  area_affected_pct: number;
  heatmap_data?: string;
  mask_points: number[][];
  estimated_repair_cost: number;
  estimated_repair_time_mins: number;
}

export interface ViewInspectionResult {
  view_type: VisionViewType;
  status: InspectionStatus;
  image_filename?: string;
  findings: DefectFinding[];
  view_health_score: number;
  defect_count: number;
  critical_count: number;
  processing_time_ms: number;
  inference_engine: string;
  model_version: string;
  gpu_status: string;
  cpu_usage_pct: number;
  memory_usage_mb: number;
  queue_position: number;
  inspected_at?: string;
  operator?: string;
}

export interface CompositeAnalysis {
  overall_health_score: number;
  risk_score: number;
  quality_score: number;
  inspection_confidence: number;
  total_defects: number;
  critical_defects: number;
  views_inspected: number;
  remaining_useful_life_years: number;
  maintenance_priority: MaintenancePriority;
  maintenance_cost_estimate_usd: number;
  asset_readiness_pct: number;
  deployment_status: string;
}

export interface ExecutiveSummary {
  summary_id: string;
  narrative: string;
  key_findings: string[];
  risk_matrix: Record<string, number>;
  recommendations: string[];
  generated_at: string;
}

export interface DigitalTwinState {
  asset_name: string;
  health_score: number;
  risk_score: number;
  temperature_celsius: number;
  pressure_psi: number;
  rotation_rpm: number;
  maintenance_status: string;
  inspection_progress_pct: number;
  views_completed: VisionViewType[];
  historical_health_trend: number[];
  historical_risk_trend: number[];
  last_updated: string;
}

export interface InspectionSession {
  session_id: string;
  asset_id?: string;
  asset_name: string;
  operator: string;
  started_at: string;
  completed_at?: string;
  status: InspectionStatus;
  view_results: Record<string, ViewInspectionResult>;
  composite?: CompositeAnalysis;
  executive_summary?: ExecutiveSummary;
  digital_twin: DigitalTwinState;
}

export interface UploadViewResponse {
  session_id: string;
  view_result: ViewInspectionResult;
  digital_twin?: DigitalTwinState;
}

export interface Composite360Response {
  session_id: string;
  composite: CompositeAnalysis;
  executive_summary: ExecutiveSummary;
  digital_twin?: DigitalTwinState;
}

export interface InspectionHistoryItem {
  session_id: string;
  asset_name: string;
  operator: string;
  started_at: string;
  completed_at?: string;
  views_inspected: number;
  total_defects: number;
  critical_defects: number;
  health_score: number;
  risk_score: number;
  maintenance_priority: MaintenancePriority;
  status: InspectionStatus;
}

export interface VisionStatistics {
  total_inspections: number;
  avg_health_score: number;
  avg_risk_score: number;
  most_common_defect: string;
  critical_defect_rate_pct: number;
  avg_inspection_time_seconds: number;
  avg_queue_time_ms: number;
  active_gpu_utilization_pct: number;
}

export interface CreateMaintenanceTicketRequest {
  session_id: string;
  asset_id?: string;
  finding_id: string;
  defect_type: string;
  priority: MaintenancePriority;
  estimated_cost: number;
}

// UI-only types
export interface ViewPanelState {
  viewType: VisionViewType;
  label: string;
  status: InspectionStatus;
  previewUrl?: string;
  result?: ViewInspectionResult;
}
