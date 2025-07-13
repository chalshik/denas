'use client';

import React, { useState } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Switch } from '@heroui/switch';
import { Card, CardBody, CardHeader } from '@heroui/card';
import { Select, SelectItem } from '@heroui/select';

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState({
    siteName: 'Denas',
    siteDescription: 'Modern e-commerce platform',
    emailNotifications: true,
    smsNotifications: false,
    maintenanceMode: false,
    currency: 'USD',
    timezone: 'UTC',
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your application settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* General Settings */}
        <Card className="bg-white">
          <CardHeader className="pb-0 pt-6 px-6">
            <h3 className="text-lg font-semibold">General Settings</h3>
          </CardHeader>
          <CardBody className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Site Name
              </label>
              <Input
                value={settings.siteName}
                onValueChange={(value) => handleSettingChange('siteName', value)}
                placeholder="Enter site name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Site Description
              </label>
              <Input
                value={settings.siteDescription}
                onValueChange={(value) => handleSettingChange('siteDescription', value)}
                placeholder="Enter site description"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Currency
              </label>
              <Select
                selectedKeys={[settings.currency]}
                onSelectionChange={(keys) => {
                  const selected = Array.from(keys)[0] as string;
                  handleSettingChange('currency', selected);
                }}
              >
                <SelectItem key="USD">USD ($)</SelectItem>
                <SelectItem key="EUR">EUR (€)</SelectItem>
                <SelectItem key="GBP">GBP (£)</SelectItem>
                <SelectItem key="RUB">RUB (₽)</SelectItem>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timezone
              </label>
              <Select
                selectedKeys={[settings.timezone]}
                onSelectionChange={(keys) => {
                  const selected = Array.from(keys)[0] as string;
                  handleSettingChange('timezone', selected);
                }}
              >
                <SelectItem key="UTC">UTC</SelectItem>
                <SelectItem key="EST">EST</SelectItem>
                <SelectItem key="PST">PST</SelectItem>
                <SelectItem key="GMT">GMT</SelectItem>
              </Select>
            </div>
          </CardBody>
        </Card>

        {/* Notification Settings */}
        <Card className="bg-white">
          <CardHeader className="pb-0 pt-6 px-6">
            <h3 className="text-lg font-semibold">Notification Settings</h3>
          </CardHeader>
          <CardBody className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-700">Email Notifications</p>
                <p className="text-xs text-gray-500">Receive notifications via email</p>
              </div>
              <Switch
                isSelected={settings.emailNotifications}
                onValueChange={(value) => handleSettingChange('emailNotifications', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-700">SMS Notifications</p>
                <p className="text-xs text-gray-500">Receive notifications via SMS</p>
              </div>
              <Switch
                isSelected={settings.smsNotifications}
                onValueChange={(value) => handleSettingChange('smsNotifications', value)}
              />
            </div>
          </CardBody>
        </Card>

        {/* System Settings */}
        <Card className="bg-white">
          <CardHeader className="pb-0 pt-6 px-6">
            <h3 className="text-lg font-semibold">System Settings</h3>
          </CardHeader>
          <CardBody className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-700">Maintenance Mode</p>
                <p className="text-xs text-gray-500">Put the site in maintenance mode</p>
              </div>
              <Switch
                isSelected={settings.maintenanceMode}
                onValueChange={(value) => handleSettingChange('maintenanceMode', value)}
                color="warning"
              />
            </div>
          </CardBody>
        </Card>

        {/* Actions */}
        <Card className="bg-white">
          <CardHeader className="pb-0 pt-6 px-6">
            <h3 className="text-lg font-semibold">Actions</h3>
          </CardHeader>
          <CardBody className="p-6 space-y-4">
            <Button color="primary" className="w-full">
              Save Settings
            </Button>
            <Button variant="bordered" color="danger" className="w-full">
              Reset to Defaults
            </Button>
            <Button variant="bordered" className="w-full">
              Export Settings
            </Button>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
