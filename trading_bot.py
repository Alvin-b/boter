"""
Pocket Option Trading Bot - Advanced AI Version
"""

import asyncio
import logging
import time
from pocket_option_api import PocketOptionAPI, MockPocketOptionAPI
from signals import SignalGenerator
import config as cfg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AssetAnalyzer:
    """Analyzes multiple assets to find the best trading opportunity"""
    
    def __init__(self, api):
        self.api = api
        self.signal_generator = SignalGenerator()
        
    async def analyze_all_assets(self, assets):
        """Analyze all assets and return the best one to trade"""
        results = []
        
        logger.info(f"Scanning {len(assets)} assets for best trading opportunity...")
        
        for asset in assets:
            try:
                candles = await self.api.get_candles(asset, timeframe=60, count=100)
                
                if not candles or len(candles) < 50:
                    continue
                
                signal = self.signal_generator.analyze_market(candles)
                strength = self.signal_generator.get_signal_strength(candles)
                
                volatility = self._calculate_volatility(candles)
                trend_strength = self._get_trend_strength(candles)
                
                score = self._calculate_opportunity_score(signal, strength, volatility, trend_strength)
                
                results.append({
                    'asset': asset,
                    'signal': signal,
                    'strength': strength,
                    'volatility': volatility,
                    'trend_strength': trend_strength,
                    'score': score
                })
                
                logger.info(f"  {asset}: {signal} (Strength: {strength:.1%}, Score: {score:.1f})")
                
            except Exception as e:
                import traceback
                logger.warning(f"  Error analyzing {asset}: {str(e)}")
                print(f"DEBUG: {traceback.format_exc()}")
        
        if not results:
            return None, "NEUTRAL", 0
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        best = results[0]
        
        logger.info(f"\n*** BEST OPPORTUNITY: {best['asset']} ***")
        logger.info(f"    Signal: {best['signal']}, Strength: {best['strength']:.1%}")
        logger.info(f"    Score: {best['score']:.1f}\n")
        
        return best['asset'], best['signal'], best['strength']
    
    def _calculate_volatility(self, candles):
        if len(candles) < 20:
            return 0
        
        prices = [c['close'] for c in candles[-20:]]
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        volatility = (variance ** 0.5 / mean) * 100 if mean > 0 else 0
        return volatility
    
    def _get_trend_strength(self, candles):
        if len(candles) < 20:
            return 0
        
        prices = [c['close'] for c in candles[-20:]]
        n = len(prices)
        x_mean = (n - 1) / 2
        y_mean = sum(prices) / n
        
        numerator = sum((i - x_mean) * (prices[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        trend_strength = abs(slope / y_mean) * 100 if y_mean > 0 else 0
        return trend_strength
    
    def _calculate_opportunity_score(self, signal, strength, volatility, trend_strength):
        if signal == "NEUTRAL":
            return 0
        
        score = 0
        score += strength * 40
        score += min(trend_strength * 3, 30)
        
        if 0.5 < volatility < 2.0:
            score += 20
        elif 0.2 < volatility < 3.0:
            score += 10
        
        if signal == "CALL" or signal == "PUT":
            score += 10
        
        return score


class TradingBot:
    """Main trading bot class with AI-powered asset selection"""
    
    def __init__(self, api, config):
        self.api = api
        self.config = config
        self.signal_generator = SignalGenerator()
        self.asset_analyzer = AssetAnalyzer(api)
        
        self.is_trading = False
        self.current_asset = config.get('asset', 'EUR/USD')
        self.base_amount = config.get('amount', 10)
        self.current_amount = self.base_amount
        self.trades_today = 0
        self.wins_today = 0
        self.losses_today = 0
        self.daily_pnl = 0
        self.last_trade_time = 0
        self.martingale_step = 0
        
        self.total_trades = 0
        self.total_wins = 0
        self.total_losses = 0
        self.win_streak = 0
        self.loss_streak = 0
        self.best_win_streak = 0
        self.best_loss_streak = 0
        
        self.available_assets = config.get('available_assets', [
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", 
            "USD/CAD", "EUR/GBP", "BTC/USD", "ETH/USD"
        ])
        
        logger.info("Advanced Trading Bot initialized")
    
    async def start(self):
        logger.info("=" * 60)
        logger.info("POCKET OPTION AI TRADING BOT")
        logger.info("=" * 60)
        
        try:
            connected = await self.api.connect()
            if not connected:
                logger.warning("Failed to connect, using mock API")
                self.api = MockPocketOptionAPI(demo=True)
                await self.api.connect()
            
            authenticated = await self.api.authenticate()
            if not authenticated:
                logger.warning("Authentication failed, using mock mode")
            
            balance = await self.api.get_balance()
            logger.info(f"Account Balance: ${balance:.2f}")
            logger.info(f"Available Assets: {', '.join(self.available_assets)}")
            
            self.is_trading = True
            await self.trading_loop()
            
        except KeyboardInterrupt:
            logger.info("Trading interrupted by user")
            await self.stop()
        except Exception as e:
            logger.error(f"Trading error: {e}")
            await self.stop()
    
    async def stop(self):
        logger.info("Stopping Trading Bot...")
        self.is_trading = False
        self.print_statistics()
        await self.api.disconnect()
        logger.info("Trading Bot stopped")
    
    async def trading_loop(self):
        logger.info("\n" + "=" * 60)
        logger.info("STARTING AI TRADING LOOP")
        logger.info("=" * 60 + "\n")
        
        scan_count = 0
        
        while self.is_trading:
            try:
                if not self.should_trade():
                    await asyncio.sleep(10)
                    continue
                
                scan_count += 1
                logger.info(f"\n--- Scan #{scan_count} ---")
                
                best_asset, signal, strength = await self.asset_analyzer.analyze_all_assets(
                    self.available_assets
                )
                
                if best_asset is None or signal == "NEUTRAL":
                    logger.info("No good trading opportunities found, waiting...")
                    await asyncio.sleep(self.config.get('signal_check_interval', 10))
                    continue
                
                min_strength = self.config.get('min_signal_strength', 0.6)
                
                if strength >= min_strength:
                    self.current_asset = best_asset
                    await self.execute_trade(signal, strength)
                else:
                    logger.info(f"Signal strength {strength:.1%} below threshold {min_strength:.1%}")
                
                wait_time = self.config.get('signal_check_interval', 10)
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(10)
    
    def should_trade(self):
        if self.daily_pnl <= -self.config.get('max_daily_loss', 100):
            logger.warning("Daily loss limit reached")
            return False
        
        if self.trades_today >= self.config.get('max_trades_per_day', 50):
            logger.warning("Max daily trades reached")
            return False
        
        if self.trades_today > 10:
            win_rate = self.wins_today / self.trades_today
            if win_rate < self.config.get('min_win_rate', 0.6):
                logger.warning(f"Win rate too low: {win_rate:.1%}")
                return False
        
        return True
    
    async def execute_trade(self, signal, strength):
        logger.info(f"\n*** EXECUTING TRADE ***")
        logger.info(f"Asset: {self.current_asset}")
        logger.info(f"Direction: {signal}")
        logger.info(f"Strength: {strength:.1%}")
        logger.info(f"Amount: ${self.current_amount}")
        
        direction = "call" if signal == "CALL" else "put"
        
        result = await self.api.open_trade(
            self.current_asset,
            direction,
            self.current_amount,
            self.config.get('expiry', 60)
        )
        
        if result and result.get('success'):
            self.total_trades += 1
            self.trades_today += 1
            self.last_trade_time = time.time()
            
            trade_id = result.get('trade_id')
            logger.info(f"Trade opened: {trade_id}")
            
            await self.process_trade_result(result)
            self.apply_martingale(result.get('result') == 'win')
            
        else:
            logger.error("Failed to open trade")
    
    async def process_trade_result(self, trade_result):
        result = trade_result.get('result', 'win')
        
        if result == 'win':
            self.wins_today += 1
            self.total_wins += 1
            self.win_streak += 1
            self.loss_streak = 0
            
            if self.win_streak > self.best_win_streak:
                self.best_win_streak = self.win_streak
            
            profit = trade_result.get('profit', self.current_amount * 0.8)
            self.daily_pnl += profit
            
            logger.info(f"\n✅ WIN! Profit: ${profit:.2f}")
            logger.info(f"   Daily PnL: ${self.daily_pnl:.2f}\n")
            
        else:
            self.losses_today += 1
            self.total_losses += 1
            self.loss_streak += 1
            self.win_streak = 0
            
            if self.loss_streak > self.best_loss_streak:
                self.best_loss_streak = self.loss_streak
            
            loss = trade_result.get('profit', -self.current_amount)
            self.daily_pnl += loss
            
            logger.info(f"\n❌ LOSS! Loss: ${abs(loss):.2f}")
            logger.info(f"   Daily PnL: ${self.daily_pnl:.2f}\n")
    
    def apply_martingale(self, won):
        if not self.config.get('martingale_enabled', True):
            self.current_amount = self.base_amount
            self.martingale_step = 0
            return
        
        if won:
            self.current_amount = self.base_amount
            self.martingale_step = 0
            logger.info(f"Martingale: Reset to ${self.base_amount}")
        else:
            if self.martingale_step < self.config.get('max_martingale_steps', 3):
                self.martingale_step += 1
                multiplier = self.config.get('martingale_multiplier', 2.0)
                self.current_amount = self.base_amount * (multiplier ** self.martingale_step)
                logger.info(f"Martingale: Step {self.martingale_step}, Amount: ${self.current_amount}")
            else:
                self.current_amount = self.base_amount
                self.martingale_step = 0
    
    def print_statistics(self):
        logger.info("\n" + "=" * 60)
        logger.info("TRADING STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total Trades: {self.total_trades}")
        logger.info(f"Wins: {self.total_wins}")
        logger.info(f"Losses: {self.total_losses}")
        
        if self.total_trades > 0:
            win_rate = self.total_wins / self.total_trades * 100
            logger.info(f"Win Rate: {win_rate:.1f}%")
        
        logger.info(f"Best Win Streak: {self.best_win_streak}")
        logger.info(f"Best Loss Streak: {self.best_loss_streak}")
        logger.info(f"Daily PnL: ${self.daily_pnl:.2f}")
        logger.info("=" * 60)


class TradingConfig:
    """Trading configuration"""
    
    def __init__(self):
        self.demo = getattr(cfg, 'DEMO_MODE', True)
        self.use_browser_login = getattr(cfg, 'USE_BROWSER_LOGIN', True)
        self.email = getattr(cfg, 'POCKET_OPTION_EMAIL', '')
        self.password = getattr(cfg, 'POCKET_OPTION_PASSWORD', '')
        
        self.asset = getattr(cfg, 'DEFAULT_ASSET', 'EUR/USD')
        self.amount = getattr(cfg, 'TRADING_AMOUNT', 10)
        self.expiry = getattr(cfg, 'TRADE_EXPIRY', 60)
        
        self.max_daily_loss = getattr(cfg, 'MAX_DAILY_LOSS', 100)
        self.max_trades_per_day = getattr(cfg, 'MAX_TRADES_PER_DAY', 50)
        self.min_win_rate = getattr(cfg, 'MIN_WIN_RATE', 0.6)
        
        self.martingale_enabled = getattr(cfg, 'MARTINGALE_ENABLED', True)
        self.martingale_multiplier = getattr(cfg, 'MARTINGALE_MULTIPLIER', 2.0)
        self.max_martingale_steps = getattr(cfg, 'MAX_MARTINGALE_STEPS', 3)
        
        self.signal_check_interval = getattr(cfg, 'SIGNAL_CHECK_INTERVAL', 10)
        self.min_signal_strength = getattr(cfg, 'MIN_SIGNAL_STRENGTH', 0.6)
        
        self.available_assets = getattr(cfg, 'AVAILABLE_ASSETS', [
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", 
            "USD/CAD", "EUR/GBP", "BTC/USD", "ETH/USD"
        ])
    
    def get(self, key, default=None):
        return getattr(self, key, default)


async def main():
    config = TradingConfig()
    
    logger.info("=" * 60)
    logger.info("POCKET OPTION AI TRADING BOT")
    logger.info("=" * 60)
    logger.info(f"Demo Mode: {config.demo}")
    logger.info(f"Assets: {', '.join(config.available_assets)}")
    logger.info("=" * 60)
    
    api = MockPocketOptionAPI(demo=True)
    
    bot_config = {
        'asset': config.asset,
        'amount': config.amount,
        'expiry': config.expiry,
        'max_daily_loss': config.max_daily_loss,
        'max_trades_per_day': config.max_trades_per_day,
        'min_win_rate': config.min_win_rate,
        'martingale_enabled': config.martingale_enabled,
        'martingale_multiplier': config.martingale_multiplier,
        'max_martingale_steps': config.max_martingale_steps,
        'signal_check_interval': config.signal_check_interval,
        'min_signal_strength': config.min_signal_strength,
        'available_assets': config.available_assets,
    }
    
    bot = TradingBot(api, bot_config)
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
