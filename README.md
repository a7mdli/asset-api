# Asset API

A FastAPI service for tracking discovered assets and the relationships between them. It stores asset inventory records in PostgreSQL, supports filtering and pagination, and exposes relationship queries for building an asset graph.

## Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Uvicorn

## Project Structure

```text
app/
  api/            HTTP route handlers
  core/           Database configuration and session dependency
  crud/           Database operations used by the routes
  models/         SQLAlchemy models and enums
  schemas/        Pydantic request/response schemas
  main.py         FastAPI application entry point
```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   On macOS or Linux:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a PostgreSQL database:

   ```sql
   CREATE DATABASE assetdb;
   CREATE USER assetuser WITH PASSWORD 'password123';
   GRANT ALL PRIVILEGES ON DATABASE assetdb TO assetuser;
   ```

4. Create a `.env` file in the project root:

   ```env
   DATABASE_URL=postgresql://assetuser:password123@localhost:5432/assetdb
   ```

5. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

The API is available at `http://localhost:8000`.

Interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

| Variable | Required | Description | Example |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | SQLAlchemy database connection string. The current models use PostgreSQL-specific `UUID` and `ARRAY` column types, so PostgreSQL is expected. | `postgresql://assetuser:password123@localhost:5432/assetdb` |

## Running

Development server with auto-reload:

```bash
uvicorn app.main:app --reload
```

Production-style local run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Database Notes

The application calls `Base.metadata.create_all(bind=engine)` during startup in `app/main.py`. This creates missing tables automatically, which is convenient for local development and small assessments.

There are currently no Alembic migrations. For production usage, add migrations before making schema changes or deploying to shared environments.

## Design Decisions and Assumptions

- The API is intentionally split into route, CRUD, model, and schema layers to keep HTTP concerns separate from persistence logic.
- PostgreSQL is assumed because the models use PostgreSQL UUIDs and array columns for asset tags.
- Asset `metadata` is exposed in the API, while the SQLAlchemy column is named `asset_metadata` to avoid colliding with SQLAlchemy's reserved `metadata` attribute.
- Assets are identified by UUIDs. `POST /assets/` can accept an optional `id` query parameter, and `POST /assets/import` requires each imported asset to include an `id`.
- Bulk import is idempotent by asset id. Existing assets have `last_seen`, `tags`, and `metadata` updated rather than creating duplicates.
- Pagination defaults to `page=1` and `page_size=20`, with a maximum page size of `100`.
- Sorting for asset listing defaults to `last_seen desc`. Unknown `sort_by` values fall back to `last_seen`.
- Relationships are directional at write time through `first_asset_id` and `second_asset_id`, but related-asset lookup returns matches where the requested asset is on either side.
- There is no authentication, authorization, rate limiting, or request auditing in the current implementation.
- The current startup path creates tables directly and does not seed sample data.

## Data Model

### Asset

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID | Primary key |
| `type` | enum | `domain`, `subdomain`, `ip_address`, `service`, `certificate`, `technology` |
| `value` | string | Asset value, such as a domain, IP address, service name, or technology |
| `status` | enum | `active`, `stale`, `archived` |
| `first_seen` | datetime | Set automatically on create |
| `last_seen` | datetime | Set automatically on create and refreshed during import for existing assets |
| `source` | string | Source that discovered or provided the asset |
| `tags` | string array | PostgreSQL array of labels |
| `metadata` | object | JSON metadata exposed as `metadata` in API responses |

### Relationship

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID | Primary key |
| `first_asset_id` | UUID | Source/first asset reference |
| `second_asset_id` | UUID | Target/second asset reference |
| `relationship_type` | enum | Relationship type |

Relationship types:

- `subdomain_of`
- `hosts`
- `resolves_to`
- `resolved_by`
- `secured_by`
- `runs`

## API Documentation

### Health and Discovery

The project does not currently define a dedicated health-check endpoint. Use FastAPI's generated OpenAPI schema at:

```http
GET /openapi.json
```

### Assets

#### Create Asset

```http
POST /assets/?id={optional_uuid}
```

Request body:

```json
{
  "type": "domain",
  "value": "example.com",
  "status": "active",
  "source": "scanner",
  "tags": ["external", "production"],
  "metadata": {
    "registrar": "Example Registrar"
  }
}
```

Response:

Returns the created asset object.

#### List Assets

```http
GET /assets/
```

Query parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `page` | integer | `1` | Must be `>= 1` |
| `page_size` | integer | `20` | Must be between `1` and `100` |
| `type` | enum | none | Filters by asset type |
| `status` | enum | none | Filters by asset status |
| `tag` | string | none | Filters assets containing the tag |
| `value` | string | none | Case-insensitive partial match on asset value |
| `sort_by` | string | `last_seen` | Allowed: `value`, `type`, `status`, `first_seen`, `last_seen`, `source` |
| `sort_order` | string | `desc` | Use `asc` for ascending; all other values sort descending |

