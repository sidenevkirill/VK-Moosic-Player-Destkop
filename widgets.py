# widgets.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QProgressBar, QGroupBox, QTextEdit, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

class TokenWidget(QWidget):
    """Виджет для работы с токеном"""
    token_changed = pyqtSignal(str)
    token_saved = pyqtSignal()
    token_loaded = pyqtSignal()
    token_checked = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Поле для ввода токена
        token_group = QGroupBox("Токен VK")
        token_layout = QVBoxLayout(token_group)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Введите ваш VK токен здесь...")
        self.token_input.setEchoMode(QLineEdit.Password)
        token_layout.addWidget(QLabel("Токен:"))
        token_layout.addWidget(self.token_input)
        
        # Кнопки управления токеном
        btn_layout = QHBoxLayout()
        
        self.set_token_btn = QPushButton("Установить токен")
        self.set_token_btn.clicked.connect(self.emit_token_changed)
        btn_layout.addWidget(self.set_token_btn)
        
        self.load_token_btn = QPushButton("Загрузить из файла")
        self.load_token_btn.clicked.connect(self.emit_token_loaded)
        btn_layout.addWidget(self.load_token_btn)
        
        self.save_token_btn = QPushButton("Сохранить в файл")
        self.save_token_btn.clicked.connect(self.emit_token_saved)
        btn_layout.addWidget(self.save_token_btn)
        
        self.check_token_btn = QPushButton("Проверить токен")
        self.check_token_btn.clicked.connect(self.emit_token_checked)
        btn_layout.addWidget(self.check_token_btn)
        
        token_layout.addLayout(btn_layout)
        layout.addWidget(token_group)
        
        # Статус токена
        self.status_label = QLabel("Токен не установлен")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
    def set_token(self, token):
        """Установить токен в поле ввода"""
        self.token_input.setText(token)
        
    def get_token(self):
        """Получить токен из поля ввода"""
        return self.token_input.text().strip()
        
    def set_status(self, message, is_success=True):
        """Установить статус"""
        color = "#d4edda" if is_success else "#f8d7da"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"padding: 10px; background-color: {color}; border-radius: 5px;")
        
    def emit_token_changed(self):
        """Эмитировать сигнал изменения токена"""
        token = self.get_token()
        if token:
            self.token_changed.emit(token)
            
    def emit_token_saved(self):
        """Эмитировать сигнал сохранения токена"""
        self.token_saved.emit()
        
    def emit_token_loaded(self):
        """Эмитировать сигнал загрузки токена"""
        self.token_loaded.emit()
        
    def emit_token_checked(self):
        """Эмитировать сигнал проверки токена"""
        self.token_checked.emit()

class AudioListWidget(QListWidget):
    """Кастомный виджет списка аудиозаписей"""
    track_selected = pyqtSignal(dict)
    track_double_clicked = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_list = []
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.itemSelectionChanged.connect(self.on_item_selected)
        
    def set_audio_list(self, audio_list):
        """Установить список аудиозаписей"""
        self.audio_list = audio_list
        self.clear()
        
        for track in audio_list:
            artist = track.get('artist', 'Unknown Artist')
            title = track.get('title', 'Unknown Title')
            duration = track.get('duration', 0)
            
            # Форматирование длительности
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
            
            item = QListWidgetItem(f"{artist} - {title} [{duration_str}]")
            item.setData(Qt.UserRole, track)
            self.addItem(item)
            
    def get_selected_track(self):
        """Получить выбранный трек"""
        current_item = self.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
        
    def on_item_double_clicked(self, item):
        """Обработка двойного клика"""
        track = item.data(Qt.UserRole)
        if track:
            self.track_double_clicked.emit(track)
            
    def on_item_selected(self):
        """Обработка выбора элемента"""
        track = self.get_selected_track()
        if track:
            self.track_selected.emit(track)

class ProgressWidget(QWidget):
    """Виджет отображения прогресса"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        
        self.status_label = QLabel("Готово")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
    def set_progress(self, value, maximum=100):
        """Установить прогресс"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        
    def set_status(self, message):
        """Установить статус"""
        self.status_label.setText(message)
        
    def reset(self):
        """Сбросить прогресс"""
        self.progress_bar.reset()
        self.status_label.setText("Готово")

