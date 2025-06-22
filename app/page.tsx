'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  User, 
  Settings, 
  Calendar, 
  MessageSquare, 
  Plus,
  Save,
  Trash2,
  Power,
  Clock,
  MapPin,
  PoundSterling
} from 'lucide-react';

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

export default function BobDashboard() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'account' | 'agent'>('dashboard');
  const [account, setAccount] = useState<BobAccount>({
    name: '',
    role: '',
    roleDescription: '',
    profile: '',
    servicesType: 'pricing',
    services: [{ name: '', price: undefined }],
    servicesNotProvided: '',
    location: ''
  });
  
  const [agentSettings, setAgentSettings] = useState<AgentSettings>({
    enabled: true,
    delayTime: 5,
    defaultGreeting: ''
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Load settings on component mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const [accountResponse, agentResponse] = await Promise.all([
        fetch('/api/bob-settings?type=account'),
        fetch('/api/bob-settings?type=agent')
      ]);

      if (accountResponse.ok) {
        const accountData = await accountResponse.json();
        if (accountData.account) {
          setAccount(accountData.account);
        }
      }

      if (agentResponse.ok) {
        const agentData = await agentResponse.json();
        setAgentSettings(agentData.agentSettings);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const addService = () => {
    setAccount(prev => ({
      ...prev,
      services: [...prev.services, { name: '', price: undefined }]
    }));
  };

  const removeService = (index: number) => {
    setAccount(prev => ({
      ...prev,
      services: prev.services.filter((_, i) => i !== index)
    }));
  };

  const updateService = (index: number, field: 'name' | 'price', value: string | number) => {
    setAccount(prev => ({
      ...prev,
      services: prev.services.map((service, i) => 
        i === index ? { ...service, [field]: value } : service
      )
    }));
  };

  const saveAccount = async () => {
    setLoading(true);
    setMessage('');

    try {
      // Validate required fields
      if (!account.name || !account.profile || !account.location) {
        setMessage('Please fill in all required fields (name, profile, location)');
        return;
      }
      
      if (account.servicesType !== 'none' && account.services.some(s => !s.name)) {
        setMessage('Please fill in all service names');
        return;
      }

      const response = await fetch('/api/bob-settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'account',
          data: account
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setMessage('Account details saved successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage(result.error || 'Failed to save account details');
      }
    } catch (error) {
      setMessage('Error saving account details');
    } finally {
      setLoading(false);
    }
  };

  const clearAccount = () => {
    setAccount({
      name: '',
      role: '',
      roleDescription: '',
      profile: '',
      servicesType: 'pricing',
      services: [{ name: '', price: undefined }],
      servicesNotProvided: '',
      location: ''
    });
    setMessage('');
  };

  const saveAgentSettings = async () => {
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/bob-settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'agent',
          data: agentSettings
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setMessage('Agent settings saved successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage(result.error || 'Failed to save agent settings');
      }
    } catch (error) {
      setMessage('Error saving agent settings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-green-50 to-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🐝 Bob's Beehive Dashboard
          </h1>
          <p className="text-gray-600">Manage your beehive consultation business</p>
        </div>

        {/* Message Display */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.includes('successfully') 
              ? 'bg-green-100 text-green-800 border border-green-200' 
              : 'bg-red-100 text-red-800 border border-red-200'
          }`}>
            {message}
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-2 bg-white rounded-lg p-2 shadow-md">
            <Button
              variant={activeTab === 'dashboard' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('dashboard')}
              className="flex items-center space-x-2"
            >
              <User className="w-4 h-4" />
              <span>Dashboard</span>
            </Button>
            <Button
              variant={activeTab === 'account' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('account')}
              className="flex items-center space-x-2"
            >
              <Settings className="w-4 h-4" />
              <span>Account Settings</span>
            </Button>
            <Button
              variant={activeTab === 'agent' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('agent')}
              className="flex items-center space-x-2"
            >
              <Power className="w-4 h-4" />
              <span>Agent Settings</span>
            </Button>
          </div>
        </div>

        {/* Dashboard View */}
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="text-center">
                <User className="w-12 h-12 mx-auto text-blue-600 mb-2" />
                <CardTitle>Account Settings</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <p className="text-gray-600 mb-4">Manage your profile and services</p>
                <Button onClick={() => setActiveTab('account')} className="w-full">
                  Configure
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="text-center">
                <Power className="w-12 h-12 mx-auto text-green-600 mb-2" />
                <CardTitle>Agent Settings</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <div className="flex items-center justify-center mb-4">
                  <Badge variant={agentSettings.enabled ? 'default' : 'secondary'}>
                    {agentSettings.enabled ? 'ON' : 'OFF'}
                  </Badge>
                </div>
                <Button onClick={() => setActiveTab('agent')} className="w-full">
                  Configure
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="text-center">
                <Calendar className="w-12 h-12 mx-auto text-blue-500 mb-2" />
                <CardTitle>Calendar</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <p className="text-gray-600 mb-4">View and manage appointments</p>
                <Button variant="outline" className="w-full" disabled>
                  Coming Soon
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="text-center">
                <MessageSquare className="w-12 h-12 mx-auto text-green-500 mb-2" />
                <CardTitle>WhatsApp Messages</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <p className="text-gray-600 mb-4">View conversation history</p>
                <Button variant="outline" className="w-full" disabled>
                  Coming Soon
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Account Settings View */}
        {activeTab === 'account' && (
          <div className="max-w-4xl mx-auto">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="w-6 h-6" />
                  <span>Account Details</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      value={account.name}
                      onChange={(e) => setAccount(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Bob Smith"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Role
                    </label>
                    <input
                      type="text"
                      value={account.role}
                      onChange={(e) => setAccount(prev => ({ ...prev, role: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Beehive Builder & Consultant"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role Description (Optional)
                  </label>
                  <textarea
                    value={account.roleDescription}
                    onChange={(e) => setAccount(prev => ({ ...prev, roleDescription: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={2}
                    placeholder="Brief description of your role..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Profile *
                  </label>
                  <textarea
                    value={account.profile}
                    onChange={(e) => setAccount(prev => ({ ...prev, profile: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    placeholder="Tell clients about yourself, your experience, and what makes you unique..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location (UK Postcode) *
                  </label>
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={account.location}
                      onChange={(e) => setAccount(prev => ({ ...prev, location: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="SW1A 1AA"
                    />
                  </div>
                </div>

                {/* Services Section */}
                <div className="border-t pt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Services Configuration</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Services Type *
                      </label>
                      <div className="space-y-2">
                        <label className="flex items-center">
                          <input
                            type="radio"
                            name="servicesType"
                            value="pricing"
                            checked={account.servicesType === 'pricing'}
                            onChange={(e) => setAccount(prev => ({ 
                              ...prev, 
                              servicesType: e.target.value as 'pricing',
                              services: [{ name: '', price: undefined }]
                            }))}
                            className="mr-2"
                          />
                          Services and Pricing List
                        </label>
                        <label className="flex items-center">
                          <input
                            type="radio"
                            name="servicesType"
                            value="list"
                            checked={account.servicesType === 'list'}
                            onChange={(e) => setAccount(prev => ({ 
                              ...prev, 
                              servicesType: e.target.value as 'list',
                              services: [{ name: '', price: undefined }]
                            }))}
                            className="mr-2"
                          />
                          Services List (No Pricing)
                        </label>
                        <label className="flex items-center">
                          <input
                            type="radio"
                            name="servicesType"
                            value="none"
                            checked={account.servicesType === 'none'}
                            onChange={(e) => setAccount(prev => ({ 
                              ...prev, 
                              servicesType: e.target.value as 'none',
                              services: []
                            }))}
                            className="mr-2"
                          />
                          Services Discussed/None
                        </label>
                      </div>
                    </div>

                    {(account.servicesType === 'pricing' || account.servicesType === 'list') && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="block text-sm font-medium text-gray-700">
                            Services *
                          </label>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={addService}
                            className="flex items-center space-x-1"
                          >
                            <Plus className="w-4 h-4" />
                            <span>Add Service</span>
                          </Button>
                        </div>
                        
                        <div className="space-y-3">
                          {account.services.map((service, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <input
                                type="text"
                                value={service.name}
                                onChange={(e) => updateService(index, 'name', e.target.value)}
                                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Service name"
                              />
                              {account.servicesType === 'pricing' && (
                                <div className="flex items-center space-x-1">
                                  <PoundSterling className="w-4 h-4 text-gray-400" />
                                  <input
                                    type="number"
                                    value={service.price || ''}
                                    onChange={(e) => updateService(index, 'price', parseFloat(e.target.value) || 0)}
                                    className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="0"
                                  />
                                </div>
                              )}
                              {account.services.length > 1 && (
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  onClick={() => removeService(index)}
                                  className="text-red-600 hover:text-red-700"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Services NOT Provided (Optional)
                      </label>
                      <textarea
                        value={account.servicesNotProvided}
                        onChange={(e) => setAccount(prev => ({ ...prev, servicesNotProvided: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={2}
                        placeholder="Enter services you don't provide, separated by commas..."
                      />
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-4 pt-6 border-t">
                  <Button 
                    onClick={saveAccount} 
                    disabled={loading}
                    className="flex items-center space-x-2"
                  >
                    <Save className="w-4 h-4" />
                    <span>{loading ? 'Saving...' : 'Save Account'}</span>
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={clearAccount} 
                    className="flex items-center space-x-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Clear All</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Agent Settings View */}
        {activeTab === 'agent' && (
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Power className="w-6 h-6" />
                  <span>Agent Settings</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Agent Status
                    </label>
                    <p className="text-sm text-gray-500">
                      Enable or disable the WhatsApp agent
                    </p>
                  </div>
                  <Button
                    variant={agentSettings.enabled ? 'default' : 'outline'}
                    onClick={() => setAgentSettings(prev => ({ ...prev, enabled: !prev.enabled }))}
                    className="flex items-center space-x-2"
                  >
                    <Power className="w-4 h-4" />
                    <span>{agentSettings.enabled ? 'Enabled' : 'Disabled'}</span>
                  </Button>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message Processing Delay (seconds)
                  </label>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <input
                      type="number"
                      min="1"
                      max="30"
                      value={agentSettings.delayTime}
                      onChange={(e) => setAgentSettings(prev => ({ 
                        ...prev, 
                        delayTime: parseInt(e.target.value) || 5 
                      }))}
                      className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-500">seconds</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    Time to buffer user messages before processing
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Greeting Message (Optional)
                  </label>
                  <textarea
                    value={agentSettings.defaultGreeting}
                    onChange={(e) => setAgentSettings(prev => ({ ...prev, defaultGreeting: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Default message to send when agent is enabled..."
                  />
                </div>

                <div className="pt-6 border-t">
                  <Button 
                    onClick={saveAgentSettings} 
                    disabled={loading}
                    className="flex items-center space-x-2"
                  >
                    <Save className="w-4 h-4" />
                    <span>{loading ? 'Saving...' : 'Save Settings'}</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
