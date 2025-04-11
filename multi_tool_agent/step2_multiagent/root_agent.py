# @title Interact with the Agent Team
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# 共通モジュールからインポート
from ..common import (
    get_weather,
    call_agent_async,
    load_environment_variables
)

# サブエージェントをインポート
from .sub_agents import get_greeting_agent, get_farewell_agent
from .litellm_openai_agent import create_gpt_weather_agent
from .litellm_claude_agent import create_claude_weather_agent

# 親ディレクトリの.envファイルを読み込む
parent_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(parent_dir, ".env")
load_environment_variables(dotenv_path=dotenv_path)

# ルートエージェント (weather_agent_team) を定義
# これはGPT-4oを使用してユーザークエリを処理し、適切なサブエージェントに委任します
MODEL_GPT_4O = "gpt-4o"

# サブエージェントのインスタンスを取得
greeting_agent = get_greeting_agent()
farewell_agent = get_farewell_agent()
weather_agent_gpt = create_gpt_weather_agent()
weather_agent_claude = create_claude_weather_agent()

# ルートエージェントを作成
root_agent = None
try:
    root_agent = Agent(
        name="weather_agent_team",
        model=LiteLlm(model=MODEL_GPT_4O),
        description="A router agent that handles different types of queries by delegating to specialized sub-agents.",
        instruction="""You are a router agent that delegates tasks to specialized sub-agents.
        - For greetings and hello messages, delegate to the greeting_agent.
        - For weather questions, delegate to either weather_agent_gpt or weather_agent_claude.
        - For farewell messages and conversation endings, delegate to the farewell_agent.
        
        Always delegate to the most appropriate sub-agent rather than trying to handle queries yourself.
        """,
        # ルートエージェントの下に全てのサブエージェントを設定
        sub_agents=[
            greeting_agent,
            weather_agent_gpt,
            weather_agent_claude,
            farewell_agent
        ],
        tools=[get_weather],  # 冗長ですが、安全のために
    )
    print(f"✅ Root agent '{root_agent.name}' created successfully.")
except Exception as e:
    print(f"❌ Could not create Root agent. Error: {e}")
    root_agent = None

# Check if the root agent variable exists before defining the conversation function
root_agent_var_name = 'root_agent'  # Default name from Step 3 guide
if 'weather_agent_team' in globals():  # Check if user used this name instead
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")
    # Assign a dummy value to prevent NameError later if the code block runs anyway
    root_agent = None

if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    async def run_team_conversation():
        print("\n--- Testing Agent Team Delegation ---")
        # InMemorySessionService is simple, non-persistent storage for this tutorial.
        session_service = InMemorySessionService()

        # Define constants for identifying the interaction context
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"  # Using a fixed ID for simplicity

        # Create the specific session where the conversation will happen
        session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        print(
            f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        # --- Get the actual root agent object ---
        # Use the determined variable name
        actual_root_agent = globals()[root_agent_var_name]

        # Create a runner specific to this agent team test
        runner_agent_team = Runner(
            agent=actual_root_agent,  # Use the root agent object
            app_name=APP_NAME,       # Use the specific app name
            session_service=session_service  # Use the specific session service
        )
        # Corrected print statement to show the actual root agent's name
        print(f"Runner created for agent '{actual_root_agent.name}'.")

        # Always interact via the root agent's runner, passing the correct IDs
        await call_agent_async(query="Hello there!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query="What is the weather in New York?",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query="Thanks, bye!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)

    # 非同期関数を実行するための正しい方法
    if __name__ == "__main__":
        asyncio.run(run_team_conversation())
else:
    print("\n⚠️ Skipping agent team conversation as the root agent was not successfully defined in the previous step.")
