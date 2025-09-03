# 🐍 Pydantic Settings

This is a complete lesson on **Pydantic Settings** (v2 with `pydantic-settings`), going step by step from minimal usage to advanced patterns with `model_config` and `PYTHONPATH` handling.

---

## 📦 Installation

```bash
pip install "pydantic>=2.0" "pydantic-settings>=2.0" python-dotenv
```

---

## 🔹 0. Why Pydantic Settings?

- Manage app config with **environment variables** and `.env` files.
- Instead of `os.getenv("VAR")` scattered everywhere:
  - ✅ Type validation
  - ✅ Defaults
  - ✅ Env override order
  - ✅ Nested structures
  - ✅ Secrets support

---

## 🔹 1. Minimal Example

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My App"
    debug: bool = False
    port: int = 8000

settings = Settings()
print(settings.app_name)  # "My App"
```

---

## 🔹 2. Environment Variable Override

```bash
export APP_NAME="ProdApp"
export DEBUG=true
export PORT=9000
```

```python
settings = Settings()
print(settings.app_name)  # "ProdApp"
```

---

## 🔹 3. Using `.env` Files

`.env` file:

```
APP_NAME=EnvApp
DEBUG=true
PORT=7000
```

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str
    debug: bool
    port: int

    model_config = SettingsConfigDict(env_file=".env")
```

---

## 🔹 4. Deep Dive: `model_config`

The **central control panel** for how settings are loaded.

```python
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent / ".env"

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),        # .env file
        env_file_encoding="utf-8",     # encoding
        case_sensitive=False,          # insensitive env var names
        env_prefix="APP_",             # all env vars prefixed
        env_nested_delimiter="__",     # nested model support
        extra="ignore",                # ignore unknown env vars
    )
```

### `model_config` Options
- **`env_file`**: one or more `.env` files (tuple allowed, ordered priority).
- **`env_file_encoding`**: default `"utf-8"`.
- **`case_sensitive`**: toggle strict casing.
- **`env_prefix`**: prepend to all vars (`APP_...`).
- **`env_nested_delimiter`**: flatten nested models (`DB__URL → db.url`).
- **`extra`**: `"ignore"` / `"forbid"` / `"allow"`.

👉 You can **override at runtime**:

```python
settings = Settings(
    _env_file=".env.dev",
    _case_sensitive=True
)
```

---

## 🔹 5. Nested Settings

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    url: str = "sqlite:///./test.db"
    pool_size: int = 10

class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"
    )
```

`.env` file:

```
DATABASE__URL=postgresql://user:pass@db/dbname
DATABASE__POOL_SIZE=20
```

---

## 🔹 6. Profiles (dev/staging/prod)

```python
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ProfiledApp"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            f".env.{os.getenv('ENV', 'dev')}"
        )
    )
```

👉 `ENV=prod` → loads `.env.prod`.

---

## 🔹 7. Secrets Support

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_key: str

    model_config = SettingsConfigDict(secrets_dir="/var/run/secrets")
```

File `/var/run/secrets/api_key` → `settings.api_key == "supersecret"`

---

## 🔹 8. Ultimate Example

```python
from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    url: str = "sqlite:///./app.db"
    pool_size: int = Field(10, ge=1, le=100)

class LoggingSettings(BaseModel):
    level: str = "INFO"
    json: bool = False

class HTTPSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

class SecuritySettings(BaseModel):
    cors_origins: list[HttpUrl] = []

class Settings(BaseSettings):
    app_name: str = "AvatarApp"
    debug: bool = False
    version: str = "1.0.0"

    http: HTTPSettings = HTTPSettings()
    log: LoggingSettings = LoggingSettings()
    db: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="APP_",
        env_nested_delimiter="__",
        extra="ignore"
    )
```

---

## 🔹 9. Integration with FastAPI

