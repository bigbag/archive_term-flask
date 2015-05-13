from external_services import api_request

from configs.general import Config

TROIKA_CARD_API_URL = "%(troika_url)s/api/card" % {'troika_url': Config.TROIKA_URL}


def get_card_by_hard_id(hard_id):
    url = "%(api_url)s/hard_id/%(hard_id)s" % {
        'api_url': TROIKA_CARD_API_URL,
        'hard_id': hard_id
    }
    result = api_request(
        method='GET',
        url=url,
        auth=(Config.TROIKA_USER, Config.TROIKA_PASSWORD))

    return result


def release_card(hard_id):
    url = "%(api_url)s/release" % {'api_url': TROIKA_CARD_API_URL}
    result = api_request(
        method='POST',
        url=url,
        auth=(Config.TROIKA_USER, Config.TROIKA_PASSWORD),
        data={'hard_id': hard_id})

    return result
