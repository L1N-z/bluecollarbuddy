import { NextRequest, NextResponse } from 'next/server'
import { supabase, AgentSettings } from '@/lib/supabase'

export async function GET() {
  try {
    const { data, error } = await supabase
      .from('agent_settings')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    if (error && error.code !== 'PGRST116') {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ settings: data || null })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch agent settings' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const settings: AgentSettings = body.settings

    // Validate required fields
    if (typeof settings.enabled !== 'boolean' || 
        typeof settings.delay_time !== 'number' || 
        !settings.default_greeting) {
      return NextResponse.json(
        { error: 'Enabled status, delay time, and default greeting are required' },
        { status: 400 }
      )
    }

    // Check if settings already exist
    const { data: existingSettings } = await supabase
      .from('agent_settings')
      .select('id')
      .limit(1)
      .single()

    let result
    if (existingSettings) {
      // Update existing settings
      result = await supabase
        .from('agent_settings')
        .update({
          enabled: settings.enabled,
          delay_time: settings.delay_time,
          default_greeting: settings.default_greeting,
          updated_at: new Date().toISOString()
        })
        .eq('id', existingSettings.id)
        .select()
        .single()
    } else {
      // Create new settings
      result = await supabase
        .from('agent_settings')
        .insert({
          enabled: settings.enabled,
          delay_time: settings.delay_time,
          default_greeting: settings.default_greeting
        })
        .select()
        .single()
    }

    if (result.error) {
      return NextResponse.json({ error: result.error.message }, { status: 500 })
    }

    return NextResponse.json({ 
      settings: result.data,
      message: 'Agent settings saved successfully' 
    })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to save agent settings' }, { status: 500 })
  }
} 