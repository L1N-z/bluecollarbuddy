'use client'

import { Card, CardContent, Typography, Button, Box } from '@mui/material'
import { Calendar } from 'lucide-react'
import Link from 'next/link'

export default function CalendarPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-white p-4">
      <Card className="w-full max-w-md text-center shadow-lg p-8">
        <Box className="mx-auto bg-blue-100 p-4 rounded-full w-fit">
          <Calendar className="w-12 h-12 text-blue-600" />
        </Box>
        <CardContent>
          <Typography variant="h4" component="h1" className="mt-6 font-bold text-gray-800">
            Calendar
          </Typography>
          <Typography variant="h6" className="text-lg text-gray-600 my-4">
            This feature is coming soon!
          </Typography>
          <Typography variant="body1" className="text-gray-500 mb-8">
            You will be able to view and manage your appointments directly from here.
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