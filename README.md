# Currency Exchange Rate Telegram Bot

This Telegram bot allows users to fetch and analyze currency exchange rates. It provides functionality to get current rates, historical data, and visualize exchange rate trends.

## Features

- Fetch current exchange rates
- Load historical exchange rate data for specific date ranges
- Visualize exchange rate trends with graphs
- Store data in PostgreSQL database
- User message tracking and management
- Interactive progress visualization for long operations

## Getting API Keys

### Telegram Bot Token (BotFather)
1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather and send `/newbot`
3. Follow the instructions:
   - Provide a name for your bot
   - Provide a username for your bot (must end in 'bot')
4. BotFather will give you a token. It looks like this: `123456789:ABCdefGHIjklmNOPQrstUVwxyz`
5. Copy this token and save it as `BOT_TOKEN` in your `.env` file

### OpenExchangeRates API Key
1. Go to [OpenExchangeRates](https://openexchangerates.org/)
2. Click "Sign Up" and create a free account
3. After registration, go to your account dashboard
4. Find your API key under "App IDs"
5. Copy the API key and save it as `API_KEY` in your `.env` file

Note: The free plan has some limitations:
- Updates every hour
- USD as base currency only
- Limited number of requests per month
- Historical data access may be restricted

## Installation with Docker

1. Clone the repository:
```bash
git clone https://github.com/Marinazuzum/Telegram-Bot-Currency-Analysis.git
cd Telegram-Bot-Currency-Analysis
```

2. Create a `.env` file in the project root directory with the required environment variables

```bash
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
API_KEY=your_openexchangerates_api_key

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/dbname
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=telegram_bot_db

# PGAdmin Configuration
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin
```

3. Build and run the containers:
```bash
docker-compose up -d
```

This will start three containers:
- `telegram-bot`: The main bot application
- `postgres-db`: PostgreSQL database
- `pgadmin`: Web interface for database management

## Bot Commands

### Basic Commands

- `/start` - Initialize bot interaction
- `/get_rates` - Fetch current exchange rates
  ```
  Example: /get_rates
  ```

### Historical Data Commands

- `/get_historical_rates [start_date] [end_date]` - Fetch historical exchange rates for a date range
  ```
  Example: /get_historical_rates 2024-01-01 2024-01-31
  ```
  The command shows a progress bar with animation while loading data.

### Visualization Commands

- `/plot [currency]` - Generate a graph showing exchange rate trends for a specific currency
  ```
  Example: /plot EUR
  ```
  Returns a graph showing the exchange rate trend for the specified currency against USD.

### Message Management Commands

- `/return_all_messages` - Display all messages sent by the current user
- `/delete_all_messages` - Delete all messages from the current user
- `/update_all_messages` - Update all messages from the current user (adds ')' to the end)

## Database Access

PGAdmin is available at `http://localhost:5050` for database management. Use the credentials specified in your `.env` file to log in.

## Notes

- The bot uses the OpenExchangeRates API for currency data
- All exchange rates are relative to USD
- Historical data requests are limited by the API's rate limits
- The database automatically handles data deduplication
