# ClipMaster - AI-Powered Video Clipping System

ClipMaster is an advanced AI-powered video clipping system that automatically identifies and extracts the most engaging moments from your videos. Built with Next.js, React, and PostgreSQL, it provides a comprehensive solution for content creators, streamers, and video editors.

## Features

### 🎯 AI-Powered Clipping
- Automatic highlight detection using advanced AI algorithms
- Custom prompt-based clipping for specific content types
- Smart scene detection and transition analysis
- Audio analysis for excitement and engagement detection

### 🎮 Twitch Integration
- Direct Twitch stream integration
- Real-time clip generation during live streams
- Automatic VOD processing
- Chat sentiment analysis for clip timing

### 📁 File Management
- Drag-and-drop video upload
- Support for multiple video formats
- Cloud storage integration
- Organized clip library with tagging

### ⚡ Processing Queue
- Background video processing
- Real-time progress tracking
- Batch processing capabilities
- Priority queue management

### 🎨 Modern UI/UX
- Clean, intuitive dashboard
- Dark/light theme support
- Responsive design for all devices
- Real-time notifications

### 📊 Analytics & Monitoring
- Processing statistics
- Storage usage monitoring
- Performance metrics
- Export capabilities

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **UI Components**: Radix UI, Tailwind CSS, Framer Motion
- **Backend**: Next.js API Routes
- **Database**: PostgreSQL with Prisma ORM
- **File Upload**: React Dropzone
- **Styling**: Tailwind CSS with custom components
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ 
- PostgreSQL database
- Yarn package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/KenB-Good/ClipMaster.git
cd ClipMaster
```

2. Install dependencies:
```bash
cd app
yarn install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your database connection string:
```
DATABASE_URL="postgresql://username:password@localhost:5432/clipmaster"
```

4. Set up the database:
```bash
yarn prisma generate
yarn prisma db push
```

5. Start the development server:
```bash
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

```
app/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── dashboard.tsx     # Main dashboard
│   ├── file-upload.tsx   # File upload component
│   ├── processing-queue.tsx # Processing queue
│   └── ...               # Other components
├── lib/                  # Utility libraries
│   ├── db.ts            # Database connection
│   ├── types.ts         # TypeScript types
│   └── utils.ts         # Utility functions
├── prisma/              # Database schema
│   └── schema.prisma    # Prisma schema
└── hooks/               # Custom React hooks
    └── use-toast.ts     # Toast notifications
```

## Database Schema

The application uses PostgreSQL with Prisma ORM. Key entities include:

- **User**: User accounts and authentication
- **Video**: Uploaded video files and metadata
- **Clip**: Generated clips with timestamps
- **ProcessingJob**: Background processing tasks
- **TwitchIntegration**: Twitch account connections

## API Routes

The application provides RESTful API endpoints for:

- Video upload and management
- Clip generation and retrieval
- Processing queue management
- User authentication
- Twitch integration

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the development team.

## Roadmap

- [ ] Advanced AI models for better clip detection
- [ ] YouTube integration
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Plugin system for custom AI models

---

**ClipMaster** - Transforming video content creation with AI-powered automation.