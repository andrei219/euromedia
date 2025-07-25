-- MySQL dump 10.13  Distrib 8.4.0, for Win64 (x86_64)
--
-- Host: localhost    Database: euromedia
-- ------------------------------------------------------
-- Server version	8.4.0

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
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `parent_id` int DEFAULT NULL,
  `related_type` varchar(50) DEFAULT NULL,
  `related_id` int DEFAULT NULL,
  `created_on` datetime NOT NULL,
  `updated_on` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_parent_unique` (`code`,`parent_id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `accounts_chk_1` CHECK ((`related_type` in (_utf8mb4'partner',_utf8mb4'bank_account')))
) ENGINE=InnoDB AUTO_INCREMENT=1251 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `advanced_lines`
--

DROP TABLE IF EXISTS `advanced_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `advanced_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `origin_id` int DEFAULT NULL,
  `proforma_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `mixed_description` varchar(50) DEFAULT NULL,
  `free_description` varchar(255) DEFAULT NULL,
  `condition` varchar(50) DEFAULT NULL,
  `spec` varchar(50) DEFAULT NULL,
  `quantity` int NOT NULL,
  `price` double DEFAULT NULL,
  `tax` int NOT NULL,
  `ignore_spec` tinyint(1) NOT NULL,
  `showing_condition` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `proforma_id` (`proforma_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `advanced_lines_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `sale_proformas` (`id`),
  CONSTRAINT `advanced_lines_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3380 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `advanced_lines_definition`
--

DROP TABLE IF EXISTS `advanced_lines_definition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `advanced_lines_definition` (
  `id` int NOT NULL AUTO_INCREMENT,
  `line_id` int DEFAULT NULL,
  `item_id` int NOT NULL,
  `condition` varchar(50) NOT NULL,
  `spec` varchar(50) NOT NULL,
  `quantity` int DEFAULT NULL,
  `showing_condition` varchar(50) DEFAULT NULL,
  `local_count_relevant` tinyint(1) DEFAULT NULL,
  `global_count_relevant` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `line_id` (`line_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `advanced_lines_definition_ibfk_1` FOREIGN KEY (`line_id`) REFERENCES `advanced_lines` (`id`),
  CONSTRAINT `advanced_lines_definition_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `agent_documents`
--

DROP TABLE IF EXISTS `agent_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agent_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `agent_id` int DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `document` longblob,
  PRIMARY KEY (`id`),
  KEY `agent_id` (`agent_id`),
  CONSTRAINT `agent_documents_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `agents`
--

DROP TABLE IF EXISTS `agents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fiscal_number` varchar(50) DEFAULT NULL,
  `fiscal_name` varchar(50) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `phone` varchar(60) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `fixed_salary` double NOT NULL,
  `from_profit` double NOT NULL,
  `from_turnover` double NOT NULL,
  `fixed_perpiece` double NOT NULL,
  `bank_name` varchar(50) DEFAULT NULL,
  `iban` varchar(50) DEFAULT NULL,
  `swift` varchar(50) DEFAULT NULL,
  `bank_address` varchar(50) DEFAULT NULL,
  `bank_postcode` varchar(50) DEFAULT NULL,
  `bank_city` varchar(50) DEFAULT NULL,
  `bank_state` varchar(50) DEFAULT NULL,
  `bank_country` varchar(50) DEFAULT NULL,
  `bank_routing` varchar(50) DEFAULT NULL,
  `from_profit_purchase` tinyint(1) NOT NULL,
  `from_profit_sale` tinyint(1) NOT NULL,
  `from_turnover_purchase` tinyint(1) NOT NULL,
  `from_turnover_sale` tinyint(1) NOT NULL,
  `fixed_perpiece_purchase` tinyint(1) NOT NULL,
  `fixed_perpiece_sale` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fiscal_name` (`fiscal_name`),
  CONSTRAINT `no_empty_email` CHECK ((`email` <> _utf8mb4'')),
  CONSTRAINT `no_empty_fiscal_name` CHECK ((`fiscal_name` <> _utf8mb4'')),
  CONSTRAINT `no_empty_fiscal_number` CHECK ((`fiscal_number` <> _utf8mb4'')),
  CONSTRAINT `no_empty_phone` CHECK ((`phone` <> _utf8mb4''))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `balances`
