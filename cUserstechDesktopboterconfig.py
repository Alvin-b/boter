# Trading Bot Configuration
# This is for educational purposes only - do not use for real trading

CONFIG = {
    # API Settings
    'email': 'your_email@example.com',  # Replace with your Pocket Option email
    'password': 'your_password',        # Replace with your Pocket Option password
    'demo': True,                       # Use demo account for testing
    
    # Trading Settings
    'asset': 'EUR/USD',                 # Trading asset
    'amount': 10,                       # Base trade amount in USD
    'expiry': 60,                       # Trade expiry in seconds (1 minute)
    
    # Risk Management
    'max_daily_loss': 100,              # Stop trading if daily loss exceeds this
    'max_trades_per_day': 50,           # Maximum trades per day
    'min_win_rate': 0.6,                # Minimum win rate to continue trading
    
    # Strategy Settings
    'signal_check_interval': 5,         # Seconds between signal checks
    
    # Martingale Settings (HIGH RISK - Use with caution)
    'martingale_enabled': False,        # Enable/disable Martingale
    'martingale_multiplier': 2.0,       # Amount multiplier after loss
    'max_martingale_steps': 3,          # Maximum Martingale steps
    
    # Technical Indicators
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'bollinger_period': 20,
    'bollinger_std': 2,
    'stochastic_period': 14,
    'adx_period': 14,
    'cci_period': 20,
}
