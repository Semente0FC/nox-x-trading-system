import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

class LogManager:
    def __init__(self, config: dict):
        """Initialize logging system with configuration"""
        self.config = config['logging']
        self.log_path = self.config['file_path']
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration"""
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(self.log_path)
            Path(log_dir).mkdir(parents=True, exist_ok=True)

            # Create root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(self.config['level'])

            # Remove existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Create formatters
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
            )
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )

            # File handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_path,
                maxBytes=self.config['max_file_size_mb'] * 1024 * 1024,
                backupCount=self.config['backup_count']
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

            # Create logger instance for this class
            self.logger = logging.getLogger(__name__)
            self.logger.info("Logging system initialized successfully")

        except Exception as e:
            print(f"Error setting up logging: {str(e)}")
            raise

    def log_trade(self, trade_data: Dict):
        """Log trade-related information"""
        try:
            message = (
                f"Trade: {trade_data['action']} {trade_data['symbol']} "
                f"Volume: {trade_data['volume']} "
                f"Price: {trade_data['price']} "
                f"SL: {trade_data.get('sl', 'None')} "
                f"TP: {trade_data.get('tp', 'None')}"
            )
            self.logger.info(message, extra={'trade_data': trade_data})
        except Exception as e:
            self.logger.error(f"Error logging trade: {str(e)}")

    def log_signal(self, signal_data: Dict):
        """Log trading signal information"""
        try:
            message = (
                f"Signal: {signal_data['signal_type']} "
                f"Confidence: {signal_data['confidence']:.2f} "
                f"Entry: {signal_data.get('entry_price', 'None')}"
            )
            self.logger.info(message, extra={'signal_data': signal_data})
        except Exception as e:
            self.logger.error(f"Error logging signal: {str(e)}")

    def log_error(self, error_message: str, error: Optional[Exception] = None, 
                  module: str = "", additional_data: Optional[Dict] = None):
        """Log error information with stack trace if available"""
        try:
            error_data = {
                'timestamp': datetime.now().isoformat(),
                'module': module,
                'message': error_message,
                'error_type': type(error).__name__ if error else None,
                'error_details': str(error) if error else None,
                'additional_data': additional_data
            }
            
            message = f"Error in {module}: {error_message}"
            if error:
                message += f" - {str(error)}"
                
            self.logger.error(message, exc_info=error is not None, 
                            extra={'error_data': error_data})
        except Exception as e:
            self.logger.error(f"Error logging error: {str(e)}")

    def log_system_status(self, status_data: Dict):
        """Log system status information"""
        try:
            message = (
                f"System Status - "
                f"MT5 Connected: {status_data.get('mt5_connected', False)} "
                f"Active Models: {status_data.get('active_models', 0)} "
                f"Memory Usage: {status_data.get('memory_usage', '0')}MB"
            )
            self.logger.info(message, extra={'status_data': status_data})
        except Exception as e:
            self.logger.error(f"Error logging system status: {str(e)}")

    def log_model_performance(self, model_data: Dict):
        """Log AI model performance metrics"""
        try:
            message = (
                f"Model Performance - "
                f"Version: {model_data['version']} "
                f"Accuracy: {model_data['accuracy']:.2f} "
                f"Loss: {model_data['loss']:.4f}"
            )
            self.logger.info(message, extra={'model_data': model_data})
        except Exception as e:
            self.logger.error(f"Error logging model performance: {str(e)}")

    def log_market_data(self, market_data: Dict):
        """Log market data updates"""
        try:
            message = (
                f"Market Update - "
                f"Symbol: {market_data['symbol']} "
                f"Price: {market_data['price']} "
                f"Spread: {market_data.get('spread', 'N/A')}"
            )
            self.logger.debug(message, extra={'market_data': market_data})
        except Exception as e:
            self.logger.error(f"Error logging market data: {str(e)}")

    def log_config_change(self, old_config: Dict, new_config: Dict):
        """Log configuration changes"""
        try:
            changes = {}
            for key in set(old_config.keys()) | set(new_config.keys()):
                if key not in old_config:
                    changes[key] = {'action': 'added', 'value': new_config[key]}
                elif key not in new_config:
                    changes[key] = {'action': 'removed', 'value': old_config[key]}
                elif old_config[key] != new_config[key]:
                    changes[key] = {
                        'action': 'modified',
                        'old_value': old_config[key],
                        'new_value': new_config[key]
                    }

            if changes:
                message = f"Configuration changed: {len(changes)} settings modified"
                self.logger.info(message, extra={'config_changes': changes})
        except Exception as e:
            self.logger.error(f"Error logging config change: {str(e)}")

    def log_performance_metrics(self, metrics: Dict):
        """Log trading performance metrics"""
        try:
            message = (
                f"Performance Metrics - "
                f"Win Rate: {metrics.get('win_rate', 0):.2f}% "
                f"Profit Factor: {metrics.get('profit_factor', 0):.2f} "
                f"Sharp Ratio: {metrics.get('sharp_ratio', 0):.2f}"
            )
            self.logger.info(message, extra={'performance_metrics': metrics})
        except Exception as e:
            self.logger.error(f"Error logging performance metrics: {str(e)}")

    def log_backtesting_result(self, backtest_data: Dict):
        """Log backtesting results"""
        try:
            message = (
                f"Backtest Results - "
                f"Period: {backtest_data['period']} "
                f"Total Trades: {backtest_data['total_trades']} "
                f"Net Profit: {backtest_data['net_profit']:.2f} "
                f"Win Rate: {backtest_data['win_rate']:.2f}%"
            )
            self.logger.info(message, extra={'backtest_data': backtest_data})
        except Exception as e:
            self.logger.error(f"Error logging backtest results: {str(e)}")

    def get_recent_logs(self, level: str = "INFO", 
                       limit: int = 100) -> list:
        """Retrieve recent log entries"""
        try:
            logs = []
            with open(self.log_path, 'r') as f:
                for line in f.readlines()[-limit:]:
                    if level in line:  # Simple filtering by log level
                        logs.append(line.strip())
            return logs
        except Exception as e:
            self.logger.error(f"Error retrieving recent logs: {str(e)}")
            return []

    def archive_old_logs(self):
        """Archive old log files"""
        try:
            # Create archive directory if it doesn't exist
            archive_dir = os.path.join(os.path.dirname(self.log_path), 'archive')
            Path(archive_dir).mkdir(parents=True, exist_ok=True)

            # Move old log files to archive
            log_dir = os.path.dirname(self.log_path)
            for file in os.listdir(log_dir):
                if file.startswith(os.path.basename(self.log_path)) and file != os.path.basename(self.log_path):
                    old_path = os.path.join(log_dir, file)
                    new_path = os.path.join(archive_dir, file)
                    os.rename(old_path, new_path)

            self.logger.info("Old log files archived successfully")
        except Exception as e:
            self.logger.error(f"Error archiving old logs: {str(e)}")
