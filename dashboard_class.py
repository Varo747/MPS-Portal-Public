from PyQt6.QtGui import QFont, QTextCharFormat, QColor
from PyQt6.QtWidgets import QWidget, QListWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QCalendarWidget, QSizePolicy, QTimeEdit, QMenu, QListWidgetItem
from PyQt6.QtCore import QTime, Qt, QDate

# Class for the reminders window
class ReminderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Reminder")
        self.setFixedSize(400, 250)
        self.setModal(True)

        layout = QVBoxLayout()

        # Reminder text
        label = QLabel("Write your reminder:")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("e.g., Follow up with HR")

        # Time input
        time_label = QLabel("Pick a time:")
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")

        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("Cancel")

        add_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)

        # Add widgets to layout
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        layout.addWidget(time_label)
        layout.addWidget(self.time_edit)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_text_and_time(self):
        text = self.text_edit.toPlainText().strip()
        time = self.time_edit.time().toString("HH:mm")
        return text, time

# Class for the Dashboard window
class Dashboard_page(QWidget):
    def __init__(self, account, app):
        super().__init__()
        self.account=account
        self.app=app
        self.reminders_by_date = {}

        main_layout=QVBoxLayout()
        title=QLabel("Dashboard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addSpacing(50)

        # Info layout
        welcome_layout = QHBoxLayout()

        # First info box
        welcome_container_1 = QWidget()
        welcome_container_1.setObjectName("DashboardContainer")
        welcome_container_1.setFixedWidth(600)
        sub_wel_layout1 = QVBoxLayout(welcome_container_1)
        welcome_label = QLabel(f"Welcome back {self.account.username}!\nHere's your recent activity summary.")
        welcome_label.setObjectName("DashboardLabel")
        sub_wel_layout1.addWidget(welcome_label)

        # Second info box
        system_container_2 = QWidget()
        system_container_2.setObjectName("DashboardContainer")
        system_container_2.setFixedWidth(600)
        sub_wel_layout2 = QVBoxLayout(system_container_2)

        text=""
        if self.app.health_check == "":
            text = "System Status:\n✅ All systems operational"
        else:
            issues = "\n".join(self.app.health_check)
            text = f"System Status:\n❌ One or more systems are not operational:\n{issues}"
        status_label = QLabel(text)
        status_label.setObjectName("DashboardLabel")
        sub_wel_layout2.addWidget(status_label)

        # Add both to the row
        welcome_layout.addWidget(welcome_container_1)
        welcome_layout.addWidget(system_container_2)

        # Info layout
        info_layout=QHBoxLayout()
        info_layout.setSpacing(30)

        # Left layout
        left_layout=QVBoxLayout()
        left_layout.setSpacing(30)
        pending_container=QWidget()
        pending_container.setObjectName("DashboardContainer")
        pending_container.setFixedWidth(300)
        pending_layout=QVBoxLayout(pending_container)
        pending_label=QLabel("📝 Pending Task:")
        pending_label.setObjectName("DashboardLabel")

        self.pending_text_str=self.app.day_check
        pending_task = QTextEdit()
        pending_task.setPlainText(self.pending_text_str)

        pending_layout.addWidget(pending_label)
        pending_layout.addWidget(pending_task)

        weekly_container=QWidget()
        weekly_container.setObjectName("DashboardContainer")
        weekly_container.setFixedWidth(500)
        weekly_layout=QVBoxLayout(weekly_container)
        weekly_label=QLabel("📈 Weekly summary:")
        weekly_text = QTextEdit()
        weekly_text.setPlainText(self.app.weekly_info)
        weekly_layout.addWidget(weekly_label)
        weekly_layout.addWidget(weekly_text)

        left_layout.addWidget(pending_container)
        left_layout.addWidget(weekly_container)
        info_layout.addLayout(left_layout)

        # Center layout
        center_layout=QVBoxLayout()
        reminder_container=QWidget()
        reminder_container.setObjectName("DashboardContainer")
        reminder_container.setFixedWidth(500)
        reminder_layout=QVBoxLayout(reminder_container)
        self.reminder_list = QListWidget()
        self.reminder_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.reminder_list.customContextMenuRequested.connect(self.show_reminder_menu)
        reminder_label=QLabel("Reminders:")
        reminder_label.setObjectName("DashboardLabel")
        creat_reminder_btn = QPushButton("+ Add Reminder")
        creat_reminder_btn.clicked.connect(self.open_reminder_dialog)
        reminder_layout.addWidget(reminder_label)
        reminder_layout.addWidget(self.reminder_list)
        reminder_layout.addStretch()
        reminder_layout.addWidget(creat_reminder_btn)

        center_layout.addWidget(reminder_container)
        info_layout.addLayout(center_layout)

        # Right layout
        right_layout=QVBoxLayout()
        calendar_container=QWidget()
        calendar_container.setObjectName("DashboardContainer")
        calendar_container.setFixedWidth(500)
        calendar_layout=QVBoxLayout(calendar_container)
        self.calendar_widget=QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        calendar_layout.addWidget(self.calendar_widget, stretch=1)
        self.calendar_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        calendar_layout.addWidget(self.calendar_widget)
        self.load_reminders_from_account()

        right_layout.addWidget(calendar_container)
        info_layout.addLayout(right_layout)

        # Final layouts
        main_layout.addLayout(welcome_layout)
        main_layout.addSpacing(100)
        main_layout.addLayout(info_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    # Load reminders from user information
    def load_reminders_from_account(self):
        reminders = getattr(self.account, "reminders", {})
        self.reminders_by_date = reminders.copy() if reminders else {}

        self.reminder_list.clear()
        for date_str, reminders_list in self.reminders_by_date.items():
            for text, time in reminders_list:
                display = f"📅 {date_str} | 🕒 {time} - {text}"
                item = QListWidgetItem(display)
                font = QFont("Segoe UI", 14)
                item.setFont(font)
                self.reminder_list.addItem(item)
        self.highlight_reminder_dates(self.calendar_widget)

    def open_reminder_dialog(self):
        dialog = ReminderDialog(self)
        if dialog.exec():
            text, time = dialog.get_text_and_time()
            if text:
                date = self.calendar_widget.selectedDate()
                date_str = date.toString("yyyy-MM-dd")

                if date_str not in self.reminders_by_date:
                    self.reminders_by_date[date_str] = []
                self.reminders_by_date[date_str].append((text, time))

                self.account.reminders = self.reminders_by_date
                self.app.update_json_info(self.account, "reminders", self.reminders_by_date)

                self.app.update_log_info(self.account, "Reminder created", f"{date_str}: {text} at {time}", True)
                display = f"📅 {date_str} | 🕒 {time} - {text}"
                item = QListWidgetItem(display)
                font = QFont("Segoe UI", 14)
                item.setFont(font)
                self.reminder_list.addItem(item)

                self.highlight_reminder_dates(self.calendar_widget)

    def show_reminder_menu(self, position):
        selected_item = self.reminder_list.itemAt(position)
        if selected_item:
            menu = QMenu()
            menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #ccd3db;
                    border-radius: 8px;
                    padding: 4px;
                }

                QMenu::item {
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                }

                QMenu::item:selected {
                    background-color: #d2e3fc;
                    color: #2c2f33;
                }
            """)
            delete_action = menu.addAction("🗑️ Delete")
            action = menu.exec(self.reminder_list.mapToGlobal(position))
            if action == delete_action:
                row = self.reminder_list.row(selected_item)
                text = selected_item.text()
                try:
                    date_str = text.split(" | ")[0].replace("📅 ", "").strip()
                    time = text.split(" | ")[1].split(" - ")[0].replace("🕒 ", "").strip()
                    reminder_text = text.split(" - ")[1].strip()
                    if date_str in self.reminders_by_date:
                        self.reminders_by_date[date_str] = [
                            (t, ti) for (t, ti) in self.reminders_by_date[date_str]
                            if not (t == reminder_text and ti == time)
                        ]
                        if not self.reminders_by_date[date_str]:
                            del self.reminders_by_date[date_str]
                except Exception as e:
                    print(f"Could not parse reminder: {e}")
                self.account.reminders = self.reminders_by_date
                self.app.update_json_info(self.account, "reminders", self.reminders_by_date)
                self.reminder_list.takeItem(row)
                self.highlight_reminder_dates(self.calendar_widget)

    # Highlight days in calendar if there is a reminder
    def highlight_reminder_dates(self, calendar_widget):
        format = QTextCharFormat()
        format.setBackground(QColor("#cce0ff"))
        format.setForeground(QColor("#2c2f33"))

        for date_str in self.reminders_by_date:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            calendar_widget.setDateTextFormat(qdate, format)