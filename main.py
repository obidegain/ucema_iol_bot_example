import asyncio
import time
from datetime import datetime
from iol_api import InvertirOnlineAPI
from database.database_conn import DatabaseConn
from dotenv import load_dotenv
import os
import logging
from strategy import strategy_rebalance_bonos, strategy_sma


if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/data_collection.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class DataCollector:
    def __init__(self, broker, database):
        self.broker = broker
        self.database = database

    async def collect_and_store_data(self, market, symbol):
        while True:
            try:
                data = self.broker.get_data_with_market_and_symbol(market, symbol)
                price = data['ultimoPrecio']
                timestamp = datetime.now()

                self.database.save_market_data(market, symbol, price, timestamp)

                print(f"Guardado: {symbol} - {price} - {timestamp}")
            except Exception as e:
                logging.error(f"Error DataCollector: {e}")

            await asyncio.sleep(1)

class StrategyEvaluator:
    def __init__(self, database):
        self.database = database

    async def evaluate_opportunity_bonos(self):
        rebalance = ""
        while True:
            try:
                #self.database.cur.execute("SELECT * FROM market_data")
                #latest_data = self.database.cur.fetchall()

                self.database.cur.execute("SELECT * FROM market_data WHERE symbol = 'AL30'")
                al30_data = self.database.cur.fetchall()

                self.database.cur.execute("SELECT * FROM market_data WHERE symbol = 'GD30'")
                gd30_data = self.database.cur.fetchall()

                new_rebalance = strategy_rebalance_bonos(al30_data, gd30_data)

                if new_rebalance != rebalance:
                    rebalance = new_rebalance
                    print("----------------------------------")
                    print(rebalance)
                    print("----------------------------------")
                    logging.warning(f"Rebalanceo: {rebalance}")

            except Exception as e:
                logging.error(f"Error strtategy: {e}")

            # Espera de 1 segundo antes de la próxima evaluación
            await asyncio.sleep(1)

    async def evaluate_opportunity_sma(self, symbol):
        signal = ""
        while True:
            try:
                #self.database.cur.execute("SELECT * FROM market_data")
                #latest_data = self.database.cur.fetchall()
                query = "SELECT * FROM market_data WHERE symbol = ?"
                self.database.cur.execute(query, (symbol,))
                data = self.database.cur.fetchall()

                new_signal, price = strategy_sma(data)
                if new_signal and new_signal != signal:
                    signal = new_signal
                    print("----------------------------------")
                    print(f"Symbol: {symbol} - Signal: {signal} - Price: {price}")
                    print("----------------------------------")
                    logging.warning(f"Symbol: {symbol} - Signal: {signal} - Price: {price}")

            except Exception as e:
                logging.error(f"Error strtategy: {e}")

            # Espera de 1 segundo antes de la próxima evaluación
            await asyncio.sleep(1)

async def main():
    load_dotenv()
    # Instanciar la API y la conexión a la base de datos
    broker = InvertirOnlineAPI(os.getenv('IOL_USER'), os.getenv('IOL_PASS'))
    database = DatabaseConn()

    # Crear instancias de los módulos de recolección de datos y evaluación de estrategias
    data_collector = DataCollector(broker, database)
    strategy_evaluator = StrategyEvaluator(database)

    # Ejecutar tareas de forma concurrente
    await asyncio.gather(
        data_collector.collect_and_store_data("bCBA", "AL30"),
        data_collector.collect_and_store_data("bCBA", "GD30"),
        data_collector.collect_and_store_data("bCBA", "GGAL"),
        data_collector.collect_and_store_data("bCBA", "EDN"),
        data_collector.collect_and_store_data("bCBA", "GD35"),
        strategy_evaluator.evaluate_opportunity_bonos(),
        strategy_evaluator.evaluate_opportunity_sma("GGAL")
    )

if __name__ == "__main__":
    asyncio.run(main())
