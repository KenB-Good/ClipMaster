
'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { 
  MessageSquare, 
  Plus, 
  Edit, 
  Trash2, 
  Save, 
  X, 
  Play,
  Copy,
  Star,
  Clock,
  TrendingUp,
  Zap,
  Brain,
  Target
} from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';

interface CustomPrompt {
  id: string;
  name: string;
  description: string;
  prompt: string;
  category: 'GENERAL' | 'GAMING' | 'REACTIONS' | 'EDUCATIONAL' | 'ENTERTAINMENT';
  useCount: number;
  lastUsedAt?: string;
  createdAt: string;
  isDefault: boolean;
  tags: string[];
}

const CustomPrompts = () => {
  const [prompts, setPrompts] = useState<CustomPrompt[]>([
    {
      id: '1',
      name: 'Epic Gaming Moments',
      description: 'Detects clutch plays, comeback moments, and victory celebrations',
      prompt: 'Identify moments with high excitement including: clutch plays where the player overcomes difficult odds, comeback victories, impressive skill displays, victory celebrations, and moments where the chat explodes with excitement. Look for audio spikes indicating surprise or celebration.',
      category: 'GAMING',
      useCount: 45,
      lastUsedAt: '2024-01-15T10:30:00Z',
      createdAt: '2024-01-10T15:20:00Z',
      isDefault: true,
      tags: ['gaming', 'victory', 'clutch']
    },
    {
      id: '2',
      name: 'Funny Reactions',
      description: 'Captures hilarious and unexpected reactions',
      prompt: 'Find moments with genuine laughter, surprised reactions, funny fails, unexpected events that cause strong emotional responses, and moments where the streamer breaks character or has uncontrolled laughter.',
      category: 'REACTIONS',
      useCount: 32,
      lastUsedAt: '2024-01-14T16:45:00Z',
      createdAt: '2024-01-08T09:15:00Z',
      isDefault: true,
      tags: ['funny', 'laughter', 'surprise']
    },
    {
      id: '3',
      name: 'Educational Highlights',
      description: 'Identifies teaching moments and explanations',
      prompt: 'Capture moments where the streamer explains strategies, teaches techniques, provides tips or tutorials, answers important questions, or demonstrates complex concepts clearly.',
      category: 'EDUCATIONAL',
      useCount: 18,
      lastUsedAt: '2024-01-13T11:20:00Z',
      createdAt: '2024-01-05T14:30:00Z',
      isDefault: false,
      tags: ['tutorial', 'teaching', 'strategy']
    },
    {
      id: '4',
      name: 'Chat Interaction Peaks',
      description: 'Detects high engagement moments with chat',
      prompt: 'Identify moments when chat activity spikes significantly, when the streamer has meaningful interactions with viewers, responds to donations or subscriptions, or when chat collectively reacts to something happening on stream.',
      category: 'ENTERTAINMENT',
      useCount: 27,
      lastUsedAt: '2024-01-12T19:10:00Z',
      createdAt: '2024-01-03T12:45:00Z',
      isDefault: false,
      tags: ['chat', 'interaction', 'community']
    }
  ]);

  const [isCreating, setIsCreating] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [newPrompt, setNewPrompt] = useState({
    name: '',
    description: '',
    prompt: '',
    category: 'GENERAL' as const,
    tags: [] as string[]
  });

  const categories = [
    { value: 'GENERAL', label: 'General', icon: Target, color: 'from-gray-500 to-gray-600' },
    { value: 'GAMING', label: 'Gaming', icon: Play, color: 'from-blue-500 to-purple-500' },
    { value: 'REACTIONS', label: 'Reactions', icon: MessageSquare, color: 'from-yellow-500 to-orange-500' },
    { value: 'EDUCATIONAL', label: 'Educational', icon: Brain, color: 'from-green-500 to-emerald-500' },
    { value: 'ENTERTAINMENT', label: 'Entertainment', icon: Star, color: 'from-purple-500 to-pink-500' }
  ];

  const getCategoryColor = (category: string) => {
    const categoryInfo = categories.find(cat => cat.value === category);
    return categoryInfo ? categoryInfo.color : 'from-gray-500 to-gray-600';
  };

  const getCategoryIcon = (category: string) => {
    const categoryInfo = categories.find(cat => cat.value === category);
    return categoryInfo ? categoryInfo.icon : Target;
  };

  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = filterCategory === 'all' || prompt.category === filterCategory;
    
    return matchesSearch && matchesCategory;
  });

  const createPrompt = () => {
    if (!newPrompt.name || !newPrompt.prompt) {
      toast({
        title: "Error",
        description: "Please fill in the name and prompt fields.",
        variant: "destructive",
      });
      return;
    }

    const prompt: CustomPrompt = {
      id: Math.random().toString(36).substring(7),
      ...newPrompt,
      useCount: 0,
      createdAt: new Date().toISOString(),
      isDefault: false
    };

    setPrompts(prev => [prompt, ...prev]);
    setNewPrompt({ name: '', description: '', prompt: '', category: 'GENERAL', tags: [] });
    setIsCreating(false);
    
    toast({
      title: "Prompt Created",
      description: `"${prompt.name}" has been added to your prompts.`,
    });
  };

  const deletePrompt = (promptId: string) => {
    const prompt = prompts.find(p => p.id === promptId);
    if (prompt?.isDefault) {
      toast({
        title: "Cannot Delete",
        description: "Default prompts cannot be deleted.",
        variant: "destructive",
      });
      return;
    }

    setPrompts(prev => prev.filter(p => p.id !== promptId));
    toast({
      title: "Prompt Deleted",
      description: "The prompt has been removed.",
    });
  };

  const duplicatePrompt = (promptId: string) => {
    const original = prompts.find(p => p.id === promptId);
    if (!original) return;

    const duplicate: CustomPrompt = {
      ...original,
      id: Math.random().toString(36).substring(7),
      name: `${original.name} (Copy)`,
      useCount: 0,
      createdAt: new Date().toISOString(),
      isDefault: false,
      lastUsedAt: undefined
    };

    setPrompts(prev => [duplicate, ...prev]);
    toast({
      title: "Prompt Duplicated",
      description: `"${duplicate.name}" has been created.`,
    });
  };

  const usePrompt = (promptId: string) => {
    setPrompts(prev => prev.map(prompt => 
      prompt.id === promptId 
        ? { ...prompt, useCount: prompt.useCount + 1, lastUsedAt: new Date().toISOString() }
        : prompt
    ));
    
    const prompt = prompts.find(p => p.id === promptId);
    toast({
      title: "Prompt Applied",
      description: `"${prompt?.name}" is now being used for processing.`,
    });
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
          <h1 className="text-2xl font-bold text-white mb-2">Custom Prompts</h1>
          <p className="text-gray-400">
            Create and manage AI prompts to detect specific moments in your content
          </p>
        </div>
        <Button
          onClick={() => setIsCreating(true)}
          className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
        >
          <Plus className="h-4 w-4 mr-2" />
          Create Prompt
        </Button>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <Card className="glass-effect border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Prompts</p>
                <p className="text-2xl font-bold text-white">{prompts.length}</p>
              </div>
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                <MessageSquare className="h-4 w-4 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Most Used</p>
                <p className="text-lg font-bold text-white">
                  {prompts.reduce((max, p) => p.useCount > max ? p.useCount : max, 0)} times
                </p>
              </div>
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Categories</p>
                <p className="text-2xl font-bold text-white">
                  {new Set(prompts.map(p => p.category)).size}
                </p>
              </div>
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center">
                <Target className="h-4 w-4 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Now</p>
                <p className="text-2xl font-bold text-white">3</p>
              </div>
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-orange-500 to-red-500 flex items-center justify-center">
                <Zap className="h-4 w-4 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex flex-col sm:flex-row gap-4"
      >
        <div className="relative flex-1">
          <Input
            placeholder="Search prompts, descriptions, or tags..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-white/5 border-white/20 text-white placeholder:text-gray-500"
          />
        </div>
        <Select value={filterCategory} onValueChange={setFilterCategory}>
          <SelectTrigger className="w-48 bg-white/5 border-white/20 text-white">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map(category => (
              <SelectItem key={category.value} value={category.value}>
                {category.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </motion.div>

      {/* Create/Edit Modal */}
      <AnimatePresence>
        {isCreating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="w-full max-w-2xl"
            >
              <Card className="glass-effect border-white/20">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-white">Create New Prompt</CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsCreating(false)}
                      className="text-gray-400 hover:text-white"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-white mb-2 block">Prompt Name</Label>
                      <Input
                        placeholder="e.g., Epic Gaming Moments"
                        value={newPrompt.name}
                        onChange={(e) => setNewPrompt(prev => ({ ...prev, name: e.target.value }))}
                        className="bg-white/5 border-white/20 text-white placeholder:text-gray-500"
                      />
                    </div>
                    <div>
                      <Label className="text-white mb-2 block">Category</Label>
                      <Select value={newPrompt.category} onValueChange={(value: any) => setNewPrompt(prev => ({ ...prev, category: value }))}>
                        <SelectTrigger className="bg-white/5 border-white/20 text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {categories.map(category => (
                            <SelectItem key={category.value} value={category.value}>
                              {category.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label className="text-white mb-2 block">Description (Optional)</Label>
                    <Input
                      placeholder="Brief description of what this prompt detects..."
                      value={newPrompt.description}
                      onChange={(e) => setNewPrompt(prev => ({ ...prev, description: e.target.value }))}
                      className="bg-white/5 border-white/20 text-white placeholder:text-gray-500"
                    />
                  </div>

                  <div>
                    <Label className="text-white mb-2 block">AI Prompt</Label>
                    <Textarea
                      placeholder="Describe in detail what moments you want the AI to detect. Be specific about audio cues, visual elements, context, and timing..."
                      value={newPrompt.prompt}
                      onChange={(e) => setNewPrompt(prev => ({ ...prev, prompt: e.target.value }))}
                      className="bg-white/5 border-white/20 text-white placeholder:text-gray-500 min-h-[120px]"
                    />
                    <p className="text-gray-500 text-sm mt-2">
                      Pro tip: Include specific details about audio spikes, visual changes, chat reactions, and context clues.
                    </p>
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      onClick={() => setIsCreating(false)}
                      className="border-white/20 text-white hover:bg-white/10"
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={createPrompt}
                      className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Create Prompt
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Prompts Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        <AnimatePresence>
          {filteredPrompts.map((prompt, index) => {
            const CategoryIcon = getCategoryIcon(prompt.category);
            
            return (
              <motion.div
                key={prompt.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="clip-card h-full">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${getCategoryColor(prompt.category)}`}>
                          <CategoryIcon className="h-4 w-4 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-white font-semibold">{prompt.name}</h3>
                            {prompt.isDefault && (
                              <Badge variant="secondary" className="bg-blue-500/20 text-blue-300 text-xs">
                                Default
                              </Badge>
                            )}
                          </div>
                          <p className="text-gray-400 text-sm">{prompt.description}</p>
                        </div>
                      </div>
                    </div>

                    <div className="mb-4">
                      <p className="text-gray-300 text-sm line-clamp-3">
                        {prompt.prompt}
                      </p>
                    </div>

                    <div className="flex flex-wrap gap-1 mb-4">
                      {prompt.tags.map((tag, tagIndex) => (
                        <Badge key={tagIndex} variant="outline" className="text-xs border-white/20 text-gray-400">
                          {tag}
                        </Badge>
                      ))}
                    </div>

                    <div className="flex items-center justify-between text-sm text-gray-400 mb-4">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1">
                          <TrendingUp className="h-3 w-3" />
                          <span>{prompt.useCount} uses</span>
                        </div>
                        {prompt.lastUsedAt && (
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            <span>
                              {new Date(prompt.lastUsedAt).toLocaleDateString()}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        onClick={() => usePrompt(prompt.id)}
                        className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                      >
                        <Play className="h-3 w-3 mr-1" />
                        Use
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => duplicatePrompt(prompt.id)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Copy className="h-3 w-3 mr-1" />
                        Copy
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEditingPrompt(prompt.id)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      {!prompt.isDefault && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => deletePrompt(prompt.id)}
                          className="border-red-500/50 text-red-400 hover:bg-red-500/20"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </motion.div>

      {filteredPrompts.length === 0 && (
        <div className="text-center py-12">
          <MessageSquare className="h-16 w-16 mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-medium text-white mb-2">
            {searchTerm ? 'No prompts found' : 'No custom prompts yet'}
          </h3>
          <p className="text-gray-400 mb-6">
            {searchTerm 
              ? 'Try adjusting your search terms or filters' 
              : 'Create your first custom prompt to get started'
            }
          </p>
          {!searchTerm && (
            <Button
              onClick={() => setIsCreating(true)}
              className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Prompt
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default CustomPrompts;
