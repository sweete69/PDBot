import requests
import os

HF_TOKEN = "8229333698:AAGcU3pYqoI-PNLTn4ZdUHLqu4kl4yJQ5fQ"
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_image(prompt: str, output_path: str = "banner.png") -> str | None:
    """
    Генерация изображения по тексту
    """
    enhanced_prompt = f"professional product photo: {prompt}, clean background, high quality, advertising banner"
    
    payload = {
        "inputs": enhanced_prompt
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
        response.raise_for_status()
        
        if response.content:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        else:
            return None
            
    except Exception as e:
        print(f"Ошибка генерации изображения: {e}")
        return None

def generate_image_from_photo(photo_path: str, prompt: str, output_path: str = "banner.png") -> str | None:
    """
    Генерация изображения на основе фото пользователя
    """
    try:
        with open(photo_path, "rb") as f:
            files = {"image": f}
            data = {"inputs": f"advertising banner, {prompt}, professional photo"}
            
            response = requests.post(API_URL, headers=HEADERS, files=files, data=data, timeout=180)
            response.raise_for_status()
            
            if response.content:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            else:
                return None
                
    except Exception as e:
        print(f"Ошибка генерации изображения из фото: {e}")
        return None