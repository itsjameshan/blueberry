from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, Response
from werkzeug.security import check_password_hash
from functools import wraps
from dotenv import load_dotenv
import os
import json
import webbrowser
import threading

load_dotenv()

from database import (
    init_db, get_user_by_username, get_user_by_id, create_user, delete_user,
    get_all_users, save_detection_record, get_user_records, get_detection_stats,
    save_model_config, get_active_model, get_all_models, set_active_model, delete_model,
    create_garden, get_garden_by_id, get_gardens_by_user, get_all_gardens,
    update_garden, delete_garden, save_weather_data, get_latest_weather,
    save_weather_alert, get_active_alerts, get_all_alerts, update_user_email
)
from detect_engine import (
    load_model, is_model_loaded, detect_single_image, draw_boxes,
    crop_image, rebuild_results, CLASS_NAMES, preprocess_image, postprocess
)
import detect_engine

app = Flask(__name__, template_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'blueberry_detection_secret_key_2026')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
RESULT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
CROP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crop_output')
ONNX_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'onnx_data')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(CROP_FOLDER, exist_ok=True)
os.makedirs(ONNX_FOLDER, exist_ok=True)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page', next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        user = get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


def row_value(row, key, default=None):
    if not row:
        return default
    if hasattr(row, 'get'):
        return row.get(key, default)
    if hasattr(row, 'keys') and key in row.keys():
        return row[key]
    return default


def get_dev_server_port(environ=None):
    if environ is None:
        environ = os.environ
    return int(environ.get('FLASK_PORT') or environ.get('PORT') or 5001)


@app.route('/')
def root():
    # 公开门户首页：未登录也可浏览；蓝莓检测 / 天气预警入口仍受 login_required 保护
    return render_template('landing.html', active='home', username=session.get('username'), role=session.get('role'))


@app.route('/about')
def about_page():
    return render_template('about.html', active='about', username=session.get('username'), role=session.get('role'))


@app.route('/tech')
def tech_page():
    return render_template('tech.html', active='tech', username=session.get('username'), role=session.get('role'))


@app.route('/more')
def more_page():
    return render_template('more.html', active='more', username=session.get('username'), role=session.get('role'))


@app.route('/portal')
@login_required
def portal():
    return render_template('portal.html', username=session.get('username'), role=session.get('role'))


@app.route('/weather')
@login_required
def weather_page():
    return render_template('weather.html', username=session.get('username'), role=session.get('role'))


@app.route('/weather/alerts')
@login_required
def alerts_page():
    return render_template('alerts.html', username=session.get('username'), role=session.get('role'))


@app.route('/api/alerts')
@login_required
def api_get_alerts():
    garden_id = request.args.get('garden_id', type=int)
    alerts = get_all_alerts(garden_id=garden_id)
    return jsonify({
        'success': True,
        'alerts': [{
            'id': a['id'],
            'garden_id': a['garden_id'],
            'garden_name': a['garden_name'],
            'title': a['alert_title'],
            'level': a['alert_level'],
            'content': a['alert_content'],
            'start_time': a['start_time'],
            'end_time': a['end_time'],
            'created_at': a['created_at']
        } for a in alerts]
    })


@app.route('/api/alerts/stats')
@login_required
def api_alerts_stats():
    """获取预警统计数据"""
    from database import get_alert_stats
    garden_id = request.args.get('garden_id', type=int)
    stats = get_alert_stats(garden_id=garden_id)
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/user/thresholds', methods=['GET'])
@login_required
def api_get_thresholds():
    """获取用户自定义预警阈值"""
    from database import get_user_thresholds
    user_id = session.get('user_id')
    thresholds = get_user_thresholds(user_id)
    return jsonify({'success': True, 'thresholds': thresholds})


@app.route('/api/user/thresholds', methods=['POST'])
@login_required
def api_save_thresholds():
    """保存用户自定义预警阈值"""
    from database import save_user_thresholds
    user_id = session.get('user_id')
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效数据'})
    success, msg = save_user_thresholds(user_id, data)
    return jsonify({'success': success, 'message': msg})


@app.route('/garden')
@login_required
def garden_page():
    return render_template('garden.html', username=session.get('username'), role=session.get('role'))


