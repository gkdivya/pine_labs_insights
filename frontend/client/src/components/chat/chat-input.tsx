import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Paperclip } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const QUICK_SUGGESTIONS = [
  "Show me my recent transactions",
  "Help with refund process", 
  "Contact support team"
];

export default function ChatInput({ onSendMessage, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleQuickSuggestion = (suggestion: string) => {
    if (!disabled) {
      onSendMessage(suggestion);
    }
  };

  const autoResize = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const target = e.target;
    target.style.height = 'auto';
    target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1">
          <div className="relative">
            <Textarea
              value={message}
              onChange={(e) => {
                setMessage(e.target.value);
                autoResize(e);
              }}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="resize-none pr-12 min-h-[44px] auto-resize"
              rows={1}
              disabled={disabled}
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
              disabled={disabled}
            >
              <Paperclip className="w-4 h-4" />
            </Button>
          </div>
        </div>
        <Button
          type="submit"
          size="default"
          className="bg-pine-blue hover:bg-pine-dark text-white"
          disabled={disabled || !message.trim()}
        >
          <Send className="w-4 h-4" />
        </Button>
      </form>

      {/* Quick Suggestions */}
      <div className="mt-3 flex flex-wrap gap-2">
        {QUICK_SUGGESTIONS.map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => handleQuickSuggestion(suggestion)}
            className="text-xs bg-gray-100 text-gray-700 hover:bg-gray-200 border-gray-200"
            disabled={disabled}
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
}
