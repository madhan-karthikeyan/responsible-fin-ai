import { cn } from "@/lib/utils"

interface ChatBubbleProps {
  message: string
  isUser: boolean
  timestamp: Date
}

export function ChatBubble({ message, isUser, timestamp }: ChatBubbleProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    })
  }

  return (
    <div
      className={cn(
        "flex w-full mb-4",
        isUser ? "justify-end animate-slide-in-right" : "justify-start animate-slide-in-left",
      )}
    >
      <div
        className={cn(
          "max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 shadow-lg",
          isUser
            ? "bg-gradient-to-r from-emerald-400 to-green-600 text-slate-900 ml-12" // Updated user message colors from yellow to emerald/green gradient
            : "bg-slate-800/80 text-slate-100 border border-slate-700/50 mr-12 backdrop-blur-sm",
        )}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-2 text-xs text-slate-400">
            <div className="w-6 h-6 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 flex items-center justify-center text-sm">
              🤖
            </div>
            <span>AI Financial Advisor</span>
          </div>
        )}

        <div className={cn("text-sm leading-relaxed", isUser ? "font-medium" : "text-slate-200")}>
          {message.split("\n").map((line, index) => (
            <p key={index} className={index > 0 ? "mt-2" : ""}>
              {line}
            </p>
          ))}
        </div>

        <div className={cn("text-xs mt-2 opacity-70", isUser ? "text-slate-800" : "text-slate-400")}>
          {formatTime(timestamp)}
        </div>
      </div>
    </div>
  )
}
