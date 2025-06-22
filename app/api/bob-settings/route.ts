import { NextRequest, NextResponse } from 'next/server';

interface Service {
  name: string;
  price?: number;
}

interface BobAccount {
  name: string;
  role: string;
  roleDescription: string;
  profile: string;
  servicesType: 'pricing' | 'list' | 'none';
  services: Service[];
  servicesNotProvided: string;
  location: string;
}

interface AgentSettings {
  enabled: boolean;
  delayTime: number;
  defaultGreeting: string;
}

// In-memory storage (in production, use a database)
let bobAccount: BobAccount | null = null;
let agentSettings: AgentSettings = {
  enabled: true,
  delayTime: 5,
  defaultGreeting: ''
};

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const type = searchParams.get('type');

  if (type === 'account') {
    return NextResponse.json({ account: bobAccount });
  } else if (type === 'agent') {
    return NextResponse.json({ agentSettings });
  } else {
    return NextResponse.json({ 
      account: bobAccount, 
      agentSettings 
    });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type, data } = body;

    if (type === 'account') {
      // Validate required fields
      if (!data.name || !data.profile || !data.location) {
        return NextResponse.json(
          { error: 'Missing required fields: name, profile, location' },
          { status: 400 }
        );
      }

      if (data.servicesType !== 'none' && data.services.some((s: Service) => !s.name)) {
        return NextResponse.json(
          { error: 'All services must have names' },
          { status: 400 }
        );
      }

      bobAccount = data;
      
      // Update the Python server with new account details
      await updatePythonServerSettings();
      
      return NextResponse.json({ 
        success: true, 
        message: 'Account settings saved successfully' 
      });
    } else if (type === 'agent') {
      agentSettings = data;
      
      // Update the Python server with new agent settings
      await updatePythonServerSettings();
      
      return NextResponse.json({ 
        success: true, 
        message: 'Agent settings saved successfully' 
      });
    } else {
      return NextResponse.json(
        { error: 'Invalid type parameter' },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Error saving settings:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

async function updatePythonServerSettings() {
  try {
    const pythonServerUrl = process.env.PYTHON_SERVER_URL;
    if (!pythonServerUrl) {
      console.warn('Python server URL not configured');
      return;
    }

    const settingsData = {
      bobAccount,
      agentSettings
    };

    const response = await fetch(`${pythonServerUrl}/update-settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settingsData),
    });

    if (!response.ok) {
      console.error('Failed to update Python server settings');
    }
  } catch (error) {
    console.error('Error updating Python server settings:', error);
  }
} 