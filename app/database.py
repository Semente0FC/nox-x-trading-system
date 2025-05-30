import sqlite3
import pandas as pd
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
import os

class Database:
    def __init__(self, config: dict):
        """Initialize database connection"""
        self.config = config['database']
        self.logger = logging.getLogger(__name__)
        self.db_path = self.config['path']
        self._ensure_db_directory()
        self._initialize_tables()

    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except Exception as e:
            self.logger.error(f"Error creating database directory: {str(e)}")
            raise

    def _initialize_tables(self):
        """Create necessary database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Candles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS candles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        timeframe TEXT NOT NULL,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        volume REAL NOT NULL,
                        UNIQUE(symbol, timestamp, timeframe)
                    )
                ''')

                # Signals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        symbol TEXT NOT NULL,
                        signal_type TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        price REAL NOT NULL,
                        confidence REAL NOT NULL,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Trades table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket INTEGER UNIQUE NOT NULL,
                        symbol TEXT NOT NULL,
                        order_type TEXT NOT NULL,
                        volume REAL NOT NULL,
                        open_time DATETIME NOT NULL,
                        open_price REAL NOT NULL,
                        sl REAL,
                        tp REAL,
                        close_time DATETIME,
                        close_price REAL,
                        profit REAL,
                        commission REAL,
                        swap REAL,
                        metadata TEXT,
                        status TEXT NOT NULL
                    )
                ''')

                # AI Models table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ai_models (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version INTEGER NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        accuracy REAL NOT NULL,
                        loss REAL NOT NULL,
                        parameters TEXT NOT NULL,
                        metadata TEXT
                    )
                ''')

                # System logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        level TEXT NOT NULL,
                        module TEXT NOT NULL,
                        message TEXT NOT NULL,
                        metadata TEXT
                    )
                ''')

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error initializing database tables: {str(e)}")
            raise

    def save_candles(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """Save candle data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Prepare data for insertion
                df_copy = df.copy()
                df_copy['symbol'] = symbol
                df_copy['timeframe'] = timeframe
                
                # Convert DataFrame to SQL
                df_copy.to_sql('candles', conn, if_exists='append', index=False)

        except Exception as e:
            self.logger.error(f"Error saving candles: {str(e)}")
            raise

    def get_candles(self, symbol: str, timeframe: str, 
                    start_time: Optional[datetime] = None, 
                    end_time: Optional[datetime] = None,
                    limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve candle data from database"""
        try:
            query = '''
                SELECT timestamp, open, high, low, close, volume 
                FROM candles 
                WHERE symbol = ? AND timeframe = ?
            '''
            params = [symbol, timeframe]

            if start_time:
                query += ' AND timestamp >= ?'
                params.append(start_time)
            if end_time:
                query += ' AND timestamp <= ?'
                params.append(end_time)

            query += ' ORDER BY timestamp DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df.set_index('timestamp')

        except Exception as e:
            self.logger.error(f"Error retrieving candles: {str(e)}")
            return pd.DataFrame()

    def save_signal(self, signal_data: Dict):
        """Save trading signal to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO signals (
                        timestamp, symbol, signal_type, timeframe,
                        price, confidence, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal_data['timestamp'],
                    signal_data['symbol'],
                    signal_data['signal_type'],
                    signal_data['timeframe'],
                    signal_data['price'],
                    signal_data['confidence'],
                    json.dumps(signal_data.get('metadata', {}))
                ))
                
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error saving signal: {str(e)}")
            raise

    def save_trade(self, trade_data: Dict):
        """Save trade information to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO trades (
                        ticket, symbol, order_type, volume,
                        open_time, open_price, sl, tp,
                        close_time, close_price, profit,
                        commission, swap, metadata, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade_data['ticket'],
                    trade_data['symbol'],
                    trade_data['order_type'],
                    trade_data['volume'],
                    trade_data['open_time'],
                    trade_data['open_price'],
                    trade_data.get('sl'),
                    trade_data.get('tp'),
                    trade_data.get('close_time'),
                    trade_data.get('close_price'),
                    trade_data.get('profit', 0),
                    trade_data.get('commission', 0),
                    trade_data.get('swap', 0),
                    json.dumps(trade_data.get('metadata', {})),
                    trade_data['status']
                ))
                
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error saving trade: {str(e)}")
            raise

    def update_trade(self, ticket: int, update_data: Dict):
        """Update existing trade information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query dynamically based on provided fields
                update_fields = []
                params = []
                
                for key, value in update_data.items():
                    if key in ['close_time', 'close_price', 'profit', 'status']:
                        update_fields.append(f"{key} = ?")
                        params.append(value)
                
                if not update_fields:
                    return
                
                params.append(ticket)
                query = f'''
                    UPDATE trades 
                    SET {', '.join(update_fields)}
                    WHERE ticket = ?
                '''
                
                cursor.execute(query, params)
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error updating trade: {str(e)}")
            raise

    def save_model_version(self, model_data: Dict):
        """Save AI model version information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO ai_models (
                        version, accuracy, loss, parameters, metadata
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    model_data['version'],
                    model_data['accuracy'],
                    model_data['loss'],
                    json.dumps(model_data['parameters']),
                    json.dumps(model_data.get('metadata', {}))
                ))
                
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error saving model version: {str(e)}")
            raise

    def log_system_event(self, level: str, module: str, message: str, metadata: Optional[Dict] = None):
        """Log system event to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO system_logs (
                        level, module, message, metadata
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    level,
                    module,
                    message,
                    json.dumps(metadata) if metadata else None
                ))
                
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error logging system event: {str(e)}")
            raise

    def get_trade_statistics(self, start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Dict:
        """Get trading statistics for a given time period"""
        try:
            query = '''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(profit) as total_profit,
                    AVG(profit) as avg_profit,
                    MIN(profit) as max_loss,
                    MAX(profit) as max_profit
                FROM trades
                WHERE status = 'CLOSED'
            '''
            params = []

            if start_time:
                query += ' AND close_time >= ?'
                params.append(start_time)
            if end_time:
                query += ' AND close_time <= ?'
                params.append(end_time)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()

                return {
                    'total_trades': row[0],
                    'winning_trades': row[1],
                    'losing_trades': row[2],
                    'total_profit': row[3],
                    'average_profit': row[4],
                    'max_loss': row[5],
                    'max_profit': row[6],
                    'win_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0
                }

        except Exception as e:
            self.logger.error(f"Error getting trade statistics: {str(e)}")
            return {}

    def backup_database(self):
        """Create a backup of the database"""
        try:
            backup_path = f"{self.db_path}.backup"
            with sqlite3.connect(self.db_path) as conn:
                backup = sqlite3.connect(backup_path)
                conn.backup(backup)
                backup.close()
            
            self.logger.info(f"Database backup created: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating database backup: {str(e)}")
            raise
