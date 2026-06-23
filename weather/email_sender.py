"""
邮件发送模块
用于发送气象预警邮件
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_alert_email(to_email, subject, content, html_content=None):
    """
    发送预警邮件
    
    Args:
        to_email: 收件人邮箱
        subject: 邮件主题
        content: 纯文本内容
        html_content: HTML格式内容（可选）
    
    Returns:
        bool: 发送成功返回True，失败返回False
        str: 错误信息（如果有）
    """
    # 从环境变量获取SMTP配置
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.qq.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '465'))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_pass = os.environ.get('SMTP_PASS', '')
    smtp_from = os.environ.get('SMTP_FROM', smtp_user)
    
    if not smtp_user or not smtp_pass:
        return False, "SMTP配置缺失，请检查环境变量SMTP_USER和SMTP_PASS"
    
    try:
        # 创建邮件消息
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_from
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # 添加纯文本内容
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # 添加HTML内容（如果有）
        if html_content:
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # 连接SMTP服务器并发送
        if smtp_port == 465:
            # 使用SSL
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            # 使用TLS
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
        
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_from, [to_email], msg.as_string())
        server.quit()
        
        return True, None
        
    except Exception as e:
        return False, str(e)


def send_weather_alert_email(to_email, garden_name, alert_title, alert_content, weather_data=None):
    """
    发送气象预警邮件
    
    Args:
        to_email: 收件人邮箱
        garden_name: 果园名称
        alert_title: 预警标题
        alert_content: 预警内容
        weather_data: 当前天气数据（可选）
    
    Returns:
        bool: 发送成功返回True，失败返回False
        str: 错误信息（如果有）
    """
    subject = f"【气象预警】{garden_name} - {alert_title}"
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 纯文本内容
    content = f"""
气象预警通知

果园：{garden_name}
预警：{alert_title}
详情：{alert_content}
时间：{now}

请及时采取相应措施，确保果园安全。

---
蓝莓智慧农业平台
"""
    
    # 提取天气数据（如果有）
    weather_info = ''
    if weather_data and weather_data.get('realtime'):
        rt = weather_data['realtime']
        temp = rt.get('temp', '--')
        humidity = rt.get('humidity', '--')
        wind = rt.get('windSpeed', '--')
        weather_text = rt.get('text', '--')
        weather_info = f"""
            <tr>
                <td style="padding: 12px 0; border-bottom: 1px solid #eee; font-weight: bold;">当前天气</td>
                <td style="padding: 12px 0; border-bottom: 1px solid #eee;">{weather_text} / {temp}°C</td>
            </tr>
            <tr>
                <td style="padding: 12px 0; border-bottom: 1px solid #eee; font-weight: bold;">湿度</td>
                <td style="padding: 12px 0; border-bottom: 1px solid #eee;">{humidity}%</td>
            </tr>
            <tr>
                <td style="padding: 12px 0; border-bottom: 1px solid #eee; font-weight: bold;">风速</td>
                <td style="padding: 12px 0; border-bottom: 1px solid #eee;">{wind} km/h</td>
            </tr>
"""
    
    # HTML内容 - 优化版模板
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f0f2f5; font-family: -apple-system, 'Microsoft YaHei', 'Helvetica Neue', sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 30px 15px;">
                <table role="presentation" style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                    
                    <!-- 顶部品牌栏 -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%); padding: 24px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 600; letter-spacing: 1px;">蓝莓智慧农业平台</h1>
                            <p style="margin: 6px 0 0; color: rgba(255,255,255,0.85); font-size: 13px;">Blueberry Smart Agriculture</p>
                        </td>
                    </tr>
                    
                    <!-- 预警标题栏 -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); padding: 20px 30px;">
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td style="vertical-align: middle;">
                                        <span style="display: inline-block; width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; text-align: center; line-height: 40px; font-size: 22px; color: #fff;">&#9888;</span>
                                    </td>
                                    <td style="vertical-align: middle; padding-left: 14px;">
                                        <div style="color: #ffffff; font-size: 18px; font-weight: 600;">气象预警通知</div>
                                        <div style="color: rgba(255,255,255,0.8); font-size: 12px; margin-top: 2px;">{now}</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- 果园信息 -->
                    <tr>
                        <td style="padding: 24px 30px 0;">
                            <div style="background: #F8F7FF; border-radius: 8px; padding: 16px 20px; border-left: 4px solid #6C5CE7;">
                                <div style="color: #6C5CE7; font-size: 13px; font-weight: 600; margin-bottom: 4px;">果园信息</div>
                                <div style="color: #333; font-size: 16px; font-weight: 600;">{garden_name}</div>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- 预警详情 -->
                    <tr>
                        <td style="padding: 20px 30px 0;">
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-weight: 600; color: #555; width: 80px; font-size: 14px;">预警</td>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0; color: #E74C3C; font-weight: 600; font-size: 14px;">{alert_title}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-weight: 600; color: #555; vertical-align: top; font-size: 14px;">详情</td>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0; color: #333; font-size: 14px; line-height: 1.7;">{alert_content}</td>
                                </tr>
                                {weather_info}
                                <tr>
                                    <td style="padding: 12px 0; font-weight: 600; color: #555; font-size: 14px;">时间</td>
                                    <td style="padding: 12px 0; color: #888; font-size: 14px;">{now}</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- 建议操作 -->
                    <tr>
                        <td style="padding: 20px 30px 0;">
                            <div style="background: #FFF5F5; border-radius: 8px; padding: 18px 20px; border-left: 4px solid #E74C3C;">
                                <div style="color: #E74C3C; font-size: 14px; font-weight: 600; margin-bottom: 6px;">&#128680; 请及时处理</div>
                                <p style="margin: 0; color: #555; font-size: 13px; line-height: 1.7;">请根据预警内容及时采取相应措施，确保果园安全。如有疑问，请联系农业技术顾问。</p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- 底部 -->
                    <tr>
                        <td style="padding: 30px; text-align: center;">
                            <div style="border-top: 1px solid #f0f0f0; padding-top: 20px;">
                                <div style="color: #999; font-size: 12px; line-height: 1.8;">
                                    此邮件由蓝莓智慧农业平台自动发送<br>
                                    请勿直接回复此邮件
                                </div>
                                <div style="margin-top: 12px;">
                                    <span style="display: inline-block; background: #6C5CE7; color: #fff; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 500;">蓝莓智慧农业平台</span>
                                </div>
                            </div>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    return send_alert_email(to_email, subject, content, html_content)
