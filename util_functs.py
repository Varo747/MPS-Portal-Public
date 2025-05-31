import os, glob, threading, subprocess
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, QObject, QTimer

# Python file with general functions used by the app

# Class for status feedback in automatic reports
class StatusEmitter(QObject):
    status_signal = pyqtSignal(str)
    preview_signal = pyqtSignal(str)

# Security check to ensure user can access a certain feature
def security_check(account_security, security_level):
    if account_security>=security_level: return True
    else: return False

def get_desktop_files():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    xlsx_files = glob.glob(os.path.join(desktop_path, "*.xlsx"))
    return xlsx_files

def run_report(path, account, security, status_layout: QVBoxLayout, app, preview_callback=None):
    emitter = StatusEmitter()

    def handle_status_update(message):
        if message.startswith("[PREVIEW_UPDATE]"):
            report_path = message.replace("[PREVIEW_UPDATE]", "").strip()
            if preview_callback and os.path.exists(report_path):
                QTimer.singleShot(0, lambda: preview_callback(report_path))
            else:
                emitter.status_signal.emit("⚠️ Report not found after generation.")
        else:
            status_label = QLabel(message)
            status_layout.addWidget(status_label)

    emitter.status_signal.connect(handle_status_update)

    def target(path):
        abs_path = os.path.abspath(path)
        script_dir = os.path.dirname(abs_path)

        emitter.status_signal.emit(f"Running script: {abs_path}")

        process = subprocess.Popen(
            ["python", abs_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=script_dir
        )

        report_path = None

        for line in process.stdout:
            line = line.strip()
            print("[SUBPROCESS]", line)  # ← imprime en consola para depurar
            if "[STATUS]" in line:
                status = line.replace("[STATUS]", "").strip()
                emitter.status_signal.emit(f"Status: {status}")
            elif "[REPORT_PATH]" in line:
                report_path = line.replace("[REPORT_PATH]", "").strip()
                emitter.status_signal.emit(f"[PREVIEW_UPDATE]{report_path}")

        process.stdout.close()
        process.wait()

        if report_path and os.path.exists(report_path) and preview_callback:
            QTimer.singleShot(0, lambda: preview_callback(report_path))
        elif report_path:
            emitter.status_signal.emit("⚠️ Report path detected but file does not exist.")
        else:
            emitter.status_signal.emit("❌ Report failed or did not return path.")

    to_log = "Unknown type"
    if security_check(account.security_level, security):
        emitter.status_signal.emit("Status: Security check passed")
        thread = threading.Thread(target=target, args=(path,))
        thread.start()

        if "attendance" in path: to_log = "Attendance"
        elif "clock" in path: to_log = "Production"
        elif "agency" in path: to_log = "Agency"

        app.update_report_count(account, to_log)
    else:
        emitter.status_signal.emit("Status: Action canceled due to security rights")

    app.update_log_info(account, "Create new report", f"{to_log} Report Created", True)