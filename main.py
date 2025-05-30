import sys, os, time
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QMainWindow, QSizePolicy, QStackedWidget, QDialog,
    QProgressBar, QGraphicsOpacityEffect, QFrame, QMenu, QToolButton)
from PyQt6.QtCore import Qt, QPropertyAnimation, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QSize
from PyQt6.QtGui import QIcon, QPixmap, QAction

from app_status import App_status
from user_class import user
from dashboard_class import Dashboard_page
from automatic_reports_class import Reports_page
from history_class import History_page
from utilities_class import Utilities_page
from settings_class import Settings_page
from account_class import Account_page

from util_functs import security_check

class LoaderThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, parent=None, account=None, app_status=None):
        super().__init__(parent)
        self.account = account
        self.app_status = app_status

    def run(self):
        time.sleep(1)
        self.finished.emit(self.app_status)

# Class for log in window
class LoginWindow(QWidget):
    def __init__(self, app_status):
        super().__init__()
        icon_path = os.path.join("app_resources", "icons", "app_icon.png")
        self.app_status = app_status
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Log In")
        self.setFixedSize(600, 300)

        # Create widgets for user interaction
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("User")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Log in")
        self.login_button.setObjectName("LoginStyle")
        self.login_button.clicked.connect(self.check_login)

        title = QLabel("Welcome to the Portal")
        title.setObjectName("LoginStyle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form = QVBoxLayout()
        form.addWidget(title)
        form.addSpacing(10)
        form.addWidget(self.username_input)
        form.addWidget(self.password_input)
        form.addSpacing(10)
        form.addWidget(self.login_button)

        container = QWidget()
        container.setLayout(form)

        wrapper = QVBoxLayout()
        wrapper.addStretch()
        wrapper.addWidget(container)
        wrapper.addStretch()
        self.setLayout(wrapper)

    # Check details and open main window if user details are correct
    def check_login(self):
        users_info = self.app_status.user_info

        username = self.username_input.text()
        password = self.password_input.text()

        if username in users_info and users_info[username]["password"] == password:
            account = user(users_info, username, password)
            self.app_status.update_log_info(account, "Log in", f"{account.username} Log in", True)
            self.app_status.update_last_login(account)
            if account.notification[1]:
                self.app_status.save_last_session(account.username)
            self.open_main_window(account)
        else:
            class TempAccount:
                def __init__(self, username):
                    self.username = username
                    self.id = "Unknown"

            self.app_status.update_log_info(TempAccount(username), "Log in", f"Failed login attempt with username '{username}'", False, 3)
            QMessageBox.warning(self, "Access denied", "User or password are incorrect")

    def open_main_window(self, account):
        self.hide()
        self.splash = LoadingSplash(self, account, self.app_status)
        self.splash.show()

# Class for laoding window
class LoadingSplash(QDialog):
    def __init__(self, parent=None, account=None, app_status=None):
        super().__init__(parent)
        self.account = account
        self.app_status = app_status
        self.setModal(True)
        self.setFixedSize(300, 120)
        icon_path = os.path.join("app_resources", "icons", "app_icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Loading...")

        layout = QVBoxLayout()
        label = QLabel("🌊 Launching the app, please wait...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)

        layout.addWidget(label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        self.anim = QPropertyAnimation(opacity_effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

        self.setStyleSheet("""
            QDialog {
                background-color: #f0f4f8;
                border-radius: 0px;
            }
            QLabel {
                font-size: 15px;
                font-weight: 600;
            }
            QProgressBar {
                height: 12px;
                background: #e0e0e0;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background-color: #7289da;
                border-radius: 6px;
            }
        """)

        self.thread = LoaderThread(account=self.account, app_status=self.app_status)
        self.thread.finished.connect(self.finish_loading)
        self.thread.start()

    def finish_loading(self, app_status):
        self.close()
        self.main_window = MainWindow(self.account, app_status)
        self.main_window.show()

# Class for main window
class MainWindow(QMainWindow):
    def __init__(self, account, app_status):
        super().__init__()
        icon_path = os.path.join("app_resources", "icons", "app_icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Marine Products Scotland App")
        self.showMaximized()

        self.account = account
        self.app = app_status
        self.is_animating = False
        self.init_content_stack()

        # Create top banner with logo and account button
        top_banner_layout = QHBoxLayout()
        top_banner_layout.setContentsMargins(0, 0, 0, 0)

        icon_path = os.path.join("app_resources", "icons", "app_icon.png")
        icon_pixmap = QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        icon_label = QLabel()
        icon_pixmap = QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_label = QLabel("Marine Products Scotland")
        text_label.setObjectName("TitleLabel")
        text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        title_container = QWidget()
        title_container.setObjectName("TitleLabel")
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(text_label)
        title_container.setLayout(title_layout)
        top_banner_layout.addStretch()
        top_banner_layout.addWidget(title_container)
        top_banner_layout.addStretch()

        avatar_button = QToolButton()
        avatar_button.setText(f" {account.username}")

        avatar_icon = QIcon(account.create_rounded_profile_pixmap(account.user_image_path))
        avatar_button.setIcon(avatar_icon)

        avatar_button.setIconSize(QSize(36, 36))
        avatar_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        avatar_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        avatar_button.setObjectName("Accountbutton")

        user_menu = QMenu()
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(lambda: self.switch_content("Settings"))
        account_action = QAction("👤 Account", self)
        account_action.triggered.connect(lambda: self.switch_content("Account"))
        logout_action = QAction("🔐 Log out", self)
        logout_action.triggered.connect(self.logout_user)

        user_menu.addAction(settings_action)
        user_menu.addAction(account_action)
        user_menu.addAction(logout_action)
        avatar_button.setMenu(user_menu)

        top_banner_layout.addWidget(avatar_button)

        top_banner_widget = QWidget()
        top_banner_widget.setObjectName("TopBanner")
        top_banner_widget.setLayout(top_banner_layout)
        top_banner_widget.setFixedHeight(60)
        top_banner_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Create side banner with categories
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(20)
        sidebar_layout.addSpacing(10)

        category_map = {
            "📊 Dashboard": "Dashboard",
            "🧾 Automatic Reports": "Automatic Reports",
            "🕓 History": "History",
            "🛠 Utilities": "Utilities",
            "⚙️ Settings": "Settings",
            "👤 Account": "Account"
        }

        for i, (label, key) in enumerate(category_map.items()):
            btn = QPushButton(label)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, name=key: self.switch_content(name))
            sidebar_layout.addWidget(btn)

            if i < len(category_map) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Plain)
                line.setObjectName("DashLine")
                line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                sidebar_layout.addWidget(line)

        sidebar_layout.addStretch()
        version_label=QLabel(f"ⓘ Version {self.app.app_version}")
        version_label.setObjectName("VersionLabel")
        sidebar_layout.addWidget(version_label)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("SideBar")
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.addWidget(sidebar_widget)
        middle_layout.addWidget(self.content_stack)

        middle_widget = QWidget()
        middle_widget.setLayout(middle_layout)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(top_banner_widget, stretch=0)
        main_layout.addWidget(middle_widget, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        style_path = os.path.join("app_resources", "styles", "main_window.qss")
        self.setStyleSheet(load_stylesheet(style_path))

    # Function for animating change of windows
    def animate_transition(self, new_index):
        if self.is_animating:
            return
        current_index = self.content_stack.currentIndex()
        if current_index == new_index:
            return

        self.is_animating = True

        direction = 1 if new_index > current_index else -1
        width = self.content_stack.width()

        current_widget = self.content_stack.currentWidget()
        next_widget = self.content_stack.widget(new_index)

        next_widget.setGeometry(QRect(direction * width, 0, width, self.content_stack.height()))
        next_widget.show()

        anim_old = QPropertyAnimation(current_widget, b"geometry")
        anim_old.setDuration(300)
        anim_old.setStartValue(QRect(0, 0, width, self.content_stack.height()))
        anim_old.setEndValue(QRect(-direction * width, 0, width, self.content_stack.height()))
        anim_old.setEasingCurve(QEasingCurve.Type.InOutCubic)

        anim_new = QPropertyAnimation(next_widget, b"geometry")
        anim_new.setDuration(300)
        anim_new.setStartValue(QRect(direction * width, 0, width, self.content_stack.height()))
        anim_new.setEndValue(QRect(0, 0, width, self.content_stack.height()))
        anim_new.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.anim_group = [anim_old, anim_new]
        anim_old.start()
        anim_new.start()

        def on_animation_finished():
            self.content_stack.setCurrentIndex(new_index)
            current_widget.setGeometry(QRect(0, 0, width, self.content_stack.height()))
            next_widget.setGeometry(QRect(0, 0, width, self.content_stack.height()))
            self.is_animating = False

        anim_new.finished.connect(on_animation_finished)

    def init_content_stack(self):
        self.content_stack = QStackedWidget()
        self.pages = {
            "Dashboard": Dashboard_page(self.account, self.app),
            "Settings": Settings_page(self.account, self.app, self),
            "Account": Account_page(self.account, self.app),
            "History": History_page(self.account, self.app),
            "Automatic Reports": Reports_page(self.account, self.app)
        }

        for name, widget in self.pages.items():
            if isinstance(widget, QLabel):
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_stack.addWidget(widget)

        self.page_indices = {name: i for i, name in enumerate(self.pages)}

    def switch_content(self, category_name):
        if category_name not in self.page_indices:
            if category_name == "Utilities":
                if security_check(self.account.security_level, 3):
                    widget = Utilities_page(self.account, self.app)
                else:
                    self.app.update_log_info(self.account, "Access Utilities", f"{self.account.username} tried to access utilities tab", False, 3)
                    widget = self.access_denied_widget()
                self.pages[category_name] = widget
                self.content_stack.addWidget(widget)
                self.page_indices[category_name] = self.content_stack.count() - 1

        index = self.page_indices.get(category_name, 0)
        self.animate_transition(index)

    # Define widget for denied access
    def access_denied_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("⚠️ Access denied: insufficient security level.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        widget.setLayout(layout)
        
        return widget
    
    def logout_user(self):
        self.app.update_log_info(self.account, "Logout", "User was logged out", True)
        self.close()
        self.login_window = LoginWindow(app_status=self.app)
        self.login_window.show()

# Load the QSS style
def load_stylesheet(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] QSS could not be loaded: {e}")
        return ""

# Launch App and load a session if one is available
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_style = load_stylesheet(os.path.join("app_resources", "styles", "main_window.qss"))
    app.setStyleSheet(main_style)

    app_status = App_status()

    session_user =app_status.load_last_session()
    if session_user:
        users_info = app_status.user_info
        if session_user in users_info:
            account = user(users_info, session_user, users_info[session_user]["password"])
            app_status.update_log_info(account, "Auto Log in", f"{account.username} auto logged in", True)
            app_status.update_last_login(account)

            splash = LoadingSplash(account=account, app_status=app_status)
            splash.show()
            sys.exit(app.exec())

    login = LoginWindow(app_status=app_status)
    login.show()
    sys.exit(app.exec())