import os

root = r"D:/PythonProject/yolo_training_ready"
subs = ["train", "validation"]
nc = 3

for sub in subs:
    img_dir = os.path.join(root, "image", sub)
    label_dir = os.path.join(root, "labels", sub)

    if not os.path.exists(label_dir):
        print(f"❌ 缺失文件夹：{label_dir}")
        continue

    img_list = [f[:-4] for f in os.listdir(img_dir) if f.endswith((".jpg", ".png", ".jpeg"))]
    label_list = [f[:-4] for f in os.listdir(label_dir) if f.endswith(".txt")]

    # 有图无标签
    no_label = set(img_list) - set(label_list)
    if no_label:
        print(f"\n{sub} 图片无对应标签：{len(no_label)} 张")
        for name in list(no_label)[:10]:
            print("  -", name)

    # 有标签无图
    no_img = set(label_list) - set(img_list)
    if no_img:
        print(f"\n{sub} 标签无对应图片：{len(no_img)} 个")

    # 校验txt内容
    for txt in os.listdir(label_dir):
        txt_path = os.path.join(label_dir, txt)
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                print(f"⚠️ 空标签文件：{txt}")
                continue
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 5:
                    print(f"⚠️ {txt} 字段数量错误：{line}")
                    continue
                cls = int(parts[0])
                if cls < 0 or cls >= nc:
                    print(f"⚠️ {txt} 类别ID越界：{cls}")