import os
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent

# 共通モジュールからインポート
from ..common import (
    load_environment_variables
)

# 親ディレクトリの.envファイルを読み込む
parent_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(parent_dir, ".env")
load_environment_variables(dotenv_path=dotenv_path)

# LiteLLM: https://docs.litellm.ai/docs/

MODEL_GPT_4O = "gpt-4o"  # GPT-4oのモデル識別子

# @title Define Tools for Greeting and Farewell Agents

# Ensure 'get_weather' from Step 1 is available if running this step independently.
# def get_weather(city: str) -> dict: ... (from Step 1)


def say_hello(name: str = "there") -> str:
    """Provides a simple greeting, optionally addressing the user by name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to "there".

    Returns:
        str: A friendly greeting message.
    """
    print(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"


def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print("--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."


# @title Define Greeting and Farewell Sub-Agents

# Ensure LiteLlm is imported and API keys are set (from Step 0/2)
# from google.adk.models.lite_llm import LiteLlm
# MODEL_GPT_4O, MODEL_CLAUDE_SONNET etc. should be defined

# --- Greeting Agent ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=LiteLlm(model=MODEL_GPT_4O),
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        # Crucial for delegation
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(
        f"✅ Agent '{greeting_agent.name}' created using model '{MODEL_GPT_4O}'.")
except Exception as e:
    print(
        f"❌ Could not create Greeting agent. Check API Key ({MODEL_GPT_4O}). Error: {e}")

# --- Farewell Agent ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # Can use the same or a different model
        # Sticking with GPT for this example
        model=LiteLlm(model=MODEL_GPT_4O),
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        # Crucial for delegation
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],

    )
    print(
        f"✅ Agent '{farewell_agent.name}' created using model '{MODEL_GPT_4O}'.")
except Exception as e:
    print(
        f"❌ Could not create Farewell agent. Check API Key ({MODEL_GPT_4O}). Error: {e}")


# エージェントインスタンスをインポート可能な状態とするヘルパー関数
def get_greeting_agent():
    """Greeting Agentのインスタンスを返します。

    Returns:
        Agent: Greeting Agentのインスタンス、または作成に失敗した場合はNone
    """
    return greeting_agent


def get_farewell_agent():
    """Farewell Agentのインスタンスを返します。

    Returns:
        Agent: Farewell Agentのインスタンス、または作成に失敗した場合はNone
    """
    return farewell_agent
