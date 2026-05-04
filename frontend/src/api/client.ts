import axios from "axios";

import { notifyBadges } from "@/lib/badgeNotifier";

const api = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Send httpOnly cookies with every request
});

// Track if we're currently refreshing to avoid infinite loops
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: unknown = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve();
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => {
    const newlyEarned = response.data?.newly_earned_badges;
    if (Array.isArray(newlyEarned) && newlyEarned.length > 0) {
      notifyBadges(newlyEarned);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Only attempt refresh on 401 and not on auth endpoints themselves
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
        !originalRequest.url?.includes("/auth/login") &&
        !originalRequest.url?.includes("/auth/token/refresh") &&
        !originalRequest.url?.includes("/auth/me/")
    ) {
      if (isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => api(originalRequest));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await api.post("/auth/token/refresh/");
        processQueue();
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        // Refresh failed — redirect to login
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
