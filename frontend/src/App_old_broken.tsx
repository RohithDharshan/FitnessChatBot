import { useState, useEffect, useRef, createContext, useContext } from 'react';
import axios from 'axios';

// Define a type for our message objects for better code quality
type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type ChatMode = 'general' | 'rag';
type Theme = 'light' | 'dark';

// Theme Context
const ThemeContext = createContext<{
  theme: Theme;
  toggleTheme: () => void;
}>({
  theme: 'light',
  toggleTheme: () => {},
});

function App() {
  // THEME STATE
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('fitness-chatbot-theme');
    return (saved as Theme) || 'light';
  });

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('fitness-chatbot-theme', newTheme);
  };

  // STATE MANAGEMENT
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatMode, setChatMode] = useState<ChatMode>('general');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Set initial welcome message
  useEffect(() => {
    setMessages([
      { role: 'assistant', content: "Hello! I'm REVLINE. Ask me anything about workouts, nutrition, or wellness!" }
    ]);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || file.type !== 'application/pdf') {
      alert('Please select a PDF file');
      return;
    }

    setUploadedFile(file);
    setIsUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('http://127.0.0.1:8000/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadSuccess(true);
      setChatMode('rag');
      setMessages([
        { role: 'assistant', content: `Great! I've processed "${file.name}". Now you can ask me questions about the document content.` }
      ]);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle sending messages
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = { role: 'user', content: inputValue };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue('');
    setIsLoading(true);
    setIsTyping(true);

    // Add a small delay for better UX
    setTimeout(() => setIsTyping(false), 1500);

    try {
      let response;
      if (chatMode === 'rag' && uploadSuccess) {
        response = await axios.post('http://127.0.0.1:8000/chat-rag', {
          question: userMessage.content
        });
      } else {
        response = await axios.post('http://127.0.0.1:8000/chat', {
          messages: newMessages.map(msg => ({ role: msg.role, content: msg.content }))
        });
      }
      
      const aiResponse: Message = response.data.response;
      setMessages(prevMessages => [...prevMessages, aiResponse]);

    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = { 
        role: 'assistant', 
        content: "Sorry, I'm having trouble connecting right now. Please try again later." 
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const switchChatMode = (mode: ChatMode) => {
    setChatMode(mode);
    if (mode === 'general') {
      setMessages([
        { role: 'assistant', content: "Hello! I'm REVLINE. Ask me anything about workouts, nutrition, or wellness!" }
      ]);
    } else if (mode === 'rag' && uploadSuccess) {
      setMessages([
        { role: 'assistant', content: `I'm ready to answer questions about "${uploadedFile?.name}". What would you like to know?` }
      ]);
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className={`flex h-screen transition-all duration-500 ${
        theme === 'dark' 
          ? 'bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900' 
          : 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50'
      }`}>
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className={`absolute -top-4 -left-4 w-72 h-72 rounded-full opacity-20 animate-pulse ${
            theme === 'dark' ? 'bg-purple-500' : 'bg-blue-400'
          }`}></div>
          <div className={`absolute top-1/3 right-10 w-64 h-64 rounded-full opacity-10 animate-bounce ${
            theme === 'dark' ? 'bg-violet-500' : 'bg-purple-400'
          } animation-delay-1000`}></div>
          <div className={`absolute bottom-10 left-1/4 w-48 h-48 rounded-full opacity-15 animate-pulse ${
            theme === 'dark' ? 'bg-pink-500' : 'bg-pink-300'
          } animation-delay-2000`}></div>
        </div>

        {/* Sidebar */}
        <div className={`relative z-10 w-72 lg:w-80 xl:w-96 backdrop-blur-xl border-r transition-all duration-500 flex flex-col ${
          theme === 'dark' 
            ? 'bg-gray-900/50 border-purple-500/30' 
            : 'bg-white/70 border-gray-200/50'
        }`}>
          {/* Header with Theme Toggle */}
          <div className={`p-6 border-b transition-all duration-300 ${
            theme === 'dark' ? 'border-purple-500/30' : 'border-gray-200/50'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 ${
                    theme === 'dark' 
                      ? 'bg-gradient-to-r from-purple-600 to-violet-600 shadow-purple-500/25' 
                      : 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-blue-500/25'
                  } shadow-lg`}>
                    <span className="text-white font-bold text-xl animate-pulse">R</span>
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-ping"></div>
                </div>
                <div>
                  <h1 className={`text-2xl font-bold transition-colors duration-300 ${
                    theme === 'dark' ? 'text-white' : 'text-gray-900'
                  }`}>
                    REVLINE
                  </h1>
                  <span className={`text-xs font-medium transition-colors duration-300 ${
                    theme === 'dark' ? 'text-purple-400' : 'text-purple-600'
                  }`}>
                    AI FITNESS ASSISTANT
                  </span>
                </div>
              </div>
              
              {/* Theme Toggle Button */}
              <button
                onClick={toggleTheme}
                className={`p-3 rounded-xl transition-all duration-300 hover:scale-110 ${
                  theme === 'dark'
                    ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'
                    : 'bg-purple-500/20 text-purple-600 hover:bg-purple-500/30'
                }`}
              >
                <div className="animate-spin-slow">
                  {theme === 'dark' ? '☀️' : '🌙'}
                </div>
              </button>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 p-6">
            <div className="space-y-4 mb-8">
              <button
                onClick={() => switchChatMode('general')}
                className={`group w-full flex items-center space-x-4 p-4 rounded-2xl transition-all duration-300 hover:scale-105 transform ${
                  chatMode === 'general' 
                    ? theme === 'dark'
                      ? 'bg-gradient-to-r from-purple-600/30 to-violet-600/30 text-purple-300 border border-purple-500/50 shadow-lg shadow-purple-500/20' 
                      : 'bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 border border-purple-300 shadow-lg shadow-purple-200/50'
                    : theme === 'dark'
                    ? 'text-gray-300 hover:bg-gray-800/50 hover:text-white'
                    : 'text-gray-600 hover:bg-white/50 hover:text-gray-900'
                }`}
              >
                <div className={`w-6 h-6 rounded-lg flex items-center justify-center transition-all duration-300 ${
                  chatMode === 'general' 
                    ? 'bg-white/20 group-hover:rotate-12' 
                    : 'group-hover:scale-110'
                }`}>
                  💬
                </div>
                <span className="font-semibold">General Chat</span>
                <div className={`ml-auto transform transition-transform duration-300 ${
                  chatMode === 'general' ? 'rotate-90' : 'group-hover:rotate-45'
                }`}>
                  ✨
                </div>
              </button>
              
              <button
                onClick={() => switchChatMode('rag')}
                disabled={!uploadSuccess}
                className={`group w-full flex items-center space-x-4 p-4 rounded-2xl transition-all duration-300 hover:scale-105 transform ${
                  chatMode === 'rag' && uploadSuccess
                    ? theme === 'dark'
                      ? 'bg-gradient-to-r from-violet-600/30 to-pink-600/30 text-violet-300 border border-violet-500/50 shadow-lg shadow-violet-500/20' 
                      : 'bg-gradient-to-r from-violet-100 to-pink-100 text-violet-700 border border-violet-300 shadow-lg shadow-violet-200/50'
                    : uploadSuccess
                    ? theme === 'dark'
                      ? 'text-gray-300 hover:bg-gray-800/50 hover:text-white'
                      : 'text-gray-600 hover:bg-white/50 hover:text-gray-900'
                    : theme === 'dark'
                    ? 'text-gray-500 cursor-not-allowed opacity-50'
                    : 'text-gray-400 cursor-not-allowed opacity-50'
                }`}
              >
                <div className={`w-6 h-6 rounded-lg flex items-center justify-center transition-all duration-300 ${
                  chatMode === 'rag' && uploadSuccess 
                    ? 'bg-white/20 group-hover:rotate-12' 
                    : uploadSuccess ? 'group-hover:scale-110' : ''
                }`}>
                  📄
                </div>
                <span className="font-semibold">Document Chat</span>
                <div className={`ml-auto transform transition-transform duration-300 ${
                  chatMode === 'rag' && uploadSuccess ? 'rotate-90' : uploadSuccess ? 'group-hover:rotate-45' : ''
                }`}>
                  ✨
                </div>
              </button>
            </div>

            {/* File Upload Section */}
            <div className={`rounded-2xl p-6 border transition-all duration-300 ${
              theme === 'dark' 
                ? 'bg-gray-800/50 border-purple-500/30' 
                : 'bg-white/50 border-gray-200/50'
            }`}>
              <h3 className={`font-bold mb-4 transition-colors duration-300 ${
                theme === 'dark' ? 'text-white' : 'text-gray-900'
              }`}>
                Upload Document
              </h3>
              <input
                type="file"
                ref={fileInputRef}
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
              />
              
              {!uploadedFile ? (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className={`group w-full p-6 border-2 border-dashed rounded-2xl transition-all duration-300 hover:scale-105 flex flex-col items-center space-y-3 ${
                    theme === 'dark'
                      ? 'border-purple-400/50 hover:border-purple-400 hover:bg-purple-900/20 text-purple-300'
                      : 'border-purple-300 hover:border-purple-500 hover:bg-purple-50 text-purple-600'
                  } ${isUploading ? 'animate-pulse' : ''}`}
                >
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 group-hover:rotate-12 ${
                    theme === 'dark' ? 'bg-purple-500/20' : 'bg-purple-100'
                  }`}>
                    {isUploading ? '⏳' : '📎'}
                  </div>
                  <span className="font-medium">
                    {isUploading ? 'Uploading...' : 'Choose PDF file'}
                  </span>
                  <div className="text-xs opacity-70">
                    Drag & drop or click to browse
                  </div>
                </button>
              ) : (
                <div className="space-y-4">
                  <div className={`flex items-center space-x-3 p-4 rounded-2xl transition-all duration-300 ${
                    theme === 'dark' ? 'bg-gray-700/50' : 'bg-white'
                  } shadow-lg`}>
                    <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center">
                      📄
                    </div>
                    <span className={`flex-1 font-medium transition-colors duration-300 ${
                      theme === 'dark' ? 'text-white' : 'text-gray-700'
                    }`}>
                      {uploadedFile?.name}
                    </span>
                    {uploadSuccess && (
                      <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center animate-bounce">
                        <span className="text-white text-xs">✓</span>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => {
                      setUploadedFile(null);
                      setUploadSuccess(false);
                      setChatMode('general');
                      fileInputRef.current!.value = '';
                    }}
                    className={`w-full py-3 px-4 rounded-2xl font-medium transition-all duration-300 hover:scale-105 ${
                      theme === 'dark'
                        ? 'text-red-400 hover:bg-red-900/20 hover:text-red-300'
                        : 'text-red-600 hover:bg-red-50 hover:text-red-700'
                    }`}
                  >
                    🗑️ Remove file
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className={`relative z-10 flex-1 flex flex-col backdrop-blur-xl transition-all duration-500 ${
          theme === 'dark' ? 'bg-gray-900/30' : 'bg-white/30'
        }`}>
          {/* Chat Header */}
          <div className={`p-6 border-b transition-all duration-300 ${
            theme === 'dark' ? 'border-purple-500/30' : 'border-gray-200/50'
          }`}>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 ${
                  theme === 'dark' 
                    ? 'bg-gradient-to-r from-violet-600 to-purple-600 shadow-violet-500/25' 
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-blue-500/25'
                } shadow-xl`}>
                  <span className="text-white text-xl animate-pulse">🤖</span>
                </div>
                {isTyping && (
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-ping"></div>
                )}
              </div>
              <div>
                <h2 className={`text-xl font-bold transition-colors duration-300 ${
                  theme === 'dark' ? 'text-white' : 'text-gray-900'
                }`}>
                  {chatMode === 'general' ? '🎯 General Chat' : '📚 Document Chat'}
                </h2>
                <p className={`text-sm transition-colors duration-300 ${
                  theme === 'dark' ? 'text-purple-300' : 'text-purple-600'
                }`}>
                  {chatMode === 'general' 
                    ? 'Ask about fitness, nutrition, or wellness' 
                    : uploadSuccess 
                    ? `Analyzing ${uploadedFile?.name}` 
                    : 'Upload a document to start'
                  }
                </p>
              </div>
            </div>
          </div>
            </div>
          </div>
        </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 lg:p-8">
            <div className="max-w-6xl mx-auto space-y-8">
              {messages.map((message, index) => (
                <div 
                  key={index} 
                  className={`flex animate-fade-in-up ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className={`max-w-lg lg:max-w-4xl xl:max-w-5xl ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                    <div className={`flex space-x-4 ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
                        message.role === 'user' 
                          ? theme === 'dark'
                            ? 'bg-gradient-to-r from-green-500 to-emerald-500 shadow-green-500/25'
                            : 'bg-gradient-to-r from-green-500 to-emerald-500 shadow-green-500/25'
                          : theme === 'dark'
                          ? 'bg-gradient-to-r from-violet-600 to-purple-600 shadow-violet-500/25'
                          : 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-blue-500/25'
                      } shadow-xl hover:scale-110`}>
                        <span className="text-white text-lg">
                          {message.role === 'user' ? '👤' : '🤖'}
                        </span>
                      </div>
                      <div className={`rounded-3xl p-6 transition-all duration-300 hover:scale-[1.02] ${
                        message.role === 'user' 
                          ? theme === 'dark'
                            ? 'bg-gradient-to-r from-green-600/80 to-emerald-600/80 text-white shadow-xl shadow-green-500/20 backdrop-blur-sm'
                            : 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-xl shadow-green-500/20'
                          : theme === 'dark'
                          ? 'bg-gray-800/80 text-gray-100 shadow-xl shadow-purple-500/10 backdrop-blur-sm border border-purple-500/20'
                          : 'bg-white/80 text-gray-900 shadow-xl shadow-blue-500/10 backdrop-blur-sm border border-gray-200/50'
                      }`}>
                        <p className="whitespace-pre-wrap leading-relaxed text-lg">{message.content}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start animate-fade-in">
                  <div className="flex space-x-4">
                    <div className={`w-10 h-10 rounded-2xl flex items-center justify-center transition-all duration-300 ${
                      theme === 'dark'
                        ? 'bg-gradient-to-r from-violet-600 to-purple-600 shadow-violet-500/25'
                        : 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-blue-500/25'
                    } shadow-xl`}>
                      <span className="text-white text-lg animate-bounce">🤖</span>
                    </div>
                    <div className={`rounded-3xl p-6 transition-all duration-300 ${
                      theme === 'dark'
                        ? 'bg-gray-800/80 backdrop-blur-sm border border-purple-500/20'
                        : 'bg-white/80 backdrop-blur-sm border border-gray-200/50'
                    } shadow-xl`}>
                      <div className="flex space-x-2">
                        <div className={`w-3 h-3 rounded-full animate-bounce ${
                          theme === 'dark' ? 'bg-purple-400' : 'bg-purple-600'
                        }`}></div>
                        <div className={`w-3 h-3 rounded-full animate-bounce ${
                          theme === 'dark' ? 'bg-purple-400' : 'bg-purple-600'
                        }`} style={{animationDelay: '0.1s'}}></div>
                        <div className={`w-3 h-3 rounded-full animate-bounce ${
                          theme === 'dark' ? 'bg-purple-400' : 'bg-purple-600'
                        }`} style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className={`p-6 lg:p-8 border-t transition-all duration-300 ${
            theme === 'dark' ? 'border-purple-500/30' : 'border-gray-200/50'
          }`}>
            <div className="max-w-6xl mx-auto">
              <div className="flex space-x-4 items-end">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                    placeholder="Ask REVLINE for fitness advice..."
                    disabled={isLoading || (chatMode === 'rag' && !uploadSuccess)}
                    className={`w-full px-8 py-5 rounded-3xl transition-all duration-300 focus:scale-[1.02] text-lg ${
                      theme === 'dark'
                        ? 'bg-gray-800/80 text-white border border-purple-500/30 focus:border-purple-400 placeholder-gray-400 backdrop-blur-sm shadow-xl shadow-purple-500/10'
                        : 'bg-white/80 text-gray-900 border border-gray-300/50 focus:border-purple-500 placeholder-gray-500 backdrop-blur-sm shadow-xl shadow-blue-500/10'
                    } focus:outline-none focus:ring-4 ${
                      theme === 'dark' ? 'focus:ring-purple-500/20' : 'focus:ring-purple-500/20'
                    } disabled:opacity-50`}
                  />
                  <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                    {isTyping && (
                      <div className="animate-spin w-5 h-5">
                        <div className={`w-5 h-5 rounded-full border-2 border-t-transparent ${
                          theme === 'dark' ? 'border-purple-400' : 'border-purple-600'
                        }`}></div>
                      </div>
                    )}
                  </div>
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputValue.trim() || (chatMode === 'rag' && !uploadSuccess)}
                  className={`w-16 h-16 rounded-3xl transition-all duration-300 hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center shadow-xl ${
                    theme === 'dark'
                      ? 'bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 shadow-purple-500/25'
                      : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 shadow-purple-500/25'
                  }`}
                >
                  <span className="text-white text-2xl transform transition-transform duration-300 hover:rotate-12">
                    {isLoading ? '⏳' : '🚀'}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ThemeContext.Provider>
  );
            
            }
          </div>
        </div>

        {/* Input Area */}
        <div className="p-4 lg:p-6 border-t border-gray-200 bg-white">
          <div className="max-w-5xl mx-auto">
            <div className="flex space-x-4 items-end">
              <div className="flex-1">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                  placeholder="Ask REVLINE for fitness advice..."
                  disabled={isLoading || (chatMode === 'rag' && !uploadSuccess)}
                  className="w-full px-6 py-4 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none text-base"
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim() || (chatMode === 'rag' && !uploadSuccess)}
                className="w-14 h-14 bg-purple-600 text-white rounded-full hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
              >
                <span className="text-xl">↑</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;