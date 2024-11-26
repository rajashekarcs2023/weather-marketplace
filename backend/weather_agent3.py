from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from flask import Flask, request
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
weather_identity = None
claude = None

def create_graph():
    global claude
    claude = ChatAnthropic(
        model="claude-3-sonnet-20240229",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_data().decode("utf-8")
        message = parse_message_from_agent(data)
        location = message.payload.get("location", "")

        if not location:
            return {"status": "error", "message": "No location provided"}

        prompt = f"What's the weather like in {location}? Give a brief, natural response with one recommendation and a date idea in this weather"
        response = claude.invoke([HumanMessage(content=prompt)])

        response_payload = {
            "location": location,
            "analysis": response.content,
            "price": 2.99  # Including price in response
        }

        result = send_message_to_agent(
            weather_identity,
            message.sender,
            response_payload
        )

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

def init_app():
    global weather_identity
    try:
        weather_identity = Identity.from_seed(os.getenv("WEATHER_KEY3"), 0)
        create_graph()

        readme = """
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
            <price>2.99</price>
            <currency>USD</currency>
            <per_request>true</per_request>
        </pricing>
        """

        register_with_agentverse(
            identity=weather_identity,
            url="http://localhost:5006/webhook",  # Change port for each agent
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Luxury Weather Assistant",
            readme=readme
        )

        logger.info("Agent initialization complete!")

    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        raise

if __name__ == "__main__":
    load_dotenv()
    init_app()
    app.run(host="0.0.0.0", port=5006)  # Change port for each agent