import os, subprocess, platform
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QScrollArea, QTableWidget, QTableWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt

from util_functs import security_check, get_desktop_files, run_report

# Class for the Automatic reports window
class Reports_page(QWidget):
    def __init__(self, account, app_status):
        super().__init__()
        self.account = account
        self.app = app_status
        self.status_label = QLabel("Status: Idle")
        main_layout = QVBoxLayout()

        # Store user-selected folders (None until set)
        self.production_reports_dir = None
        self.attendance_reports_dir = None
        self.agency_reports_dir = None

        title = QLabel("Automated Reports")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Horizontal layout for two columns
        horizontal_layout = QHBoxLayout()

        # Left Column
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.setContentsMargins(50, 50, 0, 0)
        left_layout.setSpacing(30)

        button_size = (250, 40)
        report_button_size = (150, 40)

        # --- Daily Production Report Buttons ---
        daily_btn = QPushButton("🧾 Daily Production Report")
        daily_btn.setFixedSize(*button_size)
        daily_btn.clicked.connect(lambda: run_report(
            "apps\\clock_in_out_main.py",
            self.account, 2, self.status_layout, self.app,
            preview_callback=lambda path: self.update_preview(path, sheet=3)
        ))

        report_btn_1 = QPushButton("📁 Reports")
        report_btn_1.setFixedSize(*report_button_size)
        # NEW: open selected folder, not hardcoded
        report_btn_1.clicked.connect(lambda: self.open_selected_folder("production"))

        select_prod_btn = QPushButton("Select Folder")
        select_prod_btn.setFixedSize(*report_button_size)
        select_prod_btn.clicked.connect(lambda: self.select_folder("production"))

        sub_horizontal_1 = QHBoxLayout()
        sub_horizontal_1.setContentsMargins(5, 5, 5, 5)
        sub_horizontal_1.setSpacing(10)
        sub_horizontal_1.addWidget(daily_btn)
        sub_horizontal_1.addWidget(report_btn_1)
        sub_horizontal_1.addWidget(select_prod_btn)

        # --- Attendance Report Buttons ---
        attendance_btn = QPushButton("🧾 Attendance Report")
        attendance_btn.setFixedSize(*button_size)
        attendance_btn.clicked.connect(lambda: run_report(
            "apps\\attendance_main.py",
            self.account, 2, self.status_layout, self.app,
            preview_callback=self.update_preview
        ))

        report_btn_2 = QPushButton("📁 Reports")
        report_btn_2.setFixedSize(*report_button_size)
        report_btn_2.clicked.connect(lambda: self.open_selected_folder("attendance"))

        select_att_btn = QPushButton("Select Folder")
        select_att_btn.setFixedSize(*report_button_size)
        select_att_btn.clicked.connect(lambda: self.select_folder("attendance"))

        sub_horizontal_2 = QHBoxLayout()
        sub_horizontal_2.setContentsMargins(5, 5, 5, 5)
        sub_horizontal_2.setSpacing(10)
        sub_horizontal_2.addWidget(attendance_btn)
        sub_horizontal_2.addWidget(report_btn_2)
        sub_horizontal_2.addWidget(select_att_btn)

        # --- Agency Report Buttons ---
        agency_btn = QPushButton("🧾 Agency Report")
        agency_btn.setFixedSize(*button_size)
        agency_btn.clicked.connect(lambda: run_report(
            "apps\\agency_main.py",
            self.account, 2, self.status_layout, self.app,
            preview_callback=lambda path: self.update_preview(path, sheet=2)
        ))

        report_btn_3 = QPushButton("📁 Reports")
        report_btn_3.setFixedSize(*report_button_size)
        report_btn_3.clicked.connect(lambda: self.open_selected_folder("agency"))

        select_agency_btn = QPushButton("Select Folder")
        select_agency_btn.setFixedSize(*report_button_size)
        select_agency_btn.clicked.connect(lambda: self.select_folder("agency"))

        sub_horizontal_3 = QHBoxLayout()
        sub_horizontal_3.setContentsMargins(5, 5, 5, 5)
        sub_horizontal_3.setSpacing(10)
        sub_horizontal_3.addWidget(agency_btn)
        sub_horizontal_3.addWidget(report_btn_3)
        sub_horizontal_3.addWidget(select_agency_btn)

        sub_horizontals = [sub_horizontal_1, sub_horizontal_2, sub_horizontal_3]
        for sub in sub_horizontals:
            container = QWidget()
            container.setLayout(sub)
            left_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.setSpacing(10)
        left_layout.addSpacing(40)

        # Show reports preview once a report has been generated
        self.preview_scroll_area = QScrollArea()
        self.preview_scroll_area.setStyleSheet("background-color: #e0e0e0; border: 1px solid #ccc; border-radius: 5px;")
        self.preview_scroll_area.setFixedSize(800, 500)
        self.preview_scroll_area.setWidgetResizable(True)

        self.preview_content = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_content)

        preview_label = QLabel("Preview")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_layout.addWidget(preview_label)

        self.preview_scroll_area.setWidget(self.preview_content)
        left_layout.addWidget(self.preview_scroll_area, alignment=Qt.AlignmentFlag.AlignHCenter)

        # --- Right Column: File List, Status, etc ---
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.setContentsMargins(50, 50, 0, 0)
        right_layout.setSpacing(5)

        xlsx_files = get_desktop_files()

        file_num_label = QLabel(self.get_string(xlsx_files))
        file_num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(file_num_label)

        # Create a container for file names
        file_container = QWidget()
        file_container.setObjectName("FileContainer")
        file_layout = QVBoxLayout()

        for file in xlsx_files:
            file_name = os.path.basename(file)
            label = QLabel(file_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            file_layout.addWidget(label)

        file_container.setLayout(file_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(300)
        scroll_area.setWidget(file_container)
        right_layout.addWidget(scroll_area)
        right_layout.addStretch()

        # Add status box
        status_container = QWidget()
        status_container.setObjectName("StatusContainer")
        status_layout = QVBoxLayout()
        status_container.setLayout(status_layout)

        # Save for later use
        self.status_layout = status_layout

        self.status_label = QLabel("Status: Idle")
        self.status_layout.addWidget(self.status_label)

        status_scroll_area = QScrollArea()
        status_scroll_area.setWidgetResizable(True)
        status_scroll_area.setFixedHeight(150)
        status_scroll_area.setWidget(status_container)

        right_layout.addWidget(status_scroll_area)
        right_layout.addStretch()

        # Add both vertical layouts to the horizontal layout
        horizontal_layout.addLayout(left_layout)
        horizontal_layout.addLayout(right_layout)

        # Add horizontal layout to main layout
        main_layout.addLayout(horizontal_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def get_string(self, xlsx_files):
        if len(xlsx_files) > 1:
            return f"There are {len(xlsx_files)} excel files on the desktop:"
        elif len(xlsx_files) == 1:
            return f"There is {len(xlsx_files)} excel file on the desktop:"
        else:
            return f"There are no excel files in the desktop"

    def select_folder(self, report_type):
        folder = QFileDialog.getExistingDirectory(self, "Select Reports Folder")
        if folder:
            if report_type == "production":
                self.production_reports_dir = folder
            elif report_type == "attendance":
                self.attendance_reports_dir = folder
            elif report_type == "agency":
                self.agency_reports_dir = folder
            QMessageBox.information(self, "Folder Selected", f"Folder selected for {report_type}: {folder}")

    def open_selected_folder(self, report_type):
        if report_type == "production":
            folder = self.production_reports_dir
        elif report_type == "attendance":
            folder = self.attendance_reports_dir
        elif report_type == "agency":
            folder = self.agency_reports_dir
        else:
            folder = None

        if folder is None or not os.path.isdir(folder):
            QMessageBox.warning(self, "No Folder Selected",
                "No folder has been selected yet. Please click 'Select Folder' first.")
            return

        self.open_folder(folder)

    def open_folder(self, path):
        _pass = security_check(self.account.security_level, 1)

        if not os.path.isdir(path):
            QMessageBox.critical(self, "Error", f"The path '{path}' does not exist or is not a directory.")
            self.app.update_log_info(self.account, "Open Folder Failed", f"Invalid path: {path}", False)
            return

        system_platform = platform.system()
        if _pass:
            if system_platform == "Windows":
                os.startfile(path)
            elif system_platform == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        else:
            QMessageBox.warning(self, "Access Denied", "You do not have permission to open this folder.")

        self.app.update_log_info(self.account, f"Open folder", f"Open folder at path: {path}", _pass)

    def update_preview(self, report_path, sheet=1):
        try:
            xls = pd.ExcelFile(report_path)
            available_sheets = xls.sheet_names

            if sheet > len(available_sheets):
                sheet = 1

            sheet_to_load = available_sheets[-sheet]
            df = pd.read_excel(report_path, sheet_name=sheet_to_load)

            rows_to_display = len(df)
            table = QTableWidget(rows_to_display, len(df.columns))
            table.setHorizontalHeaderLabels([str(col) for col in df.columns])

            for row in range(rows_to_display):
                for col in range(len(df.columns)):
                    value = str(df.iloc[row, col]) if not pd.isna(df.iloc[row, col]) else ""
                    table.setItem(row, col, QTableWidgetItem(value))

            table.resizeColumnsToContents()
            table.resizeRowsToContents()
            self.preview_scroll_area.setWidget(table)

        except Exception as e:
            report_label = QLabel(f"New Report: {os.path.basename(report_path)}")
            report_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            report_label.setStyleSheet("color: blue; text-decoration: underline; cursor: pointer;")
            report_label.mousePressEvent = lambda event: self.open_folder(os.path.dirname(report_path))
            self.preview_scroll_area.setWidget(report_label)
