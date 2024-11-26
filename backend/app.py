from flask import Flask, request, jsonify
from flask_cors import CORS
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
from fetchai import fetch
import logging
import os
import threading
import time
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)

CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

client_identity = None
weather_response = None
responses_received = 0

def init_client():
    """Initialize and register the client agent"""
    global client_identity
    try:
        client_identity = Identity.from_seed(os.getenv("CLIENT_KEY3"), 0)
        logger.info(f"Client agent started with address: {client_identity.address}")
        
        readme = """
        <description>Frontend client that requests weather information</description>
        <use_cases>
            <use_case>Receive and display weather reports</use_case>
        </use_cases>
        <payload_requirements>
            <description>Expects weather information responses</description>
            <payload>
                <requirement>
                    <parameter>location</parameter>
                    <description>The location of the weather report</description>
                </requirement>
            </payload>
        </payload_requirements>
        """
        
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5001/api/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Weather Frontend Client",
            readme=readme
        )
        
        logger.info("Client agent registration complete!")
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

@app.route('/api/search-agents')
def search_agents():
    """Search for available weather agents"""
    try:
        logger.info("Searching for weather agents...")
        available_ais = fetch.ai("weather forecast analysis recommendations")
        agents = available_ais.get('agents', [])
        
        weather_agents = []
        logger.info("\nAvailable Weather Agents:")
        
        for agent in agents:
            if "weather" in agent.get('name', '').lower():
                readme = agent.get('readme', '')
                try:
                    price_start = readme.index('<price>') + 7
                    price_end = readme.index('</price>')
                    price = float(readme[price_start:price_end])
                    
                    agent_info = {
                        "name": agent.get('name'),
                        "price": price,
                        "address": agent.get('address')
                    }
                    weather_agents.append(agent_info)
                    logger.info(f"Found agent: {agent_info}")
                except (ValueError, IndexError):
                    continue
        
        if not weather_agents:
            logger.error("No weather agents found")
            return jsonify({"error": "No weather agents available"}), 404
            
        return jsonify({"agents": weather_agents})
        
    except Exception as e:
        logger.error(f"Error finding agents: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-weather', methods=['POST'])
def get_weather():
    """Send weather request to selected agent"""
    global weather_response
    weather_response = None
    
    try:
        data = request.json
        location = data.get('location')
        agent_address = data.get('agentAddress')
        
        if not location or not agent_address:
            return jsonify({"error": "Missing location or agent address"}), 400
            
        logger.info(f"Sending weather request for {location} to {agent_address}")
        
        payload = {"location": location}
        send_message_to_agent(
            client_identity,
            agent_address,
            payload
        )
        
        return jsonify({"status": "request_sent"})
        
    except Exception as e:
        logger.error(f"Error sending weather request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-weather-response')
def get_weather_response():
    """Get the most recent weather response"""
    global weather_response
    try:
        if weather_response:
            response = weather_response
            weather_response = None
            return jsonify(response)
        return jsonify({"status": "waiting"})
    except Exception as e:
        logger.error(f"Error getting weather response: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle incoming messages from weather agents"""
    global weather_response, responses_received
    try:
        data = request.get_data().decode("utf-8")
        logger.info("Received weather response")
        
        message = parse_message_from_agent(data)
        weather_response = message.payload
        responses_received += 1
        
        logger.info(f"Processed weather response: {weather_response}")
        return jsonify({"status": "success"})
        
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500

def start_server():
    """Start the Flask server"""
    try:
        load_dotenv()
        init_client()
        app.run(host="0.0.0.0", port=5001)
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    start_server()