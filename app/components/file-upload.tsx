
'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Upload, 
  FileVideo, 
  X, 
  Play, 
  AlertCircle,
  CheckCircle,
  Loader2,
  Settings,
  Zap
} from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface UploadFile {
  id: string;
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  error?: string;
}

const FileUpload = () => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [processingConfig, setProcessingConfig] = useState({
    enableTranscription: true,
    enableHighlightDetection: true,
    generateSubtitles: true,
    clipFormat: 'HORIZONTAL' as const,
    confidenceThreshold: 0.7,
    customPrompt: ''
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadFile[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substring(7),
      file,
      progress: 0,
      status: 'uploading'
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Simulate upload and processing
    newFiles.forEach(uploadFile => {
      simulateUpload(uploadFile.id);
    });
  }, []);

  const simulateUpload = (fileId: string) => {
    const updateProgress = () => {
      setFiles(prev => prev.map(file => {
        if (file.id === fileId) {
          const newProgress = Math.min(file.progress + Math.random() * 10, 100);
          const newStatus = newProgress === 100 ? 'processing' : file.status;
          
          if (newProgress === 100 && file.status === 'uploading') {
            setTimeout(() => simulateProcessing(fileId), 1000);
          }
          
          return { ...file, progress: newProgress, status: newStatus };
        }
        return file;
      }));
    };

    const interval = setInterval(updateProgress, 200);
    setTimeout(() => clearInterval(interval), 3000);
  };

  const simulateProcessing = (fileId: string) => {
    setFiles(prev => prev.map(file => {
      if (file.id === fileId) {
        return { ...file, status: 'processing', progress: 0 };
      }
      return file;
    }));

    const updateProcessing = () => {
      setFiles(prev => prev.map(file => {
        if (file.id === fileId && file.status === 'processing') {
          const newProgress = Math.min(file.progress + Math.random() * 8, 100);
          const newStatus = newProgress === 100 ? 'complete' : 'processing';
          
          if (newProgress === 100) {
            toast({
              title: "Processing Complete",
              description: `${file.file.name} has been processed successfully.`,
            });
          }
          
          return { ...file, progress: newProgress, status: newStatus };
        }
        return file;
      }));
    };

    const interval = setInterval(updateProcessing, 300);
    setTimeout(() => clearInterval(interval), 5000);
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    },
    multiple: true
  });

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-400" />;
      case 'complete':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Upload className="h-5 w-5 text-purple-400" />
              Upload Videos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={`upload-zone p-8 text-center cursor-pointer ${
                isDragActive ? 'border-purple-400 bg-purple-500/20' : ''
              }`}
            >
              <input {...getInputProps()} />
              <motion.div
                initial={{ scale: 1 }}
                animate={{ scale: isDragActive ? 1.05 : 1 }}
                className="space-y-4"
              >
                <div className="mx-auto w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
                  <FileVideo className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {isDragActive ? 'Drop your videos here' : 'Upload your videos'}
                  </h3>
                  <p className="text-gray-400">
                    Drag and drop your video files here, or click to browse
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Supports MP4, MOV, AVI, MKV, WebM • No size limit
                  </p>
                </div>
                <Button 
                  type="button"
                  className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                >
                  Choose Files
                </Button>
              </motion.div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Processing Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Settings className="h-5 w-5 text-blue-400" />
              Processing Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="transcription"
                    checked={processingConfig.enableTranscription}
                    onCheckedChange={(checked) =>
                      setProcessingConfig(prev => ({ ...prev, enableTranscription: checked as boolean }))
                    }
                  />
                  <Label htmlFor="transcription" className="text-white">
                    Enable Speech-to-Text Transcription
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="highlights"
                    checked={processingConfig.enableHighlightDetection}
                    onCheckedChange={(checked) =>
                      setProcessingConfig(prev => ({ ...prev, enableHighlightDetection: checked as boolean }))
                    }
                  />
                  <Label htmlFor="highlights" className="text-white">
                    AI Highlight Detection
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="subtitles"
                    checked={processingConfig.generateSubtitles}
                    onCheckedChange={(checked) =>
                      setProcessingConfig(prev => ({ ...prev, generateSubtitles: checked as boolean }))
                    }
                  />
                  <Label htmlFor="subtitles" className="text-white">
                    Generate Animated Subtitles
                  </Label>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label className="text-white mb-2 block">Clip Format</Label>
                  <div className="flex gap-2">
                    {[
                      { value: 'HORIZONTAL', label: '16:9' },
                      { value: 'VERTICAL', label: '9:16' },
                      { value: 'SQUARE', label: '1:1' }
                    ].map((format) => (
                      <Button
                        key={format.value}
                        variant={processingConfig.clipFormat === format.value ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setProcessingConfig(prev => ({ ...prev, clipFormat: format.value as any }))}
                        className={processingConfig.clipFormat === format.value 
                          ? 'bg-purple-500 hover:bg-purple-600' 
                          : 'border-white/20 text-white hover:bg-white/10'
                        }
                      >
                        {format.label}
                      </Button>
                    ))}
                  </div>
                </div>

                <div>
                  <Label htmlFor="confidence" className="text-white mb-2 block">
                    Confidence Threshold: {processingConfig.confidenceThreshold}
                  </Label>
                  <input
                    type="range"
                    min="0.1"
                    max="1"
                    step="0.1"
                    value={processingConfig.confidenceThreshold}
                    onChange={(e) => setProcessingConfig(prev => ({ ...prev, confidenceThreshold: parseFloat(e.target.value) }))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="customPrompt" className="text-white mb-2 block">
                Custom AI Prompt (Optional)
              </Label>
              <Textarea
                id="customPrompt"
                placeholder="Describe what specific moments you want to detect..."
                value={processingConfig.customPrompt}
                onChange={(e) => setProcessingConfig(prev => ({ ...prev, customPrompt: e.target.value }))}
                className="bg-white/5 border-white/20 text-white placeholder:text-gray-500"
                rows={3}
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Upload Queue */}
      {files.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="glass-effect border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-400" />
                Upload Queue ({files.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <AnimatePresence>
                  {files.map((file) => (
                    <motion.div
                      key={file.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="p-4 rounded-lg bg-white/5 border border-white/10"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(file.status)}
                          <div>
                            <h4 className="text-white font-medium">{file.file.name}</h4>
                            <p className="text-gray-400 text-sm">
                              {formatFileSize(file.file.size)} • {file.status}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant={file.status === 'complete' ? 'default' : 'secondary'}
                            className={
                              file.status === 'complete' 
                                ? 'bg-green-500/20 text-green-300'
                                : file.status === 'error'
                                ? 'bg-red-500/20 text-red-300'
                                : 'bg-blue-500/20 text-blue-300'
                            }
                          >
                            {file.status}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(file.id)}
                            className="text-gray-400 hover:text-white hover:bg-white/10"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">
                            {file.status === 'uploading' ? 'Uploading' : 
                             file.status === 'processing' ? 'Processing' : 'Progress'}
                          </span>
                          <span className="text-white">{Math.round(file.progress)}%</span>
                        </div>
                        <Progress 
                          value={file.progress} 
                          className={`h-2 ${file.status === 'processing' ? 'processing-glow' : ''}`}
                        />
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};

export default FileUpload;
