import { NextRequest, NextResponse } from 'next/server';
import { sendWhatsAppMessage } from '@/lib/twilio';

// In-memory conversation history (in production, use a database)
const conversationHistory: { [phoneNumber: string]: Array<{ role: 'user' | 'assistant', content: string, timestamp: Date }> } = {};

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const formData = await request.formData();
    const from = formData.get('From') as string;
    const body = formData.get('Body') as string;
    const messageId = formData.get('MessageSid') as string;

    console.log(`[DEBUG] Webhook received from ${from}: ${body}`);

    if (!from || !body) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Clean phone number (remove 'whatsapp:' prefix)
    const phoneNumber = from.replace('whatsapp:', '');

    // Get conversation history for this phone number
    if (!conversationHistory[phoneNumber]) {
      conversationHistory[phoneNumber] = [];
    }

    // Add user message to history
    conversationHistory[phoneNumber].push({
      role: 'user',
      content: body,
      timestamp: new Date()
    });

    // Keep only last 10 messages to prevent memory issues
    if (conversationHistory[phoneNumber].length > 10) {
      conversationHistory[phoneNumber] = conversationHistory[phoneNumber].slice(-10);
    }

    console.log(`[DEBUG] Conversation history for ${phoneNumber}:`, conversationHistory[phoneNumber]);

    // Process message with conversation history
    const processResponse = await fetch(`${process.env.PYTHON_SERVER_URL}/process-message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: body,
        phone_number: phoneNumber,
        conversation_history: conversationHistory[phoneNumber].slice(0, -1) // Exclude current message
      }),
    });

    if (!processResponse.ok) {
      console.error(`[ERROR] Process message failed: ${processResponse.status}`);
      await sendWhatsAppMessage(phoneNumber, "I'm having trouble processing your message right now. Could you try again?");
      return NextResponse.json({ error: 'Failed to process message' }, { status: 500 });
    }

    const processResult = await processResponse.json();
    console.log(`[DEBUG] Process result for ${phoneNumber}:`, processResult);
    
    const response = processResult.response || "I'm sorry, I didn't understand that. Could you please rephrase?";

    // Add assistant response to history
    conversationHistory[phoneNumber].push({
      role: 'assistant',
      content: response,
      timestamp: new Date()
    });

    // Send WhatsApp response
    await sendWhatsAppMessage(phoneNumber, response);

    console.log(`[DEBUG] Response sent to ${phoneNumber}: ${response}`);

    return NextResponse.json({ success: true });

  } catch (error) {
    console.error(`[ERROR] Webhook processing failed: ${error}`);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest): Promise<NextResponse> {
  // Handle webhook verification for Twilio
  const url = new URL(request.url);
  const mode = url.searchParams.get('hub.mode');
  const token = url.searchParams.get('hub.verify_token');
  const challenge = url.searchParams.get('hub.challenge');

  if (mode === 'subscribe' && token === process.env.TWILIO_WEBHOOK_VERIFY_TOKEN) {
    console.log('[DEBUG] Webhook verified successfully');
    return new NextResponse(challenge, { status: 200 });
  }

  return NextResponse.json({ error: 'Invalid verification token' }, { status: 403 });
}
