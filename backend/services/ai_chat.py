"""
AI Chat Service - จัดการการสนทนากับ AI

Features:
- เชื่อมต่อกับ Groq API
- สกัด JSON จากข้อความ
- ทำความสะอาดข้อความ
"""
import json
import re
from typing import Dict, Any, List, Optional

from openai import OpenAI

from config import GROQ_API_KEY, LLMConfig
from utils.exceptions import AINotConfiguredError, AIResponseError


# ==================== REGEX PATTERNS ====================
EXTRACTED_DATA_PATTERN = re.compile(
    r'<extracted_data>\s*([\s\S]*?)\s*</extracted_data>',
    re.IGNORECASE
)

PRODUCT_INFO_PATTERN = re.compile(
    r'\{"product_info"[\s\S]*?\}\s*\}'
)

LARGE_JSON_PATTERN = re.compile(
    r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
)

# Pattern สำหรับลบข้อความ internal ที่ไม่ควรแสดงลูกค้า
INTERNAL_MESSAGE_PATTERNS = [
    re.compile(r'\*\*ตั้งค่า\s*ready_to_design\s*=\s*true[^*]*\*\*', re.IGNORECASE),
    re.compile(r'ตั้งค่า\s*ready_to_design\s*=\s*true[^\n]*', re.IGNORECASE),
    re.compile(r'\*\*ตั้งค่า\s*ready_to_quote\s*=\s*true[^*]*\*\*', re.IGNORECASE),
    re.compile(r'ตั้งค่า\s*ready_to_quote\s*=\s*true[^\n]*', re.IGNORECASE),
    re.compile(r'\*\*ตั้งค่า\s*box_confirmed\s*=\s*true[^*]*\*\*', re.IGNORECASE),
    re.compile(r'ready_to_design\s*=\s*true', re.IGNORECASE),
    re.compile(r'ready_to_quote\s*=\s*true', re.IGNORECASE),
    re.compile(r'box_confirmed\s*=\s*true', re.IGNORECASE),
    re.compile(r'\[ข้อมูลที่เก็บได้:[^\]]*\]', re.IGNORECASE),
]


# ==================== AI CHAT CLASS ====================
class AIChat:
    """
    คลาสสำหรับจัดการ AI Chat
    
    ใช้ Groq API (OpenAI compatible)
    
    Example:
        chat = AIChat()
        response = chat.send_message(
            user_message="สวัสดี",
            conversation_history=[],
            system_prompt="คุณคือผู้ช่วย AI"
        )
    """
    
    # ขนาด JSON ที่ถือว่า "ใหญ่" (ควรลบออกจากข้อความ)
    LARGE_JSON_THRESHOLD = 100
    
    # JSON keys ที่ต้องการค้นหา
    TARGET_JSON_KEYS = ['{"product_info"', '{"items"', '{"name"']
    
    def __init__(self):
        """Initialize AI Chat client"""
        self._client: Optional[OpenAI] = None
        
        if GROQ_API_KEY:
            self._client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url=LLMConfig.BASE_URL
            )
    
    @property
    def is_configured(self) -> bool:
        """ตรวจสอบว่า configure แล้วหรือยัง"""
        return self._client is not None
    
    # ==================== PUBLIC METHODS ====================
    def send_message(
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
        
        Raises:
            AINotConfiguredError: ถ้ายังไม่ได้ configure API key
            AIResponseError: ถ้า AI ตอบกลับผิดปกติ
        """
        if not self._client:
            raise AINotConfiguredError()
        
        messages = self._build_messages(
            user_message, 
            conversation_history, 
            system_prompt,
            current_requirements
        )
        
        try:
            response = self._client.chat.completions.create(
                model=LLMConfig.MODEL,
                messages=messages,
                temperature=LLMConfig.TEMPERATURE,
                max_tokens=LLMConfig.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            raise AIResponseError(f"AI request failed: {str(e)}")
    
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
    
    @staticmethod
    def extract_json(response_text: str) -> Dict[str, Any]:
        """
        สกัด JSON จากข้อความตอบกลับ
        
        ลำดับการค้นหา:
        1. ใน <extracted_data> tag
        2. JSON block ที่มี product_info
        3. JSON block ใดๆ ที่พบ
        
        Args:
            response_text: ข้อความจาก AI
        
        Returns:
            ข้อมูล JSON หรือ {} ถ้าไม่พบ
        """
        # วิธีที่ 1: หาใน <extracted_data> tag
        result = AIChat._extract_from_tag(response_text)
        if result:
            return result
        
        # วิธีที่ 2: หา JSON block
        result = AIChat._extract_json_block(response_text)
        if result:
            return result
        
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
        text = response_text
        
        # ลบ <extracted_data> tag และเนื้อหา
        text = EXTRACTED_DATA_PATTERN.sub('', text)
        
        # ลบ JSON block ที่มี product_info
        text = PRODUCT_INFO_PATTERN.sub('', text)
        
        # ลบ JSON block ขนาดใหญ่
        text = AIChat._remove_large_json_blocks(text)
        
        # ลบข้อความ internal ที่ไม่ควรแสดงลูกค้า
        for pattern in INTERNAL_MESSAGE_PATTERNS:
            text = pattern.sub('', text)
        
        # ลบบรรทัดว่างที่เกิน
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    # ==================== PRIVATE METHODS ====================
    def _build_messages(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        system_prompt: str,
        current_requirements: Optional[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """สร้าง messages array สำหรับส่งไป API"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # เพิ่มประวัติการสนทนา
        for msg in history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # เพิ่มข้อมูลที่เก็บได้ (ถ้ามี)
        final_message = user_message
        if current_requirements:
            requirements_json = json.dumps(current_requirements, ensure_ascii=False)
            final_message += f"\n\n[ข้อมูลที่เก็บได้: {requirements_json}]"
        
        messages.append({"role": "user", "content": final_message})
        
        return messages
    
    @staticmethod
    def _extract_from_tag(text: str) -> Optional[Dict[str, Any]]:
        """สกัด JSON จาก <extracted_data> tag"""
        match = EXTRACTED_DATA_PATTERN.search(text)
        if match:
            try:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        return None
    
    @staticmethod
    def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
        """สกัด JSON block จากข้อความ"""
        # หา index เริ่มต้นของ JSON
        start_idx = AIChat._find_json_start(text)
        if start_idx == -1:
            return None
        
        # หา JSON ที่สมบูรณ์ด้วย bracket matching
        try:
            json_str = AIChat._extract_complete_json(text, start_idx)
            if json_str:
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return None
    
    @staticmethod
    def _find_json_start(text: str) -> int:
        """หา index เริ่มต้นของ JSON"""
        # ลอง pattern ที่เฉพาะเจาะจงก่อน
        for pattern in AIChat.TARGET_JSON_KEYS:
            idx = text.find(pattern)
            if idx != -1:
                return idx
        
        # Fallback: หา { ตัวแรก
        return text.find('{')
    
    @staticmethod
    def _extract_complete_json(text: str, start_idx: int) -> Optional[str]:
        """สกัด JSON ที่สมบูรณ์ด้วย bracket matching"""
        depth = 0
        
        for i, char in enumerate(text[start_idx:]):
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    return text[start_idx:start_idx + i + 1]
        
        return None
    
    @staticmethod
    def _remove_large_json_blocks(text: str) -> str:
        """ลบ JSON block ที่มีขนาดใหญ่"""
        def replace_large(match):
            if len(match.group(0)) > AIChat.LARGE_JSON_THRESHOLD:
                return ''
            return match.group(0)
        
        return LARGE_JSON_PATTERN.sub(replace_large, text)