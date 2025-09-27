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
  const [uploadStatus, setUploadStatus] = useState<string>('');

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Set the initial welcome message when the component loads
  useEffect(() => {
    const welcomeMessage = chatMode === 'general' 
      ? "Hello! I'm REVLINE. Ask me anything about workouts, nutrition, or wellness!"
      : "Hello! I'm REVLINE in document analysis mode. Upload a fitness document and I'll help you analyze it!";
      
    setMessages([
      { role: 'assistant', content: welcomeMessage }
    ]);
  }, [chatMode]);

  // Auto-scroll to the bottom of the chat window whenever a new message is added
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // GENERAL CHAT FUNCTION
  const handleGeneralChat = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = { role: 'user', content: inputValue };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/chat', {
        messages: newMessages.map(msg => ({ role: msg.role, content: msg.content }))
      });
      
      const aiResponse: Message = response.data.response;
      setMessages(prevMessages => [...prevMessages, aiResponse]);

    } catch (error) {
      console.error("Error communicating with the backend:", error);
      const errorMessage: Message = { role: 'assistant', content: "Sorry, I'm having trouble connecting to my brain right now. Please try again later." };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // RAG CHAT FUNCTION
  const handleRAGChat = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = { role: 'user', content: inputValue };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/chat-rag', {
        question: userMessage.content
      });
      
      const aiResponse: Message = { role: 'assistant', content: response.data.response.content };
      setMessages(prevMessages => [...prevMessages, aiResponse]);

    } catch (error) {
      console.error("Error with RAG chat:", error);
      const errorMessage: Message = { role: 'assistant', content: "Sorry, I couldn't find relevant information in the uploaded document. Please try a different question or upload a new document." };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // FILE UPLOAD FUNCTION
  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setUploadStatus('');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('http://127.0.0.1:8000/upload-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setUploadStatus('✅ Document uploaded successfully! You can now ask questions about it.');
      setUploadedFile(file);
      setChatMode('rag');
      
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploadStatus('❌ Failed to upload document. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      handleFileUpload(file);
    } else {
      setUploadStatus('❌ Please select a PDF file.');
    }
  };

  // Switch chat modes
  const switchChatMode = (mode: ChatMode) => {
    setChatMode(mode);
    setUploadStatus('');
  };

  // Determine which send function to use
  const handleSendMessage = chatMode === 'general' ? handleGeneralChat : handleRAGChat;

  return (
    <div className="flex h-screen bg-gray-900 text-white font-sans">
      {/* Sidebar */}
      <div className="w-1/4 bg-gray-800 p-6 flex flex-col border-r border-gray-700">
        <h2 className="text-2xl font-bold mb-6 text-purple-400">💪 REVLINE</h2>
        
        {/* Chat Mode Toggle */}
        <div className="mb-6">
          <h3 className="text-lg mb-3 text-gray-300">Chat Mode</h3>
          <div className="space-y-2">
            <button
              onClick={() => switchChatMode('general')}
              className={`w-full text-left p-3 rounded-lg transition-colors ${
                chatMode === 'general' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              🗣️ General Chat
            </button>
            <button
              onClick={() => switchChatMode('rag')}
              className={`w-full text-left p-3 rounded-lg transition-colors ${
                chatMode === 'rag' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
              disabled={!uploadedFile}
            >
              📄 Document Chat
              {!uploadedFile && <span className="text-xs block text-gray-400">Upload a PDF first</span>}
            </button>
          </div>
        </div>

        <div className="flex-grow"></div>
        
        {/* File Upload Section */}
        <div className="border border-gray-700 rounded-lg p-4">
          <h3 className="font-semibold mb-3 text-gray-300">Analyze a Fitness Document</h3>
          <p className="text-sm text-gray-400 mb-4">
            Upload a PDF to chat with your fitness documents
          </p>
          
          <div className="space-y-3">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="pdf-upload"
              disabled={isUploading}
            />
            
            <label
              htmlFor="pdf-upload"
              className={`block w-full p-3 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
                isUploading
                  ? 'border-gray-500 bg-gray-700 cursor-not-allowed'
                  : 'border-gray-600 hover:border-purple-500 hover:bg-gray-700'
              }`}
            >
              {isUploading ? (
                <span className="text-gray-400">Uploading...</span>
              ) : (
                <>
                  <span className="block text-2xl mb-1">�</span>
                  <span className="text-sm text-gray-300">Click to upload PDF</span>
                </>
              )}
            </label>

            {uploadedFile && (
              <div className="text-sm text-gray-400">
                📄 {uploadedFile.name}
              </div>
            )}

            {uploadStatus && (
              <div className="text-sm p-2 rounded bg-gray-700">
                {uploadStatus}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-purple-400">
            {chatMode === 'general' ? '🗣️ General Chat' : '📄 Document Chat'}
          </h2>
          <p className="text-sm text-gray-400">
            {chatMode === 'general' 
              ? 'Ask me anything about fitness, nutrition, and wellness'
              : uploadedFile 
                ? `Chatting with: ${uploadedFile.name}`
                : 'Upload a document to start document chat'
            }
          </p>
        </div>

        {/* Chat Messages Area */}
        <div className="flex-1 p-6 overflow-y-auto">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`flex items-start space-x-4 mb-6 ${message.role === 'user' ? 'justify-end' : ''}`}
            >
              {message.role === 'assistant' && <span className="text-2xl">💪</span>}
              <div 
                className={`p-4 rounded-lg max-w-2xl ${
                  message.role === 'user' 
                  ? 'bg-purple-600' 
                  : 'bg-gray-800'
                }`}
              >
                {message.role === 'assistant' && <p className="text-purple-400 font-semibold">REVLINE</p>}
                <p className="text-gray-200 whitespace-pre-wrap">{message.content}</p>
              </div>
              {message.role === 'user' && <span className="text-2xl">👤</span>}
            </div>
          ))}
          {/* Loading indicator */}
          {isLoading && (
             <div className="flex items-start space-x-4 mb-6">
                <span className="text-2xl">💪</span>
                <div className="bg-gray-800 p-4 rounded-lg max-w-2xl">
                    <p className="text-purple-400 font-semibold">REVLINE</p>
                    <p className="text-gray-400">Analyzing...</p>
                </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Chat Input */}
        <div className="p-6">
          <div className="flex items-center bg-gray-800 rounded-lg p-2">
            <input 
              type="text" 
              placeholder={chatMode === 'general' ? "Ask REVLINE for fitness advice..." : "Ask questions about your document..."}
              className="flex-1 bg-transparent focus:outline-none px-4 text-gray-300"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={isLoading || (chatMode === 'rag' && !uploadedFile)}
            />
            <button 
              className="bg-purple-600 hover:bg-purple-700 text-white p-2 rounded-full transition-colors disabled:bg-gray-600"
              onClick={handleSendMessage}
              disabled={isLoading || (chatMode === 'rag' && !uploadedFile)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;