--

DROP TABLE IF EXISTS `balances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `balances` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `account_id` int NOT NULL,
  `amount` decimal(18,4) NOT NULL,
  `created_on` datetime NOT NULL,
  `updated_on` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `balances_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bank_accounts`
--

DROP TABLE IF EXISTS `bank_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bank_accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `iban` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `banking_transactions`
--

DROP TABLE IF EXISTS `banking_transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banking_transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `journal_entry_id` int NOT NULL,
  `bank_id` int NOT NULL,
  `source` varchar(50) NOT NULL,
  `description` varchar(255) NOT NULL,
  `transaction_date` date NOT NULL,
  `value_date` date NOT NULL,
  `amount` decimal(18,4) NOT NULL,
  `posted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bank_id` (`bank_id`),
  KEY `journal_entry_id` (`journal_entry_id`),
  CONSTRAINT `banking_transactions_ibfk_1` FOREIGN KEY (`bank_id`) REFERENCES `bank_accounts` (`id`),
  CONSTRAINT `banking_transactions_ibfk_2` FOREIGN KEY (`journal_entry_id`) REFERENCES `journal_entries` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `condition_changes`
--

DROP TABLE IF EXISTS `condition_changes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `condition_changes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sn` varchar(50) NOT NULL,
  `before` varchar(50) NOT NULL,
  `after` varchar(50) NOT NULL,
  `created_on` datetime DEFAULT NULL,
  `comment` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8534 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `conditions`
--

DROP TABLE IF EXISTS `conditions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conditions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `couriers`
--

DROP TABLE IF EXISTS `couriers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `couriers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `credit_note_lines`
--

DROP TABLE IF EXISTS `credit_note_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_note_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `condition` varchar(50) NOT NULL,
  `spec` varchar(50) NOT NULL,
  `quantity` int NOT NULL,
  `price` double NOT NULL,
  `tax` int NOT NULL,
  `sn` varchar(100) NOT NULL,
  `public_condition` varchar(50) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `invoice_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `item_id` (`item_id`),
  KEY `proforma_id` (`proforma_id`),
  KEY `invoice_id` (`invoice_id`),
  CONSTRAINT `credit_note_lines_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  CONSTRAINT `credit_note_lines_ibfk_2` FOREIGN KEY (`proforma_id`) REFERENCES `sale_proformas` (`id`),
  CONSTRAINT `credit_note_lines_ibfk_3` FOREIGN KEY (`invoice_id`) REFERENCES `sale_invoices` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5248 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `discounts`
--

DROP TABLE IF EXISTS `discounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sn` varchar(50) NOT NULL,
  `invoice_id` int NOT NULL,
  `item_id` int NOT NULL,
  `discount` decimal(18,4) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `discounts_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `purchase_invoices` (`id`),
  CONSTRAINT `discounts_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expedition_lines`
--

DROP TABLE IF EXISTS `expedition_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expedition_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `expedition_id` int DEFAULT NULL,
  `item_id` int NOT NULL,
  `condition` varchar(50) NOT NULL,
  `spec` varchar(50) NOT NULL,
  `showing_condition` varchar(50) DEFAULT NULL,
  `quantity` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`,`expedition_id`),
  KEY `expedition_id` (`expedition_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `expedition_lines_ibfk_1` FOREIGN KEY (`expedition_id`) REFERENCES `expeditions` (`id`),
  CONSTRAINT `expedition_lines_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16592 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expedition_series`
--

