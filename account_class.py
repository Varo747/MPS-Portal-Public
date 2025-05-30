import os, shutil
from PyQt6.QtWidgets import (QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QSizePolicy, QDialog, QFileDialog)
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

# Create Account window
class Account_page(QWidget):
    def __init__(self, account, app):
        super().__init__()
        self.account = account
        self.app = app

        main_layout = QVBoxLayout()
        title = QLabel("Account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addSpacing(20)

        horizontal_layout = QHBoxLayout()

        # Left side 
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(50, 20, 0, 0)
        left_layout.setSpacing(15)

        self.avatar_label = QLabel()
        self.avatar_label.setObjectName("AvatarImage")
        self.avatar_label.installEventFilter(self)
        self.avatar_label.setPixmap(self.create_rounded_profile_pixmap(account.user_image_path))
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setFixedSize(300, 300)
        self.avatar_label.setScaledContents(True)
        left_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)

        change_avatar_picture_btn = QPushButton("Change Profile Picture")
        change_avatar_picture_btn.clicked.connect(self.change_profile_pic)
        left_layout.addWidget(change_avatar_picture_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # White box for user info
        user_info_container = QWidget()
        user_info_container.setObjectName("UserInfoBox")
        user_info_layout = QVBoxLayout(user_info_container)
        user_info_layout.setContentsMargins(15, 15, 15, 15)
        user_info_layout.setSpacing(10)

        labels = [
            QLabel(f"Username: {account.username}"),
            QLabel(f"Role: {account.role}"),
            QLabel(f"ID: {account.id}"),
            QLabel(f"Email: {account.mail}"),
            QLabel(f"Last login: {account.last_log}"),
            QLabel(f"Account created: {account.account_creation}"),
        ]

        for label in labels:
            label.setStyleSheet("margin: 0px; padding: 0px;")
            label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            user_info_layout.addWidget(label)

        left_layout.addWidget(user_info_container)

        # Change password button
        chg_pass_btn = QPushButton("Change password")
        chg_pass_btn.clicked.connect(self.change_password)
        chg_pass_btn.setFixedSize(150, 40)
        left_layout.addSpacing(30)
        left_layout.addWidget(chg_pass_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addStretch()

        # Right side
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 20, 0, 50)
        right_layout.setSpacing(20)

        pie_label = QLabel("Reports information")
        pie_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pie_chart = self.create_pie_chart()

        report_container = QWidget()
        report_container.setObjectName("ReportsInformation")
        report_container_layout = QVBoxLayout()
        report_container_layout.setContentsMargins(40, 0, 0, 0)
        report_container_layout.setSpacing(5)

        for key in ["Production", "Attendance", "Agency", "Total"]:
            label = QLabel(f"{key} Reports: {account.reports[key]}")
            label.setObjectName("ReportLabel")
            report_container_layout.addWidget(label)

        report_container.setLayout(report_container_layout)

        right_layout.addWidget(pie_label)
        right_layout.addWidget(self.pie_chart)
        right_layout.addWidget(report_container)

        # Final layout
        horizontal_layout.addLayout(left_layout)
        horizontal_layout.addLayout(right_layout)
        main_layout.addLayout(horizontal_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    # Make profile picture rounded and centered
    def create_rounded_profile_pixmap(self, image_path, size=300):
        original = QPixmap(image_path)
        if original.isNull():
            original = QPixmap(size, size)
            original.fill(Qt.GlobalColor.lightGray)

        w = original.width()
        h = original.height()
        side = min(w, h)
        x = (w - side) // 2
        y = (h - side) // 2
        square = original.copy(x, y, side, side)

        square = square.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

        rounded = QPixmap(size, size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, square)
        painter.end()
        
        return rounded
    
    # Add hover effect
    def eventFilter(self, obj, event):
        if obj == self.avatar_label:
            if event.type() == event.Type.Enter:
                self.avatar_label.setStyleSheet("border: 4px solid #3399ff; border-radius: 150px;")
            elif event.type() == event.Type.Leave:
                self.avatar_label.setStyleSheet("")
        elif obj == self.pie_chart_canvas:
            if event.type() == event.Type.Enter:
                self.pie_chart_canvas.setStyleSheet("border: 3px solid #00aa00;")
            elif event.type() == event.Type.Leave:
                self.pie_chart_canvas.setStyleSheet("background: transparent;")
        return super().eventFilter(obj, event)
    
    def change_profile_pic(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Images (*.png *.jpg *.jpeg *.bmp)"])
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]

            base_dir = os.path.dirname(os.path.abspath(__file__))
            dest_folder = os.path.join(base_dir, "app_resources", "images", "user_images")
            os.makedirs(dest_folder, exist_ok=True)

            dest_file = os.path.join(dest_folder, f"{self.account.username}.png")

            try:
                if os.path.exists(dest_file):
                    os.remove(dest_file)

                shutil.copyfile(selected_file, dest_file)

                self.account.user_image_path = dest_file
                self.app.update_json_info(self.account, "user_image_path", dest_file)

                new_pixmap = self.create_rounded_profile_pixmap(dest_file, size=300)
                self.avatar_label.setPixmap(new_pixmap)

                QMessageBox.information(self, "Success", "Profile picture updated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update profile picture:\n{e}")
    
    # Create pie chart with user information based on json file
    def create_pie_chart(self):
        reports = self.account.reports

        labels = []
        sizes = []
        for k in ["Production", "Attendance", "Agency"]:
            count = reports.get(k, 0)
            if count > 0:
                labels.append(k)
                sizes.append(count)

        if not sizes:
            labels = ["No reports"]
            sizes = [1]

        fig = Figure(figsize=(4, 4), facecolor='none')
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')
        wedges, _, _ = ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        ax.axis("equal")

        self.pie_chart_canvas = FigureCanvas(fig)
        self.pie_chart_canvas.setStyleSheet("background: transparent")

        self.pie_wedges = wedges
        self.pie_wedges_colors = [w.get_facecolor() for w in wedges]
        self.pie_chart_canvas.mpl_connect("motion_notify_event", self.on_pie_hover)

        return self.pie_chart_canvas
    
    # Add hover effect to the pie chart
    def darker_color(self, color, factor=0.7):
        rgb = mcolors.to_rgb(color)
        dark_rgb = tuple([max(0, c * factor) for c in rgb])
        if len(color) == 4:
            return dark_rgb + (color[3],)
        else:
            return dark_rgb
    
    def on_pie_hover(self, event):
        if event.inaxes is None:
            for i, w in enumerate(self.pie_wedges):
                w.set_facecolor(self.pie_wedges_colors[i])
            self.pie_chart_canvas.draw_idle()
            return

        for i, wedge in enumerate(self.pie_wedges):
            contains = wedge.contains_point((event.x, event.y))
            if contains:
                dark = self.darker_color(self.pie_wedges_colors[i], factor=0.7)
                wedge.set_facecolor(dark)
            else:
                wedge.set_facecolor(self.pie_wedges_colors[i])
        self.pie_chart_canvas.draw_idle()
        
    # Change password with minimum requirements and update json file
    def change_password(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Change Password")
        dialog.setFixedSize(400, 300)
        layout = QVBoxLayout(dialog)

        warning1 = QLabel("⚠️ Changing your password will log you out of all active sessions.")
        warning2 = QLabel("⚠️ This action cannot be undone.")
        warning3 = QLabel("⚠️ Password must be at least 8 characters, with one uppercase and one number.")
        for w in [warning1, warning2, warning3]:
            w.setWordWrap(True)
            w.setStyleSheet("color: red; font-size: 12px;")
            layout.addWidget(w)

        new_pass_input = QLineEdit()
        new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        new_pass_input.setPlaceholderText("New Password")
        confirm_pass_input = QLineEdit()
        confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_pass_input.setPlaceholderText("Confirm Password")
        layout.addWidget(new_pass_input)
        layout.addWidget(confirm_pass_input)

        confirm_btn = QPushButton("Confirm Change")
        layout.addWidget(confirm_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        def submit():
            new_pass = new_pass_input.text()
            confirm_pass = confirm_pass_input.text()

            if new_pass != confirm_pass:
                QMessageBox.warning(dialog, "Error", "Passwords do not match.")
                return
            if len(new_pass) < 8 or not any(c.isupper() for c in new_pass) or not any(c.isdigit() for c in new_pass):
                QMessageBox.warning(dialog, "Error", "Password does not meet complexity requirements.")
                return

            self.app.update_json_info(self.account, "password", new_pass)
            self.app.update_log_info(self.account, "Password changed", f"{self.account.username} changed password", True, security_level=2)
            QMessageBox.information(dialog, "Success", "Password changed successfully.")
            dialog.accept()

        confirm_btn.clicked.connect(submit)
        dialog.exec()