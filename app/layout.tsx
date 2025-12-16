import type { Metadata } from "next"
import "./globals.css"
import { QueryProvider } from "@/components/providers/query-provider"

export const metadata: Metadata = {
  title: "Nonprofit CRM Dashboard",
  description: "AI-powered insights for nonprofit constituent relationships",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  )
}
