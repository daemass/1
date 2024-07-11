import os
from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    def __init__(self):
        self.font_path = "C:/Windows/Fonts/malgun.ttf"  # Windows의 기본 한글 폰트 경로
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_announcer_image(self, name):
        img = Image.new('RGB', (400, 400), color='white')
        d = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(self.font_path, 40)
        except IOError:
            print(f"Font file not found: {self.font_path}")
            font = ImageFont.load_default()

        # 간단한 아나운서 이미지 생성 (텍스트만 포함)
        d.text((50, 180), f"아나운서 {name}", font=font, fill='black')

        output_path = os.path.join(self.output_dir, f"{name}_announcer.png")
        img.save(output_path)
        return output_path