export class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
    public details: unknown = null,
  ) {
    super(message);
  }
}
export function apiUrl(path: string): string {
  const base = (import.meta.env.VITE_API_BASE_URL || "/api").replace(
    /\/+$/,
    "",
  );
  return base + "/" + path.replace(/^\/+/, "");
}

export async function apiResponse(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const token =
    path === "/status" || path === "/health" ? null : await accessToken();
  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      ...init,
      signal: init.signal || AbortSignal.timeout(90000),
      headers: {
        "X-ProofPath-Client": "web",
        ...(init.body instanceof FormData
          ? {}
          : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init.headers,
      },
    });
  } catch {
    throw new ApiError(
      "Cannot reach the API or the request timed out. The service may be starting. Your current draft is still here. Refresh saved records before retrying a write.",
      "NETWORK_ERROR",
    );
  }
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ message: "Server request failed" }));
    throw new ApiError(
      error.details?.length
        ? `${error.message}: ${error.details.map((d: any) => `${d.field}: ${d.message}`).join("; ")}`
        : error.message ||
            `API request failed (${response.status}). Please retry.`,
      error.code || "HTTP_ERROR",
      error.details,
    );
  }
  return response;
}
export async function api<T = any>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await apiResponse(path, init);
  return response.status === 204 ? (undefined as T) : response.json();
}
export const post = <T = any>(path: string, body: unknown) =>
  api<T>(path, { method: "POST", body: JSON.stringify(body) });
import { accessToken } from "./auth";
