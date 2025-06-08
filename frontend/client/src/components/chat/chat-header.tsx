import { useState } from "react";
import { Search, MoreVertical, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Message } from "@shared/schema";

interface ChatHeaderProps {
  searchVisible: boolean;
  onToggleSearch: () => void;
  onSearch: (query: string) => void;
  onClearSearch: () => void;
  searchResults?: Message[] | null;
}

export default function ChatHeader({ 
  searchVisible, 
  onToggleSearch, 
  onSearch, 
  onClearSearch,
  searchResults 
}: ChatHeaderProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery.trim());
    } else {
      onClearSearch();
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    
    if (!value.trim()) {
      onClearSearch();
    }
  };

  return (
    <>
      {/* Main Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-pine-blue rounded-full flex items-center justify-center">
            <Bot className="text-white w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Pine Labs Assistant</h1>
            <p className="text-sm text-gray-500">Online • Ready to help</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleSearch}
            className="text-gray-500 hover:text-gray-700"
          >
            <Search className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-gray-500 hover:text-gray-700"
          >
            <MoreVertical className="w-4 h-4" />
          </Button>
        </div>
      </header>

      {/* Search Bar */}
      {searchVisible && (
        <div className="bg-white border-b border-gray-200 px-4 py-3">
          <form onSubmit={handleSearchSubmit} className="relative">
            <Input
              type="text"
              placeholder="Search chat history..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="pl-10 pr-4"
              autoFocus
            />
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
          </form>
          {searchResults && (
            <p className="text-xs text-gray-500 mt-2">
              Found {searchResults.length} message{searchResults.length !== 1 ? 's' : ''}
            </p>
          )}
        </div>
      )}
    </>
  );
}
