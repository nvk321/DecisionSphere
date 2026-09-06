/**
 * Central HTTP Client with Correlation ID & Normalized Error Handling.
 */

export class DecisionSphereAPIError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public get status(): number {
    return this.statusCode;
  }
  public readonly requestId?: string;
  public readonly details?: unknown;

  constructor(
    message: string,
    code: string,
    statusCode: number,
    requestId?: string,
    details?: unknown
  ) {
    super(message);
    this.name = "DecisionSphereAPIError";
    this.code = code;
    this.statusCode = statusCode;
    this.requestId = requestId;
    this.details = details;
  }
}

// In Next.js client environment, calling /api/v1/... triggers the next.config rewrite to FastAPI.
// If NEXT_PUBLIC_API_URL is explicitly set (e.g. in tests or SSR), it uses that.
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

function generateRequestId(): string {
  return `req-${Math.random().toString(36).substring(2, 11)}`;
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | null | undefined>;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, headers, ...restOptions } = options;

  let url = endpoint.startsWith("http") ? endpoint : `${BASE_URL}${endpoint}`;
  if (params) {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined) {
        query.append(key, String(value));
      }
    }
    const queryString = query.toString();
    if (queryString) {
      url += (url.includes("?") ? "&" : "?") + queryString;
    }
  }

  const requestId = generateRequestId();
  const mergedHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
    "X-Request-ID": requestId,
    ...(headers as Record<string, string>),
  };

  let response: Response;
  try {
    response = await fetch(url, {
      ...restOptions,
      headers: mergedHeaders,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Network error";
    throw new DecisionSphereAPIError(
      `Unable to reach DecisionSphere API at ${url}: ${message}`,
      "NETWORK_ERROR",
      0,
      requestId
    );
  }

  if (!response.ok) {
    let errorCode = "HTTP_ERROR";
    let errorMessage = `Request failed with status ${response.status} (${response.statusText})`;
    let details: unknown = null;
    let respRequestId = response.headers.get("X-Request-ID") || requestId;

    try {
      const data = await response.json();
      if (data && typeof data === "object") {
        if ("error" in data && typeof data.error === "object" && data.error) {
          const errObj = data.error as Record<string, unknown>;
          errorCode = String(errObj.code || errorCode);
          errorMessage = String(errObj.message || errorMessage);
          respRequestId = String(errObj.request_id || respRequestId);
          details = errObj.details;
        } else if ("detail" in data) {
          errorMessage = String(data.detail);
        }
      }
    } catch {
      // Non-JSON error payload
    }

    throw new DecisionSphereAPIError(
      errorMessage,
      errorCode,
      response.status,
      respRequestId,
      details
    );
  }

  // If 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return (await response.json()) as T;
}
