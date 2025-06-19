
'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Clock, 
  Play, 
  Pause, 
  Square, 
  RotateCcw,
  AlertCircle,
  CheckCircle,
  Loader2,
  Zap,
  Brain,
  FileVideo,
  Mic,
  Scissors
} from 'lucide-react';

interface ProcessingJob {
  id: string;
  filename: string;
  type: 'TRANSCRIPTION' | 'HIGHLIGHT_DETECTION' | 'CLIP_GENERATION' | 'SUBTITLE_GENERATION';
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'PAUSED';
  progress: number;
  estimatedTime?: string;
  startedAt?: string;
  completedAt?: string;
  error?: string;
  gpuUsage?: number;
  memoryUsage?: number;
}

const ProcessingQueue = () => {
  const [jobs, setJobs] = useState<ProcessingJob[]>([
    {
      id: '1',
      filename: 'gaming_session_01.mp4',
      type: 'TRANSCRIPTION',
      status: 'RUNNING',
      progress: 75,
      estimatedTime: '2 min',
      startedAt: '2 minutes ago',
      gpuUsage: 85,
      memoryUsage: 12.4
    },
    {
      id: '2',
      filename: 'stream_highlight_reel.mp4',
      type: 'HIGHLIGHT_DETECTION',
      status: 'RUNNING',
      progress: 45,
      estimatedTime: '5 min',
      startedAt: '1 minute ago',
      gpuUsage: 92,
      memoryUsage: 8.7
    },
    {
      id: '3',
      filename: 'reaction_compilation.mp4',
      type: 'CLIP_GENERATION',
      status: 'PENDING',
      progress: 0,
      estimatedTime: '3 min'
    },
    {
      id: '4',
      filename: 'tutorial_video.mp4',
      type: 'SUBTITLE_GENERATION',
      status: 'COMPLETED',
      progress: 100,
      completedAt: '5 minutes ago'
    },
    {
      id: '5',
      filename: 'failed_upload.mp4',
      type: 'TRANSCRIPTION',
      status: 'FAILED',
      progress: 30,
      error: 'Insufficient GPU memory. Please try with a smaller file.'
    }
  ]);

  const [systemStats, setSystemStats] = useState({
    gpuUtilization: 88,
    memoryUsage: 15.2,
    totalMemory: 24,
    queueLength: 3,
    completedToday: 47
  });

  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'TRANSCRIPTION':
        return <Mic className="h-4 w-4" />;
      case 'HIGHLIGHT_DETECTION':
        return <Brain className="h-4 w-4" />;
      case 'CLIP_GENERATION':
        return <Scissors className="h-4 w-4" />;
      case 'SUBTITLE_GENERATION':
        return <FileVideo className="h-4 w-4" />;
      default:
        return <Zap className="h-4 w-4" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'RUNNING':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-400" />;
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'FAILED':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      case 'PAUSED':
        return <Pause className="h-4 w-4 text-yellow-400" />;
      case 'PENDING':
        return <Clock className="h-4 w-4 text-gray-400" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'RUNNING':
        return 'bg-blue-500/20 text-blue-300';
      case 'COMPLETED':
        return 'bg-green-500/20 text-green-300';
      case 'FAILED':
        return 'bg-red-500/20 text-red-300';
      case 'PAUSED':
        return 'bg-yellow-500/20 text-yellow-300';
      case 'PENDING':
        return 'bg-gray-500/20 text-gray-300';
      default:
        return 'bg-gray-500/20 text-gray-300';
    }
  };

  const pauseJob = (jobId: string) => {
    setJobs(prev => prev.map(job => 
      job.id === jobId ? { ...job, status: 'PAUSED' as const } : job
    ));
  };

  const resumeJob = (jobId: string) => {
    setJobs(prev => prev.map(job => 
      job.id === jobId ? { ...job, status: 'RUNNING' as const } : job
    ));
  };

  const retryJob = (jobId: string) => {
    setJobs(prev => prev.map(job => 
      job.id === jobId ? { ...job, status: 'PENDING' as const, progress: 0, error: undefined } : job
    ));
  };

  const cancelJob = (jobId: string) => {
    setJobs(prev => prev.filter(job => job.id !== jobId));
  };

  // Simulate progress updates
  useEffect(() => {
    const interval = setInterval(() => {
      setJobs(prev => prev.map(job => {
        if (job.status === 'RUNNING' && job.progress < 100) {
          const newProgress = Math.min(job.progress + Math.random() * 5, 100);
          return { ...job, progress: newProgress };
        }
        return job;
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* System Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <Card className="glass-effect border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">GPU Usage</p>
                <p className="text-2xl font-bold text-white">{systemStats.gpuUtilization}%</p>
              </div>
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center">
                <Zap className="h-4 w-4 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">VRAM Usage</p>
                <p className="text-2xl font-bold text-white">{systemStats.memoryUsage}GB</p>
              </div>
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                <Brain className="h-4 w-4 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Queue Length</p>
                <p className="text-2xl font-bold text-white">{systemStats.queueLength}</p>
              </div>
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-orange-500 to-red-500 flex items-center justify-center">
                <Clock className="h-4 w-4 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Completed Today</p>
                <p className="text-2xl font-bold text-white">{systemStats.completedToday}</p>
              </div>
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center">
                <CheckCircle className="h-4 w-4 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Processing Queue */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Clock className="h-5 w-5 text-purple-400" />
              Processing Queue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {jobs.map((job, index) => (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all duration-300 ${
                    job.status === 'RUNNING' ? 'processing-glow' : ''
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(job.status)}
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${
                          job.type === 'TRANSCRIPTION' ? 'from-blue-500 to-cyan-500' :
                          job.type === 'HIGHLIGHT_DETECTION' ? 'from-purple-500 to-pink-500' :
                          job.type === 'CLIP_GENERATION' ? 'from-green-500 to-emerald-500' :
                          'from-orange-500 to-red-500'
                        }`}>
                          {getTaskIcon(job.type)}
                        </div>
                      </div>
                      <div>
                        <h3 className="text-white font-medium text-lg">{job.filename}</h3>
                        <p className="text-gray-400 capitalize">
                          {job.type.replace('_', ' ').toLowerCase()}
                        </p>
                        {job.startedAt && (
                          <p className="text-gray-500 text-sm">Started {job.startedAt}</p>
                        )}
                        {job.completedAt && (
                          <p className="text-gray-500 text-sm">Completed {job.completedAt}</p>
                        )}
                        {job.error && (
                          <p className="text-red-400 text-sm mt-1">{job.error}</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(job.status)}>
                        {job.status}
                      </Badge>
                      {job.estimatedTime && job.status !== 'COMPLETED' && job.status !== 'FAILED' && (
                        <Badge variant="outline" className="border-white/20 text-gray-300">
                          {job.estimatedTime}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {job.status !== 'PENDING' && job.status !== 'FAILED' && (
                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Progress</span>
                        <span className="text-white">{Math.round(job.progress)}%</span>
                      </div>
                      <Progress 
                        value={job.progress} 
                        className={`h-2 ${job.status === 'RUNNING' ? 'progress-bar' : ''}`}
                      />
                    </div>
                  )}

                  {job.status === 'RUNNING' && (job.gpuUsage || job.memoryUsage) && (
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      {job.gpuUsage && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-400">GPU Usage</span>
                            <span className="text-white">{job.gpuUsage}%</span>
                          </div>
                          <Progress value={job.gpuUsage} className="h-1" />
                        </div>
                      )}
                      {job.memoryUsage && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-400">Memory</span>
                            <span className="text-white">{job.memoryUsage}GB</span>
                          </div>
                          <Progress value={(job.memoryUsage / 24) * 100} className="h-1" />
                        </div>
                      )}
                    </div>
                  )}

                  <div className="flex items-center gap-2">
                    {job.status === 'RUNNING' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => pauseJob(job.id)}
                        className="border-yellow-500/50 text-yellow-400 hover:bg-yellow-500/20"
                      >
                        <Pause className="h-3 w-3 mr-1" />
                        Pause
                      </Button>
                    )}
                    
                    {job.status === 'PAUSED' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => resumeJob(job.id)}
                        className="border-blue-500/50 text-blue-400 hover:bg-blue-500/20"
                      >
                        <Play className="h-3 w-3 mr-1" />
                        Resume
                      </Button>
                    )}
                    
                    {job.status === 'FAILED' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => retryJob(job.id)}
                        className="border-green-500/50 text-green-400 hover:bg-green-500/20"
                      >
                        <RotateCcw className="h-3 w-3 mr-1" />
                        Retry
                      </Button>
                    )}
                    
                    {(job.status === 'PENDING' || job.status === 'PAUSED' || job.status === 'FAILED') && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => cancelJob(job.id)}
                        className="border-red-500/50 text-red-400 hover:bg-red-500/20"
                      >
                        <Square className="h-3 w-3 mr-1" />
                        Cancel
                      </Button>
                    )}
                  </div>
                </motion.div>
              ))}

              {jobs.length === 0 && (
                <div className="text-center py-12">
                  <Clock className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                  <h3 className="text-xl font-medium text-white mb-2">No Processing Jobs</h3>
                  <p className="text-gray-400">Upload some videos to see them here</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default ProcessingQueue;
