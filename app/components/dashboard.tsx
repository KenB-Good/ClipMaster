
'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  Video, 
  Scissors, 
  Clock, 
  TrendingUp, 
  Zap,
  Play,
  Download,
  Eye,
  BarChart3
} from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalVideos: 0,
    totalClips: 0,
    processingQueue: 0,
    storageUsed: 0
  });

  const recentActivity = [
    {
      id: '1',
      type: 'clip_generated',
      title: 'Epic Gaming Moment #1',
      timestamp: '2 minutes ago',
      status: 'completed'
    },
    {
      id: '2',
      type: 'video_uploaded',
      title: 'Stream_2024_01_15.mp4',
      timestamp: '5 minutes ago',
      status: 'processing'
    },
    {
      id: '3',
      type: 'highlight_detected',
      title: 'Reaction Highlights Found',
      timestamp: '8 minutes ago',
      status: 'completed'
    }
  ];

  const processingQueue = [
    {
      id: '1',
      filename: 'gaming_session_01.mp4',
      progress: 75,
      task: 'Highlight Detection',
      estimatedTime: '2 min'
    },
    {
      id: '2',
      filename: 'stream_vod_latest.mp4',
      progress: 45,
      task: 'Transcription',
      estimatedTime: '5 min'
    }
  ];

  const topClips = [
    {
      id: '1',
      title: 'Amazing Comeback',
      duration: '00:15',
      views: 1250,
      thumbnail: 'https://i.ytimg.com/vi/VwbdhG6Vwbk/maxresdefault.jpg'
    },
    {
      id: '2',
      title: 'Funny Reaction',
      duration: '00:12',
      views: 890,
      thumbnail: 'https://i.ytimg.com/vi/unk3mp-NIdw/maxresdefault.jpg'
    },
    {
      id: '3',
      title: 'Clutch Moment',
      duration: '00:18',
      views: 645,
      thumbnail: 'https://i.ytimg.com/vi/UHqhllNQXCQ/maxresdefault.jpg'
    }
  ];

  useEffect(() => {
    // Simulate counting animation
    const interval = setInterval(() => {
      setStats(prev => ({
        totalVideos: Math.min(prev.totalVideos + 1, 47),
        totalClips: Math.min(prev.totalClips + 2, 189),
        processingQueue: Math.min(prev.processingQueue + 1, 3),
        storageUsed: Math.min(prev.storageUsed + 1, 68)
      }));
    }, 50);

    setTimeout(() => clearInterval(interval), 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-effect rounded-2xl p-8 border border-white/10"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Welcome to ClipMaster
            </h1>
            <p className="text-gray-300 text-lg">
              AI-powered video clipping at your fingertips. Create viral moments effortlessly.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white">
              <Upload className="h-4 w-4 mr-2" />
              Upload Video
            </Button>
            <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
              <Zap className="h-4 w-4 mr-2" />
              Connect Twitch
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { title: 'Total Videos', value: stats.totalVideos, icon: Video, color: 'from-blue-500 to-cyan-500' },
          { title: 'Generated Clips', value: stats.totalClips, icon: Scissors, color: 'from-purple-500 to-pink-500' },
          { title: 'Processing Queue', value: stats.processingQueue, icon: Clock, color: 'from-orange-500 to-red-500' },
          { title: 'Storage Used', value: `${stats.storageUsed}%`, icon: BarChart3, color: 'from-green-500 to-emerald-500' }
        ].map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="glass-effect border-white/10 hover:bg-white/5 transition-all duration-300 hover:scale-105">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">{stat.title}</p>
                    <p className="text-2xl font-bold text-white mt-1">
                      {typeof stat.value === 'number' && stat.title !== 'Storage Used' 
                        ? stat.value.toLocaleString() 
                        : stat.value
                      }
                    </p>
                  </div>
                  <div className={`h-12 w-12 rounded-xl bg-gradient-to-r ${stat.color} flex items-center justify-center`}>
                    <stat.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Processing Queue */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="glass-effect border-white/10 h-full">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Clock className="h-5 w-5 text-purple-400" />
                Processing Queue
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {processingQueue.map((item) => (
                <div key={item.id} className="p-4 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="text-white font-medium">{item.filename}</h4>
                      <p className="text-gray-400 text-sm">{item.task}</p>
                    </div>
                    <Badge variant="secondary" className="bg-purple-500/20 text-purple-300">
                      {item.estimatedTime}
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Progress</span>
                      <span className="text-white">{item.progress}%</span>
                    </div>
                    <Progress value={item.progress} className="h-2" />
                  </div>
                </div>
              ))}
              {processingQueue.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No items in queue</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="glass-effect border-white/10 h-full">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-400" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="p-4 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`h-2 w-2 rounded-full ${
                        activity.status === 'completed' ? 'bg-green-400' : 'bg-yellow-400'
                      }`} />
                      <div>
                        <h4 className="text-white font-medium">{activity.title}</h4>
                        <p className="text-gray-400 text-sm">{activity.timestamp}</p>
                      </div>
                    </div>
                    <Badge 
                      variant={activity.status === 'completed' ? 'default' : 'secondary'}
                      className={activity.status === 'completed' ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'}
                    >
                      {activity.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Top Clips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Scissors className="h-5 w-5 text-blue-400" />
              Top Performing Clips
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {topClips.map((clip, index) => (
                <motion.div
                  key={clip.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 * index }}
                  className="group"
                >
                  <div className="clip-card">
                    <div className="relative mb-4">
                      <div className="aspect-video bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg overflow-hidden">
                        <img 
                          src={clip.thumbnail}
                          alt={clip.title}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300">
                          <Button size="sm" className="bg-white/20 hover:bg-white/30">
                            <Play className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <Badge className="absolute top-2 right-2 bg-black/60 text-white">
                        {clip.duration}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-white font-medium">{clip.title}</h3>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-gray-400 text-sm">
                          <Eye className="h-4 w-4" />
                          <span>{clip.views.toLocaleString()} views</span>
                        </div>
                        <Button size="sm" variant="ghost" className="text-gray-400 hover:text-white">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Dashboard;
