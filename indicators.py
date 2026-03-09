"""
Technical Indicators Module for Pocket Option Trading Bot
Advanced technical analysis - NO numpy dependency
"""

from collections import deque
import math


class TechnicalIndicators:
    """Technical analysis indicators for trading signal generation"""
    
    @staticmethod
    def sma(data, period):
        """Simple Moving Average"""
        if len(data) < period:
            return None
        return sum(data[-period:]) / period
    
    @staticmethod
    def ema(data, period):
        """Exponential Moving Average"""
        if len(data) < period:
            return None
        
        data = list(data)
        multiplier = 2 / (period + 1)
        ema = data[0]
        
        for price in data[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    @staticmethod
    def rsi(prices, period=14):
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return None
        
        prices = list(prices)
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(prices, fast=12, slow=26, signal=9):
        """MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return None, None, None
        
        ema_fast = TechnicalIndicators.ema(prices, fast)
        ema_slow = TechnicalIndicators.ema(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None, None
        
        macd_line = ema_fast - ema_slow
        signal_line = ema_fast * 0.9 + ema_slow * 0.1
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(prices, period=20, std_dev=2):
        """Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
        
        data = list(prices[-period:])
        sma_val = sum(data) / period
        variance = sum((x - sma_val) ** 2 for x in data) / period
        std = variance ** 0.5
        
        upper_band = sma_val + (std_dev * std)
        lower_band = sma_val - (std_dev * std)
        
        return upper_band, sma_val, lower_band
    
    @staticmethod
    def stochastic(highs, lows, close, period=14):
        """Stochastic Oscillator"""
        if len(highs) < period or len(lows) < period:
            return None, None
        
        highest_high = max(highs[-period:])
        lowest_low = min(lows[-period:])
        
        if highest_high == lowest_low:
            return 50, 50
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k
        
        return k, d
    
    @staticmethod
    def atr(highs, lows, closes, period=14):
        """Average True Range - Volatility indicator"""
        if len(highs) < period + 1:
            return None
        
        tr_values = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            tr = max(high_low, high_close, low_close)
            tr_values.append(tr)
        
        if len(tr_values) < period:
            return None
        
        atr = sum(tr_values[-period:]) / period
        return atr
    
    @staticmethod
    def adx(highs, lows, closes, period=14):
        """Average Directional Index"""
        if len(highs) < period + 1:
            return None
        
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(highs)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            plus_dm.append(high_diff if high_diff > low_diff and high_diff > 0 else 0)
            minus_dm.append(low_diff if low_diff > high_diff and low_diff > 0 else 0)
        
        if len(plus_dm) < period:
            return None
        
        plus_di = 100 * sum(plus_dm[-period:]) / period
        minus_di = 100 * sum(minus_dm[-period:]) / period
        
        di_sum = plus_di + minus_di
        if di_sum == 0:
            return 0
        
        dx = 100 * abs(plus_di - minus_di) / di_sum
        
        return dx
    
    @staticmethod
    def cci(highs, lows, closes, period=20):
        """Commodity Channel Index"""
        if len(highs) < period:
            return None
        
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs[-period:], lows[-period:], closes[-period:])]
        sma_tp = sum(typical_prices) / period
        mean_deviation = sum(abs(tp - sma_tp) for tp in typical_prices) / period
        
        if mean_deviation == 0:
            return 0
        
        cci = (typical_prices[-1] - sma_tp) / (0.015 * mean_deviation)
        
        return cci
    
    @staticmethod
    def detect_trend(prices, period=20):
        """Detect market trend"""
        if len(prices) < period:
            return "sideways"
        
        recent_prices = list(prices[-period:])
        first_half = sum(recent_prices[:period//2]) / (period//2)
        second_half = sum(recent_prices[period//2:]) / (period - period//2)
        
        if first_half == 0:
            return "sideways"
        
        change_percent = (second_half - first_half) / first_half * 100
        
        if change_percent > 1:
            return "uptrend"
        elif change_percent < -1:
            return "downtrend"
        else:
            return "sideways"
    
    @staticmethod
    def fibonacci_retracement(high, low):
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        return {
            '0.0%': high,
            '23.6%': high - (diff * 0.236),
            '38.2%': high - (diff * 0.382),
            '50.0%': high - (diff * 0.5),
            '61.8%': high - (diff * 0.618),
            '100.0%': low
        }
    
    @staticmethod
    def pivot_points(highs, lows, closes):
        """Calculate pivot points and support/resistance"""
        if not highs or not lows or not closes:
            return None
        
        high = highs[-1]
        low = lows[-1]
        close = closes[-1]
        
        pp = (high + low + close) / 3
        r1 = 2 * pp - low
        s1 = 2 * pp - high
        r2 = pp + (high - low)
        s2 = pp - (high - low)
        
        return {'pp': pp, 'r1': r1, 's1': s1, 'r2': r2, 's2': s2}
    
    @staticmethod
    def detect_pattern(prices, highs, lows):
        """Detect common chart patterns"""
        if len(prices) < 20:
            return []
        
        patterns = []
        
        # Double bottom
        if len(highs) >= 10:
            recent_highs = highs[-10:]
            if min(recent_highs) == recent_highs[-5]:
                patterns.append("double_bottom")
        
        # Double top
        if len(highs) >= 10:
            recent_highs = highs[-10:]
            if max(recent_highs) == recent_highs[-5]:
                patterns.append("double_top")
        
        # Head and shoulders
        if len(highs) >= 15:
            recent_highs = highs[-15:]
            middle = max(recent_highs[5:10])
            if middle > recent_highs[2] and middle > recent_highs[12]:
                patterns.append("head_shoulders")
        
        return patterns
    
    @staticmethod
    def volume_analysis(volumes, prices):
        """Analyze volume trends"""
        if len(volumes) < 20:
            return "neutral"
        
        recent_vol = volumes[-10:]
        older_vol = volumes[-20:-10]
        
        if not older_vol:
            return "neutral"
            
        avg_recent = sum(recent_vol) / len(recent_vol)
        avg_older = sum(older_vol) / len(older_vol)
        
        if avg_older == 0:
            return "neutral"
            
        if avg_recent > avg_older * 1.5:
            return "increasing"
        elif avg_recent < avg_older * 0.7:
            return "decreasing"
        else:
            return "stable"


class AdvancedPatternRecognition:
    """Advanced AI-powered pattern recognition"""
    
    @staticmethod
    def detect_wedge(prices, period=20):
        """Detect rising/falling wedge patterns"""
        if len(prices) < period:
            return None
        
        recent = list(prices[-period:])
        
        first_quarter = recent[:period//4]
        last_quarter = recent[-(period//4):]
        
        if first_quarter[-1] > recent[period//2] > last_quarter[0]:
            return "rising_wedge"
        elif first_quarter[-1] < recent[period//2] < last_quarter[0]:
            return "falling_wedge"
        
        return None
    
    @staticmethod
    def detect_triangle(prices, period=30):
        """Detect triangle patterns"""
        if len(prices) < period:
            return None
        
        recent = list(prices[-period:])
        
        highs = [recent[i] for i in range(0, period, 3) if i < len(recent)]
        lows = [recent[i] for i in range(0, period, 3) if i < len(recent)]
        
        if len(highs) < 2 or len(lows) < 2:
            return None
            
        high_trend = sum(highs[-5:]) / 5 - sum(highs[:5]) / 5
        low_trend = sum(lows[-5:]) / 5 - sum(lows[:5]) / 5
        
        if high_trend < -0.001 and low_trend > 0.001:
            return "ascending_triangle"
        elif high_trend > 0.001 and low_trend < -0.001:
            return "descending_triangle"
        
        return None
    
    @staticmethod
    def detect_flag(prices, period=20):
        """Detect flag patterns"""
        if len(prices) < period:
            return None
        
        recent = list(prices[-period:])
        
        first_move = recent[5] - recent[0]
        consolidation = recent[-1] - recent[5]
        
        if abs(first_move) > 0.005 and abs(consolidation) < abs(first_move) * 0.3:
            if first_move > 0:
                return "bullish_flag"
            else:
                return "bearish_flag"
        
        return None
    
    @staticmethod
    def detect_divergence(prices, indicator_values, period=20):
        """Detect bullish/bearish divergence"""
        if len(prices) < period or len(indicator_values) < period:
            return None
        
        recent_prices = prices[-period:]
        recent_indicator = indicator_values[-period:]
        
        price_low = min(recent_prices)
        price_high = max(recent_prices)
        ind_low = min(recent_indicator)
        ind_high = max(recent_indicator)
        
        if recent_prices[-1] < price_low * 1.01 and recent_indicator[-1] > ind_low * 1.05:
            return "bullish_divergence"
        
        if recent_prices[-1] > price_high * 0.99 and recent_indicator[-1] < ind_high * 0.95:
            return "bearish_divergence"
        
        return None


class SignalScoring:
    """Advanced signal scoring system"""
    
    @staticmethod
    def calculate_confidence(indicators_data):
        """Calculate confidence score (0-100%)"""
        score = 0
        max_score = 0
        
        # EMA Alignment (weight: 15)
        max_score += 15
        if indicators_data.get('ema_aligned'):
            score += 15
        
        # RSI Position (weight: 10)
        max_score += 10
        rsi = indicators_data.get('rsi', 50)
        if rsi < 30 or rsi > 70:
            score += 10
        elif rsi < 40 or rsi > 60:
            score += 5
        
        # MACD (weight: 15)
        max_score += 15
        if indicators_data.get('macd_bullish'):
            score += 15
        elif indicators_data.get('macd_strength', 0) > 0.5:
            score += 10
        
        # Trend (weight: 15)
        max_score += 15
        if indicators_data.get('trend') in ['uptrend', 'downtrend']:
            score += 15
        
        # Bollinger Position (weight: 10)
        max_score += 10
        bb_position = indicators_data.get('bb_position', 0.5)
        if bb_position < 0.2 or bb_position > 0.8:
            score += 10
        
        # Stochastic (weight: 10)
        max_score += 10
        if indicators_data.get('stoch_oversold') or indicators_data.get('stoch_overbought'):
            score += 10
        
        # Pattern (weight: 15)
        max_score += 15
        if indicators_data.get('pattern'):
            score += 15
        elif indicators_data.get('candle_pattern'):
            score += 10
        
        confidence = (score / max_score) * 100
        return min(100, confidence)
    
    @staticmethod
    def get_signal_quality(confidence):
        """Get signal quality rating"""
        if confidence >= 80:
            return "EXCELLENT"
        elif confidence >= 65:
            return "GOOD"
        elif confidence >= 50:
            return "FAIR"
        elif confidence >= 35:
            return "WEAK"
        else:
            return "POOR"
