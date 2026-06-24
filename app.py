from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, Response
from werkzeug.security import check_password_hash
from functools import wraps
import os
import json
import webbrowser
import threading
# 新增跨域模块
from flask_cors import CORS

from database import (
    init_db, get_user_by_username, get_user_by_id, create_user, delete_user,
    get_all_users, save_detection_record, get_user_records, get_detection_stats,
    save_model_config, get_active_model, get_all_models, set_active_model, delete_model
)
from detect_engine import (
    load_model, is_model_loaded, detect_single_image, draw_boxes,
    crop_image, rebuild_results, CLASS_NAMES, preprocess_image, postprocess
)
import detect_engine

app = Flask(__name__, template_folder='static')
app.secret_key = 'blueberry_detection_secret_key_2026'
# 全局跨域配置：允许小程序携带 Cookie，保留登录态
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
# Session 适配小程序，登录 7 天有效，不丢失登录
app.config['PERMANENT_SESSION_LIFETIME'] = 3600*24*7
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False
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
            return redirect(url_for('login_page'))
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


@app.route('/')
def root():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


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
    session.clear()
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


if __name__ == '__main__':
    init_db()
    model = get_active_model()
    if model:
        print(f"找到激活模型: {model['model_name']}")
        print(f"模型路径: {model['model_path']}")
        if os.path.exists(model['model_path']):
            print("模型文件存在，开始加载...")
            success = load_model(model['model_path'])
            if success:
                print("✅ 模型加载成功！")
            else:
                print("❌ 模型加载失败！")
        else:
            print(f"❌ 模型文件不存在: {model['model_path']}")
    else:
        print("⚠️ 未找到激活模型，检查 database.py 中 init_db 是否正确初始化")
        print(f"ONNX_FOLDER 目录内容: {os.listdir(ONNX_FOLDER) if os.path.exists(ONNX_FOLDER) else '目录不存在'}")
    print("蓝莓检测系统启动中...")
    print("本地地址: http://127.0.0.1:5000")
    print("局域网地址: http://10.77.56.49:5000")
    print("默认管理员账号: admin / admin123")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)