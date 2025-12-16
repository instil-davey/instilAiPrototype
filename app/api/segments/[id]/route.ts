import { NextResponse } from "next/server"
import { getDb } from "@/lib/db"

export const dynamic = "force-dynamic"

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const db = getDb()

    // Convert id back to constituent_type
    const constituentType = id
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")

    // Get segment overview
    const segment = db
      .prepare(`
        SELECT
          constituent_type,
          COUNT(*) as count,
          COALESCE(SUM(total_lifetime_giving), 0) as total_giving,
          COALESCE(AVG(total_lifetime_giving), 0) as avg_giving
        FROM constituents
        WHERE constituent_type = ?
        GROUP BY constituent_type
      `)
      .get(constituentType) as {
      constituent_type: string
      count: number
      total_giving: number
      avg_giving: number
    } | undefined

    if (!segment) {
      return NextResponse.json({ error: "Segment not found" }, { status: 404 })
    }

    // Get top constituents in this segment
    const topConstituents = db
      .prepare(`
        SELECT
          constituent_id,
          first_name,
          last_name,
          email,
          city,
          state,
          total_lifetime_giving,
          created_date
        FROM constituents
        WHERE constituent_type = ?
        ORDER BY total_lifetime_giving DESC
        LIMIT 10
      `)
      .all(constituentType)

    // Get contribution stats for this segment
    const contributionStats = db
      .prepare(`
        SELECT
          COUNT(DISTINCT c.contribution_id) as total_contributions,
          COUNT(DISTINCT c.constituent_id) as contributing_count,
          COALESCE(SUM(c.amount), 0) as total_amount,
          COALESCE(AVG(c.amount), 0) as avg_contribution
        FROM contributions c
        JOIN constituents co ON c.constituent_id = co.constituent_id
        WHERE co.constituent_type = ?
      `)
      .get(constituentType) as {
      total_contributions: number
      contributing_count: number
      total_amount: number
      avg_contribution: number
    }

    // Get interaction stats
    const interactionStats = db
      .prepare(`
        SELECT
          COUNT(*) as total_interactions,
          COUNT(DISTINCT i.constituent_id) as engaged_count,
          interaction_type,
          COUNT(*) as type_count
        FROM interactions i
        JOIN constituents c ON i.constituent_id = c.constituent_id
        WHERE c.constituent_type = ?
        GROUP BY interaction_type
        ORDER BY type_count DESC
        LIMIT 5
      `)
      .all(constituentType) as Array<{
      total_interactions: number
      engaged_count: number
      interaction_type: string
      type_count: number
    }>

    const totalInteractions =
      interactionStats.length > 0 ? interactionStats[0].total_interactions : 0
    const engagedCount =
      interactionStats.length > 0 ? interactionStats[0].engaged_count : 0

    // Get opportunities stats
    const opportunityStats = db
      .prepare(`
        SELECT
          COUNT(*) as total_opportunities,
          COALESCE(SUM(expected_amount), 0) as total_pipeline,
          stage,
          COUNT(*) as stage_count
        FROM opportunities o
        JOIN constituents c ON o.constituent_id = c.constituent_id
        WHERE c.constituent_type = ?
        GROUP BY stage
        ORDER BY stage_count DESC
      `)
      .all(constituentType) as Array<{
      total_opportunities: number
      total_pipeline: number
      stage: string
      stage_count: number
    }>

    const totalOpportunities =
      opportunityStats.length > 0 ? opportunityStats[0].total_opportunities : 0
    const totalPipeline =
      opportunityStats.length > 0 ? opportunityStats[0].total_pipeline : 0

    return NextResponse.json({
      segment: {
        id,
        name: segment.constituent_type,
        count: segment.count,
        totalGiving: segment.total_giving,
        avgGiving: segment.avg_giving,
      },
      topConstituents,
      stats: {
        contributions: contributionStats,
        interactions: {
          total: totalInteractions,
          engaged: engagedCount,
          byType: interactionStats.map((s) => ({
            type: s.interaction_type,
            count: s.type_count,
          })),
        },
        opportunities: {
          total: totalOpportunities,
          pipeline: totalPipeline,
          byStage: opportunityStats.map((s) => ({
            stage: s.stage,
            count: s.stage_count,
          })),
        },
      },
    })
  } catch (error) {
    console.error("Error fetching segment details:", error)
    return NextResponse.json(
      { error: "Failed to fetch segment details" },
      { status: 500 }
    )
  }
}
