import { messages, chatSessions, type Message, type InsertMessage, type ChatSession, type InsertChatSession, users, type User, type InsertUser } from "@shared/schema";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  createChatSession(session: InsertChatSession): Promise<ChatSession>;
  getChatSession(sessionId: string): Promise<ChatSession | undefined>;
  updateSessionActivity(sessionId: string): Promise<void>;
  
  createMessage(message: InsertMessage): Promise<Message>;
  getMessagesBySession(sessionId: string): Promise<Message[]>;
  searchMessages(sessionId: string, query: string): Promise<Message[]>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private messages: Map<number, Message>;
  private chatSessions: Map<string, ChatSession>;
  private currentUserId: number;
  private currentMessageId: number;
  private currentSessionId: number;

  constructor() {
    this.users = new Map();
    this.messages = new Map();
    this.chatSessions = new Map();
    this.currentUserId = 1;
    this.currentMessageId = 1;
    this.currentSessionId = 1;
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async createChatSession(insertSession: InsertChatSession): Promise<ChatSession> {
    const id = this.currentSessionId++;
    const now = new Date();
    const session: ChatSession = {
      id,
      sessionId: insertSession.sessionId,
      createdAt: now,
      lastActivity: now,
    };
    this.chatSessions.set(insertSession.sessionId, session);
    return session;
  }

  async getChatSession(sessionId: string): Promise<ChatSession | undefined> {
    return this.chatSessions.get(sessionId);
  }

  async updateSessionActivity(sessionId: string): Promise<void> {
    const session = this.chatSessions.get(sessionId);
    if (session) {
      session.lastActivity = new Date();
      this.chatSessions.set(sessionId, session);
    }
  }

  async createMessage(insertMessage: InsertMessage): Promise<Message> {
    const id = this.currentMessageId++;
    const message: Message = {
      id,
      content: insertMessage.content,
      sender: insertMessage.sender,
      sessionId: insertMessage.sessionId,
      timestamp: new Date(),
    };
    this.messages.set(id, message);
    return message;
  }

  async getMessagesBySession(sessionId: string): Promise<Message[]> {
    return Array.from(this.messages.values())
      .filter((message) => message.sessionId === sessionId)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  async searchMessages(sessionId: string, query: string): Promise<Message[]> {
    const sessionMessages = await this.getMessagesBySession(sessionId);
    return sessionMessages.filter((message) =>
      message.content.toLowerCase().includes(query.toLowerCase())
    );
  }
}

export const storage = new MemStorage();
