import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description="Export YOLO model to ONNX")
    parser.add_argument("--weights", type=str, required=True, help="Path to YOLO .pt weights")
    parser.add_argument("--output-dir", type=str, default=".", help="Directory to save the ONNX file")
    args = parser.parse_args()

    weights = Path(args.weights).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(weights))
    model.export(format="onnx", dynamic=True, simplify=True, opset=17)

    # Ultralytics saves the ONNX file next to the weights by default.
    onnx_path = weights.with_suffix(".onnx")
    if not onnx_path.exists():
        # Fallback: search the current working directory.
        onnx_path = Path.cwd() / weights.with_suffix(".onnx").name

    if onnx_path.exists():
        dest = output_dir / onnx_path.name
        shutil.move(str(onnx_path), str(dest))
        print(f"Exported ONNX to: {dest}")
    else:
        raise FileNotFoundError("ONNX file not found after export")


if __name__ == "__main__":
    main()