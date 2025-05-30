import os
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt

# Create class for user profile
class user():
    def __init__(self, users_info, username, password):
        self.username=username
        self.password=password
        self.id=users_info[username]["id"]
        self.role=users_info[username]["role"]
        self.mail=users_info[username]["mail"]
        self.department=users_info[username]["department"]
        self.reports=users_info[username]["reports"]
        self.last_log=users_info[username]["last_login"]
        self.account_creation=users_info[username]["account_creation"]
        self.user_image_path=os.path.join("app_resources", "images", "user_images", "default_user_image.png")
        self.notification=users_info[username]["notification"]
        self.reminders=users_info[username]["reminders"]

        security={"guest": 1, "staff": 2, "manager": 3, "admin": 4}
        self.security_level = security.get(self.role, 0)
    
    def create_rounded_profile_pixmap(self, image_path, size=48):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.lightGray)
        else:
            pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            w, h = pixmap.width(), pixmap.height()
            x = max(0, (w - size) // 2)
            y = max(0, (h - size) // 2)
            pixmap = pixmap.copy(x, y, size, size)
        rounded = QPixmap(size, size)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return rounded