import os
import requests
import random
import json
from datetime import datetime

class VKMusicManager:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.user_info = None
        # User-Agent для Kate Mobile
        self.kate_user_agent = "KateMobileAndroid/51.1-442 (Android 11; SDK 30; arm64-v8a; Samsung SM-G991B; ru_RU)"
        self.headers = {
            'User-Agent': self.kate_user_agent,
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive'
        }
        self.downloads_history = []
        self.load_downloads_history()

    def load_downloads_history(self):
        """Загрузить историю загрузок из файла"""
        try:
            if os.path.exists('downloads_history.json'):
                with open('downloads_history.json', 'r', encoding='utf-8') as f:
                    self.downloads_history = json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке истории загрузок: {e}")
            self.downloads_history = []

    def save_downloads_history(self):
        """Сохранить историю загрузок в файл"""
        try:
            with open('downloads_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.downloads_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении истории загрузок: {e}")

    def add_to_downloads_history(self, audio_info, filepath):
        """Добавить запись в историю загрузок"""
        download_info = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'title': audio_info.get('title', 'Unknown'),
            'artist': audio_info.get('artist', 'Unknown'),
            'duration': audio_info.get('duration', 0),
            'filepath': filepath,
            'file_size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
        }
        self.downloads_history.append(download_info)
        self.save_downloads_history()

    def get_downloads_history(self):
        """Получить историю загрузок"""
        return self.downloads_history

    def clear_downloads_history(self):
        """Очистить историю загрузок"""
        self.downloads_history = []
        self.save_downloads_history()

    def set_token(self, token):
        """Установить токен"""
        self.token = token
        if token and '.' in token:
            parts = token.split('.')
            if len(parts) > 0:
                try:
                    self.user_id = int(parts[0])
                except ValueError:
                    self.user_id = None
        else:
            self.user_id = None

    def load_token_from_file(self, filename='vk_token.txt'):
        """Загрузить токен из файла"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                    if token:
                        self.set_token(token)
                        return True, f"✅ Токен загружен из файла {filename}"
            return False, f"❌ Файл {filename} не найден или пуст"
        except Exception as e:
            return False, f"❌ Ошибка при чтении файла: {e}"

    def save_token_to_file(self, filename='vk_token.txt'):
        """Сохранить токен в файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.token)
            return True, f"✅ Токен сохранен в файл {filename}"
        except Exception as e:
            return False, f"❌ Ошибка при сохранении токена: {e}"

    def check_token_validity(self):
        """Проверить валидность токена"""
        if not self.token:
            return {"valid": False, "error_msg": "Токен не установлен"}
        
        url = "https://api.vk.com/method/users.get"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "fields": "first_name,last_name"
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                self.user_info = data["response"][0]
                # Обновляем user_id из ответа API
                self.user_id = self.user_info.get('id')
                return {"valid": True, "user_info": self.user_info}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"valid": False, "error_msg": error_msg}
                
        except Exception as e:
            return {"valid": False, "error_msg": f"Ошибка запроса: {e}"}

    def get_friends_list(self):
        """Получить список друзей"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/friends.get"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "count": 200,
            "fields": "first_name,last_name,photo_100",
            "order": "name"
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "friends": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_groups_list(self):
        """Получить список групп пользователя"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/groups.get"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "count": 200,
            "extended": 1,
            "fields": "name,photo_100",
            "filter": "groups"
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "groups": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_friend_audio_list(self, friend_id):
        """Получить список аудиозаписей друга"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        url = "https://api.vk.com/method/audio.get"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "count": 200,
            "owner_id": friend_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_group_audio_list(self, group_id):
        """Получить список аудиозаписей группы"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        # Для групп используем отрицательный owner_id
        owner_id = -abs(int(group_id))
        
        url = "https://api.vk.com/method/audio.get"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "count": 200,
            "owner_id": owner_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_my_audio_list(self):
        """Получить список моих аудиозаписей"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/audio.get"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "count": 200,
            "owner_id": self.user_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_playlists(self):
        """Получить список плейлистов"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/audio.getPlaylists"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "owner_id": self.user_id,
            "count": 200
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "playlists": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_playlist_tracks(self, playlist_id):
        """Получить треки из плейлиста"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/audio.get"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "count": 100,
            "album_id": playlist_id,
            "owner_id": self.user_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_recommendations(self):
        """Получить рекомендации через метод audio.getRecommendations"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        url = "https://api.vk.com/method/audio.getRecommendations"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "count": 200,
            "shuffle": 1
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return self.get_popular_music()
                
        except Exception as e:
            return self.get_popular_music()

    def get_popular_music(self):
        """Получить популярную музыку через поиск"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
            
        popular_queries = [
            "популярные песни 2024", "хиты", "top hits", "новинки музыки",
            "русские хиты", "зарубежные хиты", "топ чарт", "billboard top 100"
        ]
        
        query = random.choice(popular_queries)
        
        url = "https://api.vk.com/method/audio.search"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "q": query,
            "count": 200,
            "auto_complete": 1,
            "sort": 2
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def search_audio(self, query):
        """Поиск музыки"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        url = "https://api.vk.com/method/audio.search"
        params = {
            "access_token": self.token,
            "v": "5.131",
            "q": query,
            "count": 200,
            "auto_complete": 1
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {
                    "success": True, 
                    "results": data["response"]["items"],
                    "total_count": data["response"]["count"]
                }
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def download_audio(self, audio_url, filename, audio_info):
        """Скачать аудиозапись"""
        try:
            headers = self.headers.copy()
            headers.update({
                'Referer': 'https://vk.com/',
                'Origin': 'https://vk.com'
            })
            response = requests.get(audio_url, stream=True, headers=headers)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                # Добавляем в историю загрузок
                self.add_to_downloads_history(audio_info, filename)
                return True
            return False
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
            return False