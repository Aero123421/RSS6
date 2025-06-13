#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIプロセッサー

記事のAI処理（翻訳、要約、分類）を行う
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List

from .gemini_api import GeminiAPI
from .summarizer import Summarizer
from .classifier import Classifier

logger = logging.getLogger(__name__)


class AIProcessor:
    """AI処理クラス"""

    def __init__(self, config: Dict[str, Any]):
        """
        初期化

        Args:
            config: 設定辞書
        """
        self.config = config

        # AIモデルの設定（Google Geminiのみを利用）
        self.ai_provider = "gemini"
        self.ai_model = config.get("ai_model", "gemini-2.0-flash")
        self.qa_model = config.get("qa_model", self.ai_model)
        self.thinking_budget = config.get("thinking_budget", 0)

        self.api = self._create_api(self.ai_model)
        self.qa_api = self._create_api(self.qa_model)

        prompts = config.get("prompts", {})

        # 各処理クラスの初期化
        self.summarizer = Summarizer(self.api, prompts.get("summarizer_system"))
        self.classifier = Classifier(self.api, prompts.get("classifier_template"))

        logger.info("AIプロセッサーを初期化しました")

    async def reload_from_config(self) -> None:
        """設定の変更を反映してAPIクライアントを再初期化する"""
        self.ai_model = self.config.get("ai_model", "gemini-2.0-flash")
        self.qa_model = self.config.get("qa_model", self.ai_model)

        if self.api:
            await self.api.close()
        if self.qa_api:
            await self.qa_api.close()

        self.api = self._create_api(self.ai_model)
        self.qa_api = self._create_api(self.qa_model)

        self.summarizer.api = self.api
        self.classifier.api = self.api

        logger.info("AIプロセッサーの設定を再読み込みしました")

    def _create_api(self, model: Optional[str] = None):
        """Google Gemini APIインスタンスを生成する"""
        api_key = self.config.get("gemini_api_key", "")
        keys = self.config.get("gemini_api_keys")
        selected_model = model or "gemini-2.0-flash"
        logger.info(f"Google Gemini APIを使用します: {selected_model}")
        return GeminiAPI(api_key, model=selected_model, api_keys=keys)

    async def process_article(
        self, article: Dict[str, Any], feed_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        記事を処理する

        Args:
            article: 記事データ
            feed_info: フィード情報

        Returns:
            処理済み記事データ
        """
        processed = article.copy()

        try:
            # 要約（翻訳を兼ねる）
            if self.config.get("summarize", True):
                try:
                    processed = await self._summarize_article(processed, feed_info)
                except Exception as e:
                    logger.warning(f"要約に失敗しました: {e}")
                    processed["summarized"] = False

            # ジャンル分類
            if self.config.get("classify", False):
                processed = await self._classify_article(processed)

            # 検索用キーワード抽出
            try:
                keywords = await self.extract_keywords_for_storage(processed)
                processed["keywords_en"] = keywords
            except Exception as e:
                logger.warning(f"キーワード抽出に失敗しました: {e}")

            # 処理フラグを追加
            processed["ai_processed"] = True

            return processed

        except Exception as e:
            logger.error(
                f"記事処理中にエラーが発生しました: {article.get('title')}: {e}",
                exc_info=True,
            )

            # エラーが発生した場合は元の記事を返す
            processed["ai_processed"] = False
            processed["ai_error"] = str(e)
            return processed

    async def _summarize_article(
        self,
        article: Dict[str, Any],
        feed_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        記事を要約する

        Args:
            article: 記事データ

        Returns:
            要約済み記事データ
        """
        # 要約対象のコンテンツ
        content = article.get("content", "")

        # 要約の最大文字数
        max_length = self.config.get("summary_length", 4000)
        summary_type = feed_info.get("summary_type")

        summarizer = self.summarizer

        # 要約の生成
        summary = await summarizer.summarize(
            content, max_length, summary_type or "normal"
        )

        # タイトルの翻訳
        title = article.get("title", "")
        if title:
            translated = await summarizer.summarize(title, max_length, "title")
            if translated:
                article["title"] = translated

        # 要約結果を記事に追加
        article["summary"] = summary
        article["summarized"] = True

        logger.info(f"記事を要約しました: {article.get('title')}")

        return article

    async def _classify_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        記事のジャンルを分類する

        Args:
            article: 記事データ

        Returns:
            分類済み記事データ
        """
        try:
            # 分類対象のコンテンツ
            title = article.get("title", "")
            content = article.get("content", "")

            # カテゴリリスト
            categories = self.config.get("categories", [])
            category_names = [cat.get("name") for cat in categories]

            # ジャンル分類
            category = await self.classifier.classify(title, content, category_names)

            # 分類結果を記事に追加
            article["category"] = category
            article["classified"] = True

            logger.info(f"記事を分類しました: {article.get('title')} -> {category}")
            return article

        except Exception as e:
            logger.error(
                f"記事分類中にエラーが発生しました: {article.get('title')}: {e}",
                exc_info=True,
            )
            article["classified"] = False
            article["category"] = "other"  # デフォルトカテゴリ
            return article

    async def extract_keywords_for_storage(self, article: Dict[str, Any]) -> str:
        """記事から検索用キーワードを抽出する"""
        title = article.get("title", "")
        content = article.get("content", "")
        prompt = (
            "You are a data indexer. Analyze the following article and extract the 5-7 most important and representative keywords in English. "
            "The keywords should be suitable for later searching. Output them as a single, comma-separated string.\n\n"
            f"Title: {title}\n\nContent:\n{content}\n\nKeywords:"
        )
        try:
            return await self.api.generate_text(prompt, max_tokens=50, temperature=0.3)
        except Exception as e:
            logger.error(f"キーワード抽出中にエラーが発生しました: {e}", exc_info=True)
            return ""

    async def _generate_search_keywords(
        self, article: Dict[str, Any], question: str
    ) -> List[str]:
        """質問と記事から関連記事検索用のキーワードを抽出する"""
        title = article.get("title", "")
        content = article.get("content", "")
        prompt = (
            "You are a search query expert. Extract up to 5 important English keywords from the user's question and the original article to find related information.\n\n"
            f"Title: {title}\n\nContent:\n{content}\n\nQuestion: {question}\n\nKeywords:"
        )
        try:
            text = await self.api.generate_text(prompt, max_tokens=30, temperature=0.3)
            return [k.strip() for k in text.split(",") if k.strip()]
        except Exception as e:
            logger.error(
                f"検索キーワード生成中にエラーが発生しました: {e}", exc_info=True
            )
            return []

    async def answer_question(
        self,
        original_article: Dict[str, Any],
        related_articles: List[Dict[str, Any]],
        question: str,
    ) -> str:
        """元記事と関連記事を参照して質問に回答する"""
        main_title = original_article.get("title", "")
        main_content = original_article.get("content", "")
        prompt = (
            "You are an expert news commentator. Based on the following articles, please answer the user's question in Japanese.\n\n"
            f"**Main Article:**\nTitle: {main_title}\nContent: {main_content}\n\n"
            "**Related Articles:**\n"
        )
        for i, art in enumerate(related_articles[:15], 1):
            part = art.get("content", "")
            prompt += (
                f"{i}. Title: {art.get('title','')}\n   Content: {part[:600]}...\n"
            )
        prompt += f"\n**User's Question:**\n{question}\n\n**Answer (in Japanese):**"
        try:
            return await self.qa_api.generate_text(
                prompt,
                max_tokens=1000,
                temperature=0.3,
                thinking_budget=self.thinking_budget,
            )
        except Exception as e:
            logger.error(f"回答生成中にエラーが発生しました: {e}", exc_info=True)
            return "回答を生成できませんでした。"
