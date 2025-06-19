
'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Header from '@/components/header';
import Sidebar from '@/components/sidebar';
import Dashboard from '@/components/dashboard';
import FileUpload from '@/components/file-upload';
import ProcessingQueue from '@/components/processing-queue';
import FileManager from '@/components/file-manager';
import TwitchIntegration from '@/components/twitch-integration';
import CustomPrompts from '@/components/custom-prompts';
import Settings from '@/components/settings';
import StorageMonitor from '@/components/storage-monitor';

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'upload':
        return <FileUpload />;
      case 'processing':
        return <ProcessingQueue />;
      case 'files':
        return <FileManager />;
      case 'twitch':
        return <TwitchIntegration />;
      case 'prompts':
        return <CustomPrompts />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen flex">
      <Sidebar 
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
      />
      
      <div className="flex-1 flex flex-col">
        <Header 
          activeTab={activeTab}
          toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />
        
        <main className="flex-1 p-6 overflow-auto">
          <div className="max-w-7xl mx-auto">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="h-full"
            >
              {renderContent()}
            </motion.div>
          </div>
        </main>
        
        <StorageMonitor />
      </div>
    </div>
  );
}
