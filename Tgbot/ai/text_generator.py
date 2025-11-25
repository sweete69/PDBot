import requests
import json

HF_TOKEN = "8229333698:AAGcU3pYqoI-PNLTn4ZdUHLqu4kl4yJQ5fQ"
API_URL = "https://api-inference.huggingface.co/models/gpt2"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_text(prompt: str, style: str = "description") -> str | None:
    """
    Генерация текста по запросу
    """
    try:
        if style == "description":
            enhanced_prompt = f"Создай подробное описание товара для маркетплейса: {prompt}. Опиши характеристики, преимущества и особенности использования."
        else:
            enhanced_prompt = f"Создай рекламный текст для баннера: {prompt}. Текст должен быть ярким, привлекательным и побуждать к покупке."
        
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        print(f"Отправка запроса к API с промптом: {enhanced_prompt}")
        
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        
        # Проверяем статус ответа
        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        print(f"Получен ответ от API: {result}")
        
        # Обрабатываем разные форматы ответа
        if isinstance(result, list) and len(result) > 0:
            if 'generated_text' in result[0]:
                generated_text = result[0]['generated_text']
                # Убираем исходный промпт из результата, если он есть
                if generated_text.startswith(enhanced_prompt):
                    generated_text = generated_text[len(enhanced_prompt):].strip()
                return generated_text
            else:
                # Если ответ содержит просто текст
                return str(result[0])
        elif isinstance(result, dict) and 'generated_text' in result:
            return result['generated_text']
        else:
            print(f"Неожиданный формат ответа: {result}")
            return None
            
    except requests.exceptions.Timeout:
        print("Таймаут при запросе к API")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return None
    except Exception as e:
        print(f"Общая ошибка при генерации текста: {e}")
        return None