# Pocket Option AI Trading Bot

A professional automated binary options trading bot with AI-powered asset selection and high accuracy signals.

## Features

- **🤖 AI Asset Scanner**: Scans 10+ currency pairs and crypto to find the BEST trading opportunity
- **🎯 High Accuracy Signals**: Uses 9+ technical indicators with weighted scoring
- **🔐 Browser Login**: Login to your Pocket Option account via browser
- **📊 Risk Management**: Daily loss limits, win rate monitoring, martingale
- **📈 Real-time Analysis**: Continuous market scanning and signal generation

## Quick Start

### Option 1: Demo Mode (Recommended for testing)

```bash
pip install -r requirements.txt
python trading_bot.py
```

The bot will run in demo mode with simulated trades.

### Option 2: Live Trading with Browser Login

1. Edit `config.py`:
```python
DEMO_MODE = False
USE_BROWSER_LOGIN = True
```

2. Run the bot:
```bash
python trading_bot.py
```

3. The bot will show you the Pocket Option login URL
4. Login in your browser
5. Press ENTER in the terminal
6. Bot will start executing trades on your account!

## Configuration

Edit `config.py` to customize:

```python
# Trading Amount
TRADING_AMOUNT = 10          # $10 per trade

# Risk Management
MAX_DAILY_LOSS = 100         # Stop if loss > $100
MIN_WIN_RATE = 0.6           # Stop if win rate < 60%

# Signal Strength (Higher = Safer trades)
MIN_SIGNAL_STRENGTH = 0.7   # Only trade with 70%+ confidence
```

## How the AI Works

1. **Multi-Asset Scanning**: Scans all available assets (EUR/USD, GBP/USD, etc.)
2. **Signal Generation**: Uses 9 technical indicators:
   - EMA Crossover
   - RSI Divergence
   - MACD Momentum
   - Bollinger Bands
   - Stochastic Oscillator
   - Trend Alignment
   - Candlestick Patterns
   - Support/Resistance
   - Price Action

3. **Best Pair Selection**: Chooses the asset with:
   - Highest signal strength
   - Best trend alignment
   - Optimal volatility

4. **High Accuracy**: Only trades when multiple indicators agree (score ≥ 8/20)

## Project Structure

```
boter/
├── config.py            # Configuration settings
├── indicators.py        # Technical indicators
├── signals.py           # AI signal generation
├── pocket_option_api.py # API connection
├── trading_bot.py       # Main trading bot
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Risk Warning

⚠️ **IMPORTANT**: Binary options trading involves substantial risk.
- Never trade with money you cannot afford to lose
- Always start with demo mode
- Use risk management settings
- Past performance does not guarantee future results

## Support

For issues or questions, check the logs in `trading_bot.log`


