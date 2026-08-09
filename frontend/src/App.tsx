import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import { AppShell } from "@/components/layout/AppShell"
import { Toaster } from "@/components/ui/toaster"
import { ChatPage } from "@/pages/ChatPage"
import { DocumentsPage } from "@/pages/DocumentsPage"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1 },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppShell>
          <Routes>
            <Route path="/" element={<Navigate to="/documents" replace />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/chat" element={<ChatPage />} />
          </Routes>
        </AppShell>
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
