import { Bot, User } from "lucide-react";
import { format } from "date-fns";
import type { Message } from "@shared/schema";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isBot = message.sender === "bot";
  const timestamp = format(new Date(message.timestamp), "h:mm a");

  if (isBot) {
    return (
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 bg-pine-blue rounded-full flex items-center justify-center flex-shrink-0">
          <Bot className="text-white w-4 h-4" />
        </div>
        <div className="max-w-xs lg:max-w-md">
          <div className="bg-white rounded-lg px-4 py-3 shadow-sm border border-gray-200">
            <div className="text-gray-800 whitespace-pre-wrap">{message.content}</div>
          </div>
          <p className="text-xs text-gray-500 mt-1">{timestamp}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start space-x-3 justify-end">
      <div className="max-w-xs lg:max-w-md">
        <div className="bg-pine-blue rounded-lg px-4 py-3 shadow-sm">
          <div className="text-white whitespace-pre-wrap">{message.content}</div>
        </div>
        <p className="text-xs text-gray-500 mt-1 text-right">{timestamp}</p>
      </div>
      <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
        <User className="text-gray-600 w-4 h-4" />
      </div>
    </div>
  );
}
