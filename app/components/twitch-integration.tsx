
'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Twitch, 
  Link, 
  Unlink, 
  Radio, 
  MessageSquare, 
  Download,
  Eye,
  Users,
  Clock,
  Play,
  Settings,
  AlertCircle,
  CheckCircle,
  Zap
} from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface TwitchConnection {
  isConnected: boolean;
  username: string;
  userId: string;
  profileImage: string;
  followerCount: number;
  connectedAt: string;
}

interface StreamInfo {
  isLive: boolean;
  title: string;
  game: string;
  viewerCount: number;
  duration: string;
  thumbnail: string;
}

interface StreamCapture {
  id: string;
  title: string;
  game: string;
  duration: string;
  capturedAt: string;
  status: 'CAPTURING' | 'COMPLETED' | 'PROCESSING';
  progress: number;
  fileSize: number;
}

const TwitchIntegration = () => {
  const [connection, setConnection] = useState<TwitchConnection>({
    isConnected: false,
    username: '',
    userId: '',
    profileImage: '',
    followerCount: 0,
    connectedAt: ''
  });

  const [streamInfo, setStreamInfo] = useState<StreamInfo>({
    isLive: false,
    title: '',
    game: '',
    viewerCount: 0,
    duration: '',
    thumbnail: ''
  });

  const [settings, setSettings] = useState({
    autoCapture: false,
    chatMonitoring: true,
    highlightDetection: true,
    clipFormat: 'HORIZONTAL' as const,
    minClipDuration: 10,
    maxClipDuration: 60,
    qualityPreset: 'source'
  });

  const [captures, setCaptures] = useState<StreamCapture[]>([
    {
      id: '1',
      title: 'Epic Gaming Session - Victory Royale',
      game: 'Fortnite',
      duration: '2:34:15',
      capturedAt: '2024-01-15T10:30:00Z',
      status: 'COMPLETED',
      progress: 100,
      fileSize: 2400000000
    },
    {
      id: '2',
      title: 'Chill Stream - Just Chatting',
      game: 'Just Chatting',
      duration: '1:45:30',
      capturedAt: '2024-01-14T15:45:00Z',
      status: 'PROCESSING',
      progress: 65,
      fileSize: 1800000000
    },
    {
      id: '3',
      title: 'Live Stream Capture',
      game: 'Valorant',
      duration: '0:23:45',
      capturedAt: '2024-01-15T18:30:00Z',
      status: 'CAPTURING',
      progress: 45,
      fileSize: 450000000
    }
  ]);

  const [isConnecting, setIsConnecting] = useState(false);

  const connectToTwitch = async () => {
    setIsConnecting(true);
    
    // Simulate OAuth flow
    setTimeout(() => {
      setConnection({
        isConnected: true,
        username: 'EpicGamer2024',
        userId: 'twitch_user_12345',
        profileImage: 'https://i.pinimg.com/originals/b0/c8/b5/b0c8b5763c6bb85a82ea9f9e90b877ad.gif',
        followerCount: 15420,
        connectedAt: new Date().toISOString()
      });
      
      setStreamInfo({
        isLive: true,
        title: 'Epic Gaming Session - Victory Royale Hunt!',
        game: 'Fortnite',
        viewerCount: 1247,
        duration: '2:34:15',
        thumbnail: 'https://i.ytimg.com/vi/304xBN1gXhE/maxresdefault.jpg'
      });
      
      setIsConnecting(false);
      
      toast({
        title: "Twitch Connected",
        description: "Successfully connected to your Twitch account.",
      });
    }, 2000);
  };

  const disconnectFromTwitch = () => {
    setConnection({
      isConnected: false,
      username: '',
      userId: '',
      profileImage: '',
      followerCount: 0,
      connectedAt: ''
    });
    
    setStreamInfo({
      isLive: false,
      title: '',
      game: '',
      viewerCount: 0,
      duration: '',
      thumbnail: ''
    });
    
    toast({
      title: "Twitch Disconnected",
      description: "Successfully disconnected from Twitch.",
    });
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-500/20 text-green-300';
      case 'PROCESSING':
        return 'bg-blue-500/20 text-blue-300';
      case 'CAPTURING':
        return 'bg-purple-500/20 text-purple-300';
      default:
        return 'bg-gray-500/20 text-gray-300';
    }
  };

  // Simulate live updates
  useEffect(() => {
    if (connection.isConnected && streamInfo.isLive) {
      const interval = setInterval(() => {
        setStreamInfo(prev => ({
          ...prev,
          viewerCount: prev.viewerCount + Math.floor(Math.random() * 10 - 5)
        }));
        
        setCaptures(prev => prev.map(capture => {
          if (capture.status === 'CAPTURING') {
            const newProgress = Math.min(capture.progress + Math.random() * 3, 95);
            return { ...capture, progress: newProgress };
          }
          if (capture.status === 'PROCESSING') {
            const newProgress = Math.min(capture.progress + Math.random() * 2, 100);
            return { 
              ...capture, 
              progress: newProgress,
              status: newProgress === 100 ? 'COMPLETED' : 'PROCESSING'
            };
          }
          return capture;
        }));
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [connection.isConnected, streamInfo.isLive]);

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Twitch className="h-5 w-5 text-purple-400" />
              Twitch Connection
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!connection.isConnected ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                  <Twitch className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Connect Your Twitch Account</h3>
                <p className="text-gray-400 mb-6 max-w-md mx-auto">
                  Connect your Twitch account to enable automatic stream capture, chat monitoring, and real-time highlight detection.
                </p>
                <Button 
                  onClick={connectToTwitch}
                  disabled={isConnecting}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                >
                  {isConnecting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Link className="h-4 w-4 mr-2" />
                      Connect to Twitch
                    </>
                  )}
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Profile Info */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <img 
                        src={connection.profileImage}
                        alt={connection.username}
                        className="w-16 h-16 rounded-full border-2 border-purple-500"
                      />
                      <div className="absolute -bottom-1 -right-1 h-6 w-6 bg-green-500 rounded-full border-2 border-gray-900 flex items-center justify-center">
                        <CheckCircle className="h-3 w-3 text-white" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white">{connection.username}</h3>
                      <p className="text-gray-400">{connection.followerCount.toLocaleString()} followers</p>
                      <p className="text-gray-500 text-sm">
                        Connected {new Date(connection.connectedAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    onClick={disconnectFromTwitch}
                    className="border-red-500/50 text-red-400 hover:bg-red-500/20"
                  >
                    <Unlink className="h-4 w-4 mr-2" />
                    Disconnect
                  </Button>
                </div>

                {/* Stream Status */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="glass-effect border-white/10">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-white font-medium">Stream Status</h4>
                        <div className="flex items-center gap-2">
                          {streamInfo.isLive ? (
                            <>
                              <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                              <Badge className="bg-red-500/20 text-red-300">LIVE</Badge>
                            </>
                          ) : (
                            <Badge className="bg-gray-500/20 text-gray-300">OFFLINE</Badge>
                          )}
                        </div>
                      </div>
                      
                      {streamInfo.isLive ? (
                        <div className="space-y-2">
                          <p className="text-white font-medium">{streamInfo.title}</p>
                          <div className="flex items-center gap-4 text-sm text-gray-400">
                            <div className="flex items-center gap-1">
                              <Play className="h-3 w-3" />
                              <span>{streamInfo.game}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Users className="h-3 w-3" />
                              <span>{streamInfo.viewerCount.toLocaleString()}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              <span>{streamInfo.duration}</span>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <p className="text-gray-400">No active stream</p>
                      )}
                    </CardContent>
                  </Card>

                  <Card className="glass-effect border-white/10">
                    <CardContent className="p-4">
                      <h4 className="text-white font-medium mb-3">Quick Actions</h4>
                      <div className="space-y-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          disabled={!streamInfo.isLive}
                          className="w-full border-blue-500/50 text-blue-400 hover:bg-blue-500/20 disabled:opacity-50"
                        >
                          <Download className="h-3 w-3 mr-2" />
                          Capture Current Stream
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          className="w-full border-purple-500/50 text-purple-400 hover:bg-purple-500/20"
                        >
                          <Zap className="h-3 w-3 mr-2" />
                          Generate Highlights
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Settings */}
      {connection.isConnected && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="glass-effect border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Settings className="h-5 w-5 text-blue-400" />
                Stream Capture Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Auto-Capture Streams</Label>
                      <p className="text-gray-400 text-sm">Automatically record when you go live</p>
                    </div>
                    <Switch
                      checked={settings.autoCapture}
                      onCheckedChange={(checked) =>
                        setSettings(prev => ({ ...prev, autoCapture: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Chat Monitoring</Label>
                      <p className="text-gray-400 text-sm">Monitor chat for "clip that" moments</p>
                    </div>
                    <Switch
                      checked={settings.chatMonitoring}
                      onCheckedChange={(checked) =>
                        setSettings(prev => ({ ...prev, chatMonitoring: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Real-time Highlights</Label>
                      <p className="text-gray-400 text-sm">Detect highlights during live streams</p>
                    </div>
                    <Switch
                      checked={settings.highlightDetection}
                      onCheckedChange={(checked) =>
                        setSettings(prev => ({ ...prev, highlightDetection: checked }))
                      }
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label className="text-white mb-2 block">Quality Preset</Label>
                    <select 
                      value={settings.qualityPreset}
                      onChange={(e) => setSettings(prev => ({ ...prev, qualityPreset: e.target.value }))}
                      className="w-full p-2 rounded-lg bg-white/5 border border-white/20 text-white"
                    >
                      <option value="source">Source Quality</option>
                      <option value="1080p">1080p</option>
                      <option value="720p">720p</option>
                      <option value="480p">480p</option>
                    </select>
                  </div>

                  <div>
                    <Label className="text-white mb-2 block">Default Clip Format</Label>
                    <div className="flex gap-2">
                      {[
                        { value: 'HORIZONTAL', label: '16:9' },
                        { value: 'VERTICAL', label: '9:16' },
                        { value: 'SQUARE', label: '1:1' }
                      ].map((format) => (
                        <Button
                          key={format.value}
                          variant={settings.clipFormat === format.value ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setSettings(prev => ({ ...prev, clipFormat: format.value as any }))}
                          className={settings.clipFormat === format.value 
                            ? 'bg-purple-500 hover:bg-purple-600' 
                            : 'border-white/20 text-white hover:bg-white/10'
                          }
                        >
                          {format.label}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-white mb-2 block">Min Clip Length</Label>
                      <Input
                        type="number"
                        value={settings.minClipDuration}
                        onChange={(e) => setSettings(prev => ({ ...prev, minClipDuration: parseInt(e.target.value) }))}
                        className="bg-white/5 border-white/20 text-white"
                        min={5}
                        max={30}
                      />
                    </div>
                    <div>
                      <Label className="text-white mb-2 block">Max Clip Length</Label>
                      <Input
                        type="number"
                        value={settings.maxClipDuration}
                        onChange={(e) => setSettings(prev => ({ ...prev, maxClipDuration: parseInt(e.target.value) }))}
                        className="bg-white/5 border-white/20 text-white"
                        min={30}
                        max={120}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Stream Captures */}
      {connection.isConnected && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="glass-effect border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Radio className="h-5 w-5 text-green-400" />
                Stream Captures ({captures.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {captures.map((capture, index) => (
                  <motion.div
                    key={capture.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-4 rounded-lg bg-white/5 border border-white/10"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="text-white font-medium">{capture.title}</h4>
                        <div className="flex items-center gap-4 text-sm text-gray-400 mt-1">
                          <div className="flex items-center gap-1">
                            <Play className="h-3 w-3" />
                            <span>{capture.game}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            <span>{capture.duration}</span>
                          </div>
                          <span>{formatFileSize(capture.fileSize)}</span>
                        </div>
                        <p className="text-gray-500 text-sm">
                          {new Date(capture.capturedAt).toLocaleString()}
                        </p>
                      </div>
                      <Badge className={getStatusColor(capture.status)}>
                        {capture.status}
                      </Badge>
                    </div>

                    {capture.status !== 'COMPLETED' && (
                      <div className="mb-3">
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-400">
                            {capture.status === 'CAPTURING' ? 'Capturing' : 'Processing'}
                          </span>
                          <span className="text-white">{Math.round(capture.progress)}%</span>
                        </div>
                        <Progress value={capture.progress} className="h-2" />
                      </div>
                    )}

                    <div className="flex items-center gap-2">
                      {capture.status === 'COMPLETED' && (
                        <>
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="border-blue-500/50 text-blue-400 hover:bg-blue-500/20"
                          >
                            <Eye className="h-3 w-3 mr-1" />
                            Preview
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="border-green-500/50 text-green-400 hover:bg-green-500/20"
                          >
                            <Download className="h-3 w-3 mr-1" />
                            Download
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="border-purple-500/50 text-purple-400 hover:bg-purple-500/20"
                          >
                            <Zap className="h-3 w-3 mr-1" />
                            Generate Clips
                          </Button>
                        </>
                      )}
                    </div>
                  </motion.div>
                ))}

                {captures.length === 0 && (
                  <div className="text-center py-8">
                    <Radio className="h-12 w-12 mx-auto mb-4 text-gray-600" />
                    <h3 className="text-lg font-medium text-white mb-2">No Stream Captures</h3>
                    <p className="text-gray-400">Start streaming to see captures here</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};

export default TwitchIntegration;
