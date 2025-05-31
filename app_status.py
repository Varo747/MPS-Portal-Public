import os, csv, json, io
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

# === File paths and key locations ===
KEY_JSON = os.path.join("app_resources", "json.key")     # Key file for encrypting/decrypting user JSON
KEY_CSV = os.path.join("app_resources", "csv.key")       # Key file for encrypting/decrypting log CSV
USER_FILE = os.path.join("app_resources", "users_example.json.enc")  # Encrypted user database
LOG_FILE = os.path.join("app_resources", "log_info_example.csv.enc") # Encrypted log database

class App_status():
    """
    Core class for managing application status, user authentication,
    encrypted file handling, logging, and reporting utilities.
    """
    def __init__(self):
        # Load application version and initialize core data
        self.app_version = "1.0"
        self.health_check = self.check_system_health()   # List of detected problems, if any
        self.user_info = self.decrypt_file(USER_FILE)    # Decrypted user dictionary
        self.log_info = self.decrypt_file(LOG_FILE)      # Decrypted log list
        self.weekly_info = self.create_summary()         # Weekly activity summary
        self.day_check = self.report_check(self.check_on_day())  # Daily report checks

    def check_system_health(self):
        """
        Checks for the existence and readability of critical encrypted files.
        Returns a list of errors found, or an empty string if everything is fine.
        """
        issues = []
        base_path = "app_resources"

        # Check existence and readability of encrypted log file
        log_file = os.path.join(base_path, "log_info_example.csv.enc")
        if not os.path.exists(log_file):
            issues.append("❌ Missing log_info_example.csv file.")
        else:
            try:
                log_rows = self.decrypt_file(log_file)
                if len(log_rows) < 2:
                    issues.append("⚠️ Log file exists but seems empty or incomplete.")
            except Exception as e:
                issues.append(f"❌ Failed to decrypt or read log_info_example.csv.enc: {e}")

        # Check existence and readability of encrypted user file
        user_file = os.path.join(base_path, "users_example.json.enc")
        if not os.path.exists(user_file):
            issues.append("❌ Missing users_example.json file.")
        else:
            try:
                user_info = self.decrypt_file(user_file)
                if not user_info or not isinstance(user_info, dict):
                    issues.append("⚠️ users_example.json is empty or invalid.")
            except Exception as e:
                issues.append(f"❌ Failed to decrypt or read users_example.json.enc: {e}")

        return issues if issues else ""

    def update_last_login(self, account):
        """
        Updates the user's last_login timestamp in the user info.
        """
        now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.update_json_info(account, "last_login", now)

    def save_last_session(self, username):
        """
        Saves the last session username to a local JSON file for auto-login.
        """
        try:
            with open("last_session.json", "w") as f:
                json.dump({"username": username}, f)
        except Exception as e:
            print(f"[ERROR saving last session]: {e}")

    def load_last_session(self):
        """
        Loads the last session username if present.
        """
        try:
            with open("last_session.json", "r") as f:
                return json.load(f).get("username")
        except Exception as e:
            print(f"[ERROR loading last session]: {e}")
            return None

    def get_week_info(self):
        """
        Retrieves all log entries generated during the current week.
        Returns a list of log rows.
        """
        file_path = os.path.join("app_resources", "log_info.csv")

        if not os.path.exists(file_path):
            return []

        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        weekly_logs = []

        # Parse each row, filter by week
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or len(row) < 1:
                    continue
                try:
                    timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    print(f"⚠️ Skipping invalid timestamp: {row[0]} - {e}")
                    continue

                if start_of_week.date() <= timestamp.date() <= end_of_week.date():
                    weekly_logs.append(row)

        return weekly_logs

    def report_check(self, logs):
        """
        Checks which daily reports are pending (Attendance, Production, Agency).
        Returns a string with the pending tasks, or a confirmation if all are done.
        """
        to_return = ["- Attendance Report", "- Production Report", "- Agency Report"]

        # Only consider logs with "create new report" action
        pending_reports = [
            row for row in logs
            if "create new report" in row["Action"].lower()
        ]

        # Remove from the list if already submitted
        for row in pending_reports:
            if "Attendance" in row["Details"]:
                to_return[0] = ""
            elif "Production" in row["Details"]:
                to_return[1] = ""
            elif "Agency" in row["Details"]:
                to_return[2] = ""

        task_lines = [task for task in to_return if task]
        return "\n".join(task_lines) if task_lines else "No pending tasks today ✅"

    def create_summary(self):
        """
        Builds a weekly report summary: how many reports submitted, per type, and checks for over/under-reporting.
        Returns a formatted summary string.
        """
        weekly_info = self.get_week_info()
        weekly_report_aim = 11
        total_reports = 0
        production_reports = 0
        attendance_reports = 0
        agency_reports = 0

        # Aggregate by type
        for row in weekly_info:
            if "Create new report" in row[3]:
                total_reports += 1
                if "Production" in row[4]: production_reports += 1
                elif "Attendance" in row[4]: attendance_reports += 1
                elif "Agency" in row[4]: agency_reports += 1

        # Determine summary message
        if total_reports < weekly_report_aim:
            summary_line = f"A total of {total_reports} of the expected {weekly_report_aim} reports have been generated this week."
        elif total_reports == weekly_report_aim:
            summary_line = f"The weekly reporting goal of {weekly_report_aim} has been successfully met."
        else:
            summary_line = (
                f"A total of {total_reports} reports were generated this week, exceeding the expected {weekly_report_aim}. "
                "This may indicate duplicate submissions or report generation errors."
            )

        report_breakdown = (
            f"\n\n📊 Weekly Report Summary:\n"
            f"- Production Reports: {production_reports}\n"
            f"- Attendance Reports: {attendance_reports}\n"
            f"- Agency Reports: {agency_reports}"
        )

        return summary_line + report_breakdown

    def load_key(self, path):
        """
        Loads an encryption/decryption key from the given file path.
        """
        with open(path, "rb") as key_file:
            return key_file.read()

    def encrypt_file(self, input_path, output_file):
        """
        Encrypts a CSV or JSON file (or raw binary) and saves the encrypted file.
        Picks the right key based on the file type.
        """
        name = os.path.basename(input_path).lower()
        if "log_info" in name:
            key_path = KEY_CSV
            with open(input_path, "r", encoding="utf-8") as infile:
                data = infile.read().encode("utf-8")
        elif "user" in name:
            key_path = KEY_JSON
            with open(input_path, "r", encoding="utf-8") as infile:
                json_obj = json.load(infile)
            data = json.dumps(json_obj).encode("utf-8")
        else:
            key_path = KEY_JSON
            with open(input_path, "rb") as infile:
                data = infile.read()
        key = self.load_key(key_path)
        f = Fernet(key)
        encrypted = f.encrypt(data)
        with open(output_file, "wb") as file:
            file.write(encrypted)

    def decrypt_file(self, input_path):
        """
        Decrypts the given encrypted file.
        Returns a CSV as a list, JSON as dict, or bytes if neither.
        """
        name = os.path.basename(input_path).lower()
        if "log_info" in name:
            key_path = KEY_CSV
        elif "user" in name:
            key_path = KEY_JSON
        else:
            key_path = KEY_JSON
        key = self.load_key(key_path)
        f = Fernet(key)
        with open(input_path, "rb") as file:
            encrypted = file.read()
        decrypted = f.decrypt(encrypted)
        if "log_info" in name:
            text = decrypted.decode("utf-8")
            return list(csv.reader(io.StringIO(text)))
        elif "user" in name:
            return json.loads(decrypted.decode("utf-8"))
        else:
            return decrypted

    def update_json_info(self, account, key, change):
        """
        Update a user's value in the user JSON, then re-encrypt the file.
        Uses a temp file in app_resources for safe editing.
        """
        self.user_info[account.username][key] = change

        temp_path = os.path.join("app_resources", "user_info_temp.json")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.user_info, f, indent=4)

        self.encrypt_file(temp_path, USER_FILE)

        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"File could not be deleted: {e}")

    def update_log_info(self, account, action, details, _pass, security_level=1):
        """
        Appends a log entry to the encrypted CSV log file.
        Handles decryption, appending, re-encryption, and temp file cleanup.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = [timestamp, account.username, account.id, action, details, _pass, security_level]

        temp_csv = os.path.join("app_resources", "log_info_temp.csv")
        enc_path = LOG_FILE

        # Read and decrypt existing logs (if any)
        log_rows = []
        if os.path.exists(enc_path):
            try:
                log_rows = self.decrypt_file(enc_path)
            except Exception as e:
                print(f"Could not decrypt existing log: {e}")

        # Create header if empty/new
        if not log_rows:
            log_rows = [["Timestamp", "Username", "UserID", "Action", "Details", "Pass/Fail", "Security Level"]]

        log_rows.append(log_entry)

        with open(temp_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(log_rows)

        self.encrypt_file(temp_csv, enc_path)
        try:
            os.remove(temp_csv)
        except Exception as e:
            print(f"Temp log CSV could not be deleted: {e}")

    def update_report_count(self, account, report_type):
        """
        Increments the count for the given report type and total for the user.
        Re-encrypts the user info file.
        """
        self.user_info[account.username]["reports"][report_type] += 1
        self.user_info[account.username]["reports"]["Total"] += 1

        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        temp_path = os.path.join(documents_path, "user_info_temp.json")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.user_info, f, indent=4)

        self.encrypt_file(temp_path, USER_FILE)

        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"File could not be deleted: {e}")

    def check_on_day(self, date_str=None):
        """
        Returns all log entries for a specific date (defaults to today).
        Output: List of dicts (one per matching log row).
        """
        rows = self.log_info[1:] if len(self.log_info) > 1 else []
        if date_str is None:
            date_str = datetime.today().strftime("%Y-%m-%d")

        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        results = []
        for row in rows:
            try:
                log_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").date()
                if log_date == target_date:
                    results.append({
                        "Timestamp": row[0],
                        "Username": row[1],
                        "Idnumber": row[2],
                        "Action": row[3],
                        "Details": row[4],
                        "Success": row[5],
                        "Security level": row[6]
                    })
            except Exception:
                continue
        return results