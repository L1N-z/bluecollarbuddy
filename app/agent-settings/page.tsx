'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Button,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Switch, 
  TextField, 
  Slider,
  Box,
  CircularProgress,
  Alert
} from '@mui/material'
import { Power } from 'lucide-react'

interface AgentSettings {
  enabled: boolean
  delayTime: number
  defaultGreeting: string
}

export default function AgentSettingsPage() {
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'info' | 'error'>('info')
  const [loading, setLoading] = useState(true) // Start with true to show loader
  const [saving, setSaving] = useState(false)

  const [agentSettings, setAgentSettings] = useState<AgentSettings>({
    enabled: true,
    delayTime: 2,
    defaultGreeting: "Hi! I'm BizzyBuddy, your friendly assistant. How can I help you today?"
  })

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      // setLoading(true) is already set
      const response = await fetch('/api/agent-settings')
      if (response.ok) {
        const data = await response.json()
        if (data.settings) {
          setAgentSettings({
            enabled: data.settings.enabled,
            delayTime: data.settings.delay_time,
            defaultGreeting: data.settings.default_greeting
          })
        }
      }
    } catch (error) {
      console.error('Error loading agent settings:', error)
      setMessage('Error loading settings')
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  const saveAgentSettings = async () => {
    try {
      setSaving(true)
      setMessage('')

      const response = await fetch('/api/agent-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings: agentSettings })
      })

      const data = await response.json()

      if (response.ok) {
        setMessage('Agent settings saved successfully!')
        setMessageType('success')
      } else {
        setMessage(data.error || 'Failed to save agent settings')
        setMessageType('error')
      }
    } catch (error) {
      console.error('Error saving agent settings:', error)
      setMessage('Error saving agent settings')
      setMessageType('error')
    } finally {
      setSaving(false)
    }
  }
  
  const clearAgentSettings = () => {
    setAgentSettings({
      enabled: true,
      delayTime: 2,
      defaultGreeting: "Hi! I'm BizzyBuddy, your friendly assistant. How can I help you today?"
    })
    setMessage('Form cleared to default. Click "Save" to apply changes.')
    setMessageType('info')
  }

  if (loading) {
    return (
      <Box className="min-h-screen flex justify-center items-center">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <div className="min-h-screen bg-white p-4 sm:p-6 lg:p-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto"
      >
        <Card className="shadow-lg">
          <CardHeader
            title={
              <Box className="flex items-center space-x-3">
                <Power className="w-8 h-8 text-blue-500" />
                <Typography variant="h4" component="span">
                  Agent Settings
                </Typography>
              </Box>
            }
            subheader="Configure the behavior of your WhatsApp agent."
          />
          <CardContent className="space-y-8">
            {message && (
              <Alert severity={messageType} onClose={() => setMessage('')}>
                {message}
              </Alert>
            )}

            <Box component="fieldset" className="border p-4 rounded-md">
              <legend className="text-xl font-semibold text-gray-700 px-2">Agent Status</legend>
              <Box className="flex items-center justify-between">
                <div>
                  <Typography variant="body1" className="font-semibold text-gray-700">Enable WhatsApp Agent</Typography>
                  <Typography variant="body2" className="text-sm text-gray-500 mt-1">
                    When enabled, the agent will respond automatically.
                  </Typography>
                </div>
                <Switch
                  checked={agentSettings.enabled}
                  onChange={(e) => setAgentSettings(prev => ({ ...prev, enabled: e.target.checked }))}
                  color="primary"
                />
              </Box>
            </Box>

            <Box component="fieldset" className="border p-4 rounded-md">
              <legend className="text-xl font-semibold text-gray-700 px-2">Message Delay</legend>
              <Typography variant="body2" className="text-sm text-gray-500 mb-2">
                A short delay makes the agent feel more natural. ({agentSettings.delayTime} seconds)
              </Typography>
              <Slider
                value={agentSettings.delayTime}
                onChange={(_, value) => setAgentSettings(prev => ({ ...prev, delayTime: value as number }))}
                aria-labelledby="delay-slider"
                valueLabelDisplay="auto"
                step={1}
                marks
                min={0}
                max={10}
              />
            </Box>

            <Box component="fieldset" className="border p-4 rounded-md">
              <legend className="text-xl font-semibold text-gray-700 px-2">Default Greeting Message</legend>
               <Typography variant="body2" className="text-sm text-gray-500 mb-4">
                This is the first message the agent sends in a new conversation.
              </Typography>
              <TextField
                multiline
                rows={4}
                fullWidth
                variant="outlined"
                label="Greeting Message"
                value={agentSettings.defaultGreeting}
                onChange={(e) => setAgentSettings(prev => ({ ...prev, defaultGreeting: e.target.value }))}
                placeholder="e.g., Hi there! I'm BizzyBuddy, your friendly assistant..."
              />
            </Box>
            
            <Box className="flex justify-end space-x-4 pt-4 border-t">
               <Button 
                variant="outlined" 
                color="secondary" 
                onClick={clearAgentSettings}
                disabled={saving}
              >
                Reset to Default
              </Button>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={saveAgentSettings}
                disabled={saving}
                startIcon={saving ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {saving ? 'Saving...' : 'Save Agent Settings'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
} 