class UserInfoWidget(QWidget):
    """Виджет информации о пользователе"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.info_label = QLabel("Токен не установлен")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("""
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #ddd;
            font-weight: bold;
            font-size: 14px;
        """)
        
        layout.addWidget(self.info_label)
        
    def set_user_info(self, user_info):
        """Установить информацию о пользователе"""
        if user_info and "valid" in user_info and user_info["valid"]:
            user_data = user_info.get("user_info", {})
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            user_id = user_data.get('id', '')
            
            self.info_label.setText(f"👤 {first_name} {last_name} (ID: {user_id})")
            self.info_label.setStyleSheet("""
                background-color: #d4edda;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #c3e6cb;
                font-weight: bold;
                font-size: 14px;
                color: #155724;
            """)
        else:
            self.info_label.setText("❌ Токен невалиден")
            self.info_label.setStyleSheet("""
                background-color: #f8d7da;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #f5c6cb;
                font-weight: bold;
                font-size: 14px;
                color: #721c24;
            """)

class SearchWidget(QWidget):
    """Виджет поиска"""
    search_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        search_group = QGroupBox("Поиск музыки")
        search_layout = QVBoxLayout(search_group)
        
        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название трека, артиста или альбома...")
        self.search_input.returnPressed.connect(self.emit_search)
        
        # Кнопка поиска
        self.search_btn = QPushButton("🔍 Поиск")
        self.search_btn.clicked.connect(self.emit_search)
        self.search_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        
        layout.addWidget(search_group)
        
    def emit_search(self):
        """Эмитировать сигнал поиска"""
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)
            
    def clear_search(self):
        """Очистить поле поиска"""
        self.search_input.clear()

class InfoWidget(QWidget):
    """Виджет информации о программе"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        info_group = QGroupBox("О программе")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        
        info_layout.addWidget(self.info_text)
        layout.addWidget(info_group)
        
    def set_info(self, program_info):
        """Установить информацию о программе"""
        text = f"""
        <center>
        <h2>{program_info['name']} v{program_info['version']}</h2>
        <p><i>{program_info['description']}</i></p>
        <p><b>Разработчик:</b> {program_info['author']}</p>
        <p><b>Дата релиза:</b> {program_info['release_date']}</p>
        </center>
        
        <h3>🚀 Возможности:</h3>
        <ul>
        """
        
        for feature in program_info['features']:
            text += f"<li>{feature}</li>"
            
        text += "</ul>"
        
        self.info_text.setHtml(text)

class PlayerControlsWidget(QWidget):
    """Виджет управления плеером"""
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    previous_clicked = pyqtSignal()
    volume_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Кнопки управления
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.clicked.connect(self.previous_clicked.emit)
        self.prev_btn.setToolTip("Предыдущий трек")
        
        self.play_btn = QPushButton("▶")
        self.play_btn.clicked.connect(self.on_play_pause_clicked)
        self.play_btn.setToolTip("Воспроизвести")
        self.play_btn.setStyleSheet("font-size: 16px;")
        
        self.next_btn = QPushButton("⏭")
        self.next_btn.clicked.connect(self.next_clicked.emit)
        self.next_btn.setToolTip("Следующий трек")
        
        # Громкость
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("🔊"))
        
        self.volume_slider = QProgressBar()
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        
        volume_layout.addWidget(self.volume_slider)
        
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.next_btn)
        layout.addLayout(volume_layout)
        
        self.is_playing = False
        
    def on_play_pause_clicked(self):
        """Обработка клика play/pause"""
        if self.is_playing:
            self.pause_clicked.emit()
            self.play_btn.setText("▶")
            self.play_btn.setToolTip("Воспроизвести")
        else:
            self.play_clicked.emit()
            self.play_btn.setText("⏸")
            self.play_btn.setToolTip("Пауза")
            
        self.is_playing = not self.is_playing
        
    def set_playing_state(self, is_playing):
        """Установить состояние воспроизведения"""
        self.is_playing = is_playing
        if is_playing:
            self.play_btn.setText("⏸")
            self.play_btn.setToolTip("Пауза")
        else:
            self.play_btn.setText("▶")
            self.play_btn.setToolTip("Воспроизвести")
            
    def set_volume(self, volume):
        """Установить громкость"""
        self.volume_slider.setValue(volume)

class NowPlayingWidget(QWidget):
    """Виджет текущего трека"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.track_label = QLabel("Трек не выбран")
        self.track_label.setAlignment(Qt.AlignCenter)
        self.track_label.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 6px;
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        
        time_layout = QHBoxLayout()
        self.current_time = QLabel("0:00")
        self.total_time = QLabel("0:00")
        self.total_time.setAlignment(Qt.AlignRight)
        
        time_layout.addWidget(self.current_time)
        time_layout.addWidget(self.total_time)
        
        layout.addWidget(self.track_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(time_layout)
        
    def set_track_info(self, artist, title):
        """Установить информацию о треке"""
        self.track_label.setText(f"{artist} - {title}")
        
    def set_progress(self, current, total):
        """Установить прогресс воспроизведения"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            
            # Форматирование времени
            current_min = current // 60000
            current_sec = (current % 60000) // 1000
            total_min = total // 60000
            total_sec = (total % 60000) // 1000
            
            self.current_time.setText(f"{current_min}:{current_sec:02d}")
            self.total_time.setText(f"{total_min}:{total_sec:02d}")