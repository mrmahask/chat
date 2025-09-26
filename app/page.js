// app/page.js
import Chatbot from './Chatbot'; // Import component Chatbot

export default function Home() {
  return (
    <main style={{ fontFamily: 'sans-serif', padding: '2rem' }}>
      <h1>Chào mừng đến với Trang Tư vấn MMO</h1>
      <p>Đây là trang web của bạn. Chatbot sẽ xuất hiện ở góc dưới bên phải.</p>

      {/* Thêm Chatbot vào đây */}
      <Chatbot />
    </main>
  );
}