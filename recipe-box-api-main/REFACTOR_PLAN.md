# Refactor Plan for Recipe Box API

## Acceptance List (Current Public Behavior)

The purpose of this acceptance list is to document how my Recipe Box API currently works. During the BE105 refactor, I will preserve these behaviors while improving the internal structure of my application.

### 1. POST /register
- **Request:** JSON containing `username`, `email`, and `password`.
- **Authentication:** Not required.
- **Behavior:** Creates a new user account and securely hashes the password.
- **Expected response:** `201 Created` with the user's ID, username, email, and role.
- **Error response:** `409 Conflict` if the username or email already exists.

### 2. POST /login
- **Request:** JSON containing `username` and `password`.
- **Authentication:** Not required.
- **Behavior:** Verifies the user's credentials and generates a signed JWT.
- **Expected response:** `200 OK` with user information and an authentication token.
- **Error response:** `401 Unauthorized` for invalid login credentials.

### 3. GET /recipes
- **Request:** GET request without a JSON body.
- **Authentication:** Not required for public recipes.
- **Behavior:** Retrieves recipes that users are allowed to view.
- **Expected response:** `200 OK` with a JSON list of recipes.
- **Security requirement:** Private recipes must not be exposed to unauthorized users.

### 4. POST /recipes
- **Request:** JSON containing recipe details such as `title`, `ingredients`, `instructions`, and optionally `is_public`.
- **Authentication:** Requires a valid JWT using `Authorization: Bearer <token>`.
- **Behavior:** Creates a recipe associated with the authenticated user.
- **Expected response:** `201 Created` with the new recipe's information, including its ID and owner ID.
- **Error response:** `401 Unauthorized` if the authentication token is missing, invalid, or expired.

### 5. GET /recipes/<id>
- **Request:** GET request with a recipe ID in the URL.
- **Authentication:** Public recipes can be viewed without logging in. Private recipes require appropriate authorization.
- **Behavior:** Retrieves a specific recipe while checking whether the requester has permission to view it.
- **Expected response:** `200 OK` with the recipe's JSON information when access is allowed.
- **Error responses:**
  - `404 Not Found` if the recipe doesn't exist.
  - `403 Forbidden` if the requester is not authorized to view a private recipe.
- **Security requirement:** Private recipes must remain protected from unauthorized access.

### 6. PATCH /recipes/<id>
- **Request:** JSON containing recipe fields to update, such as `title`.
- **Authentication:** Requires a valid JWT.
- **Behavior:** Allows the recipe owner or an authorized administrator to update a recipe.
- **Expected response:** `200 OK` with the updated recipe information.
- **Error responses:**
  - `401 Unauthorized` for missing or invalid authentication.
  - `403 Forbidden` if the user doesn't have permission to update the recipe.
- **Security requirement:** Users cannot modify recipes belonging to other users unless they have administrator privileges.

### 7. DELETE /recipes/<id>
- **Request:** DELETE request with a recipe ID in the URL.
- **Authentication:** Requires a valid JWT.
- **Behavior:** Allows the recipe owner or an administrator to delete a recipe.
- **Expected response:** `204 No Content` with an empty response body.
- **Error responses:**
  - `404 Not Found` with `{"error": "recipe not found"}` if the recipe doesn't exist.
  - `403 Forbidden` with `{"error": "you do not have permission to delete this recipe"}` if the authenticated user is neither the owner nor an administrator.
  - Authentication errors are handled by `get_authenticated_user()`.
- **Security requirement:** Users cannot delete recipes belonging to other users unless they have administrator privileges.

### 8. GET /
- **Request:** GET request to the application's root URL.
- **Authentication:** Not required.
- **Behavior:** Provides a basic response confirming the Recipe Box API is running.
- **Expected response:** `200 OK` with JSON containing `message` and `recipes`.
- **Example response:** `{"message": "Recipe Box API", "recipes": "/recipes"}`.

## Acceptance Items Count

**Total documented acceptance items: 8**

