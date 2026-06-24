"""
和风天气 API 封装模块
文档：https://dev.qweather.com/docs/api/
"""
import os
import json
import requests
from datetime import datetime


API_KEY = os.environ.get('QWEATHER_API_KEY', '')
API_HOST = os.environ.get('QWEATHER_API_HOST', '')
# 使用开发者独立的 API Host
BASE_URL = f'https://{API_HOST}/v7' if API_HOST else ''
GEO_URL = f'https://{API_HOST}/geo/v2' if API_HOST else ''


def _request(url, params=None):
    """发送 GET 请求到和风天气 API"""
    if not API_KEY:
        raise RuntimeError('和风天气 API Key 未配置')
    params = params or {}
    params['key'] = API_KEY
    try:
        resp = requests.get(url, params=params, timeout=10)
        # 403表示免费版不支持该接口，返回None而不是抛出异常
        if resp.status_code == 403:
            return None
        resp.raise_for_status()
        data = resp.json()
        if data.get('code') != '200':
            # 400等错误也返回None，让调用方处理
            return None
        return data
    except requests.RequestException:
        return None


def lookup_city(city_name):
    """
    通过城市名查询 location_id
    返回: dict 或 None
    """
    data = _request(f'{GEO_URL}/city/lookup', {'location': city_name})
    location_list = data.get('location', [])
    if not location_list:
        return None
    loc = location_list[0]
    return {
        'location_id': loc['id'],
        'name': loc['name'],
        'province': loc.get('adm1', ''),
        'country': loc.get('country', '')
    }


def get_realtime_weather(location_id):
    """
    获取实时天气
    返回: dict
    """
    data = _request(f'{BASE_URL}/weather/now', {'location': location_id})
    if not data:
        return None
    now = data.get('now', {})
    return {
        'temp': now.get('temp'),
        'feelsLike': now.get('feelsLike'),
        'humidity': now.get('humidity'),
        'precipitation': now.get('precip'),
        'windSpeed': now.get('windSpeed'),
        'windDir': now.get('windDir'),
        'pressure': now.get('pressure'),
        'visibility': now.get('vis'),
        'cloud': now.get('cloud'),
        'text': now.get('text'),
        'icon': now.get('icon'),
        'obsTime': now.get('obsTime')
    }


def get_forecast_7d(location_id):
    """
    获取7天天气预报（免费版支持）
    返回: list of dict
    """
    data = _request(f'{BASE_URL}/weather/7d', {'location': location_id})
    if not data:
        return []
    daily = data.get('daily', [])
    results = []
    for d in daily:
        results.append({
            'date': d.get('fxDate'),
            'tempMax': d.get('tempMax'),
            'tempMin': d.get('tempMin'),
            'textDay': d.get('textDay'),
            'textNight': d.get('textNight'),
            'humidity': d.get('humidity'),
            'windSpeedDay': d.get('windSpeedDay'),
            'precip': d.get('precip'),
            'uvIndex': d.get('uvIndex')
        })
    return results


def get_forecast_3d(location_id):
    """
    获取3天天气预报（含今天）
    返回: list of dict
    """
    data = _request(f'{BASE_URL}/weather/3d', {'location': location_id})
    if not data:
        return []
    daily = data.get('daily', [])
    results = []
    for d in daily:
        results.append({
            'date': d.get('fxDate'),
            'tempMax': d.get('tempMax'),
            'tempMin': d.get('tempMin'),
            'textDay': d.get('textDay'),
            'textNight': d.get('textNight'),
            'humidity': d.get('humidity'),
            'windSpeedDay': d.get('windSpeedDay'),
            'precip': d.get('precip'),
            'uvIndex': d.get('uvIndex')
        })
    return results


def get_weather_warnings(location_id):
    """
    获取当前天气预警
    返回: list of dict
    """
    data = _request(f'{BASE_URL}/warning/now', {'location': location_id})
    if not data:
        return []
    warnings = data.get('warning', [])
    results = []
    for w in warnings:
        results.append({
            'title': w.get('title'),
            'level': w.get('level'),
            'type': w.get('type'),
            'text': w.get('text'),
            'startTime': w.get('startTime'),
            'endTime': w.get('endTime')
        })
    return results


def get_minutely_precipitation(location_id):
    """
    获取未来2小时逐5分钟降水预报
    返回: dict
    """
    data = _request(f'{BASE_URL}/minutely/5m', {'location': location_id})
    if not data:
        return {'summary': '', 'minutely': []}
    return {
        'summary': data.get('summary', ''),
        'minutely': data.get('minutely', [])
    }


def get_air_quality(location_id):
    """
    获取实时空气质量
    返回: dict
    """
    data = _request(f'{BASE_URL}/air/now', {'location': location_id})
    if not data:
        return None
    now = data.get('now', {})
    return {
        'aqi': now.get('aqi'),
        'pm2p5': now.get('pm2p5'),
        'pm10': now.get('pm10'),
        'no2': now.get('no2'),
        'so2': now.get('so2'),
        'co': now.get('co'),
        'o3': now.get('o3'),
        'category': now.get('category')
    }


def get_sunrise_sunset(location_id, date=None):
    """
    获取日出日落时间
    date: 格式YYYY-MM-DD，默认为今天
    返回: dict
    """
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    data = _request(f'{BASE_URL}/astronomy/sun', {'location': location_id, 'date': date})
    if not data:
        return {'sunrise': '', 'sunset': '', 'date': date}
    return {
        'sunrise': data.get('sunrise', ''),
        'sunset': data.get('sunset', ''),
        'date': date
    }


def get_historical_weather(location_id, date):
    """
    获取历史天气（时光机）
    date: 格式YYYY-MM-DD
    返回: dict或None
    """
    data = _request(f'{BASE_URL}/historical/weather', {'location': location_id, 'date': date})
    if not data:
        return None
    daily = data.get('daily', [])
    if not daily:
        return None
    d = daily[0]
    return {
        'date': d.get('fxDate'),
        'tempMax': d.get('tempMax'),
        'tempMin': d.get('tempMin'),
        'humidity': d.get('humidity'),
        'precip': d.get('precip'),
        'windSpeed': d.get('windSpeed'),
        'textDay': d.get('textDay')
    }


def get_full_weather(location_id):
    """
    获取完整气象数据（实时 + 预报 + 预警 + 空气质量 + 天文）
    返回: dict
    """
    realtime = get_realtime_weather(location_id)
    forecast = get_forecast_7d(location_id)
    warnings = get_weather_warnings(location_id)
    air = get_air_quality(location_id)
    sun = get_sunrise_sunset(location_id)

    return {
        'realtime': realtime,
        'forecast': forecast,
        'warnings': warnings,
        'air': air,
        'sun': sun,
        'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
