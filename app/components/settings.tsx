
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { 
  Settings as SettingsIcon, 
  Save, 
  RotateCcw, 
  HardDrive, 
  Zap, 
  Brain,
  Video,
  Trash2,
  Shield,
  Database,
  Cpu,
  AlertTriangle,
  CheckCircle,
  Download,
  Upload
} from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';

const Settings = () => {
  const [settings, setSettings] = useState({
    // Processing Settings
    enableGPUAcceleration: true,
    whisperModel: 'medium',
    maxConcurrentJobs: 3,
    defaultClipDuration: 30,
    confidenceThreshold: 0.7,
    enableSubtitles: true,
    
    // Storage Settings
    autoCleanupEnabled: true,
    autoCleanupDays: 30,
    autoCleanupThreshold: 90,
    maxFileSize: 10, // GB
    compressionQuality: 'high',
    
    // Twitch Settings
    twitchAutoCapture: false,
    twitchQuality: 'source',
    chatMonitoringEnabled: true,
    clipThatThreshold: 5, // messages per minute
    
    // AI Settings
    enableRealTimeProcessing: true,
    batchProcessingEnabled: true,
    customPromptWeighting: 1.0,
    highlightMinDuration: 5,
    highlightMaxDuration: 60,
    
    // System Settings
    enableNotifications: true,
    enableTelemetry: false,
    darkMode: true,
    language: 'en',
    timezone: 'UTC'
  });

  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const updateSetting = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const saveSettings = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
    setHasChanges(false);
    
    toast({
      title: "Settings Saved",
      description: "Your configuration has been updated successfully.",
    });
  };

  const resetSettings = () => {
    // Reset to defaults
    setSettings({
      enableGPUAcceleration: true,
      whisperModel: 'medium',
      maxConcurrentJobs: 3,
      defaultClipDuration: 30,
      confidenceThreshold: 0.7,
      enableSubtitles: true,
      autoCleanupEnabled: true,
      autoCleanupDays: 30,
      autoCleanupThreshold: 90,
      maxFileSize: 10,
      compressionQuality: 'high',
      twitchAutoCapture: false,
      twitchQuality: 'source',
      chatMonitoringEnabled: true,
      clipThatThreshold: 5,
      enableRealTimeProcessing: true,
      batchProcessingEnabled: true,
      customPromptWeighting: 1.0,
      highlightMinDuration: 5,
      highlightMaxDuration: 60,
      enableNotifications: true,
      enableTelemetry: false,
      darkMode: true,
      language: 'en',
      timezone: 'UTC'
    });
    setHasChanges(false);
    
    toast({
      title: "Settings Reset",
      description: "All settings have been reset to defaults.",
    });
  };

  const cleanupOldFiles = () => {
    toast({
      title: "Cleanup Started",
      description: "Old files are being cleaned up in the background.",
    });
  };

  const exportSettings = () => {
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'clipmaster-settings.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row gap-4 justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">
            Configure ClipMaster to optimize your workflow and performance
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={exportSettings}
            className="border-white/20 text-white hover:bg-white/10"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          {hasChanges && (
            <Button
              onClick={saveSettings}
              disabled={isSaving}
              className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          )}
        </div>
      </motion.div>

      {/* AI Processing Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-400" />
              AI Processing
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">GPU Acceleration</Label>
                    <p className="text-gray-400 text-sm">Use GPU for faster processing</p>
                  </div>
                  <Switch
                    checked={settings.enableGPUAcceleration}
                    onCheckedChange={(checked) => updateSetting('enableGPUAcceleration', checked)}
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">Whisper Model</Label>
                  <Select value={settings.whisperModel} onValueChange={(value) => updateSetting('whisperModel', value)}>
                    <SelectTrigger className="bg-white/5 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="tiny">Tiny (Fast, Lower Quality)</SelectItem>
                      <SelectItem value="base">Base (Balanced)</SelectItem>
                      <SelectItem value="small">Small (Good Quality)</SelectItem>
                      <SelectItem value="medium">Medium (High Quality)</SelectItem>
                      <SelectItem value="large">Large (Best Quality)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-white mb-2 block">
                    Max Concurrent Jobs: {settings.maxConcurrentJobs}
                  </Label>
                  <Slider
                    value={[settings.maxConcurrentJobs]}
                    onValueChange={([value]) => updateSetting('maxConcurrentJobs', value)}
                    max={8}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label className="text-white mb-2 block">
                    Confidence Threshold: {settings.confidenceThreshold}
                  </Label>
                  <Slider
                    value={[settings.confidenceThreshold]}
                    onValueChange={([value]) => updateSetting('confidenceThreshold', value)}
                    max={1}
                    min={0.1}
                    step={0.05}
                    className="w-full"
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">
                    Default Clip Duration: {settings.defaultClipDuration}s
                  </Label>
                  <Slider
                    value={[settings.defaultClipDuration]}
                    onValueChange={([value]) => updateSetting('defaultClipDuration', value)}
                    max={120}
                    min={5}
                    step={5}
                    className="w-full"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Generate Subtitles</Label>
                    <p className="text-gray-400 text-sm">Auto-generate subtitles for clips</p>
                  </div>
                  <Switch
                    checked={settings.enableSubtitles}
                    onCheckedChange={(checked) => updateSetting('enableSubtitles', checked)}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Storage Management */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <HardDrive className="h-5 w-5 text-blue-400" />
              Storage Management
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Auto-Cleanup</Label>
                    <p className="text-gray-400 text-sm">Automatically clean old files</p>
                  </div>
                  <Switch
                    checked={settings.autoCleanupEnabled}
                    onCheckedChange={(checked) => updateSetting('autoCleanupEnabled', checked)}
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">
                    Cleanup After: {settings.autoCleanupDays} days
                  </Label>
                  <Slider
                    value={[settings.autoCleanupDays]}
                    onValueChange={([value]) => updateSetting('autoCleanupDays', value)}
                    max={365}
                    min={7}
                    step={1}
                    className="w-full"
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">
                    Cleanup Threshold: {settings.autoCleanupThreshold}%
                  </Label>
                  <Slider
                    value={[settings.autoCleanupThreshold]}
                    onValueChange={([value]) => updateSetting('autoCleanupThreshold', value)}
                    max={95}
                    min={50}
                    step={5}
                    className="w-full"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label className="text-white mb-2 block">
                    Max File Size: {settings.maxFileSize} GB
                  </Label>
                  <Slider
                    value={[settings.maxFileSize]}
                    onValueChange={([value]) => updateSetting('maxFileSize', value)}
                    max={50}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">Compression Quality</Label>
                  <Select value={settings.compressionQuality} onValueChange={(value) => updateSetting('compressionQuality', value)}>
                    <SelectTrigger className="bg-white/5 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low (Smaller files)</SelectItem>
                      <SelectItem value="medium">Medium (Balanced)</SelectItem>
                      <SelectItem value="high">High (Better quality)</SelectItem>
                      <SelectItem value="lossless">Lossless (Largest files)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button
                  onClick={cleanupOldFiles}
                  variant="outline"
                  className="w-full border-red-500/50 text-red-400 hover:bg-red-500/20"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clean Up Old Files Now
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Twitch Integration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Video className="h-5 w-5 text-purple-400" />
              Twitch Integration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Auto-Capture Streams</Label>
                    <p className="text-gray-400 text-sm">Record streams automatically</p>
                  </div>
                  <Switch
                    checked={settings.twitchAutoCapture}
                    onCheckedChange={(checked) => updateSetting('twitchAutoCapture', checked)}
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">Stream Quality</Label>
                  <Select value={settings.twitchQuality} onValueChange={(value) => updateSetting('twitchQuality', value)}>
                    <SelectTrigger className="bg-white/5 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="source">Source Quality</SelectItem>
                      <SelectItem value="1080p60">1080p 60fps</SelectItem>
                      <SelectItem value="1080p">1080p 30fps</SelectItem>
                      <SelectItem value="720p60">720p 60fps</SelectItem>
                      <SelectItem value="720p">720p 30fps</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Chat Monitoring</Label>
                    <p className="text-gray-400 text-sm">Monitor for "clip that" moments</p>
                  </div>
                  <Switch
                    checked={settings.chatMonitoringEnabled}
                    onCheckedChange={(checked) => updateSetting('chatMonitoringEnabled', checked)}
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">
                    "Clip That" Threshold: {settings.clipThatThreshold} msgs/min
                  </Label>
                  <Slider
                    value={[settings.clipThatThreshold]}
                    onValueChange={([value]) => updateSetting('clipThatThreshold', value)}
                    max={20}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* System Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <SettingsIcon className="h-5 w-5 text-green-400" />
              System Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Notifications</Label>
                    <p className="text-gray-400 text-sm">Enable system notifications</p>
                  </div>
                  <Switch
                    checked={settings.enableNotifications}
                    onCheckedChange={(checked) => updateSetting('enableNotifications', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Anonymous Telemetry</Label>
                    <p className="text-gray-400 text-sm">Help improve ClipMaster</p>
                  </div>
                  <Switch
                    checked={settings.enableTelemetry}
                    onCheckedChange={(checked) => updateSetting('enableTelemetry', checked)}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label className="text-white mb-2 block">Language</Label>
                  <Select value={settings.language} onValueChange={(value) => updateSetting('language', value)}>
                    <SelectTrigger className="bg-white/5 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                      <SelectItem value="pt">Portuguese</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-white mb-2 block">Timezone</Label>
                  <Select value={settings.timezone} onValueChange={(value) => updateSetting('timezone', value)}>
                    <SelectTrigger className="bg-white/5 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                      <SelectItem value="Europe/London">London</SelectItem>
                      <SelectItem value="Europe/Paris">Paris</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <div className="flex gap-2 pt-4 border-t border-white/10">
              <Button
                onClick={resetSettings}
                variant="outline"
                className="border-red-500/50 text-red-400 hover:bg-red-500/20"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset to Defaults
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Cpu className="h-5 w-5 text-orange-400" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
                <div>
                  <p className="text-white font-medium">AI Engine</p>
                  <p className="text-gray-400 text-sm">Online</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
                <div>
                  <p className="text-white font-medium">GPU Acceleration</p>
                  <p className="text-gray-400 text-sm">Available</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-yellow-400 animate-pulse" />
                <div>
                  <p className="text-white font-medium">Twitch API</p>
                  <p className="text-gray-400 text-sm">Connected</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Settings;
