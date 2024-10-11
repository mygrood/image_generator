import json
import os
import sys
import time
import requests
import base64

class Text2ImageAPI:
    API_URL = 'https://api-key.fusionbrain.ai/'
    API_KEY = '1FAF8A96A0CB8313677DE079B96E04CA'
    SECRET_KEY = 'C0ABF6FE57699F4D7A6E02D4F80C5BFC'

    # Стили для генерации
    STYLES = [
        {"name": "DEFAULT", "title": "Свой стиль"},
        {"name": "UHD", "title": "Детальное фото"},
        {"name": "ANIME", "title": "Аниме"},
        {"name": "KANDINSKY", "title": "Кандинский"}
    ]

    def __init__(self):
        self.AUTH_HEADERS = {
            'X-Key': f'Key {self.API_KEY}',
            'X-Secret': f'Secret {self.SECRET_KEY}',
        }

    def get_model(self):
        response = requests.get(f"{self.API_URL}key/api/v1/models", headers=self.AUTH_HEADERS)
        return response.json()[0]['id']

    def generate(self, prompt, model, style='DEFAULT', images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt,
                "style": style
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }

        try:
            response = requests.post(f"{self.API_URL}key/api/v1/text2image/run", headers=self.AUTH_HEADERS, files=data, timeout=30)
            response.raise_for_status()
            return response.json()['uuid']

        except requests.exceptions.Timeout:
            print("Ошибка: Тайм-аут при попытке соединения с API.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            if response is not None:
                print(f"Статус ответа: {response.status_code}")
                print(f"Ответ от API: {response.text}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None

    def check_generation(self, request_id, attempts=10, delay=10):
        for _ in range(attempts):
            response = requests.get(f"{self.API_URL}key/api/v1/text2image/status/{request_id}", headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']
            time.sleep(delay)
        return None

    import os
    import base64

    def save_image(self, image_data, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        directory = os.path.join(script_dir, "GENERATED IMAGES")
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, filename)

        try:
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(image_data))
            print(f"Файл сохранён как: {file_path}")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")


def main():
    api = Text2ImageAPI()
    model_id = api.get_model()

    # Вывод списка стилей
    print("Выберите стиль:")
    for idx, style in enumerate(api.STYLES, 1):
        print(f"{idx}. {style['title']}")

    # Ввод стиля от пользователя
    style_index = int(input("Введите номер стиля: ")) - 1
    style = api.STYLES[style_index]["name"]

    print("Введите список промптов, разделенных ';':")
    prompt_input = input().strip()
    prompts = prompt_input.split(';')
    prompts = [prompt.strip() for prompt in prompts]

    base_name = input("Введите базовое имя файлов для сохранения изображений: ")

    for index, prompt in enumerate(prompts):
        filename = f"{base_name}_{index + 1}.png"
        print(f"Генерация изображения для промпта: '{prompt}' в стиле '{style}'")
        uuid = api.generate(prompt, model_id, style)

        if uuid:
            print(f"UUID генерации: {uuid}")
        else:
            print("Не удалось начать генерацию.")
            continue

        images = api.check_generation(uuid)
        if images:
            api.save_image(images[0], filename)
            print(f"Изображение сохранено как '{filename}'")
        else:
            print("Не удалось получить изображение.")


if __name__ == "__main__":
    main()
