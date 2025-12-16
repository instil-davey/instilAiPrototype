import { NextResponse } from "next/server"
import { getDb } from "@/lib/db"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const db = getDb()

    // Get total constituents
    const totalConstituents = db
      .prepare("SELECT COUNT(*) as count FROM constituents")
      .get() as { count: number }

    // Get total contributions
    const totalContributions = db
      .prepare("SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM contributions")
      .get() as { count: number; total: number }

    // Get active opportunities
    const activeOpportunities = db
      .prepare(
        "SELECT COUNT(*) as count, COALESCE(SUM(expected_amount), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Won', 'Closed Lost')"
      )
      .get() as { count: number; total: number }

    // Get recent interactions
    const recentInteractions = db
      .prepare(
        "SELECT COUNT(*) as count FROM interactions WHERE interaction_date >= date('now', '-30 days')"
      )
      .get() as { count: number }

    // Get top campaigns
    const topCampaigns = db
      .prepare(`
        SELECT
          campaign_id,
          COUNT(*) as count,
          COALESCE(SUM(amount), 0) as total
        FROM contributions
        WHERE campaign_id IS NOT NULL
        GROUP BY campaign_id
        ORDER BY total DESC
        LIMIT 3
      `)
      .all() as Array<{ campaign_id: string; count: number; total: number }>

    // Get constituent type breakdown
    const constituentTypes = db
      .prepare(`
        SELECT
          constituent_type,
          COUNT(*) as count,
          COALESCE(SUM(total_lifetime_giving), 0) as total_giving
        FROM constituents
        GROUP BY constituent_type
        ORDER BY total_giving DESC
      `)
      .all() as Array<{
        constituent_type: string
        count: number
        total_giving: number
      }>

    // Calculate average gift
    const avgGift =
      totalContributions.count > 0
        ? totalContributions.total / totalContributions.count
        : 0

    const insights = [
      {
        id: "total-constituents",
        title: "Total Constituents",
        value: totalConstituents.count.toLocaleString(),
        change: "+12%",
        trend: "up" as const,
        description: "Active individuals in database",
        icon: "users",
      },
      {
        id: "total-raised",
        title: "Total Raised",
        value: `$${totalContributions.total.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}`,
        change: "+23%",
        trend: "up" as const,
        description: "Lifetime contributions",
        icon: "dollar-sign",
      },
      {
        id: "avg-gift",
        title: "Average Gift",
        value: `$${avgGift.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}`,
        change: "+8%",
        trend: "up" as const,
        description: "Per contribution",
        icon: "trending-up",
      },
      {
        id: "active-opportunities",
        title: "Active Pipeline",
        value: `$${activeOpportunities.total.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}`,
        change: `${activeOpportunities.count} opportunities`,
        trend: "neutral" as const,
        description: "In progress fundraising",
        icon: "target",
      },
      {
        id: "recent-interactions",
        title: "Recent Engagement",
        value: recentInteractions.count.toLocaleString(),
        change: "Last 30 days",
        trend: "up" as const,
        description: "Constituent interactions",
        icon: "message-square",
      },
      {
        id: "top-campaign",
        title: "Top Campaign",
        value:
          topCampaigns.length > 0
            ? `$${topCampaigns[0].total.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`
            : "$0",
        change:
          topCampaigns.length > 0
            ? `${topCampaigns[0].campaign_id}`
            : "No campaigns",
        trend: "neutral" as const,
        description: `${topCampaigns.length > 0 ? topCampaigns[0].count : 0} contributions`,
        icon: "flag",
      },
    ]

    return NextResponse.json({ insights, constituentTypes })
  } catch (error) {
    console.error("Error fetching insights:", error)
    return NextResponse.json(
      { error: "Failed to fetch insights" },
      { status: 500 }
    )
  }
}
