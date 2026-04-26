-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: RefurbishedTech_CRM
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Table structure for table `complaints`
--

DROP TABLE IF EXISTS `complaints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaints` (
  `ComplaintID` int NOT NULL AUTO_INCREMENT,
  `DeviceID` int DEFAULT NULL,
  `CustomerID` int DEFAULT NULL,
  `Issue` text,
  `Status` enum('Open','In Progress','Resolved') DEFAULT 'Open',
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ComplaintID`),
  KEY `DeviceID` (`DeviceID`),
  KEY `CustomerID` (`CustomerID`),
  CONSTRAINT `complaints_ibfk_1` FOREIGN KEY (`DeviceID`) REFERENCES `devices` (`DeviceID`),
  CONSTRAINT `complaints_ibfk_2` FOREIGN KEY (`CustomerID`) REFERENCES `customers` (`CustomerID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaints`
--

LOCK TABLES `complaints` WRITE;
/*!40000 ALTER TABLE `complaints` DISABLE KEYS */;
INSERT INTO `complaints` VALUES (1,5,7,'taking too much time.','Resolved','2026-04-26 15:48:45');
/*!40000 ALTER TABLE `complaints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `CustomerID` int NOT NULL AUTO_INCREMENT,
  `FullName` varchar(100) DEFAULT NULL,
  `Contact` varchar(20) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Password` varchar(255) DEFAULT 'default',
  `LoyaltyPoints` int DEFAULT '100',
  PRIMARY KEY (`CustomerID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (6,'ABC','',NULL,'default',100),(7,'PARTH','1234567890',NULL,'default',100);
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devicelogs`
--

DROP TABLE IF EXISTS `devicelogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devicelogs` (
  `LogID` int NOT NULL AUTO_INCREMENT,
  `DeviceID` int DEFAULT NULL,
  `OldStatus` varchar(50) DEFAULT NULL,
  `NewStatus` varchar(50) DEFAULT NULL,
  `ChangedBy` varchar(50) DEFAULT NULL,
  `ChangeDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`LogID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devicelogs`
--

LOCK TABLES `devicelogs` WRITE;
/*!40000 ALTER TABLE `devicelogs` DISABLE KEYS */;
INSERT INTO `devicelogs` VALUES (1,1,'Salvage','Repair','admin','2026-04-26 12:53:38'),(2,3,'Repair','Resale','admin','2026-04-26 15:32:39'),(3,3,'Resale','Repair','admin','2026-04-26 15:35:08');
/*!40000 ALTER TABLE `devicelogs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devices` (
  `DeviceID` int NOT NULL AUTO_INCREMENT,
  `OwnerID` int DEFAULT NULL,
  `Brand` varchar(50) DEFAULT NULL,
  `Model` varchar(100) DEFAULT NULL,
  `DeviceType` varchar(50) DEFAULT NULL,
  `Storage` varchar(50) DEFAULT NULL,
  `PurchaseYear` varchar(50) DEFAULT NULL,
  `BatteryCycleCount` int DEFAULT NULL,
  `ScreenCondition` int DEFAULT NULL,
  `HealthScore` int DEFAULT NULL,
  `CurrentStatus` varchar(50) DEFAULT NULL,
  `BuybackPrice` int DEFAULT NULL,
  `TicketID` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`DeviceID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
INSERT INTO `devices` VALUES (2,7,'Xiaomi','VICTUS','Smartphone','N/A','2025',448,90,47,'Repair',6788,'RT-79770'),(3,7,'OPPO','VICTUS','Laptop','N/A','2025',316,90,57,'Repair',12349,'RT-98214'),(4,7,'Samsung','VICTUS','Smartphone','N/A','2025',379,90,85,'Resale',16572,'RT-63731'),(5,7,'Samsung','VICTUS','Smartphone','N/A','2025',379,90,85,'Resale',16572,'RT-12362');
/*!40000 ALTER TABLE `devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(50) DEFAULT NULL,
  `Password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `Username` (`Username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin123');
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

-- Dump completed on 2026-04-26 22:25:26
