'use client'

import { Card, CardContent, Typography, Button, Box } from '@mui/material'
import { MessageSquare } from 'lucide-react'
import Link from 'next/link'

export default function MessagesPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-white p-4">
      <Card className="w-full max-w-md text-center shadow-lg p-8">
        <Box className="mx-auto bg-green-100 p-4 rounded-full w-fit">
          <MessageSquare className="w-12 h-12 text-green-600" />
        </Box>
        <CardContent>
          <Typography variant="h4" component="h1" className="mt-6 font-bold text-gray-800">
            WhatsApp Messages
          </Typography>
          <Typography variant="h6" className="text-lg text-gray-600 my-4">
            This feature is coming soon!
          </Typography>
          <Typography variant="body1" className="text-gray-500 mb-8">
            You will be able to view your complete WhatsApp conversation history here.
          </Typography>
          <Link href="/" passHref>
            <Button variant="contained" color="primary">
              Back to Dashboard
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  )
} 