@app.route('/login', methods=['GET'])
def login_page():
    # 根据 next 目标切换登录主题：进入天气预警系统时显示天空主题登录窗
    nxt = request.args.get('next', '')
    sys = 'weather' if nxt.startswith('/weather') else 'blueberry'
    return render_template('login.html', sys=sys)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    user = get_user_by_username(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'message': '用户名或密码错误'})
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    return jsonify({'success': True, 'message': '登录成功', 'role': user['role']})


@app.route('/api/user/email', methods=['POST'])
@login_required
def api_set_email():
    data = request.get_json()
    email = data.get('email', '').strip()
    if not email:
        return jsonify({'success': False, 'message': '邮箱不能为空'})
    # 简单邮箱格式校验
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'message': '邮箱格式不正确'})
    update_user_email(session['user_id'], email)
    return jsonify({'success': True, 'message': '邮箱设置成功'})


@app.route('/api/user/info')
@login_required
def api_user_info():
    user = get_user_by_id(session['user_id'])
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'email': user['email'] if 'email' in user.keys() else ''
        }
    })


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    if len(username) < 3:
        return jsonify({'success': False, 'message': '用户名至少3个字符'})
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6个字符'})
    success, msg = create_user(username, password)
    return jsonify({'success': success, 'message': msg})


@app.route('/logout')
def logout():
    # 退出后可回到指定系统的登录界面（如天气预警系统登录窗）
    nxt = request.args.get('next', '')
    session.clear()
    if nxt.startswith('/') and not nxt.startswith('//'):
        return redirect(url_for('login_page', next=nxt))
    return redirect(url_for('login_page'))


@app.route('/index')
@login_required
def index():
    return render_template('index.html', username=session.get('username'), role=session.get('role'))


@app.route('/single_detect')
@login_required
def single_detect_page():
    return render_template('single_detect.html', username=session.get('username'), role=session.get('role'))


@app.route('/big_image')
@login_required
def big_image_page():
    return render_template('big_image.html', username=session.get('username'), role=session.get('role'))


@app.route('/batch_detect')
@login_required
def batch_detect_page():
    return render_template('batch_detect.html', username=session.get('username'), role=session.get('role'))


@app.route('/crop')
@login_required
def crop_page():
    return redirect(url_for('big_image_page'))


@app.route('/detect')
@login_required
def detect_page():
    return redirect(url_for('big_image_page'))


@app.route('/rebuild')
@login_required
def rebuild_page():
    return redirect(url_for('big_image_page'))


@app.route('/result')
@login_required
def result_page():
    record_id = request.args.get('id')
    return render_template('result.html', username=session.get('username'), role=session.get('role'), record_id=record_id)


@app.route('/admin')
@admin_required
def admin_page():
    return render_template('admin.html', username=session.get('username'), role=session.get('role'))


@app.route('/api/check_login')
def check_login():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'username': session.get('username'), 'role': session.get('role')})
    return jsonify({'logged_in': False})


@app.route('/api/detect_single', methods=['POST'])
@login_required
def api_detect_single():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': '请上传图片'})
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择图片'})

    conf = float(request.form.get('conf', 0.5))

    filename = f"{session['user_id']}_{os.urandom(8).hex()}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        results, stats = detect_single_image(filepath, conf_threshold=conf)

        result_filename = f"result_{filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        draw_boxes(filepath, results, result_path)

        save_detection_record(
            session['user_id'], file.filename, result_filename,
            stats['total'], stats['RipeBlueBerry'],
            stats['Semi-RipeBlueBerry'], stats['UnripeBlueBerry'], conf,
            json.dumps(results, ensure_ascii=False)
        )

        return jsonify({
            'success': True,
            'results': results,
            'stats': stats,
            'result_image': f'/api/result_image/{result_filename}',
            'conf_threshold': conf
        })
    except RuntimeError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'检测失败: {str(e)}'})


