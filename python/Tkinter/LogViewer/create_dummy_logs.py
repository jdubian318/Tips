import random
from datetime import datetime, timedelta

# ログの設定
LOG_LEVELS = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]
MESSAGES = [
    "User logged in successfully",
    "Database connection established",
    "Failed to fetch data from API",
    "Timeout occurred while waiting for response",
    "Disk space reaching 90% threshold",
    "Connection to server lost",
    "Initialising background worker process",
    "Query executed: SELECT * FROM users",
    "Syntax error in configuration file line 42",
    "Memory leak detected in module 'auth'",
]

def generate_logs(filename="test_logs.txt", count=1000):
    start_time = datetime.now() - timedelta(days=1)
    
    with open(filename, "w", encoding="utf-8") as f:
        for i in range(count):
            # 1秒ごとに進むタイムスタンプ
            timestamp = (start_time + timedelta(seconds=i)).strftime("%Y-%m-%d %H:%M:%S")
            level = random.choice(LOG_LEVELS)
            msg = random.choice(MESSAGES)
            
            # 特定の単語が含まれる場合にエラー詳細を付け足す（テスト用）
            detail = ""
            if level in ["ERROR", "CRITICAL"]:
                detail = f" - [Code: {random.randint(100, 500)}] Exception: {random.choice(['NullPointer', 'IOException', 'KeyError'])}"
            
            log_line = f"[{timestamp}] {level.ljust(8)}: {msg}{detail}"
            f.write(log_line + "\n")
    
    print(f"Created: {filename} ({count} lines)")

if __name__ == "__main__":
    generate_logs()
