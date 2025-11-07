import pygame
import time
import threading
import requests
from urllib.parse import urlparse
import tempfile
import os
import re

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_track = None
        self.track_name = ""
        self.paused = False
        self.playing = False
        self.position = 0
        self.duration = 0
        self.volume = 70
        self.position_thread = None
        self.stop_event = threading.Event()
        self.temp_files = []  # Для хранения всех временных файлов
        self.start_time = 0
        self.current_temp_file = None
    
    def load_track(self, source, track_name=""):
        """Загружает трек из URL или локального файла"""
        try:
            print(f"DEBUG: Loading track from: {source}")
            
            # Останавливаем текущее воспроизведение
            if self.playing:
                self.stop()
            
            # Проверяем, является ли source URL или локальным путем
            parsed = urlparse(source)
            
            if parsed.scheme in ('http', 'https'):
                # Это URL - загружаем через requests
                return self._load_from_url(source, track_name)
            else:
                # Это локальный путь
                return self._load_from_file(source, track_name)
                
        except Exception as e:
            print(f"Ошибка при загрузке трека: {e}")
            return False
    
    def _load_from_url(self, url, track_name):
        """Загружает трек из URL"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                # Создаем временный файл
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                temp_file.close()
                
                # Загружаем аудио в pygame
                pygame.mixer.music.load(temp_file.name)
                
                # Получаем длительность трека
                try:
                    sound = pygame.mixer.Sound(temp_file.name)
                    self.duration = sound.get_length()  # Длительность в секундах
                except:
                    # Если не удалось получить длительность, устанавливаем по умолчанию
                    self.duration = 0
                
                self.current_track = url
                self.track_name = track_name
                self.paused = False
                self.playing = False
                self.position = 0
                self.current_temp_file = temp_file.name
                self.temp_files.append(temp_file.name)
                
                # Устанавливаем громкость
                self.set_volume(self.volume)
                
                print(f"DEBUG: Track loaded successfully. Duration: {self.duration} seconds")
                return True
            else:
                print(f"Ошибка загрузки трека: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Ошибка при загрузке из URL: {e}")
            return False
    
    def _load_from_file(self, file_path, track_name):
        """Загружает трек из локального файла"""
        try:
            if not os.path.exists(file_path):
                print(f"Файл не найден: {file_path}")
                return False
            
            # Если имя трека не указано, извлекаем из имени файла
            if not track_name:
                filename = os.path.basename(file_path)
                track_name = filename.replace('.mp3', '').replace('_', ' ')
            
            # Загружаем аудио в pygame
            pygame.mixer.music.load(file_path)
            
            # Получаем длительность трека
            try:
                sound = pygame.mixer.Sound(file_path)
                self.duration = sound.get_length()
            except:
                self.duration = 0
            
            self.current_track = file_path
            self.track_name = track_name
            self.paused = False
            self.playing = False
            self.position = 0
            self.current_temp_file = None
            
            # Устанавливаем громкость
            self.set_volume(self.volume)
            
            print(f"DEBUG: Local track loaded successfully. Duration: {self.duration} seconds")
            return True
            
        except Exception as e:
            print(f"Ошибка при загрузке локального файла: {e}")
            return False
    
    def play(self):
        """Начинает воспроизведение"""
        if not self.playing:
            try:
                pygame.mixer.music.play()
                self.playing = True
                self.paused = False
                self.start_time = time.time() - self.position
                
                # Запускаем поток для отслеживания позиции
                self.stop_event.clear()
                if self.position_thread and self.position_thread.is_alive():
                    self.position_thread.join(timeout=0.1)
                
                self.position_thread = threading.Thread(target=self._track_position, daemon=True)
                self.position_thread.start()
                return True
            except Exception as e:
                print(f"Ошибка воспроизведения: {e}")
                return False
        return False
    
    def pause(self):
        """Приостанавливает воспроизведение"""
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            return True
        return False
    
    def unpause(self):
        """Продолжает воспроизведение после паузы"""
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.start_time = time.time() - self.position
            return True
        return False
    
    def stop(self):
        """Останавливает воспроизведение"""
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.position = 0
        self.stop_event.set()
        
        # Очищаем временные файлы
        self._cleanup_temp_files()
    
    def set_volume(self, volume):
        """Устанавливает громкость (0-100)"""
        try:
            volume = int(volume)
            volume = max(0, min(100, volume))
            self.volume = volume
            pygame_volume = volume / 100.0
            pygame.mixer.music.set_volume(pygame_volume)
            return True
        except (ValueError, TypeError) as e:
            print(f"Неверное значение громкости: {volume}, ошибка: {e}")
            return False
    
    def get_status(self):
        """Возвращает текущий статус плеера"""
        return {
            'playing': self.playing and not self.paused,
            'paused': self.paused,
            'position': self.position,
            'duration': self.duration,
            'volume': self.volume,
            'track_name': self.track_name,
            'current_track': self.current_track
        }
    
    def _track_position(self):
        """Поток для отслеживания позиции воспроизведения"""
        while self.playing and not self.stop_event.is_set():
            try:
                if not self.paused and self.playing:
                    # Рассчитываем позицию на основе времени воспроизведения
                    current_pos = time.time() - self.start_time
                    
                    # Проверяем, не превышает ли позиция длительность
                    if self.duration > 0 and current_pos >= self.duration:
                        self.position = self.duration
                        self.playing = False
                        break
                    else:
                        self.position = current_pos
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Ошибка в потоке отслеживания позиции: {e}")
                break
    
    def _cleanup_temp_files(self):
        """Очищает временные файлы"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Ошибка при удалении временного файла {temp_file}: {e}")
        
        self.temp_files = []
        self.current_temp_file = None
    
    def seek(self, position):
        """Перематывает трек на указанную позицию (в секундах)"""
        if self.duration > 0 and 0 <= position <= self.duration:
            try:
                # Останавливаем текущее воспроизведение
                was_playing = self.playing and not self.paused
                pygame.mixer.music.stop()
                
                # Перезагружаем трек и устанавливаем позицию
                if self.current_temp_file:
                    pygame.mixer.music.load(self.current_temp_file)
                elif self.current_track and os.path.exists(self.current_track):
                    pygame.mixer.music.load(self.current_track)
                
                # Устанавливаем позицию
                self.position = position
                self.start_time = time.time() - position
                
                # Продолжаем воспроизведение, если оно было
                if was_playing:
                    pygame.mixer.music.play(start=position)
                    self.playing = True
                    self.paused = False
                
                return True
            except Exception as e:
                print(f"Ошибка перемотки: {e}")
                return False
        return False
    
    def cleanup(self):
        """Полная очистка ресурсов"""
        self.stop()
        if self.position_thread and self.position_thread.is_alive():
            self.stop_event.set()
            self.position_thread.join(timeout=1.0)
        self._cleanup_temp_files()
        pygame.mixer.quit()