@app.route('/api/result_image/<filename>')
@login_required
def api_result_image(filename):
    path = os.path.join(RESULT_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({'error': '图片不存在'}), 404
    return send_file(path, mimetype='image/jpeg')


@app.route('/api/crop_tile/<crop_dir>/<filename>')
@login_required
def api_crop_tile(crop_dir, filename):
    path = os.path.join(CROP_FOLDER, crop_dir, filename)
    if not os.path.exists(path):
        return jsonify({'error': '图片不存在'}), 404
    return send_file(path, mimetype='image/jpeg')


@app.route('/api/crop', methods=['POST'])
@login_required
def api_crop():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': '请上传图片'})
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择图片'})

    tile_size = int(request.form.get('tile_size', 640))
    overlap = int(request.form.get('overlap', 200))

    filename = f"crop_{session['user_id']}_{os.urandom(8).hex()}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    crop_subdir = os.path.join(CROP_FOLDER, f"crop_{filename.rsplit('.', 1)[0]}")
    tiles = crop_image(filepath, tile_size=tile_size, overlap=overlap, output_dir=crop_subdir)

    return jsonify({
        'success': True,
        'tile_count': len(tiles),
        'tiles': tiles,
        'crop_dir': crop_subdir,
        'original_image': filename
    })


@app.route('/api/batch_detect', methods=['POST'])
@login_required
def api_batch_detect():
    data = request.get_json()
    crop_dir = data.get('crop_dir', '')
    conf = float(data.get('conf', 0.5))

    if not crop_dir or not os.path.exists(crop_dir):
        return jsonify({'success': False, 'message': '裁剪目录不存在'})

    tile_files = [f for f in os.listdir(crop_dir) if f.endswith('.jpg')]
    if not tile_files:
        return jsonify({'success': False, 'message': '裁剪目录中没有图片'})

    all_results = []
    for tile_file in tile_files:
        tile_path = os.path.join(crop_dir, tile_file)
        try:
            results, stats = detect_single_image(tile_path, conf_threshold=conf)
            all_results.append({
                'tile_name': tile_file,
                'results': results,
                'stats': stats
            })
        except RuntimeError:
            return jsonify({'success': False, 'message': '模型未加载'})
        except Exception as e:
            all_results.append({
                'tile_name': tile_file,
                'results': [],
                'stats': {'total': 0, 'RipeBlueBerry': 0, 'Semi-RipeBlueBerry': 0, 'UnripeBlueBerry': 0},
                'error': str(e)
            })

    total_stats = {'RipeBlueBerry': 0, 'Semi-RipeBlueBerry': 0, 'UnripeBlueBerry': 0, 'total': 0}
    for ar in all_results:
        for key in total_stats:
            total_stats[key] += ar['stats'].get(key, 0)

    return jsonify({
        'success': True,
        'results': all_results,
        'total_stats': total_stats,
        'conf_threshold': conf
    })


@app.route('/api/batch_detect_multi', methods=['POST'])
@login_required
def api_batch_detect_multi():
    if 'images' not in request.files:
        return jsonify({'success': False, 'message': '请上传图片'})

    files = request.files.getlist('images')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'success': False, 'message': '请选择图片'})

    conf = float(request.form.get('conf', 0.5))

    all_results = []
    total_stats = {'RipeBlueBerry': 0, 'Semi-RipeBlueBerry': 0, 'UnripeBlueBerry': 0, 'total': 0}

    for file in files:
        if file.filename == '':
            continue
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        try:
            filename = f"batch_{session['user_id']}_{os.urandom(8).hex()}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            results, stats = detect_single_image(filepath, conf_threshold=conf)

            result_filename = f"result_{filename}"
            result_path = os.path.join(RESULT_FOLDER, result_filename)
            draw_boxes(filepath, results, result_path)

            save_detection_record(
                session['user_id'], file.filename, result_filename,
                stats['total'], stats['RipeBlueBerry'],
                stats['Semi-RipeBlueBerry'], stats['UnripeBlueBerry'], conf,
                json.dumps(results, ensure_ascii=False)
            )

            for key in total_stats:
                total_stats[key] += stats.get(key, 0)

            all_results.append({
                'filename': file.filename,
                'results': results,
                'stats': stats,
                'result_image': f'/api/result_image/{result_filename}'
            })
        except RuntimeError as e:
            all_results.append({
                'filename': file.filename,
                'results': [],
                'stats': {'RipeBlueBerry': 0, 'Semi-RipeBlueBerry': 0, 'UnripeBlueBerry': 0, 'total': 0},
                'result_image': '',
                'error': str(e)
            })
        except Exception as e:
            all_results.append({
                'filename': file.filename,
                'results': [],
                'stats': {'RipeBlueBerry': 0, 'Semi-RipeBlueBerry': 0, 'UnripeBlueBerry': 0, 'total': 0},
                'result_image': '',
                'error': str(e)
            })

    return jsonify({
        'success': True,
        'results': all_results,
        'total_stats': total_stats,
        'conf_threshold': conf
    })


