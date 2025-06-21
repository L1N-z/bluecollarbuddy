import twilio from 'twilio';

// Initialize Twilio client
const twilioClient = twilio(
  process.env.TWILIO_ACCOUNT_SID!,
  process.env.TWILIO_AUTH_TOKEN!
);

export async function sendWhatsAppMessage(to: string, body: string): Promise<void> {
  try {
    // Add 'whatsapp:' prefix if not present
    const formattedTo = to.startsWith('whatsapp:') ? to : `whatsapp:${to}`;
    
    await twilioClient.messages.create({
      body: body,
      from: process.env.TWILIO_PHONE_NUMBER!, // Your Twilio WhatsApp number
      to: formattedTo,
    });

    console.log(`✅ WhatsApp message sent to ${to}: ${body}`);
  } catch (error) {
    console.error(`❌ Failed to send WhatsApp message to ${to}:`, error);
    throw error;
  }
}

export function formatPhoneNumber(phoneNumber: string): string {
  // Remove 'whatsapp:' prefix if present
  return phoneNumber.replace('whatsapp:', '');
} 