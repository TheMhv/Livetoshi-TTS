class Queue {
    constructor() {
        this.items = [];
    }

    put(item) {
        this.items.push(item);
        return item;
    }

    get() {
        return this.items.shift();
    }

    isEmpty() {
        return this.items.length === 0;
    }
}

class AudioPlayer {
    static async play(audioSource) {
        const audio = new Audio(audioSource);
        return new Promise((resolve, reject) => {
            audio.onended = resolve;
            audio.onerror = reject;
            audio.play().catch(reject);
        });
    }
}

class MessageFormatter {
    static format(text) {
        const parts = text.split(': ');
        if (parts.length > 1) {
            const header = parts[0] + ':';
            const message = parts.slice(1).join(': ');
            return `<strong>${header}</strong><br>${message}`;
        }
        return text;
    }
}

class Widget {
    constructor(containerId, elementId) {
        this.container = document.getElementById(containerId);
        this.element = document.getElementById(elementId);
    }

    show(text) {
        this.element.innerHTML = text;
        this.container.style.display = 'block';
        requestAnimationFrame(() => {
            this.container.classList.add('animate-in');
        });
    }

    hide() {
        this.container.classList.remove('animate-in');
        this.container.classList.add('animate-out');
        setTimeout(() => {
            this.container.style.display = 'none';
            this.container.classList.remove('animate-out');
        }, 500);
    }
}

class EventSourceHandler {
    constructor(url, onMessage) {
        this.url = url;
        this.onMessage = onMessage;
    }

    setup() {
        const eventSource = new EventSource(this.url);

        eventSource.onopen = () => {
            console.log('EventSource connected');
        };

        eventSource.addEventListener('Message', (event) => {
            const message = JSON.parse(event.data);
            console.log('Message received:', message);
            this.onMessage(message);
        });

        eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            eventSource.close();
            setTimeout(() => this.setup(), 5000); // Try to reconnect after 5 seconds
        };

        return eventSource;
    }
}

class LiveSatoshiWidget {
    constructor() {
        this.widget = new Widget('widget-container', 'widget');
        this.queue = new Queue();
        this.eventSource = new EventSourceHandler('/events', (message) => this.queue.put(message));
        
        this.NOTIFY_AUDIO_URL = "notification.mp3";
        this.QUEUE_CHECK_INTERVAL = 3000;
        this.WIDGET_DISPLAY_DELAY = 2000;
        this.WIDGET_HIDE_DELAY = 5000;
    }

    async start() {
        this.eventSource.setup();
        this.handleQueue();
    }

    async handleQueue() {
        while (true) {
            try {
                if (this.queue.isEmpty()) {
                    await new Promise(resolve => setTimeout(resolve, this.QUEUE_CHECK_INTERVAL));
                    continue;
                }

                const message = this.queue.get();
                await this.processMessage(message);
            } catch (error) {
                console.error('Error processing message:', error);
                await new Promise(resolve => setTimeout(resolve, this.QUEUE_CHECK_INTERVAL));
            }
        }
    }

    async processMessage(message) {
        await AudioPlayer.play(this.NOTIFY_AUDIO_URL);
        this.widget.show(MessageFormatter.format(message.text));
        await new Promise(resolve => setTimeout(resolve, this.WIDGET_DISPLAY_DELAY));

        await AudioPlayer.play("data:audio/wav;base64," + message.audio);
        this.widget.hide();
        await new Promise(resolve => setTimeout(resolve, this.WIDGET_HIDE_DELAY));
    }
}

// Initialize and start the widget
const liveSatoshiWidget = new LiveSatoshiWidget();
liveSatoshiWidget.start();