

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/toaster'
import KofiWidget from '@/components/kofi-widget'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ClipMaster - AI-Powered Video Clipping Platform | WeirdDucks Studio',
  description: 'Transform your content creation with ClipMaster - the ultimate AI-powered video clipping system. Intelligent highlight detection, automated editing, real-time Twitch integration, and professional video processing for creators and streamers.',
  keywords: 'AI video clipping, video editing software, Twitch highlights, content creation, automated video editing, AI video processing, stream highlights, video clips generator, WeirdDucks Studio',
  authors: [{ name: 'WeirdDucks Studio' }, { name: 'KenB-Good' }, { name: 'EpicKenBee' }],
  creator: 'WeirdDucks Studio',
  publisher: 'WeirdDucks Studio',
  robots: 'index, follow',
  openGraph: {
    title: 'ClipMaster - AI-Powered Video Clipping Platform',
    description: 'Transform your content creation with intelligent AI-powered video clipping and highlight detection.',
    url: 'https://github.com/KenB-Good/ClipMaster',
    siteName: 'ClipMaster',
    type: 'website',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'ClipMaster - AI-Powered Video Clipping Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ClipMaster - AI-Powered Video Clipping Platform',
    description: 'Transform your content creation with intelligent AI-powered video clipping and highlight detection.',
    creator: '@weirdduckstudio',
    images: ['/og-image.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            {children}
          </div>
          <Toaster />
          <KofiWidget 
            username="epickenbee"
            backgroundColor="#FF5E5B"
            textColor="#FFFFFF"
            ctaText="💖 Support ClipMaster"
            type="floating-chat"
          />
        </ThemeProvider>
      </body>
    </html>
  )
}

