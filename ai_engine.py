"""
Advanced AI Module for Pocket Option Trading Bot
Integrates with external AI APIs for enhanced predictions
"""

import asyncio
import json
import logging
import time
import hashlib
import hmac
import aiohttp
import os

logger = logging.getLogger(__name__)


class DeepSeekAI:
    """DeepSeek-R1 integration for advanced market predictions"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-reasoner"
        
    async def analyze_market(self, candles, asset, indicators_data):
        """Use DeepSeek-R1 to analyze market"""
        if not self.api_key:
            logger.info("No DeepSeek API key - using local AI")
            return None
        
        try:
            recent_prices = [c['close'] for c in candles[-20:]]
            prompt = self._create_analysis_prompt(asset, recent_prices, indicators_data)
            
            # Use aiohttp for non-blocking HTTP request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result['choices'][0]['message']['content']
                        return self._parse_ai_response(ai_response)
                    else:
                        logger.warning(f"DeepSeek API returned status: {response.status}")
        
        except asyncio.TimeoutError:
            logger.error("DeepSeek API request timed out")
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
        
        return None
    
    def _create_analysis_prompt(self, asset, prices, indicators):
        return f"""Analyze {asset} and predict next direction.
Recent prices: {prices}
RSI: {indicators.get('rsi', 'N/A')}
MACD: {indicators.get('macd', 'N/A')}
Trend: {indicators.get('trend', 'N/A')}
Respond with only "CALL" or "PUT" and confidence."""
    
    def _parse_ai_response(self, response):
        response = response.upper()
        if "CALL" in response and "PUT" not in response:
            return "CALL"
        elif "PUT" in response:
            return "PUT"
        return None


class GrokAI:
    """Grok AI for real-time market analysis"""
    def __init__(self, api_key=None):
        self.api_key = api_key
        
    async def analyze_sentiment(self, asset):
        return {"sentiment": "neutral", "confidence": 0.5}


class EnsembleAI:
    """Ensemble AI combining multiple models"""
    
    def __init__(self, config):
        self.deepseek = DeepSeekAI(config.get('deepseek_api_key'))
        self.grok = GrokAI(config.get('grok_api_key'))
        self.use_ensemble = config.get('use_ensemble_ai', True)
        
    async def generate_prediction(self, candles, asset, indicators):
        predictions = []
        
        deepseek_pred = await self.deepseek.analyze_market(candles, asset, indicators)
        if deepseek_pred:
            predictions.append(("DEEPSEEK", deepseek_pred, 0.8))
        
        sentiment = await self.grok.analyze_sentiment(asset)
        if sentiment['sentiment'] == "bullish":
            predictions.append(("SENTIMENT", "CALL", sentiment['confidence']))
        elif sentiment['sentiment'] == "bearish":
            predictions.append(("SENTIMENT", "PUT", sentiment['confidence']))
        
        return self._combine_predictions(predictions)
    
    def _combine_predictions(self, predictions):
        if not predictions:
            return None, 0
        
        call_votes = 0
        put_votes = 0
        total_weight = 0
        
        for source, direction, confidence in predictions:
            if direction == "CALL":
                call_votes += confidence
            else:
                put_votes += confidence
            total_weight += confidence
        
        if total_weight == 0:
            return None, 0
        
        call_score = call_votes / total_weight
        put_score = put_votes / total_weight
        
        if call_score > 0.6:
            return "CALL", call_score
        elif put_score > 0.6:
            return "PUT", put_score
        
        return None, 0


class MLPatternRecognition:
    """ML for pattern recognition"""
    
    def __init__(self):
        self.patterns_learned = []
        
    async def detect_patterns(self, candles):
        if len(candles) < 50:
            return []
        
        patterns = []
        
        if self._is_head_shoulders(candles):
            patterns.append("head_shoulders")
        if self._is_double_top(candles):
            patterns.append("double_top")
        if self._is_double_bottom(candles):
            patterns.append("double_bottom")
        if self._is_triangle(candles):
            patterns.append("triangle")
        
        return patterns
    
    def _is_head_shoulders(self, candles):
        highs = [c['high'] for c in candles[-20:]]
        if len(highs) < 15:
            return False
        middle_high = max(highs[5:10])
        left_shoulder = max(highs[:5])
        right_shoulder = max(highs[10:])
        if (middle_high > left_shoulder * 1.02 and 
            middle_high > right_shoulder * 1.02):
            return True
        return False
    
    def _is_double_top(self, candles):
        highs = [c['high'] for c in candles[-20:]]
        if len(highs) < 10:
            return False
        recent_highs = highs[-10:]
        max1 = max(recent_highs[:5])
        max2 = max(recent_highs[5:])
        if abs(max1 - max2) / max1 < 0.02:
            return True
        return False
    
    def _is_double_bottom(self, candles):
        lows = [c['low'] for c in candles[-20:]]
        if len(lows) < 10:
            return False
        recent_lows = lows[-10:]
        min1 = min(recent_lows[:5])
        min2 = min(recent_lows[5:])
        if abs(min1 - min2) / min1 < 0.02:
            return True
        return False
    
    def _is_triangle(self, candles):
        highs = [c['high'] for c in candles[-20:]]
        lows = [c['low'] for c in candles[-20:]]
        if len(highs) < 15:
            return False
        high_trend = highs[-1] - highs[-15]
        low_trend = lows[-1] - lows[-15]
        if high_trend < 0 and low_trend > 0:
            return True
        return False


class AdaptiveAI:
    """Self-learning AI that adapts to market conditions"""
    
    def __init__(self):
        self.market_regimes = {
            "trending_up": {"calls_weight": 0.8, "puts_weight": 0.2},
            "trending_down": {"calls_weight": 0.2, "puts_weight": 0.8},
            "sideways": {"calls_weight": 0.5, "puts_weight": 0.5},
            "volatile": {"calls_weight": 0.4, "puts_weight": 0.4},
        }
        self.current_regime = "sideways"
        self.performance_history = []
        
    async def detect_regime(self, candles):
        if len(candles) < 50:
            return "sideways"
        
        prices = [c['close'] for c in candles[-50:]]
        first_half = sum(prices[:25]) / 25
        second_half = sum(prices[25:]) / 25
        trend = (second_half - first_half) / first_half
        
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        volatility = (variance ** 0.5) / mean
        
        if abs(trend) > 0.02:
            if trend > 0:
                self.current_regime = "trending_up"
            else:
                self.current_regime = "trending_down"
        elif volatility > 0.02:
            self.current_regime = "volatile"
        else:
            self.current_regime = "sideways"
        
        return self.current_regime
    
    def get_adjusted_prediction(self, base_prediction, confidence):
        regime = self.market_regimes.get(self.current_regime, {"calls_weight": 0.5, "puts_weight": 0.5})
        
        if base_prediction == "CALL":
            adjusted_confidence = confidence * regime["calls_weight"]
        elif base_prediction == "PUT":
            adjusted_confidence = confidence * regime["puts_weight"]
        else:
            adjusted_confidence = 0
        
        return adjusted_confidence
    
    def record_performance(self, prediction, actual_result):
        self.performance_history.append({
            "prediction": prediction,
            "result": actual_result,
            "regime": self.current_regime,
            "timestamp": time.time()
        })
        
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]


def create_ai_engine(config):
    """Factory function to create AI engine"""
    ai_type = config.get('ai_engine', 'ensemble')
    
    if ai_type == 'deepseek':
        return DeepSeekAI(config.get('deepseek_api_key'))
    elif ai_type == 'ensemble':
        return EnsembleAI(config)
    elif ai_type == 'adaptive':
        return AdaptiveAI()
    else:
        return EnsembleAI(config)
