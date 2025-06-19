

'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Menu, Zap, Settings, Bell } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import KofiPanel from '@/components/kofi-panel';

interface HeaderProps {
  activeTab: string;
  toggleSidebar: () => void;
}

const Header = ({ activeTab, toggleSidebar }: HeaderProps) => {
  const getTabTitle = (tab: string) => {
    const titles: Record<string, string> = {
      dashboard: 'Dashboard',
      upload: 'Upload Videos',
      processing: 'Processing Queue',
      files: 'File Manager',
      twitch: 'Twitch Integration',
      prompts: 'Custom Prompts',
      settings: 'Settings'
    };
    return titles[tab] || 'ClipMaster';
  };

  return (
    <motion.header 
      className="glass-effect border-b border-white/10 px-6 py-4 sticky top-0 z-40"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="text-white hover:bg-white/10"
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Zap className="h-6 w-6 text-purple-400" />
              <h1 className="text-xl font-bold text-white">ClipMaster</h1>
            </div>
            <div className="h-6 w-px bg-white/20" />
            <h2 className="text-lg text-gray-300">{getTabTitle(activeTab)}</h2>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <KofiPanel 
            username="epickenbee"
            title="Support ClipMaster Development"
            description="Help us continue developing amazing AI-powered video tools for creators like you!"
            className="mr-2"
          />
          
          <Button
            variant="ghost"
            size="sm"
            className="relative text-white hover:bg-white/10"
          >
            <Bell className="h-5 w-5" />
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs"
            >
              3
            </Badge>
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className="text-white hover:bg-white/10"
          >
            <Settings className="h-5 w-5" />
          </Button>

          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
              <span className="text-sm font-bold text-white">AI</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-sm text-gray-300">Online</span>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;

