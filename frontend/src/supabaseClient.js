/**
 * Supabase Client Configuration
 *
 * Initializes and exports the Supabase client for use throughout the application.
 */

import { createClient } from '@supabase/supabase-js'

// Get Supabase configuration from environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://yzkmlvnwllxrybywafrh.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_vsqohPH_vhHEuowhZa2tHQ_H1LcelWg'

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// Helper functions for common database operations
export const db = {
  // Constituents
  async getConstituents() {
    const { data, error } = await supabase
      .from('constituents')
      .select('*')
      .order('created_date', { ascending: false })

    if (error) throw error
    return data
  },

  async getConstituent(id) {
    const { data, error } = await supabase
      .from('constituents')
      .select(`
        *,
        contributions (*),
        interactions (*),
        opportunities (*)
      `)
      .eq('constituent_id', id)
      .single()

    if (error) throw error
    return data
  },

  async createConstituent(constituent) {
    const { data, error } = await supabase
      .from('constituents')
      .insert([constituent])
      .select()
      .single()

    if (error) throw error
    return data
  },

  async updateConstituent(id, updates) {
    const { data, error } = await supabase
      .from('constituents')
      .update(updates)
      .eq('constituent_id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  // Contributions
  async getContributions(constituentId = null) {
    let query = supabase
      .from('contributions')
      .select('*, constituents(*)')
      .order('contribution_date', { ascending: false })

    if (constituentId) {
      query = query.eq('constituent_id', constituentId)
    }

    const { data, error } = await query
    if (error) throw error
    return data
  },

  async createContribution(contribution) {
    const { data, error } = await supabase
      .from('contributions')
      .insert([contribution])
      .select()
      .single()

    if (error) throw error
    return data
  },

  // Interactions
  async getInteractions(constituentId = null) {
    let query = supabase
      .from('interactions')
      .select('*, constituents(*)')
      .order('interaction_date', { ascending: false })

    if (constituentId) {
      query = query.eq('constituent_id', constituentId)
    }

    const { data, error } = await query
    if (error) throw error
    return data
  },

  async createInteraction(interaction) {
    const { data, error } = await supabase
      .from('interactions')
      .insert([interaction])
      .select()
      .single()

    if (error) throw error
    return data
  },

  // Opportunities
  async getOpportunities(constituentId = null) {
    let query = supabase
      .from('opportunities')
      .select('*, constituents(*)')
      .order('expected_close_date', { ascending: false })

    if (constituentId) {
      query = query.eq('constituent_id', constituentId)
    }

    const { data, error } = await query
    if (error) throw error
    return data
  },

  async createOpportunity(opportunity) {
    const { data, error } = await supabase
      .from('opportunities')
      .insert([opportunity])
      .select()
      .single()

    if (error) throw error
    return data
  }
}

export default supabase
