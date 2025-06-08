import { Button } from "@/components/ui/button";

const QUICK_REPLIES = [
  "How do I check my transaction history?",
  "What are the settlement timings?",
  "How to resolve payment failures?"
];

interface QuickRepliesProps {
  onReply?: (message: string) => void;
}

export default function QuickReplies({ onReply }: QuickRepliesProps) {
  const handleReply = (message: string) => {
    if (onReply) {
      onReply(message);
    }
  };

  return (
    <div className="flex flex-wrap gap-2 ml-11">
      {QUICK_REPLIES.map((reply, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          onClick={() => handleReply(reply)}
          className="bg-pine-light text-pine-dark hover:bg-blue-100 border-blue-200 text-sm"
        >
          {reply.replace("How do I check my ", "").replace("What are the ", "").replace("How to resolve ", "")}
        </Button>
      ))}
    </div>
  );
}