```python
from fastapi import FastAPI

settings = Settings()
app = FastAPI(title=settings.app_name)

@app.get("/info")
def info():
    return settings.model_dump()
```

---

## 🔹 10. PYTHONPATH and Settings

When working on structured projects:

```
project/
├── app/
│   ├── core/
│   │   └── config.py   # settings here
│   ├── main.py
├── .env
```

`config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AvatarApp"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

In `main.py`:

```python
from app.core.config import settings
print(settings.app_name)
```

### Problem: `ModuleNotFoundError: No module named 'app'`

👉 Solutions:
1. Run with module mode:
   ```bash
   python -m app.main
   ```
2. Add `PYTHONPATH`:
   ```bash
   export PYTHONPATH=$(pwd)
   python app/main.py
   ```
3. Use `.env` file:
   ```
   PYTHONPATH=.
   ```
   And load with `dotenv`.

This ensures **imports work consistently** across dev, test, and prod.

---

## 🔹 11. Testing Settings

```python
def configure_for_tests(env: dict) -> Settings:
    old_env = dict(os.environ)
    try:
        os.environ.update(env)
        return Settings(_env_file=None)  # ignore .env
    finally:
        os.environ.clear()
        os.environ.update(old_env)
```

---

## 🔹 12. Migration Notes (v1 → v2)

- **v1**:
  ```python
  class Config:
      env_file = ".env"
      env_prefix = "APP_"
  ```
- **v2**:
  ```python
  model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")
  ```

---

# ✅ Summary

- **`model_config`** = core for customizing env parsing.
- **`.env` files + env vars** integrated seamlessly.
- **Nested models** with `__`.
- **Profiles & secrets** supported.
- **PYTHONPATH** handling is crucial for imports in structured projects.

---

⚡ With this, you can handle **local dev, testing, production, and containerized deployments** — all with one unified config system.


---

# 📚 References for Pydantic Settings

## 🔹 Official Documentation
1. **Pydantic Settings (v2) Docs**
   👉 [https://docs.pydantic.dev/latest/concepts/pydantic_settings/](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
   - Official explanation of `BaseSettings`, `SettingsConfigDict`, env precedence, `.env` integration, and secrets.

2. **Pydantic v2 Main Docs**
   👉 [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)
   - Full reference for `BaseModel`, `model_config`, and validation.

3. **GitHub Repository**
   👉 [https://github.com/pydantic/pydantic-settings](https://github.com/pydantic/pydantic-settings)
   - Source code and issues (helpful to understand real-world usage, bug reports, and workarounds).

---

## 🔹 Articles & Tutorials
4. **RealPython – Settings with Pydantic** (v1 focus but concepts still valid for v2)
   👉 [https://realpython.com/python-pydantic/](https://realpython.com/python-pydantic/)

5. **FastAPI Advanced Config with Pydantic**
   👉 [https://fastapi.tiangolo.com/advanced/settings/](https://fastapi.tiangolo.com/advanced/settings/)
   - Shows how to integrate Pydantic Settings into FastAPI (uses v1 syntax, but easily translatable to v2).

6. **TestDriven.io – Environment Variables with Pydantic**
   👉 [https://testdriven.io/blog/fastapi-env-vars/](https://testdriven.io/blog/fastapi-env-vars/)

---

## 🔹 Migration & Version Notes
7. **Pydantic v1 → v2 Migration Guide**
   👉 [https://docs.pydantic.dev/latest/migration/](https://docs.pydantic.dev/latest/migration/)
   - Explains differences (e.g., `Config` → `model_config`, `.dict()` → `.model_dump()`).

---

## 🔹 Community & Discussions
8. **Stack Overflow – Pydantic Settings Questions**
   👉 [https://stackoverflow.com/questions/tagged/pydantic](https://stackoverflow.com/questions/tagged/pydantic)

9. **Discussions on GitHub**
   👉 [https://github.com/pydantic/pydantic/discussions](https://github.com/pydantic/pydantic/discussions)
