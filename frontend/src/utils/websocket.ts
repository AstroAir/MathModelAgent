type MessageHandler = (data: any) => void;
type ConnectionStateHandler = (state: 'connecting' | 'connected' | 'disconnected' | 'error') => void;

export class TaskWebSocket {
  private socket: WebSocket | null = null;
  private url: string;
  private onMessage: MessageHandler;
  private onConnectionStateChange?: ConnectionStateHandler;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // 初始延迟 1 秒
  private reconnectTimer: number | null = null;
  private shouldReconnect = true;
  private heartbeatTimer: number | null = null;
  private heartbeatInterval = 30000; // 30 秒心跳

  constructor(
    url: string,
    onMessage: MessageHandler,
    onConnectionStateChange?: ConnectionStateHandler
  ) {
    this.url = url;
    this.onMessage = onMessage;
    this.onConnectionStateChange = onConnectionStateChange;
  }

  connect() {
    try {
      this.notifyStateChange('connecting');
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        console.log("WebSocket 连接已建立");
        this.reconnectAttempts = 0; // 重置重连计数
        this.reconnectDelay = 1000;
        this.notifyStateChange('connected');
        this.startHeartbeat();
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessage(data);
        } catch (error) {
          console.error("解析 WebSocket 消息失败:", error);
        }
      };

      this.socket.onclose = (event) => {
        console.log("WebSocket 连接已关闭", event.code, event.reason);
        this.stopHeartbeat();
        this.notifyStateChange('disconnected');

        if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.error("WebSocket 重连次数已达上限");
          this.notifyStateChange('error');
        }
      };

      this.socket.onerror = (error) => {
        console.error("WebSocket 错误:", error);
        this.notifyStateChange('error');
      };
    } catch (error) {
      console.error("WebSocket 连接失败:", error);
      this.notifyStateChange('error');
      if (this.shouldReconnect) {
        this.scheduleReconnect();
      }
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectAttempts++;
    // 指数退避算法，最大延迟 30 秒
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      30000
    );

    console.log(`将在 ${delay}ms 后尝试第 ${this.reconnectAttempts} 次重连...`);

    this.reconnectTimer = window.setTimeout(() => {
      console.log(`正在尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      this.connect();
    }, delay);
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = window.setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        // 发送心跳包
        this.send({ type: 'ping' });
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private notifyStateChange(state: 'connecting' | 'connected' | 'disconnected' | 'error') {
    if (this.onConnectionStateChange) {
      this.onConnectionStateChange(state);
    }
  }

  send(data: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.warn("WebSocket 未连接，无法发送消息");
    }
  }

  close() {
    this.shouldReconnect = false; // 禁用自动重连
    this.stopHeartbeat();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    if (this.socket) {
      this.socket.close();
    }
  }

  // 获取当前连接状态
  getReadyState(): number {
    return this.socket?.readyState ?? WebSocket.CLOSED;
  }
}
