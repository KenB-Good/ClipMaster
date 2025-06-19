
'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  FileVideo, 
  Search, 
  Filter, 
  Download, 
  Trash2, 
  Eye, 
  Play,
  Calendar,
  Clock,
  HardDrive,
  Scissors,
  MoreVertical,
  Grid3X3,
  List,
  SortAsc,
  SortDesc
} from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';

interface VideoFile {
  id: string;
  filename: string;
  originalFilename: string;
  fileSize: number;
  duration: number;
  format: string;
  resolution: string;
  uploadedAt: string;
  status: 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'ERROR';
  source: 'UPLOAD' | 'TWITCH_STREAM' | 'TWITCH_VOD';
  thumbnail: string;
  clipCount: number;
  highlightCount: number;
}

interface Clip {
  id: string;
  filename: string;
  fileSize: number;
  duration: number;
  format: 'HORIZONTAL' | 'VERTICAL' | 'SQUARE';
  createdAt: string;
  parentVideo: string;
  thumbnail: string;
  views: number;
  downloads: number;
}

const FileManager = () => {
  const [videos, setVideos] = useState<VideoFile[]>([
    {
      id: '1',
      filename: 'gaming_session_01.mp4',
      originalFilename: 'Gaming Session - Epic Moments.mp4',
      fileSize: 2400000000, // 2.4GB
      duration: 3600, // 1 hour
      format: 'MP4',
      resolution: '1920x1080',
      uploadedAt: '2024-01-15T10:30:00Z',
      status: 'PROCESSED',
      source: 'UPLOAD',
      thumbnail: 'https://i.ytimg.com/vi/tsx95odmMCw/maxresdefault.jpg',
      clipCount: 8,
      highlightCount: 12
    },
    {
      id: '2',
      filename: 'stream_highlight_reel.mp4',
      originalFilename: 'Stream Highlight Reel.mp4',
      fileSize: 1800000000, // 1.8GB
      duration: 2700, // 45 min
      format: 'MP4',
      resolution: '1920x1080',
      uploadedAt: '2024-01-14T15:45:00Z',
      status: 'PROCESSED',
      source: 'TWITCH_STREAM',
      thumbnail: 'https://i.ytimg.com/vi/BR97ESmk7e0/maxresdefault.jpg',
      clipCount: 15,
      highlightCount: 20
    },
    {
      id: '3',
      filename: 'reaction_compilation.mp4',
      originalFilename: 'Funny Reactions Compilation.mp4',
      fileSize: 950000000, // 950MB
      duration: 1200, // 20 min
      format: 'MP4',
      resolution: '1920x1080',
      uploadedAt: '2024-01-13T09:15:00Z',
      status: 'PROCESSING',
      source: 'UPLOAD',
      thumbnail: 'https://i.ytimg.com/vi/gEt6bUWgMDk/maxresdefault.jpg',
      clipCount: 3,
      highlightCount: 8
    }
  ]);

  const [clips, setClips] = useState<Clip[]>([
    {
      id: '1',
      filename: 'epic_comeback_moment.mp4',
      fileSize: 45000000, // 45MB
      duration: 15,
      format: 'HORIZONTAL',
      createdAt: '2024-01-15T11:30:00Z',
      parentVideo: 'gaming_session_01.mp4',
      thumbnail: 'https://i.pinimg.com/736x/4f/a4/83/4fa4837443b4d8d577c756b8b0bcf33d.jpg',
      views: 1250,
      downloads: 89
    },
    {
      id: '2',
      filename: 'funny_reaction_vertical.mp4',
      fileSize: 25000000, // 25MB
      duration: 12,
      format: 'VERTICAL',
      createdAt: '2024-01-14T16:20:00Z',
      parentVideo: 'stream_highlight_reel.mp4',
      thumbnail: 'https://i.ytimg.com/vi/D2gbLowRSSk/maxresdefault.jpg',
      views: 890,
      downloads: 156
    },
    {
      id: '3',
      filename: 'clutch_play_square.mp4',
      fileSize: 35000000, // 35MB
      duration: 18,
      format: 'SQUARE',
      createdAt: '2024-01-13T10:45:00Z',
      parentVideo: 'gaming_session_01.mp4',
      thumbnail: 'https://i.ytimg.com/vi/tU_kSIW8CzE/maxresdefault.jpg',
      views: 645,
      downloads: 73
    }
  ]);

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [activeTab, setActiveTab] = useState<'videos' | 'clips'>('videos');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('uploadedAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSource, setFilterSource] = useState('all');

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PROCESSED':
        return 'bg-green-500/20 text-green-300';
      case 'PROCESSING':
        return 'bg-blue-500/20 text-blue-300';
      case 'ERROR':
        return 'bg-red-500/20 text-red-300';
      default:
        return 'bg-gray-500/20 text-gray-300';
    }
  };

  const getFormatColor = (format: string) => {
    switch (format) {
      case 'HORIZONTAL':
        return 'bg-blue-500/20 text-blue-300';
      case 'VERTICAL':
        return 'bg-purple-500/20 text-purple-300';
      case 'SQUARE':
        return 'bg-green-500/20 text-green-300';
      default:
        return 'bg-gray-500/20 text-gray-300';
    }
  };

  const toggleItemSelection = (itemId: string) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const selectAllItems = () => {
    const currentItems = activeTab === 'videos' ? videos : clips;
    const allIds = currentItems.map(item => item.id);
    setSelectedItems(selectedItems.length === allIds.length ? [] : allIds);
  };

  const deleteSelectedItems = () => {
    if (activeTab === 'videos') {
      setVideos(prev => prev.filter(video => !selectedItems.includes(video.id)));
    } else {
      setClips(prev => prev.filter(clip => !selectedItems.includes(clip.id)));
    }
    setSelectedItems([]);
  };

  const downloadSelectedItems = () => {
    // Implementation for downloading selected items
    console.log('Downloading items:', selectedItems);
  };

  const filteredAndSortedItems = () => {
    const items = activeTab === 'videos' ? videos : clips;
    
    let filtered = items.filter(item => {
      const matchesSearch = item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           ('originalFilename' in item ? item.originalFilename.toLowerCase().includes(searchTerm.toLowerCase()) : true);
      
      const matchesStatus = filterStatus === 'all' || 
                           ('status' in item ? item.status === filterStatus : true);
      
      const matchesSource = filterSource === 'all' || 
                           ('source' in item ? item.source === filterSource : true);
      
      return matchesSearch && matchesStatus && matchesSource;
    });

    // Sort items
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'filename':
          aValue = a.filename;
          bValue = b.filename;
          break;
        case 'fileSize':
          aValue = a.fileSize;
          bValue = b.fileSize;
          break;
        case 'duration':
          aValue = a.duration;
          bValue = b.duration;
          break;
        case 'uploadedAt':
        case 'createdAt':
          aValue = new Date('uploadedAt' in a ? a.uploadedAt : a.createdAt).getTime();
          bValue = new Date('uploadedAt' in b ? b.uploadedAt : b.createdAt).getTime();
          break;
        default:
          return 0;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row gap-4 justify-between"
      >
        <div className="flex items-center gap-4">
          <div className="flex bg-white/5 rounded-lg p-1">
            <Button
              variant={activeTab === 'videos' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('videos')}
              className={activeTab === 'videos' ? 'bg-purple-500 hover:bg-purple-600' : 'text-gray-400 hover:text-white hover:bg-white/10'}
            >
              <FileVideo className="h-4 w-4 mr-2" />
              Videos ({videos.length})
            </Button>
            <Button
              variant={activeTab === 'clips' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('clips')}
              className={activeTab === 'clips' ? 'bg-purple-500 hover:bg-purple-600' : 'text-gray-400 hover:text-white hover:bg-white/10'}
            >
              <Scissors className="h-4 w-4 mr-2" />
              Clips ({clips.length})
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            className="border-white/20 text-white hover:bg-white/10"
          >
            {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid3X3 className="h-4 w-4" />}
          </Button>
          
          {selectedItems.length > 0 && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={downloadSelectedItems}
                className="border-blue-500/50 text-blue-400 hover:bg-blue-500/20"
              >
                <Download className="h-4 w-4 mr-2" />
                Download ({selectedItems.length})
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={deleteSelectedItems}
                className="border-red-500/50 text-red-400 hover:bg-red-500/20"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete ({selectedItems.length})
              </Button>
            </>
          )}
        </div>
      </motion.div>

      {/* Filters and Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4"
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder={`Search ${activeTab}...`}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-white/5 border-white/20 text-white placeholder:text-gray-500"
          />
        </div>

        <div className="flex gap-2">
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-32 bg-white/5 border-white/20 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="uploadedAt">Date</SelectItem>
              <SelectItem value="filename">Name</SelectItem>
              <SelectItem value="fileSize">Size</SelectItem>
              <SelectItem value="duration">Duration</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="border-white/20 text-white hover:bg-white/10"
          >
            {sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
          </Button>

          {activeTab === 'videos' && (
            <>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-32 bg-white/5 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="PROCESSED">Processed</SelectItem>
                  <SelectItem value="PROCESSING">Processing</SelectItem>
                  <SelectItem value="ERROR">Error</SelectItem>
                </SelectContent>
              </Select>

              <Select value={filterSource} onValueChange={setFilterSource}>
                <SelectTrigger className="w-32 bg-white/5 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sources</SelectItem>
                  <SelectItem value="UPLOAD">Upload</SelectItem>
                  <SelectItem value="TWITCH_STREAM">Twitch Stream</SelectItem>
                  <SelectItem value="TWITCH_VOD">Twitch VOD</SelectItem>
                </SelectContent>
              </Select>
            </>
          )}
        </div>
      </motion.div>

      {/* Bulk Actions */}
      {filteredAndSortedItems().length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center gap-4 p-4 glass-effect rounded-lg border border-white/10"
        >
          <div className="flex items-center gap-2">
            <Checkbox
              checked={selectedItems.length === filteredAndSortedItems().length}
              onCheckedChange={selectAllItems}
            />
            <span className="text-white text-sm">
              {selectedItems.length > 0 
                ? `${selectedItems.length} selected` 
                : 'Select all'
              }
            </span>
          </div>
        </motion.div>
      )}

      {/* File Grid/List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <AnimatePresence>
              {filteredAndSortedItems().map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.05 }}
                  className="group"
                >
                  <Card className={`clip-card ${selectedItems.includes(item.id) ? 'ring-2 ring-purple-500' : ''}`}>
                    <CardContent className="p-4">
                      <div className="relative mb-4">
                        <div className="aspect-video bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg overflow-hidden">
                          <img 
                            src={item.thumbnail}
                            alt={item.filename}
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300">
                            <Button size="sm" className="bg-white/20 hover:bg-white/30">
                              <Play className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        
                        <div className="absolute top-2 left-2">
                          <Checkbox
                            checked={selectedItems.includes(item.id)}
                            onCheckedChange={() => toggleItemSelection(item.id)}
                            className="bg-white/20 border-white/50"
                          />
                        </div>
                        
                        <div className="absolute top-2 right-2 flex gap-1">
                          {activeTab === 'videos' && 'status' in item && (
                            <Badge className={getStatusColor(item.status)}>
                              {item.status}
                            </Badge>
                          )}
                          {activeTab === 'clips' && 'format' in item && (
                            <Badge className={getFormatColor(item.format)}>
                              {item.format}
                            </Badge>
                          )}
                        </div>
                        
                        <Badge className="absolute bottom-2 right-2 bg-black/60 text-white">
                          {formatDuration(item.duration)}
                        </Badge>
                      </div>
                      
                      <div className="space-y-2">
                        <h3 className="text-white font-medium truncate" title={item.filename}>
                          {item.filename}
                        </h3>
                        
                        <div className="flex items-center justify-between text-sm text-gray-400">
                          <span>{formatFileSize(item.fileSize)}</span>
                          <div className="flex items-center gap-1">
                            <HardDrive className="h-3 w-3" />
                            <span>{formatFileSize(item.fileSize)}</span>
                          </div>
                        </div>
                        
                        {activeTab === 'videos' && 'clipCount' in item && (
                          <div className="flex items-center justify-between text-sm text-gray-400">
                            <div className="flex items-center gap-1">
                              <Scissors className="h-3 w-3" />
                              <span>{item.clipCount} clips</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Eye className="h-3 w-3" />
                              <span>{item.highlightCount} highlights</span>
                            </div>
                          </div>
                        )}
                        
                        {activeTab === 'clips' && 'views' in item && (
                          <div className="flex items-center justify-between text-sm text-gray-400">
                            <div className="flex items-center gap-1">
                              <Eye className="h-3 w-3" />
                              <span>{item.views} views</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Download className="h-3 w-3" />
                              <span>{item.downloads}</span>
                            </div>
                          </div>
                        )}
                        
                        <div className="flex items-center justify-between pt-2 border-t border-white/10">
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            <Calendar className="h-3 w-3" />
                            <span>
                              {new Date(
                                'uploadedAt' in item ? item.uploadedAt : item.createdAt
                              ).toLocaleDateString()}
                            </span>
                          </div>
                          
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent>
                              <DropdownMenuItem>
                                <Play className="h-4 w-4 mr-2" />
                                Preview
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Download className="h-4 w-4 mr-2" />
                                Download
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-red-400">
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        ) : (
          <Card className="glass-effect border-white/10">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left p-4 text-gray-400 font-medium">
                        <Checkbox
                          checked={selectedItems.length === filteredAndSortedItems().length}
                          onCheckedChange={selectAllItems}
                        />
                      </th>
                      <th className="text-left p-4 text-gray-400 font-medium">Name</th>
                      <th className="text-left p-4 text-gray-400 font-medium">Size</th>
                      <th className="text-left p-4 text-gray-400 font-medium">Duration</th>
                      <th className="text-left p-4 text-gray-400 font-medium">Date</th>
                      <th className="text-left p-4 text-gray-400 font-medium">Status</th>
                      <th className="text-left p-4 text-gray-400 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAndSortedItems().map((item, index) => (
                      <motion.tr
                        key={item.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`border-b border-white/5 hover:bg-white/5 ${
                          selectedItems.includes(item.id) ? 'bg-purple-500/10' : ''
                        }`}
                      >
                        <td className="p-4">
                          <Checkbox
                            checked={selectedItems.includes(item.id)}
                            onCheckedChange={() => toggleItemSelection(item.id)}
                          />
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-8 bg-gradient-to-br from-gray-800 to-gray-900 rounded overflow-hidden">
                              <img 
                                src={item.thumbnail}
                                alt={item.filename}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            <div>
                              <p className="text-white font-medium">{item.filename}</p>
                              {'originalFilename' in item && (
                                <p className="text-gray-400 text-sm">{item.originalFilename}</p>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="p-4 text-gray-300">{formatFileSize(item.fileSize)}</td>
                        <td className="p-4 text-gray-300">{formatDuration(item.duration)}</td>
                        <td className="p-4 text-gray-300">
                          {new Date(
                            'uploadedAt' in item ? item.uploadedAt : item.createdAt
                          ).toLocaleDateString()}
                        </td>
                        <td className="p-4">
                          {activeTab === 'videos' && 'status' in item && (
                            <Badge className={getStatusColor(item.status)}>
                              {item.status}
                            </Badge>
                          )}
                          {activeTab === 'clips' && 'format' in item && (
                            <Badge className={getFormatColor(item.format)}>
                              {item.format}
                            </Badge>
                          )}
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                              <Play className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                              <Download className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {filteredAndSortedItems().length === 0 && (
          <div className="text-center py-12">
            <FileVideo className="h-16 w-16 mx-auto mb-4 text-gray-600" />
            <h3 className="text-xl font-medium text-white mb-2">No {activeTab} found</h3>
            <p className="text-gray-400">
              {searchTerm ? 'Try adjusting your search or filters' : `Upload some videos to see them here`}
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default FileManager;