Response:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000000",
      "type": "domain",
      "value": "example.com",
      "status": "active",
      "first_seen": "2026-06-28T10:00:00Z",
      "last_seen": "2026-06-28T10:00:00Z",
      "source": "scanner",
      "tags": ["external"],
      "metadata": {}
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

#### Get Asset

```http
GET /assets/{asset_id}
```

Path parameters:

| Parameter | Type | Notes |
| --- | --- | --- |
| `asset_id` | UUID | Asset id |

Responses:

- `200 OK` with the asset object
- `404 Not Found` when the asset does not exist

#### Update Asset

```http
PUT /assets/{asset_id}
```

All request fields are optional:

```json
{
  "type": "subdomain",
  "value": "api.example.com",
  "status": "active",
  "source": "scanner",
  "tags": ["api"],
  "metadata": {
    "owner": "security"
  }
}
```

Responses:

- `200 OK` with the updated asset object
- `404 Not Found` when the asset does not exist

#### Delete Asset

```http
DELETE /assets/{asset_id}
```

Responses:

```json
{
  "message": "Deleted"
}
```

Returns `404 Not Found` when the asset does not exist.

#### Bulk Import Assets

```http
POST /assets/import
```

Request body:

```json
[
  {
    "id": "00000000-0000-0000-0000-000000000001",
    "type": "domain",
    "value": "example.com",
    "status": "active",
    "source": "scanner",
    "tags": ["external"],
    "metadata": {
      "confidence": "high"
    }
  }
]
```

Behavior:

- Creates new assets when `id` does not exist.
- Updates `last_seen`, merges tags, and merges metadata when `id` already exists.

Response:

Returns a list of imported asset objects.

#### Mark Asset Stale

```http
PATCH /assets/{asset_id}/stale
```

Responses:

- `200 OK` with the updated asset object where `status` is `stale`
- `404 Not Found` when the asset does not exist

### Relationships

#### Create Relationship

```http
POST /relationships/
```

Request body:

```json
{
  "first_asset_id": "00000000-0000-0000-0000-000000000001",
  "second_asset_id": "00000000-0000-0000-0000-000000000002",
  "relationship_type": "resolves_to"
}
```

Response:

```json
{
  "id": "00000000-0000-0000-0000-000000000003",
  "first_asset_id": "00000000-0000-0000-0000-000000000001",
  "second_asset_id": "00000000-0000-0000-0000-000000000002",
  "relationship_type": "resolves_to"
}
```

#### List Relationships

```http
GET /relationships/
```

Query parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `page` | integer | `1` | Must be `>= 1` |
| `page_size` | integer | `20` | Must be between `1` and `100` |
| `type` | enum | none | Filters by relationship type |

Response:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000003",
      "first_asset_id": "00000000-0000-0000-0000-000000000001",
      "second_asset_id": "00000000-0000-0000-0000-000000000002",
      "relationship_type": "resolves_to"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

#### Delete Relationship

```http
DELETE /relationships/{relationship_id}
```

Responses:

```json
{
  "message": "Deleted"
}
```

Returns `404 Not Found` when the relationship does not exist.

#### Get Related Assets

```http
GET /relationships/assets/{asset_id}/relationships
```

Returns relationships where the asset appears as either `first_asset_id` or `second_asset_id`.

Response:

```json
{
  "asset_id": "00000000-0000-0000-0000-000000000001",
  "relationships": [
    {
      "relationship_type": "resolves_to",
      "asset": {
        "id": "00000000-0000-0000-0000-000000000002",
        "type": "ip_address",
        "value": "203.0.113.10",
        "status": "active",
        "first_seen": "2026-06-28T10:00:00Z",
        "last_seen": "2026-06-28T10:00:00Z",
        "source": "scanner",
        "tags": ["external"],
        "asset_metadata": {}
      }
    }
  ]
}
```

## Example Requests

Create an asset:

```bash
curl -X POST "http://localhost:8000/assets/" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"domain\",\"value\":\"example.com\",\"status\":\"active\",\"source\":\"scanner\",\"tags\":[\"external\"],\"metadata\":{}}"
```

List active domains:

```bash
curl "http://localhost:8000/assets/?type=domain&status=active&page=1&page_size=20"
```

Create a relationship:

```bash
curl -X POST "http://localhost:8000/relationships/" \
  -H "Content-Type: application/json" \
  -d "{\"first_asset_id\":\"00000000-0000-0000-0000-000000000001\",\"second_asset_id\":\"00000000-0000-0000-0000-000000000002\",\"relationship_type\":\"resolves_to\"}"
```

