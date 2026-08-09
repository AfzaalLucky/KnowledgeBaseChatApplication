import { SearchIcon } from "lucide-react"

import { Input } from "@/components/ui/input"

interface DocumentSearchBarProps {
  value: string
  onChange: (value: string) => void
}

export function DocumentSearchBar({ value, onChange }: DocumentSearchBarProps) {
  return (
    <div className="relative w-full max-w-xs">
      <SearchIcon className="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        placeholder="Search documents..."
        className="pl-8"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}
