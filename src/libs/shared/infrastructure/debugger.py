# import pydevd_pycharm
from ptvsd import enable_attach


def enable_debugger(host: str, port: int) -> None:
    try:
        print('Starting Debug...')
        # pydevd_pycharm.settrace(HTTP_HOST, port=int(DEBUG_PORT), stdoutToServer=True, stderrToServer=True)
        enable_attach(address=(host, int(port)))
    except Exception:  # nosec
        pass
