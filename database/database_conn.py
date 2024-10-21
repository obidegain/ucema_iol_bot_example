import time
import sqlite3
import logging
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger()

class DatabaseConn:
    def __init__(self):
        self.conn = sqlite3.connect('market_data.db')
        self.cur = self.conn.cursor()
        self.create_table_if_doesnt_exists("market_data")
        logger.info(f"Conexión a la base de datos establecida correctamente")

    def create_table_if_doesnt_exists(self, table_name):
        self.cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT,
            symbol TEXT,
            price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()
        logger.info(f"Table created: {table_name}")

    def save_market_data(self, market, symbol, price, timestamp):
        self.cur.execute("INSERT INTO market_data (market, symbol, price, timestamp) VALUES (?, ?, ?, ?)", (market, symbol, price, timestamp))
        self.conn.commit()
        logger.info(f"Data saved: {market} - {symbol} - {price} - {timestamp}")