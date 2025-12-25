import React, { useState, useRef, Suspense } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls, ContactShadows } from '@react-three/drei';
import { TextureLoader } from 'three';
import jsPDF from 'jspdf'; 
import HeatmapBox from './HeatmapBox';
import Chatbot from './components/Chatbot'; // ✅ Import Chatbot

// --- Component กล่องปกติ (PlainBox) ---
function PlainBox({ width, height, depth, color }) {
  const mesh = useRef();
  useFrame((state, delta) => mesh.current.rotation.y += delta * 0.1);
  return (
    <mesh ref={mesh} position={[0, height / 20, 0]}>
      <boxGeometry args={[width / 10, height / 10, depth / 10]} />
      <meshStandardMaterial color={color} roughness={0.5} />
    </mesh>
  );
}

// --- Component กล่องมีลาย (TexturedBox) ---
function TexturedBox({ width, height, depth, textureUrl }) {
  const mesh = useRef();
  const texture = useLoader(TextureLoader, textureUrl);
  useFrame((state, delta) => mesh.current.rotation.y += delta * 0.1);
  return (
    <mesh ref={mesh} position={[0, height / 20, 0]}>
      <boxGeometry args={[width / 10, height / 10, depth / 10]} />
      <meshStandardMaterial map={texture} roughness={0.5} />
    </mesh>
  );
}

