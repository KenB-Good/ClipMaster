

'use client'

import { useEffect, useState } from 'react'

interface KofiWidgetProps {
  username?: string
  backgroundColor?: string
  textColor?: string
  ctaText?: string
  type?: 'floating-chat' | 'floating-button'
}

export default function KofiWidget({
  username = 'epickenbee',
  backgroundColor = '#FF5E5B',
  textColor = '#FFFFFF',
  ctaText = 'Support Us',
  type = 'floating-chat'
}: KofiWidgetProps) {
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    // Check if script is already loaded
    if (window.kofiWidgetOverlay) {
      setLoaded(true)
      return
    }

    // Load Ko-fi overlay script
    const script = document.createElement('script')
    script.src = 'https://storage.ko-fi.com/cdn/scripts/overlay-widget.js'
    script.async = true
    script.onload = () => setLoaded(true)
    script.onerror = () => console.error('Failed to load Ko-fi widget script')
    
    document.body.appendChild(script)

    // Cleanup function
    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script)
      }
    }
  }, [])

  useEffect(() => {
    if (loaded && window.kofiWidgetOverlay) {
      try {
        window.kofiWidgetOverlay.draw(username, {
          'type': type,
          'floating-chat.donateButton.text': ctaText,
          'floating-chat.donateButton.background-color': backgroundColor,
          'floating-chat.donateButton.text-color': textColor
        })
      } catch (error) {
        console.error('Error initializing Ko-fi widget:', error)
      }
    }
  }, [loaded, username, backgroundColor, textColor, ctaText, type])

  return null // This component doesn't render anything visible
}

// Extend Window interface for TypeScript
declare global {
  interface Window {
    kofiWidgetOverlay: {
      draw: (username: string, options: Record<string, string>) => void
    }
  }
}

