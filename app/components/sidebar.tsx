
'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  LayoutDashboard, 
  Upload, 
  Cog, 
  FileVideo, 
  Twitch, 
  MessageSquare, 
  Settings,
  Zap,
  X
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const Sidebar = ({ activeTab, setActiveTab, isOpen, setIsOpen }: SidebarProps) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'upload', label: 'Upload', icon: Upload, badge: null },
    { id: 'processing', label: 'Processing', icon: Cog, badge: '2' },
    { id: 'files', label: 'Files', icon: FileVideo, badge: null },
    { id: 'twitch', label: 'Twitch', icon: Twitch, badge: null },
    { id: 'prompts', label: 'Prompts', icon: MessageSquare, badge: '8' },
    { id: 'settings', label: 'Settings', icon: Settings, badge: null },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Mobile overlay */}
          <motion.div
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
          />
          
          <motion.aside
            className="fixed lg:static left-0 top-0 h-full w-64 glass-effect border-r border-white/10 z-50 lg:z-auto"
            initial={{ x: -256 }}
            animate={{ x: 0 }}
            exit={{ x: -256 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
                    <Zap className="h-5 w-5 text-white" />
                  </div>
                  <span className="font-bold text-lg text-white">ClipMaster</span>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  className="lg:hidden text-white hover:bg-white/10"
                  onClick={() => setIsOpen(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <nav className="space-y-2">
                {menuItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  
                  return (
                    <motion.div
                      key={item.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Button
                        variant={isActive ? "secondary" : "ghost"}
                        className={`w-full justify-between text-left h-12 ${
                          isActive 
                            ? "bg-purple-500/20 text-purple-300 border border-purple-500/30" 
                            : "text-gray-300 hover:bg-white/10 hover:text-white"
                        }`}
                        onClick={() => {
                          setActiveTab(item.id);
                          setIsOpen(false); // Close sidebar on mobile
                        }}
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="h-5 w-5" />
                          <span>{item.label}</span>
                        </div>
                        {item.badge && (
                          <Badge 
                            variant={isActive ? "default" : "secondary"}
                            className="ml-auto"
                          >
                            {item.badge}
                          </Badge>
                        )}
                      </Button>
                    </motion.div>
                  );
                })}
              </nav>

              <div className="mt-8 p-4 rounded-xl bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
                  <span className="text-sm font-medium text-white">AI Status</span>
                </div>
                <p className="text-xs text-gray-300">
                  Processing engine online
                </p>
                <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full w-3/4 bg-gradient-to-r from-green-400 to-blue-400 rounded-full" />
                </div>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
};

export default Sidebar;
