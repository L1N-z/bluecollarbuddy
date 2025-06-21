import { type NextRequest, NextResponse } from "next/server"
import twilio from "twilio"

// Initialize Twilio client
const twilioClient = twilio(
  process.env.TWILIO_ACCOUNT_SID!,
  process.env.TWILIO_AUTH_TOKEN!
)

// Store message timestamps to handle batching
const messageTimestamps = new Map<string, number>()

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()

    // Extract Twilio webhook data
    const messageData = {
      MessageSid: formData.get("MessageSid"),
      From: formData.get("From"),
      To: formData.get("To"),
      Body: formData.get("Body"),
      NumMedia: formData.get("NumMedia"),
      ProfileName: formData.get("ProfileName"),
    }

    console.log("Received WhatsApp message:", messageData)

    const from = messageData.From as string
    const body = messageData.Body as string

    // Check if this is a quick follow-up message (within 20 seconds)
    const now = Date.now()
    const lastMessageTime = messageTimestamps.get(from) || 0
    const timeDiff = now - lastMessageTime

    messageTimestamps.set(from, now)

    // If it's a quick follow-up (within 20 seconds), don't send immediate response
    // The batching logic in gemini-chat will handle it
    if (timeDiff < 20000 && lastMessageTime > 0) {
      console.log(`Quick follow-up message from ${from}, batching...`)

      // Still process for batching but don't send immediate response
      await processMessage(body, from)

      // Return empty TwiML to avoid duplicate responses
      return new NextResponse(`<?xml version="1.0" encoding="UTF-8"?><Response></Response>`, {
        headers: { "Content-Type": "text/xml" },
      })
    }

    // Process the message and get response
    const processedResponse = await processMessage(body, from)

    // Send the response back via Twilio WhatsApp API
    try {
      await twilioClient.messages.create({
        body: processedResponse,
        from: process.env.TWILIO_PHONE_NUMBER!, // Your Twilio WhatsApp number
        to: from, // The user's WhatsApp number
      })

      console.log(`✅ Response sent to ${from}: ${processedResponse}`)
    } catch (twilioError) {
      console.error("Twilio send error:", twilioError)
      // Fallback to TwiML if Twilio API fails
      const twimlResponse = `<?xml version="1.0" encoding="UTF-8"?>
      <Response>
        <Message>
          <Body>${processedResponse}</Body>
        </Message>
      </Response>`

      return new NextResponse(twimlResponse, {
        headers: { "Content-Type": "text/xml" },
      })
    }

    // Return empty TwiML since we sent the message via API
    return new NextResponse(`<?xml version="1.0" encoding="UTF-8"?><Response></Response>`, {
      headers: { "Content-Type": "text/xml" },
    })
  } catch (error) {
    console.error("Webhook error:", error)

    // Return a friendly error message as TwiML
    const errorResponse = `<?xml version="1.0" encoding="UTF-8"?>
    <Response>
      <Message>
        <Body>Hey, this is Bob! I'm having some technical trouble right now. Could you try sending your message again in a moment?</Body>
      </Message>
    </Response>`

    return new NextResponse(errorResponse, {
      headers: { "Content-Type": "text/xml" },
    })
  }
}

async function processMessage(message: string, from: string): Promise<string> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"}/api/process-message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, from }),
    })

    if (!response.ok) {
      throw new Error(`Processing API error: ${response.statusText}`)
    }

    const result = await response.json()
    return result.response
  } catch (error) {
    console.error("Message processing error:", error)
    return "Hey, this is Bob! I'm having a bit of trouble with my system right now, but I'd love to help you with your beehive needs. Could you try again in a moment?"
  }
}
