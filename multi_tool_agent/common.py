"""
共通のエージェント機能とツールを提供するモジュール
このモジュールは複数のエージェント実装で再利用可能な機能を提供します
"""
import datetime
from zoneinfo import ZoneInfo
from typing import Optional
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse


from google.genai import types  # For creating message Content/Parts

from dotenv import load_dotenv
import os

# 環境変数の読み込み


def load_environment_variables(dotenv_path=None):
    """
    環境変数を.envファイルから読み込みます。

    Args:
        dotenv_path: .envファイルのパス（指定しない場合はデフォルトの場所から読み込み）
    """
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path)
    else:
        load_dotenv()


# ツール関数
def get_weather(city: str) -> dict:
    """特定の都市の現在の天気レポートを取得します。

    Args:
        city (str): 都市名（例："New York", "London", "Tokyo"）。

    Returns:
        dict: 天気情報を含む辞書。
              'status'キー（'success'または'error'）を含みます。
              'success'の場合、'report'キーに天気の詳細が含まれます。
              'error'の場合、'error_message'キーが含まれます。
    """
    # ベストプラクティス：デバッグが容易になるようにツールの実行をログに記録
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")  # 基本的な入力の正規化

    # シンプルさのためのモック天気データ
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    # ベストプラクティス：ツール内で潜在的なエラーを適切に処理
    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get(
        "user_preference_temperature_unit", "Celsius")  # Default to Celsius
    print(
        f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32  # Calculate Fahrenheit
            temp_unit = "°F"
        else:  # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(
            f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(
            f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}


def get_current_time(city: str) -> dict:
    """指定された都市の現在時刻を返します。

    Args:
        city (str): 現在時刻を取得する都市の名前。

    Returns:
        dict: ステータスと結果またはエラーメッセージ。
    """
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    elif city.lower() == "tokyo":
        tz_identifier = "Asia/Tokyo"
    elif city.lower() == "london":
        tz_identifier = "Europe/London"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


# エージェントセッションとランナーの設定
def setup_session(agent, app_name, user_id, session_id):
    """セッションサービスとランナーを設定して返します。

    Args:
        agent: 使用するエージェントインスタンス
        app_name (str): アプリケーション識別子
        user_id (str): ユーザー識別子
        session_id (str): セッション識別子

    Returns:
        tuple: (session_service, runner, session)
    """
    # セッション管理
    session_service = InMemorySessionService()

    # 会話が行われる特定のセッションを作成
    session = session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    print(
        f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")

    # ランナーのセットアップ
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    return session_service, runner, session


async def call_agent_async(runner, user_id, session_id, query: str):
    """エージェントにクエリを送信し、最終的な応答を出力します。

    Args:
        runner: エージェントランナー
        user_id: ユーザーID
        session_id: セッションID
        query: ユーザークエリ
    """
    print(f"\n>>> User Query: {query}")

    # ユーザーのメッセージをADK形式で準備
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # デフォルト

    # 重要な概念：run_asyncはエージェントのロジックを実行し、イベントを返します。
    # 最終的な回答を見つけるためにイベントを反復処理します。
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # 以下の行のコメントを解除すると、実行中のすべてのイベントを確認できます
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # 重要な概念：is_final_response()は、ターンの最後のメッセージをマークします。
        if event.is_final_response():
            if event.content and event.content.parts:
                # 最初の部分にテキスト応答があると仮定
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:  # 潜在的なエラー／エスカレーションを処理
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # 必要に応じて、ここに他のチェックを追加します（特定のエラーコードなど）
            break  # 最終応答が見つかったらイベントの処理を停止

    print(f"<<< Agent Response: {final_response_text}")


async def run_conversation(runner, user_id, session_id, queries):
    """エージェントとのサンプル会話を実行します。

    Args:
        runner: エージェントランナー
        user_id: ユーザーID
        session_id: セッションID
        queries: 実行するクエリのリスト
    """
    for query in queries:
        await call_agent_async(runner, user_id, session_id, query)


def simple_print_before_agent_call(callback_context: CallbackContext) -> Optional[types.Content]:
    """print outs the agent name and the query before calling the agent."""
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    print(
        f"[Callback] Entering agent: {agent_name} (Invocation: {invocation_id})")
    print(f"[Callback] user_content: {callback_context.user_content}")
    print(f"[Callback] state: {callback_context.state}")
    print(f"[Callback]: {dir(callback_context)}")


def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name  # Get the name of the agent whose model call is being intercepted
    print(
        f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break  # Found the last user message text

    # Log first 100 chars
    print(
        f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---")

    # --- Guardrail Logic ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper():  # Case-insensitive check
        print(
            f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        # Optionally, set a flag in state to record the block event
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print("--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")

        # Construct and return an LlmResponse to stop the flow and send this back instead
        return LlmResponse(
            content=types.Content(
                role="model",  # Mimic a response from the agent's perspective
                parts=[types.Part(
                    text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
            # Note: You could also set an error_message field here if needed
        )
    else:
        # Keyword not found, allow the request to proceed to the LLM
        print(
            f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
        return None  # Returning None signals ADK to continue normally
