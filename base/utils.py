from collections import namedtuple

import requests
from django.conf import settings

NormalizeAddress = namedtuple('NormalizeAddress', 'old new zip city district town')


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
    print(juso)
    return NormalizeAddress(
        juso['jibunAddr'], # 구 주소(지번)
        juso['roadAddrPart1'], # 신 주소(도로명)
        juso['zipNo'], # 우편번호
        juso['siNm'], # 시/도
        juso['sggNm'], # 시/구/군
        juso['emdNm'], # 읍/명/동
    )
