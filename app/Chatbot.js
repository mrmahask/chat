// app/Chatbot.js
'use client'; // Đánh dấu đây là Client Component
import { useState } from 'react';
import styles from './Chatbot.module.css';

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { text: "Xin chào! Tôi là trợ lý tư vấn về lĩnh vực MMO. Tôi có thể giúp gì cho bạn?", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [userInfo, setUserInfo] = useState({ name: '', email: '', phone: '' });
  const [stage, setStage] = useState('greeting'); // Các giai đoạn: greeting, collecting_name, collecting_email, collecting_phone, done

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { text: input, sender: 'user' }];
    setMessages(newMessages);
    setInput('');

    // Logic trả lời của bot
    setTimeout(() => {
      let botResponse = '';
      let nextStage = stage;

      switch (stage) {
        case 'greeting':
          botResponse = 'Cảm ơn câu hỏi của bạn. Để được tư vấn chi tiết hơn, bạn vui lòng cho tôi biết tên của bạn được không?';
          nextStage = 'collecting_name';
          break;
        case 'collecting_name':
          setUserInfo(prev => ({ ...prev, name: input }));
          botResponse = `Cảm ơn bạn ${input}. Bạn có thể cung cấp email để chúng tôi gửi tài liệu tham khảo không?`;
          nextStage = 'collecting_email';
          break;
        case 'collecting_email':
          setUserInfo(prev => ({ ...prev, email: input }));
          botResponse = 'Tuyệt vời! Cuối cùng, bạn vui lòng cho tôi xin số điện thoại để đội ngũ chuyên gia có thể liên hệ trực tiếp nhé.';
          nextStage = 'collecting_phone';
          break;
        case 'collecting_phone':
          setUserInfo(prev => ({ ...prev, phone: input }));
          botResponse = 'Cảm ơn bạn đã cung cấp thông tin! Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất. Chúc bạn một ngày tốt lành!';
          nextStage = 'done';
          console.log('Thông tin khách hàng:', { ...userInfo, phone: input });
          // Tại đây, bạn có thể gửi thông tin này đến API hoặc cơ sở dữ liệu
          break;
        default:
          botResponse = "Cảm ơn bạn! Chúng tôi sẽ sớm liên hệ lại.";
      }

      setMessages(prev => [...prev, { text: botResponse, sender: 'bot' }]);
      setStage(nextStage);
    }, 500);
  };

  return (
    <div className={styles.chatbotContainer}>
      <div className={styles.chatWindow}>
        {messages.map((msg, index) => (
          <div key={index} className={`${styles.message} ${styles[msg.sender]}`}>
            {msg.text}
          </div>
        ))}
      </div>
      {stage !== 'done' && (
        <div className={styles.inputArea}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Nhập tin nhắn..."
          />
          <button onClick={handleSend}>Gửi</button>
        </div>
      )}
    </div>
  );
}