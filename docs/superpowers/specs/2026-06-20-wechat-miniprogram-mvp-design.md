# WeChat Mini Program MVP Design

## Goal

Build a standalone WeChat Mini Program MVP for blueberry maturity detection. A user can take or select one blueberry photo, upload it to the existing Flask inference service, and see the total blueberry count plus counts for ripe, semi-ripe, and unripe blueberries.

## Scope

The MVP adds a new mini program frontend under `miniprogram/` and small mini-program-specific API endpoints in the Flask backend. The existing web UI under `static/` remains unchanged.

Included:

- One mini program page for photo capture, upload, detection, and result display.
- Image selection from camera or album through WeChat native APIs.
- Server-side inference using the existing ONNX model and `detect_engine.py`.
- Result summary: total, ripe and harvestable, semi-ripe, and unripe.
- Annotated result image returned by the backend.
- Detection detail list with class name, confidence, and bounding box coordinates.
- Local development configuration for the backend base URL.

Excluded from MVP:

- Real-time video stream inference.
- Running ONNX inference inside the mini program.
- User login, WeChat identity binding, and historical record browsing.
- Admin model management inside the mini program.
- Changes to existing web pages or their JavaScript/CSS.

## Architecture

The mini program is a thin client. It owns the mobile interaction and display, but sends every image to Flask for inference. Flask keeps the model, image preprocessing, postprocessing, box drawing, and file storage responsibilities.

The implementation introduces a `miniprogram/` directory with WeChat project files and one page. It also adds mini API routes in `app.py` that do not require browser session login, so the MVP can be demonstrated from WeChat Developer Tools without building an auth flow first.

## Components

### Mini Program Frontend

Files live under `miniprogram/`.

- `project.config.json`: WeChat Developer Tools project configuration.
- `app.json`: page registration, window style, and permissions.
- `app.js`: global app bootstrap.
- `app.wxss`: shared layout and theme.
- `utils/config.js`: backend base URL, defaulting to local development.
- `utils/api.js`: wrappers around `wx.uploadFile` and response normalization.
- `pages/index/index.wxml`: capture/upload/result UI.
- `pages/index/index.wxss`: page-specific mobile layout.
- `pages/index/index.js`: choose image, upload, render result, retry, preview image.
- `pages/index/index.json`: page title and page options.

### Flask Backend Additions

New routes are added without changing existing web routes:

- `GET /api/mini/health`: returns whether the active model is configured and loaded.
- `POST /api/mini/detect`: accepts one image file and optional `conf`, runs existing detection, writes an annotated result image, and returns mobile-friendly JSON.
- `GET /api/mini/result_image/<filename>`: serves mini program result images.

The backend reuses:

- `detect_single_image` for ONNX inference.
- `draw_boxes` for annotated output image generation.
- `CLASS_NAMES` and existing class labels.

The mini route does not save a `detection_records` row in the MVP because there is no user identity. That keeps the workflow independent from the existing browser session model.

## Data Flow

1. User taps the primary camera button or album button.
2. Mini program calls `wx.chooseMedia` with image-only selection.
3. Mini program stores the temporary local image path and shows a preview.
4. User taps detect.
5. Mini program calls `wx.uploadFile` with field name `image` and form field `conf`.
6. Flask saves the upload to `uploads/mini_<random>.jpg`.
7. Flask runs `detect_single_image`.
8. Flask draws boxes to `results/mini_result_<random>.jpg`.
9. Flask returns JSON with counts, details, and `result_image_url`.
10. Mini program displays the result image and counts.

## API Contract

### `GET /api/mini/health`

Response:

```json
{
  "success": true,
  "model_loaded": true,
  "model_name": "v12best.onnx"
}
```

### `POST /api/mini/detect`

Multipart form:

- `image`: required image file.
- `conf`: optional confidence threshold, default `0.5`.

Success response:

```json
{
  "success": true,
  "summary": {
    "total": 12,
    "ripe": 5,
    "semi_ripe": 4,
    "unripe": 3,
    "harvestable": 5
  },
  "labels": {
    "ripe": "成熟可采",
    "semi_ripe": "半熟",
    "unripe": "未熟"
  },
  "results": [
    {
      "class_name": "RipeBlueBerry",
      "display_name": "成熟可采",
      "confidence": 0.91,
      "bbox": [10.0, 20.0, 80.0, 100.0],
      "x1": 10.0,
      "y1": 20.0,
      "x2": 80.0,
      "y2": 100.0
    }
  ],
  "result_image": "mini_result_abc.jpg",
  "result_image_url": "http://127.0.0.1:5000/api/mini/result_image/mini_result_abc.jpg",
  "conf_threshold": 0.5
}
```

Failure response:

```json
{
  "success": false,
  "message": "模型未加载，请先加载ONNX模型"
}
```

## Error Handling

The mini program shows clear states for:

- Backend unreachable.
- No model loaded.
- Missing image.
- Upload failure.
- Detection failure.
- Empty result, when the model finds zero blueberries.

The backend validates:

- The request includes an `image` file.
- The filename is not empty.
- The confidence threshold is numeric and clamped to a valid range.
- The active model is loaded before inference.

## Testing

Backend tests cover:

- Mini summary mapping from existing model stats.
- Confidence threshold parsing and clamping.
- Missing image request returns a useful error.
- Successful detection route returns the mini API contract when inference and drawing are stubbed.

Mini program tests are not automated in this repo because WeChat Developer Tools is the primary runtime. Verification uses:

- Static inspection of `miniprogram/` project files.
- Manual run in WeChat Developer Tools with domain verification disabled for local development.
- Flask route smoke test with a local image once dependencies are installed.

## Local Development

For local demos:

- Run Flask on `http://127.0.0.1:5000`.
- Open `miniprogram/` in WeChat Developer Tools.
- Set `utils/config.js` base URL to the local Flask URL.
- In WeChat Developer Tools, enable local development settings that skip legal-domain checks.

For real phone or production demos:

- Deploy Flask behind HTTPS.
- Configure the HTTPS backend domain in WeChat Mini Program request, upload, and download legal domain settings.
- Update `utils/config.js` to the HTTPS base URL.

## Risks

- Localhost works in WeChat Developer Tools but not for normal scanned production usage.
- The active ONNX model must be loaded before mini detection works.
- Detection quality depends on the existing trained model and photo quality.
- Large images may upload slowly on mobile networks.

## Acceptance Criteria

- Existing web pages and static assets remain unchanged.
- `miniprogram/` opens as a WeChat Mini Program project.
- A user can choose or take one image.
- The mini program can upload the image to Flask.
- The backend returns total, ripe, semi-ripe, and unripe counts.
- The mini program displays the annotated result image and the summary counts.
- Backend tests for the mini API pass.
