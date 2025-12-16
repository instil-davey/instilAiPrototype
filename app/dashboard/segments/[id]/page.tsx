"use client"

import { use } from "react"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import {
  ArrowLeft,
  Users,
  DollarSign,
  TrendingUp,
  MessageSquare,
  Target,
  AlertCircle,
  Mail,
  MapPin,
} from "lucide-react"
import { LoadingCard } from "@/components/LoadingCard"
import { EmptyState } from "@/components/EmptyState"

interface Constituent {
  constituent_id: number
  first_name: string
  last_name: string
  email: string | null
  city: string | null
  state: string | null
  total_lifetime_giving: number
  created_date: string
}

interface SegmentDetailResponse {
  segment: {
    id: string
    name: string
    count: number
    totalGiving: number
    avgGiving: number
  }
  topConstituents: Constituent[]
  stats: {
    contributions: {
      total_contributions: number
      contributing_count: number
      total_amount: number
      avg_contribution: number
    }
    interactions: {
      total: number
      engaged: number
      byType: Array<{ type: string; count: number }>
    }
    opportunities: {
      total: number
      pipeline: number
      byStage: Array<{ stage: string; count: number }>
    }
  }
}

export default function SegmentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)

  const {
    data,
    isLoading,
    error,
  } = useQuery<SegmentDetailResponse>({
    queryKey: ["segment", id],
    queryFn: async () => {
      const res = await fetch(`/api/segments/${id}`)
      if (!res.ok) throw new Error("Failed to fetch segment details")
      return res.json()
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <header className="border-b bg-white/80 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-6">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="grid gap-6 md:grid-cols-3 mb-8">
            {[...Array(3)].map((_, i) => (
              <LoadingCard key={i} delay={i * 50} />
            ))}
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            {[...Array(4)].map((_, i) => (
              <LoadingCard key={i} delay={i * 50} />
            ))}
          </div>
        </main>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <header className="border-b bg-white/80 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-6">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
              <div>
                <h3 className="font-semibold text-destructive mb-1">
                  Failed to load segment
                </h3>
                <p className="text-sm text-destructive/80">
                  There was an error loading the segment details. Please try
                  again.
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    )
  }

  const { segment, topConstituents, stats } = data

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                {segment.name}
              </h1>
              <p className="text-muted-foreground">
                {segment.count} constituents in this segment
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Overview Stats */}
        <section>
          <h2 className="text-xl font-semibold text-foreground mb-4">
            Overview
          </h2>
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-xl border bg-card p-6 hover:shadow-lg transition-shadow animate-slide-in">
              <div className="flex items-center gap-3 mb-3">
                <div className="rounded-lg bg-blue-100 p-2">
                  <Users className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="font-semibold text-foreground">Total Count</h3>
              </div>
              <div className="text-3xl font-bold text-foreground">
                {segment.count}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                constituents
              </p>
            </div>

            <div className="rounded-xl border bg-card p-6 hover:shadow-lg transition-shadow animate-slide-in" style={{ animationDelay: "50ms" }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="rounded-lg bg-green-100 p-2">
                  <DollarSign className="h-5 w-5 text-green-600" />
                </div>
                <h3 className="font-semibold text-foreground">Total Giving</h3>
              </div>
              <div className="text-3xl font-bold text-foreground">
                $
                {segment.totalGiving.toLocaleString(undefined, {
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                })}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                lifetime contributions
              </p>
            </div>

            <div className="rounded-xl border bg-card p-6 hover:shadow-lg transition-shadow animate-slide-in" style={{ animationDelay: "100ms" }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="rounded-lg bg-purple-100 p-2">
                  <TrendingUp className="h-5 w-5 text-purple-600" />
                </div>
                <h3 className="font-semibold text-foreground">Avg per Person</h3>
              </div>
              <div className="text-3xl font-bold text-foreground">
                $
                {segment.avgGiving.toLocaleString(undefined, {
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                })}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                average lifetime value
              </p>
            </div>
          </div>
        </section>

        {/* Detailed Stats */}
        <section>
          <h2 className="text-xl font-semibold text-foreground mb-4">
            Detailed Statistics
          </h2>
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Contributions */}
            <div className="rounded-xl border bg-card p-6 animate-slide-in" style={{ animationDelay: "150ms" }}>
              <div className="flex items-center gap-2 mb-4">
                <div className="rounded-lg bg-amber-100 p-2">
                  <DollarSign className="h-5 w-5 text-amber-600" />
                </div>
                <h3 className="font-semibold text-foreground">Contributions</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="text-sm text-muted-foreground">Total Contributions</div>
                  <div className="text-2xl font-bold text-foreground">
                    {stats.contributions.total_contributions}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Contributing Count</div>
                  <div className="text-xl font-semibold text-foreground">
                    {stats.contributions.contributing_count}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Avg Contribution</div>
                  <div className="text-xl font-semibold text-foreground">
                    $
                    {stats.contributions.avg_contribution.toLocaleString(
                      undefined,
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Interactions */}
            <div className="rounded-xl border bg-card p-6 animate-slide-in" style={{ animationDelay: "200ms" }}>
              <div className="flex items-center gap-2 mb-4">
                <div className="rounded-lg bg-blue-100 p-2">
                  <MessageSquare className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="font-semibold text-foreground">Interactions</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="text-sm text-muted-foreground">Total Interactions</div>
                  <div className="text-2xl font-bold text-foreground">
                    {stats.interactions.total}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Engaged Count</div>
                  <div className="text-xl font-semibold text-foreground">
                    {stats.interactions.engaged}
                  </div>
                </div>
                {stats.interactions.byType.length > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">
                      Top Types
                    </div>
                    <div className="space-y-1">
                      {stats.interactions.byType.slice(0, 3).map((type) => (
                        <div
                          key={type.type}
                          className="flex justify-between text-sm"
                        >
                          <span className="text-muted-foreground">
                            {type.type}
                          </span>
                          <span className="font-medium text-foreground">
                            {type.count}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Opportunities */}
            <div className="rounded-xl border bg-card p-6 animate-slide-in" style={{ animationDelay: "250ms" }}>
              <div className="flex items-center gap-2 mb-4">
                <div className="rounded-lg bg-rose-100 p-2">
                  <Target className="h-5 w-5 text-rose-600" />
                </div>
                <h3 className="font-semibold text-foreground">Opportunities</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="text-sm text-muted-foreground">Total Opportunities</div>
                  <div className="text-2xl font-bold text-foreground">
                    {stats.opportunities.total}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Pipeline Value</div>
                  <div className="text-xl font-semibold text-foreground">
                    $
                    {stats.opportunities.pipeline.toLocaleString(undefined, {
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 0,
                    })}
                  </div>
                </div>
                {stats.opportunities.byStage.length > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">
                      Top Stages
                    </div>
                    <div className="space-y-1">
                      {stats.opportunities.byStage.slice(0, 3).map((stage) => (
                        <div
                          key={stage.stage}
                          className="flex justify-between text-sm"
                        >
                          <span className="text-muted-foreground">
                            {stage.stage}
                          </span>
                          <span className="font-medium text-foreground">
                            {stage.count}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Top Constituents */}
        <section>
          <h2 className="text-xl font-semibold text-foreground mb-4">
            Top Constituents
          </h2>
          {topConstituents.length > 0 ? (
            <div className="rounded-xl border bg-card overflow-hidden animate-slide-in" style={{ animationDelay: "300ms" }}>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left py-3 px-4 font-semibold text-sm text-muted-foreground">
                        Name
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-sm text-muted-foreground">
                        Email
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-sm text-muted-foreground">
                        Location
                      </th>
                      <th className="text-right py-3 px-4 font-semibold text-sm text-muted-foreground">
                        Lifetime Giving
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {topConstituents.map((constituent, index) => (
                      <tr
                        key={constituent.constituent_id}
                        className="border-b last:border-0 hover:bg-muted/30 transition-colors"
                        style={{
                          animation: "fade-in 0.3s ease-out forwards",
                          animationDelay: `${350 + index * 30}ms`,
                          opacity: 0,
                        }}
                      >
                        <td className="py-3 px-4">
                          <div className="font-medium text-foreground">
                            {constituent.first_name} {constituent.last_name}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          {constituent.email ? (
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <Mail className="h-3 w-3" />
                              {constituent.email}
                            </div>
                          ) : (
                            <span className="text-sm text-muted-foreground/50">
                              —
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          {constituent.city || constituent.state ? (
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <MapPin className="h-3 w-3" />
                              {[constituent.city, constituent.state]
                                .filter(Boolean)
                                .join(", ")}
                            </div>
                          ) : (
                            <span className="text-sm text-muted-foreground/50">
                              —
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="font-semibold text-foreground">
                            $
                            {constituent.total_lifetime_giving.toLocaleString(
                              undefined,
                              {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              }
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <EmptyState
              title="No constituents found"
              description="There are no constituents in this segment."
            />
          )}
        </section>
      </main>
    </div>
  )
}
