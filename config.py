# config.py
# API ключи и константы приложения
APP_ID = 2685278  # VK Android app ID
API_VERSION = "5.131"

# User-Agent для Kate Mobile
KATE_USER_AGENT = "KateMobileAndroid/51.1-442 (Android 11; SDK 30; arm64-v8a; Samsung SM-G991B; ru_RU)"

# Настройки запросов
REQUEST_HEADERS = {
    'User-Agent': KATE_USER_AGENT,
    'Accept': 'application/json',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive'
}

# Настройки скачивания
DOWNLOAD_HEADERS = {
    'User-Agent': KATE_USER_AGENT,
    'Referer': 'https://vk.com/',
    'Origin': 'https://vk.com',
    'Accept': '*/*',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive'
}

# Файлы
TOKEN_FILE = 'vk_token.txt'

# Популярные запросы для рекомендаций
POPULAR_QUERIES = [
    "популярные песни 2024", "хиты", "top hits", "новинки музыки",
    "русские хиты", "зарубежные хиты", "топ чарт", "billboard top 100"
]

# Лимиты
FRIENDS_LIMIT = 200
GROUPS_LIMIT = 200
AUDIO_LIMIT = 200
SEARCH_LIMIT = 200
PLAYLISTS_LIMIT = 200

# URL API endpoints
API_BASE_URL = "https://api.vk.com/method/"
API_ENDPOINTS = {
    'users_get': 'users.get',
    'friends_get': 'friends.get',
    'groups_get': 'groups.get',
    'audio_get': 'audio.get',
    'audio_search': 'audio.search',
    'audio_get_playlists': 'audio.getPlaylists',
    'audio_get_recommendations': 'audio.getRecommendations'
}