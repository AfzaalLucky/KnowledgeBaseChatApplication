import { useQuery } from "@tanstack/react-query"

import { listDocuments } from "@/api/documents"
import type { KbDocument } from "@/types/document"

const ACTIVE_STATUSES = new Set(["pending", "processing"])

export function useDocuments(search?: string) {
  return useQuery({
    queryKey: ["documents", search ?? ""],
    queryFn: () => listDocuments(search),
    refetchInterval: (query) => {
      const data = query.state.data as KbDocument[] | undefined
      return data?.some((d) => ACTIVE_STATUSES.has(d.status)) ? 2000 : false
    },
  })
}
