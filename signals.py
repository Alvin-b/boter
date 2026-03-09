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
        Analyze candles and generate trading signal
        Returns: 'CALL', 'PUT', or 'NEUTRAL'
        """
        # Check we have enough data
        if not candles or len(candles) < 20:
            return "NEUTRAL"
        
        try:
            # Extract close prices safely
            closes = []
            for c in candles:
                if isinstance(c, dict):
                    closes.append(float(c.get('close', 0)))
                elif isinstance(c, (list, tuple)) and len(c) > 3:
                    closes.append(float(c[3]))
                else:
                    continue
            
            if len(closes) < 25:
                return "NEUTRAL"
            
            # Simple trend detection
            recent = closes[-10:]
            avg_recent = sum(recent) / len(recent)
            last_price = closes[-1]
            
            # Simple moving average comparison
            sma5 = sum(closes[-5:]) / 5
            sma10 = sum(closes[-10:]) / 10
            
            # Decision
            if sma5 > sma10 * 1.001:
                return "CALL"
            elif sma5 < sma10 * 0.999:
                return "PUT"
            elif last_price > avg_recent:
                return "CALL"
            elif last_price < avg_recent:
                return "PUT"
            
            return "NEUTRAL"
            
        except Exception as e:
            print(f"Signal error: {e}")
            return "NEUTRAL"
    
    def get_signal_strength(self, candles):
        """Calculate signal strength"""
        signal = self.analyze_market(candles)
        
        if signal == "CALL" or signal == "PUT":
            return 0.7
        
        return 0.0
    
    def should_trade(self):
        """Check if we should trade"""
        return True
