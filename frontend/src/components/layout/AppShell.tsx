import { FileTextIcon, MessageSquareIcon, MoonIcon, SunIcon } from "lucide-react"
import type { ReactNode } from "react"
import { Link, useLocation } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { useHealth } from "@/hooks/useHealth"
import { useTheme } from "@/hooks/useTheme"
import { cn } from "@/lib/utils"

const NAV_ITEMS = [
  { to: "/documents", label: "Documents", icon: FileTextIcon },
  { to: "/chat", label: "Chat", icon: MessageSquareIcon },
]

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { theme, toggle } = useTheme()
  const { isError: apiUnreachable } = useHealth()

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
          <span className="font-semibold">Knowledge Base Chat</span>

          <nav className="hidden items-center gap-1 md:flex">
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  location.pathname.startsWith(to)
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                )}
              >
                <Icon className="size-4" />
                {label}
              </Link>
            ))}
          </nav>

          <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
            {theme === "dark" ? <SunIcon className="size-4" /> : <MoonIcon className="size-4" />}
          </Button>
        </div>

        {apiUnreachable ? (
          <div className="bg-warning/15 px-4 py-1.5 text-center text-xs text-warning">
            Can&apos;t reach the API — check that the backend is running.
          </div>
        ) : null}
      </header>

      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 pb-24 md:pb-6">{children}</main>

      <nav className="fixed inset-x-0 bottom-0 z-40 flex border-t border-border bg-background md:hidden">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <Link
            key={to}
            to={to}
            className={cn(
              "flex flex-1 flex-col items-center gap-1 py-2 text-xs font-medium",
              location.pathname.startsWith(to) ? "text-primary" : "text-muted-foreground",
            )}
          >
            <Icon className="size-5" />
            {label}
          </Link>
        ))}
      </nav>
    </div>
  )
}
