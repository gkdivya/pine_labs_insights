import { useEffect, useRef } from "react";
import MessageBubble from "./message-bubble";
import TypingIndicator from "./typing-indicator";
import QuickReplies from "./quick-replies";
import { Skeleton } from "@/components/ui/skeleton";
import type { Message } from "@shared/schema";

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
  isTyping: boolean;
  isSearchMode?: boolean;
}

export default function ChatMessages({ 
  messages, 
  isLoading, 
  isTyping, 
  isSearchMode = false 
}: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (!isSearchMode) {
      scrollToBottom();
    }
  }, [messages, isTyping, isSearchMode]);

  if (isLoading && messages.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-scroll" ref={containerRef}>
        <div className="flex items-start space-x-3">
          <Skeleton className="w-8 h-8 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-64" />
            <Skeleton className="h-4 w-48" />
          </div>
        </div>
      </div>
    );
  }

  const showWelcome = messages.length === 0 && !isLoading;
  const showQuickReplies = messages.length <= 1 && !isSearchMode;

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-scroll" ref={containerRef}>
      {showWelcome && (
        <>
          <MessageBubble
            message={{
              id: 0,
              content: "Hello! I'm your Pine Labs Assistant. I'm here to help you with merchant services, payment processing, and any questions about your Pine Labs account. How can I assist you today?",
              sender: "bot",
              timestamp: new Date(),
              sessionId: "",
            }}
          />
          {showQuickReplies && <QuickReplies />}
        </>
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isTyping && <TypingIndicator />}
      
      <div ref={messagesEndRef} />
    </div>
  );
}
