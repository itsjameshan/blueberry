"""
农业建议规则引擎
根据气象数据和蓝莓生长阶段生成农业建议
"""

# 默认阈值
DEFAULT_THRESHOLDS = {
    'temp_high': 35,
    'temp_low': 5,
    'humidity_high': 85,
    'humidity_low': 40,
    'wind_speed_high': 30,
    'precipitation_high': 30
}


def get_agricultural_advice(weather_data, growth_stage, thresholds=None):
    """
    根据气象数据和生长阶段生成农业建议
    
    Args:
        weather_data: 气象数据字典
        growth_stage: 生长阶段 (dormant/sprouting/flowering/fruiting)
        thresholds: 用户自定义阈值（可选）
    
    Returns:
        list: 建议列表，每项包含 title, content, level
    """
    advice_list = []
    
    if not weather_data or not weather_data.get('realtime'):
        return advice_list
    
    # 合并阈值（用户自定义覆盖默认值）
    if thresholds:
        t = {**DEFAULT_THRESHOLDS, **thresholds}
    else:
        t = DEFAULT_THRESHOLDS
    
    realtime = weather_data['realtime']
    forecast = weather_data.get('forecast', [])
    
    # 获取气象数据
    temp = float(realtime.get('temp', 0))
    humidity = float(realtime.get('humidity', 0))
    wind_speed = float(realtime.get('windSpeed', 0))
    precipitation = float(realtime.get('precipitation', 0))
    pressure = float(realtime.get('pressure', 0))
    visibility = float(realtime.get('visibility', 0))
    
    # 根据生长阶段和气象数据生成建议
    if growth_stage == 'dormant':
        advice_list.extend(_get_dormant_advice(temp, humidity, forecast, t))
    elif growth_stage == 'sprouting':
        advice_list.extend(_get_sprouting_advice(temp, humidity, forecast, t))
    elif growth_stage == 'flowering':
        advice_list.extend(_get_flowering_advice(temp, humidity, wind_speed, precipitation, forecast, t))
    elif growth_stage == 'fruiting':
        advice_list.extend(_get_fruiting_advice(temp, humidity, wind_speed, precipitation, forecast, t))
    
    # 通用建议（所有阶段都适用）
    advice_list.extend(_get_general_advice(temp, humidity, wind_speed, precipitation, pressure, visibility, forecast, t))
    
    return advice_list


def _get_dormant_advice(temp, humidity, forecast, t):
    """休眠期建议"""
    advice = []
    
    # 极端低温防护（固定阈值，不受用户设置影响）
    if temp < -10:
        advice.append({
            'title': '极端低温预警',
            'content': '温度低于-10°C，存在严重冻害风险！建议立即采取应急措施：培土覆盖根部、包裹树干、果园熏烟防霜。',
            'level': 'warning'
        })
    elif temp < -5:
        advice.append({
            'title': '低温冻害预警',
            'content': '温度低于-5°C，建议加强防寒措施：检查覆盖物是否完好，必要时增加保温层。',
            'level': 'warning'
        })
    elif temp < t['temp_low']:
        advice.append({
            'title': '低温预警',
            'content': f'当前温度低于{t["temp_low"]}°C（您的预警阈值），建议检查果园防寒措施，确保蓝莓植株安全越冬。',
            'level': 'warning'
        })
    
    # 高温预警（所有阶段通用）
    if temp > t['temp_high']:
        advice.append({
            'title': '高温预警',
            'content': f'当前温度{temp}°C，超过您的高温预警阈值{t["temp_high"]}°C，请注意果园防暑降温。',
            'level': 'warning'
        })
    
    if 0 <= temp < 5:
        advice.append({
            'title': '温度适宜',
            'content': '当前温度适合蓝莓休眠，注意保持土壤适度湿润，避免干旱。',
            'level': 'info'
        })
    
    # 湿度建议
    if humidity < t['humidity_low']:
        advice.append({
            'title': '空气干燥',
            'content': '空气湿度较低，建议适当灌溉，保持土壤湿润，防止植株脱水。',
            'level': 'info'
        })
    elif humidity > t['humidity_high']:
        advice.append({
            'title': '湿度过高',
            'content': '休眠期湿度过高，注意排水防涝，避免根部腐烂。',
            'level': 'warning'
        })
    
    # 未来天气预警
    if forecast:
        for day in forecast[:3]:
            temp_min = float(day.get('tempMin', 0))
            if temp_min < -10:
                advice.append({
                    'title': '未来极端低温',
                    'content': f'预计{day.get("date", "近期")}最低温度{temp_min}°C，请提前做好防寒准备。',
                    'level': 'warning'
                })
                break
    
    return advice


