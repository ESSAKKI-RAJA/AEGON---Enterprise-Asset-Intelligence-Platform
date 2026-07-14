export interface StandardResponse<T> {
  success: boolean;
  message: string;
  data: T;
  meta?: Record<string, any>;
}

export interface Asset {
  id?: string;
  name: string;
  code: string;
  serial_number?: string;
  status: "Active" | "Maintenance" | "Retired" | "Lost";
  purchase_date?: string;
  purchaseValue?: number;
  health: number;
  category?: string;
  department?: string;
  room_id?: string;
  vendor_id?: string;
}

export interface WorkOrder {
  id: string;
  assetId: string;
  assetName: string;
  assetCode: string;
  status: "Scheduled" | "In Progress" | "Completed" | "Emergency";
  type: "Preventive" | "Corrective" | "Emergency";
  technician: string;
  vendor?: string;
  scheduledDate: string;
  estimatedCost: number;
  downtimeHours: number;
  notes?: string;
}

export interface DashboardMetrics {
  total_assets?: number;
  critical_assets?: number;
  active_work_orders?: number;
  total_value?: number;
  health_score?: number;
  [key: string]: any;
}
