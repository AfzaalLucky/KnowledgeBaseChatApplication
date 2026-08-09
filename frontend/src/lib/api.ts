export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json()
    if (typeof body?.detail === "string") return body.detail
  } catch {
    // response wasn't JSON — fall through to a generic message
  }
  return `Request failed with status ${res.status}`
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init)
  if (!res.ok) {
    throw new ApiError(res.status, await parseErrorDetail(res))
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}
