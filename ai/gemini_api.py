#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Gemini API連携

Google Gemini APIを使用してAI処理を行う
"""

import os
import logging
import asyncio
from typing import Optional, List

from google.api_core import exceptions as google_exceptions

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)

class GeminiAPI:
    """Google Gemini API連携クラス"""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-pro", api_keys: Optional[List[str]] = None):
        """
        初期化

        Args:
            api_key: Google Gemini API Key（指定がない場合は環境変数から取得）
            model: 使用するモデル名
        """
        self.api_keys = [k for k in (api_keys or []) if k]

        if api_key:
            if api_key not in self.api_keys:
                self.api_keys.insert(0, api_key)

        env_keys = []
        if os.environ.get("GEMINI_API_1") or os.environ.get("GEMINI_API_2"):
            if os.environ.get("GEMINI_API_1"):
                env_keys.append(os.environ.get("GEMINI_API_1"))
            if os.environ.get("GEMINI_API_2"):
                env_keys.append(os.environ.get("GEMINI_API_2"))
        elif os.environ.get("GEMINI_API_KEYS"):
            env_keys = [k.strip() for k in os.environ.get("GEMINI_API_KEYS").split(',') if k.strip()]
        elif os.environ.get("GEMINI_API_KEY"):
            env_keys.append(os.environ.get("GEMINI_API_KEY"))

        for key in env_keys:
            if key not in self.api_keys:
                self.api_keys.append(key)

        if not self.api_keys:
            logger.warning("Gemini API Keyが設定されていません")

        self.model_name = model
        self.current_key_index = 0
        self._configure_client()

        logger.info("Google Gemini APIを初期化しました")

    def _configure_client(self):
        """APIキーに基づきクライアントを構成する"""
        if not self.api_keys:
            self.api_key = None
            return

        from utils.helpers import select_gemini_api_key
        self.api_key = select_gemini_api_key(self.api_keys)
        self.current_key_index = self.api_keys.index(self.api_key)
        genai.configure(api_key=self.api_key)

    def _switch_api_key(self):
        """次のAPIキーに切り替える"""
        if not self.api_keys:
            return
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_index]
        logger.info(f"APIキーを切り替えました: index={self.current_key_index}")
        self._configure_client()

    def _is_rate_limit_error(self, error: Exception) -> bool:
        if isinstance(error, (google_exceptions.TooManyRequests, google_exceptions.ResourceExhausted)):
            return True
        msg = str(error).lower()
        return "rate" in msg and "limit" in msg or "quota" in msg

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        テキストを生成する
        
        Args:
            prompt: プロンプト
            max_tokens: 生成する最大トークン数
            temperature: 生成の多様性（0.0-1.0）
            
        Returns:
            生成されたテキスト
        """
        if not self.api_key:
            raise ValueError("Gemini API Keyが設定されていません")
        
        consecutive_limits = 0
        while True:
            try:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction
                )
                
                config = GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    candidate_count=1,
                )

                response = await model.generate_content_async(
                    contents=prompt,
                    generation_config=config,
                )
                
                if response.candidates:
                    text = response.text
                    return text.strip() if text else ""

                logger.warning(f"APIレスポンスに有効な結果がありません: {response}")
                return ""

            except Exception as e:
                if self._is_rate_limit_error(e) and self.api_keys:
                    consecutive_limits += 1
                    logger.warning("レート制限に達しました。APIキーを切り替えて再試行します")
                    self._switch_api_key()
                    if consecutive_limits >= len(self.api_keys):
                        logger.warning("すべてのAPIキーがレート制限に達しました。30秒待機します")
                        await asyncio.sleep(30)
                        consecutive_limits = 0
                    continue
                logger.error(f"テキスト生成中にエラーが発生しました: {e}", exc_info=True)
                raise
    
    async def close(self):
        """互換性のために存在するダミーメソッド"""
        logger.info("Google Gemini APIは特別なクローズ処理を必要としません")
