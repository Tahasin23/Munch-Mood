-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 05, 2025 at 07:15 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `munchydb`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `AdminID` int(11) NOT NULL,
  `FirstName` varchar(50) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`AdminID`, `FirstName`, `LastName`, `Email`, `Password`, `Phone`, `CreatedAt`) VALUES
(1, 'Admin', 'User', 'munchadmin@gmail.com', 'pbkdf2:sha256:600000$ABC123$xyzhashedvalue', '0123456789', '2025-04-24 15:57:13');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`id`, `name`, `email`, `password_hash`, `created_at`) VALUES
(1, 'Rizwanul', 'riz123@gmail.com', 'scrypt:32768:8:1$5jpFSoZEE8d0WokL$bf077640a1b3a7aca759fa717b814601dff9f0d0f98549d5b075434f7499567192e03502f4a879e7dc9d1a91066dd625011494f070c509db3624247846824081', '2025-04-24 15:48:07'),
(2, 'Auntik', 'auntik123@gmail.com', 'scrypt:32768:8:1$JWOY6pEXFOwL5JFZ$d1f9c88c75e797351eb8a63fd8c56e1c4708c6fad98f0afdc2707c198dc8135b40a6928441e168098b37583ec21543df6fa929e04d284878691e69716b8a4148', '2025-04-25 05:50:35'),
(3, 'Tahasin', 'tahasin@gmail.com', 'scrypt:32768:8:1$ag8I3HbNO7zY6uM1$85052fa00ac6c347cb9d2263afb87bc52b17b15013387c26c455b0b22229beebe588b659ac18a9db60b915b7195ff68fe72dabb553f8b9579bc4c8520e298d70', '2025-05-05 13:18:37'),
(4, 'Toufik', 'toufik@gmail.com', 'scrypt:32768:8:1$Z0sMYtENnQJvwQzr$a9d69896cb65195ce039125d74d50bc35586ecb2dbc07bc99297c6224e28f47a2edcc9b0a22a2a24719923ab4e4a3673c1121fe3c83a03da84f817fde7892583', '2025-05-05 16:52:57');

-- --------------------------------------------------------

--
-- Table structure for table `delivery_address`
--

