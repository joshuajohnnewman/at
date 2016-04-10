import oandapy

def get_broker():
    oanda = oandapy.API(environment="practice", access_token=os.environ['OANDA_ACCESS_TOKEN'])
