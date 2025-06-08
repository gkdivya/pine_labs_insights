import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertMessageSchema, insertChatSessionSchema } from "@shared/schema";
import OpenAI from "openai";
import { pinelabsKnowledgeBase } from "../client/src/lib/pinelabs-knowledge";

// the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY_ENV_VAR || "default_key",
});

export async function registerRoutes(app: Express): Promise<Server> {
  // Create or get chat session
  app.post("/api/chat/session", async (req, res) => {
    try {
      const { sessionId } = req.body;
      
      let session = await storage.getChatSession(sessionId);
      if (!session) {
        session = await storage.createChatSession({ sessionId });
      } else {
        await storage.updateSessionActivity(sessionId);
      }
      
      res.json(session);
    } catch (error) {
      res.status(500).json({ error: "Failed to create or get session" });
    }
  });

  // Get messages for a session
  app.get("/api/chat/:sessionId/messages", async (req, res) => {
    try {
      const { sessionId } = req.params;
      const messages = await storage.getMessagesBySession(sessionId);
      res.json(messages);
    } catch (error) {
      res.status(500).json({ error: "Failed to get messages" });
    }
  });

  // Search messages
  app.get("/api/chat/:sessionId/search", async (req, res) => {
    try {
      const { sessionId } = req.params;
      const { q } = req.query;
      
      if (!q || typeof q !== 'string') {
        return res.status(400).json({ error: "Search query is required" });
      }
      
      const messages = await storage.searchMessages(sessionId, q);
      res.json(messages);
    } catch (error) {
      res.status(500).json({ error: "Failed to search messages" });
    }
  });

  // Get weekly insights
  app.get("/api/insights/weekly", async (req, res) => {
    try {
      // Mock data for demonstration - in production this would come from Pine Labs API or database
      const insights = {
        totalTransactions: 1247,
        transactionChange: 12.5,
        totalRevenue: 89650,
        revenueChange: 8.3,
        activeCustomers: 342,
        customerChange: 15.2,
        failureRate: 2.1,
        failureChange: -0.8,
        topPaymentMethod: "UPI",
        averageTicket: 719
      };
      
      res.json(insights);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch insights" });
    }
  });

  // Send message and get AI response
  app.post("/api/chat/:sessionId/message", async (req, res) => {
    try {
      const { sessionId } = req.params;
      const messageData = insertMessageSchema.parse(req.body);
      
      // Update session activity
      await storage.updateSessionActivity(sessionId);
      
      // Save user message
      const userMessage = await storage.createMessage({
        ...messageData,
        sessionId,
      });
      
      // Generate AI response
      try {
        const botResponse = await generateAIResponse(messageData.content, sessionId);
        
        // Save bot message
        const botMessage = await storage.createMessage({
          content: botResponse,
          sender: "bot",
          sessionId,
        });
        
        res.json({
          userMessage,
          botMessage,
        });
      } catch (aiError) {
        // If AI fails, provide a fallback response
        const fallbackResponse = getFallbackResponse(messageData.content);
        const botMessage = await storage.createMessage({
          content: fallbackResponse,
          sender: "bot",
          sessionId,
        });
        
        res.json({
          userMessage,
          botMessage,
        });
      }
    } catch (error) {
      res.status(500).json({ error: "Failed to send message" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}

async function generateAIResponse(userMessage: string, sessionId: string): Promise<string> {
  // Get recent conversation context
  const recentMessages = await storage.getMessagesBySession(sessionId);
  const context = recentMessages.slice(-10).map(msg => 
    `${msg.sender}: ${msg.content}`
  ).join('\n');

  const knowledgeContext = pinelabsKnowledgeBase.getRelevantInfo(userMessage);
  
  const systemPrompt = `You are a Pine Labs customer support assistant helping merchants with their payment processing needs. 

Use this Pine Labs knowledge base information to answer questions:
${knowledgeContext}

Guidelines:
- Be helpful, professional, and concise
- Focus on Pine Labs specific information
- If you don't know something specific, offer to connect them with support
- Always maintain a supportive tone for merchant success
- Provide step-by-step guidance when possible

Recent conversation context:
${context}

Respond in a helpful, professional manner as a Pine Labs support assistant.`;

  const response = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: userMessage }
    ],
    max_tokens: 500,
    temperature: 0.7,
  });

  return response.choices[0].message.content || "I'm sorry, I couldn't generate a response. Please try again or contact our support team.";
}

function getFallbackResponse(userMessage: string): string {
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('transaction') || lowerMessage.includes('payment')) {
    return "I can help you with transaction-related queries. You can view your transaction history in the Pine Labs merchant dashboard under the 'Transactions' section. For specific issues, please contact our support team at 1800-XXX-XXXX.";
  }
  
  if (lowerMessage.includes('settlement') || lowerMessage.includes('money')) {
    return "Settlement typically occurs within 1-2 business days for most transactions. UPI settlements are usually faster, often same-day. You can track your settlements in the merchant dashboard.";
  }
  
  if (lowerMessage.includes('refund')) {
    return "To process a refund, go to your transaction history, find the specific transaction, and click 'Refund'. The amount will be credited back to the customer within 5-7 business days.";
  }
  
  if (lowerMessage.includes('commission') || lowerMessage.includes('rate') || lowerMessage.includes('fee')) {
    return "Commission rates vary by payment method: Credit Cards (1.8%-2.5%), Debit Cards (0.9%-1.2%), UPI (0%-0.5%). Your specific rates depend on your merchant category and monthly volume. Check your merchant dashboard for exact rates.";
  }
  
  return "I'm here to help you with your Pine Labs merchant services. For detailed assistance, please contact our support team at 1800-XXX-XXXX or email support@pinelabs.com. We're available 24/7 to assist you.";
}
