import type { LibraryResponse, UpdateAnnotationsPayload } from "@/types/domain";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// Empty filter values are dropped so the API applies only active facet constraints.

/** Query params forwarded to GET /v1/library (includes dynamic facet keys). */
export type LibraryQueryParams = Record<string, string>;

export async function fetchLibrary(filters: LibraryQueryParams): Promise<LibraryResponse> {
  const query = new URLSearchParams();

  for (const [key, value] of Object.entries(filters)) {
    if (typeof value === "string" && value.trim().length > 0) {
      query.set(key, value);
    }
  }

  const endpoint = `${API_BASE_URL}/v1/library${query.toString() ? `?${query.toString()}` : ""}`;
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch library: ${response.status}`);
  }

  return (await response.json()) as LibraryResponse;
}

export async function updateAnnotations(itemId: string, payload: UpdateAnnotationsPayload): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/v1/library/${itemId}/annotations`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to update annotations: ${response.status}`);
  }
}