def _get_sprouting_advice(temp, humidity, forecast, t):
    """萌芽期建议"""
    advice = []
    
    # 倒春寒预警
    if temp < 0:
        advice.append({
            'title': '倒春寒预警',
            'content': '萌芽期遭遇低温，新芽可能受冻！建议立即采取防霜措施：熏烟、覆盖、喷施防冻剂。',
            'level': 'warning'
        })
    elif temp < t['temp_low']:
        advice.append({
            'title': '温度偏低',
            'content': f'萌芽期温度低于{t["temp_low"]}°C（您的预警阈值），可能影响萌芽速度，建议关注天气预报，必要时采取保温措施。',
            'level': 'warning'
        })
    elif 10 <= temp <= 20:
        advice.append({
            'title': '温度适宜',
            'content': '当前温度适合萌芽生长，建议保持土壤湿润，促进新芽发育。',
            'level': 'info'
        })
    elif temp > t['temp_high']:
        advice.append({
            'title': '温度偏高',
            'content': f'萌芽期温度超过{t["temp_high"]}°C（您的预警阈值），建议加强通风，防止病虫害发生，注意适当遮阴。',
            'level': 'info'
        })
    
    # 湿度建议
    if humidity > t['humidity_high']:
        advice.append({
            'title': '湿度过高',
            'content': '萌芽期湿度过高，容易引发病害，建议加强通风降湿，注意病害防治。',
            'level': 'warning'
        })
    elif humidity < t['humidity_low']:
        advice.append({
            'title': '空气干燥',
            'content': '空气湿度较低，建议适当灌溉或喷雾，保持果园湿度在60-70%。',
            'level': 'info'
        })
    elif 50 <= humidity <= 75:
        advice.append({
            'title': '湿度适宜',
            'content': '当前湿度适合萌芽生长，继续保持良好管理。',
            'level': 'info'
        })
    
    # 未来天气预警
    if forecast:
        for day in forecast[:3]:
            temp_min = float(day.get('tempMin', 0))
            if temp_min < 0:
                advice.append({
                    'title': '霜冻预警',
                    'content': f'预计{day.get("date", "近期")}最低温度{temp_min}°C，萌芽期霜冻危害大，请提前准备防霜物资。',
                    'level': 'warning'
                })
                break
    
    return advice


