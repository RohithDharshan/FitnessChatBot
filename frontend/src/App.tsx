import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

// Define a type for our message objects for better code quality
type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type ChatMode = 'general' | 'rag';

function App() {
  // STATE MANAGEMENT
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatMode, setChatMode] = useState<ChatMode>('general');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

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
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-72 lg:w-80 xl:w-96 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">R</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">REVLINE</h1>
            <span className="text-xs text-purple-600 font-medium">v2.0 - Wide Layout</span>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 p-6">
          <div className="space-y-3 mb-8">
            <button
              onClick={() => switchChatMode('general')}
              className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                chatMode === 'general' 
                  ? 'bg-purple-100 text-purple-700 border border-purple-200' 
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <div className="w-5 h-5">💬</div>
              <span className="font-medium">General Chat</span>
            </button>
            
            <button
              onClick={() => switchChatMode('rag')}
              disabled={!uploadSuccess}
              className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                chatMode === 'rag' && uploadSuccess
                  ? 'bg-purple-100 text-purple-700 border border-purple-200' 
                  : uploadSuccess
                  ? 'text-gray-600 hover:bg-gray-100'
                  : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              <div className="w-5 h-5">📄</div>
              <span className="font-medium">Document Chat</span>
            </button>
          </div>

          {/* File Upload Section */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-3">Upload Document</h3>
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
                className="w-full p-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-colors flex flex-col items-center space-y-2 text-gray-600"
              >
                <div className="w-8 h-8">📎</div>
                <span className="text-sm">
                  {isUploading ? 'Uploading...' : 'Choose PDF file'}
                </span>
              </button>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center space-x-2 p-2 bg-white rounded border">
                  <div className="w-4 h-4 text-red-500">📄</div>
                  <span className="text-sm text-gray-700 flex-1">{uploadedFile?.name}</span>
                  {uploadSuccess && <div className="w-4 h-4 text-green-500">✓</div>}
                </div>
                <button
                  onClick={() => {
                    setUploadedFile(null);
                    setUploadSuccess(false);
                    setChatMode('general');
                    fileInputRef.current!.value = '';
                  }}
                  className="w-full text-sm text-red-600 hover:text-red-700 transition-colors"
                >
                  Remove file
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Chat Header */}
        <div className="p-4 border-b border-gray-200 bg-white">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
              <span className="text-white text-lg">🤖</span>
            </div>
            <div>
              <h2 className="font-semibold text-gray-900">
                {chatMode === 'general' ? 'General Chat' : 'Document Chat'}
              </h2>
              <p className="text-sm text-gray-500">
                {chatMode === 'general' 
                  ? 'Ask about fitness, nutrition, or wellness' 
                  : uploadSuccess 
                  ? `Chatting about ${uploadedFile?.name}` 
                  : 'Upload a document to start'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-6">
          <div className="max-w-5xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-lg lg:max-w-3xl xl:max-w-4xl ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                  <div className={`flex space-x-3 ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.role === 'user' ? 'bg-green-500' : 'bg-gray-600'
                    }`}>
                      <span className="text-white text-sm">
                        {message.role === 'user' ? '👤' : '🤖'}
                      </span>
                    </div>
                    <div className={`rounded-2xl p-4 ${
                      message.role === 'user' 
                        ? 'bg-green-500 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex space-x-3">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">🤖</span>
                  </div>
                  <div className="bg-gray-100 rounded-2xl p-4">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
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