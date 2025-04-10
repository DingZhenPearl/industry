-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: industry_db
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(64) NOT NULL,
  `role` varchar(20) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `phone` varchar(20) DEFAULT NULL,
  `status` enum('鍦ㄥ矖','璇峰亣','绂诲矖') DEFAULT '鍦ㄥ矖',
  `employee_id` varchar(20) DEFAULT NULL,
  `group_id` int DEFAULT NULL COMMENT '鎵€灞炲垎缁処D',
  `line_id` int DEFAULT NULL COMMENT '鎵€灞炰骇绾縄D',
  `machine_id` int DEFAULT NULL COMMENT '鎵€灞炴満鍣↖D',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `employee_id` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin1','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','supervisor','2025-04-07 08:37:37','19999999999','鍦ㄥ矖','SP0001',0,1,1),(2,'foreman1','50d2cec061dab3dc059c09b0bc8e167214fb9780739242687386e3ab978d68b3','foreman','2025-04-07 08:37:37',NULL,'鍦ㄥ矖','FM0002',1,2,NULL),(3,'worker','87eba76e7f3164534045ba922e7770fb58bbd14ad732bbf5ba6f11cc56989e6e','member','2025-04-07 08:37:37','18874458888','鍦ㄥ矖','WK0003',1,2,NULL),(4,'safety','9a72c3f322b7c34eef4c4558f6114664956bbcd448da5fa4377185a188b6a4ce','safety_officer','2025-04-07 08:37:37','15452987466','鍦ㄥ矖','SF0004',1,2,NULL),(6,'foreman','c02994d302dfc314bd1b67c07fb58dd783b0938cf58e4d5b55d94db5a4994550','foreman','2025-04-07 09:26:02','15895959595','鍦ㄥ矖','FM0006',99,NULL,NULL),(8,'worker1','312bba6ac1c4274943d7d3c1f346e8e27310c731e407ce5592d82f0d101fbff1','member','2025-04-07 13:26:52',NULL,'鍦ㄥ矖','WK0008',1,2,NULL),(9,'safety1','9a72c3f322b7c34eef4c4558f6114664956bbcd448da5fa4377185a188b6a4ce','safety_officer','2025-04-07 13:26:52',NULL,'鍦ㄥ矖','SF0009',1,1,1),(10,'new','11507a0e2f5e69d5dfa40a62a1bd7b6ee57e6bcd85c67c9b8431b36fff21c437','member','2025-04-09 06:17:49',NULL,'鍦ㄥ矖','WK0010',1,1,1),(12,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','supervisor','2025-04-09 14:24:02','13800138000','鍦ㄥ矖',NULL,NULL,NULL,NULL),(13,'foreman2','50d2cec061dab3dc059c09b0bc8e167214fb9780739242687386e3ab978d68b3','foreman','2025-04-09 14:24:02','13800138005','鍦ㄥ矖',NULL,2,NULL,NULL),(14,'worker2','312bba6ac1c4274943d7d3c1f346e8e27310c731e407ce5592d82f0d101fbff1','member','2025-04-09 14:24:02','13800138006','鍦ㄥ矖',NULL,2,NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-10 14:51:39