// --- Main App ---
export default function App() {
  const [formData, setFormData] = useState({
    length: 20, width: 15, height: 10, 
    weight: 5, flute_type: 'C'
  });
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState(null);

  // API URL - ใช้ environment variable หรือค่า default
  const API_URL = import.meta.env.VITE_API_URL || 'https://lumopack.onrender.com';

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) setImage(URL.createObjectURL(file));
  };

  // ✅ ฟังก์ชันรับข้อมูลจาก Chatbot และอัปเดตกล่อง 3D
  const handleChatbotUpdateDimensions = (dimensions) => {
    setFormData(prev => ({
      ...prev,
      length: dimensions.length || prev.length,
      width: dimensions.width || prev.width,
      height: dimensions.height || prev.height
    }));
    
    // Reset analysis เมื่อขนาดเปลี่ยน
    setAnalysis(null);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          length: parseFloat(formData.length),
          width: parseFloat(formData.width),
          height: parseFloat(formData.height),
          weight: parseFloat(formData.weight),
          flute_type: formData.flute_type
        })
      });
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      alert("เชื่อมต่อ Backend ไม่ได้!");
    }
    setLoading(false);
  };

  // --- 🖨️ ฟังก์ชันสร้าง PDF ---
  const generatePDF = () => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return;

    const imgData = canvas.toDataURL('image/png');
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();

    // HEADER
    doc.setFontSize(22); doc.setTextColor(40, 40, 40);
    doc.text("LumoPack Quotation", 20, 20);
    doc.setFontSize(10); doc.setTextColor(100);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, 20, 30);
    doc.setDrawColor(200); doc.line(20, 35, pageWidth - 20, 35);

    // SPECS
    doc.setFontSize(16); doc.setTextColor(0);
    doc.text("1. Product Specifications", 20, 50);
    doc.setFontSize(12); doc.setTextColor(60);
    const dimText = doc.splitTextToSize(`- Dimensions: ${formData.length}x${formData.width}x${formData.height} cm`, 80);
    doc.text(dimText, 25, 60);
    doc.text(`- Material: Flute ${formData.flute_type}`, 25, 70);
    doc.text(`- Weight Load: ${formData.weight} kg`, 25, 80);

    // IMAGE
    doc.addImage(imgData, 'PNG', 110, 45, 80, 80);

    // AI ANALYSIS
    if (analysis) {
      doc.setFontSize(16); doc.setTextColor(0);
      doc.text("2. AI Engineering Analysis", 20, 140);

      if (analysis.status === 'DANGER') {
        doc.setTextColor(220, 53, 69);
        doc.setFont(undefined, 'bold');
      } else {
        doc.setTextColor(40, 167, 69);
        doc.setFont(undefined, 'bold');
      }
      doc.text(`STATUS: ${analysis.status}`, 25, 150);
      doc.setFont(undefined, 'normal');

      doc.setTextColor(60); doc.setFontSize(12);
      doc.text(`- Safety Score: ${analysis.safety_score} / 100`, 25, 160);
      doc.text(`- Max Load Capacity: ${analysis.max_load_kg} kg`, 25, 170);
      
      doc.setFont(undefined, 'italic');
      const recText = doc.splitTextToSize(`NOTE: ${analysis.recommendation}`, pageWidth - 40);
      doc.text(recText, 25, 180);
    }

    // PRICE
    doc.setDrawColor(200); doc.line(20, 200, pageWidth - 20, 200);
    const price = (formData.length * formData.width * formData.height) * 0.005;
    doc.setFontSize(14); doc.setTextColor(100);
    doc.text("Total Estimated Price:", 20, 215);
    doc.setFontSize(24); doc.setTextColor(0, 86, 179);
    doc.setFont(undefined, 'bold');
    doc.text(`THB ${price.toFixed(2)}`, pageWidth - 20, 215, { align: 'right' });

    doc.save("LumoPack_Quotation_v2.pdf");
  };

  const isDanger = analysis?.status === 'DANGER';
  const showTexture = image && !isDanger;

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', background: '#f8f9fa' }}>
      
      {/* Panel ซ้าย */}
      <div style={{ width: '350px', padding: '20px', background: 'white', boxShadow: '4px 0 15px rgba(0,0,0,0.05)', zIndex: 10, overflowY: 'auto' }}>
        <h2 style={{ color: '#2d3436' }}>📦 LumoPack Studio</h2>

        {/* Inputs */}
        <div style={{ display: 'grid', gap: '15px' }}>
          <div><label>ยาว: {formData.length} cm</label><input type="range" min="10" max="60" name="length" value={formData.length} onChange={handleChange} style={{width:'100%'}}/></div>
          <div><label>กว้าง: {formData.width} cm</label><input type="range" min="10" max="60" name="width" value={formData.width} onChange={handleChange} style={{width:'100%'}}/></div>
          <div><label>สูง: {formData.height} cm</label><input type="range" min="5" max="50" name="height" value={formData.height} onChange={handleChange} style={{width:'100%'}}/></div>
        </div>
        <hr style={{ margin: '20px 0', border: 'none', borderTop: '1px solid #eee' }} />

        {/* AI Section */}
        <div style={{ background: '#f1f2f6', padding: '15px', borderRadius: '10px' }}>
          <h4 style={{ margin: '0 0 10px 0' }}>🤖 AI Simulation</h4>
          <input type="number" name="weight" placeholder="น้ำหนักสินค้า (kg)" value={formData.weight} onChange={handleChange} style={{width:'100%', padding:'8px', marginBottom:'10px', borderRadius:'5px', border:'1px solid #ddd'}} />
          <select name="flute_type" value={formData.flute_type} onChange={handleChange} style={{width:'100%', padding:'8px', marginBottom:'10px', borderRadius:'5px', border:'1px solid #ddd'}}>
            <option value="A">ลอน A (หนา 4.5mm)</option>
            <option value="C">ลอน C (มาตรฐาน 3.6mm)</option>
            <option value="B">ลอน B (บาง 2.5mm)</option>
            <option value="E">ลอน E (จิ๋ว 1.5mm)</option>
          </select>
          <button onClick={handleAnalyze} disabled={loading} style={{ width: '100%', background: isDanger ? '#ff6b6b' : '#0984e3', color: 'white', padding: '10px', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
            {loading ? 'AI กำลังคิด...' : '⚡ วิเคราะห์ความแข็งแรง'}
          </button>
          {analysis && (
            <div style={{ marginTop: '10px', fontSize: '0.9em', color: isDanger ? 'red' : 'green' }}>
              <strong>Status: {analysis.status}</strong> <br/>
              Score: {analysis.safety_score} (Max: {analysis.max_load_kg}kg)
            </div>
          )}
        </div>

        {/* Upload Image */}
        <div style={{ marginTop: '20px' }}>
          <label style={{ fontWeight: 'bold' }}>🎨 ออกแบบลายกล่อง</label>
          <input type="file" accept="image/*" onChange={handleImageUpload} style={{ marginTop: '5px' }} />
        </div>

        {/* ปุ่ม Download PDF */}
        {analysis && (
          <button onClick={generatePDF} style={{
            marginTop: '20px', width: '100%', padding: '15px', 
            background: '#2d3436', color: 'white', border: 'none', borderRadius: '8px',
            fontSize: '16px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px'
          }}>
            📄 ดาวน์โหลดใบเสนอราคา (PDF)
          </button>
        )}

        {/* Chatbot Hint */}
        <div style={{ 
          marginTop: '20px', 
          padding: '15px', 
          background: 'linear-gradient(135deg, #667eea20 0%, #764ba220 100%)',
          borderRadius: '10px',
          border: '1px dashed #667eea'
        }}>
          <p style={{ margin: 0, fontSize: '14px', color: '#667eea' }}>
            💬 <strong>ลองคุยกับ AI!</strong><br/>
            <span style={{ fontSize: '12px', color: '#666' }}>
              คลิกปุ่มแชทมุมขวาล่างเพื่อให้ AI ช่วยออกแบบกล่องและคำนวณราคา
            </span>
          </p>
        </div>
      </div>

      {/* 3D Canvas */}
      <div style={{ flex: 1 }}>
        <Canvas 
          camera={{ position: [6, 6, 6], fov: 45 }}
          gl={{ preserveDrawingBuffer: true }}
        >
          <color attach="background" args={['#e0e0e0']} />
          <ambientLight intensity={0.8} />
          <spotLight position={[10, 10, 10]} angle={0.15} />

          <Suspense fallback={null}>
            {showTexture ? (
              <TexturedBox width={formData.length} height={formData.height} depth={formData.width} textureUrl={image} />
            ) : isDanger ? (
              <HeatmapBox width={formData.length} height={formData.height} depth={formData.width} />
            ) : (
              <PlainBox width={formData.length} height={formData.height} depth={formData.width} color="#d4a373" />
            )}
          </Suspense>

          <ContactShadows opacity={0.4} scale={10} blur={2.5} />
          <OrbitControls makeDefault />
          <gridHelper args={[20, 20]} />
        </Canvas>
      </div>

      {/* ✅ Chatbot Component - Pop-up มุมขวาล่าง */}
      <Chatbot 
        onUpdateBoxDimensions={handleChatbotUpdateDimensions}
        apiUrl={API_URL}
      />
    </div>
  );
}