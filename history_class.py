import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QScrollArea, QTableWidget, QTableWidgetItem,
    QComboBox, QDateEdit, QLineEdit, QSizePolicy)
from PyQt6.QtCore import Qt

# Create class for history window
class History_page(QWidget):
    def __init__(self, account, app_status):
        super().__init__()
        self.account = account
        self.app=app_status
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Read the logging information
        rows = self.app.log_info
        data = rows[1:]
        df = pd.DataFrame(data, columns=["Timestamp", "Username", "Idnumber", "Action", "Details", "Success", "Security level"])
        username = str(self.account.username).strip()
        df["Username"] = df["Username"].astype(str).str.strip()
        self.df = df[df["Username"] == username].copy()
        self.df["Security level"] = pd.to_numeric(self.df["Security level"], errors='coerce')
        self.df = self.df[self.df["Security level"] <= self.account.security_level]

        title = QLabel("Reports History")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        filter_bar = QHBoxLayout()

        # === Date ===
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDisplayFormat("yyyy-MM-dd")

        # === Action ===
        self.action_filter = QComboBox()
        self.action_filter.addItems(["All Actions", "Open Folder", "Create Report"])

        # === Search ===
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search details...")

        apply_button = QPushButton("Apply Filters")
        apply_button.clicked.connect(lambda: self.apply_filters(self.df.copy()))

        filter_bar.addWidget(QLabel("Date:"))
        filter_bar.addWidget(self.date_filter)
        filter_bar.addWidget(QLabel("Action:"))
        filter_bar.addWidget(self.action_filter)
        filter_bar.addWidget(self.search_bar)
        filter_bar.addWidget(apply_button)

        main_layout.addLayout(filter_bar)

        self.history_label = QScrollArea()
        self.history_label.setWidgetResizable(True)
        self.history_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout.addWidget(self.history_label, stretch=1)

        self.setLayout(main_layout)
        self.display_results(self.df)

    # Function for creating filters
    def apply_filters(self, df):
        try:
            # === Date ===
            selected_date = self.date_filter.date().toString("yyyy-MM-dd")
            if selected_date:
                df = df[df['Timestamp'].str.startswith(selected_date)]

            # === Action ===
            action_map = {
                "All Actions": None,
                "Open Folder": "Open folder",
                "Create Report": "Create new report",
                "Access Utilities": "Access Utilities",
                "Log in": "Log in",
                "Password changed": "Password changed"
            }

            selected_action = self.action_filter.currentText()
            mapped_action = action_map.get(selected_action)

            if mapped_action:
                df = df[df["Action"] == mapped_action]

            # === Search ===
            search_term = self.search_bar.text().lower()
            if search_term:
                df = df[df.apply(lambda row: search_term in str(row['Details']).lower(), axis=1)]

            self.display_results(df)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load log: {e}")

    # Display information based on the filters selected (All information by default)
    def display_results(self, df):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        if df.empty:
            content_layout.addWidget(QLabel("No records found."))
        else:
            table = QTableWidget(len(df), len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)

            for row in range(len(df)):
                for col in range(len(df.columns)):
                    value = str(df.iloc[row, col])
                    table.setItem(row, col, QTableWidgetItem(value))

            table.resizeColumnsToContents()
            table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            content_layout.addWidget(table)

        self.history_label.setWidget(content_widget)