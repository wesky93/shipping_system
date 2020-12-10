from collections import namedtuple

import requests
from django.conf import settings

NormalizeAddress = namedtuple('NormalizeAddress', 'old new zip')


def normalize_address(address: str) -> NormalizeAddress:
    data = {
        "confmKey": settings.ADDRESS_SECRET_KEY,
        "currentPage": 1,
        "countPerPage": 1,
        "keyword": address,
        "resultType": 'json',
    }
    resp = requests.post('https://www.juso.go.kr/addrlink/addrLinkApi.do', data=data).json().get('results', {})
    # 주소가 특정 되지 않으면 에러 발생
    meta = resp.get('common', {})
    if meta.get('errorMessage') != '정상' or meta.get('totalCount') != '1':
        raise ValueError('please input more detail address')
    juso = resp.get('juso')[0]
    return NormalizeAddress(juso['jibunAddr'], juso['roadAddrPart1'], juso['zipNo'])
