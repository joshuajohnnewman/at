def normalize_price_data(price_data, target_field='ask'):
    prices = [candle_data[target_field] for candle_data in price_data]
    return prices


def normalize_current_price_data(price_data):
    return price_data['prices'][0]