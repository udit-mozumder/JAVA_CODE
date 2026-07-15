# Data Model

## User
| Column | Type | Notes |
|--------|------|-------|
| id | UUID (str) | PK |
| google_id | str | unique, indexed |
| email | str | unique, indexed |
| display_name | str | nullable |
| avatar_url | str | nullable |
| is_active | bool | default true |
| created_at | datetime | |
| updated_at | datetime | |

## AuthAuditLog
| Column | Type | Notes |
|--------|------|-------|
| id | UUID (str) | PK |
| user_id | FK User | nullable |
| event_type | enum | LOGIN_SUCCESS / LOGIN_FAILURE / LOGOUT |
| ip_address | str | nullable |
| user_agent | str | nullable |
| failure_reason | str | nullable |
| created_at | datetime | |

## TokenDenylist
| Column | Type | Notes |
|--------|------|-------|
| id | UUID (str) | PK |
| jti | str | unique, indexed |
| user_id | FK User | nullable |
| expires_at | datetime | |
| created_at | datetime | |
