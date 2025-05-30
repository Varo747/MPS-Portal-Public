import os, threading
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox,
    QLabel, QSpinBox, QTextEdit, QFrame, QComboBox)
from PyQt6.QtCore import Qt, QTimer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Class for Settings window
class Settings_page(QWidget):
    def __init__(self, account, app, main_window):
        super().__init__()
        self.account = account
        self.app = app
        self.main_window = main_window

        main_layout = QVBoxLayout()
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addSpacing(50)

        horizontal_layout = QHBoxLayout()

        # Left Side
        left_layout = QVBoxLayout()
        left_layout.setSpacing(50)

        left_box_container = QWidget()
        left_box_container.setFixedWidth(600)
        left_box_container.setObjectName("SettingsBox")
        left_layout_box = QVBoxLayout(left_box_container)
        left_layout_box.addSpacing(10)
        left_layout_box.setSpacing(20)

        exp_logs_btn = QPushButton("📤 Export Logs")
        exp_logs_btn.clicked.connect(self.export_logs)
        left_layout_box.addWidget(exp_logs_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout_box.addWidget(self.create_divider())

        # Auto login
        auto_log_container = QWidget()
        auto_log_container.setObjectName("SettingsContainer")
        auto_log_layout = QHBoxLayout(auto_log_container)
        auto_log_layout.setContentsMargins(0, 0, 0, 0)
        auto_log_layout.setSpacing(20)

        auto_login_label = QLabel("Auto Log In:")
        self.remember_me_box = QCheckBox("Remember me")
        self.remember_me_box.stateChanged.connect(self.handle_checkbox_change)

        auto_log_layout.addWidget(auto_login_label)
        auto_log_layout.addWidget(self.remember_me_box)
        left_layout_box.addWidget(auto_log_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout_box.addWidget(self.create_divider())

        # Session timeout
        session_container = QWidget()
        session_container.setObjectName("SettingsContainer")
        session_layout = QHBoxLayout(session_container)
        session_layout.setContentsMargins(0, 0, 0, 0)
        session_layout.setSpacing(20)

        # Add end of session feature
        session_label = QLabel("Session timeout:")
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(60)
        self.spin_box.setSuffix(" min")
        session_value = self.account.notification[2] if len(self.account.notification) > 2 else 30
        self.spin_box.setValue(session_value)

        self.session_enable_box = QCheckBox("Enable")
        self.session_enable_box.stateChanged.connect(self.handle_checkbox_change)

        session_layout.addWidget(session_label)
        session_layout.addWidget(self.spin_box)
        session_layout.addWidget(self.session_enable_box)
        left_layout_box.addWidget(session_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout_box.addWidget(self.create_divider())

        # Add notification preferences
        notification_label = QLabel("🔔 Notification Preferences:")
        left_layout_box.addWidget(notification_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        notification_container = QWidget()
        notification_container.setObjectName("SettingsContainer")
        notification_layout = QHBoxLayout(notification_container)
        notification_layout.setContentsMargins(0, 0, 0, 0)
        notification_layout.setSpacing(20)

        self.email_check = QCheckBox("Email")
        self.email_check.setObjectName("SettingsBox")
        self.email_check.stateChanged.connect(self.handle_checkbox_change)

        self.none_check = QCheckBox("None")
        self.none_check.setObjectName("SettingsBox")
        self.none_check.stateChanged.connect(self.handle_checkbox_change)
        self.none_check.setChecked(True)

        notification_layout.addWidget(self.email_check)
        notification_layout.addWidget(self.none_check)
        left_layout_box.addWidget(notification_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Add style selector options
        style_container = QWidget()
        style_container.setObjectName("SettingsContainer")
        style_layout = QHBoxLayout()
        style_layout.setContentsMargins(0, 0, 0, 0)
        style_layout.setSpacing(20)
        style_container.setLayout(style_layout)

        style_label = QLabel("Change Style:")
        style_dropdown = QComboBox()
        style_dropdown.addItems(["Light (Default)", "Dark", "Vibrant", "Industrial"])
        style_dropdown.currentIndexChanged.connect(self.change_style)

        style_layout.addWidget(style_label)
        style_layout.addWidget(style_dropdown)
        left_layout_box.addWidget(style_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Wrap up left layout
        left_layout.addWidget(left_box_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch()

        save_button = QPushButton("💾 Save Settings")
        save_button.clicked.connect(self.save_settings)
        left_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch()

        app_version_label = QLabel(f"App Version: {self.app.app_version}")
        left_layout.addWidget(app_version_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Right side (feedback)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(30)

        feedback_label = QLabel("Feedback")
        right_layout.addWidget(feedback_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.feedback_input = QTextEdit()
        self.feedback_input.setObjectName("FeedbackBox")
        self.feedback_input.setPlaceholderText("Feedback")
        right_layout.addWidget(self.feedback_input, alignment=Qt.AlignmentFlag.AlignHCenter)

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.send_feedback)
        right_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        right_layout.addStretch()

        # Final layouts
        horizontal_layout.addLayout(left_layout)
        horizontal_layout.addLayout(right_layout)
        main_layout.addLayout(horizontal_layout)
        self.setLayout(main_layout)

        # Session timer
        self.session_timer = QTimer()
        self.session_timer.setSingleShot(True)
        self.session_timer.timeout.connect(self.session_timeout)
        self.installEventFilter(self)

        # Load stored settings
        try:
            notif = self.account.notification
            self.remember_me_box.setChecked(bool(notif[1]))
            self.spin_box.setValue(int(notif[2]))
            self.session_enable_box.setChecked(bool(notif[3]))
            self.email_check.setChecked(bool(notif[4]))
            self.none_check.setChecked(bool(notif[5]))
        except Exception as e:
            print(f"[ERROR loading settings]: {e}")
    
    def eventFilter(self, source, event):
        if self.session_enable_box.isChecked():
            self.restart_session_timer()
        return super().eventFilter(source, event)
    
    def restart_session_timer(self):
        timeout_minutes = self.spin_box.value()
        self.session_timer.start(timeout_minutes * 60 * 1000)

    def session_timeout(self):
        print("Session timed out.")
        self.app.update_log_info(self.account, "Session Timeout", "User was logged out due to inactivity", True)
        self.main_window.logout_user()

    def run_export_logs(self):
        log_path = os.path.join("app_resources", "log_info_example.csv")
        df = pd.read_csv(log_path, names=["Timestamp", "Username", "Idnumber", "Action", "Details", "Success", "Security level"], header=None)
        username = str(self.account.username).strip()
        df["Username"] = df["Username"].astype(str).str.strip()
        self.df = df[df["Username"] == username].copy()
        self.df["Security level"] = pd.to_numeric(self.df["Security level"], errors='coerce')
        self.df = self.df[self.df["Security level"] <= self.account.security_level]

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"{username}_log_export.xlsx"
        export_path = os.path.join(desktop, filename)
        self.df.to_excel(export_path, index=False)

        self.app.update_log_info(self.account, "Export Logs", f"Logs were manually downloaded by user", True, 3)

    # Function for exporting logs to desktop
    def export_logs(self):
        thread = threading.Thread(target=self.run_export_logs)
        thread.start()

    def send_feedback(self):
        feedback_text = self.feedback_input.toPlainText().strip()
        if not feedback_text:
            return

        def send_feedback_txt():
            try:
                feedback_path = os.path.join("app_resources", "feedback.txt")
                with open(feedback_path, mode="a", encoding="utf-8") as file:
                    file.write(f"{self.account.username} ({self.account.id})\n")
                    file.write(f"{feedback_text}\n")
                    file.write("-" * 40 + "\n")
                self.app.update_log_info(self.account, "Feedback Logged", "Feedback saved to feedback.txt", True)
            except Exception as e:
                print(f"[ERROR] Writing to feedback.txt failed: {e}")

        threading.Thread(target=send_feedback_txt).start()

    # Create dividers in setting widget for styling
    def create_divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setFixedHeight(2)
        line.setStyleSheet("""
            QFrame {
                background-color: #e0e6f0;
                border: none;
                margin-left: 20px;
                margin-right: 20px;
                border-radius: 4px;
            }
        """)
        return line
    
    def handle_checkbox_change(self):
        self.spin_box.interpretText()
        return [
            self.account.notification[0],
            self.remember_me_box.isChecked(),
            self.spin_box.value(),
            self.session_enable_box.isChecked(),
            self.email_check.isChecked(),
            self.none_check.isChecked()
        ]
    
    # Save setting into users json file
    def save_settings(self):
        settings = self.handle_checkbox_change()
        self.account.notification = settings
        self.app.update_json_info(self.account, "notification", settings)
        self.app.update_log_info(self.account, "Settings Saved", f"Settings updated: {settings}", True)

        if not settings[1]:
            try:
                os.remove("last_session.json")
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"[ERROR] Couldn't remove last_session.json: {e}")

        if self.session_enable_box.isChecked():
            self.restart_session_timer()
        else:
            self.session_timer.stop()

    def change_style(self, index):
        style_files = ["main_window.qss", "dark.qss", "vibrant.qss", "industrial.qss"]
        try:
            style_path = os.path.join("app_resources", "styles", style_files[index])
            self.account.notification[0] = style_files[index]
            with open(style_path, "r") as f:
                style = f.read()
                self.main_window.setStyleSheet(style)
                self.app.update_log_info(self.account, "Style Changed", f"New style applied: {style_files[index]}", True)
                self.app.update_json_info(self.account, "notification", self.account.notification)

        except Exception as e:
            print(f"[ERROR loading style]: {e}")