@app.route('/api/rebuild', methods=['POST'])
@login_required
def api_rebuild():
    data = request.get_json()
    crop_dir = data.get('crop_dir', '')
    original_image = data.get('original_image', '')
    original_width = int(data.get('original_width', 0))
    original_height = int(data.get('original_height', 0))
    tile_size = int(data.get('tile_size', 640))
    overlap = int(data.get('overlap', 200))
    conf = float(data.get('conf', 0.5))

    if not crop_dir or not os.path.exists(crop_dir):
        return jsonify({'success': False, 'message': '裁剪目录不存在'})

    tile_results = []
    tile_files = sorted([f for f in os.listdir(crop_dir) if f.endswith('.jpg')])

    for tile_file in tile_files:
        tile_path = os.path.join(crop_dir, tile_file)
        parts = tile_file.rsplit('.', 1)[0].split('_tile_')
        if len(parts) == 2:
            try:
                y_idx, x_idx = parts[1].split('_')
                y_idx, x_idx = int(y_idx), int(x_idx)
            except ValueError:
                continue
        else:
            continue

        y = y_idx * (tile_size - overlap)
        x = x_idx * (tile_size - overlap)

        tile_info = {'name': tile_file, 'x': x, 'y': y}
        try:
            results, _ = detect_single_image(tile_path, conf_threshold=conf)
            tile_results.append((tile_info, results))
        except Exception:
            tile_results.append((tile_info, []))

    original_size = (original_width, original_height)
    final_results = rebuild_results(
        tile_results, original_size,
        tile_size=tile_size, overlap=overlap, conf_threshold=conf
    )

    if original_image:
        original_path = os.path.join(UPLOAD_FOLDER, original_image)
        if os.path.exists(original_path):
            result_filename = f"rebuild_{original_image}"
            result_path = os.path.join(RESULT_FOLDER, result_filename)
            draw_boxes(original_path, final_results, result_path)

            stats = {'RipeBlueBerry': 0, 'Semi-RipeBlueBerry': 0, 'UnripeBlueBerry': 0, 'total': len(final_results)}
            for r in final_results:
                name = r['class_name']
                if name in stats:
                    stats[name] += 1

            save_detection_record(
                session['user_id'], original_image, result_filename,
                stats['total'], stats['RipeBlueBerry'],
                stats['Semi-RipeBlueBerry'], stats['UnripeBlueBerry'], conf,
                json.dumps(final_results, ensure_ascii=False)
            )

            return jsonify({
                'success': True,
                'results': final_results,
                'stats': stats,
                'result_image': f'/api/result_image/{result_filename}'
            })

    stats = {'RipeBlueBerry': 0, 'Semi-RipeBlueBerry': 0, 'UnripeBlueBerry': 0, 'total': len(final_results)}
    for r in final_results:
        name = r['class_name']
        if name in stats:
            stats[name] += 1

    return jsonify({'success': True, 'results': final_results, 'stats': stats})


@app.route('/api/current_model')
@login_required
def api_current_model():
    model = get_active_model()
    if model:
        return jsonify({
            'success': True,
            'model_name': model['model_name'],
            'model_loaded': is_model_loaded()
        })
    return jsonify({
        'success': True,
        'model_name': '未配置模型',
        'model_loaded': False
    })


@app.route('/api/records')
@login_required
def api_records():
    user_id = session['user_id']
    role = session.get('role', 'user')
    if role == 'admin':
        records = get_user_records()
    else:
        records = get_user_records(user_id)

    result = []
    for r in records:
        result.append({
            'id': r['id'],
            'username': r['username'],
            'image_name': r['image_name'],
            'result_image': r['result_image'],
            'total_count': r['total_count'],
            'ripe_count': r['ripe_count'],
            'semi_ripe_count': r['semi_ripe_count'],
            'unripe_count': r['unripe_count'],
            'conf_threshold': r['conf_threshold'],
            'created_at': r['created_at']
        })
    return jsonify({'success': True, 'records': result})


