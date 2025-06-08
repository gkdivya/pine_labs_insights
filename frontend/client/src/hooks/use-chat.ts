import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import type { Message } from "@shared/schema";

// Generate a unique session ID for this chat session
const generateSessionId = () => {
  return `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export function useChat() {
  const [sessionId] = useState(() => generateSessionId());
  const [isTyping, setIsTyping] = useState(false);
  const [searchVisible, setSearchVisible] = useState(false);
  const [searchResults, setSearchResults] = useState<Message[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const queryClient = useQueryClient();

  // Initialize session
  const { mutate: initSession } = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("POST", "/api/chat/session", { sessionId });
      return response.json();
    },
    onError: (error) => {
      setError("Failed to initialize chat session. Please refresh the page.");
    },
  });

  // Get messages for the session
  const { 
    data: messages = [], 
    isLoading, 
    error: messagesError 
  } = useQuery({
    queryKey: ["/api/chat", sessionId, "messages"],
    enabled: !!sessionId,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      setIsTyping(true);
      setError(null);
      
      const response = await apiRequest("POST", `/api/chat/${sessionId}/message`, {
        content,
        sender: "user",
      });
      return response.json();
    },
    onSuccess: () => {
      // Invalidate and refetch messages
      queryClient.invalidateQueries({ queryKey: ["/api/chat", sessionId, "messages"] });
      setIsTyping(false);
    },
    onError: (error) => {
      setIsTyping(false);
      setError("Failed to send message. Please try again.");
    },
  });

  // Search messages mutation
  const searchMessagesMutation = useMutation({
    mutationFn: async (query: string) => {
      const response = await apiRequest("GET", `/api/chat/${sessionId}/search?q=${encodeURIComponent(query)}`);
      return response.json();
    },
    onSuccess: (results) => {
      setSearchResults(results);
    },
    onError: (error) => {
      setError("Failed to search messages. Please try again.");
    },
  });

  // Initialize session on mount
  useEffect(() => {
    initSession();
  }, []);

  // Handle messages error
  useEffect(() => {
    if (messagesError) {
      setError("Failed to load messages. Please refresh the page.");
    }
  }, [messagesError]);

  const sendMessage = (content: string) => {
    sendMessageMutation.mutate(content);
  };

  const toggleSearch = () => {
    setSearchVisible(!searchVisible);
    if (searchVisible) {
      setSearchResults(null);
    }
  };

  const searchMessages = (query: string) => {
    if (query.trim()) {
      searchMessagesMutation.mutate(query);
    } else {
      setSearchResults(null);
    }
  };

  const clearSearch = () => {
    setSearchResults(null);
  };

  return {
    sessionId,
    messages,
    isLoading,
    isTyping,
    sendMessage,
    searchVisible,
    toggleSearch,
    searchMessages,
    searchResults,
    clearSearch,
    error,
  };
}
