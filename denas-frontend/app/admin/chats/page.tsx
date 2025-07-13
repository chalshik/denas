'use client';

import React, { useState } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Avatar } from '@heroui/avatar';

// Mock data for demonstration
const mockChats = [
  { 
    id: 1, 
    customer: 'John Doe', 
    email: 'john@example.com',
    lastMessage: 'I have a question about my order',
    status: 'Active',
    unread: 2,
    lastActivity: '2 minutes ago'
  },
  { 
    id: 2, 
    customer: 'Jane Smith', 
    email: 'jane@example.com',
    lastMessage: 'Thank you for your help!',
    status: 'Resolved',
    unread: 0,
    lastActivity: '1 hour ago'
  },
  { 
    id: 3, 
    customer: 'Mike Johnson', 
    email: 'mike@example.com',
    lastMessage: 'When will my order arrive?',
    status: 'Active',
    unread: 1,
    lastActivity: '30 minutes ago'
  },
];

export default function AdminChatsPage() {
  const [chats, setChats] = useState(mockChats);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredChats = chats.filter(chat =>
    chat.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
    chat.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Customer Support</h1>
          <p className="text-gray-600 mt-2">Manage customer conversations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="bordered">
            Export Chats
          </Button>
          <Button color="primary">
            New Chat
          </Button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <Input
            placeholder="Search chats..."
            value={searchTerm}
            onValueChange={setSearchTerm}
            className="max-w-md"
          />
        </div>

        <div className="divide-y">
          {filteredChats.map((chat) => (
            <div key={chat.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Avatar
                    name={chat.customer}
                    className="flex-shrink-0"
                  />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {chat.customer}
                    </h3>
                    <p className="text-sm text-gray-600">{chat.email}</p>
                    <p className="text-sm text-gray-500 mt-1">{chat.lastMessage}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      chat.status === 'Active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {chat.status}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">{chat.lastActivity}</p>
                  </div>
                  
                  {chat.unread > 0 && (
                    <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                      {chat.unread}
                    </span>
                  )}
                  
                  <Button size="sm" variant="bordered">
                    Open Chat
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
