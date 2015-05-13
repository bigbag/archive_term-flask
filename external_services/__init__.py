import time
import logging
import requests


__all__ = (
    'api_request',
)

DEFAULT_TIMEOUT = 30  # 30 sec


def api_request(method, url, timeout=DEFAULT_TIMEOUT, auth=None, params=None, data=None):

    start_time = time.time()

    logging.debug(u'Request URL: %(url)s', {'url': url})
    logging.debug(u'Request method: %(method)s', {'method': method})
    logging.debug(u'Request POST data: %(post_data)s', {'post_data': data})
    logging.debug(u'Request GET params: %(get_params)s', {'get_params': params})

    try:

        response = requests.request(
            method,
            url,
            data=data if data else None,
            params=params if params else None,
            auth=auth if auth else None,
            timeout=timeout)
        response_data = response.json()
    except Exception:
        logging.exception("Exception: %(body)s", {'body': response.content})
        return
    else:
        logging.debug(u'Response headers: %(headers)s',
                      {'headers': response.headers})
        logging.debug(u'Response data: %(data)s',
                      {'data': response_data})

        if response.status_code in (200, 201):
            return response_data
        else:
            logging.error(u'Request failed. Response_code: %(code)s',
                          {'code': response.status_code})
            return
    finally:
        request_time = (time.time() - start_time) * 1000
        logging.debug(u'Request time: %(time)s ms', {'time': request_time})
