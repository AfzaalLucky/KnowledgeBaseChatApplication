import { useQuery } from "@tanstack/react-query"

import { apiFetch } from "@/lib/api"

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiFetch<{ status: string }>("/api/health"),
    retry: false,
    refetchInterval: 15000,
  })
}
