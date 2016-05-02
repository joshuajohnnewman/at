# at

### Installation

- Make VirtualEnv by following instructions at: http://docs.python-guide.org/en/latest/dev/virtualenvs/
- Install MongoDB by following instructions for OSX: https://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/
- Install Requirements via pip install -r /path/to/requirements.txt
- Install Application by running python setup.py install
- Brew install ta-lib

### Running a Trading Strategy
- Get an Oanda Account ID, and API Token at: https://www.oanda.com/demo-account/login?intcmp=fxTradeAll_Site_TopNav_TradeDemoSignOutButton
- Start Mongod Process by running starting script: bash trading/scripts/start.sh
- Test out trading strategy by running script: python trading/scripts/josh_strategy.py


### API (Interactive Candlestick Chart Marking)
- Start Mongod Process by running starting script: bash trading/scripts/start.sh
- python scripts/make_dataset.py 2015 1 1 h 2000
- To inspect database run command mongodb
    - use $db
    - show tables
    - db.$table.findOne()
- Run python -m trading.application
- Open index.html in client application at: https://github.com/joshtrades/atc
- Follow instructions for starting client application at: https://github.com/joshtrades/atc/readme.MD