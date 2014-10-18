# -*- coding: utf-8 -*-
"""
    Хелпер для работы с сигнатурами

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import string
import hashlib
import hmac
import time
import base64
from flask.ext.bcrypt import check_password_hash, generate_password_hash

from functools import reduce

EDGE = '101'
MIDDLE = '01010'
CODES = {
    'A': ('0001101', '0011001', '0010011', '0111101', '0100011',
          '0110001', '0101111', '0111011', '0110111', '0001011'),
    'B': ('0100111', '0110011', '0011011', '0100001', '0011101',
          '0111001', '0000101', '0010001', '0001001', '0010111'),
    'C': ('1110010', '1100110', '1101100', '1000010', '1011100',
          '1001110', '1010000', '1000100', '1001000', '1110100'),
}
LEFT_PATTERN = ('AAAAAA', 'AABABB', 'AABBAB', 'AABBBA', 'ABAABB',
                'ABBAAB', 'ABBBAA', 'ABABAB', 'ABABBA', 'ABBABA')

CRYPT_ROUND = 10


def get_content_md5(data):
    m = hashlib.md5()
    m.update(data)
    signature = base64.b64encode(m.digest())
    return signature


def get_ean_checksum(ean):
    sum_ = lambda x, y: int(x) + int(y)
    evensum = reduce(sum_, ean[::2])
    oddsum = reduce(sum_, ean[1::2])
    return (10 - ((evensum + oddsum * 3) % 10)) % 10


def get_ean_barcode(ean):
    code = EDGE[:]
    pattern = LEFT_PATTERN[int(ean[0])]
    for i, number in enumerate(ean[1:7]):
        code += CODES[pattern[i]][int(number)]
    code += MIDDLE
    for number in ean[7:]:
        code += CODES['C'][int(number)]
    code += EDGE
    return [code]


def get_isin_checksum(isin):
    """Calculate and return the check digit"""
    # Convert alpha characters to digits
    isin2 = []
    for char in isin[:-1]:
        if char.isalpha():
            isin2.append((string.ascii_uppercase.index(char.upper()) + 9 + 1))
        else:
            isin2.append(char)
    # Convert each int into string and join
    isin2 = ''.join([str(i) for i in isin2])
    # Gather every second digit (even)
    even = isin2[::2]
    # Gather the other digits (odd)
    odd = isin2[1::2]
    # If len(isin2) is odd, multiply evens by 2, else multiply odds by 2
    if len(isin2) % 2 > 0:
        even = ''.join([str(int(i) * 2) for i in list(even)])
    else:
        odd = ''.join([str(int(i) * 2) for i in list(odd)])
    even_sum = sum([int(i) for i in even])
    # then add each single int in both odd and even
    odd_sum = sum([int(i) for i in odd])
    mod = (even_sum + odd_sum) % 10

    result = 10 - mod
    if result == 10:
        result = 0
    return result


def get_api_sign(secret, data):
    keys = sorted(data.keys())

    post = []
    for key in keys:
        if isinstance(data[key], unicode):
            post.append('%s=%s' % (key, data[key].encode('utf-8')))
        else:
            post.append('%s=%s' % (key, data[key]))

    H = hmac.new(secret, digestmod=hashlib.sha512)
    H.update('&'.join(post))
    return H.hexdigest()


def get_activkey(data):
    data = str(time.time()) + data
    return hashlib.sha1(data).hexdigest()


def get_password_hash(password):
    return generate_password_hash(password, CRYPT_ROUND)


def check_password(password_hash, password):
    return check_password_hash(password_hash, password)


def get_user_token(request):
    address = request.remote_addr
    user_agent = request.user_agent

    base = '{0}|{1}'.format(address, user_agent)
    if str is bytes:
        base = unicode(base, 'utf-8', errors='replace')
    h = hashlib.md5()
    h.update(base.encode('utf8'))
    return h.hexdigest()
