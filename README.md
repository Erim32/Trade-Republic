![Trade Republic SDK banner](docs/banner.png)

# Trade Republic Python SDK

Unofficial Python SDK for Trade Republic API - provides comprehensive functionality for account management, portfolio tracking, order placement, and market data retrieval.

## Features

- 🔐 Authentication and session management
- 📊 Portfolio tracking and performance analysis
- 💼 Account information and balance queries
- 📈 Market data and price information
- 🔍 Instrument search and details
- 📝 Order placement and management
- 🔔 Alert management
- 💸 Transaction history
- 💰 Savings plans management

## Installation

```bash
pip install trade-republic
```

## Authentication

To use the Trade Republic API, you need to authenticate with your phone number and PIN. The client will handle the authentication automatically:

```python
from trade_republic import TRClient

# Initialize the client with your credentials
async with TRClient(phone="+49...", pin="1234") as client:
    # Your code here
    portfolio = await client.portfolio_service.fetch_portfolio(client)
```

If no credentials are supplied during initialization, the library will look for them in environment variables:

- `TR_PHONE`: Your Trade Republic phone number
- `TR_PIN`: Your Trade Republic PIN

The client uses async/await for all API calls and should be used with `async with` context manager to ensure proper cleanup.

## Quick Start

```python
import asyncio
from trade_republic import TRClient

async def main():
    # Initialize the client
    async with TRClient(phone="+49...", pin="1234") as client:
        # Get portfolio information
        portfolio_service = client.portfolio_service
        portfolio = await portfolio_service.fetch_portfolio(client)

        # Display portfolio data
        client.display_json(portfolio)

        # Get account information
        account_service = client.account_service
        accounts = await account_service.fetch_accounts()
        print(f"You have {len(accounts)} account(s)")

asyncio.run(main())
```

## Services Overview

The `TRClient` provides access to multiple services, each specializing in different areas of the Trade Republic API:

```python
# Access individual services through the client
client.account_service           # Account and cash management
client.portfolio_service         # Portfolio tracking
client.market_data_service       # Market data and watchlist
client.instrument_service        # Instrument information
client.order_service             # Order and savings plan management
client.search_service            # Instrument search
client.alert_service             # Price alerts
client.transaction_service       # Transaction and timeline history
client.experience_service        # User experience settings
```

## All Available Methods

### Account Service

Manage account information and cash/balance queries.

```python
account_service = client.account_service

# Fetch account information
await account_service.fetch_accounts()

# Fetch and extract available cash
data, amount, currency = await account_service.fetch_available_cash()

# Fetch cash information
await account_service.fetch_cash()

# Fetch available cash for withdrawal/payout
await account_service.fetch_available_cash_for_payout()

# Fetch portfolio by account
await account_service.fetch_portfolio_by_account(securities_account_number)

# Get detailed account information with portfolio and instruments (advanced)
await account_service.fetch_accounts_details(client)
```

### Portfolio Service

Track portfolio positions, history, and performance.

```python
portfolio_service = client.portfolio_service

# Fetch complete portfolio with all accounts
await portfolio_service.fetch_portfolio(client)

# Fetch portfolio positions with optional formatting
positions = await portfolio_service.fetch_portfolio_positions(
    client,
    french_classification=False,
    add_cash=True
)

# Fetch portfolio status
await portfolio_service.fetch_portfolio_status()

# Fetch portfolio history for a specific timeframe
await portfolio_service.fetch_portfolio_history(timeframe="1y")

# Fetch performance data for a specific instrument
await portfolio_service.fetch_performance(isin, exchange="LSX")
```

### Market Data Service

Access real-time and historical market data.

```python
market_data_service = client.market_data_service

# Fetch ticker information (real-time prices)
await market_data_service.fetch_ticker(isin="DE0005933931", exchange="LSX")

# Fetch last price for an instrument
await market_data_service.fetch_last_price(isin, exchange=None)

# Fetch watchlist
await market_data_service.fetch_watchlist()

# Add instrument to watchlist
await market_data_service.add_to_watchlist(isin)

# Remove instrument from watchlist
await market_data_service.remove_from_watchlist(isin)
```

### Instrument Service

Get detailed information about financial instruments.

```python
instrument_service = client.instrument_service

# Fetch complete instrument information
await instrument_service.fetch_instrument(isin)

# Fetch all instruments of a specific type
await instrument_service.fetch_instruments_by_type(instrument_type="stock")

# Fetch all available instruments (all types)
await instrument_service.fetch_instruments()
```

Valid instrument types: `"stock"`, `"fund"`, `"derivate"`, `"crypto"`, `"bond"`, `"mutualFund"`, `"privateFund"`

### Order Service

Place, manage, and cancel orders, as well as manage savings plans.

#### Orders

Be careful, these methods can create actual live trades.

```python
order_service = client.order_service

# Fetch all active orders
await order_service.fetch_orders()

# Create a market order
await order_service.create_market_order(
    isin="DE0005933931",
    exchange="LSX",
    order_type="buy",              # "buy" or "sell"
    size=10,                       # Number of shares
    expiry="gfd",                  # "gfd", "gtd", or "gtc"
    sell_fractions=False
)

# Create a limit order
await order_service.create_limit_order(
    isin="DE0005933931",
    exchange="LSX",
    order_type="buy",
    size=10,
    limit=100.50,                  # Limit price
    expiry="gfd"
)

# Create a stop-market order
await order_service.create_stop_market_order(
    isin="DE0005933931",
    exchange="LSX",
    order_type="sell",
    size=10,
    stop=95.00,                    # Stop price
    expiry="gtc"
)

# Cancel an order
await order_service.cancel_order(order_id)
```

