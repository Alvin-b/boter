"""
Configuration UI for Pocket Option Trading Bot
Run this to configure the bot via web interface
"""
from flask import Flask, render_template_string, request, redirect, url_for
import json
import os

app = Flask(__name__)
CONFIG_FILE = 'bot_config.json'

# Default configuration
DEFAULT_CONFIG = {
    # Login Mode
    "demo": True,
    "USE_BROWSER_LOGIN": True,
    "POCKET_OPTION_EMAIL": "",
    "POCKET_OPTION_PASSWORD": "",
    
    # Trading Settings
    "TRADING_AMOUNT": 10,
    "DEFAULT_ASSET": "EUR/USD",
    "TRADE_EXPIRY": 60,
    
    # Money Management
    "MARTINGALE_ENABLED": True,
    "MARTINGALE_MULTIPLIER": 2.0,
    "MAX_MARTINGALE_STEPS": 3,
    
    # Risk Management
    "MAX_DAILY_LOSS": 100,
    "MAX_TRADES_PER_DAY": 50,
    "MIN_WIN_RATE": 0.6,
    
    # Signal Settings
    "MIN_SIGNAL_STRENGTH": 0.7,
    "SIGNAL_CHECK_INTERVAL": 10,
    
    # Assets
    "AVAILABLE_ASSETS": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "BTC/USD", "ETH/USD"]
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Pocket Option Bot - Configuration</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { 
            color: #00d4ff; 
            text-align: center; 
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle { 
            text-align: center; 
            color: #888; 
            margin-bottom: 30px;
        }
        .card {
            background: #1e1e2f;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .card h2 {
            color: #00d4ff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }
        .form-group { margin-bottom: 15px; }
        label {
            display: block;
            color: #ccc;
            margin-bottom: 5px;
            font-weight: 500;
        }
        input[type="text"], input[type="number"], input[type="password"], select {
            width: 100%;
            padding: 12px;
            border: 1px solid #333;
            border-radius: 8px;
            background: #2a2a3e;
            color: #fff;
            font-size: 14px;
        }
        input:focus { outline: none; border-color: #00d4ff; }
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        input[type="checkbox"] {
            width: 20px;
            height: 20px;
            accent-color: #00d4ff;
        }
        .assets-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        .asset-checkbox {
            background: #2a2a3e;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .asset-checkbox:hover { background: #3a3a4e; }
        .asset-checkbox.selected { 
            background: #00d4ff; 
            color: #000;
        }
        .btn {
            padding: 15px 40px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #000;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0,212,255,0.4); }
        .btn-secondary {
            background: #333;
            color: #fff;
        }
        .btn-danger {
            background: #ff4757;
            color: #fff;
        }
        .buttons { text-align: center; margin-top: 20px; }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-success { background: #2ed573; color: #000; }
        .status-bar {
            background: #0f0f1a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background: #2ed573; }
        .demo-badge {
            background: #ffa502;
            color: #000;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Pocket Option Trading Bot</h1>
        <p class="subtitle">Configuration Panel</p>
        
        {% if saved %}
        <div class="alert alert-success">✅ Configuration saved successfully!</div>
        {% endif %}
        
        <form method="POST">
            <!-- Status Bar -->
            <div class="status-bar">
                <div>
                    <span class="status-indicator {% if config.demo %}status-active{% endif %}"></span>
                    <span>Mode: <strong>{% if config.demo %}DEMO{% else %}REAL TRADING{% endif %}</strong></span>
                    {% if config.demo %}
                    <span class="demo-badge">SIMULATION</span>
                    {% endif %}
                </div>
            </div>
            
            <!-- Login Settings -->
            <div class="card">
                <h2>🔐 Login Settings</h2>
                <div class="form-group checkbox-group">
                    <input type="checkbox" id="demo" name="demo" {% if config.demo %}checked{% endif %}>
                    <label for="demo">Use Demo Account (Uncheck for Real Trading with real money)</label>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="text" name="POCKET_OPTION_EMAIL" value="{{ config.POCKET_OPTION_EMAIL }}" placeholder="your@email.com">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="POCKET_OPTION_PASSWORD" value="{{ config.POCKET_OPTION_PASSWORD }}" placeholder="Your password">
                </div>
            
            <!-- Trading Settings -->
            <div class="card">
                <h2>💰 Trading Settings</h2>
                <div class="form-group">
                    <label>Trading Amount ($)</label>
                    <input type="number" name="TRADING_AMOUNT" value="{{ config.TRADING_AMOUNT }}" min="1">
                </div>
                <div class="form-group">
                    <label>Default Asset</label>
                    <select name="DEFAULT_ASSET">
                        {% for asset in assets %}
                        <option value="{{ asset }}" {% if config.DEFAULT_ASSET == asset %}selected{% endif %}>{{ asset }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>Trade Expiry (seconds)</label>
                    <input type="number" name="TRADE_EXPIRY" value="{{ config.TRADE_EXPIRY }}" min="30">
                </div>
            
            <!-- Risk Management -->
            <div class="card">
                <h2>⚠️ Risk Management</h2>
                <div class="form-group">
                    <label>Max Daily Loss ($)</label>
                    <input type="number" name="MAX_DAILY_LOSS" value="{{ config.MAX_DAILY_LOSS }}" min="10">
                </div>
                <div class="form-group">
                    <label>Max Trades Per Day</label>
                    <input type="number" name="MAX_TRADES_PER_DAY" value="{{ config.MAX_TRADES_PER_DAY }}" min="1">
                </div>
                <div class="form-group">
                    <label>Min Win Rate (%)</label>
                    <input type="number" name="MIN_WIN_RATE" value="{{ config.MIN_WIN_RATE }}" min="0.1" max="1.0" step="0.1">
                </div>
            
            <!-- Martingale -->
            <div class="card">
                <h2>📈 Martingale Strategy</h2>
                <div class="form-group checkbox-group">
                    <input type="checkbox" id="MARTINGALE_ENABLED" name="MARTINGALE_ENABLED" {% if config.MARTINGALE_ENABLED %}checked{% endif %}>
                    <label for="MARTINGALE_ENABLED">Enable Martingale</label>
                </div>
                <div class="form-group">
                    <label>Multiplier</label>
                    <input type="number" name="MARTINGALE_MULTIPLIER" value="{{ config.MARTINGALE_MULTIPLIER }}" min="1.5" max="3.0" step="0.1">
                </div>
                <div class="form-group">
                    <label>Max Steps</label>
                    <input type="number" name="MAX_MARTINGALE_STEPS" value="{{ config.MAX_MARTINGALE_STEPS }}" min="1" max="5">
                </div>
            
            <!-- Assets -->
            <div class="card">
                <h2>📊 Trading Assets</h2>
                <div class="assets-grid">
                    {% for asset in all_assets %}
                    <div class="asset-checkbox {% if asset in config.AVAILABLE_ASSETS %}selected{% endif %}" onclick="toggleAsset('{{ asset }}')">
                        <input type="checkbox" name="AVAILABLE_ASSETS" value="{{ asset }}" {% if asset in config.AVAILABLE_ASSETS %}checked{% endif %} style="display:none;">
                        {{ asset }}
                    </div>
                    {% endfor %}
                </div>
            
            <!-- Signal Settings -->
            <div class="card">
                <h2>🎯 Signal Settings</h2>
                <div class="form-group">
                    <label>Min Signal Strength (0.1 - 1.0)</label>
                    <input type="number" name="MIN_SIGNAL_STRENGTH" value="{{ config.MIN_SIGNAL_STRENGTH }}" min="0.1" max="1.0" step="0.1">
                </div>
                <div class="form-group">
                    <label>Check Interval (seconds)</label>
                    <input type="number" name="SIGNAL_CHECK_INTERVAL" value="{{ config.SIGNAL_CHECK_INTERVAL }}" min="1">
                </div>
            
            <div class="buttons">
                <button type="submit" class="btn btn-primary">💾 Save Configuration</button>
                <a href="/start" class="btn btn-secondary">▶️ Start Bot</a>
            </div>
        </form>
    </div>
    
    <script>
    function toggleAsset(asset) {
        const checkbox = event.currentTarget.querySelector('input[type="checkbox"]');
        checkbox.checked = !checkbox.checked;
        event.currentTarget.classList.toggle('selected', checkbox.checked);
    }
    </script>
</body>
</html>
'''

def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file (with key names matching main.py)"""
    # Map GUI field names to main.py expected names
    mapped_config = {
        'demo': config.get('DEMO_MODE', True),
        'email': config.get('POCKET_OPTION_EMAIL', ''),
        'password': config.get('POCKET_OPTION_PASSWORD', ''),
        'browser_auth': config.get('USE_BROWSER_LOGIN', True),
        'asset': config.get('DEFAULT_ASSET', 'EUR/USD'),
        'amount': int(config.get('TRADING_AMOUNT', 10)),
        'expiry': int(config.get('TRADE_EXPIRY', 60)),
        'max_daily_loss': int(config.get('MAX_DAILY_LOSS', 100)),
        'max_trades_per_day': int(config.get('MAX_TRADES_PER_DAY', 50)),
        'min_win_rate': float(config.get('MIN_WIN_RATE', 0.6)),
        'signal_check_interval': int(config.get('SIGNAL_CHECK_INTERVAL', 10)),
        'martingale_enabled': config.get('MARTINGALE_ENABLED', True),
        'martingale_multiplier': float(config.get('MARTINGALE_MULTIPLIER', 2.0)),
        'max_martingale_steps': int(config.get('MAX_MARTINGALE_STEPS', 3)),
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(mapped_config, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    config = load_config()
    all_assets = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "EUR/JPY", "GBP/JPY", "BTC/USD", "ETH/USD"]
    
    if request.method == 'POST':
        # Update config from form - use 'demo' key consistently
        config['demo'] = 'demo' in request.form
        config['USE_BROWSER_LOGIN'] = 'USE_BROWSER_LOGIN' in request.form
        config['POCKET_OPTION_EMAIL'] = request.form.get('POCKET_OPTION_EMAIL', '')
        config['POCKET_OPTION_PASSWORD'] = request.form.get('POCKET_OPTION_PASSWORD', '')
        config['TRADING_AMOUNT'] = int(request.form.get('TRADING_AMOUNT', 10))
        config['DEFAULT_ASSET'] = request.form.get('DEFAULT_ASSET', 'EUR/USD')
        config['TRADE_EXPIRY'] = int(request.form.get('TRADE_EXPIRY', 60))
        config['MARTINGALE_ENABLED'] = 'MARTINGALE_ENABLED' in request.form
        config['MARTINGALE_MULTIPLIER'] = float(request.form.get('MARTINGALE_MULTIPLIER', 2.0))
        config['MAX_MARTINGALE_STEPS'] = int(request.form.get('MAX_MARTINGALE_STEPS', 3))
        config['MAX_DAILY_LOSS'] = int(request.form.get('MAX_DAILY_LOSS', 100))
        config['MAX_TRADES_PER_DAY'] = int(request.form.get('MAX_TRADES_PER_DAY', 50))
        config['MIN_WIN_RATE'] = float(request.form.get('MIN_WIN_RATE', 0.6))
        config['MIN_SIGNAL_STRENGTH'] = float(request.form.get('MIN_SIGNAL_STRENGTH', 0.7))
        config['SIGNAL_CHECK_INTERVAL'] = int(request.form.get('SIGNAL_CHECK_INTERVAL', 10))
        config['AVAILABLE_ASSETS'] = request.form.getlist('AVAILABLE_ASSETS')
        
        save_config(config)
        return render_template_string(HTML_TEMPLATE, config=config, assets=all_assets, all_assets=all_assets, saved=True)
    
    return render_template_string(HTML_TEMPLATE, config=config, assets=all_assets, all_assets=all_assets, saved=False)

@app.route('/start')
def start():
    """Start the trading bot"""
    return redirect('/')

if __name__ == '__main__':
    print("=" * 50)
    print("🎛️  Pocket Option Bot - Configuration UI")
    print("=" * 50)
    print("Open your browser and go to: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
