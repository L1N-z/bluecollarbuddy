'use client'

import { useState, useEffect } from 'react'
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Box,
  CircularProgress,
  Alert,
  SelectChangeEvent
} from '@mui/material'
import { User, MapPin, Plus, X } from 'lucide-react'
import { motion } from 'framer-motion'

interface Service {
  name: string
  price?: number
}

interface BobAccount {
  name: string
  role: string
  roleDescription: string
  profile: string
  servicesType: 'pricing' | 'list' | 'none'
  services: Service[]
  servicesNotProvided: string
  location: string
}

export default function AccountSettingsPage() {
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'info' | 'error'>('info')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const [account, setAccount] = useState<BobAccount>({
    name: '',
    role: '',
    roleDescription: '',
    profile: '',
    servicesType: 'pricing',
    services: [],
    servicesNotProvided: '',
    location: ''
  })

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/account-settings')
      if (response.ok) {
        const data = await response.json()
        if (data.account) {
          setAccount({
            name: data.account.name || '',
            role: data.account.role || '',
            roleDescription: data.account.role_description || '',
            profile: data.account.profile || '',
            servicesType: data.account.services_type || 'pricing',
            services: data.account.services || [],
            servicesNotProvided: data.account.services_not_provided || '',
            location: data.account.location || ''
          })
        }
      }
    } catch (error) {
      console.error('Error loading account settings:', error)
      setMessage('Error loading settings')
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  const addService = () => {
    setAccount(prev => ({
      ...prev,
      services: [...prev.services, { name: '', price: 0 }]
    }))
  }

  const removeService = (index: number) => {
    setAccount(prev => ({
      ...prev,
      services: prev.services.filter((_, i) => i !== index)
    }))
  }

  const updateService = (index: number, field: 'name' | 'price', value: string | number) => {
    setAccount(prev => ({
      ...prev,
      services: prev.services.map((service, i) =>
        i === index ? { ...service, [field]: value } : service
      )
    }))
  }

  const saveAccount = async () => {
    try {
      setSaving(true)
      setMessage('')

      const response = await fetch('/api/account-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account })
      })

      const data = await response.json()

      if (response.ok) {
        setMessage('Account settings saved successfully!')
        setMessageType('success')
      } else {
        setMessage(data.error || 'Failed to save account settings')
        setMessageType('error')
      }
    } catch (error) {
      console.error('Error saving account settings:', error)
      setMessage('Error saving account settings')
      setMessageType('error')
    } finally {
      setSaving(false)
    }
  }

  const clearAccount = () => {
    setAccount({
      name: '',
      role: '',
      roleDescription: '',
      profile: '',
      servicesType: 'pricing',
      services: [],
      servicesNotProvided: '',
      location: ''
    })
    setMessage('Form cleared. Click "Save" to apply changes.')
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
        className="max-w-4xl mx-auto"
      >
        <Card className="shadow-lg">
          <CardHeader
            title={
              <Box className="flex items-center space-x-3">
                <User className="w-8 h-8 text-green-500" />
                <Typography variant="h4" component="span">
                  Account Settings
                </Typography>
              </Box>
            }
            subheader="Manage your public profile and service offerings."
          />
          <CardContent className="space-y-8">
            {message && (
              <Alert severity={messageType} onClose={() => setMessage('')}>
                {message}
              </Alert>
            )}

            {/* Basic Information */}
            <Box component="fieldset" className="border p-4 rounded-md space-y-6">
              <legend className="text-xl font-semibold text-gray-700 px-2">Basic Information</legend>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <TextField
                  label="Name *"
                  value={account.name}
                  onChange={(e) => setAccount(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Bob Smith"
                  fullWidth
                  variant="outlined"
                />
                <TextField
                  label="Role"
                  value={account.role}
                  onChange={(e) => setAccount(prev => ({ ...prev, role: e.target.value }))}
                  placeholder="e.g., Beehive Builder & Consultant"
                  fullWidth
                  variant="outlined"
                />
              </div>
              <TextField
                label="Role Description"
                value={account.roleDescription}
                onChange={(e) => setAccount(prev => ({ ...prev, roleDescription: e.target.value }))}
                placeholder="A brief, engaging description of your role."
                fullWidth
                multiline
                rows={2}
                variant="outlined"
              />
              <TextField
                label="Your Profile *"
                value={account.profile}
                onChange={(e) => setAccount(prev => ({ ...prev, profile: e.target.value }))}
                placeholder="Tell clients about your experience, your passion for bees, and what makes your service unique."
                fullWidth
                multiline
                rows={4}
                variant="outlined"
              />
              <TextField
                label="Location (UK Postcode) *"
                value={account.location}
                onChange={(e) => setAccount(prev => ({ ...prev, location: e.target.value }))}
                placeholder="e.g., SW1A 1AA"
                fullWidth
                variant="outlined"
                InputProps={{
                  startAdornment: (
                    <MapPin className="w-5 h-5 text-gray-400 mr-2" />
                  ),
                }}
              />
            </Box>

            {/* Services Section */}
            <Box component="fieldset" className="border p-4 rounded-md space-y-6">
              <legend className="text-xl font-semibold text-gray-700 px-2">Services Configuration</legend>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="services-type-label">How do you want to list services? *</InputLabel>
                <Select
                  labelId="services-type-label"
                  label="How do you want to list services? *"
                  value={account.servicesType}
                  onChange={(e: SelectChangeEvent) => setAccount(prev => ({ ...prev, servicesType: e.target.value as 'pricing' | 'list' | 'none' }))}
                >
                  <MenuItem value="pricing">Show services with prices</MenuItem>
                  <MenuItem value="list">Show services without prices</MenuItem>
                  <MenuItem value="none">Do not list specific services</MenuItem>
                </Select>
              </FormControl>

              {(account.servicesType === 'pricing' || account.servicesType === 'list') && (
                <Box className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Typography variant="body1" className="font-medium text-gray-700">Your Services</Typography>
                    <Button
                      type="button"
                      onClick={addService}
                      variant="outlined"
                      startIcon={<Plus className="w-4 h-4" />}
                    >
                      Add Service
                    </Button>
                  </div>
                  <div className="space-y-4">
                    {account.services.map((service, index) => (
                      <motion.div key={index} layout className="flex items-center space-x-2 p-3 bg-gray-50 rounded-md border">
                        <TextField
                          label="Service Name"
                          value={service.name}
                          onChange={(e) => updateService(index, 'name', e.target.value)}
                          variant="outlined"
                          size="small"
                          className="flex-grow"
                        />
                        {account.servicesType === 'pricing' && (
                          <TextField
                            label="Price (£)"
                            type="number"
                            value={service.price}
                            onChange={(e) => updateService(index, 'price', parseFloat(e.target.value))}
                            variant="outlined"
                            size="small"
                            className="w-28"
                          />
                        )}
                        <IconButton onClick={() => removeService(index)} color="error">
                          <X className="w-5 h-5" />
                        </IconButton>
                      </motion.div>
                    ))}
                  </div>
                </Box>
              )}

              {account.servicesType === 'none' && (
                 <TextField
                  label="Services Not Provided"
                  value={account.servicesNotProvided}
                  onChange={(e) => setAccount(prev => ({ ...prev, servicesNotProvided: e.target.value }))}
                  placeholder="Briefly state what you do not provide, e.g., 'I do not offer hive removal services.'"
                  fullWidth
                  multiline
                  rows={2}
                  variant="outlined"
                />
              )}
            </Box>
            
            <Box className="flex justify-end space-x-4 pt-4 border-t">
              <Button 
                variant="outlined" 
                color="secondary" 
                onClick={clearAccount}
                disabled={saving}
              >
                Clear Form
              </Button>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={saveAccount}
                disabled={saving}
                startIcon={saving ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {saving ? 'Saving...' : 'Save Account'}
              </Button>
            </Box>

          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
} 