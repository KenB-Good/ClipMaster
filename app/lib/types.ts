
export interface VideoFile {
  id: string;
  filename: string;
  originalFilename: string;
  fileSize: number;
  duration?: number;
  format: string;
  resolution?: string;
  uploadedAt: string;
  status: 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'ERROR' | 'ARCHIVED';
  source: 'UPLOAD' | 'TWITCH_STREAM' | 'TWITCH_VOD';
  transcription?: string;
  highlights: Highlight[];
  clips: Clip[];
}

export interface Highlight {
  id: string;
  startTime: number;
  endTime: number;
  confidence: number;
  type: HighlightType;
  description?: string;
  metadata?: any;
  clips: Clip[];
}

export interface Clip {
  id: string;
  filename: string;
  fileSize: number;
  duration: number;
  startTime: number;
  endTime: number;
  format: 'HORIZONTAL' | 'VERTICAL' | 'SQUARE';
  hasSubtitles: boolean;
  hasOverlay: boolean;
  createdAt: string;
}

export interface ProcessingTask {
  id: string;
  type: 'TRANSCRIPTION' | 'HIGHLIGHT_DETECTION' | 'CLIP_GENERATION' | 'SUBTITLE_GENERATION' | 'TWITCH_CAPTURE';
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  progress: number;
  config?: any;
  customPrompt?: string;
  result?: any;
  error?: string;
  startedAt?: string;
  completedAt?: string;
  createdAt: string;
}

export interface TwitchIntegration {
  id: string;
  username: string;
  userId: string;
  isMonitoring: boolean;
  autoCapture: boolean;
  chatMonitoring: boolean;
  lastStreamTitle?: string;
  lastStreamGame?: string;
  connectedAt: string;
  lastUsedAt: string;
}

export interface CustomPrompt {
  id: string;
  name: string;
  description?: string;
  prompt: string;
  category: 'GENERAL' | 'GAMING' | 'REACTIONS' | 'EDUCATIONAL' | 'ENTERTAINMENT';
  useCount: number;
  lastUsedAt?: string;
  createdAt: string;
}

export interface StorageInfo {
  totalSpace: number;
  usedSpace: number;
  availableSpace: number;
  videoCount: number;
  clipCount: number;
  usagePercentage: number;
}

export interface SystemConfig {
  autoCleanupEnabled: boolean;
  autoCleanupDays: number;
  autoCleanupThreshold: number;
  maxFileSize: number;
  defaultClipDuration: number;
  enableGPUAcceleration: boolean;
  whisperModel: string;
}

export type HighlightType =
  | 'GAMEPLAY_MOMENT'
  | 'EMOTIONAL_REACTION'
  | 'CHAT_SPIKE'
  | 'GAMEPLAY_MECHANIC'
  | 'STRATEGIC_EXPLANATION'
  | 'CONTENT_PEAK'
  | 'CLIP_THAT_MOMENT'
  | 'CUSTOM_PROMPT';

export interface UploadProgress {
  filename: string;
  progress: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  error?: string;
}

export interface ProcessingConfig {
  enableTranscription: boolean;
  enableHighlightDetection: boolean;
  highlightTypes: HighlightType[];
  customPrompts: string[];
  clipFormat: 'HORIZONTAL' | 'VERTICAL' | 'SQUARE';
  generateSubtitles: boolean;
  addOverlays: boolean;
  minHighlightDuration: number;
  maxHighlightDuration: number;
  confidenceThreshold: number;
}
