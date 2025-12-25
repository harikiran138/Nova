import { useState, useEffect, useRef } from 'react'
import './App.css'
import { A2UIRootRenderer } from './a2ui/renderer';
import type { A2UIRoot } from './a2ui/types';

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  type?: 'text' | 'chunk' | 'done'
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    connectWebSocket()
    return () => {
      wsRef.current?.close()
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/chat')

    ws.onopen = () => {
      setIsConnected(true)
      setMessages(prev => [...prev, { role: 'system', content: 'Connected to Nova Agent' }])
    }

    ws.onclose = () => {
      setIsConnected(false)
      setMessages(prev => [...prev, { role: 'system', content: 'Disconnected. Reconnecting...' }])
      setTimeout(connectWebSocket, 3000)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'chunk') {
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1]
          if (lastMsg && lastMsg.role === 'assistant' && lastMsg.type !== 'done') {
            return [
              ...prev.slice(0, -1),
              { ...lastMsg, content: lastMsg.content + data.content }
            ]
          } else {
            return [...prev, { role: 'assistant', content: data.content, type: 'chunk' }]
          }
        })
      } else if (data.type === 'done') {
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1]
          if (lastMsg) {
            return [
              ...prev.slice(0, -1),
              { ...lastMsg, type: 'done' }
            ]
          }
          return prev
        })
      }
    }

    wsRef.current = ws
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !isConnected) return

    const userMsg = input
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setInput('')

    wsRef.current?.send(JSON.stringify({
      message: userMsg,
      session_id: 'default'
    }))
  }

  const isA2UI = (content: string) => {
    try {
      if (content.trim().startsWith('{"root":')) {
        JSON.parse(content);
        return true;
      }
    } catch (e) {
      return false;
    }
    return false;
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>🚀 Nova v2</h1>
        <span className={`status ${isConnected ? 'online' : 'offline'}`}>
          {isConnected ? 'Online' : 'Offline'}
        </span>
      </header>

      <div className="chat-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {isA2UI(msg.content) ? (
                 <div className="message-content a2ui-container" style={{ width: '100%' }}>
                    <A2UIRootRenderer data={JSON.parse(msg.content) as A2UIRoot} />
                 </div>
            ) : (
                <div className="message-content">
                  {msg.content}
                </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Nova anything..."
          disabled={!isConnected}
        />
        <button type="submit" disabled={!isConnected}>
          Send
        </button>
      </form>
    </div>
  )
}

export default App
