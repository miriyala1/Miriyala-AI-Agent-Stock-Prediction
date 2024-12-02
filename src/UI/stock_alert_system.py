# src/UI/stock_alert_system.py

import time
import logging
from yahooquery import Ticker
from src.Agents.Alert_agent.alert_agent import AlertAgent
from src.Helpers.notification import send_email, send_sms_alert

# Configure logging
logging.basicConfig(
    filename='stock_alert_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StockAlertSystem:
    def __init__(self, stock, threshold, notify_email=False, notify_sms=False):
        self.stock = stock
        self.threshold = threshold
        self.notify_email = notify_email
        self.notify_sms = notify_sms
        self.alert_agent = AlertAgent()
        self.monitoring = False
        self.recipient_email = None
        self.recipient_phone = None
        print(f"Initialized StockAlertSystem for {self.stock} with threshold {self.threshold}%.")
        logging.info(f"Initialized StockAlertSystem for {self.stock} with threshold {self.threshold}%.")
    
    def fetch_stock_data(self):
        ticker = Ticker(self.stock)
        history = ticker.history(period='1d', interval='1m')
        if history.empty:
            print(f"No data fetched for {self.stock}.")
            logging.warning(f"No data fetched for {self.stock}.")
        return history
    
    def monitor_stock(self):
        previous_close = None
        self.monitoring = True
        print(f"Started monitoring {self.stock} with threshold {self.threshold}%")
        logging.info(f"Started monitoring {self.stock} with threshold {self.threshold}%")
        while self.monitoring:
            try:
                stock_data = self.fetch_stock_data()

                if stock_data.empty:
                    print(f"No data fetched for {self.stock}. Retrying in 60 seconds.")
                    logging.warning(f"No data fetched for {self.stock}. Retrying in 60 seconds.")
                    time.sleep(60)
                    continue

                latest_price = stock_data['close'].iloc[-1]
                print(f"Latest price fetched: {latest_price}")
                logging.debug(f"Latest price fetched: {latest_price}")

                if previous_close:
                    change = ((latest_price - previous_close) / previous_close) * 100
                    print(f"Previous close: {previous_close}, Change: {change}%")
                    logging.debug(f"Previous close: {previous_close}, Change: {change}%")

                    if abs(change) >= self.threshold:
                        stock_recent_data = stock_data.tail(1).to_dict()
                        print("Greater than threshold")
                        print(stock_recent_data)
                        # Uncomment the following lines if you want to use OpenAI for analysis
                        # analysis = self.alert_agent.analyze_stock_changes(stock_recent_data)
                        # print(analysis)
                        subject = f"Stock Alert for {self.stock}"
                        print(subject)
                        message = f"Price change of {self.stock}: {change:.4f}%"
                        print(message)

                        recipients = []
                        
                        # Send Email Alert
                        if self.notify_email and self.recipient_email:
                            recipients.append(self.recipient_email)
                            send_email(subject, message, recipients)
                            print(f"Email alert sent for {self.stock}: Change {change:.4f}%")
                            logging.info(f"Email alert sent for {self.stock}: Change {change:.4f}%")
                        
                        # Send SMS Alert
                        if self.notify_sms or self.recipient_phone:
                            send_sms_alert(message, self.recipient_phone)
                            print(f"SMS alert sent for {self.stock}: Change {change:.4f}%")
                            logging.info(f"SMS alert sent for {self.stock}: Change {change:.4f}%")
                        
                        if recipients or (self.notify_sms and self.recipient_phone):
                            print(f"Alert sent for {self.stock}: Change {change:.4f}%")
                            logging.info(f"Alert sent for {self.stock}: Change {change:.4f}%")

                previous_close = latest_price
                logging.info(f"Monitoring {self.stock}: Current price {latest_price}")
                time.sleep(60)
            except Exception as e:
                logging.error(f"An error occurred in monitor_stock: {e}")
                time.sleep(60)

    def stop_monitoring(self):
        self.monitoring = False
        print(f"Stopped monitoring {self.stock}")
        logging.info(f"Stopped monitoring {self.stock}")
