# Google ADK Tutorial

This repository contains a practical implementation of the Google AI Development Kit (ADK) tutorial, restructured to be executable as Python files. The project demonstrates how to build and implement multi-tool agents and multi-agent systems using Google's AI technologies.

## Overview

The Google ADK Tutorial provides a hands-on approach to:

- Creating AI agents with access to tools
- Setting up multi-agent systems with delegation
- Managing agent state and session handling
- Implementing guardrails for safer AI interactions
- Working with different LLMs (Gemini, GPT, Claude) through a unified interface

## Project Structure

- `multi_tool_agent/agent.py`: Basic weather and time agent implementation
- `multi_tool_agent/common.py`: Shared utilities, tool functions, and session handling
- `multi_tool_agent/guardrails.py`: Safety guardrails implementation
- `multi_tool_agent/step2_multiagent/`: Multi-agent system implementation
  - Root agent and specialized sub-agents
  - Integration with OpenAI and Claude models through LiteLLM

## Getting Started

### Prerequisites

- Python 3.9+
- Google ADK library
- API keys for Google (Gemini), OpenAI, and/or Claude (optional)

### Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install google-adk litellm python-dotenv
   ```
3. Create a `.env` file in the project root with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

### Running the Examples

#### Basic Weather Agent

```bash
python -m multi_tool_agent.agent
```

#### Multi-Agent System

```bash
python -m multi_tool_agent.step2_multiagent.root_agent
```

## Key Features

- **Tool Integration**: Weather and time tools with proper error handling
- **Stateful Tools**: Tools that can read and write session state
- **Multi-Agent Architecture**: Root agent that delegates to specialized sub-agents
- **Model Flexibility**: Use different LLM providers in the same application
- **Guardrails**: Implementation of safety checks before model calls and tool usage

## Additional Resources

- [Google AI Development Kit Documentation](https://google.github.io/adk-docs/)
- [LiteLLM Documentation](https://github.com/BerriAI/litellm)

## License

MIT License - see the [LICENSE](LICENSE) file for details.

---

# Google ADK チュートリアル

このリポジトリは、Google AI Development Kit (ADK) チュートリアルの実用的な実装を含み、Python ファイルとして実行可能な形に再構成されています。このプロジェクトでは、Google の AI 技術を使用したマルチツールエージェントおよびマルチエージェントシステムの構築と実装方法を示しています。

## 概要

Google ADK チュートリアルは以下の内容を実践的に学ぶためのものです：

- ツールにアクセスできる AI エージェントの作成
- 委任機能を持つマルチエージェントシステムの構築
- エージェントの状態とセッション管理
- より安全な AI 交互作用のためのガードレールの実装
- 統一インターフェースを通じた異なる LLM（Gemini、GPT、Claude）との連携

## プロジェクト構造

- `multi_tool_agent/agent.py`: 基本的な天気と時間のエージェント実装
- `multi_tool_agent/common.py`: 共有ユーティリティ、ツール関数、およびセッション処理
- `multi_tool_agent/guardrails.py`: 安全性ガードレールの実装
- `multi_tool_agent/step2_multiagent/`: マルチエージェントシステムの実装
  - ルートエージェントと特化型サブエージェント
  - LiteLLM を通じた OpenAI と Claude モデルの統合

## 始め方

### 前提条件

- Python 3.9+
- Google ADK ライブラリ
- Google（Gemini）、OpenAI、および/または Claude（オプション）の API キー

### インストール

1. このリポジトリをクローンします
2. 必要なパッケージをインストールします：
   ```
   pip install google-adk litellm python-dotenv
   ```
3. プロジェクトのルートに `.env` ファイルを作成し、API キーを設定します：
   ```
   GOOGLE_API_KEY=your_google_api_key
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

### サンプルの実行

#### 基本的な天気エージェント

```bash
python -m multi_tool_agent.agent
```

#### マルチエージェントシステム

```bash
python -m multi_tool_agent.step2_multiagent.root_agent
```

## 主な機能

- **ツール統合**: 適切なエラー処理を伴う天気と時間のツール
- **状態を持つツール**: セッション状態を読み書きできるツール
- **マルチエージェントアーキテクチャ**: 特化型サブエージェントに委任するルートエージェント
- **モデルの柔軟性**: 同一アプリケーション内で異なる LLM プロバイダーを使用
- **ガードレール**: モデル呼び出しとツール使用前の安全性チェック実装

## 追加リソース

- [Google AI Development Kit Documentation](https://google.github.io/adk-docs/)
- [LiteLLM Documentation](https://github.com/BerriAI/litellm)

## ライセンス

MIT ライセンス - 詳細は [LICENSE](LICENSE) ファイルを参照してください。
