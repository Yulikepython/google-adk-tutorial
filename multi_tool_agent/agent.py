import asyncio
from google.adk.agents import Agent

# 共通モジュールからインポート
from .common import (
    get_weather,
    get_current_time,
    setup_session,
    call_agent_async,
    run_conversation,
    load_environment_variables
)

# 環境変数の読み込み
load_environment_variables()


def create_weather_agent():
    """天気エージェントを作成し、ツールで構成します。"""
    return Agent(
        name="weather_agent_v1",
        model="gemini-2.0-flash-exp",
        description=(
            "Agent to answer questions about the time and weather in a city."
        ),
        instruction=(
            "I can answer your questions about the time and weather in a city."
        ),
        tools=[get_weather, get_current_time],
    )


def main():
    """天気エージェントを実行するメイン関数。"""
    # インタラクションコンテキストを識別するための定数を定義
    app_name = "weather_tutorial_app"
    user_id = "user_1"
    session_id = "session_001"  # シンプルさのために固定IDを使用

    # エージェントを作成
    weather_agent = create_weather_agent()

    # セッションとランナーを設定
    _, runner, _ = setup_session(weather_agent, app_name, user_id, session_id)

    # サンプルクエリのリスト
    sample_queries = [
        "What is the weather like in London?",
        "How about Paris?",  # ツールのエラーメッセージを期待
        "Tell me the weather in New York"
    ]

    # 会話を実行（トップレベルコードのasyncio.run）
    asyncio.run(run_conversation(runner, user_id, session_id, sample_queries))


if __name__ == "__main__":
    main()