@app.route('/api/record/<int:record_id>/download')
@login_required
def api_record_download(record_id):
    conn = get_db()
    record = conn.execute("SELECT * FROM detection_records WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    if not record:
        return jsonify({'success': False, 'message': '记录不存在'}), 404

    user_id = session['user_id']
    role = session.get('role', 'user')
    if role != 'admin' and record['user_id'] != user_id:
        return jsonify({'success': False, 'message': '无权访问'}), 403

    results_json = record['results_json']
    if not results_json:
        return jsonify({'success': False, 'message': '该记录没有检测数据'}), 404

    import io
    results_data = json.loads(results_json)
    csv_output = io.StringIO()
    csv_output.write('class_name,confidence,x1,y1,x2,y2\n')
    for r in results_data:
        csv_output.write(f"{r.get('class_name','')},{r.get('confidence','')},{r.get('x1','')},{r.get('y1','')},{r.get('x2','')},{r.get('y2','')}\n")

    csv_output.seek(0)
    return Response(
        csv_output.getvalue().encode('utf-8-sig'),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=detection_{record_id}.csv'}
    )


@app.route('/api/stats')
@login_required
def api_stats():
    stats = get_detection_stats()
    daily = [{'day': d['day'], 'count': d['cnt']} for d in stats['daily_stats']]
    return jsonify({
        'success': True,
        'total_detections': stats['total_detections'],
        'total_ripe': stats['total_ripe'],
        'total_semi_ripe': stats['total_semi_ripe'],
        'total_unripe': stats['total_unripe'],
        'total_boxes': stats['total_boxes'],
        'user_count': stats['user_count'],
        'daily_stats': daily
    })


@app.route('/api/users', methods=['GET'])
@admin_required
def api_users():
    users = get_all_users()
    result = []
    for u in users:
        result.append({
            'id': u['id'],
            'username': u['username'],
            'role': u['role'],
            'created_at': u['created_at']
        })
    return jsonify({'success': True, 'users': result})


@app.route('/api/users', methods=['POST'])
@admin_required
def api_create_user():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'user')
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    if role not in ('user', 'admin'):
        return jsonify({'success': False, 'message': '无效的角色'})
    success, msg = create_user(username, password, role)
    return jsonify({'success': success, 'message': msg})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'})
    if user['role'] == 'admin':
        return jsonify({'success': False, 'message': '不能删除管理员账户'})
    delete_user(user_id)
    return jsonify({'success': True, 'message': '用户已删除'})


@app.route('/api/models', methods=['GET'])
@admin_required
def api_models():
    models = get_all_models()
    result = []
    for m in models:
        result.append({
            'id': m['id'],
            'model_name': m['model_name'],
            'model_path': m['model_path'],
            'is_active': bool(m['is_active']),
            'created_at': m['created_at']
        })
    return jsonify({'success': True, 'models': result, 'loaded': is_model_loaded()})


@app.route('/api/models/upload', methods=['POST'])
@admin_required
def api_upload_model():
    if 'model' not in request.files:
        return jsonify({'success': False, 'message': '请选择模型文件'})
    file = request.files['model']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择模型文件'})
    if not file.filename.endswith('.onnx'):
        return jsonify({'success': False, 'message': '仅支持.onnx格式模型文件'})

    filename = file.filename
    filepath = os.path.join(ONNX_FOLDER, filename)
    file.save(filepath)

    is_active = request.form.get('is_active', '0') == '1'
    save_model_config(filename, filepath, 1 if is_active else 0)
    if is_active:
        load_model(filepath)

    return jsonify({'success': True, 'message': f'模型 {filename} 上传成功'})


@app.route('/api/models/<int:model_id>/activate', methods=['POST'])
@admin_required
def api_activate_model(model_id):
    set_active_model(model_id)
    model = get_active_model()
    if model:
        load_model(model['model_path'])
    return jsonify({'success': True, 'message': '模型已切换'})


@app.route('/api/models/<int:model_id>', methods=['DELETE'])
@admin_required
def api_delete_model(model_id):
    delete_model(model_id)
    return jsonify({'success': True, 'message': '模型已删除'})


# ===== 果园管理 API =====

@app.route('/api/gardens', methods=['GET'])
@login_required
def api_get_gardens():
    role = session.get('role', 'user')
    if role == 'admin':
        gardens = get_all_gardens()
    else:
        gardens = get_gardens_by_user(session['user_id'])
    result = []
    for g in gardens:
        result.append({
            'id': g['id'],
            'user_id': g['user_id'],
            'username': g['username'] if 'username' in g.keys() else '',
            'name': g['name'],
            'location': g['location'],
            'location_id': g['location_id'],
            'plant_date': g['plant_date'],
            'growth_stage': g['growth_stage'],
            'created_at': g['created_at']
        })
    return jsonify({'success': True, 'gardens': result})


