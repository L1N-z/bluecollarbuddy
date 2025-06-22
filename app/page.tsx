'use client';

import Link from 'next/link';
import { Calendar, User, Power, MessageSquare } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button, Card, CardContent, CardActionArea, Typography } from '@mui/material';

export default function HomeDashboard() {
  const navItems = [
    {
      href: '/calendar',
      icon: <Calendar className="w-12 h-12 text-blue-500" />,
      title: 'Calendar',
      description: 'View and manage your appointments.',
      bgColor: 'bg-blue-50',
      hoverColor: 'hover:bg-blue-100',
    },
    {
      href: '/account',
      icon: <User className="w-12 h-12 text-green-500" />,
      title: 'Account Settings',
      description: 'Manage your profile and services.',
      bgColor: 'bg-green-50',
      hoverColor: 'hover:bg-green-100',
    },
    {
      href: '/agent-settings',
      icon: <Power className="w-12 h-12 text-blue-500" />,
      title: 'Agent Settings',
      description: 'Configure your WhatsApp agent.',
      bgColor: 'bg-blue-50',
      hoverColor: 'hover:bg-blue-100',
    },
    {
      href: '/messages',
      icon: <MessageSquare className="w-12 h-12 text-green-500" />,
      title: 'WhatsApp Messages',
      description: 'View your conversation history.',
      bgColor: 'bg-green-50',
      hoverColor: 'hover:bg-green-100',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white p-4 mx-[10%]">
      <div className="text-center mb-12 w-full">
        <Typography variant="h2" component="h1" className="font-bold text-gray-800 mb-3 flex items-center justify-center gap-4">
          <span>🐝</span>
          <span>BizzyBuddy</span>
        </Typography>
        <Typography variant="h6" component="p" className="text-gray-600">
          Your central hub for managing your business.
        </Typography>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 w-full max-w-6xl">
        {navItems.map((item, index) => (
          <motion.div
            key={item.href}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            className="flex justify-center"
          >
            <Card
              className={`w-72 h-80 shadow-lg hover:shadow-2xl transition-shadow duration-300 ${item.bgColor}`}
              sx={{ '&:hover': { backgroundColor: 'inherit' } }}
            >
              <Link href={item.href} passHref legacyBehavior>
                <CardActionArea className="flex flex-col justify-start items-center h-full p-6 text-center">
                  <div className="mb-4">{item.icon}</div>
                  <Typography variant="h5" component="h2" className="text-2xl font-semibold text-gray-700 mb-2">
                    {item.title}
                  </Typography>
                  <Typography variant="body2" className="text-gray-600 flex-grow">
                    {item.description}
                  </Typography>
                  <Button variant="contained" className="w-full mt-4 bg-blue-600 hover:bg-blue-700">
                    Go to {item.title}
                  </Button>
                </CardActionArea>
              </Link>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
