"""
🎨 IMAGE CREATOR - Generate Images from Text
Using HTML Canvas & Custom Graphics
"""

import os
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
import base64
import json
from datetime import datetime

class ImageCreator:
    def __init__(self):
        self.fonts = self.load_fonts()
        self.colors = {
            "primary": ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6"],
            "background": ["#1a1a2e", "#16213e", "#0f3460", "#1f4068"],
            "text": ["#ffffff", "#ecf0f1", "#bdc3c7"]
        }
        self.templates = self.load_templates()
    
    def load_fonts(self):
        """Load available fonts"""
        fonts = {}
        
        # Try to load system fonts
        try:
            # Windows fonts
            if os.name == 'nt':
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf"
                ]
            # Linux fonts
            else:
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
                ]
            
            for path in font_paths:
                if os.path.exists(path):
                    fonts["regular"] = path
                    break
        except:
            pass
        
        # Fallback to default
        if not fonts:
            try:
                fonts["regular"] = ImageFont.load_default()
            except:
                pass
        
        return fonts
    
    def load_templates(self):
        """Load image templates"""
        return {
            "quote": {
                "layout": "centered",
                "background": "gradient",
                "font_size": 40,
                "padding": 50
            },
            "info": {
                "layout": "header_content",
                "background": "solid",
                "font_size": 30,
                "padding": 30
            },
            "instruction": {
                "layout": "step_by_step",
                "background": "pattern",
                "font_size": 28,
                "padding": 40
            },
            "concept": {
                "layout": "mindmap",
                "background": "dark",
                "font_size": 32,
                "padding": 50
            }
        }
    
    def detect_image_type(self, text: str) -> str:
        """Detect appropriate image type from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["উক্তি", "বাণী", "quote", "saying"]):
            return "quote"
        elif any(word in text_lower for word in ["তথ্য", "জ্ঞান", "information", "knowledge"]):
            return "info"
        elif any(word in text_lower for word in ["ধাপ", "নির্দেশ", "step", "instruction"]):
            return "instruction"
        elif any(word in text_lower for word in ["ধারণা", "কনসেপ্ট", "concept", "idea"]):
            return "concept"
        else:
            return "info"  # Default
    
    def create_gradient_background(self, width: int, height: int) -> Image:
        """Create gradient background"""
        # Create gradient from random colors
        color1 = random.choice(self.colors["background"])
        color2 = random.choice(self.colors["primary"])
        
        # Convert hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # Create gradient
        base = Image.new('RGB', (width, height), rgb1)
        draw = ImageDraw.Draw(base)
        
        # Draw gradient lines
        for y in range(height):
            ratio = y / height
            r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
            g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
            b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return base
    
    def create_quote_image(self, text: str, author: str = None) -> Image:
        """Create quote image"""
        width, height = 800, 600
        
        # Create background
        bg = self.create_gradient_background(width, height)
        draw = ImageDraw.Draw(bg)
        
        # Try to load font
        try:
            font_path = self.fonts.get("regular")
            if isinstance(font_path, str):
                font = ImageFont.truetype(font_path, 36)
            else:
                font = font_path
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        lines = textwrap.wrap(text, width=30)
        
        # Calculate text position
        total_text_height = len(lines) * 50
        start_y = (height - total_text_height) // 2
        
        # Draw quote marks
        draw.text((50, start_y - 60), "❝", fill="white", font=font)
        draw.text((width - 100, start_y + total_text_height + 20), "❞", fill="white", font=font)
        
        # Draw each line
        for i, line in enumerate(lines):
            # Calculate line width
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            
            # Center the line
            x = (width - line_width) // 2
            y = start_y + (i * 50)
            
            # Draw text with shadow
            draw.text((x+2, y+2), line, fill="black", font=font)
            draw.text((x, y), line, fill="white", font=font)
        
        # Draw author if provided
        if author:
            author_text = f"- {author}"
            author_bbox = draw.textbbox((0, 0), author_text, font=font)
            author_width = author_bbox[2] - author_bbox[0]
            author_x = width - author_width - 50
            author_y = height - 80
            
            draw.text((author_x, author_y), author_text, fill="rgba(255,255,255,0.8)", font=font)
        
        # Add decoration
        draw.rectangle([(40, 40), (width-40, height-40)], outline="white", width=2)
        
        return bg
    
    def create_info_image(self, title: str, content: str, items: list = None) -> Image:
        """Create information image"""
        width, height = 800, 600
        
        # Create background
        bg_color = random.choice(self.colors["background"])
        bg = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(bg)
        
        # Try to load font
        try:
            font_path = self.fonts.get("regular")
            if isinstance(font_path, str):
                title_font = ImageFont.truetype(font_path, 40)
                content_font = ImageFont.truetype(font_path, 28)
            else:
                title_font = font_path
                content_font = font_path
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
        
        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = 50
        
        draw.rectangle([(title_x-20, title_y-10), (title_x+title_width+20, title_y+50)], 
                      fill=random.choice(self.colors["primary"]))
        draw.text((title_x, title_y), title, fill="white", font=title_font)
        
        # Draw content
        content_lines = textwrap.wrap(content, width=40)
        content_y = title_y + 80
        
        for i, line in enumerate(content_lines[:8]):  # Limit to 8 lines
            line_y = content_y + (i * 40)
            draw.text((50, line_y), f"• {line}", fill="white", font=content_font)
        
        # Draw items if provided
        if items:
            items_y = content_y + (min(len(content_lines), 8) * 40) + 30
            draw.text((50, items_y), "Key Points:", fill=random.choice(self.colors["primary"]), font=content_font)
            
            for i, item in enumerate(items[:5]):  # Limit to 5 items
                item_y = items_y + 30 + (i * 35)
                draw.text((70, item_y), f"✓ {item}", fill="#bdc3c7", font=content_font)
        
        # Add border
        draw.rectangle([(20, 20), (width-20, height-20)], outline="white", width=3)
        
        return bg
    
    def create_instruction_image(self, title: str, steps: list) -> Image:
        """Create step-by-step instruction image"""
        width, height = 800, 600
        
        # Create background with pattern
        bg = Image.new('RGB', (width, height), "#1a1a2e")
        draw = ImageDraw.Draw(bg)
        
        # Add subtle pattern
        for x in range(0, width, 40):
            for y in range(0, height, 40):
                if (x + y) % 80 == 0:
                    draw.rectangle([(x, y), (x+20, y+20)], 
                                  fill=random.choice(self.colors["primary"]) + "20")
        
        # Load fonts
        try:
            font_path = self.fonts.get("regular")
            if isinstance(font_path, str):
                title_font = ImageFont.truetype(font_path, 36)
                step_font = ImageFont.truetype(font_path, 28)
                number_font = ImageFont.truetype(font_path, 32)
            else:
                title_font = font_path
                step_font = font_path
                number_font = font_path
        except:
            title_font = ImageFont.load_default()
            step_font = ImageFont.load_default()
            number_font = ImageFont.load_default()
        
        # Draw title
        draw.text((50, 30), title, fill="white", font=title_font)
        draw.line([(50, 80), (width-50, 80)], fill=random.choice(self.colors["primary"]), width=3)
        
        # Draw steps
        start_y = 100
        step_height = 90
        
        for i, step in enumerate(steps[:5]):  # Limit to 5 steps
            step_y = start_y + (i * step_height)
            
            # Draw step number circle
            circle_center = (80, step_y + 30)
            circle_radius = 25
            draw.ellipse([(circle_center[0]-circle_radius, circle_center[1]-circle_radius),
                         (circle_center[0]+circle_radius, circle_center[1]+circle_radius)],
                        fill=random.choice(self.colors["primary"]))
            
            # Draw step number
            draw.text((circle_center[0]-8, circle_center[1]-12), 
                     str(i+1), fill="white", font=number_font)
            
            # Draw step text
            step_lines = textwrap.wrap(step, width=35)
            for j, line in enumerate(step_lines):
                draw.text((130, step_y + (j * 25)), line, fill="white", font=step_font)
            
            # Draw step connector
            if i < len(steps[:5]) - 1:
                draw.line([(80, step_y + 55), (80, step_y + step_height - 15)], 
                         fill=random.choice(self.colors["primary"]) + "80", width=2)
        
        return bg
    
    def generate_from_text(self, text: str) -> Dict:
        """Main function to generate image from text"""
        image_type = self.detect_image_type(text)
        
        # Extract information from text
        lines = text.split('.')
        title = lines[0][:30] if lines[0] else "Generated Image"
        content = '.'.join(lines[1:3])[:200] if len(lines) > 1 else text[:200]
        
        # Generate image based on type
        if image_type == "quote":
            image = self.create_quote_image(text, "MASTER 🪓")
        elif image_type == "instruction":
            steps = [line.strip() for line in lines[:5] if line.strip()]
            image = self.create_instruction_image(title, steps)
        else:  # info or concept
            items = [line.strip() for line in lines[1:6] if len(line.strip()) > 10]
            image = self.create_info_image(title, content, items)
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.read()).decode()
        
        result = {
            "type": image_type,
            "title": title,
            "text": text[:500],
            "image_base64": f"data:image/png;base64,{img_str}",
            "dimensions": image.size,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def save_image(self, image_data: Dict, filename: str = None) -> str:
        """Save image to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"
        
        # Extract base64 data
        img_data = image_data["image_base64"].split(",")[1]
        img_bytes = base64.b64decode(img_data)
        
        # Save to file
        filepath = f"data/images/{filename}"
        os.makedirs("data/images", exist_ok=True)
        
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        
        return filepath