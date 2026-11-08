
## 3. Users Service Endpoints (port 5001)

The Users service owns user accounts and issues tokens. It has its own database (`instance/users.db`) and its own migrations.

### POST /register
- **Request:** JSON with `email` and `password`.
- **Behavior:** Hashes the password with Werkzeug and stores only the hash in `password_hash`.
- **Success:** `201 Created` with the new user's `id` and `email`. The password and hash are never returned.
- **Errors:** `400` if `email` or `password` is missing. `409` if the email is already registered.

### POST /login
- **Request:** JSON with `email` and `password`.
- **Behavior:** Looks up the user by email and checks the password against the stored hash. If valid, it returns a signed JWT (HS256) that expires after 60 minutes.
- **Success:** `200 OK` with `{"access_token": "<jwt>"}`.
- **Errors:** `400` if a field is missing. `401` with the same message for an unknown email or a wrong password, so callers cannot tell which emails exist.

### JWT Claims
| Claim | Meaning |
|---|---|
| `sub` | The numeric user id, stored as a string (for example `"1"`). PyJWT requires `sub` to be a string. |
| `iat` | When the token was issued. |
| `exp` | When the token expires (60 minutes after `iat`). |

The Recipes service verifies the token with the shared `JWT_SECRET`, converts `sub` with `int(...)`, and compares it to `recipe.owner_id`. If they match, access is allowed. If not, it returns `403 Forbidden`.
