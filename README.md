# NOX-X Professional Trading System

A professional AI-powered trading system integrated with MetaTrader 5, featuring real-time market analysis, automated trading, and continuous learning capabilities.

## Features

- 🤖 Advanced AI Trading System
  - LSTM-based deep learning model
  - Continuous online learning
  - Multi-factor signal generation
  - Automated pattern recognition

- 📊 Professional Trading Interface
  - Real-time price charts
  - Technical indicators
  - Trade management
  - Performance analytics

- 🔗 MetaTrader 5 Integration
  - Real account trading
  - Real-time market data
  - Automated order execution
  - Account management

- 📈 Technical Analysis
  - Multiple indicators (RSI, MACD, Bollinger Bands, etc.)
  - Pattern detection
  - Support/Resistance analysis
  - Trend analysis

- 📱 Risk Management
  - Position sizing
  - Stop-loss automation
  - Risk/reward analysis
  - Portfolio management

- 📊 Performance Tracking
  - Trade history
  - Performance metrics
  - AI model performance
  - System logs

## Requirements

- Python 3.8+
- MetaTrader 5 platform with real account
- Windows OS (MT5 requirement)
- Minimum 8GB RAM recommended
- Internet connection

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nox-x.git
cd nox-x
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure MetaTrader 5:
- Install MetaTrader 5
- Create/Login to your real trading account
- Enable automated trading
- Enable DLL imports

5. Configure the system:
- Copy `config.example.json` to `config.json`
- Update MT5 credentials in `config.json`
- Adjust trading parameters as needed

## Configuration

Edit `config.json` to customize the system:

```json
{
    "mt5": {
        "login": "YOUR_LOGIN",
        "password": "YOUR_PASSWORD",
        "server": "YOUR_SERVER"
    },
    "trading": {
        "allowed_symbols": ["EURUSD", "GBPUSD", "USDJPY"],
        "default_volume": 0.1,
        "max_positions": 5
    },
    "ai": {
        "model_type": "LSTM",
        "learning_rate": 0.001
    }
}
```

## Usage

1. Start the system:
```bash
python app/main.py
```

2. Using the Interface:
- Select trading pair and timeframe
- Enable/disable auto-trading
- Monitor signals and positions
- Track performance metrics

3. Managing Trades:
- System automatically analyzes market
- Generates trading signals
- Executes trades when auto-trading is enabled
- Manages positions with predefined risk parameters

4. Monitoring Performance:
- View real-time statistics
- Check trade history
- Monitor AI performance
- Review system logs

## Safety Features

- Real account verification
- Risk management controls
- Stop-loss protection
- Error handling and logging
- Automatic backup system

## Project Structure

```
nox-x/
├── app/
│   ├── main.py           # Main application
│   ├── gui.py            # User interface
│   ├── mt5_connector.py  # MT5 integration
│   ├── ai_model.py       # AI/ML components
│   ├── indicators.py     # Technical indicators
│   ├── signal_logic.py   # Signal generation
│   ├── database.py       # Data management
│   └── logs.py          # Logging system
├── models/              # Trained AI models
├── data/               # Market data
├── logs/               # System logs
├── requirements.txt    # Dependencies
├── config.json        # Configuration
└── README.md          # Documentation
```

## Important Notes

1. **Real Trading**
   - System is designed for real account trading
   - Paper trading/demo accounts are not supported
   - Use appropriate risk management

2. **Risk Warning**
   - Trading involves substantial risk
   - Past performance doesn't guarantee future results
   - Only trade with risk capital

3. **System Requirements**
   - Stable internet connection required
   - Adequate system resources needed
   - Regular maintenance recommended

## Troubleshooting

1. Connection Issues:
   - Verify MT5 is running
   - Check internet connection
   - Confirm credentials in config.json

2. Trading Issues:
   - Verify account has sufficient funds
   - Check symbol is available for trading
   - Confirm auto-trading is enabled

3. Performance Issues:
   - Close unnecessary applications
   - Check system resources
   - Verify database isn't too large

## Support

For issues and support:
1. Check troubleshooting guide
2. Review system logs
3. Contact support team

## License

This project is proprietary software. All rights reserved.

## Disclaimer

This software is for professional trading purposes. Trading involves significant risk of loss and is not suitable for all investors. Past performance is not indicative of future results.
