import { useState, useRef, useEffect } from 'react'
import {
  Bot,
  SendHorizontal,
  Paperclip,
  Sparkles,
  RotateCcw,
  User,
  Image as ImageIcon,
  FileUp,
  X,
  FileText
} from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [threadId] = useState(() => Math.random().toString(36).substring(7))
  const textareaRef = useRef(null)
  const bottomRef = useRef(null)
  const fileInputRef = useRef(null)
  const docInputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [input])

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      })
      if (res.ok) {
        setUploadedFile({ name: file.name })
      }
    } catch (err) {
      console.error("Upload failed", err)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const text = input
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: text }, { role: 'assistant', content: '', typing: true }])
    
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, thread_id: threadId })
      })
      const data = await res.json()
      
      setMessages(prev => {
        const last = [...prev]
        last[last.length - 1] = { 
          role: 'assistant', 
          content: data.response || "Agent currently not working", 
          typing: false 
        }
        return last
      })
    } catch (err) {
      setMessages(prev => {
        const last = [...prev]
        last[last.length - 1] = { 
          role: 'assistant', 
          content: "Agent currently not working", 
          typing: false 
        }
        return last
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-[#0A0A0A] text-neutral-200 font-sans antialiased selection:bg-neutral-800">
      <main className="flex-1 flex flex-col relative overflow-hidden">
        
        <header className="h-14 flex items-center px-6 border-b border-white/[0.03] bg-[#0A0A0A] z-30">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-white" />
            <span className="font-bold text-[13px] tracking-[0.25em] text-white uppercase italic">Jacestack AI</span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {messages.length === 0 ? (
            <div className="max-w-2xl mt-10 mx-auto h-[80%] flex flex-col items-center justify-center px-6">
              <div className="mb-6 p-4 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                <FileText size={28} className="text-neutral-600" />
              </div>
              <h2 className="text-3xl font-medium text-white mb-2 tracking-tight">Analyze your documents.</h2>
              <p className="text-neutral-500 mb-8 text-sm text-center">Upload a file to begin your session.</p>
              
              <input type="file" ref={docInputRef} className="hidden" onChange={handleFileUpload} />
              
              {!uploadedFile ? (
                <button 
                  onClick={() => docInputRef.current.click()}
                  className="w-full max-w-sm py-10 px-6 rounded-3xl border border-white/[0.05] bg-white/[0.01] hover:bg-white/[0.03] transition-all group flex flex-col items-center gap-4"
                >
                  <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center group-hover:scale-105 transition-transform">
                    <FileUp size={20} className="text-black" />
                  </div>
                  <span className="text-[13px] font-medium text-neutral-400">Click to select document</span>
                </button>
              ) : (
                <div className="w-full max-w-sm p-4 rounded-2xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-between">
                  <div className="flex items-center gap-3 overflow-hidden">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                      <FileText size={16} className="text-blue-400" />
                    </div>
                    <span className="text-sm text-white truncate">{uploadedFile.name}</span>
                  </div>
                  <button onClick={() => setUploadedFile(null)} className="p-1 hover:text-white transition-colors">
                    <X size={16} />
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="max-w-2xl mx-auto px-6 py-10">
              {messages.map((msg, i) => (
                <div key={i} className={`flex w-full gap-4 py-6 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-white/10 ${msg.role === 'user' ? 'bg-white text-black' : 'bg-neutral-900 text-neutral-500'}`}>
                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  <div className={`flex flex-col gap-2 max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`px-4 py-3 rounded-2xl text-[14px] leading-relaxed ${
                      msg.role === 'user' ? 'bg-neutral-800 text-white' : 'text-neutral-300'
                    }`}>
                      {msg.typing ? <div className="animate-pulse">...</div> : msg.content}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={bottomRef} className="h-32" />
            </div>
          )}
        </div>

        <div className="w-full pb-8 px-6">
          <div className="max-w-2xl mx-auto">
            <div className={`flex flex-col bg-[#141414] border border-white/[0.08] rounded-[22px] transition-all ${!uploadedFile && messages.length === 0 ? 'opacity-20 pointer-events-none' : ''}`}>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
                placeholder={uploadedFile ? "Ask a question..." : "Waiting for document..."}
                className="w-full bg-transparent border-none focus:ring-0 resize-none px-5 pt-4 pb-1 text-[15px] text-white placeholder:text-neutral-600 min-h-[50px]"
                rows={1}
              />
              <div className="flex items-center justify-between px-3 pb-3">
                <div className="flex items-center gap-1">
                  <input type="file" ref={fileInputRef} className="hidden" accept="image/*" />
                  <button onClick={() => fileInputRef.current.click()} className="p-2 text-neutral-500 hover:text-neutral-200 transition-colors">
                    <ImageIcon size={18} />
                  </button>
                  <button className="p-2 text-neutral-500 hover:text-neutral-200 transition-colors">
                    <Paperclip size={18} />
                  </button>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 text-neutral-700 hover:text-neutral-400">
                    <RotateCcw size={16} />
                  </button>
                  <button 
                    onClick={sendMessage}
                    disabled={!input.trim() || loading}
                    className="p-2 bg-white text-black rounded-xl disabled:opacity-20 hover:scale-105 active:scale-95 transition-all"
                  >
                    <SendHorizontal size={18} />
                  </button>
                </div>
              </div>
            </div>
            <p className="text-[9px] text-neutral-800 text-center mt-4 font-bold tracking-[0.4em] uppercase">
              Jacestack Artificial Intelligence
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