DROP TABLE IF EXISTS `expedition_series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expedition_series` (
  `id` int NOT NULL AUTO_INCREMENT,
  `line_id` int DEFAULT NULL,
  `serie` varchar(50) NOT NULL,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`,`line_id`,`serie`),
  KEY `line_id` (`line_id`),
  CONSTRAINT `expedition_series_ibfk_1` FOREIGN KEY (`line_id`) REFERENCES `expedition_lines` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=309201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expeditions`
--

DROP TABLE IF EXISTS `expeditions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expeditions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int NOT NULL,
  `created_on` datetime DEFAULT NULL,
  `from_sale_type` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sale_expedition_from_onlyone_proforma` (`proforma_id`),
  CONSTRAINT `expeditions_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `sale_proformas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2960 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `hot_agents`
--

DROP TABLE IF EXISTS `hot_agents`;
/*!50001 DROP VIEW IF EXISTS `hot_agents`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `hot_agents` AS SELECT 
 1 AS `id`,
 1 AS `fiscal_number`,
 1 AS `fiscal_name`,
 1 AS `email`,
 1 AS `phone`,
 1 AS `active`,
 1 AS `country`,
 1 AS `created_on`,
 1 AS `fixed_salary`,
 1 AS `from_profit`,
 1 AS `from_turnover`,
 1 AS `fixed_perpiece`,
 1 AS `bank_name`,
 1 AS `iban`,
 1 AS `swift`,
 1 AS `bank_address`,
 1 AS `bank_postcode`,
 1 AS `bank_city`,
 1 AS `bank_state`,
 1 AS `bank_country`,
 1 AS `bank_routing`,
 1 AS `from_profit_purchase`,
 1 AS `from_profit_sale`,
 1 AS `from_turnover_purchase`,
 1 AS `from_turnover_sale`,
 1 AS `fixed_perpiece_purchase`,
 1 AS `fixed_perpiece_sale`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `imeis`
--

DROP TABLE IF EXISTS `imeis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `imeis` (
  `imei` varchar(50) NOT NULL,
  `item_id` int NOT NULL,
  `condition` varchar(50) DEFAULT NULL,
  `spec` varchar(50) DEFAULT NULL,
  `warehouse_id` int NOT NULL,
  PRIMARY KEY (`imei`),
  KEY `item_id` (`item_id`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `imeis_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  CONSTRAINT `imeis_ibfk_2` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `imeis_mask`
--

DROP TABLE IF EXISTS `imeis_mask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `imeis_mask` (
  `imei` varchar(50) NOT NULL,
  `item_id` int NOT NULL,
  `condition` varchar(50) NOT NULL,
  `spec` varchar(50) NOT NULL,
  `warehouse_id` int NOT NULL,
  `origin_id` int NOT NULL,
  PRIMARY KEY (`imei`),
  KEY `item_id` (`item_id`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `imeis_mask_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  CONSTRAINT `imeis_mask_ibfk_2` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `incoming_rma_lines`
--

DROP TABLE IF EXISTS `incoming_rma_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `incoming_rma_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `incoming_rma_id` int DEFAULT NULL,
  `problem` varchar(100) DEFAULT NULL,
  `accepted` tinyint(1) DEFAULT NULL,
  `sn` varchar(100) NOT NULL,
  `why` varchar(100) DEFAULT NULL,
  `supp` varchar(100) NOT NULL,
  `recpt` date DEFAULT NULL,
  `wtyendsupp` date NOT NULL,
  `purchas` varchar(255) DEFAULT NULL,
  `defas` varchar(255) DEFAULT NULL,
  `soldas` varchar(255) DEFAULT NULL,
  `public` varchar(100) DEFAULT NULL,
  `cust` varchar(100) NOT NULL,
  `saledate` date DEFAULT NULL,
  `exped` date DEFAULT NULL,
  `wtyendcust` date DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `condition` varchar(50) NOT NULL,
  `spec` varchar(50) NOT NULL,
  `price` double NOT NULL,
  `cust_id` int NOT NULL,
  `agent_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `incoming_rma_id` (`incoming_rma_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `incoming_rma_lines_ibfk_1` FOREIGN KEY (`incoming_rma_id`) REFERENCES `incoming_rmas` (`id`),
  CONSTRAINT `incoming_rma_lines_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5619 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `incoming_rmas`
--

DROP TABLE IF EXISTS `incoming_rmas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `incoming_rmas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1035 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mpn` varchar(50) DEFAULT NULL,
  `manufacturer` varchar(50) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `model` varchar(50) DEFAULT NULL,
  `capacity` varchar(50) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `has_serie` tinyint(1) DEFAULT NULL,
  `weight` decimal(10,2) NOT NULL,
  `battery_weight` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_1` (`mpn`,`manufacturer`,`category`,`model`,`capacity`,`color`)
) ENGINE=InnoDB AUTO_INCREMENT=1160 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `journal_entries`
--

DROP TABLE IF EXISTS `journal_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journal_entries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `description` varchar(255) NOT NULL,
  `related_type` varchar(100) NOT NULL,
  `related_id` int DEFAULT NULL,
  `auto` enum('auto_no','auto_semi','auto_yes') NOT NULL,
  `created_on` datetime NOT NULL,
  `updated_on` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `related_type_id_unique` (`related_type`,`related_id`),
  CONSTRAINT `journal_entries_chk_1` CHECK ((`related_type` in (_utf8mb4'sale',_utf8mb4'purchase',_utf8mb4'misc',_utf8mb4'payment',_utf8mb4'collection',_utf8mb4'income',_utf8mb4'expense',_utf8mb4'sale_return',_utf8mb4'purchase_return')))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `journal_entry_lines`
--

DROP TABLE IF EXISTS `journal_entry_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journal_entry_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `journal_entry_id` int NOT NULL,
  `account_id` int NOT NULL,
  `debit` decimal(18,4) NOT NULL,
  `credit` decimal(18,4) NOT NULL,
  `description` varchar(255) NOT NULL,
  `created_on` datetime NOT NULL,
  `updated_on` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `journal_entry_id` (`journal_entry_id`),
  CONSTRAINT `journal_entry_lines_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `journal_entry_lines_ibfk_2` FOREIGN KEY (`journal_entry_id`) REFERENCES `journal_entries` (`id`),
  CONSTRAINT `non_zero_debit_or_credit` CHECK (((`debit` <> 0) or (`credit` <> 0))),
  CONSTRAINT `not_both_debit_and_credit` CHECK (((`debit` = 0) or (`credit` = 0)))
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `many_manies`
--

DROP TABLE IF EXISTS `many_manies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `many_manies` (
  `sale_id` int NOT NULL,
  `credit_id` int NOT NULL,
  `fraction` float NOT NULL,
  PRIMARY KEY (`sale_id`,`credit_id`),
  KEY `credit_id` (`credit_id`),
  CONSTRAINT `many_manies_ibfk_1` FOREIGN KEY (`credit_id`) REFERENCES `sale_invoices` (`id`),
  CONSTRAINT `many_manies_ibfk_2` FOREIGN KEY (`sale_id`) REFERENCES `sale_invoices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `partner_accounts`
--

DROP TABLE IF EXISTS `partner_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `partner_accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `partner_id` int DEFAULT NULL,
  `bank_name` varchar(50) DEFAULT NULL,
  `iban` varchar(50) DEFAULT NULL,
  `swift` varchar(50) DEFAULT NULL,
  `bank_address` varchar(50) DEFAULT NULL,
  `bank_postcode` varchar(50) DEFAULT NULL,
  `bank_city` varchar(50) DEFAULT NULL,
  `bank_state` varchar(50) DEFAULT NULL,
  `bank_country` varchar(50) DEFAULT NULL,
  `bank_routing` varchar(50) DEFAULT NULL,
  `currency` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `partner_id` (`partner_id`),
  CONSTRAINT `partner_accounts_ibfk_1` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `partner_contacts`
--

DROP TABLE IF EXISTS `partner_contacts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `partner_contacts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `partner_id` int DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `position` varchar(50) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `note` varchar(50) DEFAULT NULL,
  `preferred` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `partner_id` (`partner_id`),
  CONSTRAINT `partner_contacts_ibfk_1` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`id`),
  CONSTRAINT `no_empty_contact_email` CHECK ((`email` <> _utf8mb4'')),
  CONSTRAINT `no_empty_contact_name` CHECK ((`name` <> _utf8mb4'')),
  CONSTRAINT `no_empty_position` CHECK ((`position` <> _utf8mb4''))
) ENGINE=InnoDB AUTO_INCREMENT=412 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `partner_documents`
--

DROP TABLE IF EXISTS `partner_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `partner_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `partner_id` int DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `document` longblob,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `partner_id` (`partner_id`),
  CONSTRAINT `partner_documents_ibfk_1` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `partners`
--

DROP TABLE IF EXISTS `partners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `partners` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fiscal_number` varchar(50) NOT NULL,
  `fiscal_name` varchar(50) NOT NULL,
  `trading_name` varchar(50) NOT NULL,
  `warranty` int DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `amount_credit_limit` double DEFAULT NULL,
  `days_credit_limit` int DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `agent_id` int DEFAULT NULL,
  `they_pay_they_ship` tinyint(1) NOT NULL,
  `they_pay_we_ship` tinyint(1) NOT NULL,
  `we_pay_they_ship` tinyint(1) NOT NULL,
  `we_pay_we_ship` tinyint(1) NOT NULL,
  `euro` tinyint(1) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `isp` tinyint(1) DEFAULT NULL,
  `re` tinyint(1) DEFAULT NULL,
  `billing_line1` varchar(50) DEFAULT NULL,
  `billing_line2` varchar(50) DEFAULT NULL,
  `billing_city` varchar(50) DEFAULT NULL,
  `billing_state` varchar(50) DEFAULT NULL,
  `billing_country` varchar(50) DEFAULT NULL,
  `billing_postcode` varchar(50) DEFAULT NULL,
  `has_certificate` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `agent_id` (`agent_id`),
  CONSTRAINT `partners_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`),
  CONSTRAINT `no_empty_partner_fiscal_name` CHECK ((`fiscal_name` <> _utf8mb4'')),
  CONSTRAINT `no_empty_partner_fiscal_number` CHECK ((`fiscal_number` <> _utf8mb4'')),
  CONSTRAINT `no_empty_partner_trading_name` CHECK ((`trading_name` <> _utf8mb4''))
) ENGINE=InnoDB AUTO_INCREMENT=410 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `purchase_documents`
--

DROP TABLE IF EXISTS `purchase_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `document` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_document_name` (`proforma_id`,`name`),
  CONSTRAINT `purchase_documents_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `purchase_proformas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `purchase_expenses`
--

DROP TABLE IF EXISTS `purchase_expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_expenses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `date` date DEFAULT NULL,
  `amount` double DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `proforma_id` (`proforma_id`),
  CONSTRAINT `purchase_expenses_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `purchase_proformas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1159 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `purchase_invoices`
--

DROP TABLE IF EXISTS `purchase_invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` int NOT NULL,
  `number` int NOT NULL,
  `date` date DEFAULT NULL,
  `eta` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=959 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `purchase_payments`
--

DROP TABLE IF EXISTS `purchase_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `date` date DEFAULT NULL,
  `amount` double DEFAULT NULL,
  `rate` double NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_purchase_payments_proforma_id` (`proforma_id`),
  CONSTRAINT `purchase_payments_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `purchase_proformas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1306 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `purchase_proforma_lines`
--

DROP TABLE IF EXISTS `purchase_proforma_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_proforma_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `condition` varchar(50) DEFAULT NULL,
  `spec` varchar(50) DEFAULT NULL,
  `quantity` int NOT NULL,
  `price` double NOT NULL,
  `tax` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `proforma_id` (`proforma_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `purchase_proforma_lines_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `purchase_proformas` (`id`),
  CONSTRAINT `purchase_proforma_lines_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6845 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `purchase_proformas`
--

DROP TABLE IF EXISTS `purchase_proformas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_proformas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` smallint NOT NULL,
  `number` int NOT NULL,
  `created_on` datetime DEFAULT NULL,
  `date` date NOT NULL,
  `warranty` int DEFAULT NULL,
  `eta` date NOT NULL,
  `cancelled` tinyint(1) NOT NULL,
  `sent` tinyint(1) NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  `eur_currency` tinyint(1) NOT NULL,
  `they_pay_they_ship` tinyint(1) NOT NULL,
  `we_pay_they_ship` tinyint(1) NOT NULL,
  `we_pay_we_ship` tinyint(1) NOT NULL,
  `partner_id` int DEFAULT NULL,
  `courier_id` int DEFAULT NULL,
  `warehouse_id` int DEFAULT NULL,
  `agent_id` int DEFAULT NULL,
  `invoice_id` int DEFAULT NULL,
  `tracking` varchar(50) DEFAULT NULL,
  `external` varchar(50) DEFAULT NULL,
  `credit_amount` double DEFAULT NULL,
  `credit_days` int NOT NULL,
  `incoterm` varchar(3) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `partner_id` (`partner_id`),
  KEY `courier_id` (`courier_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `agent_id` (`agent_id`),
  KEY `invoice_id` (`invoice_id`),
  CONSTRAINT `purchase_proformas_ibfk_1` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`id`),
  CONSTRAINT `purchase_proformas_ibfk_2` FOREIGN KEY (`courier_id`) REFERENCES `couriers` (`id`),
  CONSTRAINT `purchase_proformas_ibfk_3` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`),
  CONSTRAINT `purchase_proformas_ibfk_4` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`),
  CONSTRAINT `purchase_proformas_ibfk_5` FOREIGN KEY (`invoice_id`) REFERENCES `purchase_invoices` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1321 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reception_lines`
--

DROP TABLE IF EXISTS `reception_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reception_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reception_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `condition` varchar(50) NOT NULL,
  `spec` varchar(50) NOT NULL,
  `quantity` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`,`reception_id`),
  KEY `reception_id` (`reception_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `reception_lines_ibfk_1` FOREIGN KEY (`reception_id`) REFERENCES `receptions` (`id`),
  CONSTRAINT `reception_lines_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6099 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reception_series`
--

DROP TABLE IF EXISTS `reception_series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reception_series` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_id` int NOT NULL,
  `line_id` int NOT NULL,
  `serie` varchar(50) NOT NULL,
  `condition` varchar(50) NOT NULL,
  `spec` varchar(50) NOT NULL,
  `created_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `item_id` (`item_id`),
  KEY `line_id` (`line_id`),
  CONSTRAINT `reception_series_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  CONSTRAINT `reception_series_ibfk_2` FOREIGN KEY (`line_id`) REFERENCES `reception_lines` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=312656 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `receptions`
--

DROP TABLE IF EXISTS `receptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int NOT NULL,
  `note` varchar(50) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `auto` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `purchase_reception_from_onlyone_proforma` (`proforma_id`),
  UNIQUE KEY `proforma_id` (`proforma_id`),
  CONSTRAINT `receptions_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `purchase_proformas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1297 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `repairs`
--

DROP TABLE IF EXISTS `repairs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repairs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sn` varchar(50) NOT NULL,
  `item_id` int NOT NULL,
  `partner_id` int NOT NULL,
  `date` date NOT NULL,
  `description` varchar(255) NOT NULL,
  `cost` decimal(18,4) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `item_id` (`item_id`),
  KEY `partner_id` (`partner_id`),
  CONSTRAINT `repairs_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  CONSTRAINT `repairs_ibfk_2` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sale_documents`
--

DROP TABLE IF EXISTS `sale_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sale_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `document` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_document_name` (`proforma_id`,`name`),
  CONSTRAINT `sale_documents_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `sale_proformas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sale_expenses`
--

DROP TABLE IF EXISTS `sale_expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sale_expenses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `date` date DEFAULT NULL,
  `amount` double NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `proforma_id` (`proforma_id`),
  CONSTRAINT `sale_expenses_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `sale_proformas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1535 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sale_invoices`
--

DROP TABLE IF EXISTS `sale_invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sale_invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` int NOT NULL,
  `number` int NOT NULL,
  `date` date DEFAULT NULL,
  `eta` date DEFAULT NULL,
  `wh_incoming_rma_id` int DEFAULT NULL,
  `solunion` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wh_incoming_rma_id` (`wh_incoming_rma_id`),
  CONSTRAINT `sale_invoices_ibfk_2` FOREIGN KEY (`wh_incoming_rma_id`) REFERENCES `wh_incoming_rmas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3598 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sale_payments`
--

DROP TABLE IF EXISTS `sale_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sale_payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `date` date DEFAULT NULL,
  `amount` double NOT NULL,
  `rate` double NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `proforma_id` (`proforma_id`),
  CONSTRAINT `sale_payments_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `sale_proformas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3212 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sale_proforma_lines`
--

DROP TABLE IF EXISTS `sale_proforma_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sale_proforma_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proforma_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `mix_id` varchar(36) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `condition` varchar(50) DEFAULT NULL,
  `showing_condition` varchar(50) DEFAULT NULL,
  `spec` varchar(50) DEFAULT NULL,
  `ignore_spec` tinyint(1) DEFAULT NULL,
  `quantity` int NOT NULL,
  `price` double NOT NULL,
  `tax` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`,`proforma_id`),
  KEY `proforma_id` (`proforma_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `sale_proforma_lines_ibfk_1` FOREIGN KEY (`proforma_id`) REFERENCES `sale_proformas` (`id`),
  CONSTRAINT `sale_proforma_lines_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18821 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sale_proformas`
--

DROP TABLE IF EXISTS `sale_proformas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sale_proformas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` smallint DEFAULT NULL,
  `number` int DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `date` date DEFAULT NULL,
  `warranty` int DEFAULT NULL,
  `eta` date DEFAULT NULL,
  `cancelled` tinyint(1) DEFAULT NULL,
  `sent` tinyint(1) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `eur_currency` tinyint(1) DEFAULT NULL,
  `they_pay_they_ship` tinyint(1) DEFAULT NULL,
  `they_pay_we_ship` tinyint(1) DEFAULT NULL,
  `we_pay_we_ship` tinyint(1) DEFAULT NULL,
  `partner_id` int DEFAULT NULL,
  `courier_id` int DEFAULT NULL,
  `warehouse_id` int DEFAULT NULL,
  `agent_id` int DEFAULT NULL,
  `sale_invoice_id` int DEFAULT NULL,
  `credit_amount` double DEFAULT NULL,
  `credit_days` int DEFAULT NULL,
  `tracking` varchar(50) DEFAULT NULL,
  `external` varchar(50) DEFAULT NULL,
  `ready` tinyint(1) NOT NULL,
  `incoterm` varchar(3) DEFAULT NULL,
  `warning` varchar(255) DEFAULT NULL,
  `shipping_address_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `partner_id` (`partner_id`),
  KEY `courier_id` (`courier_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `agent_id` (`agent_id`),
  KEY `sale_invoice_id` (`sale_invoice_id`),
  KEY `shipping_address_id` (`shipping_address_id`),
  CONSTRAINT `sale_proformas_ibfk_1` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`id`),
  CONSTRAINT `sale_proformas_ibfk_2` FOREIGN KEY (`courier_id`) REFERENCES `couriers` (`id`),
  CONSTRAINT `sale_proformas_ibfk_3` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`),
  CONSTRAINT `sale_proformas_ibfk_4` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`),
  CONSTRAINT `sale_proformas_ibfk_5` FOREIGN KEY (`sale_invoice_id`) REFERENCES `sale_invoices` (`id`),
  CONSTRAINT `sale_proformas_ibfk_6` FOREIGN KEY (`shipping_address_id`) REFERENCES `shipping_addresses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5063 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `shipping_addresses`
--

DROP TABLE IF EXISTS `shipping_addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shipping_addresses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `partner_id` int NOT NULL,
  `line1` varchar(50) NOT NULL,
  `line2` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `state` varchar(50) NOT NULL,
  `zipcode` varchar(50) NOT NULL,
  `country` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `partner_id` (`partner_id`),
  CONSTRAINT `shipping_addresses_ibfk_1` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=460 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `spec_changes`
--

DROP TABLE IF EXISTS `spec_changes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `spec_changes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sn` varchar(50) NOT NULL,
  `before` varchar(50) NOT NULL,
  `after` varchar(50) NOT NULL,
  `created_on` datetime DEFAULT NULL,
  `comment` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=362 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `specs`
--

DROP TABLE IF EXISTS `specs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `specs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vies_requests`
--

DROP TABLE IF EXISTS `vies_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vies_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `request_date` date NOT NULL,
  `valid` tinyint(1) NOT NULL,
  `fiscal_number` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=936 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `warehouse_changes`
--

DROP TABLE IF EXISTS `warehouse_changes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouse_changes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sn` varchar(50) NOT NULL,
  `before` varchar(50) NOT NULL,
  `after` varchar(50) NOT NULL,
  `created_on` datetime DEFAULT NULL,
  `comment` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5263 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `warehouses`
--

DROP TABLE IF EXISTS `warehouses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wh_incoming_rma_lines`
--

DROP TABLE IF EXISTS `wh_incoming_rma_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wh_incoming_rma_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `wh_incoming_rma_id` int NOT NULL,
  `sn` varchar(50) NOT NULL,
  `accepted` varchar(1) NOT NULL,
  `problem` varchar(100) DEFAULT NULL,
  `why` varchar(50) DEFAULT NULL,
  `warehouse_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `invoice_type` int NOT NULL,
  `condition` varchar(50) NOT NULL,
  `spec` varchar(50) NOT NULL,
  `price` double NOT NULL,
  `public_condition` varchar(50) DEFAULT NULL,
  `target_condition` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `wh_incoming_rma_id` (`wh_incoming_rma_id`),
  KEY `item_id` (`item_id`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `wh_incoming_rma_lines_ibfk_1` FOREIGN KEY (`wh_incoming_rma_id`) REFERENCES `wh_incoming_rmas` (`id`),
  CONSTRAINT `wh_incoming_rma_lines_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  CONSTRAINT `wh_incoming_rma_lines_ibfk_3` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5240 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wh_incoming_rmas`
--

DROP TABLE IF EXISTS `wh_incoming_rmas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wh_incoming_rmas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `incoming_rma_id` int NOT NULL,
  `dumped` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wh_order_from_onlyone_rma_order` (`incoming_rma_id`),
  CONSTRAINT `wh_incoming_rmas_ibfk_1` FOREIGN KEY (`incoming_rma_id`) REFERENCES `incoming_rmas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=826 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `hot_agents`
--

/*!50001 DROP VIEW IF EXISTS `hot_agents`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`andrei`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `hot_agents` AS select `agents`.`id` AS `id`,`agents`.`fiscal_number` AS `fiscal_number`,`agents`.`fiscal_name` AS `fiscal_name`,`agents`.`email` AS `email`,`agents`.`phone` AS `phone`,`agents`.`active` AS `active`,`agents`.`country` AS `country`,`agents`.`created_on` AS `created_on`,`agents`.`fixed_salary` AS `fixed_salary`,`agents`.`from_profit` AS `from_profit`,`agents`.`from_turnover` AS `from_turnover`,`agents`.`fixed_perpiece` AS `fixed_perpiece`,`agents`.`bank_name` AS `bank_name`,`agents`.`iban` AS `iban`,`agents`.`swift` AS `swift`,`agents`.`bank_address` AS `bank_address`,`agents`.`bank_postcode` AS `bank_postcode`,`agents`.`bank_city` AS `bank_city`,`agents`.`bank_state` AS `bank_state`,`agents`.`bank_country` AS `bank_country`,`agents`.`bank_routing` AS `bank_routing`,`agents`.`from_profit_purchase` AS `from_profit_purchase`,`agents`.`from_profit_sale` AS `from_profit_sale`,`agents`.`from_turnover_purchase` AS `from_turnover_purchase`,`agents`.`from_turnover_sale` AS `from_turnover_sale`,`agents`.`fixed_perpiece_purchase` AS `fixed_perpiece_purchase`,`agents`.`fixed_perpiece_sale` AS `fixed_perpiece_sale` from `agents` where (`agents`.`id` = 1) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-14 14:40:20
