"use client"

import { useState, type KeyboardEvent } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send } from "lucide-react"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [message, setMessage] = useState("")

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage("")
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex gap-3 items-end">
      <div className="flex-1">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about investments, budgeting, retirement planning, or any financial question..."
          className="min-h-[60px] max-h-[120px] resize-none bg-slate-800/50 border-slate-700/50 text-slate-100 placeholder:text-slate-400 focus:border-emerald-400/50 focus:ring-emerald-400/20 backdrop-blur-sm"
          disabled={disabled}
        />
      </div>
      <Button
        onClick={handleSend}
        disabled={!message.trim() || disabled}
        className="h-[60px] px-6 bg-gradient-to-r from-emerald-400 to-green-600 hover:from-emerald-500 hover:to-green-700 text-slate-900 font-medium shadow-lg hover:shadow-xl transition-all duration-200"
      >
        <Send className="w-5 h-5" />
      </Button>
    </div>
  )
}
