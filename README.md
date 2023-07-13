
# MyDP: My Data Provider
A minimal in-memory multi-exchange crypto data provider to feed trading algorithms/bots, built with Python and FastAPI.

You say what data you want (from which exchanges, symbols, timeframes, etc.) through the `config.json` file, and `MyDP` digest them for you. Then your algorithms/bots can consume the data via its `REST API` or `WebSocket`.

Here is a small example of the `config.json` file:

	[
        {
            "exchange": "binance_spot",
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "aliases": [
                        "WBTC-USDC",
                        "WBTC-DAI",
                        "WBTC-USDT"
                    ],
                    "timeframes": [
                        "1d",
                        "4h",
                        "5m"
                    ]
                }
            ]
        },
        {
            "exchange": "kucoin_spot",
            "symbols": [
                {
                    "symbol": "ETH-USDT",
                    "aliases": [
                        "WETH-USDC",
                        "WETH-DAI",
                        "WETH-USDT"
                    ],
                    "timeframes": [
                        "1day",
                        "4hour",
                        "5min"
                    ]
                }
            ]
        },
        ... 
    ]


## Implemented Exchange proxies:

| Exchange    | Spot | Futures | Notes |
| ----------- | :----------------: | :----------------: | :--------------- |
| Binance     | :white_check_mark: | :white_check_mark: | USD-M and COIN-M |
| Bingx       |  |  |  |
| ByBit       |  |  |  |
| Coinex      | :white_check_mark: | :white_check_mark: |  |
| Kucoin      | :white_check_mark: |  |  |
| Mexc        | :white_check_mark: | :white_check_mark: |  |
| OKX         |  |  |  |


## Features

- Container based: Simply create a Dockerfile and run it.
- Extendable: You can fork and implement your own exchange proxies.
- Built-in `REST API` and `WebSocket`.
- Asynchronous and non-blocking.
- Ability to declare multiple `timeframes` for each symbol.
- Ability to declare arbitrary `aliases` for each symbol (then the client can fetch data with formal symbol name or any other configured `aliases`).

## How it functions?

- First, it fetches the latest `500` historical OHLCV data rows from the configured exchanges.
- Then it subscribes to their kline sockets and keeps the in-memory data up-to-date.
- It ONLY maintains the latest 500 candles in memory.
- It also pushes updates to its `WebSocket` clients.
- Then your bots/algos can get data via `REST API` or `WebSocket` and consume them.

## Installation

- Clone the repository.
- Edit the `config.json` file according to your needs.
- Create a docker image using the `Dockerfile`.
- Run the container.

## Usages

Data can be retrieved via `REST API` or `WebSocket`. There is one endpoint for each of them. 

### REST API

The endpoint route is as the following:

    @app.get("/candles/{exchange}/{symbol}/{timeframe}/{count}", response_class=JSONResponse)

Here is the description of path params:

- exchange: the enum `Value` of the desired exchange. Must be added to `config.json` file. (e.g. 'binance_spot', etc. You can find them in `src/base/enums.py` file.)
- symbol: it can be the `symbol` value declared in the `config.json` file or one of its `aliases`.
- timeframe: Must be one of the configured `timeframes` of the symbol.
- count: the number of the latest candles you want to retrieve. The valid range is 1-500.

Here is an example with cURL (based on the example config above):

    curl localhost:8000/candles/binance_spot/BTCUSDT/1d/2

Here is an example with Python and AIOHTTP:

    MYDP_HOST = '...'
    MYDP_PORT = '...'

    BASE_URL = 'http://{}:{}/'.format(MYDP_HOST, MYDP_PORT)
    CANDLES_ENDPOINT = BASE_URL + 'candles'

    async def get_candles(exchange: str, symbol: str, timeframe: str, count: int = 2):                 

        connector = aiohttp.TCPConnector(limit=None)
        async with aiohttp.ClientSession(connector=connector) as session:
        
            try:
                url = '{}/{}/{}/{}/{}'.format(CANDLES_ENDPOINT, exchange, symbol, timeframe, count)
                async with session.get(url) as resp:
                
                    r_json = await resp.json()     

                    df = pd.DataFrame(data=r_json['result'])                       
                    df['open_datetime'] = pd.to_datetime(df['open_datetime'], format='%Y-%m-%dT%H:%M:%S')
                    df = df.set_index('open_datetime')   
                    df['open'] = df['open'].astype('float')
                    df['high'] = df['high'].astype('float')
                    df['low'] = df['low'].astype('float')
                    df['close'] = df['close'].astype('float')
                    df['volume'] = df['volume'].astype('float')
                    
                    return df                     

            except Exception as ex:
                print('exception thrown: ', ex)
                return None
       

### WebSocket

The endpoint route is as the following:

    @app.websocket("/ws/{exchange}/{symbol}/{timeframe}")

So you can subscribe to each kline with something like the following url:

    ws://localhost:8000/ws/binance_spot/BTCUSDT/1d

Then, you'll receive real-time updates from the exchange via MyDP. The update messages are in the following format:

    {
        'open_timestamp': 'timestamp of the candle opening',
        'open_datetime': 'datetime represantation of the candle opening',
        'open': 'open price',
        'high': 'high price',
        'low': 'low price',
        'close': 'latest close price',
        'volume': 'latest volume'
    } 

Some notes regarding the usage of the `WebSocket`:

- The `aliases` feature is only supported for `REST API`. So, you must subscribe to the `WebSocket` with the `symbol` value declared in the `config.json` file.
- Right now, if you supply WRONG `exchange`, `symbol`, or `timeframe` in the URL, You WILL subscribe, but you WON'T receive any updates! I'll fix it later ;)

## Cautions and Warnings

 - This is definitely NOT a production-ready tool. Do NOT use it in production or serious projects, or use it at YOUR OWN RISK!
 - Right now, it lacks some important features like authorization, rate limiting, etc. I'll try to implement them in the future.
 - It's under semi-active(!) development and it may have several breaking changes, or changes in the project roadmap.
 

 ## Project Roadmap

 - [ ] Implementing persistent storages.
 - [ ] Adding the ability to retrieve more than 500 candles (from persistent storages).
 - [ ] Adding the ability to edit and reflect configurations without restarting the app.
 - [ ] Implementing rate limiters.
 - [ ] Implementing JWT authorization and API keys.
 - [ ] Implementing Orderbook data ingestion.
 - [ ] Implementing trades data ingestion.
 
 