#### Savings Plans

```python
# Fetch all savings plans
await order_service.fetch_savings_plans()

# Create a savings plan
await order_service.create_savings_plan(
    isin="DE0005933931",
    amount=100,                    # Amount in EUR
    interval="monthly",            # "weekly", "monthly", "quarterly", "yearly"
    start_date="2024-02-01",
    start_date_type="dayOfMonth",  # "dayOfMonth" or "weekday"
    start_date_value=1             # Day of month (0-30) or weekday (0-6)
)

# Get savings plan parameters
await order_service.get_savings_plan_parameters(isin)

# Change a savings plan
await order_service.change_savings_plan(
    savings_plan_id,
    isin,
    amount,
    interval,
    start_date,
    start_date_type,
    start_date_value
)

# Cancel a savings plan
await order_service.cancel_savings_plan(savings_plan_id)
```

### Search Service

Search for instruments across the Trade Republic catalog.

```python
search_service = client.search_service

# Search for instruments by query
results = await search_service.search_instruments(
    query="Apple",
    asset_type="stock",            # "stock", "fund", "crypto", "derivative"
    page=1,
    page_size=20,
    aggregate=False,
    only_savable=False,
    filter_index=None,
    filter_country=None,
    filter_sector=None,
    filter_region=None
)

# Search instruments by country
await search_service.search_by_country(country_code)

# Search instruments by sector
await search_service.search_by_sector(sector_name)

# Get available search tags/filters
await search_service.get_search_tags()

# Get suggested tags for a search query
await search_service.get_suggested_tags(query="tech")
```

### Alert Service

Manage price alerts for instruments.

```python
alert_service = client.alert_service

# Fetch all price alerts
await alert_service.fetch_price_alarms()

# Create a price alert
await alert_service.create_price_alert(
    isin="DE0005933931",
    price=105.50                   # Alert triggers at this price
)

# Cancel a price alert
await alert_service.cancel_price_alert(price_alarm_id)
```

### Transaction Service

Access transaction history and timeline events.

```python
transaction_service = client.transaction_service

# Fetch all transactions
await transaction_service.fetch_transactions(extract_details=False)

# Fetch a specific transaction's details
await transaction_service.fetch_transaction(transaction_id)

# Fetch timeline events
await transaction_service.fetch_timeline(after=None)

# Fetch details of a specific timeline event
await transaction_service.fetch_timeline_detail(timeline_id)

# Fetch details of a specific order from timeline
await transaction_service.fetch_timeline_detail_order(order_id)

# Fetch details of a specific savings plan from timeline
await transaction_service.fetch_timeline_detail_savings_plan(savings_plan_id)
```

### Experience Service

Access user experience settings and messages.

```python
experience_service = client.experience_service

# Fetch user experience configuration
await experience_service.fetch_experience()

# Fetch message of the day
await experience_service.fetch_message_of_the_day()

# Fetch Neon cards (UI content)
await experience_service.fetch_neon_cards()
```

## Utility Methods

The `TRClient` provides convenient utility methods for working with JSON data:

```python
# Display data as formatted JSON
client.display_json(data)

# Save data to JSON file
client.save_json(data, filename="output.json")

# Load data from JSON file
data = client.load_json(filename="output.json")
```

## Common Parameters

- **isin** `string`: _International Securities Identification Number_ (e.g., "DE0005933931")
- **exchange** `string`: Stock exchange code, usually `"LSX"` for _Lang & Schwarz Exchange_
- **timeframe** `string`: Time period for historical data
  - Allowed values: `"1w"`, `"1m"`, `"3m"`, `"6m"`, `"1y"`, `"max"`
- **asset_type** `string`: Type of financial instrument
  - Allowed values: `"stock"`, `"fund"`, `"crypto"`, `"derivative"`
- **order_type** `string`: Direction of the order
  - Allowed values: `"buy"` or `"sell"`
- **size** `int`: Number of shares/units to trade
- **limit** `float`: Limit price for limit orders
- **stop** `float`: Stop price for stop-market orders
- **expiry** `string`: Order duration
  - Allowed values: `"gfd"` (good for day), `"gtd"` (good till date), `"gtc"` (good till cancelled)
- **expiry_date** `string` (optional): Expiration date for "gtd" orders (format: `"yyyy-mm-dd"`)
- **amount** `int`: Savings plan amount in EUR
- **interval** `string`: Savings plan execution frequency
  - Allowed values: `"weekly"`, `"twoPerMonth"`, `"monthly"`, `"quarterly"`, `"yearly"`
- **price** `float`: Target price for price alerts

## Error Handling

The SDK provides robust error handling with custom exceptions:

- `AuthenticationError`: Authentication and session-related failures
- `ValidationError`: Data validation errors (ISIN, exchange, order parameters)
- `APIError`: API communication and HTTP errors
- `DataError`: Data processing and transformation errors
- `ServiceError`: Service initialization and availability errors

## Examples

See the `examples/` directory for comprehensive usage examples including:

- Account management
- Portfolio tracking
- Order placement
- Market data retrieval
- Instrument search
- Advanced portfolio analysis

## Output Folder

By default, the client saves debug information and fetched data to an `output/` folder. You can customize this:

```python
client = TRClient(phone="+49...", pin="1234", output_folder="my_output")
```

## Requirements

- Python >=3.13
- Dependencies managed via pyproject.toml:
  - loguru
  - pandas
  - python-dotenv
  - requests
  - websockets

## License

MIT License - see LICENSE file for details

## Disclaimer

This is an unofficial SDK and is not affiliated with, endorsed by, or connected to Trade Republic Bank GmbH. Use at your own risk, especially when placing live orders.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
