#!/usr/bin/env python
"""Quick test of signal generator"""
import asyncio
from pocket_option_api import MockPocketOptionAPI
from signals import SignalGenerator

async def main():
    print("Testing signal generator...")
    api = MockPocketOptionAPI(demo=True)
    candles = await api.get_candles('EUR/USD', 60, 100)
    print(f"Got {len(candles)} candles")
    print(f"First candle: {candles[0]}")
    
    sg = SignalGenerator()
    signal = sg.analyze_market(candles)
    print(f"Signal: {signal}")
    
    strength = sg.get_signal_strength(candles)
    print(f"Strength: {strength}")

asyncio.run(main())
