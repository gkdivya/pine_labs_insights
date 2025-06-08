import { Bot } from "lucide-react";

export default function TypingIndicator() {
  return (
    <div className="flex items-start space-x-3">
      <div className="w-8 h-8 bg-pine-blue rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="text-white w-4 h-4" />
      </div>
      <div className="bg-white rounded-lg px-4 py-3 shadow-sm border border-gray-200">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce animate-bounce-delay-1"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce animate-bounce-delay-2"></div>
        </div>
      </div>
    </div>
  );
}
