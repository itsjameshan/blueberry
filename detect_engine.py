import numpy as np
from PIL import Image
import json
import os

CLASS_NAMES = {0: 'RipeBlueBerry', 1: 'Semi-RipeBlueBerry', 2: 'UnripeBlueBerry'}

_ort_session = None
_model_loaded = False


def load_model(model_path):
    global _ort_session, _model_loaded
    if not os.path.exists(model_path):
        _model_loaded = False
        return False
    try:
        import onnxruntime as ort
        _ort_session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        _model_loaded = True
        return True
    except Exception:
        _model_loaded = False
        return False


def is_model_loaded():
    return _model_loaded


def preprocess_image(image_path, target_size=640):
    img = Image.open(image_path).convert('RGB')
    orig_w, orig_h = img.size
    img_resized = img.resize((target_size, target_size), Image.LANCZOS)
    img_array = np.array(img_resized, dtype=np.float32) / 255.0
    img_array = np.transpose(img_array, (2, 0, 1))
    img_array = np.expand_dims(img_array, axis=0)
    return img_array, orig_w, orig_h, target_size


def postprocess(output, orig_w, orig_h, target_size, conf_threshold=0.5, iou_threshold=0.45):
    results = []
    predictions = np.squeeze(output[0]) if isinstance(output, list) else np.squeeze(output)

    if predictions.ndim == 1:
        predictions = predictions.reshape(1, -1)

    predictions = np.transpose(predictions)

    scale_x = orig_w / target_size
    scale_y = orig_h / target_size

    detections = []
    for pred in predictions:
        if len(pred) < 6:
            continue
        x_center, y_center, width, height = pred[:4]
        class_scores = pred[4:]
        class_id = int(np.argmax(class_scores))
        score = float(class_scores[class_id])

        if score < conf_threshold:
            continue

        x1 = (x_center - width / 2) * scale_x
        y1 = (y_center - height / 2) * scale_y
        x2 = (x_center + width / 2) * scale_x
        y2 = (y_center + height / 2) * scale_y

        detections.append({
            'bbox': [float(x1), float(y1), float(x2), float(y2)],
            'score': float(score),
            'class_id': class_id
        })

    detections = _nms(detections, iou_threshold)

    for det in detections:
        class_id = det['class_id']
        results.append({
            'class_name': CLASS_NAMES.get(class_id, f'class_{class_id}'),
            'class_id': class_id,
            'confidence': round(det['score'], 4),
            'bbox': [round(v, 2) for v in det['bbox']],
            'x1': round(det['bbox'][0], 2),
            'y1': round(det['bbox'][1], 2),
            'x2': round(det['bbox'][2], 2),
            'y2': round(det['bbox'][3], 2)
        })

    return results


def _nms(detections, iou_threshold):
    if len(detections) == 0:
        return detections
    detections = sorted(detections, key=lambda x: x['score'], reverse=True)
    keep = []
    while len(detections) > 0:
        keep.append(detections[0])
        if len(detections) == 1:
            break
        remaining = []
        for det in detections[1:]:
            if _iou(detections[0]['bbox'], det['bbox']) < iou_threshold:
                remaining.append(det)
        detections = remaining
    return keep


def _iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea + 1e-6)


def detect_single_image(image_path, conf_threshold=0.5):
    if not _model_loaded:
        raise RuntimeError("模型未加载，请先加载ONNX模型")

    img_array, orig_w, orig_h, target_size = preprocess_image(image_path, target_size=640)
    input_name = _ort_session.get_inputs()[0].name
    output = _ort_session.run(None, {input_name: img_array})
    results = postprocess(output[0], orig_w, orig_h, target_size, conf_threshold)

    stats = {
        'RipeBlueBerry': 0,
        'Semi-RipeBlueBerry': 0,
        'UnripeBlueBerry': 0,
        'total': len(results)
    }
    for r in results:
        name = r['class_name']
        if name in stats:
            stats[name] += 1

    return results, stats


def draw_boxes(image_path, results, output_path):
    try:
        import cv2
    except ImportError:
        from PIL import ImageDraw, ImageFont
        img = Image.open(image_path).convert('RGB')
        draw = ImageDraw.Draw(img)
        colors = {
            'RipeBlueBerry': '#6A0DAD',
            'Semi-RipeBlueBerry': '#8B5CF6',
            'UnripeBlueBerry': '#A78BFA'
        }
        for r in results:
            hex_color = colors.get(r['class_name'], '#6A0DAD')
            color = tuple(int(hex_color[i+1:i+3], 16) for i in (0, 2, 4))
            draw.rectangle([r['x1'], r['y1'], r['x2'], r['y2']], outline=color, width=3)
            draw.text((r['x1'], r['y1'] - 12), f"{r['class_name']} {r['confidence']:.2f}", fill=color)
        img.save(output_path)
        return

    img = cv2.imread(image_path)
    if img is None:
        return
    colors = {
        'RipeBlueBerry': (173, 13, 106),
        'Semi-RipeBlueBerry': (246, 92, 139),
        'UnripeBlueBerry': (250, 139, 167),
    }
    for r in results:
        x1, y1, x2, y2 = int(r['x1']), int(r['y1']), int(r['x2']), int(r['y2'])
        color = colors.get(r['class_name'], (173, 13, 106))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f"{r['class_name']} {r['confidence']:.2f}"
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    cv2.imwrite(output_path, img)


def crop_image(image_path, tile_size=640, overlap=200, output_dir='crop_output'):
    try:
        import cv2
    except ImportError:
        return []

    os.makedirs(output_dir, exist_ok=True)
    img = cv2.imread(image_path)
    if img is None:
        return []
    h, w = img.shape[:2]
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    tiles = []
    stride = tile_size - overlap
    y_starts = list(range(0, max(1, h - overlap), stride))
    x_starts = list(range(0, max(1, w - overlap), stride))

    for y_idx, y in enumerate(y_starts):
        for x_idx, x in enumerate(x_starts):
            x_end = min(x + tile_size, w)
            y_end = min(y + tile_size, h)
            tile = img[y:y_end, x:x_end]
            tile_name = f"{base_name}_tile_{y_idx}_{x_idx}.jpg"
            tile_path = os.path.join(output_dir, tile_name)
            cv2.imwrite(tile_path, tile)
            tiles.append({
                'path': tile_path,
                'name': tile_name,
                'x': x, 'y': y,
                'width': x_end - x,
                'height': y_end - y
            })
    return tiles


def rebuild_results(tiles_results, original_size, tile_size=640, overlap=200, output_path=None, conf_threshold=0.5, iou_threshold=0.45):
    all_detections = []
    for tile_info, detections in tiles_results:
        offset_x = tile_info['x']
        offset_y = tile_info['y']
        for det in detections:
            bbox = det['bbox'].copy()
            bbox[0] += offset_x
            bbox[1] += offset_y
            bbox[2] += offset_x
            bbox[3] += offset_y
            all_detections.append({
                'bbox': bbox,
                'score': det['confidence'],
                'class_id': det['class_id'],
                'class_name': det['class_name']
            })

    all_detections = _nms(all_detections, iou_threshold)

    results = []
    for det in all_detections:
        results.append({
            'class_name': det['class_name'],
            'class_id': det['class_id'],
            'confidence': round(det['score'], 4),
            'bbox': [round(v, 2) for v in det['bbox']],
            'x1': round(det['bbox'][0], 2),
            'y1': round(det['bbox'][1], 2),
            'x2': round(det['bbox'][2], 2),
            'y2': round(det['bbox'][3], 2)
        })

    return results