def _get_flowering_advice(temp, humidity, wind_speed, precipitation, forecast, t):
    """花期建议"""
    advice = []
    
    # 温度建议
    if temp < 5:
        advice.append({
            'title': '花期霜冻预警',
            'content': '花期温度低于5°C，霜冻将严重影响授粉和坐果！建议立即熏烟防霜、覆盖保温。',
            'level': 'warning'
        })
    elif temp < t['temp_low']:
        advice.append({
            'title': '花期低温',
            'content': f'花期温度低于{t["temp_low"]}°C（您的预警阈值），可能影响授粉，建议采取保温措施或延迟开花。',
            'level': 'warning'
        })
    elif 15 <= temp <= 25:
        advice.append({
            'title': '温度适宜',
            'content': '当前温度适合开花授粉，建议保护授粉昆虫，避免使用农药。',
            'level': 'info'
        })
    elif temp > t['temp_high']:
        advice.append({
            'title': '花期高温',
            'content': f'花期温度超过{t["temp_high"]}°C（您的预警阈值），可能影响授粉质量，建议遮阳降温、增加喷灌。',
            'level': 'warning'
        })
    
    # 风速建议
    if wind_speed > t['wind_speed_high']:
        advice.append({
            'title': '大风预警',
            'content': f'风速超过{t["wind_speed_high"]}km/h（您的预警阈值），严重影响授粉昆虫活动，建议设置风障保护，必要时人工辅助授粉。',
            'level': 'warning'
        })
    elif wind_speed > 20:
        advice.append({
            'title': '大风预警',
            'content': '风速较大，可能影响授粉昆虫活动，建议设置风障保护。',
            'level': 'warning'
        })
    elif 5 <= wind_speed <= 15:
        advice.append({
            'title': '风速适宜',
            'content': '当前风速适合授粉昆虫活动，有利于自然授粉。',
            'level': 'info'
        })
    
    # 降水建议
    if precipitation > t['precipitation_high']:
        advice.append({
            'title': '强降雨预警',
            'content': f'花期降水量超过{t["precipitation_high"]}mm（您的预警阈值），将严重影响授粉，建议加强排水，雨后及时人工辅助授粉。',
            'level': 'warning'
        })
    elif precipitation > 10:
        advice.append({
            'title': '降雨预警',
            'content': '花期降雨过多，可能影响授粉，建议加强排水，必要时人工辅助授粉。',
            'level': 'warning'
        })
    elif precipitation == 0:
        advice.append({
            'title': '天气晴朗',
            'content': '当前无降水，适合授粉昆虫活动，注意保持土壤适度湿润。',
            'level': 'info'
        })
    
    # 湿度建议
    if humidity > 90:
        advice.append({
            'title': '湿度过高预警',
            'content': '花期湿度过高，极易引发灰霉病等病害！建议加强通风，必要时喷施杀菌剂。',
            'level': 'warning'
        })
    elif humidity > t['humidity_high']:
        advice.append({
            'title': '湿度过高',
            'content': '花期湿度过高，容易引发灰霉病等病害，建议加强通风和病害防治。',
            'level': 'warning'
        })
    elif 50 <= humidity <= 75:
        advice.append({
            'title': '湿度适宜',
            'content': '当前湿度适合开花授粉，继续保持良好管理。',
            'level': 'info'
        })
    
    # 未来天气预警
    if forecast:
        for day in forecast[:3]:
            temp_min = float(day.get('tempMin', 0))
            precip = float(day.get('precip', 0))
            if temp_min < 5:
                advice.append({
                    'title': '花期霜冻预警',
                    'content': f'预计{day.get("date", "近期")}最低温度{temp_min}°C，花期霜冻危害极大，请提前准备防霜措施。',
                    'level': 'warning'
                })
                break
            if precip > t['precipitation_high']:
                advice.append({
                    'title': '花期降雨预警',
                    'content': f'预计{day.get("date", "近期")}降水量{precip}mm，将影响授粉，请做好应对准备。',
                    'level': 'warning'
                })
                break
    
    return advice


