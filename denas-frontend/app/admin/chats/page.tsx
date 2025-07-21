"use client";

import React, { useState } from "react";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";

export default function AdminChatsPage() {
  const [chats, setChats] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  const filteredChats = chats.filter(
    (chat) =>
      chat.customer?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      chat.email?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Customer Support</h1>
          <p className="text-gray-600 mt-2">Manage customer conversations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="bordered">Export Chats</Button>
          <Button color="primary">New Chat</Button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <Input
            className="max-w-md"
            placeholder="Search chats..."
            value={searchTerm}
            onValueChange={setSearchTerm}
          />
        </div>

        <div className="divide-y">{/* Здесь будут реальные чаты */}</div>
      </div>
    </div>
  );
}
