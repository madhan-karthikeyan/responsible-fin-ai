export function LoadingBubble() {
  return (
    <div className="flex justify-start animate-slide-in-left">
      <div className="max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 bg-slate-800/80 border border-slate-700/50 mr-12 backdrop-blur-sm shadow-lg">
        <div className="flex items-center gap-2 mb-2 text-xs text-slate-400">
          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-emerald-400 to-green-500 flex items-center justify-center text-sm animate-glow">
            🤖
          </div>
          <span>AI Financial Advisor</span>
        </div>

        <div className="flex flex-col gap-3 py-2">
          <div className="flex items-center gap-2">
            <span className="text-slate-300 text-sm">Analyzing your request</span>
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-wave" style={{ animationDelay: "0ms" }}></div>
              <div
                className="w-2 h-2 bg-emerald-400 rounded-full animate-wave"
                style={{ animationDelay: "200ms" }}
              ></div>
              <div
                className="w-2 h-2 bg-emerald-400 rounded-full animate-wave"
                style={{ animationDelay: "400ms" }}
              ></div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="h-1 bg-gradient-to-r from-emerald-400/20 to-emerald-400/60 rounded-full overflow-hidden relative w-24">
              <div className="h-full bg-emerald-400 rounded-full animate-typing"></div>
            </div>
            <span className="text-xs text-slate-500">Processing financial data...</span>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-500">
            <div className="w-4 h-4 border-2 border-emerald-400/30 border-t-emerald-400 rounded-full animate-spin"></div>
            <span>Generating insights</span>
          </div>
        </div>
      </div>
    </div>
  )
}
