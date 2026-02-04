"""
AI Chat Service - จัดการการสนทนากับ AI
"""
import json
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_BASE_URL


class AIChat:
    """คลาสสำหรับจัดการ AI Chat"""
    
    def __init__(self):
        self.client = None
        if GROQ_API_KEY:
            self.client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url=LLM_BASE_URL
            )
    
    @property
    def is_configured(self) -> bool:
        """ตรวจสอบว่า configure แล้วหรือยัง"""
        return self.client is not None
    
    def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        system_prompt: str,
        current_requirements: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        ส่งข้อความไปยัง AI และรับการตอบกลับ
        
        Args:
            user_message: ข้อความจากผู้ใช้
            conversation_history: ประวัติการสนทนา
            system_prompt: System prompt
            current_requirements: ข้อมูลที่เก็บได้
        
        Returns:
            ข้อความตอบกลับจาก AI
        """
        if not self.client:
            raise Exception("GROQ_API_KEY not configured")
        
        # สร้าง messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # เพิ่มประวัติการสนทนา
        for msg in conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # เพิ่มข้อมูลที่เก็บได้ (ถ้ามี)
        final_message = user_message
        if current_requirements:
            final_message += f"\n\n[ข้อมูลที่เก็บได้: {json.dumps(current_requirements, ensure_ascii=False)}]"
        
        messages.append({"role": "user", "content": final_message})
        
        # เรียก API
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
        
        return response.choices[0].message.content
    
    @staticmethod
    def extract_json(response_text: str) -> Dict[str, Any]:
        """
        สกัด JSON จากข้อความตอบกลับ
        
        Args:
            response_text: ข้อความจาก AI
        
        Returns:
            ข้อมูล JSON ที่สกัดได้
        """
        # วิธีที่ 1: หา JSON ใน <extracted_data> tag
        pattern = r'<extracted_data>\s*([\s\S]*?)\s*</extracted_data>'
        match = re.search(pattern, response_text)
        if match:
            try:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # วิธีที่ 2: หา JSON block ที่มี product_info
        try:
            start_patterns = ['{"product_info"', '{"items"', '{"name"']
            start_idx = -1
            
            for pattern in start_patterns:
                idx = response_text.find(pattern)
                if idx != -1 and (start_idx == -1 or idx < start_idx):
                    start_idx = idx
            
            if start_idx == -1:
                start_idx = response_text.find('{')
            
            if start_idx != -1:
                depth = 0
                for i, char in enumerate(response_text[start_idx:]):
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            json_str = response_text[start_idx:start_idx + i + 1]
                            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        return {}
    
    @staticmethod
    def clean_response(response_text: str) -> str:
        """
        ลบ JSON และ tags ออกจากข้อความ
        
        Args:
            response_text: ข้อความจาก AI
        
        Returns:
            ข้อความที่สะอาด
        """
        # ลบ <extracted_data> tag และเนื้อหาข้างใน
        text = re.sub(r'<extracted_data>[\s\S]*?</extracted_data>', '', response_text)
        
        # ลบ JSON block ที่มี product_info
        text = re.sub(r'\{"product_info"[\s\S]*?\}\s*\}', '', text)
        
        # ลบ JSON block ขนาดใหญ่ (มากกว่า 100 ตัวอักษร)
        def remove_large_json(match):
            if len(match.group(0)) > 100:
                return ''
            return match.group(0)
        
        text = re.sub(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', remove_large_json, text)
        
        # ลบบรรทัดว่างที่เกินมา
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def process_response(self, response_text: str) -> Dict[str, Any]:
        """
        ประมวลผลข้อความตอบกลับ
        
        Args:
            response_text: ข้อความจาก AI
        
        Returns:
            {
                "clean_text": ข้อความที่สะอาด,
                "extracted_data": ข้อมูลที่สกัดได้,
                "quick_replies": ตัวเลือกตอบด่วน
            }
        """
        extracted_data = self.extract_json(response_text)
        clean_text = self.clean_response(response_text)
        quick_replies = extracted_data.get("quick_replies", [])
        
        return {
            "clean_text": clean_text,
            "extracted_data": extracted_data,
            "quick_replies": quick_replies
        }
