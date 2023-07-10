-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 10, 2023 at 07:37 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.1.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `movie_emotion`
--

-- --------------------------------------------------------

--
-- Table structure for table `captured_images`
--

CREATE TABLE `captured_images` (
  `id` int(11) NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `emotion` varchar(20) NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `captured_images`
--

INSERT INTO `captured_images` (`id`, `image_path`, `emotion`, `timestamp`) VALUES
(1484, 'history_images/1689010042.0251667.jpg', 'sad', '2023-07-11 00:27:22'),
(1485, 'history_images/1689010042.0550861.jpg', 'sad', '2023-07-11 00:27:22'),
(1486, 'history_images/1689010042.0770292.jpg', 'sad', '2023-07-11 00:27:22'),
(1487, 'history_images/1689010268.5158956.jpg', 'angry', '2023-07-11 00:31:08'),
(1488, 'history_images/1689010268.5308561.jpg', 'angry', '2023-07-11 00:31:08'),
(1489, 'history_images/1689010268.5667589.jpg', 'angry', '2023-07-11 00:31:08');

-- --------------------------------------------------------

--
-- Table structure for table `recommended_movies`
--

CREATE TABLE `recommended_movies` (
  `id` int(11) NOT NULL,
  `emotion` varchar(20) NOT NULL,
  `movie_title` varchar(255) NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `recommended_movies`
--

INSERT INTO `recommended_movies` (`id`, `emotion`, `movie_title`, `timestamp`) VALUES
(73, 'sad', 'Buzzin\' Around', '2023-07-10 21:00:21'),
(74, 'sad', 'Sunburn', '2023-07-10 21:00:21'),
(75, 'sad', 'Treasure', '2023-07-10 21:00:21'),
(76, 'sad', 'Stories Not to Be Told', '2023-07-10 21:00:21'),
(77, 'sad', 'Rumba Therapy', '2023-07-10 21:00:21'),
(78, 'sad', 'The Crooked Way', '2023-07-11 00:27:21'),
(79, 'sad', 'Raw Wind in Eden', '2023-07-11 00:27:21'),
(80, 'sad', 'Step Down to Terror', '2023-07-11 00:27:21'),
(81, 'sad', 'Undertow', '2023-07-11 00:27:21'),
(82, 'sad', 'Hold Back Tomorrow', '2023-07-11 00:27:22'),
(83, 'angry', 'The Crooked Way', '2023-07-11 00:31:08'),
(84, 'angry', 'Raw Wind in Eden', '2023-07-11 00:31:08'),
(85, 'angry', 'Step Down to Terror', '2023-07-11 00:31:08'),
(86, 'angry', 'Undertow', '2023-07-11 00:31:08'),
(87, 'angry', 'Hold Back Tomorrow', '2023-07-11 00:31:08');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `firstname` varchar(30) NOT NULL,
  `lastname` varchar(30) NOT NULL,
  `email` varchar(64) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `createdAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `updatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `firstname`, `lastname`, `email`, `password`, `is_verified`, `createdAt`, `updatedAt`) VALUES
(17, 'string', 'string', 'andragons99@gmail.com', 'pbkdf2:sha256:600000$tGHwLLYtUoD0YwGH$06d464f64435482f0ba9004ce509b7f4e2031c431adffe815a790f8c10566a64', 1, '2023-07-06 15:10:30', '2023-07-06 15:10:30'),
(20, 'Ramanda', 'Kholisandra', 'anderadevista123@gmail.com', 'pbkdf2:sha256:600000$0XwLCkcAtVZI61BU$93790dc9407ccfbc2093dd99d49d1ca4aa27e20119de4e3d698e45a07f47e6fe', 0, '2023-07-06 15:20:01', '2023-07-06 15:20:01');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `captured_images`
--
ALTER TABLE `captured_images`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `recommended_movies`
--
ALTER TABLE `recommended_movies`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `captured_images`
--
ALTER TABLE `captured_images`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1490;

--
-- AUTO_INCREMENT for table `recommended_movies`
--
ALTER TABLE `recommended_movies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=88;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
