#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
デフォルト設定

システムのデフォルト設定値を定義する
"""

# デフォルト設定
DEFAULT_CONFIG = {
    # Discord設定
    "discord_token": "",  # Discordボットトークン
    "guild_id": None,  # サーバーID（Noneの場合はグローバルコマンド）
    "admin_ids": [],  # 管理者ユーザーID
    "category_id": None,  # RSSチャンネルを作成するカテゴリID
    # RSS設定
    "feeds": [],  # フィードリスト
    "check_interval": 15,  # フィード確認間隔（分）
    "max_articles": 5,  # 1回の確認で処理する最大記事数
    # AI設定
    "ai_provider": "gemini",  # AIプロバイダ（geminiのみ）
    "gemini_api_key": "",  # Google Gemini API Key (旧形式)
    "gemini_api_keys": [],  # Gemini API Keyのリスト
    "ai_model": "gemini-2.0-flash",  # 使用するAIモデル
    # gemini-2.0-flash, gemini-2.5-flash-preview-05-20
    "qa_model": "gemini-2.5-flash-preview-05-20",  # 質問応答用モデル
    "thinking_budget": 0,  # thinkingBudget の設定値
    "summarize": True,  # 要約（翻訳を兼ねる）を有効にするか
    "summary_length": 4000,  # 要約の最大文字数
    "classify": False,  # ジャンル分類を有効にするか
    # プロンプト設定
    "prompts": {
        "summarizer_system": "あなたは日本語編集者です。要点を抽出し、日本語のみで短くまとめます。長文は読みやすいように適度に改行してください。",
        "classifier_template": "次の記事のジャンルを以下のカテゴリから最も適切なもの一つだけ選んでください:{categories}\n\n記事:\n{content}\n\n出力は選んだカテゴリ名のみを英語で一語だけ返してください。余計な説明や句読点、改行は不要です。",
    },
    # カテゴリ設定
    "categories": [
        {"name": "technology", "jp_name": "テクノロジー", "emoji": "🖥️"},
        {"name": "business", "jp_name": "ビジネス", "emoji": "💼"},
        {"name": "science", "jp_name": "科学", "emoji": "🔬"},
        {"name": "health", "jp_name": "健康", "emoji": "🏥"},
        {"name": "entertainment", "jp_name": "エンタメ", "emoji": "🎬"},
        {"name": "sports", "jp_name": "スポーツ", "emoji": "⚽"},
        {"name": "politics", "jp_name": "政治", "emoji": "🏛️"},
        {"name": "other", "jp_name": "その他", "emoji": "📌"},
    ],
    # UI設定
    "embed_color": 3447003,  # Embedのカラー（青色）
    "use_thumbnails": True,  # サムネイルを使用するか
    # ログ設定
    "log_level": "INFO",  # ログレベル
    "log_file": "data/bot.log",  # ログファイル
}
