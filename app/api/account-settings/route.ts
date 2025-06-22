import { NextRequest, NextResponse } from 'next/server'
import { supabase, BobAccount } from '@/lib/supabase'

export async function GET() {
  try {
    const { data, error } = await supabase
      .from('bob_accounts')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    if (error && error.code !== 'PGRST116') {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ account: data || null })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch account settings' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const account: BobAccount = body.account

    // Validate required fields
    if (!account.name || !account.profile || !account.location) {
      return NextResponse.json(
        { error: 'Name, profile, and location are required' },
        { status: 400 }
      )
    }

    // Check if account already exists
    const { data: existingAccount } = await supabase
      .from('bob_accounts')
      .select('id')
      .limit(1)
      .single()

    let result
    if (existingAccount) {
      // Update existing account
      result = await supabase
        .from('bob_accounts')
        .update({
          name: account.name,
          role: account.role,
          role_description: account.role_description,
          profile: account.profile,
          services_type: account.services_type,
          services: account.services,
          services_not_provided: account.services_not_provided,
          location: account.location,
          updated_at: new Date().toISOString()
        })
        .eq('id', existingAccount.id)
        .select()
        .single()
    } else {
      // Create new account
      result = await supabase
        .from('bob_accounts')
        .insert({
          name: account.name,
          role: account.role,
          role_description: account.role_description,
          profile: account.profile,
          services_type: account.services_type,
          services: account.services,
          services_not_provided: account.services_not_provided,
          location: account.location
        })
        .select()
        .single()
    }

    if (result.error) {
      return NextResponse.json({ error: result.error.message }, { status: 500 })
    }

    return NextResponse.json({ 
      account: result.data,
      message: 'Account settings saved successfully' 
    })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to save account settings' }, { status: 500 })
  }
} 