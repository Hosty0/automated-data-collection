import requests
import json

TOKEN = "ТОКЕН"

url = "https://cloud-api.yandex.net/v1/disk/resources"

headers = {
    "Authorization": f"OAuth {TOKEN}"
}
# Берем данные из папки (там 2 фото)
params = {
    "path": "disk:/trrp"
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()

    with open("yandex_disk_info.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("Данные сохранены в файл 'yandex_disk_info.json'.")
else:
    print(f"Ошибка {response.status_code}: {response.text}")