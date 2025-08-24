# 📝 Python Logging: Beginner’s Guide

Logging is a way for your program to **report what it’s doing**.
Instead of just using `print()`, logging is **more powerful** because:
- You can control **how much detail** to show (levels).
- You can save logs to a **file** instead of the screen.
- You can **format** logs to include things like time, file, or line number.
- You can direct logs to different **destinations** (console, file, external system).

---
| Level      | Numeric Value | When to Use It                                                  |
| ---------- | ------------- | --------------------------------------------------------------- |
| `DEBUG`    | 10            | Very detailed info, useful only for developers while debugging. |
| `INFO`     | 20            | Normal events that confirm the program is working.              |
| `WARNING`  | 30            | Something unexpected happened, but the program still runs fine. |
| `ERROR`    | 40            | A problem that prevented part of the program from working.      |
| `CRITICAL` | 50            | A very serious problem, the program may crash.                  |


## 1. The Simplest Logger
```python
import logging
import logging

logging.basicConfig(level=logging.WARNING)

logging.debug("Debug message")   # NOT shown
logging.info("Info message")     # NOT shown
logging.warning("Warning message")  # ✅ shown
logging.error("Error message")     # ✅ shown
logging.critical("Critical message") # ✅ shown
```
👉 Output (example):
```
DEBUG:root:This is a DEBUG message
INFO:root:This is an INFO message
WARNING:root:This is a WARNING message
ERROR:root:This is an ERROR message
CRITICAL:root:This is a CRITICAL message
```

---

## 2. Logging Levels
Levels decide how **important** a log message is:

- `DEBUG` → Detailed info (good for developers).
- `INFO` → General program events (normal operation).
- `WARNING` → Something unexpected, but program continues.
- `ERROR` → A serious issue, program may not continue.
- `CRITICAL` → Very serious error, program is in trouble.

By default, only `WARNING` and above are shown unless you set `level` in `basicConfig`.

---

## 3. Formatting Logs
You can **control the look** of log messages.

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logging.info("App started")
logging.error("Something went wrong")
```

👉 Example output:
```
2025-08-24 10:20:15,345 - root - INFO - App started
2025-08-24 10:20:15,346 - root - ERROR - Something went wrong
```

**Common format fields:**
- `%(asctime)s` → Time
- `%(name)s` → Logger name
- `%(levelname)s` → Level
- `%(message)s` → The log text

---

## 4. Loggers, Handlers, and Formatters (The Trio)
Think of logging as a pipeline:
- **Logger** → the entry point (`logging.getLogger()`)
- **Handler** → decides *where* logs go (console, file, etc.)
- **Formatter** → decides *how* logs look

Example:
```python
import logging

# Create a logger
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)

# Create handler (send logs to file)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.ERROR)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)

# Logs
logger.debug("Debug message (won’t go to file)")
logger.error("Error message (will go to file)")
```
👉 This will save only **ERROR and above** messages into `app.log`.

---

## 5. Multiple Handlers
You can send logs to **console AND file** at the same time with different levels.

```python
import logging

logger = logging.getLogger("multi")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("errors.log")
file_handler.setLevel(logging.ERROR)

# Formatter
formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("This goes to console only")
logger.error("This goes to console AND file")
```

---

## 6. Best Practices
✅ Always use `logging` instead of `print()` for real apps.
✅ Use **different levels** for different situations.
✅ Send logs to **files** for later debugging.
✅ Use **formatters** to add timestamps.
✅ Use **different loggers** for different parts of your app (e.g., `logger = logging.getLogger("database")`).

---

⚡ **Next Steps:**
Practice by creating your own small script that:
1. Logs `INFO` messages to the console.
2. Logs `ERROR` messages to a file.
3. Uses a formatter that includes time and level.

## 🔹 Logging Formatters

### What are Formatters?
- A **formatter** controls the **structure and style** of log messages.
- It defines what details appear (time, level, message, file, etc.) and how they’re arranged.
- Formatters are attached to **handlers**, so each handler can format logs differently.

### 1. **Text Formatter (default style)**
The most common way: plain text with timestamp, logger name, level, and message.

```python
import logging

logger = logging.getLogger("text_example")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()

# Text formatter
text_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(text_formatter)

logger.addHandler(console_handler)

logger.info("This is a text log example")
```

**Output:**
```
2025-08-24 12:34:56,789 - text_example - INFO - This is a text log example
```

### 2. **JSON Formatter**
Useful when logs need to be structured for systems like **Elasticsearch, Kibana, or Logstash**.

```python
import logging, json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)

logger = logging.getLogger("json_example")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
json_formatter = JsonFormatter()
console_handler.setFormatter(json_formatter)

logger.addHandler(console_handler)

logger.info("This is a JSON log example")
```

**Output:**
```json
{"time": "2025-08-24 12:34:56", "level": "INFO", "logger": "json_example", "message": "This is a JSON log example"}
```

### 3. **CSV Formatter**
Sometimes logs are exported into spreadsheets or analysis tools.
We can create a **CSV-like formatter**.

```python
import logging

class CsvFormatter(logging.Formatter):
    def format(self, record):
        return f"{self.formatTime(record, self.datefmt)},{record.levelname},{record.name},{record.getMessage()}"

logger = logging.getLogger("csv_example")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
csv_formatter = CsvFormatter()
console_handler.setFormatter(csv_formatter)

logger.addHandler(console_handler)

logger.warning("This is a CSV log example")
```

**Output:**
```
2025-08-24 12:34:56,789,WARNING,csv_example,This is a CSV log example
```

👉 Summary:
- **Text** = human-friendly, console/debugging.
- **JSON** = machine-readable, structured logs for log aggregators.
- **CSV** = easy export for analysis in Excel or Pandas.
