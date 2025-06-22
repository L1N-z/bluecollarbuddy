# Supabase Integration Setup Guide

This guide will help you set up Supabase to store Bob's account details and agent settings.

## Prerequisites

1. A Supabase account (free tier available at [supabase.com](https://supabase.com))
2. Your Next.js project with the Supabase client already installed

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `bob-beehive-dashboard` (or your preferred name)
   - **Database Password**: Create a strong password
   - **Region**: Choose the closest region to your users
5. Click "Create new project"
6. Wait for the project to be created (usually takes 1-2 minutes)

## Step 2: Get Your Supabase Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like: `https://your-project-id.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

## Step 3: Set Up Environment Variables

1. In your project root, create or update your `.env.local` file:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://nymkpolttpvjnuamaeui.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_PUBLIC_KEY_HERE

# Existing environment variables (keep these)
GOOGLE_GENERATIVE_AI_API_KEY=your-gemini-api-key
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
ACI_API_KEY_READER=your-aci-reader-api-key
ACI_API_KEY_CREATOR=your-aci-creator-api-key
PYTHON_SERVER_URL=your-python-server-url
```

2. For Vercel deployment, add these environment variables in your Vercel dashboard:
   - Go to your project settings in Vercel
   - Navigate to **Environment Variables**
   - Add `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Step 4: Set Up Database Tables

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the contents of `scripts/supabase_setup.sql`
4. Click **Run** to execute the SQL script

This will create:
- `bob_accounts` table for storing account details
- `agent_settings` table for storing agent configuration
- Proper indexes and triggers for automatic timestamp updates
- Row Level Security (RLS) policies

## Step 5: Test the Integration

1. Start your development server:
   ```bash
   npm run dev
   ```

2. Open your dashboard at `http://localhost:3000`

3. Try the following:
   - Go to **Account Settings** and fill out the form
   - Click **Save Account Settings**
   - Go to **Agent Settings** and modify the configuration
   - Click **Save Agent Settings**
   - Refresh the page to verify data persistence

4. Check your Supabase dashboard:
   - Go to **Table Editor**
   - You should see data in both `bob_accounts` and `agent_settings` tables

## Step 6: Update Python Backend (Optional)

If you want your Python backend to also access Supabase data, you can install the Supabase Python client:

```bash
cd scripts
pip install supabase
```

Then update your Python server to use Supabase instead of local storage.

## Database Schema

### bob_accounts Table
- `id`: UUID primary key
- `name`: Text (required)
- `role`: Text
- `role_description`: Text
- `profile`: Text (required)
- `services_type`: Text ('pricing', 'list', 'none')
- `services`: JSONB array of services
- `services_not_provided`: Text
- `location`: Text (required)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### agent_settings Table
- `id`: UUID primary key
- `enabled`: Boolean
- `delay_time`: Integer (0-10 seconds)
- `default_greeting`: Text
- `created_at`: Timestamp
- `updated_at`: Timestamp

## Troubleshooting

### Common Issues

1. **"Invalid API key" error**
   - Make sure you're using the `anon public` key, not the `service_role` key
   - Verify the key is correctly copied without extra spaces

2. **"Table doesn't exist" error**
   - Make sure you ran the SQL setup script in Supabase
   - Check that the table names match exactly

3. **"RLS policy violation" error**
   - The setup script includes permissive RLS policies
   - If you want more security, you can modify the policies

4. **Environment variables not working**
   - Restart your development server after adding environment variables
   - For Vercel, redeploy after adding environment variables

### Security Considerations

The current setup uses permissive RLS policies for simplicity. For production:

1. Consider implementing user authentication
2. Add more restrictive RLS policies
3. Use the `service_role` key only on the server side
4. Implement proper input validation

## API Endpoints

The integration provides these new API endpoints:

- `GET /api/account-settings` - Fetch account settings
- `POST /api/account-settings` - Save account settings
- `GET /api/agent-settings` - Fetch agent settings
- `POST /api/agent-settings`