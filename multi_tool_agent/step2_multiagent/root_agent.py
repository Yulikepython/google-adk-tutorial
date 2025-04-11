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
    load_environment_variables,
    get_weather_stateful
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
        tools=[get_weather_stateful],
        # ルートエージェントの下に全てのサブエージェントを設定
        sub_agents=[
            greeting_agent,
            weather_agent_gpt,
            weather_agent_claude,
            farewell_agent
        ],
        output_key="last_weather_report"
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


async def run_team_conversation():
    print("\n--- Testing Agent Team Delegation ---")
    # InMemorySessionService is simple, non-persistent storage for this tutorial.
    session_service: InMemorySessionService = InMemorySessionService()

    # Define constants for identifying the interaction context
    APP_NAME = "weather_tutorial_agent_team"
    USER_ID = "user_1_agent_team"
    SESSION_ID = "session_001_agent_team"  # Using a fixed ID for simplicity

    initial_state = {
        "user_preference_temperature_unit": "Celsius"
    }
    # Create the specific session where the conversation will happen
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state
    )
    print(
        f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    # Verify the initial state was set correctly
    retrieved_session = session_service.get_session(app_name=APP_NAME,
                                                    user_id=USER_ID,
                                                    session_id=SESSION_ID)
    print("\n--- session ---")
    print(session)
    print("\n--- session until here ---")
    print("\n--- Initial Session State ---")
    if retrieved_session:
        print(retrieved_session.state)
    else:
        print("Error: Could not retrieve session.")

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
    # 1. Check weather (Uses initial state: Celsius)
    print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
    await call_agent_async(query="What's the weather in London?",
                           runner=runner_agent_team,
                           user_id=USER_ID,
                           session_id=SESSION_ID
                           )
    # 2. Manually update state preference to Fahrenheit - DIRECTLY MODIFY STORAGE
    print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
    try:
        # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
        stored_session = session_service.sessions[APP_NAME][USER_ID][SESSION_ID]
        stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
        # Optional: You might want to update the timestamp as well if any logic depends on it
        # import time
        # stored_session.last_update_time = time.time()
        print(
            f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state['user_preference_temperature_unit']} ---")
    except KeyError:
        print(
            f"--- Error: Could not retrieve session '{SESSION_ID}' from internal storage for user '{USER_ID}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
    except Exception as e:
        print(f"--- Error updating internal session state: {e} ---")

    # 3. Check weather again (Tool should now use Fahrenheit)
    # This will also update 'last_weather_report' via output_key
    print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
    await call_agent_async(query="What is the weather in New York?",
                           runner=runner_agent_team,
                           user_id=USER_ID,
                           session_id=SESSION_ID)
    await call_agent_async(query="Thanks, bye!",
                           runner=runner_agent_team,
                           user_id=USER_ID,
                           session_id=SESSION_ID)

    print("\n--- Inspecting Final Session State ---")
    final_session = session_service.get_session(app_name=APP_NAME,
                                                user_id=USER_ID,
                                                session_id=SESSION_ID)
    if final_session:
        print(
            f"Final Preference: {final_session.state.get('user_preference_temperature_unit')}")
        print(
            f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report')}")
        print(
            f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful')}")
        # Print full state for detailed view
        # print(f"Full State: {final_session.state}")
    else:
        print("\n❌ Error: Could not retrieve final session state.")

# 非同期関数を実行するための正しい方法
if __name__ == "__main__":
    asyncio.run(run_team_conversation())
