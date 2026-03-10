"""
⚠️ IMPORTANT DISCLAIMER - READ BEFORE USE ⚠️

This bot is for EDUCATIONAL PURPOSES ONLY.

1. DEMO MODE: When DEMO_MODE=True, this is COMPLETE SIMULATION with fake trades
2. NOT REAL TRADING: The "live trading" feature requires actual Pocket Option API 
   integration which is not fully implemented - it will simulate trades only
3. FINANCIAL RISK: Binary options trading carries HIGH RISK. You can lose ALL money.
4. MARGINALE WARNING: Martingale systems WILL eventually lose all money in long run
5. REGULATION: Binary options are heavily restricted or banned in many jurisdictions

USE AT YOUR OWN RISK. Never trade with money you cannot afford to lose.

"""

import os

# ============================================
# LOGIN MODE SETTINGS
# ============================================

# Set to False for real trading (will execute trades on real Pocket Option account)
# IMPORTANT: Make sure you have a Pocket Option account and understand the risks
DEMO_MODE = False

# Set to True to use browser login flow  
USE_BROWSER_LOGIN = True

# Credentials - RECOMMEND: Use environment variables instead
# Set via: set POCKET_OPTION_EMAIL=your@email.com
POCKET_OPTION_EMAIL = os.getenv('POCKET_OPTION_EMAIL', '')
POCKET_OPTION_PASSWORD = os.getenv('POCKET_OPTION_PASSWORD', '')

# Demo and browser auth settings (used by main.py)
POCKET_OPTION_DEMO_ACCOUNT = DEMO_MODE
POCKET_OPTION_BROWSER_AUTH = USE_BROWSER_LOGIN

# ============================================
# TRADING SETTINGS
# ============================================

TRADING_AMOUNT = 10
DEFAULT_ASSET = "EUR/USD"
TRADE_EXPIRY = 60

# ============================================
# MONEY MANAGEMENT  
# ============================================

# ⚠️ WARNING: Martingale can lead to total loss
MARTINGALE_ENABLED = True
MARTINGALE_MULTIPLIER = 2.0
MAX_MARTINGALE_STEPS = 3

# ============================================
# RISK MANAGEMENT
# ============================================

MAX_DAILY_LOSS = 100
MAX_TRADES_PER_DAY = 50
MIN_WIN_RATE = 0.6

# ============================================
# SIGNAL SETTINGS
# ============================================

MIN_SIGNAL_STRENGTH = 0.7
SIGNAL_CHECK_INTERVAL = 10

# ============================================
# AVAILABLE ASSETS
# ============================================

AVAILABLE_ASSETS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
    "USD/CAD", "EUR/GBP", "EUR/JPY", "GBP/JPY",
    "BTC/USD", "ETH/USD"
]

# ============================================
# TECHNICAL INDICATORS
# ============================================

SHORT_EMA_PERIOD = 5
LONG_EMA_PERIOD = 20
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2

# ============================================
# LOGGING
# ============================================

LOG_LEVEL = "INFO"
LOG_FILE = "trading_bot.log"

# ============================================
# AI ENGINE SETTINGS
# ============================================

USE_ENSEMBLE_AI = True
AI_ENGINE = "ensemble"
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
GROK_API_KEY = os.getenv('GROK_API_KEY', '')
USE_PATTERN_RECOGNITION = True
USE_MARKET_REGIME_DETECTION = True

