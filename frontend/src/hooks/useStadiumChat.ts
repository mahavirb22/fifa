/** Chat state management — all API calls live here, components never call fetch. */

import { useCallback, useState } from "react";
import { sendChatMessage } from "../lib/api";
import { getDeviceId } from "../lib/deviceId";
import type { ChatMessage } from "../lib/types";

interface UseStadiumChatReturn {
  messages: ChatMessage[];
  loading: boolean;
  error: string;
  sendMessage: (text: string, language: string) => Promise<void>;
  clearChat: () => void;
}

export function useStadiumChat(): UseStadiumChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const sendMessage = useCallback(async (text: string, language: string) => {
    setError("");
    setLoading(true);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      language,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const response = await sendChatMessage({
        message: text,
        language,
        device_id: getDeviceId(),
      });

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.reply,
        language: response.language,
        source: response.source,
        suggested_actions: response.suggested_actions,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get response");
    } finally {
      setLoading(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError("");
  }, []);

  return { messages, loading, error, sendMessage, clearChat };
}
