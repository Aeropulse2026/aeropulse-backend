const apiUrl = process.env.NEXT_PUBLIC_API_URL!;

export async function apiFetch(path: string, init: RequestInit = {}) {
  const request = () => fetch(`${apiUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init.headers },
  });

  let response = await request();
  if (response.status !== 401) return response;

  const refreshed = await fetch(`${apiUrl}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });
  if (!refreshed.ok) return response;

  response = await request();
  return response;
}
