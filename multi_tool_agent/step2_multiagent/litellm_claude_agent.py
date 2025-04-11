import os
import asyncio
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent

# 共通モジュールからインポート
from ..common import (
    get_weather,
    setup_session,
    call_agent_async,
    load_environment_variables
)

# 親ディレクトリの.envファイルを読み込む
parent_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(parent_dir, ".env")
load_environment_variables(dotenv_path=dotenv_path)

# LiteLLM: https://docs.litellm.ai/docs/

MODEL_CLAUDE_SONNET = "claude-3-sonnet-20240229"  # Claude Sonnetのモデル識別子


def create_claude_weather_agent():
    """Claude Sonnetを使用する天気エージェントを作成します。"""
    return Agent(
        name="weather_agent_claude",
        # 重要な変更: LiteLlmでモデル識別子をラップ
        model=LiteLlm(model=MODEL_CLAUDE_SONNET),
        description="Provides weather information (using Claude Sonnet).",
        instruction="You are a helpful weather assistant powered by Claude Sonnet. "
        "Use the 'get_weather' tool for city weather requests. "
        "Analyze the tool's dictionary output ('status', 'report'/'error_message'). "
        "Clearly present successful reports or polite error messages.",
        tools=[get_weather],  # 同じツールを再利用
    )


async def run_claude_agent():
    """非同期で実行するメイン関数"""
    # --- Claude Sonnetを使用するエージェント ---
    weather_agent_claude = None  # Noneで初期化
    runner_claude = None      # ランナーをNoneで初期化
    try:

        # Claude Sonnet用のエージェントを作成
        weather_agent_claude = create_claude_weather_agent()
        print(
            f"Agent '{weather_agent_claude.name}' created using model '{MODEL_CLAUDE_SONNET}'.")

        # このテスト用の一意のアプリ名
        app_name_claude_with_litellm = "weather_tutorial_app_claude"
        user_id_claude = "user_1_claude"
        session_id_claude = "session_001_claude"  # シンプルさのために固定IDを使用

        # セッションとランナーを設定
        _, runner_claude, _ = setup_session(
            weather_agent_claude,
            app_name_claude_with_litellm,
            user_id_claude,
            session_id_claude
        )

        # --- Claudeエージェントをテスト ---
        print("\n--- Testing Claude Agent ---")
        # 正しいランナー、ユーザーID、セッションIDを使用してcall_agent_asyncを呼び出す
        await call_agent_async(
            runner=runner_claude,
            user_id=user_id_claude,
            session_id=session_id_claude,
            query="Weather in London please."
        )

    except Exception as e:
        print(
            f"❌ Could not create or run Claude agent '{MODEL_CLAUDE_SONNET}'. Check API Key and model name. Error: {e}")


def main():
    """エントリーポイント: 非同期関数を実行します"""
    asyncio.run(run_claude_agent())


if __name__ == "__main__":
    main()
