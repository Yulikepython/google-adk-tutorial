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

MODEL_GPT_4O = "gpt-4o"

# LiteLLM: https://docs.litellm.ai/docs/


def create_gpt_weather_agent():
    """GPT-4oを使用する天気エージェントを作成します。"""

    return Agent(
        name="weather_agent_gpt",
        # 重要な変更: LiteLlmでモデル識別子をラップ
        model=LiteLlm(model=MODEL_GPT_4O),
        description="Provides weather information (using GPT-4o).",
        instruction="You are a helpful weather assistant powered by GPT-4o. "
        "Use the 'get_weather' tool for city weather requests. "
        "Clearly present successful reports or polite error messages based on the tool's output status.",
        tools=[get_weather],  # 同じツールを再利用
    )


async def run_gpt_agent():
    """非同期で実行するメイン関数"""
    # --- GPT-4oを使用するエージェント ---
    weather_agent_gpt = None  # Noneで初期化
    runner_gpt = None      # ランナーをNoneで初期化
    try:

        # GPT-4o用のエージェントを作成
        weather_agent_gpt = create_gpt_weather_agent()
        print(
            f"Agent '{weather_agent_gpt.name}' created using model '{MODEL_GPT_4O}'.")

        # このテスト用の一意のアプリ名
        app_name_gpt = "weather_tutorial_app_gpt_with_lite_llm"
        user_id_gpt_with_litellm = "user_1_gpt"
        session_id_gpt_with_litellm = "session_001_gpt"  # シンプルさのために固定IDを使用

        # セッションとランナーを設定
        _, runner_gpt, _ = setup_session(
            weather_agent_gpt,
            app_name_gpt,
            user_id_gpt_with_litellm,
            session_id_gpt_with_litellm
        )

        # --- GPTエージェントをテスト ---
        print("\n--- Testing GPT Agent ---")
        # 正しいランナー、ユーザーID、セッションIDを使用してcall_agent_asyncを呼び出す
        await call_agent_async(
            runner=runner_gpt,
            user_id=user_id_gpt_with_litellm,
            session_id=session_id_gpt_with_litellm,
            query="What's the weather in Tokyo?"
        )

    except Exception as e:
        print(
            f"❌ Could not create or run GPT agent '{MODEL_GPT_4O}'. Check API Key and model name. Error: {e}")


def main():
    """エントリーポイント: 非同期関数を実行します"""
    asyncio.run(run_gpt_agent())


if __name__ == "__main__":
    main()
