'use client';

import React from 'react';
import { Card, CardBody } from '@heroui/react';
import { BarChart3 } from 'lucide-react';

export const AnalyticsManagement: React.FC = () => {
  return (
    <div className="space-y-6 bg-gray-50 min-h-screen p-6">
      <Card className="bg-white">
        <CardBody className="text-center py-16">
          <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Analytics</h2>
          <p className="text-gray-600">Analytics dashboard will be available soon.</p>
        </CardBody>
      </Card>
    </div>
  );
};

export default AnalyticsManagement; 