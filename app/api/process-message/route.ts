import { type NextRequest, NextResponse } from "next/server"
import { spawn } from "child_process"
import path from "path"

export async function POST(request: NextRequest) {
  try {
    const { message, from } = await request.json()

    // Choose processing method based on environment
    // In production (Vercel), always use Python server
    // In development, use direct script execution
    const isProduction = process.env.NODE_ENV === 'production'
    const usePythonServer = isProduction || process.env.USE_PYTHON_SERVER === "true"
    
    let response: string
    
    if (usePythonServer) {
      // Use separate Python server (production)
      response = await processMessageWithPythonServer(message, from)
    } else {
      // Use direct Python script execution (development only)
      response = await processMessageWithPythonScript(message, from)
    }

    return NextResponse.json({ response })
  } catch (error) {
    console.error("Process message error:", error)
    return NextResponse.json({ error: "Failed to process message" }, { status: 500 })
  }
}

async function processMessageWithPythonServer(message: string, from: string): Promise<string> {
  try {
    // Call the Python script via HTTP request to a local Python server
    // In production, you'd run the Python script as a separate service
    const pythonServerUrl = process.env.PYTHON_SERVER_URL || "http://localhost:8000"
    
    const response = await fetch(`${pythonServerUrl}/process-message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message, 
        phone_number: from 
      }),
    })

    if (!response.ok) {
      throw new Error(`Python server error: ${response.statusText}`)
    }

    const result = await response.json()
    console.log(`[DEBUG] Python server response for ${from}: ${result.response}`)

    return result.response
  } catch (error) {
    console.error("Python server processing error:", error)
    
    // Production fallback: Use TypeScript-based processing
    return processMessageWithTypeScript(message, from)
  }
}

function processMessageWithTypeScript(message: string, from: string): string {
  console.log(`[DEBUG] Using TypeScript fallback for ${from}: ${message}`)
  
  // Check if it's a greeting
  if (isGreeting(message)) {
    console.log(`[DEBUG] TypeScript fallback: Detected greeting from ${from}: ${message}`)
    return getGreetingResponse()
  }

  // For non-greetings, provide a helpful response
  const lowerMessage = message.toLowerCase()
  
  if (lowerMessage.includes('beehive') || lowerMessage.includes('hive')) {
    return "Hey! I'd love to help you with your beehive needs. I build custom hives, do repairs, and provide consultation. What specific help do you need?"
  }
  
  if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('how much')) {
    return "I prefer to discuss pricing after understanding your specific needs. Could you tell me more about what you're looking for - are you interested in a new hive, repairs, or consultation?"
  }
  
  if (lowerMessage.includes('location') || lowerMessage.includes('where') || lowerMessage.includes('area')) {
    return "I serve the local area within about 50 miles. Where are you located? I can let you know if I can help with your beekeeping needs."
  }
  
  if (lowerMessage.includes('appointment') || lowerMessage.includes('schedule') || lowerMessage.includes('meet')) {
    return "I'd be happy to schedule a consultation! What works better for you - weekday afternoons or weekends? And what's your location so I can confirm I can service your area?"
  }
  
  // Default response for other messages
  return "Thanks for reaching out! I'm Bob, your friendly beehive builder. I can help with custom hive construction, repairs, consultations, and beekeeping advice. What can I do for you today?"
}

async function processMessageWithPythonScript(message: string, from: string): Promise<string> {
  return new Promise((resolve, reject) => {
    try {
      // Path to the Python script
      const scriptPath = path.join(process.cwd(), "scripts", "gemini_message_processor.py")
      
      // Create a temporary Python script that processes the message
      const tempScript = `
import sys
import json
import os
sys.path.append('${path.join(process.cwd(), "scripts")}')

from gemini_message_processor import GeminiMessageProcessor

# Set environment variables
${Object.entries(process.env)
  .filter(([key]) => key.startsWith('GEMINI_') || key.startsWith('TWILIO_'))
  .map(([key, value]) => `os.environ['${key}'] = '${value}'`)
  .join('\n')}

# Process the message
processor = GeminiMessageProcessor()
result = processor.process_message('${message.replace(/'/g, "\\'")}', '${from.replace(/'/g, "\\'")}')

# Output result as JSON
print(json.dumps(result))
`
      
      // Write temporary script
      const tempScriptPath = path.join(process.cwd(), "scripts", "temp_process.py")
      require('fs').writeFileSync(tempScriptPath, tempScript)
      
      // Execute Python script
      const pythonProcess = spawn('python', [tempScriptPath], {
        cwd: path.join(process.cwd(), "scripts"),
        env: { ...process.env, PYTHONPATH: path.join(process.cwd(), "scripts") }
      })
      
      let output = ''
      let errorOutput = ''
      
      pythonProcess.stdout.on('data', (data) => {
        output += data.toString()
      })
      
      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString()
      })
      
      pythonProcess.on('close', (code) => {
        // Clean up temporary script
        try {
          require('fs').unlinkSync(tempScriptPath)
        } catch (e) {
          // Ignore cleanup errors
        }
        
        if (code === 0) {
          try {
            const result = JSON.parse(output.trim())
            console.log(`[DEBUG] Direct Python response for ${from}: ${result.response}`)
            resolve(result.response)
          } catch (parseError) {
            console.error("Failed to parse Python output:", parseError)
            console.log("Raw output:", output)
            reject(new Error("Failed to parse Python script output"))
          }
        } else {
          console.error("Python script failed:", errorOutput)
          reject(new Error(`Python script failed with code ${code}: ${errorOutput}`))
        }
      })
      
      pythonProcess.on('error', (error) => {
        console.error("Failed to start Python process:", error)
        reject(error)
      })
      
    } catch (error) {
      console.error("Direct Python processing error:", error)
      reject(error)
    }
  })
}

function isGreeting(message: string): boolean {
  const greetingWords = [
    "hello",
    "hi",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "greetings",
    "howdy",
    "what's up",
    "sup",
  ]

  const messageLower = message.toLowerCase().trim()

  // Check if message starts with or contains greeting words
  for (const greeting of greetingWords) {
    if (messageLower.startsWith(greeting) || greeting === messageLower) {
      // Make sure it's not part of a larger sentence about something else
      if (messageLower.split(" ").length <= 3) {
        // Short messages are likely greetings
        return true
      }
      // Check if greeting is at the beginning
      if (messageLower.startsWith(greeting)) {
        return true
      }
    }
  }

  return false
}

function getGreetingResponse(): string {
  const greetings = [
    "Hey there! Bob here, your friendly neighborhood beehive builder. How can I help you today?",
    "Hi! This is Bob from Bob's Beehive Building. What can I do for you?",
    "Hello! Bob speaking - I build custom beehives and help folks with all their bee-related needs. What's on your mind?",
    "Hey! Bob here. I'm all about helping people with their beekeeping projects. What brings you my way today?",
  ]

  return greetings[Math.floor(Math.random() * greetings.length)]
}
