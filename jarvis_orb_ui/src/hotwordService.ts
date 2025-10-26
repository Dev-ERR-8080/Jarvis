class HotwordService {
  private ws: WebSocket;

  constructor() {
    this.ws = new WebSocket("ws://localhost:8080");
  }

  onWake(callback: () => void) {
    this.ws.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "wake") {
        callback();
      }
    });
  }
}

export const hotwordService = new HotwordService();
