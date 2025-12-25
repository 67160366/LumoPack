import React, { useState, useRef, useEffect } from 'react';

// ==================== STYLES ====================
const styles = {
  // ปุ่มเปิดแชท (Floating Button)
  floatingButton: {
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    width: '64px',
    height: '64px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    cursor: 'pointer',
    boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    zIndex: 1000,
  },
  
  // Chat Window Container
  chatContainer: {
    position: 'fixed',
    bottom: '100px',
    right: '24px',
    width: '380px',
    height: '550px',
    backgroundColor: '#ffffff',
    borderRadius: '20px',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    zIndex: 1000,
    animation: 'slideUp 0.3s ease-out',
  },
  
  // Header
  chatHeader: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '20px',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  
  headerInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  
  avatar: {
    width: '45px',
    height: '45px',
    borderRadius: '50%',
    background: 'rgba(255,255,255,0.2)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
  },
  
  headerText: {
    display: 'flex',
    flexDirection: 'column',
  },
  
  headerTitle: {
    margin: 0,
    fontSize: '16px',
    fontWeight: '600',
  },
  
  headerSubtitle: {
    margin: 0,
    fontSize: '12px',
    opacity: 0.9,
  },
  
  closeButton: {
    background: 'rgba(255,255,255,0.2)',
    border: 'none',
    borderRadius: '50%',
    width: '32px',
    height: '32px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: '18px',
    transition: 'background 0.2s',
  },
  
  // Messages Area
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    backgroundColor: '#f8f9fc',
  },
  
  // Message Bubbles
  messageBubble: {
    maxWidth: '85%',
    padding: '12px 16px',
    borderRadius: '18px',
    fontSize: '14px',
    lineHeight: '1.5',
    wordWrap: 'break-word',
  },
  
  userMessage: {
    alignSelf: 'flex-end',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    borderBottomRightRadius: '4px',
  },
  
  botMessage: {
    alignSelf: 'flex-start',
    backgroundColor: 'white',
    color: '#1f2937',
    borderBottomLeftRadius: '4px',
    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
  },
  
  // Typing Indicator
  typingIndicator: {
    display: 'flex',
    gap: '4px',
    padding: '12px 16px',
    backgroundColor: 'white',
    borderRadius: '18px',
    alignSelf: 'flex-start',
    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
  },
  
  typingDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: '#667eea',
    animation: 'bounce 1.4s infinite ease-in-out',
  },
  
  // Input Area
  inputContainer: {
    padding: '16px',
    backgroundColor: 'white',
    borderTop: '1px solid #e5e7eb',
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  
  input: {
    flex: 1,
    padding: '12px 16px',
    borderRadius: '24px',
    border: '2px solid #e5e7eb',
    fontSize: '14px',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  
  sendButton: {
    width: '44px',
    height: '44px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    transition: 'transform 0.2s, opacity 0.2s',
  },
  
  // Quotation Card
  quotationCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '16px',
    margin: '8px 0',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  
  quotationHeader: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#667eea',
    marginBottom: '12px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  
  quotationRow: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '13px',
    padding: '6px 0',
    borderBottom: '1px solid #f0f0f0',
  },
  
  quotationTotal: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '16px',
    fontWeight: '700',
    color: '#667eea',
    padding: '12px 0 0 0',
    marginTop: '8px',
    borderTop: '2px solid #667eea',
  },
  
  // Quick Replies
  quickReplies: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginTop: '8px',
  },
  
  quickReplyButton: {
    padding: '8px 14px',
    fontSize: '12px',
    borderRadius: '16px',
    border: '1px solid #667eea',
    backgroundColor: 'white',
    color: '#667eea',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
};

// ==================== CSS ANIMATIONS ====================
const cssAnimations = `
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes bounce {
    0%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-6px);
    }
  }
  
  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
  }
`;

// ==================== ICONS ====================
const ChatIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
  </svg>
);

const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="22" y1="2" x2="11" y2="13"/>
    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
  </svg>
);

const CloseIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

