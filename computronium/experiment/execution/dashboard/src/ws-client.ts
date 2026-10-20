/** WebSocket client with MessageRouter for self-registering handlers (TODO68). */

export type WSHandler = (data: any) => void | Promise<void>;

export interface WSMessage {
  type: string;
  [key: string]: any;
}

/**
 * MessageRouter - Components self-register handlers for message types.
 * Zero boilerplate in main.ts — components declare their own dependencies.
 */
export class MessageRouter {
  private handlers: Map<string, Set<WSHandler>> = new Map();
  private onceHandlers: Map<string, Set<WSHandler>> = new Map();

  /** Register a handler for a message type. Returns unregister function. */
  register(type: string, handler: WSHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
    return () => this.unregister(type, handler);
  }

  /** Register a one-time handler. */
  once(type: string, handler: WSHandler): () => void {
    if (!this.onceHandlers.has(type)) {
      this.onceHandlers.set(type, new Set());
    }
    this.onceHandlers.get(type)!.add(handler);
    return () => this.unregisterOnce(type, handler);
  }

  /** Public unregister for external use (e.g., component cleanup). */
  unregister(type: string, handler: WSHandler): void {
    this.handlers.get(type)?.delete(handler);
  }

  unregisterOnce(type: string, handler: WSHandler): void {
    this.onceHandlers.get(type)?.delete(handler);
  }

  /** Dispatch a message to all registered handlers. */
  async dispatch(message: WSMessage): Promise<void> {
    const { type, ...data } = message;

    // Regular handlers
    const handlers = this.handlers.get(type);
    if (handlers) {
      await Promise.all(
        Array.from(handlers).map((h) => Promise.resolve(h(data))),
      );
    }

    // One-time handlers
    const onceHandlers = this.onceHandlers.get(type);
    if (onceHandlers) {
      await Promise.all(
        Array.from(onceHandlers).map((h) => Promise.resolve(h(data))),
      );
      this.onceHandlers.delete(type);
    }
  }

  /** Clear all handlers. */
  clear(): void {
    this.handlers.clear();
    this.onceHandlers.clear();
  }
}

/**
 * WebSocket client with auto-reconnect and MessageRouter integration.
 */
export class WSClient {
  private ws: WebSocket | null = null;
  private url: string;
  private router: MessageRouter;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private reconnectAttempts = 0;
  private shouldReconnect = true;
  private onOpenCallbacks: (() => void)[] = [];
  private onCloseCallbacks: (() => void)[] = [];

  constructor(url: string, router: MessageRouter) {
    this.url = url;
    this.router = router;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}${this.url}`;

    this.ws = new WebSocket(wsUrl);
    this.ws.binaryType = "arraybuffer";

    this.ws.onopen = () => {
      console.log("[WS] Connected");
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      this.onOpenCallbacks.forEach((cb) => cb());
    };

    this.ws.onmessage = async (event) => {
      try {
        const message = JSON.parse(event.data);
        await this.router.dispatch(message);
      } catch (e) {
        console.error("[WS] Failed to parse message:", e);
      }
    };

    this.ws.onclose = () => {
      console.log("[WS] Disconnected");
      this.onCloseCallbacks.forEach((cb) => cb());
      if (this.shouldReconnect) this.scheduleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error("[WS] Error:", err);
    };
  }

  private scheduleReconnect(): void {
    const delay = Math.min(
      this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts),
      this.maxReconnectDelay,
    );
    this.reconnectAttempts++;
    console.log(
      `[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`,
    );
    setTimeout(() => this.connect(), delay);
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.ws?.close();
    this.ws = null;
  }

  send(message: WSMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  onOpen(cb: () => void): () => void {
    this.onOpenCallbacks.push(cb);
    return () => {
      const idx = this.onOpenCallbacks.indexOf(cb);
      if (idx >= 0) this.onOpenCallbacks.splice(idx, 1);
    };
  }

  onClose(cb: () => void): () => void {
    this.onCloseCallbacks.push(cb);
    return () => {
      const idx = this.onCloseCallbacks.indexOf(cb);
      if (idx >= 0) this.onCloseCallbacks.splice(idx, 1);
    };
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Global router instance for components to import
export const router = new MessageRouter();
