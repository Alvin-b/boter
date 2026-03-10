"""
Simple Pocket Option Trading Bot - Working Version
"""
import asyncio
import random
import time
import os

# Configuration
CONFIG_FILE = 'bot_config.json'

def load_config():
    """Load configuration from JSON file created by GUI"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "DEMO_MODE": True,
        "TRADING_AMOUNT": 10,
        "TRADE_EXPIRY": 60,
        "MIN_SIGNAL_STRENGTH": 0.6,
        "AVAILABLE_ASSETS": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"],
        "MAX_DAILY_LOSS": 100,
        "MAX_TRADES_PER_DAY": 50,
        "MARTINGALE_ENABLED": True,
        "MARTINGALE_MULTIPLIER": 2.0,
        "MAX_MARTINGALE_STEPS": 3
    }


class SimpleAPI:
    """Simple mock API for testing"""
    
    def __init__(self):
        self.balance = 10000
        
    async def connect(self):
        print("[API] Connected")
        return True
    
    async def authenticate(self):
        print("[API] Authenticated")
        return True
    
    async def get_balance(self):
        return self.balance
    
    async def get_candles(self, asset, timeframe=60, count=100):
        # Generate realistic candle data
        candles = []
        base_price = 1.0850
        
        for i in range(count):
            change = random.uniform(-0.0005, 0.0006)
            o = base_price
            c = base_price + change
            h = max(o, c) + random.uniform(0, 0.0003)
            l = min(o, c) - random.uniform(0, 0.0003)
            
            candles.append({
                'open': round(o, 5),
                'high': round(h, 5),
                'low': round(l, 5),
                'close': round(c, 5)
            })
            base_price = c
        
        return candles
    
    async def open_trade(self, asset, direction, amount, expiry):
        win = random.random() < 0.65
        profit = amount * 0.8 if win else -amount
        self.balance += profit
        
        return {
            'success': True,
            'trade_id': f'trade_{int(time.time())}',
            'result': 'win' if win else 'loss',
            'profit': profit
        }
    
    async def disconnect(self):
        print("[API] Disconnected")


class SignalGen:
    """Simple signal generator"""
    
    @staticmethod
    def analyze(candles):
        if not candles or len(candles) < 20:
            return "NEUTRAL", 0.0
        
        closes = [c['close'] for c in candles]
        
# Simple SMA crossover
        sma5 = sum(closes[-5:]) / 5
        sma10 = sum(closes[-10:]) / 10
        
        if sma5 > sma10 * 1.001:
            return "CALL", 0.7
        elif sma5 < sma10 * 0.999:
            return "PUT", 0.7
        elif closes[-1] > sum(closes[-10:]) / 10:
            return "CALL", 0.6
        else:
            return "PUT", 0.6


async def main():
    print("=" * 50)
    print("POCKET OPTION TRADING BOT")
    print("=" * 50)
    
    api = SimpleAPI()
    await api.connect()
    await api.authenticate()
    
    balance = await api.get_balance()
    print(f"Balance: ${balance}")
    
    assets = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]
    
    for i in range(5):
        print(f"\n--- Scan #{i+1} ---")
        
        # Find best asset
        best_asset = None
        best_signal = "NEUTRAL"
        best_strength = 0
        
        for asset in assets:
            candles = await api.get_candles(asset, 60, 100)
            signal, strength = SignalGen.analyze(candles)
            print(f"  {asset}: {signal} ({strength:.0%})")
            
            if signal != "NEUTRAL" and strength > best_strength:
                best_asset = asset
                best_signal = signal
                best_strength = strength
        
        if best_asset and best_strength >= MIN_SIGNAL_STRENGTH:
            print(f"\n>>> TRADING: {best_signal} on {best_asset} (${TRADING_AMOUNT})")
            result = await api.open_trade(best_asset, best_signal.lower(), TRADING_AMOUNT, TRADE_EXPIRY)
            print(f"Result: {result['result'].upper()} - Profit: ${result['profit']:.2f}")
        
        await asyncio.sleep(2)
    
    print("\n" + "=" * 50)
    print("Bot finished")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
