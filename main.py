import asyncio
import time
from datetime import datetime
from iol_api import InvertirOnlineAPI
from database.database_conn import DatabaseConn
from dotenv import load_dotenv
import os
import logging


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

    async def evaluate_opportunity(self):
        while True:
            try:
                self.database.cur.execute("SELECT * FROM market_data ORDER BY timestamp DESC LIMIT 10")
                latest_data = self.database.cur.fetchall()

                if latest_data:
                    for record in latest_data:
                        symbol, price, timestamp = record[1], record[2], record[3]
                        if price < 100:  # Ejemplo de lógica de compra
                            logging.warning(f"Oportunidad de venta en {symbol} a {price}")
                            print(f"Oportunidad de compra en {symbol} a {price}")
                        elif price > 200:  # Ejemplo de lógica de venta
                            logging.warning(f"Oportunidad de venta en {symbol} a {price}")
                            print(f"Oportunidad de venta en {symbol} a {price}")

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
        strategy_evaluator.evaluate_opportunity()
    )

if __name__ == "__main__":
    asyncio.run(main())
