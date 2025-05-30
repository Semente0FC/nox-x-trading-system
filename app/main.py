import sys
import os
import json
import logging
from PyQt5.QtWidgets import QApplication
from datetime import datetime
import threading
import queue
from typing import Dict, Optional

from mt5_connector import MT5Connector
from ai_model import AIModel
from indicators import TechnicalIndicators
from database import Database
from signal_logic import SignalGenerator
from logs import LogManager
from gui import TradingGUI

class TradingSystem:
    def __init__(self):
        """Initialize the trading system"""
        self.load_config()
        self.setup_components()
        self.setup_queues()
        self.setup_threads()
        self.running = False

    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            sys.exit(1)

    def setup_components(self):
        """Initialize all system components"""
        try:
            # Set up logging first
            self.log_manager = LogManager(self.config)
            self.logger = logging.getLogger(__name__)
            self.logger.info("Initializing trading system...")

            # Initialize components
            self.database = Database(self.config)
            self.mt5_connector = MT5Connector(self.config)
            self.ai_model = AIModel(self.config)
            self.indicators = TechnicalIndicators()
            self.signal_generator = SignalGenerator(self.config)

            # Initialize GUI
            self.app = QApplication(sys.argv)
            self.gui = TradingGUI(self.config)

            self.logger.info("All components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error setting up components: {str(e)}")
            sys.exit(1)

    def setup_queues(self):
        """Set up communication queues between threads"""
        try:
            self.market_data_queue = queue.Queue()
            self.signal_queue = queue.Queue()
            self.trade_queue = queue.Queue()
            self.log_queue = queue.Queue()

        except Exception as e:
            self.logger.error(f"Error setting up queues: {str(e)}")
            sys.exit(1)

    def setup_threads(self):
        """Set up worker threads"""
        try:
            self.market_thread = threading.Thread(
                target=self.market_data_worker,
                daemon=True
            )
            self.signal_thread = threading.Thread(
                target=self.signal_generation_worker,
                daemon=True
            )
            self.trade_thread = threading.Thread(
                target=self.trade_execution_worker,
                daemon=True
            )
            self.model_thread = threading.Thread(
                target=self.model_update_worker,
                daemon=True
            )

        except Exception as e:
            self.logger.error(f"Error setting up threads: {str(e)}")
            sys.exit(1)

    def start(self):
        """Start the trading system"""
        try:
            self.logger.info("Starting trading system...")
            self.running = True

            # Start worker threads
            self.market_thread.start()
            self.signal_thread.start()
            self.trade_thread.start()
            self.model_thread.start()

            # Show GUI
            self.gui.show()

            # Start event loop
            exit_code = self.app.exec_()

            # Cleanup and exit
            self.cleanup()
            sys.exit(exit_code)

        except Exception as e:
            self.logger.error(f"Error starting system: {str(e)}")
            self.cleanup()
            sys.exit(1)

    def cleanup(self):
        """Clean up resources"""
        try:
            self.logger.info("Cleaning up resources...")
            self.running = False
            
            # Wait for threads to finish
            self.market_thread.join(timeout=5)
            self.signal_thread.join(timeout=5)
            self.trade_thread.join(timeout=5)
            self.model_thread.join(timeout=5)

        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    def market_data_worker(self):
        """Worker thread for fetching market data"""
        try:
            while self.running:
                for symbol in self.config['trading']['allowed_symbols']:
                    try:
                        # Get current timeframe from GUI
                        timeframe = self.gui.timeframe_combo.currentText()

                        # Fetch market data
                        candles = self.mt5_connector.get_candles(symbol, timeframe)
                        if candles.empty:
                            continue

                        # Calculate indicators
                        data_with_indicators = self.indicators.calculate_all(candles)

                        # Save to database
                        self.database.save_candles(data_with_indicators, symbol, timeframe)

                        # Put in queue for signal generation
                        self.market_data_queue.put({
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'data': data_with_indicators
                        })

                        # Update GUI
                        self.gui.update_market_data()

                    except Exception as e:
                        self.logger.error(f"Error processing {symbol}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Market data worker error: {str(e)}")

    def signal_generation_worker(self):
        """Worker thread for generating trading signals"""
        try:
            while self.running:
                try:
                    # Get market data from queue
                    market_data = self.market_data_queue.get(timeout=1)
                    
                    # Skip if AI is disabled
                    if not self.gui.ai_enabled_btn.isChecked():
                        continue

                    # Generate AI prediction
                    prediction = self.ai_model.predict(market_data['data'])

                    # Get current price info
                    current_price = self.mt5_connector.get_symbol_info(market_data['symbol'])

                    # Get support/resistance levels
                    support_resistance = self.indicators.detect_support_resistance(
                        market_data['data']
                    )

                    # Generate trading signal
                    signal = self.signal_generator.generate_signal(
                        prediction,
                        market_data['data'],
                        current_price,
                        support_resistance
                    )

                    # Save signal to database
                    self.database.save_signal(signal)

                    # Put in queue for trade execution
                    self.signal_queue.put(signal)

                    # Update GUI
                    self.gui.update_signals_table([signal])

                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error generating signal: {str(e)}")

        except Exception as e:
            self.logger.error(f"Signal generation worker error: {str(e)}")

    def trade_execution_worker(self):
        """Worker thread for executing trades"""
        try:
            while self.running:
                try:
                    # Get signal from queue
                    signal = self.signal_queue.get(timeout=1)

                    # Skip if auto-trading is disabled
                    if not self.gui.auto_trading_btn.isChecked():
                        continue

                    # Validate signal strength
                    if signal['confidence'] < 0.8:  # Minimum confidence threshold
                        continue

                    # Calculate position size based on risk
                    risk_percent = float(self.gui.risk_input.text())
                    account_info = self.mt5_connector.get_account_info()
                    risk_amount = account_info['balance'] * (risk_percent / 100)

                    # Execute trade
                    if signal['signal_type'] in ['BUY', 'STRONG_BUY']:
                        trade_result = self.mt5_connector.place_order(
                            symbol=signal['symbol'],
                            order_type='BUY',
                            volume=self.calculate_position_size(risk_amount, signal),
                            price=signal['entry_price'],
                            sl=signal['stop_loss'],
                            tp=signal['take_profit']
                        )
                    elif signal['signal_type'] in ['SELL', 'STRONG_SELL']:
                        trade_result = self.mt5_connector.place_order(
                            symbol=signal['symbol'],
                            order_type='SELL',
                            volume=self.calculate_position_size(risk_amount, signal),
                            price=signal['entry_price'],
                            sl=signal['stop_loss'],
                            tp=signal['take_profit']
                        )

                    # Save trade to database
                    if trade_result:
                        self.database.save_trade(trade_result)
                        
                        # Update GUI
                        self.gui.update_trades_table([trade_result])

                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error executing trade: {str(e)}")

        except Exception as e:
            self.logger.error(f"Trade execution worker error: {str(e)}")

    def model_update_worker(self):
        """Worker thread for updating AI model"""
        try:
            while self.running:
                try:
                    # Get latest market data
                    market_data = self.market_data_queue.get(timeout=1)

                    # Perform online learning update
                    update_result = self.ai_model.online_update(market_data['data'])

                    # Log update results
                    self.log_manager.log_model_performance({
                        'version': self.ai_model.model_version,
                        'accuracy': update_result['accuracy'],
                        'loss': update_result['loss']
                    })

                    # Update GUI
                    self.gui.update_performance_metrics({
                        'ai_accuracy': update_result['accuracy']
                    })

                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error updating model: {str(e)}")

        except Exception as e:
            self.logger.error(f"Model update worker error: {str(e)}")

    def calculate_position_size(self, risk_amount: float, signal: Dict) -> float:
        """Calculate position size based on risk"""
        try:
            if not signal['stop_loss']:
                return 0.0

            price = signal['entry_price']
            stop_loss = signal['stop_loss']
            pip_value = self.mt5_connector.get_symbol_info(signal['symbol'])['point']
            
            # Calculate stop loss in pips
            sl_pips = abs(price - stop_loss) / pip_value
            
            if sl_pips == 0:
                return 0.0
                
            # Calculate position size
            position_size = risk_amount / sl_pips
            
            # Round to valid lot size
            symbol_info = self.mt5_connector.get_symbol_info(signal['symbol'])
            min_lot = symbol_info['min_lot']
            lot_step = symbol_info['lot_step']
            
            position_size = round(position_size / lot_step) * lot_step
            position_size = max(min_lot, min(position_size, symbol_info['max_lot']))
            
            return position_size

        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0.0

if __name__ == '__main__':
    try:
        # Create and start trading system
        trading_system = TradingSystem()
        trading_system.start()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
