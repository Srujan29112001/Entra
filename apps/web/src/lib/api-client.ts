/**
 * API client for backend communication with streaming support.
 */

export interface StreamEventHandler {
  onStart?: () => void;
  onStatus?: (message: string) => void;
  onAgent?: (agentType: string) => void;
  onContent?: (content: string) => void;
  onDone?: (metadata: any) => void;
  onError?: (error: string) => void;
}

export class APIClient {
  private baseURL: string;

  constructor(baseURL: string = "http://localhost:8000") {
    this.baseURL = baseURL;
  }

  /**
   * Stream chat responses from backend.
   */
  async streamChat(
    userId: string,
    companyId: string,
    message: string,
    handlers: StreamEventHandler
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          company_id: companyId,
          message: message,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            try {
              const event = JSON.parse(data);

              switch (event.type) {
                case "start":
                  handlers.onStart?.();
                  break;
                case "status":
                  handlers.onStatus?.(event.message);
                  break;
                case "agent":
                  handlers.onAgent?.(event.agent_type);
                  break;
                case "content":
                  handlers.onContent?.(event.content);
                  break;
                case "done":
                  handlers.onDone?.(event.metadata);
                  break;
                case "error":
                  handlers.onError?.(event.message);
                  break;
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      handlers.onError?.(error instanceof Error ? error.message : "Unknown error");
    }
  }

  /**
   * Regular (non-streaming) chat request.
   */
  async chat(userId: string, companyId: string, message: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/v1/chat/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: userId,
        company_id: companyId,
        message: message,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Upload document for RAG ingestion.
   */
  async uploadDocument(
    file: File,
    companyId: string,
    userId: string,
    documentType: string
  ): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("company_id", companyId);
    formData.append("user_id", userId);
    formData.append("document_type", documentType);

    const response = await fetch(`${this.baseURL}/api/v1/documents/ingest`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Invoke specific agent directly.
   */
  async invokeAgent(
    agentType: string,
    question: string,
    userId: string,
    companyId: string,
    context?: any
  ): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/v1/agents/invoke/${agentType}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        task_id: crypto.randomUUID(),
        agent_type: agentType,
        question: question,
        user_id: userId,
        company_id: companyId,
        context: context || {},
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

// Export singleton instance
export const apiClient = new APIClient(
  process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000"
);
