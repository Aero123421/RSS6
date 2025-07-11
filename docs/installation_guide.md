# Discord RSS Bot インストールガイド

このガイドでは、Discord RSS Botのインストール方法と初期設定について説明します。

## 目次

1. [前提条件](#前提条件)
2. [インストール方法](#インストール方法)
   - [通常インストール](#通常インストール)
   - [Docker環境でのインストール](#docker環境でのインストール)
3. [初期設定](#初期設定)
   - [Discordボットの作成](#discordボットの作成)
   - [環境変数の設定](#環境変数の設定)
   - [設定ファイルの編集](#設定ファイルの編集)
4. [起動方法](#起動方法)
5. [トラブルシューティング](#トラブルシューティング)

## 前提条件

Discord RSS Botを使用するには、以下の前提条件が必要です：

- Python 3.8以上
- Discordアカウントとボットトークン
- （オプション）Google Gemini APIキー

## インストール方法

### 通常インストール

1. リポジトリをクローンします：

```bash
git clone https://github.com/yourusername/discord-rss-bot.git
cd discord-rss-bot
```

2. 仮想環境を作成し、有効化します：

```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
venv\Scripts\activate  # Windowsの場合
```

3. 依存パッケージをインストールします：

```bash
pip install -r requirements.txt
```

4. 環境変数ファイルを作成します：

```bash
cp .env.example .env
```

5. `.env`ファイルを編集して、必要な環境変数を設定します。

### Docker環境でのインストール

1. リポジトリをクローンします：

```bash
git clone https://github.com/yourusername/discord-rss-bot.git
cd discord-rss-bot
```

2. 環境変数ファイルを作成します：

```bash
cp .env.example .env
```

3. `.env`ファイルを編集して、必要な環境変数を設定します。

4. Dockerコンテナをビルドして起動します：

```bash
docker-compose up -d
```

## 初期設定

### Discordボットの作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセスします。

2. 「New Application」をクリックして、新しいアプリケーションを作成します。

3. 「Bot」タブをクリックし、「Add Bot」をクリックしてボットを作成します。

4. 「Reset Token」をクリックして、ボットトークンを取得します。このトークンは`.env`ファイルに設定します。

5. 「OAuth2」タブをクリックし、「URL Generator」を選択します。

6. 以下のスコープとボット権限を選択します：
   - スコープ：`bot`, `applications.commands`
   - ボット権限：`Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`, `Add Reactions`, `Use Slash Commands`, `Manage Channels`

7. 生成されたURLをブラウザで開き、ボットをサーバーに招待します。

### 環境変数の設定

`.env`ファイルに以下の環境変数を設定します：

```
# Discord設定
DISCORD_TOKEN=your_discord_token_here

# Google Gemini API設定（Gemini APIを使用する場合）
# `GEMINI_API_1` と `GEMINI_API_2` にキーを設定すると、
# ボットは奇数日と偶数日で自動的にキーを切り替えます。
# また、1つ目のキーでレート制限に達した場合、
# 自動的に2つ目のキーへ切り替えて再試行します。
# 2つのキーが連続でレート制限に達した場合は30秒待機します。
# ニュースはキューに貯められ、10秒間隔でAPIに送信されます。
GEMINI_API_1=
GEMINI_API_2=
# 1つだけ指定する場合は GEMINI_API_KEY を使用
# GEMINI_API_KEY=your_gemini_api_key_here


または、Discordのスラッシュコマンド`/rss_config`を使用して、ボットの設定を行うこともできます。

## 起動方法

### 通常インストールの場合

```bash
python bot.py
```

### Docker環境の場合

```bash
docker-compose up -d
```

ボットが正常に起動すると、Discordサーバーでスラッシュコマンドが使用できるようになります。

## トラブルシューティング

### ボットが起動しない場合

1. `.env`ファイルが正しく設定されているか確認してください。
2. ログファイル（`data/bot.log`）を確認して、エラーメッセージを確認してください。
3. Discordボットトークンが有効であることを確認してください。

### スラッシュコマンドが表示されない場合

1. ボットが正常に起動しているか確認してください。
2. ボットをサーバーに再招待してみてください。
3. Discordのキャッシュをクリアしてみてください。

### RSSフィードが取得できない場合

1. フィードURLが有効であることを確認してください。
2. ネットワーク接続を確認してください。
3. フィードのフォーマットがRSSまたはAtomであることを確認してください。

### AI処理が機能しない場合

1. Google Gemini APIキーが正しいことを確認してください。
2. APIキーが有効であることを確認してください。

