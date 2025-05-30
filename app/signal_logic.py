import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime

class SignalGenerator:
    def __init__(self, config: dict):
        """Initialize Signal Generator with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.min_confidence = 0.7  # Minimum confidence threshold for signals
        self.risk_reward_ratio = 2.0  # Target profit : Stop loss ratio

    def generate_signal(self, 
                       ai_prediction: Dict,
                       technical_data: pd.DataFrame,
                       price_data: Dict,
                       support_resistance: Dict) -> Dict:
        """
        Generate trading signal by combining AI predictions with technical analysis
        """
        try:
            # Extract current market data
            current_price = price_data['close']
            
            # Initialize signal strength metrics
            signal_metrics = {
                'ai_score': self._evaluate_ai_signal(ai_prediction),
                'trend_score': self._evaluate_trend(technical_data),
                'momentum_score': self._evaluate_momentum(technical_data),
                'support_resistance_score': self._evaluate_support_resistance(
                    current_price, support_resistance
                )
            }
            
            # Calculate overall signal strength
            overall_score = self._calculate_overall_score(signal_metrics)
            signal_type = self._determine_signal_type(overall_score)
            
            if signal_type == 'NEUTRAL':
                return self._create_neutral_signal()
            
            # Calculate entry, stop loss, and take profit levels
            levels = self._calculate_trade_levels(
                signal_type,
                current_price,
                technical_data,
                support_resistance
            )
            
            return {
                'timestamp': datetime.now().isoformat(),
                'signal_type': signal_type,
                'confidence': overall_score,
                'entry_price': levels['entry'],
                'stop_loss': levels['stop_loss'],
                'take_profit': levels['take_profit'],
                'risk_reward_ratio': levels['risk_reward_ratio'],
                'metrics': signal_metrics,
                'metadata': {
                    'ai_prediction': ai_prediction,
                    'technical_indicators': self._get_technical_summary(technical_data),
                    'market_context': self._get_market_context(technical_data)
                }
            }

        except Exception as e:
            self.logger.error(f"Error generating signal: {str(e)}")
            return self._create_neutral_signal()

    def _evaluate_ai_signal(self, ai_prediction: Dict) -> float:
        """Evaluate AI prediction strength"""
        try:
            signal_strength = ai_prediction['confidence']
            probabilities = ai_prediction['probabilities']
            
            # Add weight to strong directional predictions
            if probabilities['buy'] > 0.7 or probabilities['sell'] > 0.7:
                signal_strength *= 1.2
            
            return min(signal_strength, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error evaluating AI signal: {str(e)}")
            return 0.0

    def _evaluate_trend(self, df: pd.DataFrame) -> float:
        """Evaluate market trend strength"""
        try:
            # Get latest values
            latest = df.iloc[-1]
            
            trend_score = 0.0
            
            # Evaluate moving averages
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                if latest['sma_20'] > latest['sma_50']:
                    trend_score += 0.3  # Bullish MA alignment
                elif latest['sma_20'] < latest['sma_50']:
                    trend_score -= 0.3  # Bearish MA alignment
            
            # Evaluate ADX (trend strength)
            if 'adx' in df.columns:
                adx_value = latest['adx']
                if adx_value > 25:  # Strong trend
                    trend_score *= 1.5
                elif adx_value < 20:  # Weak trend
                    trend_score *= 0.5
            
            return max(min(abs(trend_score), 1.0), 0.0)
            
        except Exception as e:
            self.logger.error(f"Error evaluating trend: {str(e)}")
            return 0.0

    def _evaluate_momentum(self, df: pd.DataFrame) -> float:
        """Evaluate market momentum"""
        try:
            latest = df.iloc[-1]
            momentum_score = 0.0
            
            # RSI Analysis
            if 'rsi' in df.columns:
                rsi = latest['rsi']
                if rsi > 70:
                    momentum_score -= 0.3  # Overbought
                elif rsi < 30:
                    momentum_score += 0.3  # Oversold
            
            # MACD Analysis
            if all(x in df.columns for x in ['macd_line', 'macd_signal']):
                if latest['macd_line'] > latest['macd_signal']:
                    momentum_score += 0.3
                else:
                    momentum_score -= 0.3
            
            # Stochastic Analysis
            if 'stoch_k' in df.columns and 'stoch_d' in df.columns:
                if latest['stoch_k'] > latest['stoch_d']:
                    momentum_score += 0.2
                else:
                    momentum_score -= 0.2
            
            return max(min(abs(momentum_score), 1.0), 0.0)
            
        except Exception as e:
            self.logger.error(f"Error evaluating momentum: {str(e)}")
            return 0.0

    def _evaluate_support_resistance(self, 
                                  current_price: float, 
                                  support_resistance: Dict) -> float:
        """Evaluate proximity to support/resistance levels"""
        try:
            score = 0.0
            
            # Get nearest levels
            support_levels = support_resistance.get('support', [])
            resistance_levels = support_resistance.get('resistance', [])
            
            if not support_levels and not resistance_levels:
                return 0.0
            
            # Find nearest support and resistance
            nearest_support = max([s for s in support_levels if s < current_price], default=None)
            nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
            
            if nearest_support:
                support_proximity = (current_price - nearest_support) / current_price
                if support_proximity < 0.01:  # Within 1% of support
                    score += 0.5
                elif support_proximity < 0.02:  # Within 2% of support
                    score += 0.3
            
            if nearest_resistance:
                resistance_proximity = (nearest_resistance - current_price) / current_price
                if resistance_proximity < 0.01:  # Within 1% of resistance
                    score -= 0.5
                elif resistance_proximity < 0.02:  # Within 2% of resistance
                    score -= 0.3
            
            return max(min(abs(score), 1.0), 0.0)
            
        except Exception as e:
            self.logger.error(f"Error evaluating support/resistance: {str(e)}")
            return 0.0

    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall signal strength"""
        try:
            weights = {
                'ai_score': 0.4,
                'trend_score': 0.25,
                'momentum_score': 0.2,
                'support_resistance_score': 0.15
            }
            
            overall_score = sum(score * weights[metric] 
                              for metric, score in metrics.items())
            
            return max(min(overall_score, 1.0), 0.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating overall score: {str(e)}")
            return 0.0

    def _determine_signal_type(self, overall_score: float) -> str:
        """Determine the type of trading signal based on overall score"""
        try:
            if overall_score < self.min_confidence:
                return 'NEUTRAL'
            
            if overall_score > 0.8:
                return 'STRONG_BUY' if overall_score > 0 else 'STRONG_SELL'
            else:
                return 'BUY' if overall_score > 0 else 'SELL'
                
        except Exception as e:
            self.logger.error(f"Error determining signal type: {str(e)}")
            return 'NEUTRAL'

    def _calculate_trade_levels(self,
                              signal_type: str,
                              current_price: float,
                              technical_data: pd.DataFrame,
                              support_resistance: Dict) -> Dict:
        """Calculate entry, stop loss, and take profit levels"""
        try:
            latest = technical_data.iloc[-1]
            atr = latest.get('atr', current_price * 0.001)  # Default to 0.1% if ATR not available
            
            # Initialize levels
            entry = current_price
            stop_loss = None
            take_profit = None
            
            if signal_type in ['BUY', 'STRONG_BUY']:
                # For buy signals
                nearby_support = max([s for s in support_resistance.get('support', [])
                                   if s < current_price], default=None)
                
                stop_loss = nearby_support if nearby_support else (current_price - 2 * atr)
                take_profit = current_price + (current_price - stop_loss) * self.risk_reward_ratio
                
            elif signal_type in ['SELL', 'STRONG_SELL']:
                # For sell signals
                nearby_resistance = min([r for r in support_resistance.get('resistance', [])
                                      if r > current_price], default=None)
                
                stop_loss = nearby_resistance if nearby_resistance else (current_price + 2 * atr)
                take_profit = current_price - (stop_loss - current_price) * self.risk_reward_ratio
            
            risk = abs(entry - stop_loss) if stop_loss else atr
            reward = abs(entry - take_profit) if take_profit else risk * self.risk_reward_ratio
            
            return {
                'entry': entry,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward_ratio': reward / risk if risk > 0 else self.risk_reward_ratio
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating trade levels: {str(e)}")
            return {
                'entry': current_price,
                'stop_loss': None,
                'take_profit': None,
                'risk_reward_ratio': self.risk_reward_ratio
            }

    def _get_technical_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary of technical indicators"""
        try:
            latest = df.iloc[-1]
            return {
                'rsi': float(latest.get('rsi', 0)),
                'macd': {
                    'line': float(latest.get('macd_line', 0)),
                    'signal': float(latest.get('macd_signal', 0)),
                    'histogram': float(latest.get('macd_histogram', 0))
                },
                'bollinger': {
                    'upper': float(latest.get('bb_upper', 0)),
                    'middle': float(latest.get('bb_middle', 0)),
                    'lower': float(latest.get('bb_lower', 0))
                },
                'adx': float(latest.get('adx', 0))
            }
            
        except Exception as e:
            self.logger.error(f"Error getting technical summary: {str(e)}")
            return {}

    def _get_market_context(self, df: pd.DataFrame) -> Dict:
        """Get market context information"""
        try:
            latest = df.iloc[-1]
            
            # Calculate volatility
            returns = df['close'].pct_change()
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            
            # Determine trend
            sma20 = latest.get('sma_20', 0)
            sma50 = latest.get('sma_50', 0)
            trend = 'uptrend' if sma20 > sma50 else 'downtrend'
            
            return {
                'trend': trend,
                'volatility': float(volatility),
                'avg_volume': float(df['volume'].mean()),
                'price_range': {
                    'daily_high': float(df['high'].max()),
                    'daily_low': float(df['low'].min())
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market context: {str(e)}")
            return {}

    def _create_neutral_signal(self) -> Dict:
        """Create a neutral signal response"""
        return {
            'timestamp': datetime.now().isoformat(),
            'signal_type': 'NEUTRAL',
            'confidence': 0.0,
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'risk_reward_ratio': None,
            'metrics': {
                'ai_score': 0.0,
                'trend_score': 0.0,
                'momentum_score': 0.0,
                'support_resistance_score': 0.0
            },
            'metadata': {}
        }
