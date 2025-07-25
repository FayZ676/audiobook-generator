/**
 * Centralized API call handler with consistent error handling
 */
export async function apiCall(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  try {
    const response = await fetch(url, options);

    if (response.status === 402) {
      throw new Error("Insufficient bandwidth for request.");
    }

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return response;
  } catch (error) {
    // Re-throw to let the caller handle it
    throw error;
  }
}

/**
 * Helper for JSON API calls
 */
export async function apiCallJson<T = any>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await apiCall(url, options);
  return response.json();
}

/**
 * Helper for API calls that don't return data
 */
export async function apiCallVoid(
  url: string,
  options: RequestInit = {}
): Promise<void> {
  await apiCall(url, options);
}
