CREATE DATABASE MunchyDB;
USE MunchyDB;



CREATE TABLE customer (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE Admin (
    AdminID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Phone VARCHAR(20),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO Admin (FirstName, LastName, Email, Password, Phone)
VALUES (
    'Admin',
    'User',
    'munchadmin@gmail.com',
    'pbkdf2:sha256:600000$ABC123$xyzhashedvalue',  -- replace this
    '0123456789'
);
CREATE TABLE food (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    image VARCHAR(255),
    rating FLOAT,
    price INT
);

CREATE TABLE restaurant_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_name VARCHAR(100) NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    food_name VARCHAR(100) NOT NULL,
    image VARCHAR(255) NOT NULL,
    price INT NOT NULL,
    approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(255),
    owner_id INT,
    approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE delivery_address (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    location VARCHAR(100) NOT NULL,
    street VARCHAR(100) NOT NULL,
    apartment VARCHAR(50) NOT NULL,
    agent_message TEXT,
    accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES customer(id) ON DELETE CASCADE
);

CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES customer(id) ON DELETE CASCADE
);