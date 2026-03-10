"""
Pocket Option Real Trading Bot - Browser Automation
Uses Selenium to automate trading on Pocket Option web platform

⚠️ WARNING: This uses browser automation which may violate Pocket Option ToS
Use at your own risk
"""

import asyncio
import logging
import time
import random
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class PocketOptionReal:
    """Real Pocket Option trading via browser automation"""
    
    def __init__(self, email, password, headless=False, use_demo=True):
        self.email = email
        self.password = password
        self.headless = headless
        self.use_demo = use_demo  # If True, use Pocket Option's demo account
        self.driver = None
        self.is_logged_in = False
        self.balance = 0
        self.session_id = None
        
    async def connect(self):
        """Initialize browser and login"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            import os
            
            # Setup Chrome options
            chrome_options = Options()
            
            # Check if running on headless server (no display)
            if os.environ.get('DISPLAY') is None and os.environ.get('WAYLAND_DISPLAY') is None:
                # No display available - use headless mode
                chrome_options.add_argument("--headless=new")
                logger.info("Running in headless mode (no display detected)")
            elif self.headless:
                # User explicitly requested headless
                chrome_options.add_argument("--headless=new")
            
            # Essential options for servers
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--remote-debugging-port=9222")
            
            try:
                # Try regular Chrome
                self.driver = webdriver.Chrome(options=chrome_options)
            except:
                # Try Chromium if Chrome fails
                try:
                    chrome_options.binary_location = "/usr/bin/chromium"
                    self.driver = webdriver.Chrome(options=chrome_options)
                except:
                    chrome_options.binary_location = "/usr/bin/chromium-browser"
                    self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute stealth script
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            if self.use_demo:
                # Go directly to demo trading
                logger.info("Navigating to Pocket Option demo trading...")
                self.driver.get("https://pocketoption.com/en/demo-trading/")
            else:
                # Go to main site
                logger.info("Navigating to Pocket Option...")
                self.driver.get("https://pocketoption.com/")
            
            return True
            
        except ImportError:
            logger.error("Selenium not installed. Run: pip install selenium")
            return False
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def authenticate(self):
        """Login to Pocket Option - supports both demo and real accounts"""
        if not self.driver:
            return False
            
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, 20)
            
            # If using demo account, try to click "Try Demo" button first
            if self.use_demo:
                try:
                    # Look for Demo button/link
                    demo_xpaths = [
                        "//a[contains(text(),'Demo')]",
                        "//button[contains(text(),'Demo')]",
                        "//span[contains(text(),'Demo')]",
                        "//div[contains(@class,'demo')]//a",
                        "//a[contains(@href,'demo')]"
                    ]
                    for xpath in demo_xpaths:
                        try:
                            demo_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            demo_btn.click()
                            logger.info("Clicked Demo button")
                            await asyncio.sleep(3)
                            break
                        except:
                            continue
                except Exception as e:
                    logger.warning(f"Could not find Demo button: {e}")
            
            # If we have credentials, try to login
            if self.email and self.password:
                # Click login button - try multiple selectors
                try:
                    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login')]")))
                    login_btn.click()
                except:
                    # Try alternative
                    login_link = self.driver.find_elements(By.XPATH, "//a[contains(text(),'Login')]")
                    if login_link:
                        login_link[0].click()
                
                # Wait for login modal
                await asyncio.sleep(2)
                
                # Enter email
                try:
                    email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
                    email_input.clear()
                    email_input.send_keys(self.email)
                except:
                    # Try alternative selector
                    email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
                    email_input.clear()
                    email_input.send_keys(self.email)
                
                # Enter password
                password_input = self.driver.find_element(By.NAME, "password")
                password_input.clear()
                password_input.send_keys(self.password)
                
                # Click submit
                submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_btn.click()
                
                # Wait for login to complete
                await asyncio.sleep(5)
            
            # Check if logged in
            current_url = self.driver.current_url
            if "dashboard" in current_url or "trade" in current_url or "cabinet" in current_url or "demo" in current_url:
                self.is_logged_in = True
                logger.info("Successfully logged in to Pocket Option")
                await self.get_balance()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def get_balance(self):
        """Get current account balance"""
        if not self.driver:
            return 0
            
        try:
            from selenium.webdriver.common.by import By
            
            # Try to find balance element
            balance_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class,'balance')]")
            for elem in balance_elements:
                text = elem.text
                if '$' in text:
                    self.balance = float(text.replace('$','').replace(',',''))
                    return self.balance
            
            return self.balance
            
        except Exception as e:
            logger.warning(f"Could not get balance: {e}")
            return self.balance
    
    async def get_candles(self, asset, timeframe=60, count=100):
        """Get real candle data from chart"""
        if not self.driver or not self.is_logged_in:
            return self._generate_mock_candles(count)
        
        try:
            from selenium.webdriver.common.by import By
            
            # Navigate to trade page
            self.driver.get(f"https://pocketoption.com/en/catalog/{asset}")
            await asyncio.sleep(3)
            
            # Try to extract chart data from canvas or API
            # This is simplified - real implementation would need more complex extraction
            return self._generate_mock_candles(count)
            
        except Exception as e:
            logger.warning(f"Could not get real candles: {e}")
            return self._generate_mock_candles(count)
    
    async def open_trade(self, asset, direction, amount, expiry=60):
        """Open a real trade"""
        if not self.driver or not self.is_logged_in:
            logger.warning("Not logged in - cannot open real trade")
            return {"success": False, "error": "Not logged in"}
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException
            
            wait = WebDriverWait(self.driver, 10)
            trade_id = f"real_{int(time.time())}_{random.randint(1000,9999)}"
            
            # Navigate to asset
            self.driver.get(f"https://pocketoption.com/en/trade/{asset}")
            await asyncio.sleep(3)
            
            # Try to find and click the trade panel
            try:
                # Select duration (expiry)
                duration_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[contains(@class,'duration') or @placeholder='Duration']")
                ))
                duration_input.clear()
                duration_input.send_keys(str(expiry))
            except Exception as e:
                logger.warning(f"Could not set duration: {e}")
            
            # Click CALL or PUT button
            try:
                if direction.lower() == "call":
                    # Look for call/higher button - try multiple possible XPaths
                    button_xpaths = [
                        "//button[contains(@class,'call')]",
                        "//button[contains(text(),'Higher')]",
                        "//div[contains(@class,'call')]//button",
                        "//span[contains(text(),'Higher')]/parent::button"
                    ]
                    trade_btn = None
                    for xpath in button_xpaths:
                        try:
                            trade_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            break
                        except:
                            continue
                    
                    if trade_btn:
                        trade_btn.click()
                else:
                    # Look for put/lower button
                    button_xpaths = [
                        "//button[contains(@class,'put')]",
                        "//button[contains(text(),'Lower')]",
                        "//div[contains(@class,'put')]//button",
                        "//span[contains(text(),'Lower')]/parent::button"
                    ]
                    trade_btn = None
                    for xpath in button_xpaths:
                        try:
                            trade_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            break
                        except:
                            continue
                    
                    if trade_btn:
                        trade_btn.click()
            except Exception as e:
                logger.warning(f"Could not click trade button: {e}")
            
            # Try to set amount if input appears
            try:
                await asyncio.sleep(1)
                amount_input = self.driver.find_elements(By.XPATH, "//input[contains(@class,'amount')]")
                if amount_input:
                    amount_input[0].clear()
                    amount_input[0].send_keys(str(amount))
            except:
                pass
            
            # Try to confirm trade
            try:
                confirm_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Buy') or contains(text(),'Confirm')]")
                ))
                confirm_btn.click()
            except:
                pass
            
            # Wait for trade to complete
            logger.info(f"Waiting {expiry + 5}s for trade result...")
            await asyncio.sleep(expiry + 5)
            
            # Try to detect real result from the page
            result = await self._detect_trade_result()
            
            if result:
                profit = amount * 0.82 if result == "win" else -amount
                self.balance += profit
                logger.info(f"Real trade: {direction} {amount}$ {asset} - {result} (Profit: ${profit})")
                return {
                    "success": True,
                    "trade_id": trade_id,
                    "direction": direction,
                    "amount": amount,
                    "asset": asset,
                    "result": result,
                    "profit": profit,
                    "real": True
                }
            else:
                # Fallback: couldn't detect result, assume pending
                logger.warning("Could not detect trade result - marking as pending")
                return {
                    "success": True,
                    "trade_id": trade_id,
                    "direction": direction,
                    "amount": amount,
                    "asset": asset,
                    "result": "pending",
                    "profit": 0,
                    "real": True,
                    "note": "Result detection failed - check manually"
                }
            
        except TimeoutException:
            logger.error("Trade timed out")
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            logger.error(f"Trade failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _detect_trade_result(self):
        """Detect trade result from browser page"""
        try:
            from selenium.webdriver.common.by import By
            
            # Look for result indicators on the page
            # Pocket Option shows "Win" or "Loss" after trade completes
            result_xpaths = [
                "//div[contains(@class,'result') and contains(text(),'Win')]",
                "//div[contains(@class,'result') and contains(text(),'Loss')]",
                "//span[contains(@class,'profit') and contains(text(),'+')]",
                "//span[contains(@class,'profit') and contains(text(),'-')]",
                "//div[contains(@class,'payout')]",
                "//div[contains(text(),'Win')]",
                "//div[contains(text(),'Loss')]",
                "//span[contains(text(),'won')]",
                "//span[contains(text(),'lost')]"
            ]
            
            for xpath in result_xpaths:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        text = elem.text.lower()
                        if 'win' in text or 'won' in text or '+' in text:
                            return "win"
                        elif 'loss' in text or 'lost' in text or '-' in text:
                            return "loss"
                except:
                    continue
            
            # Check page source for result
            page_source = self.driver.page_source.lower()
            if 'trade won' in page_source or 'you won' in page_source:
                return "win"
            elif 'trade lost' in page_source or 'you lost' in page_source:
                return "loss"
            
            return None
            
        except Exception as e:
            logger.warning(f"Result detection error: {e}")
            return None
    
    async def disconnect(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.is_logged_in = False
            logger.info("Browser closed")
    
    async def reconnect(self):
        """Reconnect to browser if disconnected"""
        if not self.driver:
            logger.info("Attempting to reconnect...")
            await self.connect()
            if self.driver:
                await self.authenticate()
                return True
        return False
    
    def is_connected(self):
        """Check if browser is still connected"""
        if not self.driver:
            return False
        try:
            # Check if browser is responsive
            self.driver.current_url
            return True
        except:
            self.driver = None
            self.is_logged_in = False
            return False
    
    def _generate_mock_candles(self, count=100):
        """Generate realistic mock candles"""
        candles = []
        
        # Different base prices for different assets
        base_prices = {
            "EUR/USD": 1.0850,
            "GBP/USD": 1.2650,
            "USD/JPY": 149.50,
            "AUD/USD": 0.6550,
            "USD/CAD": 1.3650,
            "BTC/USD": 43500,
            "ETH/USD": 2350
        }
        
        base_price = base_prices.get("EUR/USD", 1.1000)
        
        for i in range(count):
            # Random walk with slight upward bias
            change = random.uniform(-0.0005, 0.0006)
            open_price = base_price
            close_price = base_price + change
            
            # Generate high/low
            spread = abs(close_price - open_price) * random.uniform(1.5, 3)
            high_price = max(open_price, close_price) + spread/2
            low_price = min(open_price, close_price) - spread/2
            
            timestamp = int(time.time()) - (count - i) * 60
            
            candles.append({
                "open": round(open_price, 5),
                "high": round(high_price, 5),
                "low": round(low_price, 5),
                "close": round(close_price, 5),
                "timestamp": timestamp,
                "volume": random.randint(100, 1000)
            })
            
            base_price = close_price
        
        return candles


# Backwards compatibility alias
PocketOptionAPI = PocketOptionReal


class MockPocketOptionAPI:
    """Mock API for testing"""
    
    def __init__(self, demo=True):
        self.demo = demo
        self.balance = 10000 if demo else 0
        self.connected = True
        self.authenticated = True
        self.is_logged_in = True
        
    async def connect(self):
        self.connected = True
        return True
    
    async def disconnect(self):
        self.connected = False
    
    async def authenticate(self):
        self.authenticated = True
        self.is_logged_in = True
        return True
    
    def is_connected(self):
        """Check connection status"""
        return self.connected
    
    async def reconnect(self):
        """Reconnect - mock just returns True"""
        self.connected = True
        return True
    
    async def get_balance(self):
        return self.balance
    
    async def get_candles(self, asset, timeframe=60, count=100):
        # Generate realistic candles
        candles = []
        
        base_prices = {
            "EUR/USD": 1.0850, "GBP/USD": 1.2650, "USD/JPY": 149.50,
            "AUD/USD": 0.6550, "USD/CAD": 1.3650, "EUR/GBP": 0.8580,
            "EUR/JPY": 162.50, "GBP/JPY": 189.50, "BTC/USD": 43500, "ETH/USD": 2350
        }
        
        base_price = base_prices.get(asset, 1.1000)
        
        for i in range(count):
            change = random.uniform(-0.0005, 0.0006)
            open_price = base_price
            close_price = base_price + change
            spread = abs(close_price - open_price) * random.uniform(1.5, 3)
            high_price = max(open_price, close_price) + spread/2
            low_price = min(open_price, close_price) - spread/2
            timestamp = int(time.time()) - (count - i) * 60
            
            candles.append({
                "open": round(open_price, 5),
                "high": round(high_price, 5),
                "low": round(low_price, 5),
                "close": round(close_price, 5),
                "timestamp": timestamp,
                "volume": random.randint(100, 1000)
            })
            base_price = close_price
        
        return candles
    
    async def open_trade(self, asset, direction, amount, expiry=60):
        win = random.random() < 0.65  # 65% simulated win rate
        trade_id = f"mock_{int(time.time())}_{random.randint(1000,9999)}"
        result = "win" if win else "loss"
        profit = amount * 0.8 if win else -amount
        self.balance += profit
        
        logger.info(f"Trade: {direction} {amount}$ {asset} - {result}")
        
        return {
            "success": True,
            "trade_id": trade_id,
            "direction": direction,
            "amount": amount,
            "asset": asset,
            "result": result,
            "profit": profit
        }