@app.route('/api/gardens', methods=['POST'])
@admin_required
def api_create_garden():
    data = request.get_json()
    name = data.get('name', '').strip()
    location = data.get('location', '').strip()
    location_id = data.get('location_id', '')
    plant_date = data.get('plant_date', '')
    growth_stage = data.get('growth_stage', 'dormant')
    if not name or not location:
        return jsonify({'success': False, 'message': '果园名称和地点不能为空'})
    if growth_stage not in ('dormant', 'sprouting', 'flowering', 'fruiting'):
        return jsonify({'success': False, 'message': '无效的生长阶段'})
    ok, msg, garden_id = create_garden(session['user_id'], name, location, location_id, plant_date, growth_stage)
    return jsonify({'success': ok, 'message': msg, 'garden_id': garden_id})


@app.route('/api/gardens/<int:garden_id>', methods=['PUT'])
@admin_required
def api_update_garden(garden_id):
    data = request.get_json()
    ok, msg = update_garden(
        garden_id,
        name=data.get('name'),
        location=data.get('location'),
        location_id=data.get('location_id'),
        plant_date=data.get('plant_date'),
        growth_stage=data.get('growth_stage')
    )
    return jsonify({'success': ok, 'message': msg})


@app.route('/api/gardens/<int:garden_id>', methods=['DELETE'])
@admin_required
def api_delete_garden(garden_id):
    garden = get_garden_by_id(garden_id)
    if not garden:
        return jsonify({'success': False, 'message': '果园不存在'})
    delete_garden(garden_id)
    return jsonify({'success': True, 'message': '果园已删除'})


# ===== 天气数据 API =====

