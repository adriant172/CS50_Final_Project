-- SQLite

CREATE TABLE users (
  id INTEGER ,
  username TEXT,
  password_hash TEXT,
  points INTEGER,
  daily_budget NUMERIC,
  PRIMARY KEY(id)
);

CREATE TABLE recipes (
  id INTEGER,
  name TEXT,
  API_reference_id TEXT,
  num_of_shares INTEGER,
  num_of_ratings INTEGER,
  current_rating NUMERIC,
  PRIMARY KEY(id)
);

CREATE TABLE cuisine_tags (
  id INTEGER ,
  cuisine_type TEXT,
  PRIMARY KEY(id)
);

CREATE TABLE user_preferences (
  id INTEGER,
  user_id INTEGER,
  cuisine_id INTEGER,
  enabled BOOLEAN CHECK (Enabled IN (0, 1));
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(cuisine_id) REFERENCES cuisine_tags(id),
  PRIMARY KEY(id)
);

CREATE TABLE user_favorites (
  id INTEGER,
  user_id INTEGER,
  recipe_id INTEGER,
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(recipe_id) REFERENCES recipes(id),
  PRIMARY KEY(id)
);

CREATE TABLE "categorized_recipes" (
  id INTEGER,
  recipe_id INTEGER,
  cuisine_id INTEGER,
  FOREIGN KEY(recipe_id) REFERENCES recipes(id),
  FOREIGN KEY(cuisine_id) REFERENCES cuisine_tags(id),
  PRIMARY KEY(id)
);
