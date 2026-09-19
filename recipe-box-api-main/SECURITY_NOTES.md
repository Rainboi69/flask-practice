# Security baseline

2026-09-16

* GET /  ->  200 OK, anonymous requester received JSON: {"message": "Recipe Box API", "recipes": "/recipes"}
* \- GET /recipes  ->  500 Internal Server Error, anonymous requester triggered sqlite3.OperationalError: no such table: recipes (application error, not access control)

