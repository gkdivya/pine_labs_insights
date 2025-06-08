import { useEffect } from "react";
import { useChat } from "@/hooks/use-chat";
import ChatHeader from "@/components/chat/chat-header";
import ChatMessages from "@/components/chat/chat-messages";
import ChatInput from "@/components/chat/chat-input";
import InsightsSection from "@/components/insights/insights-section";
import { useToast } from "@/hooks/use-toast";

export default function Chat() {
  const { 
    messages, 
    isLoading, 
    isTyping, 
    sendMessage, 
    searchVisible, 
    toggleSearch, 
    searchMessages, 
    searchResults,
    clearSearch,
    error 
  } = useChat();
  
  const { toast } = useToast();

  useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: error,
        variant: "destructive",
      });
    }
  }, [error, toast]);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <ChatHeader 
        searchVisible={searchVisible}
        onToggleSearch={toggleSearch}
        onSearch={searchMessages}
        onClearSearch={clearSearch}
        searchResults={searchResults}
      />
      
      <InsightsSection />
      
      <div className="flex-1 flex flex-col min-h-0">
        <ChatMessages 
          messages={searchResults || messages}
          isLoading={isLoading}
          isTyping={isTyping}
          isSearchMode={!!searchResults}
        />
        
        <ChatInput 
          onSendMessage={sendMessage}
          disabled={isLoading}
        />
      </div>
    </div>
  );
}
