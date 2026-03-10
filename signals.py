"""
Simple Signal Generator for Pocket Option Trading Bot
"""

import logging
import random

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Simple signal generator with basic technical analysis"""
    
    def __init__(self):
        self.signal_history = []
        
    def analyze_market(self, candles):
        """
        Analyze candles and generate trading signal with strength
        Returns: ('CALL'/'PUT'/'NEUTRAL', confidence_score)
        """
        # Check we have enough data
        if not candles or len(candles) < 20:
            return "NEUTRAL", 0.0
        
        try:
            # Extract price data safely
            closes = []
            opens = []
            highs = []
            lows = []
            
            for c in candles:
                if isinstance(c, dict):
                    closes.append(float(c.get('close', 0)))
                    opens.append(float(c.get('open', 0)))
                    highs.append(float(c.get('high', 0)))
                    lows.append(float(c.get('low', 0)))
                elif isinstance(c, (list, tuple)) and len(c) > 3:
                    closes.append(float(c[3]))
                    opens.append(float(c[0]))
                    highs.append(float(c[1]))
                    lows.append(float(c[2]))
                else:
                    continue
            
            if len(closes) < 25:
                return "NEUTRAL", 0.0
            
            # Calculate indicators and score
            call_score = 0
            put_score = 0
            total_indicators = 0
            
            # 1. Trend (SMA Crossover)
            total_indicators += 1
            sma5 = sum(closes[-5:]) / 5
            sma10 = sum(closes[-10:]) / 10
            sma20 = sum(closes[-20:]) / 20
            
            if sma5 > sma10 > sma20:
                call_score += 3
            elif sma5 < sma10 < sma20:
                put_score += 3
            elif sma5 > sma10:
                call_score += 1
            elif sma5 < sma10:
                put_score += 1
            
            # 2. RSI (Relative Strength Index)
            total_indicators += 1
            gains = []
            losses = []
            for i in range(1, 15):
                if i >= len(closes):
                    break
                change = closes[-i] - closes[-i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if gains and losses:
                avg_gain = sum(gains) / len(gains)
                avg_loss = sum(losses) / len(losses)
                if avg_loss > 0:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    
                    if rsi < 30:  # Oversold - bullish
                        call_score += 3
                    elif rsi < 40:
                        call_score += 1
                    elif rsi > 70:  # Overbought - bearish
                        put_score += 3
                    elif rsi > 60:
                        put_score += 1
            
            # 3. MACD (Moving Average Convergence Divergence)
            total_indicators += 1
            ema12 = self._calculate_ema(closes, 12)
            ema26 = self._calculate_ema(closes, 26)
            
            if ema12 and ema26:
                macd = ema12 - ema26
                signal_line = ema12 * 0.9 + ema26 * 0.1
                
                if macd > signal_line:
                    call_score += 2
                elif macd < signal_line:
                    put_score += 2
            
            # 4. Bollinger Bands position
            total_indicators += 1
            bb_upper, bb_middle, bb_lower = self._bollinger_bands(closes)
            
            if bb_upper and bb_lower:
                last_close = closes[-1]
                position = (last_close - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5
                
                if position < 0.2:  # Near lower band
                    call_score += 2
                elif position > 0.8:  # Near upper band
                    put_score += 2
            
            # 5. Price momentum
            total_indicators += 1
            momentum = closes[-1] - closes[-5]
            if momentum > 0:
                call_score += 1
            elif momentum < 0:
                put_score += 1
            
            # 6. Candle strength
            total_indicators += 1
            last_candle = closes[-1] - opens[-1]
            if last_candle > 0:
                call_score += 1
            else:
                put_score += 1
            
            # Calculate confidence
            max_possible = total_indicators * 3
            total_score = call_score + put_score
            
            if call_score > put_score and call_score >= 3:
                confidence = min(0.95, call_score / max_possible + 0.3)
                return "CALL", confidence
            elif put_score > call_score and put_score >= 3:
                confidence = min(0.95, put_score / max_possible + 0.3)
                return "PUT", confidence
            
            return "NEUTRAL", 0.0
            
        except Exception as e:
            print(f"Signal error: {e}")
            return "NEUTRAL", 0.0
    
    def _calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def _bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
        
        recent = prices[-period:]
        sma = sum(recent) / period
        variance = sum((x - sma) ** 2 for x in recent) / period
        std = variance ** 0.5
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        return upper, sma, lower
    
    def get_signal_strength(self, candles):
        """
        Calculate signal strength based on multiple indicators
        Returns: confidence score between 0.0 and 1.0
        """
        signal, confidence = self.analyze_market(candles)
        return confidence
    
    def get_signal_with_strength(self, candles):
        """Get both signal and strength together"""
        return self.analyze_market(candles)
    
    def should_trade(self):
        """Check if we should trade"""
        return True
