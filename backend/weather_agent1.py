import os
import logging
import asyncio
from flask import Flask, request, jsonify
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask app for webhook
flask_app = Flask(__name__)

# Global variables
weather_identity = None
claude = None

async def create_chat():
    """Initialize the ChatAnthropic instance"""
    global claude
    claude = ChatAnthropic(
        model="claude-3-sonnet-20240229",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7
    )

async def get_weather_analysis(location):
    """Get weather analysis from Claude"""
    prompt = f"What's the weather like in {location}? Give a brief, natural response with one recommendation."
    response = claude.invoke([HumanMessage(content=prompt)])
    return response.content

# Flask route to handle webhook
@flask_app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        # Parse the incoming message
        data = request.get_data().decode('utf-8')
        message = parse_message_from_agent(data)
        location = message.payload.get("location", "")
        agent_address = message.sender

        if not location:
            return jsonify({"status": "error", "message": "No location provided"}), 400

        # Get weather analysis
        analysis = await get_weather_analysis(location)

        # Prepare and send response
        payload = {
            "location": location,
            "analysis": analysis,
            "price": 0.99
        }

        send_message_to_agent(
            weather_identity,
            agent_address,
            payload
        )

        return jsonify({"status": "success"})

    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Initialize the agent
def init_agent():
    global weather_identity
    try:
        weather_identity = Identity.from_seed(os.getenv("WEATHER_KEY1"), 0)
        asyncio.run(create_chat())

        register_with_agentverse(
            identity=weather_identity,
            url="http://localhost:5009/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Budget Weather Assistant",
            readme="""
            <description>AI weather assistant providing detailed weather analysis and recommendations</description>
            <use_cases>
                <use_case>Get current weather conditions and recommendations</use_case>
            </use_cases>
            <payload_requirements>
                <description>Requirements for weather requests</description>
                <payload>
                    <requirement>
                        <parameter>location</parameter>
                        <description>The city or location to get weather for</description>
                    </requirement>
                </payload>
            </payload_requirements>
            <pricing>
                <price>0.99</price>
                <currency>USD</currency>
                <per_request>true</per_request>
            </pricing>
            """
        )

        logger.info("Weather agent initialized successfully!")

    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        raise

# Run Flask server
if __name__ == "__main__":
    init_agent()
    flask_app.run(host="0.0.0.0", port=5009, debug=True)
