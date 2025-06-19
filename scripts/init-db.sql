
-- ClipMaster Database Initialization Script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE video_status AS ENUM ('UPLOADED', 'PROCESSING', 'PROCESSED', 'ERROR', 'ARCHIVED');
CREATE TYPE video_source AS ENUM ('UPLOAD', 'TWITCH_STREAM', 'TWITCH_VOD');
CREATE TYPE highlight_type AS ENUM (
    'GAMEPLAY_MOMENT', 
    'EMOTIONAL_REACTION', 
    'CHAT_SPIKE', 
    'GAMEPLAY_MECHANIC', 
    'STRATEGIC_EXPLANATION', 
    'CONTENT_PEAK', 
    'CLIP_THAT_MOMENT', 
    'CUSTOM_PROMPT'
);
CREATE TYPE clip_format AS ENUM ('HORIZONTAL', 'VERTICAL', 'SQUARE');
CREATE TYPE task_type AS ENUM (
    'TRANSCRIPTION', 
    'HIGHLIGHT_DETECTION', 
    'CLIP_GENERATION', 
    'SUBTITLE_GENERATION', 
    'TWITCH_CAPTURE'
);
CREATE TYPE task_status AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED');
CREATE TYPE prompt_category AS ENUM ('GENERAL', 'GAMING', 'REACTIONS', 'EDUCATIONAL', 'ENTERTAINMENT');
CREATE TYPE config_type AS ENUM ('STRING', 'NUMBER', 'BOOLEAN', 'JSON');

-- Create tables
CREATE TABLE IF NOT EXISTS videos (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size BIGINT NOT NULL,
    duration REAL,
    format VARCHAR NOT NULL,
    resolution VARCHAR,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    status video_status DEFAULT 'UPLOADED',
    source video_source DEFAULT 'UPLOAD',
    twitch_stream_id VARCHAR,
    twitch_title VARCHAR,
    twitch_game VARCHAR,
    transcription TEXT
);

CREATE TABLE IF NOT EXISTS highlights (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id VARCHAR NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    confidence REAL NOT NULL,
    type highlight_type NOT NULL,
    description VARCHAR,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clips (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id VARCHAR NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    highlight_id VARCHAR REFERENCES highlights(id) ON DELETE SET NULL,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size BIGINT NOT NULL,
    duration REAL NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    format clip_format DEFAULT 'HORIZONTAL',
    has_subtitles BOOLEAN DEFAULT FALSE,
    has_overlay BOOLEAN DEFAULT FALSE,
    overlay_config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    downloaded_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS processing_tasks (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id VARCHAR REFERENCES videos(id) ON DELETE CASCADE,
    type task_type NOT NULL,
    status task_status DEFAULT 'PENDING',
    progress REAL DEFAULT 0,
    config JSONB,
    custom_prompt TEXT,
    result JSONB,
    error TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS twitch_integrations (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4(),
    access_token VARCHAR NOT NULL,
    refresh_token VARCHAR NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    user_id VARCHAR UNIQUE NOT NULL,
    is_monitoring BOOLEAN DEFAULT FALSE,
    auto_capture BOOLEAN DEFAULT FALSE,
    chat_monitoring BOOLEAN DEFAULT TRUE,
    last_stream_id VARCHAR,
    last_stream_title VARCHAR,
    last_stream_game VARCHAR,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS custom_prompts (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    description VARCHAR,
    prompt TEXT NOT NULL,
    category prompt_category DEFAULT 'GENERAL',
    use_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_configs (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR UNIQUE NOT NULL,
    value TEXT NOT NULL,
    type config_type DEFAULT 'STRING',
    description VARCHAR,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS storage_stats (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4(),
    total_space BIGINT NOT NULL,
    used_space BIGINT NOT NULL,
    available_space BIGINT NOT NULL,
    video_count INTEGER NOT NULL,
    clip_count INTEGER NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_uploaded_at ON videos(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_videos_source ON videos(source);

CREATE INDEX IF NOT EXISTS idx_highlights_video_id ON highlights(video_id);
CREATE INDEX IF NOT EXISTS idx_highlights_type ON highlights(type);
CREATE INDEX IF NOT EXISTS idx_highlights_confidence ON highlights(confidence);

CREATE INDEX IF NOT EXISTS idx_clips_video_id ON clips(video_id);
CREATE INDEX IF NOT EXISTS idx_clips_highlight_id ON clips(highlight_id);
CREATE INDEX IF NOT EXISTS idx_clips_created_at ON clips(created_at);

CREATE INDEX IF NOT EXISTS idx_tasks_video_id ON processing_tasks(video_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON processing_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON processing_tasks(type);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON processing_tasks(created_at);

CREATE INDEX IF NOT EXISTS idx_twitch_username ON twitch_integrations(username);
CREATE INDEX IF NOT EXISTS idx_twitch_user_id ON twitch_integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_twitch_monitoring ON twitch_integrations(is_monitoring);

CREATE INDEX IF NOT EXISTS idx_prompts_category ON custom_prompts(category);
CREATE INDEX IF NOT EXISTS idx_prompts_use_count ON custom_prompts(use_count);

CREATE INDEX IF NOT EXISTS idx_storage_recorded_at ON storage_stats(recorded_at);

-- Insert default system configurations
INSERT INTO system_configs (key, value, type, description) VALUES
('auto_cleanup_enabled', 'true', 'BOOLEAN', 'Enable automatic cleanup of old files'),
('auto_cleanup_days', '30', 'NUMBER', 'Number of days before files are eligible for cleanup'),
('auto_cleanup_threshold', '0.8', 'NUMBER', 'Storage usage threshold for triggering cleanup'),
('whisper_model', 'base', 'STRING', 'Whisper model to use for transcription'),
('enable_gpu', 'true', 'BOOLEAN', 'Enable GPU acceleration for AI processing'),
('default_clip_duration', '30', 'NUMBER', 'Default clip duration in seconds'),
('confidence_threshold', '0.7', 'NUMBER', 'Minimum confidence threshold for highlights'),
('max_file_size', '5368709120', 'NUMBER', 'Maximum file size in bytes (5GB)')
ON CONFLICT (key) DO NOTHING;

-- Insert sample custom prompts
INSERT INTO custom_prompts (name, description, prompt, category) VALUES
('Gaming Highlights', 'Find exciting gaming moments', 'Find moments with intense gameplay, skillful plays, or exciting reactions', 'GAMING'),
('Funny Moments', 'Detect humorous content', 'Identify funny moments, jokes, laughter, and comedic situations', 'ENTERTAINMENT'),
('Educational Content', 'Extract learning moments', 'Find explanations, tutorials, tips, and educational content', 'EDUCATIONAL'),
('Emotional Reactions', 'Capture strong emotions', 'Detect strong emotional reactions, excitement, surprise, or dramatic moments', 'REACTIONS'),
('Clip That Moments', 'Find "clip that" requests', 'Identify moments when viewers say "clip that" or similar phrases indicating highlight-worthy content', 'GENERAL')
ON CONFLICT DO NOTHING;

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_custom_prompts_updated_at BEFORE UPDATE ON custom_prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_configs_updated_at BEFORE UPDATE ON system_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
