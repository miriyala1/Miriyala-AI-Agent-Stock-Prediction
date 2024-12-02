# src/Agents/Alert_agent/alert_agent.py

import openai
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='alert_agent.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AlertAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logging.error("OPENAI_API_KEY is not set in environment variables.")
            raise ValueError("OPENAI_API_KEY is not set in environment variables.")
        openai.api_key = self.api_key
        logging.info("AlertAgent initialized successfully.")
    
    def analyze_stock_changes(self, stock_data):
        try:
            # Format stock data for better readability
            formatted_data = ""
            for key, values in stock_data.items():
                formatted_data += f"{key.capitalize()}:\n"
                for idx, val in enumerate(values):
                    formatted_data += f"  Point {idx + 1}: {val}\n"
                formatted_data += "\n"
            
            prompt = f"Analyze the following stock changes and provide insights:\n{formatted_data}"
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Stock Alert Analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                n=1,
                stop=None,
                temperature=0.5
            )
            analysis = response.choices[0].message['content'].strip()
            logging.info("Stock changes analyzed successfully.")
            return analysis
        except Exception as e:
            logging.error(f"Error in analyze_stock_changes: {e}")
            raise e