These items cover all eight existing API routes. The DELETE behavior has been verified against the source code, while any remaining unverified response details should be checked before refactoring.

## Refactor Goal

My goal for BE105 is to improve the internal structure of my Recipe Box API without changing how it works for users.

Right now, my `app.py` handles multiple responsibilities, including configuration, database connections, authentication, user registration, recipe management, and permission checks.

I want to separate these responsibilities into smaller modules so my backend becomes easier to understand, troubleshoot, test, and maintain.

I also want to learn how to build a backend that remains reliable and secure as it grows.

## Current Responsibilities in app.py

1. **Configuration and application startup:** Loads environment variables, sets the JWT secret and database path, and creates the Flask application.
2. **Database connections and helpers:** Manages database connections and converts database records into JSON-friendly dictionaries.
3. **Authentication and JWT handling:** Creates and verifies authentication tokens.
4. **User registration and login:** Handles account creation, password hashing, and login verification.
5. **Recipe CRUD operations:** Handles creating, retrieving, updating, and deleting recipes.
6. **Authorization and permission checks:** Enforces recipe ownership, roles, and access restrictions.

**Total identified responsibilities: 6**

## Target Package Layout

Planned structure (no code moved yet):

```text
recipe-box-api-main/
├── wsgi.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── REFACTOR_PLAN.md
├── instance/
│   └── recipes.db
└── app/
    ├── __init__.py
    ├── config.py
    ├── auth/
    │   ├── __init__.py
    │   ├── routes.py
    │   └── helpers.py
    ├── recipes/
    │   ├── __init__.py
    │   ├── routes.py
    │   └── services.py
    └── db/
        ├── __init__.py
        └── helpers.py
```

## Responsibility Boundaries

My planned package structure separates the different responsibilities of my Recipe Box API.

- **app/auth/** will handle authentication, JWT creation and verification, and user registration/login routes.
- **app/recipes/** will handle recipe CRUD routes, recipe-specific business logic, and ownership permission checks.
- **app/db/** will manage database connections and low-level database queries.
- **app/config.py** will manage database paths, JWT secret configuration, and environment settings.
- **app/__init__.py** will create and configure the Flask application and register routes.
- **wsgi.py** will provide the application entry point.
- **instance/** will store the SQLite database separately from the application code.

Separating these responsibilities will make my API easier to troubleshoot, test, and maintain without changing how it works for users.

## Public Contract Preservation

During the refactor, I will preserve:

- Existing API endpoints and HTTP methods.
- Request formats and required JSON fields.
- Expected JSON response structures.
- HTTP status codes and error messages.
- JWT authentication requirements.
- Recipe ownership and role-based authorization.
- Public and private recipe access rules.

The internal organization of my code can change, but the existing behavior of my API must remain consistent.

## Refactor Safety Plan

Before making changes, I will:

1. Review the existing endpoints and their expected responses.
2. Use my previous BE104 curl commands and test results to verify current behavior.
3. Create a separate copy of my database for testing.
4. Document important authentication and authorization scenarios.
5. Confirm the public contract before moving code into separate modules.

During the refactor, I will make small changes and test each part to make sure I haven't broken existing functionality.

After the refactor, I will rerun the same API tests and compare the results with my acceptance list.

I will also keep sensitive information, such as JWT secrets, in environment variables rather than hard-coding them into the application.

## Countable Facts

- **Current app.py responsibilities:** 6
- **Acceptance list items:** 8
- **Existing API routes:** 8
- **Current application structure:** Single-file Flask API
- **Planned application structure:** Modular Flask package

These facts describe my Recipe Box API before the BE105 refactor.

## Personal BE105 Learning Goal

I want to become better at building backends that are organized, maintainable, secure, and reliable.

My BE104 project taught me how to build a working API with authentication and permission checks. BE105 will help me understand how to structure that API so it can grow without becoming difficult to manage.

The biggest lesson I want to take away is that improving the internal structure of an application should not change the experience of the people using it.

**This document is a planning guide only. No application code has been moved or refactored yet.**