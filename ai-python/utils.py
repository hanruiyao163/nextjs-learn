import numpy as np
from PIL import ImageDraw, ImageFont


def generate_random_color():
    return tuple(np.random.randint(0, 255, size=3))


def draw_boxes(draw:ImageDraw, box, label_text, score, color, font="", size=25):
    # draw = ImageDraw.Draw(image)

    font = ImageFont.load_default(size) if not font else ImageFont.truetype(font, size)
    (left, top, right, bottom) = font.getbbox("getbbox")

    draw.rectangle(box, outline=color, width=3)
    text_bbox = draw.textbbox((box[0], box[1]), f"{label_text}: {score:.2f}", font=font)
    draw.rectangle((text_bbox[0], text_bbox[1] - top, text_bbox[2], text_bbox[3] - top), fill=color)
    draw.text((box[0], box[1] - top), f"{label_text}: {score:.2f}", fill="white", font=font)



if __name__ == "__main__":
    print(generate_random_color())
