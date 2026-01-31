from PIL import Image

def crop_image_to_size(input_path, output_path, target_width, target_height):
    """
    将图片裁剪为指定尺寸
    
    参数:
    input_path: 输入图片路径
    output_path: 输出图片路径
    target_width: 目标宽度
    target_height: 目标高度
    """
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 计算裁剪区域（居中裁剪）
            original_width, original_height = img.size
            
            # 计算目标宽高比和原始宽高比
            target_ratio = target_width / target_height
            original_ratio = original_width / original_height
            
            # 根据比例决定裁剪方式
            if original_ratio > target_ratio:
                # 原始图片更宽，按高度裁剪宽度
                new_width = int(target_ratio * original_height)
                left = (original_width - new_width) // 2
                right = left + new_width
                top = 0
                bottom = original_height
            else:
                # 原始图片更高，按宽度裁剪高度
                new_height = int(original_width / target_ratio)
                top = (original_height - new_height) // 2
                bottom = top + new_height
                left = 0
                right = original_width
            
            # 裁剪图片
            cropped_img = img.crop((left, top, right, bottom))
            
            # 调整到目标尺寸
            resized_img = cropped_img.resize((target_width, target_height))
            
            # 保存裁剪后的图片
            resized_img.save(output_path)
            print(f"图片已成功裁剪并保存至: {output_path}")
            
    except Exception as e:
        print(f"处理图片时出错: {e}")

# 使用示例
if __name__ == "__main__":
    # 输入图片路径（请替换为你的图片路径）
    input_image_path = "RawPictures\lucky_talk_show2.png"
    # 输出图片路径
    output_image_path = "VirtualPictures\lucky_talk_show_1280p.png"
    # 目标尺寸：720x1280（宽 x 高）
    target_width = 720
    target_height = 1280
    
    crop_image_to_size(input_image_path, output_image_path, target_width, target_height)