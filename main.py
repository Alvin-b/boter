import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from trading_bot import TradingBot
from pocket_option_api import PocketOptionAPI


async def main():
    """Main function"""
    print("Pocket Option Trading Bot")
    print("Educational purposes only - do not use for real trading")
    print("=" * 50)
    
    # Load configuration
    config = {
        'email': POCKET_OPTION_EMAIL,
        'password': POCKET_OPTION_PASSWORD,
        'demo': POCKET_OPTION_DEMO_ACCOUNT,
        'browser_auth': POCKET_OPTION_BROWSER_AUTH,
        'asset': DEFAULT_ASSET,
        'amount': TRADING_AMOUNT,
        'expiry': TRADE_EXPIRY,
        'max_daily_loss': MAX_DAILY_LOSS,
        'max_trades_per_day': MAX_TRADES_PER_DAY,
        'min_win_rate': MIN_WIN_RATE,
        'signal_check_interval': SIGNAL_CHECK_INTERVAL,
        'martingale_enabled': MARTINGALE_ENABLED,
        'martingale_multiplier': MARTINGALE_MULTIPLIER,
        'max_martingale_steps': MAX_MARTINGALE_STEPS,
    }
    
    # Override with environment variables if available
    config['email'] = os.getenv('POCKET_OPTION_EMAIL', config['email'])
    config['password'] = os.getenv('POCKET_OPTION_PASSWORD', config['password'])
    
    # Create API instance
    api = PocketOptionAPI(
        email=config['email'],
        password=config['password'],
        demo=config['demo'],
        browser_auth=config['browser_auth']
    )
    
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