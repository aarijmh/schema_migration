
import cv2
import numpy as np
import pytesseract
import torch
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image
import os

# Config
input_folder = "input_images"
output_folder = "output_images"
os.makedirs(output_folder, exist_ok=True)

# Load Stable Diffusion Inpainting model
pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
).to("cuda")

pytesseract.pytesseract.tesseract_cmd = "tesseract"

def detect_watermark_mask(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
    mask = np.zeros_like(gray)

    # Text detection
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 50 and data['text'][i].strip() != "":
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

    # Logo detection (edges + contours)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 500 < area < 50000:
            cv2.drawContours(mask, [cnt], -1, 255, -1)

    return mask

def inpaint_with_sd(image_path, mask):
    image = Image.open(image_path).convert("RGB")
    mask_pil = Image.fromarray(mask).convert("RGB")

    # Prompt for realistic restoration
    prompt = "restore original background, remove watermark"
    result = pipe(prompt=prompt, image=image, mask_image=mask_pil).images[0]
    return result

# Process all images
for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        img_path = os.path.join(input_folder, filename)
        img_cv = cv2.imread(img_path)
        mask = detect_watermark_mask(img_cv)
        result_img = inpaint_with_sd(img_path, mask)
        result_img.save(os.path.join(output_folder, filename))
        print(f"Processed: {filename}")

print("✅ AI-powered watermark removal completed.")
