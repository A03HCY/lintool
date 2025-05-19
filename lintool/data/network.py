from typing    import Dict, List
from lintool   import try_for
from lintool.data import *
import requests
import json
import os

_base_dir_ = os.path.dirname(os.path.abspath(__file__))

def req_city_data() -> dict:
    data_file = os.path.join(_base_dir_, 'cn_city_id.json')
    with open(data_file, 'r', encoding='utf-8') as f:
        city_id = json.load(f)
    return city_id

_city_data_: dict = req_city_data()

def find_city_id(name:str) -> CitySearchResult:
    '''
    根据城市名称查找城市ID
    
    Args:
        name: 城市名称，如"北京"、"上海"或"Beijing"、"Shanghai"等
    
    Returns:
        返回包含操作结果的字典，成功时包含city_id字段
    '''
    lang = 'auto'
    try:
        # 找出匹配的城市
        matched_cities = []
        
        # 统一处理中英文城市名
        name_lower = name.lower()
        
        # 遍历城市列表
        for city_data in _city_data_:
            # 解析城市信息
            city_zh = city_data.get('cityZh', '')
            city_en = city_data.get('cityEn', '').lower()
            province_zh = city_data.get('provinceZh', '')
            province_en = city_data.get('provinceEn', '').lower()

            # 判断是否匹配
            is_zh_match = (name in city_zh) or (name in province_zh)
            is_en_match = (name_lower in city_en) or (name_lower in province_en)
            
            # 根据语言策略筛选
            if (
                (lang == 'zh' and is_zh_match) or
                (lang == 'en' and is_en_match) or
                (lang == 'auto' and (is_zh_match or is_en_match))
            ):
                # 构造地理坐标
                lat = city_data.get('lat')
                lon = city_data.get('lon')
                geo = GeoPoint(
                    lat=float(lat) if lat is not None else None,
                    lon=float(lon) if lon is not None else None
                )
                
                # 创建城市信息对象
                matched_cities.append(CityInfo(
                    city_id=city_data.get('id'),
                    name_zh=city_zh,
                    name_en=city_data.get('cityEn'),
                    province_zh=province_zh,
                    province_en=province_en,
                    geo=geo
                ))
        if not matched_cities:
            return CitySearchResult(success=False)
            
        return CitySearchResult(
            success=True,
            result_num=len(matched_cities),
            matches=matched_cities
        )

    except Exception as e:
        return CitySearchResult(success=False)
    

def weather_report(city_id: str) -> str:
    '''
    根据城市 ID 获取天气信息
    Args:
        city_id: 城市 ID
    Returns:
        天气信息
    '''
    url = f'http://t.weather.itboy.net/api/weather/city/{city_id}'
    res:dict = requests.get(url).json()
    data = {
        'status': res.get('status', '404'),
        'date': res.get('date'),
        'time': res.get('time'),
        'city': res.get('cityInfo', {})
    }
    now_info:dict = res.get('data', {})
    data['humidity'] = now_info.get('shidu')
    data['PM2.5'] = now_info.get('pm25')
    data['PM1.0'] = now_info.get('pm10')
    data['quality'] = now_info.get('quality')
    data['temp'] = now_info.get('wendu')
    forecast = []
    for day in now_info.get('forecast', []):
        if not isinstance(day, dict): continue
        day.pop('notice')
        forecast.append(day)
    data['forecast'] = forecast

    return data