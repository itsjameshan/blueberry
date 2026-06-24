import os
from PIL import Image

def pad_and_crop_images_to_640(input_folder, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            img_path = os.path.join(input_folder, filename)
            try:
                with Image.open(img_path) as img:
                    width, height = img.size

                    # 1. 先对图片做黑边填充，让宽高都是640的整数倍
                    new_width = ((width + 639) // 640) * 640
                    new_height = ((height + 639) // 640) * 640

                    # 创建黑底画布，把原图居中贴上去
                    padded_img = Image.new("RGB", (new_width, new_height), (0, 0, 0))
                    paste_x = (new_width - width) // 2
                    paste_y = (new_height - height) // 2
                    padded_img.paste(img, (paste_x, paste_y))

                    # 2. 按640×640无重叠裁剪
                    num_cols = new_width // 640
                    num_rows = new_height // 640

                    for row in range(num_rows):
                        for col in range(num_cols):
                            left = col * 640
                            upper = row * 640
                            right = left + 640
                            lower = upper + 640

                            cropped_img = padded_img.crop((left, upper, right, lower))

                            base_name = os.path.splitext(filename)[0]
                            ext = os.path.splitext(filename)[1]
                            output_filename = f"{base_name}_{row}_{col}{ext}"
                            output_path = os.path.join(output_folder, output_filename)

                            cropped_img.save(output_path)
                            print(f"✅ 已保存: {output_path}")

            except Exception as e:
                print(f"❌ 处理文件 {filename} 时出错: {e}")

# --------------------------
# 请修改为你的实际路径
# --------------------------
input_dir = r"D:\蓝莓数据集\BlueberryDCM\images"
output_dir = r"D:\pythonProject\bule\BlueberryDCM\images"

if __name__ == "__main__":
    pad_and_crop_images_to_640(input_dir, output_dir)
    print("\n🎉 所有图片处理完成！")