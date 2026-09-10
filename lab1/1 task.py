import requests
import json

username = "Hosty0"
url = f"https://api.github.com/users/{username}/repos"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    with open("github_repos.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("Данные сохранены в файл 'github_repos.json'.")
else:
    print(f"Ошибка: {response.status_code}")