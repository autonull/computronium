/** WebSocket client with MessageRouter for self-registering handlers (TODO68). */

export type WSHandler = (data: any) => void | Promise<void>;

export interface WSMessage {
  type: string;
  [key: string]: any;
}

type ConnectionState =
  "disconnected" | "connecting" | "connected" | "reconnecting";

/**
 * MessageRouter - Components self-register handlers for message types.
 * Zero boilerplate in main.ts — components declare their own dependencies.
 * Buffers messages for types without handlers until handlers register.
 */
export class MessageRouter {
  private handlers: Map<string, Set<WSHandler>> = new Map();
  private onceHandlers: Map<string, Set<WSHandler>> = new Map();
  private messageBuffer: Map<string, WSMessage[]> = new Map();

  /** Register a handler for a message type. Returns unregister function. */
  register(type: string, handler: WSHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
      // Flush any buffered messages for this type
      const buffered = this.messageBuffer.get(type);
      if (buffered) {
        buffered.forEach((msg) => Promise.resolve(handler(msg)));
        this.messageBuffer.delete(type);
      }
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

  /** Buffer a message for later delivery when handler registers. */
  buffer(message: WSMessage): void {
    const { type } = message;
    if (!this.messageBuffer.has(type)) {
      this.messageBuffer.set(type, []);
    }
    this.messageBuffer.get(type)!.push(message);
  }

  /** Dispatch a message to all registered handlers, or buffer if none. */
  async dispatch(message: WSMessage): Promise<void> {
    const { type, ...data } = message;

    // Regular handlers
    const handlers = this.handlers.get(type);
    if (handlers && handlers.size > 0) {
      await Promise.all(
        Array.from(handlers).map((h) => Promise.resolve(h(data))),
      );
      return;
    }

    // One-time handlers
    const onceHandlers = this.onceHandlers.get(type);
    if (onceHandlers && onceHandlers.size > 0) {
      await Promise.all(
        Array.from(onceHandlers).map((h) => Promise.resolve(h(data))),
      );
      this.onceHandlers.delete(type);
      return;
    }

    // No handlers yet — buffer for later
    this.buffer(message);
  }

  /** Clear all handlers and buffers. */
  clear(): void {
    this.handlers.clear();
    this.onceHandlers.clear();
    this.messageBuffer.clear();
  }

  /** Get buffered messages for a type (for debugging). */
  getBuffered(type: string): WSMessage[] {
    return this.messageBuffer.get(type) ?? [];
  }

  /** Check if a message type has active handlers. */
  hasHandlers(type: string): boolean {
    return (this.handlers.get(type)?.size ?? 0) > 0;
  }
}

/**
 * WebSocket client with auto-reconnect, connection state, heartbeat, and MessageRouter integration.
 */
export class WSClient {
  private ws: WebSocket | null = null;
  private url: string;
  private router: MessageRouter;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private reconnectAttempts = 0;
  private shouldReconnect = true;
  private state: ConnectionState = "disconnected";
  private stateListeners: Set<(state: ConnectionState) => void> = new Set();
  private messageQueue: WSMessage[] = [];
  private heartbeatInterval: number | null = null;
  private lastPong = 0;
  private missedPongs = 0;
  private readonly maxMissedPongs = 3;
  private readonly heartbeatIntervalMs = 15000;

  constructor(url: string, router: MessageRouter) {
    this.url = url;
    this.router = router;
  }

  /** Current connection state. */
  get connectionState(): ConnectionState {
    return this.state;
  }

  /** Subscribe to connection state changes. Returns unsubscribe function. */
  onStateChange(listener: (state: ConnectionState) => void): () => void {
    this.stateListeners.add(listener);
    // Immediately notify with current state
    listener(this.state);
    return () => this.stateListeners.delete(listener);
  }

