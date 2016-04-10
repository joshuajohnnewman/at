

def make_order(broker, order):
    order_confirmation = broker.make_order(order)
    return order_confirmation