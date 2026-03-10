import asyncio
import sys
import os
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_bot import TradingBot
from pocket_option_api import PocketOptionAPI, PocketOptionReal, MockPocketOptionAPI

CONFIG_FILE = 'bot_config.json'

# Default configuration (fallback if config file doesn't exist)
DEFAULT_CONFIG = {
    'email': '',
    'password': '',
    'demo': True,
    'browser_auth': True,
    'asset': 'EUR/USD',
    'amount': 10,
    'expiry': 60,
    'max_daily_loss': 100,
    'max_trades_per_day': 50,
    'min_win_rate': 0.6,
    'signal_check_interval': 10,
    'martingale_enabled': True,
    'martingale_multiplier': 2.0,
    'max_martingale_steps': 3,
}


def load_config():
    """Load configuration from JSON file (created by GUI)"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = DEFAULT_CONFIG.copy()
                config.update(saved_config)
                return config
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    return DEFAULT_CONFIG.copy()


async def main():
    """Main function"""
    print("Pocket Option Trading Bot")
    print("Educational purposes only - do not use for real trading")
    print("=" * 50)
    
    # Load configuration from JSON file (created by GUI)
    config = load_config()
    
    print(f"Loaded configuration from {CONFIG_FILE}")
    print(f"Demo Mode: {config['demo']}")
    print(f"Asset: {config['asset']}")
    print(f"Amount: ${config['amount']}")
    print("=" * 50)
    
    # Use Pocket Option demo account (demo=true) or real account (demo=false)
    # When demo=true: Real trades on Pocket Option's demo account with virtual money
    # When demo=false: Real trades on Pocket Option's real account with real money
    if config['demo']:
        print("Connecting to Pocket Option DEMO ACCOUNT (real trades, virtual money)...")
        api = PocketOptionReal(
            email=config['email'],
            password=config['password'],
            headless=False,
            use_demo=True
        )
    else:
        print("Connecting to Pocket Option REAL ACCOUNT (real trades, real money)...")
        api = PocketOptionReal(
            email=config['email'],
            password=config['password'],
            headless=False,
            use_demo=False
        )
    
    # Connect and authenticate
    connected = await api.connect()
    if not connected:
        print("Failed to connect to Pocket Option. Make sure Chrome is installed.")
        return
    
    authenticated = await api.authenticate()
    if not authenticated:
        print("Failed to authenticate. Check your credentials.")
        await api.disconnect()
        return
    
    if config['demo']:
        print("Successfully connected to Pocket Option DEMO ACCOUNT!")
    else:
        print("Successfully connected to Pocket Option REAL ACCOUNT!")
    
    # Create and start trading bot
    bot = TradingBot(api, config)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\nStopping bot...")
        await bot.stop()
    except Exception as e:
        print(f"Error: {e}")
        await bot.stop()


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())


