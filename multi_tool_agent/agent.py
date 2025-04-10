import datetime
from zoneinfo import ZoneInfo
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types  # For creating message Content/Parts

from dotenv import load_dotenv
load_dotenv()


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    # Best Practice: Log tool execution for easier debugging
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")  # Basic input normalization

    # Mock weather data for simplicity
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    # Best Practice: Handle potential errors gracefully within the tool
    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
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


def create_weather_agent():
    """Creates and configures the weather agent with tools."""
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


def setup_session(app_name, user_id, session_id):
    """Sets up and returns the session service and runner.

    Args:
        app_name (str): Application identifier
        user_id (str): User identifier
        session_id (str): Session identifier

    Returns:
        tuple: (session_service, runner, session)
    """
    # Session management
    session_service = InMemorySessionService()

    # Create the specific session where the conversation will happen
    session = session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    print(
        f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")

    # Create agent
    weather_agent = create_weather_agent()

    # Runner setup
    runner = Runner(
        agent=weather_agent,
        app_name=app_name,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    return session_service, runner, session


async def call_agent_async(runner, user_id, session_id, query: str):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:  # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")


async def run_conversation(runner, user_id, session_id):
    """Runs a sample conversation with the agent."""
    await call_agent_async(runner, user_id, session_id, "What is the weather like in London?")
    # Expecting the tool's error message
    await call_agent_async(runner, user_id, session_id, "How about Paris?")
    await call_agent_async(runner, user_id, session_id, "Tell me the weather in New York")


def main():
    """Main function to run the weather agent."""
    # Define constants for identifying the interaction context
    app_name = "weather_tutorial_app"
    user_id = "user_1"  # Changed USER_ID to user_id for consistency
    session_id = "session_001"  # Using a fixed ID for simplicity

    # Setup session and runner
    _, runner, _ = setup_session(app_name, user_id, session_id)

    # Run the conversation (asyncio.run for top-level code)
    asyncio.run(run_conversation(runner, user_id, session_id))


if __name__ == "__main__":
    main()
