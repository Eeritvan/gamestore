CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role TEXT NOT NULL
);

INSERT INTO roles(role) VALUES 
                            ('user'),
                            ('creator'),
                            ('moderator');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 25),
    password TEXT NOT NULL,
    joined DATE NOT NULL DEFAULT CURRENT_DATE,
    role INTEGER REFERENCES roles(id) DEFAULT 1
);

CREATE TABLE profile_picture (
    id SERIAL PRIMARY KEY,
    picturename TEXT,
    picturedata BYTEA
); 

CREATE TABLE profile (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT DEFAULT '' CHECK (LENGTH(bio) <= 500),
    picture_id INTEGER REFERENCES profile_picture(id) ON DELETE CASCADE,
    visible BOOLEAN NOT NULL DEFAULT TRUE
); 

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    title TEXT UNIQUE NOT NULL CHECK (LENGTH(title) >= 3 AND LENGTH(title) <= 50),
    description TEXT NOT NULL CHECK (LENGTH(description) <= 1000 ),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0 AND price < 1000),
    discount DECIMAL(10, 2) NOT NULL DEFAULT 1.00 CHECK (discount >= 0 AND discount <= 1),
    release_date DATE NOT NULL,
    release_time TIME NOT NULL,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL
);

INSERT INTO categories(category) VALUES 
                                    ('Action'),
                                    ('Adventure'),
                                    ('Horror'),
                                    ('Multiplayer'),
                                    ('Open World'),
                                    ('Platformer'),
                                    ('Puzzle'),
                                    ('Racing'),
                                    ('Shooting'),
                                    ('Sports'),
                                    ('Strategy'),
                                    ('Survival');

CREATE TABLE game_categories (
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) CHECK (category_id > 0)
);

CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    imagename TEXT,
    imagedata BYTEA
);

CREATE TABLE temp_images (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    imagename TEXT,
    imagedata BYTEA
);

CREATE TABLE library (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE SET NULL,
    deleted_title TEXT
);

CREATE TABLE wishlist (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE
);

CREATE TABLE cart (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE
);

CREATE TABLE reviews (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    edited DATE,
    rating TEXT NOT NULL,
    review TEXT NOT NULL
);

CREATE TABLE history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE SET NULL,
    deleted_title TEXT,
    date DATE NOT NULL,
    sum DECIMAL(10, 2) NOT NULL
);

CREATE TABLE balance (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00
    CHECK (amount >= 0)
);
