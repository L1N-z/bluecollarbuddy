import { type NextRequest, NextResponse } from "next/server"
import { GoogleGenerativeAI } from "@google/generative-ai"

// Initialize Gemini AI
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!)

// Store conversation context (in production, use a proper database)
const conversationContext = new Map<string, Array<{ role: string; content: string }>>()

// Store pending messages for batching
const pendingMessages = new Map<string, { messages: string[]; timeout: NodeJS.Timeout }>()

export async function POST(request: NextRequest): Promise<Response> {
  try {
    const { message, from } = await request.json()

    if (!process.env.GEMINI_API_KEY) {
      throw new Error("GEMINI_API_KEY not configured")
    }

    console.log(`[DEBUG] Gemini chat request from ${from}: ${message}`)

    // Handle message batching - wait 20 seconds for multiple messages
    return new Promise<Response>((resolve) => {
      const existingPending = pendingMessages.get(from)

      if (existingPending) {
        // Add to existing batch
        existingPending.messages.push(message)
        clearTimeout(existingPending.timeout)
        console.log(`[DEBUG] Added to existing batch for ${from}. Total messages: ${existingPending.messages.length}`)
      } else {
        // Start new batch
        pendingMessages.set(from, {
          messages: [message],
          timeout: null as any,
        })
        console.log(`[DEBUG] Started new batch for ${from}`)
      }

      // Set timeout for processing
      const timeout = setTimeout(async () => {
        const pending = pendingMessages.get(from)
        if (!pending) return

        console.log(`[DEBUG] Processing batch for ${from} with ${pending.messages.length} messages`)

        // Remove from pending
        pendingMessages.delete(from)

        // Combine messages
        const combinedMessage = pending.messages.join(" ")
        console.log(`[DEBUG] Combined message: ${combinedMessage}`)

        try {
          const response = await processWithGemini(combinedMessage, from)
          console.log(`[DEBUG] Final response for ${from}: ${response}`)
          resolve(NextResponse.json({ response }))
        } catch (error) {
          console.error("Gemini processing error:", error)
          resolve(
            NextResponse.json({
              response:
                "Hey, this is Bob! I'm having a bit of trouble with my system right now, but I'd love to help you with your beehive needs. Could you try again in a moment?",
            }),
          )
        }
      }, 20000) // 20 seconds

      // Update timeout reference
      const currentPending = pendingMessages.get(from)!
      currentPending.timeout = timeout
    })
  } catch (error) {
    console.error("Gemini chat error:", error)
    return NextResponse.json(
      {
        response:
          "Hey, this is Bob! I'm having some technical difficulties right now. Could you try reaching out again in a few minutes?",
      },
      { status: 500 },
    )
  }
}

async function processWithGemini(message: string, from: string): Promise<string> {
  const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash-exp" })

  // Get or initialize conversation context
  let context = conversationContext.get(from) || []

  // Bob's persona and business context
  const bobPersona = `
You are Bob, a friendly and experienced beehive builder who runs a small beehive construction business called "Bob's Beehive Building". 

BUSINESS CONTEXT:
- You build custom beehives, repair existing ones, and provide beekeeping consultation
- You serve the local area and can travel within a reasonable distance (about 50 miles)
- You're knowledgeable about different hive types (Langstroth, Top Bar, Warre, Flow Hive, etc.)
- You care about bee health and sustainable beekeeping practices
- You offer services like: custom hive construction, repairs, consultations, inspections, equipment recommendations

CONVERSATION FLOW YOU SHOULD FOLLOW:
1. Initial Contact & Greeting → Welcome customers warmly
2. Issue Discovery → Ask about their beekeeping needs, experience level, hive preferences
3. Address Collection → Get their location to confirm you can service their area
4. Scheduling → Propose meeting times for consultation or work
5. Confirmation & Wrap-up → Confirm details and next steps

PERSONALITY TRAITS:
- Friendly, approachable, and enthusiastic about bees and beekeeping
- Professional but not overly formal - like talking to a neighbor
- Ask follow-up questions to understand their specific needs
- Share relevant tips or insights when appropriate
- Keep responses conversational and concise (2-4 sentences typically)
- Use first person - you ARE Bob, don't refer to yourself in third person

IMPORTANT GUIDELINES:
- Always respond as Bob in first person
- Never mention that you're an AI or language model
- If asked about specific pricing, explain you prefer to discuss after understanding their needs
- If they're outside your service area, politely explain and offer general advice
- Be helpful and try to guide the conversation toward understanding their beekeeping needs
- Show genuine interest in their beekeeping journey

Your response should be natural, helpful, and move the conversation forward toward scheduling a consultation or providing the help they need.
`

  const conversationHistory =
    context.length > 0
      ? context.map((msg) => `${msg.role === "user" ? "Customer" : "Bob"}: ${msg.content}`).join("\n")
      : "No previous conversation history."

  const systemPrompt = `
${bobPersona}

CONVERSATION HISTORY:
${conversationHistory}

CURRENT MESSAGE TO RESPOND TO:
"${message}"

INSTRUCTIONS:
Please respond as Bob to the current message. Consider the conversation history to maintain context and continuity. 

IMPORTANT: Your entire response should be enclosed in double quotation marks like this: "Your response here"

Respond naturally as Bob would, keeping in mind the conversation flow and your role as a beehive builder.
`

  try {
    console.log(`[DEBUG] Sending to Gemini for ${from}`)
    const result = await model.generateContent(systemPrompt)
    const llmOutput = result.response.text()

    console.log(`[DEBUG] Raw LLM response for ${from}: ${llmOutput}`)

    // Extract response from quotes
    const extractedResponse = extractResponseFromQuotes(llmOutput)

    console.log(`[DEBUG] Extracted response for ${from}: ${extractedResponse}`)

    // Update conversation context
    context.push({ role: "user", content: message })
    context.push({ role: "assistant", content: extractedResponse })

    // Keep only last 20 exchanges to manage context size
    if (context.length > 20) {
      context = context.slice(-20)
    }

    conversationContext.set(from, context)

    return extractedResponse
  } catch (error) {
    console.error("Gemini API error:", error)
    throw error
  }
}

function extractResponseFromQuotes(llmOutput: string): string {
  // Look for text within double quotes
  const quotePattern = /"([^"]*)"/
  const match = llmOutput.match(quotePattern)

  if (match && match[1]) {
    const extracted = match[1].trim()
    console.log(`[DEBUG] Successfully extracted response from quotes: ${extracted}`)
    return extracted
  } else {
    // If no quotes found, return the whole response but log it
    console.log(`[DEBUG] No quotes found in LLM output, using full response: ${llmOutput}`)
    return llmOutput.trim()
  }
}