// ==================== MAIN COMPONENT ====================
export default function Chatbot({ onUpdateBoxDimensions, apiUrl = 'https://lumopack.onrender.com' }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [requirements, setRequirements] = useState({});
  const [quotation, setQuotation] = useState(null);
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Initial greeting when chat opens
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: 'สวัสดีครับ! 👋 ผมชื่อ "ลูโม่" ผู้ช่วย AI วิศวกรบรรจุภัณฑ์ของ LumoPack\n\nผมจะช่วยคุณออกแบบกล่องบรรจุภัณฑ์ที่เหมาะสมกับความต้องการครับ\n\nเริ่มต้นเลย... สินค้าที่จะใส่ในกล่องเป็นประเภทไหนครับ? 📦',
        quickReplies: ['สินค้าทั่วไป', 'Non-food', 'Food-grade', 'เครื่องสำอาง']
      }]);
    }
  }, [isOpen, messages.length]);
  
  // Inject CSS animations
  useEffect(() => {
    const styleSheet = document.createElement('style');
    styleSheet.innerText = cssAnimations;
    document.head.appendChild(styleSheet);
    return () => styleSheet.remove();
  }, []);
  
  // Send message to API
  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;
    
    const userMessage = { role: 'user', content: messageText };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          conversation_history: messages.map(m => ({ role: m.role, content: m.content })),
          current_requirements: requirements
        })
      });
      
      if (!response.ok) throw new Error('API Error');
      
      const data = await response.json();
      
      // Update requirements
      if (data.extracted_data && Object.keys(data.extracted_data).length > 0) {
        setRequirements(prev => ({ ...prev, ...data.extracted_data }));
        
        // Update 3D box if dimensions changed
        if (data.extracted_data.dimensions) {
          const dims = data.extracted_data.dimensions;
          if (dims.width && dims.length && dims.height) {
            onUpdateBoxDimensions?.({
              width: dims.width,
              length: dims.length,
              height: dims.height
            });
          }
        }
      }
      
      // Update quotation if available
      if (data.show_quotation && data.quotation_data) {
        setQuotation(data.quotation_data);
      }
      
      // Add bot response
      const botMessage = {
        role: 'assistant',
        content: data.response,
        quotation: data.show_quotation ? data.quotation_data : null,
        quickReplies: getQuickReplies(data.current_step, data.extracted_data)
      };
      
      setMessages(prev => [...prev, botMessage]);
      
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'ขออภัยครับ เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้งนะครับ 🙏'
      }]);
    }
    
    setIsLoading(false);
  };
  
  // Get quick reply suggestions based on current step
  const getQuickReplies = (step, data) => {
    if (!step) return [];
    
    switch(step) {
      case 1: // ประเภทสินค้า
        return ['สินค้าทั่วไป', 'Non-food', 'Food-grade', 'เครื่องสำอาง'];
      case 2: // ประเภทกล่อง
        return ['RSC (มาตรฐาน)', 'Die-cut (เน้นโชว์แบรนด์)'];
      case 3: // Inner
        return ['ไม่ต้องการ', 'กระดาษฝอย', 'บับเบิ้ล', 'ถุงลม'];
      case 6: // Checkpoint 1
        return ['ยืนยัน ✓', 'ขอแก้ไข'];
      case 7: // Mood & Tone
        return ['ข้าม', 'มินิมอล', 'พรีเมียม', 'สดใส', 'เรียบหรู'];
      case 8: // Logo
        return ['ไม่มีโลโก้', 'มีโลโก้'];
      case 9: // ลูกเล่นพิเศษ
        return ['ไม่ต้องการ', 'เคลือบเงา', 'เคลือบด้าน', 'ปั๊มนูน', 'ปั๊มฟอยล์'];
      case 10: // Checkpoint 2
        return ['ยืนยัน ✓', 'ขอแก้ไข'];
      case 12: // ยืนยันคำสั่งซื้อ
        return ['ยืนยันคำสั่งซื้อ ✓', 'ขอแก้ไข Mockup'];
      default:
        return [];
    }
  };
  
  // Handle quick reply click
  const handleQuickReply = (reply) => {
    sendMessage(reply);
  };
  
  // Handle input submit
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputValue);
  };
  
  // Render quotation card
  const renderQuotation = (quotationData) => {
    if (!quotationData || !quotationData.pricing) return null;
    
    const { pricing, box_type, material, dimensions, quantity } = quotationData;
    
    return (
      <div style={styles.quotationCard}>
        <div style={styles.quotationHeader}>
          📋 ใบเสนอราคา
        </div>
        
        <div style={styles.quotationRow}>
          <span>ประเภทกล่อง</span>
          <span>{box_type} ({material})</span>
        </div>
        
        <div style={styles.quotationRow}>
          <span>ขนาด</span>
          <span>{dimensions?.width}x{dimensions?.length}x{dimensions?.height} ซม.</span>
        </div>
        
        <div style={styles.quotationRow}>
          <span>จำนวน</span>
          <span>{quantity?.toLocaleString()} ชิ้น</span>
        </div>
        
        <div style={styles.quotationRow}>
          <span>ราคากล่อง</span>
          <span>฿{pricing.box_total?.toLocaleString()}</span>
        </div>
        
        {pricing.inner_total > 0 && (
          <div style={styles.quotationRow}>
            <span>Inner</span>
            <span>฿{pricing.inner_total?.toLocaleString()}</span>
          </div>
        )}
        
        {pricing.features_total > 0 && (
          <div style={styles.quotationRow}>
            <span>ลูกเล่นพิเศษ</span>
            <span>฿{pricing.features_total?.toLocaleString()}</span>
          </div>
        )}
        
        <div style={styles.quotationTotal}>
          <span>รวมทั้งสิ้น</span>
          <span>฿{pricing.grand_total?.toLocaleString()}</span>
        </div>
        
        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px', textAlign: 'center' }}>
          (ราคาต่อชิ้น ฿{pricing.price_per_unit?.toFixed(2)})
        </div>
      </div>
    );
  };
  
  return (
    <>
      {/* Floating Button */}
      <button
        style={{
          ...styles.floatingButton,
          transform: isOpen ? 'scale(0)' : 'scale(1)',
          opacity: isOpen ? 0 : 1,
        }}
        onClick={() => setIsOpen(true)}
        onMouseEnter={(e) => e.target.style.transform = 'scale(1.1)'}
        onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
      >
        <ChatIcon />
      </button>
      
      {/* Chat Window */}
      {isOpen && (
        <div style={styles.chatContainer}>
          {/* Header */}
          <div style={styles.chatHeader}>
            <div style={styles.headerInfo}>
              <div style={styles.avatar}>🤖</div>
              <div style={styles.headerText}>
                <h3 style={styles.headerTitle}>ลูโม่ - AI Assistant</h3>
                <p style={styles.headerSubtitle}>ผู้ช่วยออกแบบบรรจุภัณฑ์</p>
              </div>
            </div>
            <button
              style={styles.closeButton}
              onClick={() => setIsOpen(false)}
              onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.3)'}
              onMouseLeave={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
            >
              <CloseIcon />
            </button>
          </div>
          
          {/* Messages */}
          <div style={styles.messagesContainer}>
            {messages.map((msg, idx) => (
              <div key={idx}>
                <div
                  style={{
                    ...styles.messageBubble,
                    ...(msg.role === 'user' ? styles.userMessage : styles.botMessage)
                  }}
                >
                  {msg.content.split('\n').map((line, i) => (
                    <span key={i}>{line}<br/></span>
                  ))}
                </div>
                
                {/* Quotation Card */}
                {msg.quotation && renderQuotation(msg.quotation)}
                
                {/* Quick Replies */}
                {msg.role === 'assistant' && msg.quickReplies && msg.quickReplies.length > 0 && (
                  <div style={styles.quickReplies}>
                    {msg.quickReplies.map((reply, i) => (
                      <button
                        key={i}
                        style={styles.quickReplyButton}
                        onClick={() => handleQuickReply(reply)}
                        onMouseEnter={(e) => {
                          e.target.style.backgroundColor = '#667eea';
                          e.target.style.color = 'white';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.backgroundColor = 'white';
                          e.target.style.color = '#667eea';
                        }}
                      >
                        {reply}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {/* Typing Indicator */}
            {isLoading && (
              <div style={styles.typingIndicator}>
                <div style={{ ...styles.typingDot, animationDelay: '0s' }} />
                <div style={{ ...styles.typingDot, animationDelay: '0.2s' }} />
                <div style={{ ...styles.typingDot, animationDelay: '0.4s' }} />
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input */}
          <form style={styles.inputContainer} onSubmit={handleSubmit}>
            <input
              style={styles.input}
              type="text"
              placeholder="พิมพ์ข้อความ..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              disabled={isLoading}
            />
            <button
              type="submit"
              style={{
                ...styles.sendButton,
                opacity: inputValue.trim() ? 1 : 0.5,
                cursor: inputValue.trim() ? 'pointer' : 'not-allowed'
              }}
              disabled={!inputValue.trim() || isLoading}
            >
              <SendIcon />
            </button>
          </form>
        </div>
      )}
    </>
  );
}