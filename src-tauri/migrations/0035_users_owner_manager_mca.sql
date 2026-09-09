-- users.role had its own CHECK ('manager','worker'); widen it to the
-- owner/manager/mca model. SQLite can't alter a CHECK, so rebuild the
-- table preserving data and indexes. Legacy 'worker' rows become 'mca'
-- here (CHECK-safe, unlike an in-place UPDATE under the old CHECK).
-- Anything unexpected falls back to 'mca' (counter privilege, never admin).

CREATE TABLE users_new (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE COLLATE NOCASE,
  display_name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('owner','manager','mca')),
  is_active INTEGER NOT NULL DEFAULT 1,
  must_change_password INTEGER NOT NULL DEFAULT 0,
  created_by INTEGER REFERENCES users_new(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

INSERT INTO users_new (id, username, display_name, password_hash, role, is_active, must_change_password, created_by, created_at)
  SELECT id, username, display_name, password_hash,
    CASE role WHEN 'worker' THEN 'mca' WHEN 'owner' THEN 'owner' WHEN 'manager' THEN 'manager' ELSE 'mca' END,
    is_active, must_change_password, created_by, created_at
  FROM users;

DROP TABLE users;
ALTER TABLE users_new RENAME TO users;

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
