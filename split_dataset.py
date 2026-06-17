import os
import shutil
from sklearn.model_selection import train_test_split

# ---------------------- 配置路径（改成你自己的） ----------------------
# 原始图片文件夹
img_src_dir = r"D:\pythonProject\bule\BlueberryDCM\images"

# 目标输出文件夹（会自动创建）
train_img_dir = r"D:\pythonProject\bule\BlueberryDCM\images\train"
val_img_dir = r"D:\pythonProject\bule\BlueberryDCM\images\val"
test_img_dir = r"D:\pythonProject\bule\BlueberryDCM\images\test"

# 划分比例：训练:验证:测试 = 8:1:1
test_size_1 = 0.2    # 先分出 20% 作为 验证+测试
test_size_2 = 0.5    # 再把这20%对半分：10%验证、10%测试
random_seed = 42     # 固定随机种子，保证每次划分结果一致

# ---------------------- 自动创建目标文件夹 ----------------------
os.makedirs(train_img_dir, exist_ok=True)
os.makedirs(val_img_dir, exist_ok=True)
os.makedirs(test_img_dir, exist_ok=True)

# ---------------------- 获取所有图片文件名（不带后缀） ----------------------
img_suffix = ('.jpg', '.png', '.jpeg', '.webp')
img_files = [f for f in os.listdir(img_src_dir) if f.lower().endswith(img_suffix)]
img_stems = [os.path.splitext(f)[0] for f in img_files]

# ---------------------- 两次划分实现 8:1:1 ----------------------
# 第一步：80%训练集，20%临时集(验证+测试)
train_stems, temp_stems = train_test_split(
    img_stems,
    test_size=test_size_1,
    random_state=random_seed
)

# 第二步：临时集对半分 → 10%验证、10%测试
val_stems, test_stems = train_test_split(
    temp_stems,
    test_size=test_size_2,
    random_state=random_seed
)

# ---------------------- 移动图片的函数 ----------------------
def move_images(stems, src_img_dir, dst_img_dir):
    for stem in stems:
        # 尝试不同后缀的图片
        for ext in ['.jpg', '.png', '.jpeg', '.webp']:
            img_src = os.path.join(src_img_dir, f"{stem}{ext}")
            if os.path.exists(img_src):
                shutil.move(img_src, os.path.join(dst_img_dir, f"{stem}{ext}"))
                print(f"✅ 已移动: {img_src} → {dst_img_dir}")
                break

# ---------------------- 执行移动 ----------------------
move_images(train_stems, img_src_dir, train_img_dir)
move_images(val_stems, img_src_dir, val_img_dir)
move_images(test_stems, img_src_dir, test_img_dir)

# 输出统计
print("\n🎉 图片按 8:1:1 划分完成！")
print(f"训练集图片数：{len(train_stems)}")
print(f"验证集图片数：{len(val_stems)}")
print(f"测试集图片数：{len(test_stems)}")