  private setState(state: ConnectionState): void {
    if (this.state === state) return;
    const oldState = this.state;
    this.state = state;
    console.log(`[WS] State: ${oldState} → ${state}`);
    this.stateListeners.forEach((l) => l(state));
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    if (this.state === "connecting") return;

    this.setState("connecting");

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}${this.url}`;

    this.ws = new WebSocket(wsUrl);
    this.ws.binaryType = "arraybuffer";

    this.ws.onopen = () => {
      console.log("[WS] Connected");
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      this.missedPongs = 0;
      this.lastPong = Date.now();
      this.setState("connected");
      this.startHeartbeat();
      // Flush any queued messages
      this.flushQueue();
    };

    this.ws.onmessage = async (event) => {
      try {
        const message = JSON.parse(event.data);
        // Handle pong messages
        if (message.type === "pong") {
          this.lastPong = Date.now();
          this.missedPongs = 0;
          return;
        }
        await this.router.dispatch(message);
      } catch (e) {
        console.error("[WS] Failed to parse message:", e);
      }
    };

    this.ws.onclose = (event) => {
      console.log("[WS] Disconnected:", event.code, event.reason);
      this.stopHeartbeat();
      this.setState("disconnected");
      if (this.shouldReconnect) this.scheduleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error("[WS] Error:", err);
    };
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.missedPongs++;
        if (this.missedPongs > this.maxMissedPongs) {
          console.warn("[WS] Heartbeat failed - closing connection");
          this.ws.close(1000, "Heartbeat timeout");
          return;
        }
        this.ws.send(JSON.stringify({ type: "ping" }));
      }
    }, this.heartbeatIntervalMs);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval !== null) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.state === "reconnecting") return;
    this.setState("reconnecting");
    // Exponential backoff with jitter (±25%)
    const baseDelay = Math.min(
      this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts),
      this.maxReconnectDelay,
    );
    const jitter = baseDelay * 0.25 * (Math.random() * 2 - 1);
    const delay = Math.max(100, baseDelay + jitter);
    this.reconnectAttempts++;
    console.log(
      `[WS] Reconnecting in ${Math.round(delay)}ms (attempt ${this.reconnectAttempts})`,
    );
    setTimeout(() => this.connect(), delay);
  }

  /** Queue a message to send when connected. */
  send(message: WSMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }

  private flushQueue(): void {
    while (
      this.messageQueue.length > 0 &&
      this.ws?.readyState === WebSocket.OPEN
    ) {
      const msg = this.messageQueue.shift()!;
      this.ws.send(JSON.stringify(msg));
    }
  }

  /** Send a message with optional response handling. */
  async request(message: WSMessage, timeoutMs = 5000): Promise<any> {
    return new Promise((resolve, reject) => {
      const requestId = `${message.type}_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
      const messageWithId = { ...message, request_id: requestId };

      const unsubscribe = this.router.once(requestId, (response) => {
        clearTimeout(timer);
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.data);
        }
      });

      const timer = setTimeout(() => {
        unsubscribe();
        reject(new Error(`Request timeout: ${message.type}`));
      }, timeoutMs);

      this.send(messageWithId);
    });
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.stopHeartbeat();
    this.ws?.close(1000, "Client disconnect");
    this.ws = null;
    this.setState("disconnected");
  }

  /** Wait for connection (with optional timeout). */
  async waitForConnection(timeoutMs = 10000): Promise<boolean> {
    if (this.state === "connected") return true;
    return new Promise((resolve) => {
      const timer = setTimeout(() => {
        unsubscribe();
        resolve(false);
      }, timeoutMs);
      const unsubscribe = this.onStateChange((state) => {
        if (state === "connected") {
          clearTimeout(timer);
          unsubscribe();
          resolve(true);
        }
      });
    });
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /** Get connection quality metrics. */
  getConnectionQuality(): {
    state: ConnectionState;
    latency: number;
    missedPongs: number;
  } {
    return {
      state: this.state,
      latency: this.lastPong ? Date.now() - this.lastPong : -1,
      missedPongs: this.missedPongs,
    };
  }
}

// Global router instance for components to import
export const router = new MessageRouter();

// Global WSClient instance
export const wsClient = new WSClient("/ws", router);
