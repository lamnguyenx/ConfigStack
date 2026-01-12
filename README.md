# Multi-Layer Configuration Architecture

> **Summary**: This document describes a multi-layer configuration system with priority order (lowest to highest): (1) Code defaults, (2) Configuration files, (3) Lowercase-dotted environment variables, (4) Uppercase-underscored environment variables, (5) CLI arguments.

- [Multi-Layer Configuration Architecture](#multi-layer-configuration-architecture)
  - [Configuration Priority](#configuration-priority)
  - [Layer 1: Code Configuration Model (Lowest Priority)](#layer-1-code-configuration-model-lowest-priority)
    - [Python Implementation](#python-implementation)
    - [TypeScript Implementation](#typescript-implementation)
  - [Layer 2: Configuration File](#layer-2-configuration-file)
    - [Mapping Examples](#mapping-examples)
    - [TOML Configuration File](#toml-configuration-file)
  - [Layer 3: Lowercase-Dotted Environment Variables](#layer-3-lowercase-dotted-environment-variables)
    - [Mapping Examples](#mapping-examples-1)
  - [Layer 4: Uppercase-Underscored Environment Variables](#layer-4-uppercase-underscored-environment-variables)
    - [Mapping Examples](#mapping-examples-2)
  - [Layer 5: Command Line Arguments (Highest Priority)](#layer-5-command-line-arguments-highest-priority)
    - [Mapping Examples](#mapping-examples-3)

## Configuration Priority

The configuration system uses a **layered override approach** where each layer can override values from the previous layer:

- **Layer 1 (Code Defaults)**: Provides baseline default values (lowest priority)
- **Layer 2 (Config File)**: Overrides code defaults if specified
- **Layer 3 (Lowercase-Dotted Environment Variables)**: Overrides config file values
- **Layer 4 (Uppercase-Underscored Environment Variables)**: Overrides lowercase environment variables
- **Layer 5 (CLI Arguments)**: Overrides all other layers (highest priority)

**Example:**

| Configuration Layer                                   | Setting            | Resolved Value          |
| ----------------------------------------------------- | ------------------ | ----------------------- |
| Code Default (Layer 1)                                | port = 3000        | 3000                    |
| Configuration File (Layer 2)                          | port = 8080        | 8080                    |
| Lowercase-Dotted Environment Variables (Layer 3)      | app_name.port=5000 | 5000                    |
| Uppercase-Underscored Environment Variables (Layer 4) | APP_NAME_PORT=6000 | 6000                    |
| CLI Arguments (Layer 5)                               | --port 9000        | 9000 (highest priority) |

---

## Layer 1: Code Configuration Model (Lowest Priority)

The first layer defines the configuration structure with default values.

### Python Implementation

```python
import pydantic as pdt

# Default constants (Layer 1)
PORT_DEFAULT = 3000
HOST_DEFAULT = 'localhost'
DATABASE_URL_DEFAULT = 'postgresql://localhost/mydb'
DATABASE_PORT_DEFAULT = 5432
DATABASE_MAX_CONNECTIONS_DEFAULT = 100
CACHE_ENABLED_DEFAULT = True
CACHE_TTL_DEFAULT = 3600
CACHE_REDIS_HOST_DEFAULT = 'localhost'
API_TIMEOUT_DEFAULT = 30
API_RATE_LIMIT_DEFAULT = 100

class Config(pdt.BaseModel):
    port: int = PORT_DEFAULT
    host: str = HOST_DEFAULT

    class Database(pdt.BaseModel):
        url: str = DATABASE_URL_DEFAULT
        port: int = DATABASE_PORT_DEFAULT

        class Max(pdt.BaseModel):
            connections: int = DATABASE_MAX_CONNECTIONS_DEFAULT

        max: Max = pdt.Field(default_factory=Max)

    database: Database = pdt.Field(default_factory=Database)

    class Cache(pdt.BaseModel):
        enabled: bool = CACHE_ENABLED_DEFAULT
        ttl: int = CACHE_TTL_DEFAULT

        class Redis(pdt.BaseModel):
            host: str = CACHE_REDIS_HOST_DEFAULT

        redis: Redis = pdt.Field(default_factory=Redis)

    cache: Cache = pdt.Field(default_factory=Cache)

    class Api(pdt.BaseModel):
        timeout: int = API_TIMEOUT_DEFAULT

        class Rate(pdt.BaseModel):
            limit: int = API_RATE_LIMIT_DEFAULT

        rate: Rate = pdt.Field(default_factory=Rate)

    api: Api = pdt.Field(default_factory=Api)
```

### TypeScript Implementation

```typescript
interface Config {
  port: number;
  host: string;

  database: Config.Database;
  cache: Config.Cache;
  api: Config.Api;
}

namespace Config {
  export interface Database {
    url: string;
    port: number;
    max: Database.Max;
  }

  export namespace Database {
    export interface Max {
      connections: number;
    }
  }

  export interface Cache {
    enabled: boolean;
    ttl: number;
    redis: Cache.Redis;
  }

  export namespace Cache {
    export interface Redis {
      host: string;
    }
  }

  export interface Api {
    timeout: number;
    rate: Api.Rate;
  }

  export namespace Api {
    export interface Rate {
      limit: number;
    }
  }
}

const defaultConfig: Config = {
  port: PORT_DEFAULT,
  host: HOST_DEFAULT,
  database: {
    url: DATABASE_URL_DEFAULT,
    port: DATABASE_PORT_DEFAULT,
    max: {
      connections: DATABASE_MAX_CONNECTIONS_DEFAULT,
    },
  },
  cache: {
    enabled: CACHE_ENABLED_DEFAULT,
    ttl: CACHE_TTL_DEFAULT,
    redis: {
      host: CACHE_REDIS_HOST_DEFAULT,
    },
  },
  api: {
    timeout: API_TIMEOUT_DEFAULT,
    rate: {
      limit: API_RATE_LIMIT_DEFAULT,
    },
  },
};
```

## Layer 2: Configuration File

Configuration files (e.g., TOML) are overridden by environment variables and CLI arguments. They map directly to internal config paths using dot notation.

### Mapping Examples

| TOML Key                   | Internal Config Path                     |
| -------------------------- | ---------------------------------------- |
| `port`                     | `Config_Object.port`                     |
| `host`                     | `Config_Object.host`                     |
| `database.url`             | `Config_Object.database.url`             |
| `database.port`            | `Config_Object.database.port`            |
| `database.max.connections` | `Config_Object.database.max.connections` |
| `cache.enabled`            | `Config_Object.cache.enabled`            |
| `cache.ttl`                | `Config_Object.cache.ttl`                |
| `cache.redis.host`         | `Config_Object.cache.redis.host`         |
| `api.rate.limit`           | `Config_Object.api.rate.limit`           |
| `api.timeout`              | `Config_Object.api.timeout`              |

### TOML Configuration File

```toml
port = 8080
host = "localhost"

[database]
url = "postgresql://localhost/mydb"
port = 5432

[database.max]
connections = 100

[cache]
enabled = true
ttl = 3600

[cache.redis]
host = "localhost"

[api]
timeout = 30

[api.rate]
limit = 100
```

## Layer 3: Lowercase-Dotted Environment Variables

Lowercase-dotted environment variables provide a mid-priority configuration layer. All environment variables should be prefixed with `app_name.` where `app_name` is the lowercase name of your application. Since environment variable names containing dots require special handling, use the env command in shell scripts to set them.

**Example:**

```bash
env app_name.database.url="postgresql://localhost:5432" node app.js
```

### Mapping Examples

| Environment Variable                | Internal Config Path                     |
| ----------------------------------- | ---------------------------------------- |
| `app_name.port`                     | `Config_Object.port`                     |
| `app_name.host`                     | `Config_Object.host`                     |
| `app_name.database.url`             | `Config_Object.database.url`             |
| `app_name.database.port`            | `Config_Object.database.port`            |
| `app_name.database.max.connections` | `Config_Object.database.max.connections` |
| `app_name.cache.enabled`            | `Config_Object.cache.enabled`            |
| `app_name.cache.ttl`                | `Config_Object.cache.ttl`                |
| `app_name.cache.redis.host`         | `Config_Object.cache.redis.host`         |
| `app_name.api.rate.limit`           | `Config_Object.api.rate.limit`           |
| `app_name.api.timeout`              | `Config_Object.api.timeout`              |

## Layer 4: Uppercase-Underscored Environment Variables

Uppercase-underscored environment variables provide a high-priority configuration layer, overridden only by CLI arguments. They use single underscores (_) to represent dot notation in the config path, prefixed with the uppercase app name.

All environment variables should be prefixed with `APP_NAME_` where `APP_NAME` is the uppercase name of your application. Single underscores translate to dots in the internal config path.

**Example:**

```bash
APP_NAME_DATABASE_URL="postgresql://localhost:5432" node app.js
```

### Mapping Examples

| Environment Variable                | Internal Config Path                     |
| ----------------------------------- | ---------------------------------------- |
| `APP_NAME_PORT`                     | `Config_Object.port`                     |
| `APP_NAME_HOST`                     | `Config_Object.host`                     |
| `APP_NAME_DATABASE_URL`             | `Config_Object.database.url`             |
| `APP_NAME_DATABASE_PORT`            | `Config_Object.database.port`            |
| `APP_NAME_DATABASE_MAX_CONNECTIONS` | `Config_Object.database.max.connections` |
| `APP_NAME_CACHE_ENABLED`            | `Config_Object.cache.enabled`            |
| `APP_NAME_CACHE_TTL`                | `Config_Object.cache.ttl`                |
| `APP_NAME_CACHE_REDIS_HOST`         | `Config_Object.cache.redis.host`         |
| `APP_NAME_API_RATE_LIMIT`           | `Config_Object.api.rate.limit`           |
| `APP_NAME_API_TIMEOUT`              | `Config_Object.api.timeout`              |

## Layer 5: Command Line Arguments (Highest Priority)

CLI arguments provide the highest-priority configuration layer and override all other configuration sources. They map directly to internal config paths using dot notation.

**Example:**

```bash
node app.js --port 9000 --database.url "postgresql://localhost:5432"
```

### Mapping Examples

| CLI Argument                 | Internal Config Path                     |
| ---------------------------- | ---------------------------------------- |
| `--port`                     | `Config_Object.port`                     |
| `--host`                     | `Config_Object.host`                     |
| `--database.url`             | `Config_Object.database.url`             |
| `--database.port`            | `Config_Object.database.port`            |
| `--database.max.connections` | `Config_Object.database.max.connections` |
| `--cache.enabled`            | `Config_Object.cache.enabled`            |
| `--cache.ttl`                | `Config_Object.cache.ttl`                |
| `--cache.redis.host`         | `Config_Object.cache.redis.host`         |
| `--api.rate.limit`           | `Config_Object.api.rate.limit`           |
| `--api.timeout`              | `Config_Object.api.timeout`              |