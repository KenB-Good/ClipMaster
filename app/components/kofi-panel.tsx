

'use client'

import { useState } from 'react'
import { Heart, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

interface KofiPanelProps {
  username?: string
  title?: string
  description?: string
  className?: string
}

export default function KofiPanel({
  username = 'epickenbee',
  title = 'Support ClipMaster Development',
  description = 'Help us continue developing amazing AI-powered video tools!',
  className = ''
}: KofiPanelProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          size="sm"
          className={`bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white border-none ${className}`}
        >
          <Heart className="w-4 h-4 mr-2" />
          Support Us
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Heart className="w-5 h-5 text-red-500" />
            {title}
          </DialogTitle>
          <DialogDescription>
            {description}
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col space-y-4">
          <div className="bg-gradient-to-r from-slate-800 to-slate-900 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-2">Why Support Us?</h3>
            <ul className="text-sm text-slate-300 space-y-1">
              <li>🚀 Add new AI features</li>
              <li>🐛 Fix bugs faster</li>
              <li>📚 Improve documentation</li>
              <li>🔧 Maintain infrastructure</li>
            </ul>
          </div>
          
          <iframe
            id="kofiframe"
            src={`https://ko-fi.com/${username}/?hidefeed=true&widget=true&embed=true&preview=true`}
            style={{
              border: 'none',
              width: '100%',
              padding: '4px',
              background: '#f9f9f9',
              borderRadius: '8px'
            }}
            height="712"
            title="Ko-fi Donation Panel"
          />
          
          <div className="text-xs text-slate-500 text-center">
            Powered by Ko-fi • Secure payments via PayPal & Stripe
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

