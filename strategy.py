import pandas as pd
import logging

logger = logging.getLogger()

# Función para filtrar los datos
def filter_by_symbol(data, symbol):
    return [row for row in data if row[2] == symbol]  # 'symbol' es el tercer campo en las tuplas

# Función para calcular la media móvil
def calculate_sma(df, window=1000):
    return df['price'].rolling(window=window).mean()

# Función para calcular el ratio y tomar decisiones
def get_rebalance(df_AL30, df_GD30):
    # Obtener la última media móvil para AL30 y GD30
    media_movil_AL30 = calculate_sma(df_AL30).iloc[-1]
    media_movil_GD30 = calculate_sma(df_GD30).iloc[-1]

    # Calcular el ratio GD30/AL30
    ratio_rolling_mean_30 = media_movil_GD30 / media_movil_AL30

    # Obtener los ratios de comparación del último minuto
    ratio = df_GD30["price"].iloc[-1] / df_AL30["price"].iloc[-1]

    logger.info(f'ratio_1: {ratio} | ratio_rolling_mean_30: {ratio_rolling_mean_30}')

    # Realizar las comparaciones y tomar decisiones
    result = ratio / ratio_rolling_mean_30

    if 0.95 <= result < 0.98:
        return "Cartera GD30 60% - AL30 40%"
    elif 0.92 <= result < 0.95:
        return "Cartera GD30 70% - AL30 30%"
    elif 0.90 <= result < 0.92:
        return "Cartera GD30 80% - AL30 20%"
    elif result < 0.90:
        return "Cartera GD30 90% - AL30 10%"
    elif 1.02 <= result <= 1.05:
        return "Cartera AL30 60% - GD30 40%"
    elif 1.05 < result <= 1.08:
        return "Cartera AL30 70% - GD30 30%"
    elif 1.08 < result <= 1.1:
        return "Cartera AL30 80% - GD30 20%"
    elif result > 1.1:
        return "Cartera AL30 90% - GD30 10%"
    else:
        return "Mantener cartera AL30 50% - GD30 50%"


def strategy_rebalance_bonos(al30_data, gd30_data):
    df_AL30 = pd.DataFrame(al30_data, columns=['index', 'market', 'symbol', 'price', 'timestamp'])
    df_GD30 = pd.DataFrame(gd30_data, columns=['index', 'market', 'symbol', 'price', 'timestamp'])

    rebalance = get_rebalance(df_AL30, df_GD30)
    return rebalance

def strategy_sma(data):
    df = pd.DataFrame(data, columns=['index', 'market', 'symbol', 'price', 'timestamp'])
    fast_sma = calculate_sma(df, 20)
    slow_sma = calculate_sma(df, 200)
    price = df.iloc[-1]['price']

    if fast_sma.iloc[-1] > slow_sma.iloc[-1]:
        return "COMPRA", price
    elif fast_sma.iloc[-1] < slow_sma.iloc[-1]:
        return "VENTA", price