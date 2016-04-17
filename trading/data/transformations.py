def normalize_price_data(price_data, target_field='ask'):
    prices = [candle_data[target_field] for candle_data in price_data]
    return prices