@app.route('/api/weather/<int:garden_id>')
@login_required
def api_get_weather(garden_id):
    garden = get_garden_by_id(garden_id)
    if not garden:
        return jsonify({'success': False, 'message': '果园不存在'}), 404
    
    # 尝试从数据库获取缓存的天气数据
    cached_weather = get_latest_weather(garden_id)
    
    # 如果有缓存且未过期（1小时内），直接返回
    if cached_weather:
        from datetime import datetime
        fetched_at = datetime.strptime(cached_weather['fetched_at'], '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        if (now - fetched_at).seconds < 3600:
            weather_data = json.loads(cached_weather['weather_json'])
            
            # 即使使用缓存数据，也要运行建议引擎生成预警
            from weather.advice_engine import get_agricultural_advice
            from database import get_user_thresholds, is_alert_duplicate
            growth_stage = garden['growth_stage']
            thresholds = get_user_thresholds(garden['user_id'])
            advice = get_agricultural_advice(weather_data, growth_stage, thresholds)
            
            # 保存 warning 级别的建议为预警记录
            new_alerts = []
            for item in advice:
                if item.get('level') == 'warning':
                    title = item.get('title', '')
                    if not is_alert_duplicate(garden_id, title, hours=24):
                        save_weather_alert(
                            garden_id,
                            alert_title=title,
                            alert_level='warning',
                            alert_content=item.get('content', '')
                        )
                        new_alerts.append(item)
                        print(f"[邮件预警] 新预警: {title}")
                    else:
                        print(f"[邮件预警] 去重跳过: {title} (24h内已存在)")
            
            alerts = get_active_alerts(garden_id)
            print(f"[邮件预警] 活跃预警数: {len(alerts)}, 新预警数: {len(new_alerts)}")
            
            # 发送新生成的预警邮件
            if new_alerts:
                try:
                    from weather.email_sender import send_weather_alert_email
                    from database import get_user_by_id
                    user = get_user_by_id(garden['user_id'])
                    user_email = row_value(user, 'email')
                    if user_email:
                        for alert in new_alerts:
                            success, error = send_weather_alert_email(
                                to_email=user_email,
                                garden_name=garden['name'],
                                alert_title=alert.get('title', ''),
                                alert_content=alert.get('content', ''),
                                weather_data=weather_data
                            )
                            if success:
                                print(f"预警邮件已发送至 {user_email}")
                            else:
                                print(f"预警邮件发送失败: {error}")
                except Exception as e:
                    print(f"发送预警邮件时出错: {str(e)}")
            
            return jsonify({
                'success': True,
                'garden': {
                    'id': garden['id'],
                    'name': garden['name'],
                    'location': garden['location'],
                    'growth_stage': garden['growth_stage']
                },
                'weather': weather_data,
                'alerts': [{'title': a['alert_title'], 'level': a['alert_level'], 'content': a['alert_content']} for a in alerts],
                'advice': advice
            })
    
    # 缓存过期或不存在，调用和风天气 API
    try:
        from weather.api_client import get_full_weather, lookup_city
        
        # 获取 location_id
        location_id = garden['location_id']
        if not location_id:
            # 通过城市名查询 location_id
            city_info = lookup_city(garden['location'])
            if city_info:
                location_id = city_info['location_id']
                # 更新果园的 location_id
                update_garden(garden_id, location_id=location_id)
            else:
                return jsonify({
                    'success': False,
                    'message': f"无法找到城市: {garden['location']}"
                }), 400
        
        # 调用天气 API
        weather_data = get_full_weather(location_id)
        
        if weather_data:
            # 保存到数据库缓存
            save_weather_data(garden_id, json.dumps(weather_data, ensure_ascii=False))
            
            # 保存预警记录到数据库
            api_warnings = weather_data.get('warnings', [])
            if api_warnings:
                for w in api_warnings:
                    save_weather_alert(
                        garden_id,
                        alert_title=w.get('title', ''),
                        alert_level=w.get('level', ''),
                        alert_content=w.get('text', ''),
                        start_time=w.get('startTime'),
                        end_time=w.get('endTime')
                    )
            
            # 生成农业建议（传入用户自定义阈值）
            from weather.advice_engine import get_agricultural_advice
            from database import get_user_thresholds
            growth_stage = garden['growth_stage']
            thresholds = get_user_thresholds(garden['user_id'])
            advice = get_agricultural_advice(weather_data, growth_stage, thresholds)
            
            # 将 warning 级别的建议也保存为预警记录（不依赖官方预警 API）
            from database import is_alert_duplicate
            new_alerts = []
            for item in advice:
                if item.get('level') == 'warning':
                    title = item.get('title', '')
                    # 去重：24小时内相同标题的预警不重复保存
                    if not is_alert_duplicate(garden_id, title, hours=24):
                        save_weather_alert(
                            garden_id,
                            alert_title=title,
                            alert_level='warning',
                            alert_content=item.get('content', '')
                        )
                        new_alerts.append(item)
                        print(f"[邮件预警] 新预警: {title}")
                    else:
                        print(f"[邮件预警] 去重跳过: {title} (24h内已存在)")
            
            alerts = get_active_alerts(garden_id)
            print(f"[邮件预警] 活跃预警数: {len(alerts)}, 新预警数: {len(new_alerts)}")
            
            # 检查是否有新预警，如果有则发送邮件通知（仅发送新生成的预警）
            if new_alerts:
                try:
                    from weather.email_sender import send_weather_alert_email
                    from database import get_user_by_id
                    
                    # 获取果园管理者的邮箱
                    user = get_user_by_id(garden['user_id'])
                    user_email = row_value(user, 'email')
                    if user_email:
                        # 仅发送新生成的预警
                        for alert in new_alerts:
                            success, error = send_weather_alert_email(
                                to_email=user_email,
                                garden_name=garden['name'],
                                alert_title=alert.get('title', ''),
                                alert_content=alert.get('content', ''),
                                weather_data=weather_data
                            )
                            if success:
                                print(f"预警邮件已发送至 {user_email}")
                            else:
                                print(f"预警邮件发送失败: {error}")
                except Exception as e:
                    print(f"发送预警邮件时出错: {str(e)}")
            
            return jsonify({
                'success': True,
                'garden': {
                    'id': garden['id'],
                    'name': garden['name'],
                    'location': garden['location'],
                    'growth_stage': garden['growth_stage']
                },
                'weather': weather_data,
                'alerts': [{'title': a['alert_title'], 'level': a['alert_level'], 'content': a['alert_content']} for a in alerts],
                'advice': advice
            })
        else:
            return jsonify({
                'success': False,
                'message': '获取天气数据失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取天气数据失败: {str(e)}'
        }), 500


# ===== 检查所有果园预警（页面加载时调用） =====

@app.route('/api/weather/check-all')
@login_required
def api_check_all_gardens():
    """检查当前用户所有果园的预警，有新预警则发送邮件"""
    from database import get_gardens_by_user, get_user_thresholds, is_alert_duplicate, get_user_by_id
    from weather.advice_engine import get_agricultural_advice
    from weather.email_sender import send_weather_alert_email
    
    user = get_user_by_id(session['user_id'])
    user_email = row_value(user, 'email')
    if not user_email:
        return jsonify({'success': True, 'message': '用户未设置邮箱', 'sent': 0})
    
    gardens = get_gardens_by_user(session['user_id'])
    sent_count = 0
    
    for garden in gardens:
        cached_weather = get_latest_weather(garden['id'])
        if not cached_weather:
            continue
        
        weather_data = json.loads(cached_weather['weather_json'])
        thresholds = get_user_thresholds(garden['user_id'])
        advice = get_agricultural_advice(weather_data, garden['growth_stage'], thresholds)
        
        for item in advice:
            if item.get('level') == 'warning':
                title = item.get('title', '')
                if not is_alert_duplicate(garden['id'], title, hours=24):
                    save_weather_alert(
                        garden['id'],
                        alert_title=title,
                        alert_level='warning',
                        alert_content=item.get('content', '')
                    )
                    success, error = send_weather_alert_email(
                        to_email=user_email,
                        garden_name=garden['name'],
                        alert_title=title,
                        alert_content=item.get('content', ''),
                        weather_data=weather_data
                    )
                    if success:
                        sent_count += 1
                        print(f"[邮件预警] 已发送 {garden['name']} - {title} 至 {user_email}")
                    else:
                        print(f"[邮件预警] 发送失败 {garden['name']} - {title}: {error}")
    
    return jsonify({'success': True, 'sent': sent_count})


if __name__ == '__main__':
    init_db()
    from database import ensure_thresholds_table
    ensure_thresholds_table()
    model = get_active_model()
    if model:
        load_model(model['model_path'])
    
    # 服务器启动时：清除历史预警，重新检测并发送
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        import sqlite3
        conn = sqlite3.connect('blueberry.db')
        conn.execute("DELETE FROM weather_alerts")
        conn.commit()
        conn.close()
        print("[启动检查] 已清除历史预警记录")
        
        try:
            from database import get_gardens_by_user, get_user_thresholds, get_user_by_id
            from weather.advice_engine import get_agricultural_advice
            from weather.email_sender import send_weather_alert_email
            
            # 获取所有用户的果园
            conn = sqlite3.connect('blueberry.db')
            conn.row_factory = sqlite3.Row
            users = conn.execute("SELECT id, email FROM users WHERE email IS NOT NULL AND email != ''").fetchall()
            conn.close()
            
            for user_row in users:
                user = dict(user_row)
                gardens = get_gardens_by_user(user['id'])
                for garden in gardens:
                    cached = get_latest_weather(garden['id'])
                    if not cached:
                        continue
                    weather_data = json.loads(cached['weather_json'])
                    thresholds = get_user_thresholds(garden['user_id'])
                    advice = get_agricultural_advice(weather_data, garden['growth_stage'], thresholds)
                    
                    for item in advice:
                        if item.get('level') == 'warning':
                            title = item.get('title', '')
                            save_weather_alert(
                                garden['id'],
                                alert_title=title,
                                alert_level='warning',
                                alert_content=item.get('content', '')
                            )
                            success, error = send_weather_alert_email(
                                to_email=user['email'],
                                garden_name=garden['name'],
                                alert_title=title,
                                alert_content=item.get('content', ''),
                                weather_data=weather_data
                            )
                            if success:
                                print(f"[启动检查] 已发送 {garden['name']} - {title} 至 {user['email']}")
                            else:
                                print(f"[启动检查] 发送失败 {garden['name']} - {title}: {error}")
        except Exception as e:
            print(f"[启动检查] 预警检测出错: {str(e)}")
    
    server_port = get_dev_server_port()
    print("蓝莓检测系统启动中...")
    print(f"访问地址: http://127.0.0.1:{server_port}")
    print("默认管理员账号: admin / admin123")
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(1.5, lambda: webbrowser.open(f'http://127.0.0.1:{server_port}/')).start()
    app.run(debug=True, host='0.0.0.0', port=server_port)
