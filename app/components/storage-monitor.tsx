
'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  HardDrive, 
  AlertTriangle, 
  CheckCircle,
  X,
  Settings,
  Trash2
} from 'lucide-react';

const StorageMonitor = () => {
  const [storageInfo, setStorageInfo] = useState({
    totalSpace: 1000, // GB
    usedSpace: 680, // GB
    availableSpace: 320, // GB
    videoCount: 47,
    clipCount: 189,
    usagePercentage: 68
  });

  const [isExpanded, setIsExpanded] = useState(false);
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    // Show alert if usage is over 80%
    if (storageInfo.usagePercentage > 80) {
      setShowAlert(true);
    }
  }, [storageInfo.usagePercentage]);

  const formatSize = (gb: number) => {
    if (gb >= 1000) {
      return `${(gb / 1000).toFixed(1)} TB`;
    }
    return `${gb} GB`;
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'from-red-500 to-red-600';
    if (percentage >= 80) return 'from-yellow-500 to-orange-500';
    if (percentage >= 60) return 'from-blue-500 to-purple-500';
    return 'from-green-500 to-blue-500';
  };

  const getStatusIcon = (percentage: number) => {
    if (percentage >= 90) {
      return <AlertTriangle className="h-4 w-4 text-red-400" />;
    }
    return <CheckCircle className="h-4 w-4 text-green-400" />;
  };

  return (
    <>
      {/* Alert Banner */}
      <AnimatePresence>
        {showAlert && storageInfo.usagePercentage > 80 && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-4 right-4 z-50"
          >
            <Card className="glass-effect border-orange-500/50 bg-orange-500/10 max-w-sm">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-orange-400 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="text-white font-medium mb-1">Storage Warning</h4>
                    <p className="text-gray-300 text-sm mb-3">
                      Storage is {storageInfo.usagePercentage}% full. Consider cleaning up old files.
                    </p>
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        className="border-orange-500/50 text-orange-400 hover:bg-orange-500/20"
                      >
                        <Trash2 className="h-3 w-3 mr-1" />
                        Clean Up
                      </Button>
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={() => setShowAlert(false)}
                        className="text-gray-400 hover:bg-white/10"
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowAlert(false)}
                    className="text-gray-400 hover:text-white hover:bg-white/10 p-1"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Storage Monitor Bar */}
      <motion.div
        className="fixed bottom-0 left-0 right-0 z-40"
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ delay: 1 }}
      >
        <div className="glass-effect border-t border-white/10 p-3">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="text-white hover:bg-white/10"
                >
                  <HardDrive className="h-4 w-4 mr-2" />
                  Storage
                </Button>
                
                <div className="flex items-center gap-2">
                  {getStatusIcon(storageInfo.usagePercentage)}
                  <span className="text-white text-sm font-medium">
                    {formatSize(storageInfo.usedSpace)} / {formatSize(storageInfo.totalSpace)}
                  </span>
                  <Badge 
                    variant="secondary"
                    className={storageInfo.usagePercentage > 80 ? 'bg-orange-500/20 text-orange-300' : 'bg-green-500/20 text-green-300'}
                  >
                    {storageInfo.usagePercentage}%
                  </Badge>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="hidden md:flex items-center gap-6 text-sm text-gray-300">
                  <span>{storageInfo.videoCount} Videos</span>
                  <span>{storageInfo.clipCount} Clips</span>
                  <span>{formatSize(storageInfo.availableSpace)} Free</span>
                </div>
                
                <div className="w-32 hidden sm:block">
                  <Progress 
                    value={storageInfo.usagePercentage} 
                    className="h-2"
                  />
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  className="text-gray-400 hover:text-white hover:bg-white/10"
                >
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Expanded Storage Details */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="mt-4 overflow-hidden"
                >
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="glass-effect border-white/10">
                      <CardContent className="p-4">
                        <div className="text-center">
                          <div className="relative w-20 h-20 mx-auto mb-3">
                            <svg className="w-20 h-20 transform -rotate-90">
                              <circle
                                cx="40"
                                cy="40"
                                r="30"
                                stroke="currentColor"
                                strokeWidth="6"
                                fill="transparent"
                                className="text-gray-700"
                              />
                              <circle
                                cx="40"
                                cy="40"
                                r="30"
                                stroke="currentColor"
                                strokeWidth="6"
                                fill="transparent"
                                strokeDasharray={`${2 * Math.PI * 30}`}
                                strokeDashoffset={`${2 * Math.PI * 30 * (1 - storageInfo.usagePercentage / 100)}`}
                                className={`text-gradient bg-gradient-to-r ${getUsageColor(storageInfo.usagePercentage)}`}
                                strokeLinecap="round"
                              />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="text-lg font-bold text-white">{storageInfo.usagePercentage}%</span>
                            </div>
                          </div>
                          <h3 className="text-white font-medium">Usage Overview</h3>
                          <p className="text-gray-400 text-sm">
                            {formatSize(storageInfo.usedSpace)} used of {formatSize(storageInfo.totalSpace)}
                          </p>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="glass-effect border-white/10">
                      <CardContent className="p-4">
                        <h3 className="text-white font-medium mb-3">File Breakdown</h3>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Videos</span>
                            <span className="text-white">{storageInfo.videoCount}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Generated Clips</span>
                            <span className="text-white">{storageInfo.clipCount}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Avg. File Size</span>
                            <span className="text-white">
                              {formatSize(Math.round(storageInfo.usedSpace / (storageInfo.videoCount + storageInfo.clipCount)))}
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="glass-effect border-white/10">
                      <CardContent className="p-4">
                        <h3 className="text-white font-medium mb-3">Storage Management</h3>
                        <div className="space-y-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="w-full border-white/20 text-white hover:bg-white/10"
                          >
                            <Trash2 className="h-3 w-3 mr-2" />
                            Auto-cleanup Settings
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="w-full border-red-500/50 text-red-400 hover:bg-red-500/20"
                          >
                            Clean Old Files
                          </Button>
                          <p className="text-xs text-gray-500 mt-2">
                            Auto-cleanup: 30 days old files
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </>
  );
};

export default StorageMonitor;
