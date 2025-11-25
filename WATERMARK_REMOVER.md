# Watermark Remover

AI-powered watermark removal tool using Stable Diffusion inpainting and computer vision techniques.

## Features

- **AI-Powered Inpainting**: Uses Stable Diffusion for realistic background restoration
- **Text Detection**: OCR-based watermark text detection with Tesseract
- **Logo Detection**: Edge detection and contour analysis for logo watermarks
- **Batch Processing**: Process multiple images automatically
- **GPU Acceleration**: CUDA support for faster processing

## Installation

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended)
- Tesseract OCR

### Install Dependencies

```bash
pip install opencv-python numpy pytesseract torch diffusers pillow
```

### Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage

### Setup Directory Structure

```
watermark_remover/
├── remove_watermark.py
├── input_images/          # Place images here
└── output_images/         # Results saved here
```

### Basic Usage

1. Place images in `input_images/` folder
2. Run the script:

```bash
python remove_watermark.py
```

3. Find processed images in `output_images/` folder

### Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)

## How It Works

### 1. Watermark Detection

**Text Detection:**
- Converts image to grayscale
- Applies binary threshold (180)
- Uses Tesseract OCR with 50% confidence threshold
- Creates mask around detected text regions

**Logo Detection:**
- Edge detection using Canny algorithm
- Contour analysis for shapes between 500-50,000 pixels
- Filters potential logo regions

### 2. AI Inpainting

- Uses `runwayml/stable-diffusion-inpainting` model
- Prompt: "restore original background, remove watermark"
- Inpaints masked regions with realistic content
- GPU acceleration with float16 precision

## Configuration

### Model Settings

```python
# Change model (optional)
pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting",  # Alternative model
    torch_dtype=torch.float16
).to("cuda")
```

### Detection Parameters

```python
# Text detection threshold
_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)  # Adjust 180

# OCR confidence
if int(data['conf'][i]) > 50:  # Adjust 50

# Logo size range
if 500 < area < 50000:  # Adjust range
```

### Tesseract Path (Windows)

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Performance

- **GPU Required**: CUDA-compatible GPU recommended
- **Memory**: ~4GB VRAM for Stable Diffusion
- **Speed**: ~10-30 seconds per image (depends on size/GPU)

## Limitations

- Works best on simple watermarks
- Complex overlays may require manual adjustment
- GPU memory limits image resolution
- Detection accuracy varies with watermark style

## Troubleshooting

### Common Issues

**CUDA Out of Memory:**
```python
# Use CPU instead
.to("cpu")
```

**Tesseract Not Found:**
```bash
# Check installation
tesseract --version
```

**Poor Detection:**
- Adjust threshold values
- Try different detection parameters
- Consider manual mask creation

## Requirements

```txt
opencv-python>=4.5.0
numpy>=1.21.0
pytesseract>=0.3.8
torch>=1.11.0
diffusers>=0.10.0
pillow>=8.3.0
```

## License

MIT