"use client"

import { useState, useRef, useEffect } from "react"
import { ChatBubble } from "@/components/chat-bubble"
import { ChatInput } from "@/components/chat-input"
import { LoadingBubble } from "@/components/loading-bubble"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content:
        "Hello! I'm your AI Financial Advisor. I'm here to help you with investment strategies, budgeting, retirement planning, and all your financial questions. How can I assist you today?",
      isUser: false,
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // TODO: Replace with your actual API endpoint
      const API_URL = "https://qcwwmcfr-8000.inc1.devtunnels.ms/query" // <-- PASTE YOUR API URL HERE

      console.log("[v0] Attempting to fetch from:", API_URL)
      console.log("[v0] Sending query:", content)

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: content }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log("[v0] Received response:", data)

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.answer,
        isUser: false,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      console.error("[v0] Error sending message:", error)

      const demoResponses = [
        "Based on your question about budgeting, I'd recommend following the 50/30/20 rule: allocate 50% of your income to needs, 30% to wants, and 20% to savings and debt repayment. This provides a solid foundation for financial stability.",
        "For investment strategies, consider diversifying your portfolio across different asset classes. A mix of index funds, bonds, and perhaps some individual stocks can help balance risk and potential returns based on your risk tolerance.",
        "Regarding retirement planning, it's generally recommended to save at least 10-15% of your income for retirement. Take advantage of employer 401(k) matching if available, as it's essentially free money.",
        "Emergency funds are crucial for financial security. Aim to save 3-6 months of living expenses in a high-yield savings account for unexpected situations.",
        "When considering debt management, prioritize high-interest debt first (like credit cards) while maintaining minimum payments on other debts. This strategy minimizes total interest paid over time.",
      ]

      const randomResponse = demoResponses[Math.floor(Math.random() * demoResponses.length)]

      const demoMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `**Demo Mode**: ${randomResponse}\n\n*Note: This is a demo response. To connect to your actual financial AI, please update the API_URL in the code with your endpoint.*`,
        isUser: false,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, demoMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="flex items-center justify-center py-6 px-4 border-b border-border/20 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-emerald-400 to-green-600 flex items-center justify-center text-2xl">
            💰
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-green-600 bg-clip-text text-transparent">
            AI Financial Advisor
          </h1>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <ChatBubble
              key={message.id}
              message={message.content}
              isUser={message.isUser}
              timestamp={message.timestamp}
            />
          ))}
          {isLoading && <LoadingBubble />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Chat Input */}
      <div className="border-t border-border/20 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto p-4">
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  )
}
