"use client"

import { useQuery } from "@tanstack/react-query"
import { InsightCard, InsightCardProps } from "@/components/InsightCard"
import { SegmentCard, SegmentCardProps } from "@/components/SegmentCard"
import { LoadingCard, LoadingSegmentCard } from "@/components/LoadingCard"
import { EmptyState } from "@/components/EmptyState"
import { BarChart3, AlertCircle } from "lucide-react"

interface InsightsResponse {
  insights: InsightCardProps[]
  constituentTypes: Array<{
    constituent_type: string
    count: number
    total_giving: number
  }>
}

interface SegmentsResponse {
  segments: SegmentCardProps[]
}

export default function DashboardPage() {
  const {
    data: insightsData,
    isLoading: insightsLoading,
    error: insightsError,
  } = useQuery<InsightsResponse>({
    queryKey: ["insights"],
    queryFn: async () => {
      const res = await fetch("/api/insights")
      if (!res.ok) throw new Error("Failed to fetch insights")
      return res.json()
    },
  })

  const {
    data: segmentsData,
    isLoading: segmentsLoading,
    error: segmentsError,
  } = useQuery<SegmentsResponse>({
    queryKey: ["segments"],
    queryFn: async () => {
      const res = await fetch("/api/segments")
      if (!res.ok) throw new Error("Failed to fetch segments")
      return res.json()
    },
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary p-2">
              <BarChart3 className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Nonprofit CRM Dashboard
              </h1>
              <p className="text-sm text-muted-foreground">
                AI-powered insights for constituent relationships
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* AI Insights Section */}
        <section>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-foreground mb-1">
              Key Insights
            </h2>
            <p className="text-sm text-muted-foreground">
              Real-time metrics and performance indicators
            </p>
          </div>

          {insightsError ? (
            <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                <div>
                  <h3 className="font-semibold text-destructive mb-1">
                    Failed to load insights
                  </h3>
                  <p className="text-sm text-destructive/80">
                    There was an error loading the dashboard insights. Please
                    try again.
                  </p>
                </div>
              </div>
            </div>
          ) : insightsLoading ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <LoadingCard key={i} delay={i * 50} />
              ))}
            </div>
          ) : insightsData?.insights && insightsData.insights.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {insightsData.insights.map((insight, index) => (
                <InsightCard
                  key={insight.id}
                  {...insight}
                  delay={index * 50}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              title="No insights available"
              description="There are no insights to display at this time."
            />
          )}
        </section>

        {/* Segments Section */}
        <section>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-foreground mb-1">
              Constituent Segments
            </h2>
            <p className="text-sm text-muted-foreground">
              Click on a segment to view detailed analytics and constituent list
            </p>
          </div>

          {segmentsError ? (
            <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                <div>
                  <h3 className="font-semibold text-destructive mb-1">
                    Failed to load segments
                  </h3>
                  <p className="text-sm text-destructive/80">
                    There was an error loading the constituent segments. Please
                    try again.
                  </p>
                </div>
              </div>
            </div>
          ) : segmentsLoading ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <LoadingSegmentCard key={i} delay={i * 50} />
              ))}
            </div>
          ) : segmentsData?.segments && segmentsData.segments.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {segmentsData.segments.map((segment, index) => (
                <SegmentCard
                  key={segment.id}
                  {...segment}
                  delay={index * 50}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              title="No segments available"
              description="There are no constituent segments to display at this time."
            />
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-sm text-muted-foreground text-center">
            Nonprofit CRM Dashboard • Built with Next.js, Tailwind CSS, and
            shadcn/ui
          </p>
        </div>
      </footer>
    </div>
  )
}
