import time


def make_trading_session_info(started_at, ended_at, num_ticks, shutdown_cause):
    return {
        'session_id': time.time(),
        'started_at': started_at,
        'ended_at': ended_at,
        'num_ticks': num_ticks,
        'shutdown_cause': shutdown_cause
    }