import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice

class TechnicalIndicators:
    def __init__(self):
        """Initialize Technical Indicators calculator"""
        self.logger = logging.getLogger(__name__)

    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        try:
            # Create copy of dataframe to avoid modifying original
            df = df.copy()

            # Add all indicators
            df = self.add_moving_averages(df)
            df = self.add_rsi(df)
            df = self.add_macd(df)
            df = self.add_bollinger_bands(df)
            df = self.add_adx(df)
            df = self.add_atr(df)
            df = self.add_stochastic(df)
            df = self.add_vwap(df)
            
            return df

        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}")
            return df

    def add_moving_averages(self, df: pd.DataFrame, periods: List[int] = [9, 20, 50, 200]) -> pd.DataFrame:
        """Add Simple and Exponential Moving Averages"""
        try:
            for period in periods:
                # Simple Moving Average
                sma = SMAIndicator(close=df['close'], window=period)
                df[f'sma_{period}'] = sma.sma_indicator()

                # Exponential Moving Average
                ema = EMAIndicator(close=df['close'], window=period)
                df[f'ema_{period}'] = ema.ema_indicator()

            return df

        except Exception as e:
            self.logger.error(f"Error calculating moving averages: {str(e)}")
            return df

    def add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Relative Strength Index"""
        try:
            rsi = RSIIndicator(close=df['close'], window=period)
            df['rsi'] = rsi.rsi()
            return df

        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}")
            return df

    def add_macd(self, df: pd.DataFrame, 
                 fast_period: int = 12, 
                 slow_period: int = 26, 
                 signal_period: int = 9) -> pd.DataFrame:
        """Add Moving Average Convergence Divergence"""
        try:
            macd = MACD(
                close=df['close'],
                window_slow=slow_period,
                window_fast=fast_period,
                window_sign=signal_period
            )
            
            df['macd_line'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            return df

        except Exception as e:
            self.logger.error(f"Error calculating MACD: {str(e)}")
            return df

    def add_bollinger_bands(self, df: pd.DataFrame, 
                           period: int = 20, 
                           std_dev: float = 2.0) -> pd.DataFrame:
        """Add Bollinger Bands"""
        try:
            bb = BollingerBands(
                close=df['close'],
                window=period,
                window_dev=std_dev
            )
            
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            return df

        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return df

    def add_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Average Directional Index"""
        try:
            adx = ADXIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=period
            )
            
            df['adx'] = adx.adx()
            df['adx_pos'] = adx.adx_pos()
            df['adx_neg'] = adx.adx_neg()
            
            return df

        except Exception as e:
            self.logger.error(f"Error calculating ADX: {str(e)}")
            return df

    def add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Average True Range"""
        try:
            atr = AverageTrueRange(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=period
            )
            
            df['atr'] = atr.average_true_range()
            return df

        except Exception as e:
            self.logger.error(f"Error calculating ATR: {str(e)}")
            return df

    def add_stochastic(self, df: pd.DataFrame, 
                       k_period: int = 14, 
                       d_period: int = 3) -> pd.DataFrame:
        """Add Stochastic Oscillator"""
        try:
            stoch = StochasticOscillator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=k_period,
                smooth_window=d_period
            )
            
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            return df

        except Exception as e:
            self.logger.error(f"Error calculating Stochastic: {str(e)}")
            return df

    def add_vwap(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Volume Weighted Average Price"""
        try:
            vwap = VolumeWeightedAveragePrice(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                volume=df['tick_volume'],
                window=period
            )
            
            df['vwap'] = vwap.volume_weighted_average_price()
            return df

        except Exception as e:
            self.logger.error(f"Error calculating VWAP: {str(e)}")
            return df

    def detect_support_resistance(self, df: pd.DataFrame, 
                                window: int = 20, 
                                num_touches: int = 2) -> Dict[str, List[float]]:
        """Detect support and resistance levels"""
        try:
            levels = []
            
            # Get highs and lows
            highs = df['high'].rolling(window=window, center=True).max()
            lows = df['low'].rolling(window=window, center=True).min()
            
            # Find potential levels
            for i in range(window, len(df) - window):
                # Check highs
                if highs.iloc[i] == df['high'].iloc[i]:
                    touches = 0
                    level = highs.iloc[i]
                    
                    # Count touches
                    for j in range(max(0, i - window), min(len(df), i + window)):
                        if abs(df['high'].iloc[j] - level) <= (level * 0.002):  # 0.2% tolerance
                            touches += 1
                    
                    if touches >= num_touches:
                        levels.append(level)
                
                # Check lows
                if lows.iloc[i] == df['low'].iloc[i]:
                    touches = 0
                    level = lows.iloc[i]
                    
                    # Count touches
                    for j in range(max(0, i - window), min(len(df), i + window)):
                        if abs(df['low'].iloc[j] - level) <= (level * 0.002):  # 0.2% tolerance
                            touches += 1
                    
                    if touches >= num_touches:
                        levels.append(level)
            
            # Remove duplicates and sort
            levels = sorted(list(set(levels)))
            
            # Classify levels as support or resistance based on current price
            current_price = df['close'].iloc[-1]
            support_levels = [level for level in levels if level < current_price]
            resistance_levels = [level for level in levels if level > current_price]
            
            return {
                'support': support_levels,
                'resistance': resistance_levels
            }

        except Exception as e:
            self.logger.error(f"Error detecting support/resistance: {str(e)}")
            return {'support': [], 'resistance': []}

    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Detect various candlestick patterns"""
        try:
            patterns = []
            
            # Analyze last 3 candles for patterns
            if len(df) < 3:
                return {'patterns': patterns}
                
            last_candles = df.tail(3)
            
            # Doji pattern
            last_candle = df.iloc[-1]
            body_size = abs(last_candle['open'] - last_candle['close'])
            wick_size = last_candle['high'] - last_candle['low']
            
            if body_size <= (wick_size * 0.1):  # Body is 10% or less of total range
                patterns.append({
                    'pattern': 'doji',
                    'timestamp': last_candle.name,
                    'confidence': 0.8
                })
            
            # Engulfing pattern
            if len(df) >= 2:
                current = df.iloc[-1]
                previous = df.iloc[-2]
                
                # Bullish engulfing
                if (previous['close'] < previous['open'] and  # Previous red
                    current['close'] > current['open'] and    # Current green
                    current['open'] < previous['close'] and   # Opens below previous close
                    current['close'] > previous['open']):     # Closes above previous open
                    
                    patterns.append({
                        'pattern': 'bullish_engulfing',
                        'timestamp': current.name,
                        'confidence': 0.9
                    })
                
                # Bearish engulfing
                elif (previous['close'] > previous['open'] and  # Previous green
                      current['close'] < current['open'] and    # Current red
                      current['open'] > previous['close'] and   # Opens above previous close
                      current['close'] < previous['open']):     # Closes below previous open
                    
                    patterns.append({
                        'pattern': 'bearish_engulfing',
                        'timestamp': current.name,
                        'confidence': 0.9
                    })
            
            return {'patterns': patterns}

        except Exception as e:
            self.logger.error(f"Error detecting patterns: {str(e)}")
            return {'patterns': []}