CREATE TABLE `delivery_address` (
  `id` int(11) NOT NULL,
  `user_id` bigint(20) UNSIGNED DEFAULT NULL,
  `location` varchar(100) NOT NULL,
  `street` varchar(100) NOT NULL,
  `apartment` varchar(50) NOT NULL,
  `agent_message` text DEFAULT NULL,
  `accepted` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `delivered` tinyint(1) DEFAULT 0,
  `food_id` int(11) NOT NULL,
  `hidden` tinyint(1) DEFAULT 0,
  `order_status` varchar(32) DEFAULT 'Order Placed',
  `payment_method` varchar(50) DEFAULT NULL,
  `payment_info` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `delivery_address`
--

INSERT INTO `delivery_address` (`id`, `user_id`, `location`, `street`, `apartment`, `agent_message`, `accepted`, `created_at`, `delivered`, `food_id`, `hidden`, `order_status`, `payment_method`, `payment_info`) VALUES
(6, 1, 'Azimpur', 'Road 13 , House 25', 'Apt 5b', NULL, 1, '2025-05-05 12:15:03', 1, 18, 0, 'Order Delivered', NULL, NULL),
(8, 3, 'Mirpur', 'Road 13 , House 25', 'Apt 4b', NULL, 1, '2025-05-05 13:20:34', 1, 29, 0, 'Order Delivered', NULL, NULL),
(10, 1, 'Azimpur', 'Road 13 , House 25', 'Apt 4b', NULL, 1, '2025-05-05 14:42:32', 1, 18, 0, 'Order Delivered', 'card', NULL),
(12, 1, 'Azimpur', 'Road 12 , House 24', 'Apt 5b', 'Your order has been delivered! Please leave a review.', 1, '2025-05-05 14:55:35', 1, 18, 0, 'Order Delivered', 'cash', NULL),
(13, 1, 'Azimpur', 'Road 12 , House 24', 'Apt 5b', 'Your order has been delivered! Please leave a review.', 1, '2025-05-05 16:51:05', 1, 29, 0, 'Order Delivered', 'cash', NULL),
(14, 1, 'Dhanmondi', 'Road 13 , House 25', 'Apt 5b', 'Your order has been delivered! Please leave a review.', 1, '2025-05-05 16:56:31', 1, 18, 0, 'Order Delivered', 'card', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `delivery_agents`
--

CREATE TABLE `delivery_agents` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `delivery_agents`
--

INSERT INTO `delivery_agents` (`id`, `name`, `email`, `password`) VALUES
(1, 'Tazree', 'tazree123@gmail.com', '12345');

-- --------------------------------------------------------

--
-- Table structure for table `food`
--

CREATE TABLE `food` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `restaurant_name` varchar(255) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `available` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `food`
--

INSERT INTO `food` (`id`, `name`, `image`, `rating`, `price`, `restaurant_name`, `category`, `available`) VALUES
(15, 'Nihari', 'nihari.jpg', 3, 250, 'Peshwari', 'asian', 1),
(16, 'Meatbox', 'meatbox.webp', 4.6, 150, 'Crunch', 'asian', 1),
(17, 'Pizza', 'pizza.webp', 5, 650, 'PizzaWala', 'asian', 1),
(18, 'FryBox', 'fry_box.webp', 5, 650, 'KFC', 'asian', 1),
(19, 'Burger', 'burger.png', 3.5, 250, 'chill house', 'asian', 1),
(20, 'pizza', 'pizza.webp', 3.2, 650, 'Peyala', 'asian', 1),
(21, 'Meatbox', 'meatbox.webp', 3.2, 130, 'Peshwari', 'chicken', 1),
(22, 'Burger', 'burger.png', 3.4, 340, 'Peshwari', 'asian', 1),
(23, 'Meatbox', 'uploads/meatbox.webp', 3.2, 150, 'Peshwari', 'chicken', 1),
(24, 'Meatbox', 'uploads/meatbox.webp', 0, 140, 'Peshwari', 'asian', 1),
(25, 'Nihari', 'uploads/nihari.jpg', 0, 120, 'Peshwari', 'asian', 1),
(26, 'Burger', 'uploads/burger.png', 0, 130, 'Peshwari', 'asian', 1),
(27, 'FryBox', 'uploads/fry_box.webp', 0, 340, 'chillox', 'asian', 1),
(28, 'Burger', 'uploads/burger.png', 0, 150, 'Peyala', 'asian', 1),
(29, 'Bashmoti Kacchi', 'uploads/bashmoti kacchi.webp', 4, 220, 'sultan dine', 'biryani', 1),
(30, 'Naga', 'uploads/Naga.jpg', 0, 200, 'Khanas', 'chicken', 1),
(31, 'Burger', 'uploads/burger.png', 0, 180, 'Kudos', 'burger', 1),
(32, 'Pasta', 'uploads/pasta.webp', 3, 124, 'Peshwari', 'asian', 1);

-- --------------------------------------------------------

--
-- Table structure for table `payment`
--

CREATE TABLE `payment` (
  `id` int(11) NOT NULL,
  `payment_method` varchar(20) NOT NULL,
  `card_number` varchar(24) DEFAULT NULL,
  `expiry` varchar(7) DEFAULT NULL,
  `cvc` varchar(5) DEFAULT NULL,
  `cardholder` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payment`
--

INSERT INTO `payment` (`id`, `payment_method`, `card_number`, `expiry`, `cvc`, `cardholder`, `created_at`) VALUES
(1, 'card', '103485628', '05/26', '575', 'Rizwan', '2025-05-03 18:35:47'),
(2, 'card', '1234567891212121', '11/22', '121', 'Rizwan', '2025-05-04 15:42:14'),
(3, 'card', '1211221211212112', '03/29', '222', 'Tahasin', '2025-05-05 14:43:15'),
(4, 'card', '1212121212121121', '02/24', '232', 'Rizwan', '2025-05-05 16:56:55');

-- --------------------------------------------------------

--
-- Table structure for table `restaurants`
--

CREATE TABLE `restaurants` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `approved` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `restaurants`
--

INSERT INTO `restaurants` (`id`, `name`, `image`, `owner_id`, `approved`) VALUES
(10, 'Peshwari', 'uploads/Peshwari.webp', NULL, 1),
(11, 'chillox', 'uploads/chillox.png', NULL, 1),
(12, 'Peyala', 'uploads/Peyala.webp', NULL, 1),
(13, 'sultan dine', 'uploads/sultan.jpg', NULL, 1),
(14, 'Khanas', 'uploads/khanas.jpg', NULL, 1),
(15, 'Kudos', 'uploads/Kudos.png', NULL, 1);

-- --------------------------------------------------------

--
-- Table structure for table `restaurant_accounts`
--

CREATE TABLE `restaurant_accounts` (
  `id` int(11) NOT NULL,
  `restaurant_name` varchar(100) NOT NULL,
  `owner_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `restaurant_accounts`
--

INSERT INTO `restaurant_accounts` (`id`, `restaurant_name`, `owner_name`, `email`, `password_hash`, `created_at`) VALUES
(1, 'Peshwari', 'Amir', 'amir123@gmail.com', 'scrypt:32768:8:1$Qo5hhcrX1TgVKSIp$00e66576ad675569abbcf0c385674e3feca3f0862fb69ed3ee08216956370b748cc05f6267d60af996e171853689ca2a8b8350119ff2c0f4bfab8e96db00ba1e', '2025-05-02 05:55:50'),
(2, 'sultan dine', 'Nayeem', 'nayeem@gmail.com', 'scrypt:32768:8:1$qtrnek2r8GuYDiuk$6999dea42ed8219221a0daa41c8bdf939c8a6f8bd9e0753da76a72fff8118c359dfc3468165c2cc2318ce39424b7289b350854e9f1df1f3342c1e4ae140224bc', '2025-05-05 06:21:51');

-- --------------------------------------------------------

--
-- Table structure for table `restaurant_requests`
--

CREATE TABLE `restaurant_requests` (
  `id` int(11) NOT NULL,
  `restaurant_name` varchar(100) NOT NULL,
  `owner_name` varchar(100) NOT NULL,
  `food_name` varchar(100) NOT NULL,
  `image` varchar(255) NOT NULL,
  `price` int(11) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `approved` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `restaurant_requests`
--

INSERT INTO `restaurant_requests` (`id`, `restaurant_name`, `owner_name`, `food_name`, `image`, `price`, `category`, `approved`) VALUES
(1, 'Peshwari', 'Amir', 'Nihari', 'nihari.jpeg', 350, NULL, 1),
(2, 'Crunch', 'Jamal', 'Meatbox', 'meatbox.webp', 140, NULL, 1),
(3, 'PizzaWala', 'Nayeem', 'Pizza', 'pizza.webp', 650, NULL, 1),
(4, 'KFC', 'Rizwan', 'FryBox', 'fry_box.webp', 800, NULL, 1),
(5, 'chill house', 'Tazree', 'pizza', 'pizza.webp', 222, NULL, 1),
(6, 'Peyala', 'Nayeem', 'Burger', 'burger.png', 120, NULL, 1),
(7, 'chillox', 'Mily', 'Pasta', 'pasta.webp', 100, NULL, 1),
(8, 'Digller', 'Sabbir', 'Nihari', 'nihari.jpg', 220, NULL, 1),
(9, 'Digger', 'Tahasin', 'Meatbox', 'meatbox.webp', 150, NULL, 1),
(10, 'Peshwari', 'Amir', 'Nihari', 'nihari.jpg', 355, 'asian', 1),
(11, 'Peshwari', 'Amir', 'Nihari', 'nihari.jpeg', 350, 'asian', 1),
(12, 'Peshwari', 'Amir', 'Nihari', 'nihari.jpg', 250, 'asian', 1),
(13, 'Crunch', 'Nayeem', 'Meatbox', 'meatbox.webp', 150, 'asian', 1),
(14, 'PizzaWala', 'Nayeem', 'Pizza', 'pizza.webp', 650, 'asian', 1),
(15, 'KFC', 'Rizwan', 'FryBox', 'fry_box.webp', 650, 'asian', 1),
(16, 'chill house', 'Jamal', 'Burger', 'burger.png', 250, 'asian', 1),
(17, 'Peyala', 'Tazree', 'pizza', 'pizza.webp', 650, 'asian', 1),
(18, 'Peshwari', 'Amir', 'Meatbox', 'meatbox.webp', 130, 'chicken', 1),
(19, 'Peshwari', 'Amir', 'Burger', 'burger.png', 340, 'asian', 1),
(20, 'Peshwari', 'Amir', 'Meatbox', 'uploads/meatbox.webp', 150, 'chicken', 1),
(21, 'Peshwari', 'Amir', 'Meatbox', 'uploads/meatbox.webp', 140, 'asian', 1),
(22, 'Peshwari', 'Amir', 'Nihari', 'uploads/nihari.jpg', 120, 'asian', 1),
(23, 'Peshwari', 'Amir', 'Burger', 'uploads/burger.png', 130, 'asian', 1),
(24, 'chillox', 'Amir', 'FryBox', 'uploads/fry_box.webp', 340, 'asian', 1),
(25, 'Peyala', 'Amir', 'Burger', 'uploads/burger.png', 150, 'asian', 1),
(26, 'sultan dine', 'Nayeem', 'Bashmoti Kacchi', 'uploads/bashmoti kacchi.webp', 220, 'biryani', 1),
(27, 'Khanas', 'Nayeem', 'Naga', 'uploads/Naga.jpg', 200, 'chicken', 1),
(28, 'Kudos', 'Tazree', 'Burger', 'uploads/burger.png', 180, 'burger', 1),
(29, 'Peshwari', 'Amir', 'Pasta', 'uploads/pasta.webp', 124, 'asian', 1);

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `food_id` int(11) NOT NULL,
  `user_id` bigint(20) UNSIGNED NOT NULL,
  `rating` int(11) NOT NULL,
  `review_text` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`id`, `food_id`, `user_id`, `rating`, `review_text`, `created_at`) VALUES
(2, 18, 1, 5, 'excellent', '2025-05-05 12:29:04'),
(3, 29, 3, 4, 'good', '2025-05-05 13:22:20'),
(4, 29, 1, 4, 'superr', '2025-05-05 15:10:13'),
(5, 17, 1, 5, 'good', '2025-05-05 16:58:54');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`AdminID`),
  ADD UNIQUE KEY `Email` (`Email`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `delivery_address`
--
ALTER TABLE `delivery_address`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `fk_food` (`food_id`);

--
-- Indexes for table `delivery_agents`
--
ALTER TABLE `delivery_agents`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `food`
--
ALTER TABLE `food`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `payment`
--
ALTER TABLE `payment`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `restaurants`
--
ALTER TABLE `restaurants`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `restaurant_accounts`
--
ALTER TABLE `restaurant_accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `restaurant_requests`
--
ALTER TABLE `restaurant_requests`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `food_id` (`food_id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `AdminID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `delivery_address`
--
ALTER TABLE `delivery_address`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `delivery_agents`
--
ALTER TABLE `delivery_agents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `food`
--
ALTER TABLE `food`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `payment`
--
ALTER TABLE `payment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `restaurants`
--
ALTER TABLE `restaurants`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `restaurant_accounts`
--
ALTER TABLE `restaurant_accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `restaurant_requests`
--
ALTER TABLE `restaurant_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `delivery_address`
--
ALTER TABLE `delivery_address`
  ADD CONSTRAINT `delivery_address_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `customer` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_food` FOREIGN KEY (`food_id`) REFERENCES `food` (`id`);

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`food_id`) REFERENCES `food` (`id`),
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `customer` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
