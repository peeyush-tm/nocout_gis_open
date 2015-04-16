CREATE DATABASE  IF NOT EXISTS `nocout_dev` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `nocout_dev`;
-- MySQL dump 10.13  Distrib 5.5.37, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: nocout_dev
-- ------------------------------------------------------
-- Server version	5.5.37-0ubuntu0.13.10.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_5f412f9a` (`group_id`),
  KEY `auth_group_permissions_83d7f98b` (`permission_id`),
  CONSTRAINT `group_id_refs_id_f4b32aac` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_6ba0f519` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_37ef4eb4` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_d043b34a` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=94 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add content type',4,'add_contenttype'),(11,'Can change content type',4,'change_contenttype'),(12,'Can delete content type',4,'delete_contenttype'),(13,'Can add session',5,'add_session'),(14,'Can change session',5,'change_session'),(15,'Can delete session',5,'delete_session'),(16,'Can add site',6,'add_site'),(17,'Can change site',6,'change_site'),(18,'Can delete site',6,'delete_site'),(19,'Can add migration history',7,'add_migrationhistory'),(20,'Can change migration history',7,'change_migrationhistory'),(21,'Can delete migration history',7,'delete_migrationhistory'),(22,'Can add user profile',8,'add_userprofile'),(23,'Can change user profile',8,'change_userprofile'),(24,'Can delete user profile',8,'delete_userprofile'),(25,'Can add roles',9,'add_roles'),(26,'Can change roles',9,'change_roles'),(27,'Can delete roles',9,'delete_roles'),(28,'Can add department',10,'add_department'),(29,'Can change department',10,'change_department'),(30,'Can delete department',10,'delete_department'),(31,'Can add user group',11,'add_usergroup'),(32,'Can change user group',11,'change_usergroup'),(33,'Can delete user group',11,'delete_usergroup'),(34,'Can add organization',12,'add_organization'),(35,'Can change organization',12,'change_organization'),(36,'Can delete organization',12,'delete_organization'),(37,'Can add device type',13,'add_devicetype'),(38,'Can change device type',13,'change_devicetype'),(39,'Can delete device type',13,'delete_devicetype'),(40,'Can add device model',14,'add_devicemodel'),(41,'Can change device model',14,'change_devicemodel'),(42,'Can delete device model',14,'delete_devicemodel'),(43,'Can add device vendor',15,'add_devicevendor'),(44,'Can change device vendor',15,'change_devicevendor'),(45,'Can delete device vendor',15,'delete_devicevendor'),(46,'Can add device technology',16,'add_devicetechnology'),(47,'Can change device technology',16,'change_devicetechnology'),(48,'Can delete device technology',16,'delete_devicetechnology'),(49,'Can add device',17,'add_device'),(50,'Can change device',17,'change_device'),(51,'Can delete device',17,'delete_device'),(52,'Can add model type',18,'add_modeltype'),(53,'Can change model type',18,'change_modeltype'),(54,'Can delete model type',18,'delete_modeltype'),(55,'Can add vendor model',19,'add_vendormodel'),(56,'Can change vendor model',19,'change_vendormodel'),(57,'Can delete vendor model',19,'delete_vendormodel'),(58,'Can add technology vendor',20,'add_technologyvendor'),(59,'Can change technology vendor',20,'change_technologyvendor'),(60,'Can delete technology vendor',20,'delete_technologyvendor'),(61,'Can add inventory',21,'add_inventory'),(62,'Can change inventory',21,'change_inventory'),(63,'Can delete inventory',21,'delete_inventory'),(64,'Can add device type fields',22,'add_devicetypefields'),(65,'Can change device type fields',22,'change_devicetypefields'),(66,'Can delete device type fields',22,'delete_devicetypefields'),(67,'Can add device type fields value',23,'add_devicetypefieldsvalue'),(68,'Can change device type fields value',23,'change_devicetypefieldsvalue'),(69,'Can delete device type fields value',23,'delete_devicetypefieldsvalue'),(70,'Can add device group',24,'add_devicegroup'),(71,'Can change device group',24,'change_devicegroup'),(72,'Can delete device group',24,'delete_devicegroup'),(73,'Can add service parameters',25,'add_serviceparameters'),(74,'Can change service parameters',25,'change_serviceparameters'),(75,'Can delete service parameters',25,'delete_serviceparameters'),(76,'Can add service',26,'add_service'),(77,'Can change service',26,'change_service'),(78,'Can delete service',26,'delete_service'),(79,'Can add service group',27,'add_servicegroup'),(80,'Can change service group',27,'change_servicegroup'),(81,'Can delete service group',27,'delete_servicegroup'),(82,'Can add command',28,'add_command'),(83,'Can change command',28,'change_command'),(84,'Can delete command',28,'delete_command'),(85,'Can add site instance',29,'add_siteinstance'),(86,'Can change site instance',29,'change_siteinstance'),(87,'Can delete site instance',29,'delete_siteinstance'),(88,'Can add log entry',30,'add_logentry'),(89,'Can change log entry',30,'change_logentry'),(90,'Can delete log entry',30,'delete_logentry'),(91,'Can add visitor',31,'add_visitor'),(92,'Can change visitor',31,'change_visitor'),(93,'Can delete visitor',31,'delete_visitor');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$12000$SPMzXFDtqufn$cDLdftWoFOfUe0TniGNqg1nnodLYxOqQ8+Wp/75w9vk=','2014-05-28 15:08:00',1,'nocout','','','admin@nocout.com',1,1,'2014-05-28 14:09:12'),(2,'pbkdf2_sha256$12000$pzM0PoqRCIxZ$tKHiDncSZKXGyZUbqOkNy/86KnkbpOoDKlbV6D8M+bs=','2014-05-28 17:00:59',0,'gisadmin','GIS Admin','','default@nocout.com',0,1,'2014-05-28 15:05:51');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_6340c63c` (`user_id`),
  KEY `auth_user_groups_5f412f9a` (`group_id`),
  CONSTRAINT `group_id_refs_id_274b862c` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_id_refs_id_40c41112` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_6340c63c` (`user_id`),
  KEY `auth_user_user_permissions_83d7f98b` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_35d9ac25` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_4dc23c39` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `command_command`
--

DROP TABLE IF EXISTS `command_command`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `command_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `command_name` varchar(100) NOT NULL,
  `command_line` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `command_name` (`command_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `command_command`
--

LOCK TABLES `command_command` WRITE;
/*!40000 ALTER TABLE `command_command` DISABLE KEYS */;
INSERT INTO `command_command` VALUES (1,'ping','/omd/sites/nocout/lib/nagios/plugins/check_ping');
/*!40000 ALTER TABLE `command_command` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_device`
--

DROP TABLE IF EXISTS `device_device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(200) NOT NULL,
  `device_alias` varchar(200) NOT NULL,
  `site_instance_id` int(11) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `device_technology` int(11) DEFAULT NULL,
  `device_vendor` int(11) DEFAULT NULL,
  `device_model` int(11) DEFAULT NULL,
  `device_type` int(11) DEFAULT NULL,
  `ip_address` char(15) NOT NULL,
  `mac_address` varchar(100) NOT NULL,
  `netmask` char(15) DEFAULT NULL,
  `gateway` char(15) DEFAULT NULL,
  `dhcp_state` varchar(200) NOT NULL,
  `host_priority` varchar(200) NOT NULL,
  `host_state` varchar(200) NOT NULL,
  `timezone` varchar(100) NOT NULL,
  `latitude` varchar(20) DEFAULT NULL,
  `longitude` varchar(20) DEFAULT NULL,
  `address` longtext,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `description` longtext NOT NULL,
  `is_deleted` int(11) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`),
  UNIQUE KEY `ip_address` (`ip_address`),
  KEY `device_device_a74b81df` (`site_instance_id`),
  KEY `device_device_410d0aac` (`parent_id`),
  KEY `device_device_329f6fb3` (`lft`),
  KEY `device_device_e763210f` (`rght`),
  KEY `device_device_ba470c4a` (`tree_id`),
  KEY `device_device_20e079f4` (`level`),
  CONSTRAINT `parent_id_refs_id_0679e3c1` FOREIGN KEY (`parent_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `site_instance_id_refs_id_7810d5e5` FOREIGN KEY (`site_instance_id`) REFERENCES `site_instance_siteinstance` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_device`
--

LOCK TABLES `device_device` WRITE;
/*!40000 ALTER TABLE `device_device` DISABLE KEYS */;
INSERT INTO `device_device` VALUES (1,'default','Default',1,NULL,1,1,1,1,'127.0.0.1','0:0:0:0:0:0','255.255.255.0','','Disable','Normal','Enable','Asia/Kolkata','','','','','','It\'s default (localhost) device.',0,1,2,1,0);
/*!40000 ALTER TABLE `device_device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_device_service`
--

DROP TABLE IF EXISTS `device_device_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_device_service` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_id` (`device_id`,`service_id`),
  KEY `device_device_service_b6860804` (`device_id`),
  KEY `device_device_service_91a0ac17` (`service_id`),
  CONSTRAINT `device_id_refs_id_4598934a` FOREIGN KEY (`device_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `service_id_refs_id_1cfe1201` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_device_service`
--

LOCK TABLES `device_device_service` WRITE;
/*!40000 ALTER TABLE `device_device_service` DISABLE KEYS */;
INSERT INTO `device_device_service` VALUES (1,1,1);
/*!40000 ALTER TABLE `device_device_service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_devicemodel`
--

DROP TABLE IF EXISTS `device_devicemodel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicemodel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicemodel`
--

LOCK TABLES `device_devicemodel` WRITE;
/*!40000 ALTER TABLE `device_devicemodel` DISABLE KEYS */;
INSERT INTO `device_devicemodel` VALUES (1,'Default','Default'),(2,'Radwin2K','Radwin2K'),(3,'Starmax','Starmax'),(4,'CanopyPM100','CanopyPM100'),(5,'CanopySM100','CanopySM100');
/*!40000 ALTER TABLE `device_devicemodel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_devicetechnology`
--

DROP TABLE IF EXISTS `device_devicetechnology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetechnology` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicetechnology`
--

LOCK TABLES `device_devicetechnology` WRITE;
/*!40000 ALTER TABLE `device_devicetechnology` DISABLE KEYS */;
INSERT INTO `device_devicetechnology` VALUES (1,'Default','Default'),(2,'P2P','P2P'),(3,'WiMAX','WiMAX'),(4,'PMP','PMP');
/*!40000 ALTER TABLE `device_devicetechnology` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_devicetype`
--

DROP TABLE IF EXISTS `device_devicetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `alias` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicetype`
--

LOCK TABLES `device_devicetype` WRITE;
/*!40000 ALTER TABLE `device_devicetype` DISABLE KEYS */;
INSERT INTO `device_devicetype` VALUES (1,'Default','Default'),(2,'Radwin2KSS','Radwin2KSS'),(3,'Radwin2KBS','Radwin2KBS'),(4,'StarmaxIDU','StarmaxIDU'),(5,'StarmaxSS','StarmaxSS'),(6,'CanopyPM100AP','CanopyPM100AP'),(7,'CanopyPM100SS','CanopyPM100SS'),(8,'CanopySM100AP','CanopySM100AP'),(9,'CanopySM100SS','CanopySM100SS');
/*!40000 ALTER TABLE `device_devicetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_devicetypefields`
--

DROP TABLE IF EXISTS `device_devicetypefields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetypefields` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_type_id` int(11) DEFAULT NULL,
  `field_name` varchar(100) NOT NULL,
  `field_display_name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_devicetypefields_d8be8594` (`device_type_id`),
  CONSTRAINT `device_type_id_refs_id_45058c1e` FOREIGN KEY (`device_type_id`) REFERENCES `device_devicetype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicetypefields`
--

LOCK TABLES `device_devicetypefields` WRITE;
/*!40000 ALTER TABLE `device_devicetypefields` DISABLE KEYS */;
INSERT INTO `device_devicetypefields` VALUES (1,2,'customer_name','Customer Name'),(2,2,'ckt_id','Ckt ID'),(3,2,'qos_bw','Qos(BW)'),(6,2,'antenna_height','Antenna Height'),(7,2,'polarisation','Polarization'),(8,2,'antenna_type','Antenna Type'),(9,2,'antenna_mount_type','Antenna Mount Type'),(10,2,'ethernet_extender','Ethernet Extender'),(11,2,'building_height','Building Height'),(12,2,'tower_height','Tower Height'),(13,2,'cable_length','Cable Length'),(14,2,'rssi_during_acceptance','RSSI During Acceptance'),(15,2,'customer_address','Customer Address'),(16,2,'throughput_during_acceptance','Throughput During Acceptance'),(17,2,'date_of_acceptance','Date Of Acceptance'),(18,2,'bh_bso','BH BSO'),(19,2,'service_type','Service Type'),(20,2,'product_type','Product Type'),(21,2,'frequency_at_time_of_acceptance','Frequency At The Time Of Acceptance'),(22,2,'cbw_at_the_time_of_acceptance','CBW At The Time Of Acceptance'),(23,3,'customer_name','Customer Name'),(24,3,'ckt_id','Ckt ID'),(25,3,'qos_bw','Qos(BW)'),(28,3,'antenna_height','Antenna Height'),(29,3,'polarisation','Polarisation'),(30,3,'antenna_type','Antenna Type'),(31,3,'antenna_mount_type','Antenna Mount Type'),(32,3,'ethernet_extender','Ethernet Extender'),(33,3,'building_height','Building Height'),(34,3,'tower_height','Tower Height'),(35,3,'cable_length','Cable Length'),(36,3,'rssi_during_acceptance','RSSI During Acceptance'),(37,3,'customer_address','Customer Address'),(38,3,'throughput_during_acceptance','throughput_during_accetpance'),(39,3,'date_of_acceptance','Date Of Acceptance'),(40,3,'bh_bso','BH BSO'),(41,3,'service_type','Service Type'),(42,3,'product_type','Product Type'),(43,3,'frequency_at_time_of_acceptance','Frequency At The Time Of Acceptance'),(44,3,'cbw_at_the_time_of_acceptance','CBW At The Time Of Acceptance');
/*!40000 ALTER TABLE `device_devicetypefields` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_devicetypefieldsvalue`
--

DROP TABLE IF EXISTS `device_devicetypefieldsvalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetypefieldsvalue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_type_field_id` int(11) NOT NULL,
  `field_value` varchar(250) NOT NULL,
  `device_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_devicetypefieldsvalue_0ea03cb7` (`device_type_field_id`),
  CONSTRAINT `device_type_field_id_refs_id_601dc771` FOREIGN KEY (`device_type_field_id`) REFERENCES `device_devicetypefields` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicetypefieldsvalue`
--

LOCK TABLES `device_devicetypefieldsvalue` WRITE;
/*!40000 ALTER TABLE `device_devicetypefieldsvalue` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_devicetypefieldsvalue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_devicevendor`
--

DROP TABLE IF EXISTS `device_devicevendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicevendor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicevendor`
--

LOCK TABLES `device_devicevendor` WRITE;
/*!40000 ALTER TABLE `device_devicevendor` DISABLE KEYS */;
INSERT INTO `device_devicevendor` VALUES (1,'Default','Default'),(2,'Radwin','Radwin'),(3,'Telisma','Telisma'),(4,'Cambium','Cambium');
/*!40000 ALTER TABLE `device_devicevendor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_group_devicegroup`
--

DROP TABLE IF EXISTS `device_group_devicegroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_group_devicegroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `alias` varchar(200) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `location` varchar(200) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `is_deleted` int(11) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `device_group_devicegroup_410d0aac` (`parent_id`),
  KEY `device_group_devicegroup_329f6fb3` (`lft`),
  KEY `device_group_devicegroup_e763210f` (`rght`),
  KEY `device_group_devicegroup_ba470c4a` (`tree_id`),
  KEY `device_group_devicegroup_20e079f4` (`level`),
  CONSTRAINT `parent_id_refs_id_e4aa56d8` FOREIGN KEY (`parent_id`) REFERENCES `device_group_devicegroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_group_devicegroup`
--

LOCK TABLES `device_group_devicegroup` WRITE;
/*!40000 ALTER TABLE `device_group_devicegroup` DISABLE KEYS */;
INSERT INTO `device_group_devicegroup` VALUES (1,'default','Default',NULL,'','',0,1,2,1,0);
/*!40000 ALTER TABLE `device_group_devicegroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_inventory`
--

DROP TABLE IF EXISTS `device_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_inventory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `device_group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_inventory_b6860804` (`device_id`),
  KEY `device_inventory_a4353bbd` (`device_group_id`),
  CONSTRAINT `device_group_id_refs_id_8a9ec26a` FOREIGN KEY (`device_group_id`) REFERENCES `device_group_devicegroup` (`id`),
  CONSTRAINT `device_id_refs_id_22db70b3` FOREIGN KEY (`device_id`) REFERENCES `device_device` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_inventory`
--

LOCK TABLES `device_inventory` WRITE;
/*!40000 ALTER TABLE `device_inventory` DISABLE KEYS */;
INSERT INTO `device_inventory` VALUES (1,1,1);
/*!40000 ALTER TABLE `device_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_modeltype`
--

DROP TABLE IF EXISTS `device_modeltype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_modeltype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model_id` int(11) NOT NULL,
  `type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_modeltype_29840309` (`model_id`),
  KEY `device_modeltype_403d8ff3` (`type_id`),
  CONSTRAINT `model_id_refs_id_a541d8ea` FOREIGN KEY (`model_id`) REFERENCES `device_devicemodel` (`id`),
  CONSTRAINT `type_id_refs_id_5974f309` FOREIGN KEY (`type_id`) REFERENCES `device_devicetype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_modeltype`
--

LOCK TABLES `device_modeltype` WRITE;
/*!40000 ALTER TABLE `device_modeltype` DISABLE KEYS */;
INSERT INTO `device_modeltype` VALUES (1,1,1),(2,2,2),(3,2,3),(4,3,4),(5,3,5),(6,4,6),(7,4,7),(8,5,8),(9,5,9);
/*!40000 ALTER TABLE `device_modeltype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_modeltype_service`
--

DROP TABLE IF EXISTS `device_modeltype_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_modeltype_service` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `modeltype_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `modeltype_id` (`modeltype_id`,`service_id`),
  KEY `device_modeltype_service_27f72d94` (`modeltype_id`),
  KEY `device_modeltype_service_91a0ac17` (`service_id`),
  CONSTRAINT `modeltype_id_refs_id_dd421022` FOREIGN KEY (`modeltype_id`) REFERENCES `device_modeltype` (`id`),
  CONSTRAINT `service_id_refs_id_6c30de99` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_modeltype_service`
--

LOCK TABLES `device_modeltype_service` WRITE;
/*!40000 ALTER TABLE `device_modeltype_service` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_modeltype_service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_technologyvendor`
--

DROP TABLE IF EXISTS `device_technologyvendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_technologyvendor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `technology_id` int(11) NOT NULL,
  `vendor_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_technologyvendor_98427941` (`technology_id`),
  KEY `device_technologyvendor_bc787c37` (`vendor_id`),
  CONSTRAINT `technology_id_refs_id_e65d7c30` FOREIGN KEY (`technology_id`) REFERENCES `device_devicetechnology` (`id`),
  CONSTRAINT `vendor_id_refs_id_76002624` FOREIGN KEY (`vendor_id`) REFERENCES `device_devicevendor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_technologyvendor`
--

LOCK TABLES `device_technologyvendor` WRITE;
/*!40000 ALTER TABLE `device_technologyvendor` DISABLE KEYS */;
INSERT INTO `device_technologyvendor` VALUES (1,1,1),(2,2,2),(3,3,3),(4,4,4);
/*!40000 ALTER TABLE `device_technologyvendor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_vendormodel`
--

DROP TABLE IF EXISTS `device_vendormodel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_vendormodel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vendor_id` int(11) NOT NULL,
  `model_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_vendormodel_bc787c37` (`vendor_id`),
  KEY `device_vendormodel_29840309` (`model_id`),
  CONSTRAINT `model_id_refs_id_7a8bc72f` FOREIGN KEY (`model_id`) REFERENCES `device_devicemodel` (`id`),
  CONSTRAINT `vendor_id_refs_id_16f677d4` FOREIGN KEY (`vendor_id`) REFERENCES `device_devicevendor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_vendormodel`
--

LOCK TABLES `device_vendormodel` WRITE;
/*!40000 ALTER TABLE `device_vendormodel` DISABLE KEYS */;
INSERT INTO `device_vendormodel` VALUES (1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,4,5);
/*!40000 ALTER TABLE `device_vendormodel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_6340c63c` (`user_id`),
  KEY `django_admin_log_37ef4eb4` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_93d2d1f8` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_c0d12874` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'content type','contenttypes','contenttype'),(5,'session','sessions','session'),(6,'site','sites','site'),(7,'migration history','south','migrationhistory'),(8,'user profile','user_profile','userprofile'),(9,'roles','user_profile','roles'),(10,'department','user_profile','department'),(11,'user group','user_group','usergroup'),(12,'organization','user_group','organization'),(13,'device type','device','devicetype'),(14,'device model','device','devicemodel'),(15,'device vendor','device','devicevendor'),(16,'device technology','device','devicetechnology'),(17,'device','device','device'),(18,'model type','device','modeltype'),(19,'vendor model','device','vendormodel'),(20,'technology vendor','device','technologyvendor'),(21,'inventory','device','inventory'),(22,'device type fields','device','devicetypefields'),(23,'device type fields value','device','devicetypefieldsvalue'),(24,'device group','device_group','devicegroup'),(25,'service parameters','service','serviceparameters'),(26,'service','service','service'),(27,'service group','service_group','servicegroup'),(28,'command','command','command'),(29,'site instance','site_instance','siteinstance'),(30,'log entry','admin','logentry'),(31,'visitor','preventconcurrentlogins','visitor');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_b7b81f0c` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('isa97mh0727stgugxiz4tsdati6nl2tt','NTM0OGJhMWQ2ZjQxMzIyNDU4YWRiYTE5YjBhYmFjN2VlN2M0Y2YyNzp7fQ==','2014-06-11 17:30:33');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preventconcurrentlogins_visitor`
--

DROP TABLE IF EXISTS `preventconcurrentlogins_visitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `preventconcurrentlogins_visitor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `session_key` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_1afbbe85` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preventconcurrentlogins_visitor`
--

LOCK TABLES `preventconcurrentlogins_visitor` WRITE;
/*!40000 ALTER TABLE `preventconcurrentlogins_visitor` DISABLE KEYS */;
INSERT INTO `preventconcurrentlogins_visitor` VALUES (1,1,'gylf7h23o4g0at9w9td0w7109uvtwgl4'),(2,2,'lo0ydh42utrb2ywinfml77tgrnzaklu8');
/*!40000 ALTER TABLE `preventconcurrentlogins_visitor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_group_servicegroup`
--

DROP TABLE IF EXISTS `service_group_servicegroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_group_servicegroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `servicegroup_name` varchar(100) NOT NULL,
  `alias` varchar(100) NOT NULL,
  `notes` varchar(100) DEFAULT NULL,
  `notes_url` varchar(200) DEFAULT NULL,
  `action_url` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_group_servicegroup`
--

LOCK TABLES `service_group_servicegroup` WRITE;
/*!40000 ALTER TABLE `service_group_servicegroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `service_group_servicegroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_group_servicegroup_service`
--

DROP TABLE IF EXISTS `service_group_servicegroup_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_group_servicegroup_service` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `servicegroup_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `servicegroup_id` (`servicegroup_id`,`service_id`),
  KEY `service_group_servicegroup_service_69682e37` (`servicegroup_id`),
  KEY `service_group_servicegroup_service_91a0ac17` (`service_id`),
  CONSTRAINT `servicegroup_id_refs_id_704115ab` FOREIGN KEY (`servicegroup_id`) REFERENCES `service_group_servicegroup` (`id`),
  CONSTRAINT `service_id_refs_id_e3fa63cb` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_group_servicegroup_service`
--

LOCK TABLES `service_group_servicegroup_service` WRITE;
/*!40000 ALTER TABLE `service_group_servicegroup_service` DISABLE KEYS */;
/*!40000 ALTER TABLE `service_group_servicegroup_service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_service`
--

DROP TABLE IF EXISTS `service_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_service` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `service_name` varchar(100) NOT NULL,
  `alias` varchar(100) NOT NULL,
  `command_id` int(11) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  KEY `service_service_36c081f7` (`command_id`),
  CONSTRAINT `command_id_refs_id_df37dd44` FOREIGN KEY (`command_id`) REFERENCES `command_command` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_service`
--

LOCK TABLES `service_service` WRITE;
/*!40000 ALTER TABLE `service_service` DISABLE KEYS */;
INSERT INTO `service_service` VALUES (1,'default','Default',1,'It\'s a default (ping) service.');
/*!40000 ALTER TABLE `service_service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_service_parameters`
--

DROP TABLE IF EXISTS `service_service_parameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_service_parameters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `service_id` int(11) NOT NULL,
  `serviceparameters_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `service_id` (`service_id`,`serviceparameters_id`),
  KEY `service_service_parameters_91a0ac17` (`service_id`),
  KEY `service_service_parameters_a5b63034` (`serviceparameters_id`),
  CONSTRAINT `serviceparameters_id_refs_id_df6d55ae` FOREIGN KEY (`serviceparameters_id`) REFERENCES `service_serviceparameters` (`id`),
  CONSTRAINT `service_id_refs_id_8b31e9ca` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_service_parameters`
--

LOCK TABLES `service_service_parameters` WRITE;
/*!40000 ALTER TABLE `service_service_parameters` DISABLE KEYS */;
INSERT INTO `service_service_parameters` VALUES (1,1,1);
/*!40000 ALTER TABLE `service_service_parameters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_serviceparameters`
--

DROP TABLE IF EXISTS `service_serviceparameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_serviceparameters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parameter_description` varchar(250) NOT NULL,
  `max_check_attempts` int(11) NOT NULL,
  `check_interval` int(11) NOT NULL,
  `retry_interval` int(11) DEFAULT NULL,
  `check_period` varchar(100) DEFAULT NULL,
  `notification_interval` int(11) DEFAULT NULL,
  `notification_period` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_serviceparameters`
--

LOCK TABLES `service_serviceparameters` WRITE;
/*!40000 ALTER TABLE `service_serviceparameters` DISABLE KEYS */;
INSERT INTO `service_serviceparameters` VALUES (1,'default',5,5,3,'24x7',30,'24x7');
/*!40000 ALTER TABLE `service_serviceparameters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `site_instance_siteinstance`
--

DROP TABLE IF EXISTS `site_instance_siteinstance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `site_instance_siteinstance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` longtext,
  `site_ip` char(15) NOT NULL,
  `agent_port` int(11) DEFAULT NULL,
  `live_status_tcp_port` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site_instance_siteinstance`
--

LOCK TABLES `site_instance_siteinstance` WRITE;
/*!40000 ALTER TABLE `site_instance_siteinstance` DISABLE KEYS */;
INSERT INTO `site_instance_siteinstance` VALUES (1,'default','Default','127.0.0.1',6556,6557);
/*!40000 ALTER TABLE `site_instance_siteinstance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `south_migrationhistory`
--

DROP TABLE IF EXISTS `south_migrationhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `south_migrationhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) NOT NULL,
  `migration` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `south_migrationhistory`
--

LOCK TABLES `south_migrationhistory` WRITE;
/*!40000 ALTER TABLE `south_migrationhistory` DISABLE KEYS */;
INSERT INTO `south_migrationhistory` VALUES (1,'django_extensions','0001_empty','2014-05-28 14:10:13'),(2,'preventconcurrentlogins','0001_initial','2014-05-28 14:10:13');
/*!40000 ALTER TABLE `south_migrationhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_organization`
--

DROP TABLE IF EXISTS `user_group_organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_organization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `description` longtext,
  `user_group_id` int(11) NOT NULL,
  `device_group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `user_group_organization_1a56174b` (`user_group_id`),
  KEY `user_group_organization_a4353bbd` (`device_group_id`),
  CONSTRAINT `device_group_id_refs_id_e0b88775` FOREIGN KEY (`device_group_id`) REFERENCES `device_group_devicegroup` (`id`),
  CONSTRAINT `user_group_id_refs_id_465fbfa5` FOREIGN KEY (`user_group_id`) REFERENCES `user_group_usergroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_organization`
--

LOCK TABLES `user_group_organization` WRITE;
/*!40000 ALTER TABLE `user_group_organization` DISABLE KEYS */;
INSERT INTO `user_group_organization` VALUES (1,'default','Default organizatio',1,1);
/*!40000 ALTER TABLE `user_group_organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_usergroup`
--

DROP TABLE IF EXISTS `user_group_usergroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_usergroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `alias` varchar(50) NOT NULL,
  `address` varchar(100) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `is_deleted` int(11) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `user_group_usergroup_410d0aac` (`parent_id`),
  KEY `user_group_usergroup_329f6fb3` (`lft`),
  KEY `user_group_usergroup_e763210f` (`rght`),
  KEY `user_group_usergroup_ba470c4a` (`tree_id`),
  KEY `user_group_usergroup_20e079f4` (`level`),
  CONSTRAINT `parent_id_refs_id_aa9a5c51` FOREIGN KEY (`parent_id`) REFERENCES `user_group_usergroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_usergroup`
--

LOCK TABLES `user_group_usergroup` WRITE;
/*!40000 ALTER TABLE `user_group_usergroup` DISABLE KEYS */;
INSERT INTO `user_group_usergroup` VALUES (1,'default','Default','','',NULL,0,1,2,1,0);
/*!40000 ALTER TABLE `user_group_usergroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_profile_department`
--

DROP TABLE IF EXISTS `user_profile_department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_profile_department` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_profile_id` int(11) NOT NULL,
  `user_group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_profile_department_82936d91` (`user_profile_id`),
  KEY `user_profile_department_1a56174b` (`user_group_id`),
  CONSTRAINT `user_group_id_refs_id_df2477c9` FOREIGN KEY (`user_group_id`) REFERENCES `user_group_usergroup` (`id`),
  CONSTRAINT `user_profile_id_refs_user_ptr_id_dbc35572` FOREIGN KEY (`user_profile_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_department`
--

LOCK TABLES `user_profile_department` WRITE;
/*!40000 ALTER TABLE `user_profile_department` DISABLE KEYS */;
INSERT INTO `user_profile_department` VALUES (1,2,1);
/*!40000 ALTER TABLE `user_profile_department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_profile_roles`
--

DROP TABLE IF EXISTS `user_profile_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_profile_roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_name` varchar(100) DEFAULT NULL,
  `role_description` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_roles`
--

LOCK TABLES `user_profile_roles` WRITE;
/*!40000 ALTER TABLE `user_profile_roles` DISABLE KEYS */;
INSERT INTO `user_profile_roles` VALUES (1,'admin','Admin'),(2,'operator','Operator'),(3,'viewer','Viewer');
/*!40000 ALTER TABLE `user_profile_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_profile_userprofile`
--

DROP TABLE IF EXISTS `user_profile_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_profile_userprofile` (
  `user_ptr_id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `company` varchar(100) DEFAULT NULL,
  `designation` varchar(100) DEFAULT NULL,
  `address` varchar(150) DEFAULT NULL,
  `comment` longtext,
  `is_deleted` int(11) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`user_ptr_id`),
  KEY `user_profile_userprofile_410d0aac` (`parent_id`),
  KEY `user_profile_userprofile_329f6fb3` (`lft`),
  KEY `user_profile_userprofile_e763210f` (`rght`),
  KEY `user_profile_userprofile_ba470c4a` (`tree_id`),
  KEY `user_profile_userprofile_20e079f4` (`level`),
  CONSTRAINT `parent_id_refs_user_ptr_id_3df13107` FOREIGN KEY (`parent_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`),
  CONSTRAINT `user_ptr_id_refs_id_759b3408` FOREIGN KEY (`user_ptr_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_userprofile`
--

LOCK TABLES `user_profile_userprofile` WRITE;
/*!40000 ALTER TABLE `user_profile_userprofile` DISABLE KEYS */;
INSERT INTO `user_profile_userprofile` VALUES (2,NULL,'','','','',NULL,0,1,2,1,0);
/*!40000 ALTER TABLE `user_profile_userprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_profile_userprofile_role`
--

DROP TABLE IF EXISTS `user_profile_userprofile_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_profile_userprofile_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userprofile_id` int(11) NOT NULL,
  `roles_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userprofile_id` (`userprofile_id`,`roles_id`),
  KEY `user_profile_userprofile_role_1be1924f` (`userprofile_id`),
  KEY `user_profile_userprofile_role_e48d293c` (`roles_id`),
  CONSTRAINT `roles_id_refs_id_9a44ad44` FOREIGN KEY (`roles_id`) REFERENCES `user_profile_roles` (`id`),
  CONSTRAINT `userprofile_id_refs_user_ptr_id_43acc040` FOREIGN KEY (`userprofile_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_userprofile_role`
--

LOCK TABLES `user_profile_userprofile_role` WRITE;
/*!40000 ALTER TABLE `user_profile_userprofile_role` DISABLE KEYS */;
INSERT INTO `user_profile_userprofile_role` VALUES (1,2,1);
/*!40000 ALTER TABLE `user_profile_userprofile_role` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-05-28 23:08:17
