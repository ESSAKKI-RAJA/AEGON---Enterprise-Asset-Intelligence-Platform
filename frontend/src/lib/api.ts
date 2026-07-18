import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || (import.meta.env.PROD ? "" : "http://127.0.0.1:8000/api/v1");

if (!import.meta.env.VITE_API_URL && import.meta.env.PROD) {
  console.warn(
    "WARNING: VITE_API_URL is not set in production. Ensure the backend URL is properly configured in Vercel.",
  );
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

// ---------------------------------------------------------------------------
// Request interceptor — Enterprise Evaluation Mode (no auth token required)
// ---------------------------------------------------------------------------
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    return config;
  },
  (error) => Promise.reject(error),
);

// ---------------------------------------------------------------------------
// Response interceptor — unwrap StandardResponse { success, data, message, meta }
// ---------------------------------------------------------------------------
apiClient.interceptors.response.use(
  (response) => {
    if (response.data && response.data.data !== undefined) {
      return response.data.data;
    }
    return response.data;
  },
  (error: AxiosError) => {
    const errorData = error.response?.data as any;
    if (errorData?.message) {
      return Promise.reject(new Error(errorData.message));
    }
    return Promise.reject(error);
  },
);
