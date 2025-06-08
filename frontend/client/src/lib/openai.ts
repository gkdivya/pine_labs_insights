// This file would contain OpenAI integration but since this is client-side,
// all OpenAI calls are handled on the server in routes.ts
// This file is kept for potential future client-side integrations

export const openaiConfig = {
  model: "gpt-4o", // the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
  maxTokens: 500,
  temperature: 0.7,
};

export type OpenAIMessage = {
  role: "system" | "user" | "assistant";
  content: string;
};
