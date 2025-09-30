import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../../contexts/AppContext';
import { aiService } from '../../services/aiService';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import Alert from '../common/Alert';
import { 
  MessageCircle, 
  Send, 
  X, 
  Minimize2, 
  Maximize2,
  Bot,
  User,
  RefreshCw,
  Trash2,
  Settings,
  Download,
  Upload,
  Mic,
  MicOff,
  Paperclip,
  Smile,
  MoreVertical
} from 'lucide-react';

const AIChatbot = ({ 
  isOpen = false, 
  onClose, 
  onMinimize,
  className = '' 
}) => {
  const { addNotification } = useApp();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      loadChatHistory();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const history = await aiService.getChatHistory();
      setChatHistory(history);
    } catch (err) {
      console.error('Error loading chat history:', err);
    }
  };

  const sendMessage = async (message = inputMessage) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setIsTyping(true);

    try {
      const response = await aiService.sendChatMessage(message, {
        context: 'erp_assistant',
        user_id: 'current_user'
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.message,
        timestamp: new Date().toISOString(),
        confidence: response.confidence,
        suggestions: response.suggestions || []
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setError(err.message);
      addNotification({
        type: 'danger',
        title: 'Chat Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Handle file upload
      addNotification({
        type: 'info',
        title: 'File Upload',
        message: 'File upload feature coming soon',
      });
    }
  };

  const handleVoiceRecording = () => {
    setIsRecording(!isRecording);
    // Implement voice recording
    addNotification({
      type: 'info',
      title: 'Voice Recording',
      message: 'Voice recording feature coming soon',
    });
  };

  const clearChat = async () => {
    try {
      await aiService.clearChatHistory();
      setMessages([]);
      addNotification({
        type: 'success',
        title: 'Chat Cleared',
        message: 'Chat history has been cleared',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-success-600';
    if (confidence >= 60) return 'text-warning-600';
    return 'text-danger-600';
  };

  if (!isOpen) return null;

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${className}`}>
      <div className={`bg-white rounded-lg shadow-xl border border-gray-200 ${
        isMinimized ? 'w-80 h-16' : 'w-96 h-[500px]'
      } transition-all duration-300`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">AI Assistant</h3>
              <p className="text-xs text-gray-500">
                {isTyping ? 'Typing...' : 'Online'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Settings Panel */}
            {showSettings && (
              <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Clear Chat History</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={clearChat}
                      className="text-danger-600 hover:text-danger-900"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Clear
                    </Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Export Chat</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {/* Export chat */}}
                    >
                      <Download className="w-4 h-4 mr-1" />
                      Export
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Chat History Panel */}
            {showHistory && (
              <div className="p-4 border-b border-gray-200 bg-gray-50 max-h-32 overflow-y-auto">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Recent Chats</h4>
                <div className="space-y-2">
                  {chatHistory.slice(0, 3).map((chat, index) => (
                    <button
                      key={index}
                      onClick={() => {/* Load chat */}}
                      className="w-full text-left p-2 text-sm text-gray-600 hover:bg-gray-100 rounded"
                    >
                      {chat.title || `Chat ${index + 1}`}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Start a conversation with the AI assistant</p>
                  <p className="text-sm">Ask about your business data, get insights, or request help</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-start space-x-2 max-w-xs ${
                      message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                    }`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.type === 'user' 
                          ? 'bg-primary-100' 
                          : 'bg-gray-100'
                      }`}>
                        {message.type === 'user' ? (
                          <User className="w-4 h-4 text-primary-600" />
                        ) : (
                          <Bot className="w-4 h-4 text-gray-600" />
                        )}
                      </div>
                      
                      <div className={`rounded-lg p-3 ${
                        message.type === 'user'
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        <p className="text-sm">{message.content}</p>
                        
                        {message.type === 'bot' && message.confidence && (
                          <div className="mt-2 flex items-center space-x-2">
                            <span className="text-xs text-gray-500">Confidence:</span>
                            <span className={`text-xs font-medium ${
                              getConfidenceColor(message.confidence)
                            }`}>
                              {message.confidence}%
                            </span>
                          </div>
                        )}
                        
                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {message.suggestions.map((suggestion, index) => (
                              <button
                                key={index}
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="block w-full text-left text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-200 px-2 py-1 rounded"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-gray-600" />
                    </div>
                    <div className="bg-gray-100 rounded-lg p-3">
                      <LoadingSpinner size="sm" text="Thinking..." />
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex items-center space-x-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  onChange={handleFileUpload}
                />
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-gray-400 hover:text-gray-600"
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    disabled={loading}
                  />
                </div>
                
                <button
                  onClick={handleVoiceRecording}
                  className={`p-2 ${
                    isRecording ? 'text-danger-600' : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </button>
                
                <Button
                  onClick={() => sendMessage()}
                  disabled={!inputMessage.trim() || loading}
                  size="sm"
                  className="flex items-center space-x-1"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AIChatbot;