def _get_fruiting_advice(temp, humidity, wind_speed, precipitation, forecast, t):
    """果期建议"""
    advice = []
    
    # 温度建议
    if temp < 10:
        advice.append({
            'title': '果期低温预警',
            'content': '果期温度过低，严重影响果实发育和品质，建议采取保温措施。',
            'level': 'warning'
        })
    elif temp < t['temp_low']:
        advice.append({
            'title': '果期低温',
            'content': f'果期温度低于{t["temp_low"]}°C（您的预警阈值），可能影响果实发育，建议关注天气预报，必要时采取保温措施。',
            'level': 'warning'
        })
    elif 20 <= temp <= 28:
        advice.append({
            'title': '温度适宜',
            'content': '当前温度适宜果实发育和糖分积累，建议保持土壤湿润，定期巡查病虫害。',
            'level': 'info'
        })
    elif temp > t['temp_high']:
        advice.append({
            'title': '高温灼果预警',
            'content': f'果期温度超过{t["temp_high"]}°C（您的预警阈值），极易导致日灼病和果实软化！建议立即遮阳、早晚灌溉、地面覆盖保湿。',
            'level': 'warning'
        })
    elif temp > 30:
        advice.append({
            'title': '果期高温',
            'content': '果期温度偏高，可能导致果实品质下降，建议遮阳降温、增加灌溉。',
            'level': 'warning'
        })
    
    # 风速建议
    if wind_speed > t['wind_speed_high']:
        advice.append({
            'title': '大风预警',
            'content': f'风速超过{t["wind_speed_high"]}km/h（您的预警阈值），极易导致落果和枝条折断！建议立即加固支架，提前采摘成熟果实。',
            'level': 'warning'
        })
    elif wind_speed > 25:
        advice.append({
            'title': '大风预警',
            'content': '风速较大，可能导致落果，建议设置风障保护，加固支架。',
            'level': 'warning'
        })
    elif 5 <= wind_speed <= 15:
        advice.append({
            'title': '风速适宜',
            'content': '当前风速适中，有利于果园通风，减少病害发生。',
            'level': 'info'
        })
    
    # 降水建议
    if precipitation > t['precipitation_high']:
        advice.append({
            'title': '暴雨预警',
            'content': f'果期降水量超过{t["precipitation_high"]}mm（您的预警阈值），极易导致裂果、落果和病害爆发！建议立即排水防涝，采摘已成熟果实。',
            'level': 'warning'
        })
    elif precipitation > 20:
        advice.append({
            'title': '强降雨预警',
            'content': '降雨量过大，可能导致裂果和病害，建议加强排水和病害防治。',
            'level': 'warning'
        })
    elif precipitation > 10:
        advice.append({
            'title': '降雨注意',
            'content': '果期降雨较多，注意排水防涝，雨后及时巡查果园。',
            'level': 'info'
        })
    elif precipitation == 0:
        advice.append({
            'title': '天气晴朗',
            'content': '当前无降水，有利于果实成熟和采摘，注意保持土壤适度湿润。',
            'level': 'info'
        })
    
    # 湿度建议
    if humidity > 90:
        advice.append({
            'title': '湿度过高预警',
            'content': '果期湿度过高，极易引发炭疽病、灰霉病等病害！建议加强通风，必要时喷施杀菌剂。',
            'level': 'warning'
        })
    elif humidity > t['humidity_high']:
        advice.append({
            'title': '湿度过高',
            'content': '果期湿度过高，容易引发炭疽病等病害，建议加强通风和病害防治。',
            'level': 'info'
        })
    elif humidity < t['humidity_low']:
        advice.append({
            'title': '湿度偏低',
            'content': '空气湿度较低，建议适当灌溉或喷雾，保持果园湿度在60-70%，防止果实失水。',
            'level': 'info'
        })
    elif 50 <= humidity <= 75:
        advice.append({
            'title': '湿度适宜',
            'content': '当前湿度适合果实发育，继续保持良好管理。',
            'level': 'info'
        })
    
    # 未来天气预警
    if forecast:
        for day in forecast[:3]:
            temp_max = float(day.get('tempMax', 0))
            precip = float(day.get('precip', 0))
            if temp_max > t['temp_high']:
                advice.append({
                    'title': '高温预警',
                    'content': f'预计{day.get("date", "近期")}最高温度{temp_max}°C，果期高温危害大，请提前准备遮阳措施。',
                    'level': 'warning'
                })
                break
            if precip > t['precipitation_high']:
                advice.append({
                    'title': '暴雨预警',
                    'content': f'预计{day.get("date", "近期")}降水量{precip}mm，果期暴雨危害极大，请做好排水和采摘准备。',
                    'level': 'warning'
                })
                break
    
    return advice


