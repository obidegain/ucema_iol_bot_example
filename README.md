# ucema_iol_bot_example
Disclaimer: the project is for teaching uses only.

This project is looking for create a simple connector with real time argentinian market data. To do that, is necessary create a real account in invertironline (iol).


# Create env variables:
1) create a .env file
2) write the following sentences with your api keys:
```bash
IOL_USER=''
IOL_PASS=''
```

# Modify the symbols

The project is hardcoding to collect data of AL30 and GD30, but you have the possibility to do the same with all of symbols that are available in invertir online. Is necessary the market and the symbol and modify the following sentence in main.py. Besides, you could repeat the sentences if you want recollect data about more tickers.


```bash
await asyncio.gather(
    data_collector.collect_and_store_data(replace_with_your_market, replace_with_your_ticker),
    data_collector.collect_and_store_data(replace_with_your_market, replace_with_your_ticker),
    strategy_evaluator.evaluate_opportunity()
)
```


# Modify the evaluate_opportunity method in StrategyEvaluator as you want 



# Run main.py
Recommendations: run in debugger mode (pycharm) to try to understand the errors.
