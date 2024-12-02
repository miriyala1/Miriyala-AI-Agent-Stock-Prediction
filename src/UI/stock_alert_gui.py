# src/UI/stock_alert_gui.py

import tkinter as tk
from tkinter import messagebox
import threading
import logging
from src.UI.stock_alert_system import StockAlertSystem
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='stock_alert_gui.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StockAlertGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Alert System")

        # Stock ticker input
        self.label_stock = tk.Label(root, text="Enter Stock Ticker:")
        self.label_stock.grid(row=0, column=0, padx=10, pady=10)
        self.entry_stock = tk.Entry(root)
        self.entry_stock.grid(row=0, column=1, padx=10, pady=10)

        # Threshold input
        self.label_threshold = tk.Label(root, text="Enter Threshold (%):")
        self.label_threshold.grid(row=1, column=0, padx=10, pady=10)
        self.entry_threshold = tk.Entry(root)
        self.entry_threshold.grid(row=1, column=1, padx=10, pady=10)

        # Recipient Email input
        self.label_recipient_email = tk.Label(root, text="Recipient Email:")
        self.label_recipient_email.grid(row=2, column=0, padx=10, pady=10)
        self.entry_recipient_email = tk.Entry(root)
        self.entry_recipient_email.grid(row=2, column=1, padx=10, pady=10)

        # Recipient Phone Number input
        self.label_recipient_phone = tk.Label(root, text="Recipient Phone:")
        self.label_recipient_phone.grid(row=3, column=0, padx=10, pady=10)
        self.entry_recipient_phone = tk.Entry(root)
        self.entry_recipient_phone.grid(row=3, column=1, padx=10, pady=10)

        # Email/SMS alert options
        self.var_email = tk.BooleanVar()
        self.checkbox_email = tk.Checkbutton(root, text="Email Alert", variable=self.var_email)
        self.checkbox_email.grid(row=4, column=0, padx=10, pady=10)

        self.var_sms = tk.BooleanVar()
        self.checkbox_sms = tk.Checkbutton(root, text="SMS Alert", variable=self.var_sms)
        self.checkbox_sms.grid(row=4, column=1, padx=10, pady=10)

        # Status label
        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        # Start button
        self.button_start = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.button_start.grid(row=6, column=0, padx=10, pady=10)

        # Stop button
        self.button_stop = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.button_stop.grid(row=6, column=1, padx=10, pady=10)

        self.alert_system = None
        self.alert_thread = None

    def start_monitoring(self):
        stock = self.entry_stock.get().strip().upper()
        threshold = self.entry_threshold.get().strip()
        notify_email = self.var_email.get()
        notify_sms = self.var_sms.get()
        recipient_email = self.entry_recipient_email.get().strip()
        recipient_phone = self.entry_recipient_phone.get().strip()

        if not stock or not threshold:
            messagebox.showwarning("Input Error", "Please enter stock ticker and threshold.")
            logging.warning("Start monitoring failed: Missing stock ticker or threshold.")
            return

        if notify_email and not recipient_email:
            messagebox.showwarning("Input Error", "Please enter recipient email for email alerts.")
            logging.warning("Start monitoring failed: Missing recipient email.")
            return

        if notify_sms and not recipient_phone:
            messagebox.showwarning("Input Error", "Please enter recipient phone number for SMS alerts.")
            logging.warning("Start monitoring failed: Missing recipient phone number.")
            return

        try:
            threshold = float(threshold)
            if threshold <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid positive number for the threshold.")
            logging.warning("Start monitoring failed: Invalid threshold input.")
            return

        # Validate the stock ticker by attempting to fetch data
        temp_alert_system = StockAlertSystem(stock, threshold, False, False)
        try:
            stock_data = temp_alert_system.fetch_stock_data()
            if stock_data.empty:
                messagebox.showerror("Ticker Error", f"No data found for ticker '{stock}'. Please check the symbol and try again.")
                logging.error(f"Start monitoring failed: No data for ticker '{stock}'.")
                return
        except Exception as e:
            messagebox.showerror("API Error", f"Failed to fetch data for '{stock}': {e}")
            logging.error(f"Start monitoring failed: API error for ticker '{stock}': {e}")
            return

        # Update UI
        self.status_label.config(text="Status: Monitoring...")
        self.button_start.config(state=tk.DISABLED)
        self.button_stop.config(state=tk.NORMAL)

        # Initialize the alert system with user preferences
        self.alert_system = StockAlertSystem(stock, threshold, notify_email, notify_sms)
        self.alert_system.recipient_email = recipient_email  # Set recipient email
        self.alert_system.recipient_phone = recipient_phone  # Set recipient phone

        # Run the alert system in a separate thread
        self.alert_thread = threading.Thread(target=self.run_alert_system, args=(self.alert_system,), daemon=True)
        self.alert_thread.start()
        logging.info(f"Started monitoring thread for {stock}.")

    def stop_monitoring(self):
        if self.alert_system:
            self.alert_system.stop_monitoring()
            logging.info(f"Requested to stop monitoring for {self.alert_system.stock}.")
        self.status_label.config(text="Status: Stopped")
        self.button_start.config(state=tk.NORMAL)
        self.button_stop.config(state=tk.DISABLED)
        logging.info("Monitoring stopped by user.")

    def run_alert_system(self, alert_system):
        alert_system.monitor_stock()
        # Update status when monitoring stops
        self.status_label.config(text="Status: Stopped")
        self.button_start.config(state=tk.NORMAL)
        self.button_stop.config(state=tk.DISABLED)
        logging.info(f"Monitoring thread for {alert_system.stock} has stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = StockAlertGUI(root)
    root.mainloop()