def _get_general_advice(temp, humidity, wind_speed, precipitation, pressure, visibility, forecast, t):
    """通用建议"""
    advice = []
    
    # 基于用户阈值的通用预警（所有阶段都检查）
    if temp > t['temp_high']:
        # 已在各阶段函数中处理，这里不再重复
        pass
    
    if humidity > t['humidity_high']:
        # 已在各阶段函数中处理，这里不再重复
        pass
    
    if wind_speed > t['wind_speed_high']:
        advice.append({
            'title': '大风预警',
            'content': f'当前风速{wind_speed}km/h，超过您的大风预警阈值{t["wind_speed_high"]}km/h，请注意果园防风。',
            'level': 'warning'
        })
    
    if precipitation > t['precipitation_high']:
        advice.append({
            'title': '强降雨预警',
            'content': f'当前降水量{precipitation}mm，超过您的强降雨预警阈值{t["precipitation_high"]}mm，请注意排水防涝。',
            'level': 'warning'
        })
    
    # 灌溉建议
    if humidity < t['humidity_low'] and precipitation < 5:
        advice.append({
            'title': '灌溉建议',
            'content': '空气干燥且近期无有效降水，建议及时灌溉，保持土壤湿润。',
            'level': 'info'
        })
    
    # 气压异常预警
    if pressure > 0:
        if pressure < 980:
            advice.append({
                'title': '低气压预警',
                'content': '当前气压偏低，可能有恶劣天气来临，请关注天气预报。',
                'level': 'info'
            })
        elif pressure > 1030:
            advice.append({
                'title': '高气压提示',
                'content': '当前气压偏高，天气晴朗稳定，适合果园管理作业。',
                'level': 'info'
            })
    
    # 能见度预警
    if visibility > 0 and visibility < 1:
        advice.append({
            'title': '能见度低',
            'content': '当前能见度低于1公里，可能有雾或霾，注意果园作业安全。',
            'level': 'warning'
        })
    elif visibility > 0 and visibility < 5:
        advice.append({
            'title': '能见度较低',
            'content': '当前能见度较低，果园作业时请注意安全。',
            'level': 'info'
        })
    
    # 未来天气预警
    if forecast and len(forecast) >= 1:
        tomorrow = forecast[0]
        tomorrow_temp_max = float(tomorrow.get('tempMax', 0))
        tomorrow_temp_min = float(tomorrow.get('tempMin', 0))
        tomorrow_precip = float(tomorrow.get('precip', 0))
        
        # 温度骤变预警
        if abs(tomorrow_temp_max - temp) > 15:
            advice.append({
                'title': '温度剧变预警',
                'content': f'明日温度变化剧烈（{tomorrow_temp_min}°C ~ {tomorrow_temp_max}°C），请做好防护措施。',
                'level': 'warning'
            })
        elif abs(tomorrow_temp_max - temp) > 10:
            advice.append({
                'title': '温度变化较大',
                'content': f'明日温度变化较大（{tomorrow_temp_min}°C ~ {tomorrow_temp_max}°C），请注意防护。',
                'level': 'info'
            })
        
        # 强降雨预警
        if tomorrow_precip > 50:
            advice.append({
                'title': '暴雨预警',
                'content': f'明日预计降水量 {tomorrow_precip}mm，暴雨天气，请提前做好排水和防护措施。',
                'level': 'warning'
            })
        elif tomorrow_precip > t['precipitation_high']:
            advice.append({
                'title': '强降雨预警',
                'content': f'明日预计降水量 {tomorrow_precip}mm，建议提前做好排水准备。',
                'level': 'warning'
            })
    
    # 连续降水预警
    if forecast:
        rainy_days = 0
        for day in forecast[:5]:
            if float(day.get('precip', 0)) > 10:
                rainy_days += 1
        if rainy_days >= 3:
            advice.append({
                'title': '连续降水预警',
                'content': f'未来几天连续降水（{rainy_days}天），请注意排水防涝，加强病害防治。',
                'level': 'warning'
            })
    
    return advice
