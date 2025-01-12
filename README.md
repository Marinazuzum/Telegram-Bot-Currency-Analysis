# Currency Exchange Rate Telegram Bot

This Telegram bot allows users to fetch and analyze currency exchange rates. It provides functionality to get current rates, historical data, and visualize exchange rate trends.

## Features

- Fetch current exchange rates
- Load historical exchange rate data for specific date ranges
- Visualize exchange rate trends with graphs
- Store data in PostgreSQL database
- User message tracking and management
- Interactive progress visualization for long operations

## Installation with Docker

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-directory]
```

2. Create a `.env` file in the project root directory with the required environment variables (see Environment Variables section).

3. Build and run the containers:
```bash
docker-compose up -d
```

This will start three containers:
- `telegram-bot`: The main bot application
- `postgres-db`: PostgreSQL database
- `pgadmin`: Web interface for database management

## Environment Variables

Create a `.env` file with the following variables:

```plaintext
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
API_KEY=your_openexchangerates_api_key

# Database Configuration
DATABASE_URL=postgresql://user:password@db:5432/dbname
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name

# PGAdmin Configuration
PGADMIN_DEFAULT_EMAIL=your_email@domain.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
```

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
