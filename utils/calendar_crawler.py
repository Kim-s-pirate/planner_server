import requests
from urllib import parse
import xml.etree.ElementTree as ET

url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/"
api_key_utf8 = "pUEaeJv+OjC323nvRDSbSMceeGyvRu2nikL9kBsBw/J2C0PKhB1I9BHD8WK4YOTJLWvtnV9RsnjsRI3j9DEMzg=="
api_key_decode = parse.unquote(api_key_utf8)
'''
getRestDeInfo
getHoliDeInfo
둘중에 하나 선택
'''
url_holiday = url + "getHoliDeInfo"
params = {
    "ServiceKey": api_key_decode,
    "solYear": 2024,
    "numOfRows": 1000
}

response = requests.get(url_holiday, params=params)
root = ET.fromstring(response.content)

# 필요한 데이터 추출 및 예쁘게 출력
for item in root.findall(".//item"):
    date_name = item.find("dateName").text
    locdate = item.find("locdate").text
    is_holiday = item.find("isHoliday").text
    print(f"날짜: {locdate}, 이름: {date_name}, 공휴일 여부: {is_holiday}")