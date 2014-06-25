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
-- Table structure for table `device_group_devicegroup_devices`
--

DROP TABLE IF EXISTS `device_group_devicegroup_devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_group_devicegroup_devices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `devicegroup_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `devicegroup_id` (`devicegroup_id`,`device_id`),
  KEY `device_group_devicegroup_devices_3d849cc4` (`devicegroup_id`),
  KEY `device_group_devicegroup_devices_b6860804` (`device_id`),
  CONSTRAINT `devicegroup_id_refs_id_9ad5207e` FOREIGN KEY (`devicegroup_id`) REFERENCES `device_group_devicegroup` (`id`),
  CONSTRAINT `device_id_refs_id_91bb4273` FOREIGN KEY (`device_id`) REFERENCES `device_device` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_group_devicegroup_devices`
--

LOCK TABLES `device_group_devicegroup_devices` WRITE;
/*!40000 ALTER TABLE `device_group_devicegroup_devices` DISABLE KEYS */;
INSERT INTO `device_group_devicegroup_devices` VALUES (1,1,1);
/*!40000 ALTER TABLE `device_group_devicegroup_devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_sector`
--

DROP TABLE IF EXISTS `inventory_sector`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_sector` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `sector_id` varchar(250) DEFAULT NULL,
  `base_station_id` int(11) NOT NULL,
  `idu_id` int(11) DEFAULT NULL,
  `idu_port` int(11) DEFAULT NULL,
  `odu_id` int(11) DEFAULT NULL,
  `odu_port` int(11) DEFAULT NULL,
  `antenna_id` int(11) DEFAULT NULL,
  `mrc` varchar(4) DEFAULT NULL,
  `tx_power` int(11) DEFAULT NULL,
  `frequency` int(11) DEFAULT NULL,
  `frame_length` int(11) DEFAULT NULL,
  `cell_radius` int(11) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_sector_2ae13a96` (`base_station_id`),
  KEY `inventory_sector_43292ed6` (`idu_id`),
  KEY `inventory_sector_4651cafe` (`odu_id`),
  KEY `inventory_sector_c42a47b3` (`antenna_id`),
  CONSTRAINT `antenna_id_refs_id_17c7ec16` FOREIGN KEY (`antenna_id`) REFERENCES `inventory_antenna` (`id`),
  CONSTRAINT `base_station_id_refs_id_623a0db0` FOREIGN KEY (`base_station_id`) REFERENCES `inventory_basestation` (`id`),
  CONSTRAINT `idu_id_refs_id_589ca1cf` FOREIGN KEY (`idu_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `odu_id_refs_id_589ca1cf` FOREIGN KEY (`odu_id`) REFERENCES `device_device` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_sector`
--

LOCK TABLES `inventory_sector` WRITE;
/*!40000 ALTER TABLE `inventory_sector` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_sector` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=148 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add content type',4,'add_contenttype'),(11,'Can change content type',4,'change_contenttype'),(12,'Can delete content type',4,'delete_contenttype'),(13,'Can add session',5,'add_session'),(14,'Can change session',5,'change_session'),(15,'Can delete session',5,'delete_session'),(16,'Can add site',6,'add_site'),(17,'Can change site',6,'change_site'),(18,'Can delete site',6,'delete_site'),(19,'Can add migration history',7,'add_migrationhistory'),(20,'Can change migration history',7,'change_migrationhistory'),(21,'Can delete migration history',7,'delete_migrationhistory'),(22,'Can add user profile',8,'add_userprofile'),(23,'Can change user profile',8,'change_userprofile'),(24,'Can delete user profile',8,'delete_userprofile'),(25,'Can add roles',9,'add_roles'),(26,'Can change roles',9,'change_roles'),(27,'Can delete roles',9,'delete_roles'),(28,'Can add user group',10,'add_usergroup'),(29,'Can change user group',10,'change_usergroup'),(30,'Can delete user group',10,'delete_usergroup'),(31,'Can add country',11,'add_country'),(32,'Can change country',11,'change_country'),(33,'Can delete country',11,'delete_country'),(34,'Can add state',12,'add_state'),(35,'Can change state',12,'change_state'),(36,'Can delete state',12,'delete_state'),(37,'Can add city',13,'add_city'),(38,'Can change city',13,'change_city'),(39,'Can delete city',13,'delete_city'),(40,'Can add state geo info',14,'add_stategeoinfo'),(41,'Can change state geo info',14,'change_stategeoinfo'),(42,'Can delete state geo info',14,'delete_stategeoinfo'),(43,'Can add device frequency',15,'add_devicefrequency'),(44,'Can change device frequency',15,'change_devicefrequency'),(45,'Can delete device frequency',15,'delete_devicefrequency'),(46,'Can add device port',16,'add_deviceport'),(47,'Can change device port',16,'change_deviceport'),(48,'Can delete device port',16,'delete_deviceport'),(49,'Can add device type',17,'add_devicetype'),(50,'Can change device type',17,'change_devicetype'),(51,'Can delete device type',17,'delete_devicetype'),(52,'Can add device model',18,'add_devicemodel'),(53,'Can change device model',18,'change_devicemodel'),(54,'Can delete device model',18,'delete_devicemodel'),(55,'Can add device vendor',19,'add_devicevendor'),(56,'Can change device vendor',19,'change_devicevendor'),(57,'Can delete device vendor',19,'delete_devicevendor'),(58,'Can add device technology',20,'add_devicetechnology'),(59,'Can change device technology',20,'change_devicetechnology'),(60,'Can delete device technology',20,'delete_devicetechnology'),(61,'Can add device',21,'add_device'),(62,'Can change device',21,'change_device'),(63,'Can delete device',21,'delete_device'),(64,'Can add model type',22,'add_modeltype'),(65,'Can change model type',22,'change_modeltype'),(66,'Can delete model type',22,'delete_modeltype'),(67,'Can add vendor model',23,'add_vendormodel'),(68,'Can change vendor model',23,'change_vendormodel'),(69,'Can delete vendor model',23,'delete_vendormodel'),(70,'Can add technology vendor',24,'add_technologyvendor'),(71,'Can change technology vendor',24,'change_technologyvendor'),(72,'Can delete technology vendor',24,'delete_technologyvendor'),(73,'Can add device type fields',25,'add_devicetypefields'),(74,'Can change device type fields',25,'change_devicetypefields'),(75,'Can delete device type fields',25,'delete_devicetypefields'),(76,'Can add device type fields value',26,'add_devicetypefieldsvalue'),(77,'Can change device type fields value',26,'change_devicetypefieldsvalue'),(78,'Can delete device type fields value',26,'delete_devicetypefieldsvalue'),(79,'Can add device group',27,'add_devicegroup'),(80,'Can change device group',27,'change_devicegroup'),(81,'Can delete device group',27,'delete_devicegroup'),(82,'Can add inventory',28,'add_inventory'),(83,'Can change inventory',28,'change_inventory'),(84,'Can delete inventory',28,'delete_inventory'),(85,'Can add antenna',29,'add_antenna'),(86,'Can change antenna',29,'change_antenna'),(87,'Can delete antenna',29,'delete_antenna'),(88,'Can add backhaul',30,'add_backhaul'),(89,'Can change backhaul',30,'change_backhaul'),(90,'Can delete backhaul',30,'delete_backhaul'),(91,'Can add base station',31,'add_basestation'),(92,'Can change base station',31,'change_basestation'),(93,'Can delete base station',31,'delete_basestation'),(94,'Can add sector',32,'add_sector'),(95,'Can change sector',32,'change_sector'),(96,'Can delete sector',32,'delete_sector'),(97,'Can add customer',33,'add_customer'),(98,'Can change customer',33,'change_customer'),(99,'Can delete customer',33,'delete_customer'),(100,'Can add sub station',34,'add_substation'),(101,'Can change sub station',34,'change_substation'),(102,'Can delete sub station',34,'delete_substation'),(103,'Can add circuit',35,'add_circuit'),(104,'Can change circuit',35,'change_circuit'),(105,'Can delete circuit',35,'delete_circuit'),(106,'Can add organization',36,'add_organization'),(107,'Can change organization',36,'change_organization'),(108,'Can delete organization',36,'delete_organization'),(109,'Can add service data source',37,'add_servicedatasource'),(110,'Can change service data source',37,'change_servicedatasource'),(111,'Can delete service data source',37,'delete_servicedatasource'),(112,'Can add service parameters',38,'add_serviceparameters'),(113,'Can change service parameters',38,'change_serviceparameters'),(114,'Can delete service parameters',38,'delete_serviceparameters'),(115,'Can add service',39,'add_service'),(116,'Can change service',39,'change_service'),(117,'Can delete service',39,'delete_service'),(118,'Can add service group',40,'add_servicegroup'),(119,'Can change service group',40,'change_servicegroup'),(120,'Can delete service group',40,'delete_servicegroup'),(121,'Can add command',41,'add_command'),(122,'Can change command',41,'change_command'),(123,'Can delete command',41,'delete_command'),(124,'Can add site instance',42,'add_siteinstance'),(125,'Can change site instance',42,'change_siteinstance'),(126,'Can delete site instance',42,'delete_siteinstance'),(127,'Can add machine',43,'add_machine'),(128,'Can change machine',43,'change_machine'),(129,'Can delete machine',43,'delete_machine'),(130,'Can add performance metric',44,'add_performancemetric'),(131,'Can change performance metric',44,'change_performancemetric'),(132,'Can delete performance metric',44,'delete_performancemetric'),(133,'Can add log entry',45,'add_logentry'),(134,'Can change log entry',45,'change_logentry'),(135,'Can delete log entry',45,'delete_logentry'),(136,'Can add activity stream action',46,'add_activitystreamaction'),(137,'Can change activity stream action',46,'change_activitystreamaction'),(138,'Can delete activity stream action',46,'delete_activitystreamaction'),(139,'Can add visitor',47,'add_visitor'),(140,'Can change visitor',47,'change_visitor'),(141,'Can delete visitor',47,'delete_visitor'),(142,'Can add follow',48,'add_follow'),(143,'Can change follow',48,'change_follow'),(144,'Can delete follow',48,'delete_follow'),(145,'Can add action',49,'add_action'),(146,'Can change action',49,'change_action'),(147,'Can delete action',49,'delete_action');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'group_admin'),(2,'group_operator'),(3,'group_viewer');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_inventory_device_groups`
--

DROP TABLE IF EXISTS `inventory_inventory_device_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_inventory_device_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `inventory_id` int(11) NOT NULL,
  `devicegroup_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inventory_id` (`inventory_id`,`devicegroup_id`),
  KEY `inventory_inventory_device_groups_3d10c1ee` (`inventory_id`),
  KEY `inventory_inventory_device_groups_3d849cc4` (`devicegroup_id`),
  CONSTRAINT `devicegroup_id_refs_id_92fd7d4c` FOREIGN KEY (`devicegroup_id`) REFERENCES `device_group_devicegroup` (`id`),
  CONSTRAINT `inventory_id_refs_id_5374ffee` FOREIGN KEY (`inventory_id`) REFERENCES `inventory_inventory` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_inventory_device_groups`
--

LOCK TABLES `inventory_inventory_device_groups` WRITE;
/*!40000 ALTER TABLE `inventory_inventory_device_groups` DISABLE KEYS */;
INSERT INTO `inventory_inventory_device_groups` VALUES (1,1,1);
/*!40000 ALTER TABLE `inventory_inventory_device_groups` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=229 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
INSERT INTO `auth_user_user_permissions` VALUES (215,2,1),(191,2,2),(159,2,3),(121,2,4),(216,2,5),(192,2,6),(160,2,7),(122,2,8),(217,2,9),(117,2,22),(118,2,23),(116,2,24),(119,2,28),(120,2,29),(176,2,30),(175,2,31),(174,2,32),(173,2,33),(180,2,34),(179,2,35),(178,2,36),(177,2,37),(172,2,38),(171,2,39),(213,2,40),(115,2,41),(211,2,42),(212,2,43),(209,2,44),(210,2,45),(207,2,46),(228,2,47),(205,2,48),(206,2,49),(140,2,50),(139,2,51),(142,2,52),(141,2,53),(136,2,54),(135,2,55),(138,2,56),(137,2,57),(134,2,58),(133,2,59),(181,2,60),(182,2,61),(183,2,62),(184,2,63),(185,2,64),(186,2,65),(187,2,66),(188,2,67),(189,2,68),(190,2,69),(225,2,70),(224,2,71),(223,2,72),(222,2,73),(221,2,74),(220,2,75),(219,2,76),(218,2,77),(227,2,78),(226,2,79),(153,2,80),(154,2,81),(151,2,82),(152,2,83),(157,2,84),(158,2,85),(208,2,86),(214,2,87),(145,2,88),(146,2,89),(196,2,90),(195,2,91),(198,2,92),(197,2,93),(200,2,94),(199,2,95),(202,2,96),(201,2,97),(194,2,98),(193,2,99),(165,2,100),(166,2,101),(163,2,102),(164,2,103),(169,2,104),(170,2,105),(167,2,106),(168,2,107),(161,2,108),(162,2,109),(148,2,110),(147,2,111),(150,2,112),(149,2,113),(144,2,114),(143,2,115),(204,2,116),(203,2,117),(156,2,118),(155,2,119),(123,2,120),(124,2,121),(125,2,122),(126,2,123),(127,2,124),(128,2,125),(129,2,126),(130,2,127),(131,2,128),(132,2,129);
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
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
  `organization_id` int(11) NOT NULL,
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
  KEY `user_profile_userprofile_de772da3` (`organization_id`),
  KEY `user_profile_userprofile_329f6fb3` (`lft`),
  KEY `user_profile_userprofile_e763210f` (`rght`),
  KEY `user_profile_userprofile_ba470c4a` (`tree_id`),
  KEY `user_profile_userprofile_20e079f4` (`level`),
  CONSTRAINT `organization_id_refs_id_8bdf5a78` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `parent_id_refs_user_ptr_id_3df13107` FOREIGN KEY (`parent_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`),
  CONSTRAINT `user_ptr_id_refs_id_759b3408` FOREIGN KEY (`user_ptr_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_userprofile`
--

LOCK TABLES `user_profile_userprofile` WRITE;
/*!40000 ALTER TABLE `user_profile_userprofile` DISABLE KEYS */;
INSERT INTO `user_profile_userprofile` VALUES (2,NULL,1,NULL,NULL,NULL,NULL,NULL,0,4,4,0,0),(3,2,1,'','','','','Nocout default operator.',0,0,1,0,1),(4,2,1,'','','','','',0,2,3,0,1);
/*!40000 ALTER TABLE `user_profile_userprofile` ENABLE KEYS */;
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
-- Table structure for table `device_devicetype_device_port`
--

DROP TABLE IF EXISTS `device_devicetype_device_port`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetype_device_port` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `devicetype_id` int(11) NOT NULL,
  `deviceport_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `devicetype_id` (`devicetype_id`,`deviceport_id`),
  KEY `device_devicetype_device_port_4ad84a8d` (`devicetype_id`),
  KEY `device_devicetype_device_port_4475dc69` (`deviceport_id`),
  CONSTRAINT `deviceport_id_refs_id_39fc2259` FOREIGN KEY (`deviceport_id`) REFERENCES `device_deviceport` (`id`),
  CONSTRAINT `devicetype_id_refs_id_2767ff75` FOREIGN KEY (`devicetype_id`) REFERENCES `device_devicetype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicetype_device_port`
--

LOCK TABLES `device_devicetype_device_port` WRITE;
/*!40000 ALTER TABLE `device_devicetype_device_port` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_devicetype_device_port` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_inventory`
--

DROP TABLE IF EXISTS `inventory_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_inventory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `organization_id` int(11) NOT NULL,
  `user_group_id` int(11) NOT NULL,
  `city` varchar(200) DEFAULT NULL,
  `state` varchar(200) DEFAULT NULL,
  `country` varchar(200) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_inventory_de772da3` (`organization_id`),
  KEY `inventory_inventory_1a56174b` (`user_group_id`),
  CONSTRAINT `organization_id_refs_id_a0b4675d` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `user_group_id_refs_id_e2f206a1` FOREIGN KEY (`user_group_id`) REFERENCES `user_group_usergroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_inventory`
--

LOCK TABLES `inventory_inventory` WRITE;
/*!40000 ALTER TABLE `inventory_inventory` DISABLE KEYS */;
INSERT INTO `inventory_inventory` VALUES (1,'default','Default',1,1,'','','','It\'s default inventory.');
/*!40000 ALTER TABLE `inventory_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_deviceport`
--

DROP TABLE IF EXISTS `device_deviceport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_deviceport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `port_name` varchar(100) NOT NULL,
  `port_value` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_deviceport`
--

LOCK TABLES `device_deviceport` WRITE;
/*!40000 ALTER TABLE `device_deviceport` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_deviceport` ENABLE KEYS */;
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
-- Table structure for table `performance_performancemetric`
--

DROP TABLE IF EXISTS `performance_performancemetric`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancemetric` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_id` int(11) DEFAULT NULL,
  `site_id` int(11) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `current_value` varchar(20) NOT NULL,
  `min_value` varchar(20) NOT NULL,
  `max_value` varchar(20) NOT NULL,
  `avg_value` varchar(20) NOT NULL,
  `warning_threshold` varchar(20) NOT NULL,
  `critical_threshold` varchar(20) NOT NULL,
  `sys_timestamp` datetime DEFAULT NULL,
  `check_timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `performance_performancemetric`
--

LOCK TABLES `performance_performancemetric` WRITE;
/*!40000 ALTER TABLE `performance_performancemetric` DISABLE KEYS */;
/*!40000 ALTER TABLE `performance_performancemetric` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_backhaul`
--

DROP TABLE IF EXISTS `inventory_backhaul`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_backhaul` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `bh_configured_on_id` int(11) DEFAULT NULL,
  `bh_port` int(11) DEFAULT NULL,
  `bh_type` varchar(250) DEFAULT NULL,
  `pop_id` int(11) DEFAULT NULL,
  `pop_port` int(11) DEFAULT NULL,
  `aggregator_id` int(11) DEFAULT NULL,
  `aggregator_port` int(11) DEFAULT NULL,
  `pe_hostname` varchar(250) DEFAULT NULL,
  `pe_ip` char(15) DEFAULT NULL,
  `bh_connectivity` varchar(40) DEFAULT NULL,
  `bh_circuit_id` varchar(250) DEFAULT NULL,
  `bh_capacity` int(11) DEFAULT NULL,
  `ttsl_circuit_id` varchar(250) DEFAULT NULL,
  `dr_site` varchar(150) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_backhaul_366352e4` (`bh_configured_on_id`),
  KEY `inventory_backhaul_25fe84e8` (`pop_id`),
  KEY `inventory_backhaul_3fedd201` (`aggregator_id`),
  CONSTRAINT `aggregator_id_refs_id_1a6887f3` FOREIGN KEY (`aggregator_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `bh_configured_on_id_refs_id_1a6887f3` FOREIGN KEY (`bh_configured_on_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `pop_id_refs_id_1a6887f3` FOREIGN KEY (`pop_id`) REFERENCES `device_device` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_backhaul`
--

LOCK TABLES `inventory_backhaul` WRITE;
/*!40000 ALTER TABLE `inventory_backhaul` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_backhaul` ENABLE KEYS */;
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
-- Table structure for table `inventory_customer`
--

DROP TABLE IF EXISTS `inventory_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `city` varchar(250) NOT NULL,
  `state` varchar(250) NOT NULL,
  `address` varchar(250) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_customer`
--

LOCK TABLES `inventory_customer` WRITE;
/*!40000 ALTER TABLE `inventory_customer` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_customer` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES (3,1,37),(2,1,38),(1,1,39),(4,1,91),(6,1,92),(5,1,93);
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_state`
--

DROP TABLE IF EXISTS `device_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_state` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `state_name` varchar(200) DEFAULT NULL,
  `country_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_state_d860be3c` (`country_id`),
  CONSTRAINT `country_id_refs_id_98c8d32c` FOREIGN KEY (`country_id`) REFERENCES `device_country` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_state`
--

LOCK TABLES `device_state` WRITE;
/*!40000 ALTER TABLE `device_state` DISABLE KEYS */;
INSERT INTO `device_state` VALUES (1,'Andhra Pradesh',1),(2,'Arunachal Pradesh',1),(3,'Assam',1),(4,'Bihar',1),(5,'Chhattisgarh',1),(6,'Delhi',1),(7,'Goa',1),(8,'Gujarat',1),(9,'Haryana',1),(10,'Himachal Pradesh',1),(11,'Jammu and Kashmir',1),(12,'Jharkhand',1),(13,'Karnataka',1),(14,'Kerala',1),(15,'Madhya Pradesh',1),(16,'Maharashtra',1),(17,'Manipur',1),(18,'Meghalaya',1),(19,'Mizoram',1),(20,'Nagaland',1),(21,'Orissa',1),(22,'Punjab',1),(23,'Rajasthan',1),(24,'Sikkim',1),(25,'Tamil Nadu',1),(26,'Tripura',1),(27,'Uttarakhand',1),(28,'Uttar Pradesh',1),(29,'West Bengal',1),(30,'Andaman and Nicobar Islands',1),(31,'Lakshadweep',1);
/*!40000 ALTER TABLE `device_state` ENABLE KEYS */;
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
INSERT INTO `django_session` VALUES ('laq57pj9qavgh277sdnb1leyiwo75ws2','NTM0OGJhMWQ2ZjQxMzIyNDU4YWRiYTE5YjBhYmFjN2VlN2M0Y2YyNzp7fQ==','2014-07-08 14:38:53'),('qymxoj3cn0sbmvoyrssh2frjnt2htnte','NTM0OGJhMWQ2ZjQxMzIyNDU4YWRiYTE5YjBhYmFjN2VlN2M0Y2YyNzp7fQ==','2014-07-08 14:48:11'),('u9q9yivo4oh7v53iuv4nidd1hgnjimpo','NTM0OGJhMWQ2ZjQxMzIyNDU4YWRiYTE5YjBhYmFjN2VlN2M0Y2YyNzp7fQ==','2014-07-09 05:45:08');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (4,2,1),(5,3,2),(6,4,3);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_userprofile_role`
--

LOCK TABLES `user_profile_userprofile_role` WRITE;
/*!40000 ALTER TABLE `user_profile_userprofile_role` DISABLE KEYS */;
INSERT INTO `user_profile_userprofile_role` VALUES (1,2,1),(2,3,2),(3,4,3);
/*!40000 ALTER TABLE `user_profile_userprofile_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_circuit`
--

DROP TABLE IF EXISTS `inventory_circuit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_circuit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `circuit_id` varchar(250) NOT NULL,
  `sector_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `sub_station_id` int(11) NOT NULL,
  `date_of_acceptance` datetime DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_circuit_663ed8c9` (`sector_id`),
  KEY `inventory_circuit_09847825` (`customer_id`),
  KEY `inventory_circuit_abc593bb` (`sub_station_id`),
  CONSTRAINT `customer_id_refs_id_eba5adb0` FOREIGN KEY (`customer_id`) REFERENCES `inventory_customer` (`id`),
  CONSTRAINT `sector_id_refs_id_1b7c0cea` FOREIGN KEY (`sector_id`) REFERENCES `inventory_sector` (`id`),
  CONSTRAINT `sub_station_id_refs_id_eedc5892` FOREIGN KEY (`sub_station_id`) REFERENCES `inventory_substation` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_circuit`
--

LOCK TABLES `inventory_circuit` WRITE;
/*!40000 ALTER TABLE `inventory_circuit` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_circuit` ENABLE KEYS */;
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
  `organization_id` int(11) NOT NULL,
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
  `country` int(11) DEFAULT NULL,
  `state` int(11) DEFAULT NULL,
  `city` int(11) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `timezone` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `address` longtext,
  `is_deleted` int(11) NOT NULL,
  `agent_tag` varchar(100) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`),
  UNIQUE KEY `ip_address` (`ip_address`),
  KEY `device_device_a74b81df` (`site_instance_id`),
  KEY `device_device_410d0aac` (`parent_id`),
  KEY `device_device_de772da3` (`organization_id`),
  KEY `device_device_329f6fb3` (`lft`),
  KEY `device_device_e763210f` (`rght`),
  KEY `device_device_ba470c4a` (`tree_id`),
  KEY `device_device_20e079f4` (`level`),
  CONSTRAINT `organization_id_refs_id_0a0a8b43` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `parent_id_refs_id_0679e3c1` FOREIGN KEY (`parent_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `site_instance_id_refs_id_7810d5e5` FOREIGN KEY (`site_instance_id`) REFERENCES `site_instance_siteinstance` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_device`
--

LOCK TABLES `device_device` WRITE;
/*!40000 ALTER TABLE `device_device` DISABLE KEYS */;
INSERT INTO `device_device` VALUES (1,'default','Default',1,NULL,1,1,1,1,1,'127.0.0.1','0:0:0:0:0:0','255.255.255.0','','Disable','Normal','Enable',NULL,NULL,NULL,NULL,NULL,'Asia/Kolkata','It\'s default (localhost) device.','',0,'ping',1,2,1,0);
/*!40000 ALTER TABLE `device_device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_city`
--

DROP TABLE IF EXISTS `device_city`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_city` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `city_name` varchar(250) DEFAULT NULL,
  `state_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_city_5654bf12` (`state_id`),
  CONSTRAINT `state_id_refs_id_443f5d4c` FOREIGN KEY (`state_id`) REFERENCES `device_state` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1469 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_city`
--

LOCK TABLES `device_city` WRITE;
/*!40000 ALTER TABLE `device_city` DISABLE KEYS */;
INSERT INTO `device_city` VALUES (1,'Adilabad',1),(2,'Adoni',1),(3,'Amadalavalasa',1),(4,'Amalapuram',1),(5,'Anakapalle',1),(6,'Anantapur',1),(7,'Badepalle',1),(8,'Banganapalle',1),(9,'Bapatla',1),(10,'Bellampalle',1),(11,'Bethamcherla',1),(12,'Bhadrachalam',1),(13,'Bhainsa',1),(14,'Bheemunipatnam',1),(15,'Bhimavaram',1),(16,'Bhongir',1),(17,'Bobbili',1),(18,'Bodhan',1),(19,'Chilakaluripet',1),(20,'Chirala',1),(21,'Chittoor',1),(22,'Cuddapah',1),(23,'Devarakonda',1),(24,'Dharmavaram',1),(25,'Eluru',1),(26,'Farooqnagar',1),(27,'Gadwal',1),(28,'Gooty',1),(29,'Gudivada',1),(30,'Gudur',1),(31,'Guntakal',1),(32,'Guntur',1),(33,'Hanuman Junction',1),(34,'Hindupur',1),(35,'Hyderabad',1),(36,'Ichchapuram',1),(37,'Jaggaiahpet',1),(38,'Jagtial',1),(39,'Jammalamadugu',1),(40,'Jangaon',1),(41,'Kadapa',1),(42,'Kadiri',1),(43,'Kagaznagar',1),(44,'Kakinada',1),(45,'Kalyandurg',1),(46,'Kamareddy',1),(47,'Kandukur',1),(48,'Karimnagar',1),(49,'Kavali',1),(50,'Khammam',1),(51,'Koratla',1),(52,'Kothagudem',1),(53,'Kothapeta',1),(54,'Kovvur',1),(55,'Kurnool',1),(56,'Kyathampalle',1),(57,'Macherla',1),(58,'Machilipatnam',1),(59,'Madanapalle',1),(60,'Mahbubnagar',1),(61,'Mancherial',1),(62,'Mandamarri',1),(63,'Mandapeta',1),(64,'Manuguru',1),(65,'Markapur',1),(66,'Medak',1),(67,'Miryalaguda',1),(68,'Mogalthur',1),(69,'Nagari',1),(70,'Nagarkurnool',1),(71,'Nandyal',1),(72,'Narasapur',1),(73,'Narasaraopet',1),(74,'Narayanpet',1),(75,'Narsipatnam',1),(76,'Nellore',1),(77,'Nidadavole',1),(78,'Nirmal',1),(79,'Nizamabad',1),(80,'Nuzvid',1),(81,'Ongole',1),(82,'Palacole',1),(83,'Palasa Kasibugga',1),(84,'Palwancha',1),(85,'Parvathipuram',1),(86,'Pedana',1),(87,'Peddapuram',1),(88,'Pithapuram',1),(89,'Pondur',1),(90,'Ponnur',1),(91,'Proddatur',1),(92,'Punganur',1),(93,'Puttur',1),(94,'Rajahmundry',1),(95,'Rajam',1),(96,'Ramachandrapuram',1),(97,'Ramagundam',1),(98,'Rayachoti',1),(99,'Rayadurg',1),(100,'Renigunta',1),(101,'Repalle',1),(102,'Sadasivpet',1),(103,'Salur',1),(104,'Samalkot',1),(105,'Sangareddy',1),(106,'Sattenapalle',1),(107,'Siddipet',1),(108,'Singapur',1),(109,'Sircilla',1),(110,'Srikakulam',1),(111,'Srikalahasti',1),(112,'Suryapet',1),(113,'Tadepalligudem',1),(114,'Tadpatri',1),(115,'Tandur',1),(116,'Tanuku',1),(117,'Tenali',1),(118,'Tirupati',1),(119,'Tuni',1),(120,'Uravakonda',1),(121,'Venkatagiri',1),(122,'Vicarabad',1),(123,'Vijayawada',1),(124,'Vinukonda',1),(125,'Visakhapatnam',1),(126,'Vizianagaram',1),(127,'Wanaparthy',1),(128,'Warangal',1),(129,'Yellandu',1),(130,'Yemmiganur',1),(131,'Yerraguntla',1),(132,'Zahirabad',1),(133,'Rajampet',1),(134,'Along',2),(135,'Bomdila',2),(136,'Itanagar',2),(137,'Naharlagun',2),(138,'Pasighat',2),(139,'Abhayapuri',3),(140,'Amguri',3),(141,'Anandnagaar',3),(142,'Barpeta',3),(143,'Barpeta Road',3),(144,'Bilasipara',3),(145,'Bongaigaon',3),(146,'Dhekiajuli',3),(147,'Dhubri',3),(148,'Dibrugarh',3),(149,'Digboi',3),(150,'Diphu',3),(151,'Dispur',3),(152,'Gauripur',3),(153,'Goalpara',3),(154,'Golaghat',3),(155,'Guwahati',3),(156,'Haflong',3),(157,'Hailakandi',3),(158,'Hojai',3),(159,'Jorhat',3),(160,'Karimganj',3),(161,'Kokrajhar',3),(162,'Lanka',3),(163,'Lumding',3),(164,'Mangaldoi',3),(165,'Mankachar',3),(166,'Margherita',3),(167,'Mariani',3),(168,'Marigaon',3),(169,'Nagaon',3),(170,'Nalbari',3),(171,'North Lakhimpur',3),(172,'Rangia',3),(173,'Sibsagar',3),(174,'Silapathar',3),(175,'Silchar',3),(176,'Tezpur',3),(177,'Tinsukia',3),(178,'Amarpur',4),(179,'Araria',4),(180,'Areraj',4),(181,'Arrah',4),(182,'Asarganj',4),(183,'Aurangabad',4),(184,'Bagaha',4),(185,'Bahadurganj',4),(186,'Bairgania',4),(187,'Bakhtiarpur',4),(188,'Banka',4),(189,'Banmankhi Bazar',4),(190,'Barahiya',4),(191,'Barauli',4),(192,'Barbigha',4),(193,'Barh',4),(194,'Begusarai',4),(195,'Behea',4),(196,'Bettiah',4),(197,'Bhabua',4),(198,'Bhagalpur',4),(199,'Bihar Sharif',4),(200,'Bikramganj',4),(201,'Bodh Gaya',4),(202,'Buxar',4),(203,'Chandan Bara',4),(204,'Chanpatia',4),(205,'Chhapra',4),(206,'Colgong',4),(207,'Dalsinghsarai',4),(208,'Darbhanga',4),(209,'Daudnagar',4),(210,'Dehri-on-Sone',4),(211,'Dhaka',4),(212,'Dighwara',4),(213,'Dumraon',4),(214,'Fatwah',4),(215,'Forbesganj',4),(216,'Gaya',4),(217,'Gogri Jamalpur',4),(218,'Gopalganj',4),(219,'Hajipur',4),(220,'Hilsa',4),(221,'Hisua',4),(222,'Islampur',4),(223,'Jagdispur',4),(224,'Jamalpur',4),(225,'Jamui',4),(226,'Jehanabad',4),(227,'Jhajha',4),(228,'Jhanjharpur',4),(229,'Jogabani',4),(230,'Kanti',4),(231,'Katihar',4),(232,'Khagaria',4),(233,'Kharagpur',4),(234,'Kishanganj',4),(235,'Lakhisarai',4),(236,'Lalganj',4),(237,'Madhepura',4),(238,'Madhubani',4),(239,'Maharajganj',4),(240,'Mahnar Bazar',4),(241,'Makhdumpur',4),(242,'Maner',4),(243,'Manihari',4),(244,'Marhaura',4),(245,'Masaurhi',4),(246,'Mirganj',4),(247,'Mokameh',4),(248,'Motihari',4),(249,'Motipur',4),(250,'Munger',4),(251,'Murliganj',4),(252,'Muzaffarpur',4),(253,'Narkatiaganj',4),(254,'Naugachhia',4),(255,'Nawada',4),(256,'Nokha',4),(257,'Patna',4),(258,'Piro',4),(259,'Purnia',4),(260,'Rafiganj',4),(261,'Rajgir',4),(262,'Ramnagar',4),(263,'Raxaul Bazar',4),(264,'Revelganj',4),(265,'Rosera',4),(266,'Saharsa',4),(267,'Samastipur',4),(268,'Sasaram',4),(269,'Sheikhpura',4),(270,'Sheohar',4),(271,'Sherghati',4),(272,'Silao',4),(273,'Sitamarhi',4),(274,'Siwan',4),(275,'Sonepur',4),(276,'Sugauli',4),(277,'Sultanganj',4),(278,'Supaul',4),(279,'Warisaliganj',4),(280,'Ahiwara',5),(281,'Akaltara',5),(282,'Ambagarh Chowki',5),(283,'Ambikapur',5),(284,'Arang',5),(285,'Bade Bacheli',5),(286,'Balod',5),(287,'Baloda Bazar',5),(288,'Bemetra',5),(289,'Bhatapara',5),(290,'Bilaspur',5),(291,'Birgaon',5),(292,'Champa',5),(293,'Chirmiri',5),(294,'Dalli-Rajhara',5),(295,'Dhamtari',5),(296,'Dipka',5),(297,'Dongargarh',5),(298,'Durg-Bhilai Nagar',5),(299,'Gobranawapara',5),(300,'Jagdalpur',5),(301,'Janjgir',5),(302,'Jashpurnagar',5),(303,'Kanker',5),(304,'Kawardha',5),(305,'Kondagaon',5),(306,'Korba',5),(307,'Mahasamund',5),(308,'Mahendragarh',5),(309,'Mungeli',5),(310,'Naila Janjgir',5),(311,'Raigarh',5),(312,'Raipur',5),(313,'Rajnandgaon',5),(314,'Sakti',5),(315,'Tilda Newra',5),(316,'Asola',6),(317,'Delhi',6),(318,'Aldona',7),(319,'Curchorem Cacora',7),(320,'Madgaon',7),(321,'Mapusa',7),(322,'Margao',7),(323,'Marmagao',7),(324,'Panaji',7),(325,'Ahmedabad',8),(326,'Amreli',8),(327,'Anand',8),(328,'Ankleshwar',8),(329,'Bharuch',8),(330,'Bhavnagar',8),(331,'Bhuj',8),(332,'Cambay',8),(333,'Dahod',8),(334,'Deesa',8),(335,'Dharampur',10),(336,'Dholka',8),(337,'Gandhinagar',8),(338,'Godhra',8),(339,'Himatnagar',8),(340,'Idar',8),(341,'Jamnagar',8),(342,'Junagadh',8),(343,'Kadi',8),(344,'Kalavad',8),(345,'Kalol',8),(346,'Kapadvanj',8),(347,'Karjan',8),(348,'Keshod',8),(349,'Khambhalia',8),(350,'Khambhat',8),(351,'Kheda',8),(352,'Khedbrahma',8),(353,'Kheralu',8),(354,'Kodinar',8),(355,'Lathi',8),(356,'Limbdi',8),(357,'Lunawada',8),(358,'Mahesana',8),(359,'Mahuva',8),(360,'Manavadar',8),(361,'Mandvi',8),(362,'Mangrol',8),(363,'Mansa',8),(364,'Mehmedabad',8),(365,'Modasa',8),(366,'Morvi',8),(367,'Nadiad',8),(368,'Navsari',8),(369,'Padra',8),(370,'Palanpur',8),(371,'Palitana',8),(372,'Pardi',8),(373,'Patan',8),(374,'Petlad',8),(375,'Porbandar',8),(376,'Radhanpur',8),(377,'Rajkot',8),(378,'Rajpipla',8),(379,'Rajula',8),(380,'Ranavav',8),(381,'Rapar',8),(382,'Salaya',8),(383,'Sanand',8),(384,'Savarkundla',8),(385,'Sidhpur',8),(386,'Sihor',8),(387,'Songadh',8),(388,'Surat',8),(389,'Talaja',8),(390,'Thangadh',8),(391,'Tharad',8),(392,'Umbergaon',8),(393,'Umreth',8),(394,'Una',8),(395,'Unjha',8),(396,'Upleta',8),(397,'Vadnagar',8),(398,'Vadodara',8),(399,'Valsad',8),(400,'Vapi',8),(401,'Vapi',8),(402,'Veraval',8),(403,'Vijapur',8),(404,'Viramgam',8),(405,'Visnagar',8),(406,'Vyara',8),(407,'Wadhwan',8),(408,'Wankaner',8),(409,'Adalaj',8),(410,'Adityana',8),(411,'Alang',8),(412,'Ambaji',8),(413,'Ambaliyasan',8),(414,'Andada',8),(415,'Anjar',8),(416,'Anklav',8),(417,'Antaliya',8),(418,'Arambhada',8),(419,'Atul',8),(420,'Ballabhgarh',9),(421,'Ambala',9),(422,'Ambala',9),(423,'Asankhurd',9),(424,'Assandh',9),(425,'Ateli',9),(426,'Babiyal',9),(427,'Bahadurgarh',9),(428,'Barwala',9),(429,'Bhiwani',9),(430,'Charkhi Dadri',9),(431,'Cheeka',9),(432,'Ellenabad 2',9),(433,'Faridabad',9),(434,'Fatehabad',9),(435,'Ganaur',9),(436,'Gharaunda',9),(437,'Gohana',9),(438,'Gurgaon',9),(439,'Haibat(Nagar)',9),(440,'Hansi',9),(441,'Hisar',9),(442,'Hodal',9),(443,'Jhajjar',9),(444,'Jind',9),(445,'Kaithal',9),(446,'Kalan Wali',9),(447,'Kalka',9),(448,'Karnal',9),(449,'Ladwa',9),(450,'Mahendragarh',9),(451,'Mandi Dabwali',9),(452,'Narnaul',9),(453,'Narwana',9),(454,'Palwal',9),(455,'Panchkula',9),(456,'Panipat',9),(457,'Pehowa',9),(458,'Pinjore',9),(459,'Rania',9),(460,'Ratia',9),(461,'Rewari',9),(462,'Rohtak',9),(463,'Safidon',9),(464,'Samalkha',9),(465,'Shahbad',9),(466,'Sirsa',9),(467,'Sohna',9),(468,'Sonipat',9),(469,'Taraori',9),(470,'Thanesar',9),(471,'Tohana',9),(472,'Yamunanagar',9),(473,'Arki',10),(474,'Baddi',10),(475,'Bilaspur',10),(476,'Chamba',10),(477,'Dalhousie',10),(478,'Dharamsala',10),(479,'Hamirpur',10),(480,'Mandi',10),(481,'Nahan',10),(482,'Shimla',10),(483,'Solan',10),(484,'Sundarnagar',10),(485,'Jammu',11),(486,'Achabbal',11),(487,'Akhnoor',11),(488,'Anantnag',11),(489,'Arnia',11),(490,'Awantipora',11),(491,'Bandipore',11),(492,'Baramula',11),(493,'Kathua',11),(494,'Leh',11),(495,'Punch',11),(496,'Rajauri',11),(497,'Sopore',11),(498,'Srinagar',11),(499,'Udhampur',11),(500,'Amlabad',12),(501,'Ara',12),(502,'Barughutu',12),(503,'Bokaro Steel City',12),(504,'Chaibasa',12),(505,'Chakradharpur',12),(506,'Chandrapura',12),(507,'Chatra',12),(508,'Chirkunda',12),(509,'Churi',12),(510,'Daltonganj',12),(511,'Deoghar',12),(512,'Dhanbad',12),(513,'Dumka',12),(514,'Garhwa',12),(515,'Ghatshila',12),(516,'Giridih',12),(517,'Godda',12),(518,'Gomoh',12),(519,'Gumia',12),(520,'Gumla',12),(521,'Hazaribag',12),(522,'Hussainabad',12),(523,'Jamshedpur',12),(524,'Jamtara',12),(525,'Jhumri Tilaiya',12),(526,'Khunti',12),(527,'Lohardaga',12),(528,'Madhupur',12),(529,'Mihijam',12),(530,'Musabani',12),(531,'Pakaur',12),(532,'Patratu',12),(533,'Phusro',12),(534,'Ramngarh',12),(535,'Ranchi',12),(536,'Sahibganj',12),(537,'Saunda',12),(538,'Simdega',12),(539,'Tenu Dam-cum- Kathhara',12),(540,'Arasikere',13),(541,'Bangalore',13),(542,'Belgaum',13),(543,'Bellary',13),(544,'Chamrajnagar',13),(545,'Chikkaballapur',13),(546,'Chintamani',13),(547,'Chitradurga',13),(548,'Gulbarga',13),(549,'Gundlupet',13),(550,'Hassan',13),(551,'Hospet',13),(552,'Hubli',13),(553,'Karkala',13),(554,'Karwar',13),(555,'Kolar',13),(556,'Kota',13),(557,'Lakshmeshwar',13),(558,'Lingsugur',13),(559,'Maddur',13),(560,'Madhugiri',13),(561,'Madikeri',13),(562,'Magadi',13),(563,'Mahalingpur',13),(564,'Malavalli',13),(565,'Malur',13),(566,'Mandya',13),(567,'Mangalore',13),(568,'Manvi',13),(569,'Mudalgi',13),(570,'Mudbidri',13),(571,'Muddebihal',13),(572,'Mudhol',13),(573,'Mulbagal',13),(574,'Mundargi',13),(575,'Mysore',13),(576,'Nanjangud',13),(577,'Pavagada',13),(578,'Puttur',13),(579,'Rabkavi Banhatti',13),(580,'Raichur',13),(581,'Ramanagaram',13),(582,'Ramdurg',13),(583,'Ranibennur',13),(584,'Robertson Pet',13),(585,'Ron',13),(586,'Sadalgi',13),(587,'Sagar',13),(588,'Sakleshpur',13),(589,'Sandur',13),(590,'Sankeshwar',13),(591,'Saundatti-Yellamma',13),(592,'Savanur',13),(593,'Sedam',13),(594,'Shahabad',13),(595,'Shahpur',13),(596,'Shiggaon',13),(597,'Shikapur',13),(598,'Shimoga',13),(599,'Shorapur',13),(600,'Shrirangapattana',13),(601,'Sidlaghatta',13),(602,'Sindgi',13),(603,'Sindhnur',13),(604,'Sira',13),(605,'Sirsi',13),(606,'Siruguppa',13),(607,'Srinivaspur',13),(608,'Talikota',13),(609,'Tarikere',13),(610,'Tekkalakota',13),(611,'Terdal',13),(612,'Tiptur',13),(613,'Tumkur',13),(614,'Udupi',13),(615,'Vijayapura',13),(616,'Wadi',13),(617,'Yadgir',13),(618,'Adoor',14),(619,'Akathiyoor',14),(620,'Alappuzha',14),(621,'Ancharakandy',14),(622,'Aroor',14),(623,'Ashtamichira',14),(624,'Attingal',14),(625,'Avinissery',14),(626,'Chalakudy',14),(627,'Changanassery',14),(628,'Chendamangalam',14),(629,'Chengannur',14),(630,'Cherthala',14),(631,'Cheruthazham',14),(632,'Chittur-Thathamangalam',14),(633,'Chockli',14),(634,'Erattupetta',14),(635,'Guruvayoor',14),(636,'Irinjalakuda',14),(637,'Kadirur',14),(638,'Kalliasseri',14),(639,'Kalpetta',14),(640,'Kanhangad',14),(641,'Kanjikkuzhi',14),(642,'Kannur',14),(643,'Kasaragod',14),(644,'Kayamkulam',14),(645,'Kochi',14),(646,'Kodungallur',14),(647,'Kollam',14),(648,'Koothuparamba',14),(649,'Kothamangalam',14),(650,'Kottayam',14),(651,'Kozhikode',14),(652,'Kunnamkulam',14),(653,'Malappuram',14),(654,'Mattannur',14),(655,'Mavelikkara',14),(656,'Mavoor',14),(657,'Muvattupuzha',14),(658,'Nedumangad',14),(659,'Neyyattinkara',14),(660,'Ottappalam',14),(661,'Palai',14),(662,'Palakkad',14),(663,'Panniyannur',14),(664,'Pappinisseri',14),(665,'Paravoor',14),(666,'Pathanamthitta',14),(667,'Payyannur',14),(668,'Peringathur',14),(669,'Perinthalmanna',14),(670,'Perumbavoor',14),(671,'Ponnani',14),(672,'Punalur',14),(673,'Quilandy',14),(674,'Shoranur',14),(675,'Taliparamba',14),(676,'Thiruvalla',14),(677,'Thiruvananthapuram',14),(678,'Thodupuzha',14),(679,'Thrissur',14),(680,'Tirur',14),(681,'Vadakara',14),(682,'Vaikom',14),(683,'Varkala',14),(684,'Kavaratti',31),(685,'Ashok Nagar',15),(686,'Balaghat',15),(687,'Betul',15),(688,'Bhopal',15),(689,'Burhanpur',15),(690,'Chhatarpur',15),(691,'Dabra',15),(692,'Datia',15),(693,'Dewas',15),(694,'Dhar',15),(695,'Fatehabad',15),(696,'Gwalior',15),(697,'Indore',15),(698,'Itarsi',15),(699,'Jabalpur',15),(700,'Katni',15),(701,'Kotma',15),(702,'Lahar',15),(703,'Lundi',15),(704,'Maharajpur',15),(705,'Mahidpur',15),(706,'Maihar',15),(707,'Malajkhand',15),(708,'Manasa',15),(709,'Manawar',15),(710,'Mandideep',15),(711,'Mandla',15),(712,'Mandsaur',15),(713,'Mauganj',15),(714,'Mhow Cantonment',15),(715,'Mhowgaon',15),(716,'Morena',15),(717,'Multai',15),(718,'Murwara',15),(719,'Nagda',15),(720,'Nainpur',15),(721,'Narsinghgarh',15),(722,'Narsinghgarh',15),(723,'Neemuch',15),(724,'Nepanagar',15),(725,'Niwari',15),(726,'Nowgong',15),(727,'Nowrozabad',15),(728,'Pachore',15),(729,'Pali',15),(730,'Panagar',15),(731,'Pandhurna',15),(732,'Panna',15),(733,'Pasan',15),(734,'Pipariya',15),(735,'Pithampur',15),(736,'Porsa',15),(737,'Prithvipur',15),(738,'Raghogarh-Vijaypur',15),(739,'Rahatgarh',15),(740,'Raisen',15),(741,'Rajgarh',15),(742,'Ratlam',15),(743,'Rau',15),(744,'Rehli',15),(745,'Rewa',15),(746,'Sabalgarh',15),(747,'Sagar',15),(748,'Sanawad',15),(749,'Sarangpur',15),(750,'Sarni',15),(751,'Satna',15),(752,'Sausar',15),(753,'Sehore',15),(754,'Sendhwa',15),(755,'Seoni',15),(756,'Seoni-Malwa',15),(757,'Shahdol',15),(758,'Shajapur',15),(759,'Shamgarh',15),(760,'Sheopur',15),(761,'Shivpuri',15),(762,'Shujalpur',15),(763,'Sidhi',15),(764,'Sihora',15),(765,'Singrauli',15),(766,'Sironj',15),(767,'Sohagpur',15),(768,'Tarana',15),(769,'Tikamgarh',15),(770,'Ujhani',15),(771,'Ujjain',15),(772,'Umaria',15),(773,'Vidisha',15),(774,'Wara Seoni',15),(775,'Ahmednagar',16),(776,'Akola',16),(777,'Amravati',16),(778,'Aurangabad',16),(779,'Baramati',16),(780,'Chalisgaon',16),(781,'Chinchani',16),(782,'Devgarh',16),(783,'Dhule',16),(784,'Dombivli',16),(785,'Durgapur',16),(786,'Ichalkaranji',16),(787,'Jalna',16),(788,'Kalyan',16),(789,'Kolhapur',16),(790,'Latur',16),(791,'Loha',16),(792,'Lonar',16),(793,'Lonavla',16),(794,'Mahad',16),(795,'Mahuli',16),(796,'Malegaon',16),(797,'Malkapur',16),(798,'Manchar',16),(799,'Mangalvedhe',16),(800,'Mangrulpir',16),(801,'Manjlegaon',16),(802,'Manmad',16),(803,'Manwath',16),(804,'Mehkar',16),(805,'Mhaswad',16),(806,'Miraj',16),(807,'Morshi',16),(808,'Mukhed',16),(809,'Mul',16),(810,'Mumbai',16),(811,'Murtijapur',16),(812,'Nagpur',16),(813,'Nalasopara',16),(814,'Nanded-Waghala',16),(815,'Nandgaon',16),(816,'Nandura',16),(817,'Nandurbar',16),(818,'Narkhed',16),(819,'Nashik',16),(820,'Navi Mumbai',16),(821,'Nawapur',16),(822,'Nilanga',16),(823,'Osmanabad',16),(824,'Ozar',16),(825,'Pachora',16),(826,'Paithan',16),(827,'Palghar',16),(828,'Pandharkaoda',16),(829,'Pandharpur',16),(830,'Panvel',16),(831,'Parbhani',16),(832,'Parli',16),(833,'Parola',16),(834,'Partur',16),(835,'Pathardi',16),(836,'Pathri',16),(837,'Patur',16),(838,'Pauni',16),(839,'Pen',16),(840,'Phaltan',16),(841,'Pulgaon',16),(842,'Pune',16),(843,'Purna',16),(844,'Pusad',16),(845,'Rahuri',16),(846,'Rajura',16),(847,'Ramtek',16),(848,'Ratnagiri',16),(849,'Raver',16),(850,'Risod',16),(851,'Sailu',16),(852,'Sangamner',16),(853,'Sangli',16),(854,'Sangole',16),(855,'Sasvad',16),(856,'Satana',16),(857,'Satara',16),(858,'Savner',16),(859,'Sawantwadi',16),(860,'Shahade',16),(861,'Shegaon',16),(862,'Shendurjana',16),(863,'Shirdi',16),(864,'Shirpur-Warwade',16),(865,'Shirur',16),(866,'Shrigonda',16),(867,'Shrirampur',16),(868,'Sillod',16),(869,'Sinnar',16),(870,'Solapur',16),(871,'Soyagaon',16),(872,'Talegaon Dabhade',16),(873,'Talode',16),(874,'Tasgaon',16),(875,'Tirora',16),(876,'Tuljapur',16),(877,'Tumsar',16),(878,'Uran',16),(879,'Uran Islampur',16),(880,'Wadgaon Road',16),(881,'Wai',16),(882,'Wani',16),(883,'Wardha',16),(884,'Warora',16),(885,'Warud',16),(886,'Washim',16),(887,'Yevla',16),(888,'Uchgaon',16),(889,'Udgir',16),(890,'Umarga',16),(891,'Umarkhed',16),(892,'Umred',16),(893,'Vadgaon Kasba',16),(894,'Vaijapur',16),(895,'Vasai',16),(896,'Virar',16),(897,'Vita',16),(898,'Yavatmal',16),(899,'Yawal',16),(900,'Imphal',17),(901,'Kakching',17),(902,'Lilong',17),(903,'Mayang Imphal',17),(904,'Thoubal',17),(905,'Jowai',18),(906,'Nongstoin',18),(907,'Shillong',18),(908,'Tura',18),(909,'Aizawl',19),(910,'Champhai',19),(911,'Lunglei',19),(912,'Saiha',19),(913,'Dimapur',20),(914,'Kohima',20),(915,'Mokokchung',20),(916,'Tuensang',20),(917,'Wokha',20),(918,'Zunheboto',20),(919,'Anandapur',21),(920,'Anugul',21),(921,'Asika',21),(922,'Balangir',21),(923,'Balasore',21),(924,'Baleshwar',21),(925,'Bamra',21),(926,'Barbil',21),(927,'Bargarh',21),(928,'Bargarh',21),(929,'Baripada',21),(930,'Basudebpur',21),(931,'Belpahar',21),(932,'Bhadrak',21),(933,'Bhawanipatna',21),(934,'Bhuban',21),(935,'Bhubaneswar',21),(936,'Biramitrapur',21),(937,'Brahmapur',21),(938,'Brajrajnagar',21),(939,'Byasanagar',21),(940,'Cuttack',21),(941,'Debagarh',21),(942,'Dhenkanal',21),(943,'Gunupur',21),(944,'Hinjilicut',21),(945,'Jagatsinghapur',21),(946,'Jajapur',21),(947,'Jaleswar',21),(948,'Jatani',21),(949,'Jeypur',21),(950,'Jharsuguda',21),(951,'Joda',21),(952,'Kantabanji',21),(953,'Karanjia',21),(954,'Kendrapara',21),(955,'Kendujhar',21),(956,'Khordha',21),(957,'Koraput',21),(958,'Malkangiri',21),(959,'Nabarangapur',21),(960,'Paradip',21),(961,'Parlakhemundi',21),(962,'Pattamundai',21),(963,'Phulabani',21),(964,'Puri',21),(965,'Rairangpur',21),(966,'Rajagangapur',21),(967,'Raurkela',21),(968,'Rayagada',21),(969,'Sambalpur',21),(970,'Soro',21),(971,'Sunabeda',21),(972,'Sundargarh',21),(973,'Talcher',21),(974,'Titlagarh',21),(975,'Umarkote',21),(976,'Ahmedgarh',22),(977,'Amritsar',22),(978,'Barnala',22),(979,'Batala',22),(980,'Bathinda',22),(981,'Bhagha Purana',22),(982,'Budhlada',22),(983,'Chandigarh',22),(984,'Dasua',22),(985,'Dhuri',22),(986,'Dinanagar',22),(987,'Faridkot',22),(988,'Fazilka',22),(989,'Firozpur',22),(990,'Firozpur Cantt.',22),(991,'Giddarbaha',22),(992,'Gobindgarh',22),(993,'Gurdaspur',22),(994,'Hoshiarpur',22),(995,'Jagraon',22),(996,'Jaitu',22),(997,'Jalalabad',22),(998,'Jalandhar',22),(999,'Jalandhar Cantt.',22),(1000,'Jandiala',22),(1001,'Kapurthala',22),(1002,'Karoran',22),(1003,'Kartarpur',22),(1004,'Khanna',22),(1005,'Kharar',22),(1006,'Kot Kapura',22),(1007,'Kurali',22),(1008,'Longowal',22),(1009,'Ludhiana',22),(1010,'Malerkotla',22),(1011,'Malout',22),(1012,'Mansa',22),(1013,'Maur',22),(1014,'Moga',22),(1015,'Mohali',22),(1016,'Morinda',22),(1017,'Mukerian',22),(1018,'Muktsar',22),(1019,'Nabha',22),(1020,'Nakodar',22),(1021,'Nangal',22),(1022,'Nawanshahr',22),(1023,'Pathankot',22),(1024,'Patiala',22),(1025,'Patran',22),(1026,'Patti',22),(1027,'Phagwara',22),(1028,'Phillaur',22),(1029,'Qadian',22),(1030,'Raikot',22),(1031,'Rajpura',22),(1032,'Rampura Phul',22),(1033,'Rupnagar',22),(1034,'Samana',22),(1035,'Sangrur',22),(1036,'Sirhind Fatehgarh Sahib',22),(1037,'Sujanpur',22),(1038,'Sunam',22),(1039,'Talwara',22),(1040,'Tarn Taran',22),(1041,'Urmar Tanda',22),(1042,'Zira',22),(1043,'Zirakpur',22),(1044,'Bali',23),(1045,'Banswara',23),(1046,'Ajmer',23),(1047,'Alwar',23),(1048,'Bandikui',23),(1049,'Baran',23),(1050,'Barmer',23),(1051,'Bikaner',23),(1052,'Fatehpur',23),(1053,'Jaipur',23),(1054,'Jaisalmer',23),(1055,'Jodhpur',23),(1056,'Kota',23),(1057,'Lachhmangarh',23),(1058,'Ladnu',23),(1059,'Lakheri',23),(1060,'Lalsot',23),(1061,'Losal',23),(1062,'Makrana',23),(1063,'Malpura',23),(1064,'Mandalgarh',23),(1065,'Mandawa',23),(1066,'Mangrol',23),(1067,'Merta City',23),(1068,'Mount Abu',23),(1069,'Nadbai',23),(1070,'Nagar',23),(1071,'Nagaur',23),(1072,'Nargund',23),(1073,'Nasirabad',23),(1074,'Nathdwara',23),(1075,'Navalgund',23),(1076,'Nawalgarh',23),(1077,'Neem-Ka-Thana',23),(1078,'Nelamangala',23),(1079,'Nimbahera',23),(1080,'Nipani',23),(1081,'Niwai',23),(1082,'Nohar',23),(1083,'Nokha',23),(1084,'Pali',23),(1085,'Phalodi',23),(1086,'Phulera',23),(1087,'Pilani',23),(1088,'Pilibanga',23),(1089,'Pindwara',23),(1090,'Pipar City',23),(1091,'Prantij',23),(1092,'Pratapgarh',23),(1093,'Raisinghnagar',23),(1094,'Rajakhera',23),(1095,'Rajaldesar',23),(1096,'Rajgarh',23),(1097,'Rajsamand',23),(1098,'Ramganj Mandi',23),(1099,'Ramngarh',23),(1100,'Ratangarh',23),(1101,'Rawatbhata',23),(1102,'Rawatsar',23),(1103,'Reengus',23),(1104,'Sadri',23),(1105,'Sadulshahar',23),(1106,'Sagwara',23),(1107,'Sambhar',23),(1108,'Sanchore',23),(1109,'Sangaria',23),(1110,'Sardarshahar',23),(1111,'Sawai Madhopur',23),(1112,'Shahpura',23),(1113,'Shahpura',23),(1114,'Sheoganj',23),(1115,'Sikar',23),(1116,'Sirohi',23),(1117,'Sojat',23),(1118,'Sri Madhopur',23),(1119,'Sujangarh',23),(1120,'Sumerpur',23),(1121,'Suratgarh',23),(1122,'Taranagar',23),(1123,'Todabhim',23),(1124,'Todaraisingh',23),(1125,'Tonk',23),(1126,'Udaipur',23),(1127,'Udaipurwati',23),(1128,'Vijainagar',23),(1129,'Gangtok',24),(1130,'Arakkonam',25),(1131,'Arcot',25),(1132,'Aruppukkottai',25),(1133,'Bhavani',25),(1134,'Chengalpattu',25),(1135,'Chennai',25),(1136,'Chinna salem',25),(1137,'Coimbatore',25),(1138,'Coonoor',25),(1139,'Cuddalore',25),(1140,'Dharmapuri',25),(1141,'Dindigul',25),(1142,'Erode',25),(1143,'Gudalur',25),(1144,'Gudalur',25),(1145,'Gudalur',25),(1146,'Kanchipuram',25),(1147,'Karaikudi',25),(1148,'Karungal',25),(1149,'Karur',25),(1150,'Kollankodu',25),(1151,'Lalgudi',25),(1152,'Madurai',25),(1153,'Nagapattinam',25),(1154,'Nagercoil',25),(1155,'Namagiripettai',25),(1156,'Namakkal',25),(1157,'Nandivaram-Guduvancheri',25),(1158,'Nanjikottai',25),(1159,'Natham',25),(1160,'Nellikuppam',25),(1161,'Neyveli',25),(1162,'O\' Valley',25),(1163,'Oddanchatram',25),(1164,'P.N.Patti',25),(1165,'Pacode',25),(1166,'Padmanabhapuram',25),(1167,'Palani',25),(1168,'Palladam',25),(1169,'Pallapatti',25),(1170,'Pallikonda',25),(1171,'Panagudi',25),(1172,'Panruti',25),(1173,'Paramakudi',25),(1174,'Parangipettai',25),(1175,'Pattukkottai',25),(1176,'Perambalur',25),(1177,'Peravurani',25),(1178,'Periyakulam',25),(1179,'Periyasemur',25),(1180,'Pernampattu',25),(1181,'Pollachi',25),(1182,'Polur',25),(1183,'Ponneri',25),(1184,'Pudukkottai',25),(1185,'Pudupattinam',25),(1186,'Puliyankudi',25),(1187,'Punjaipugalur',25),(1188,'Rajapalayam',25),(1189,'Ramanathapuram',25),(1190,'Rameshwaram',25),(1191,'Rasipuram',25),(1192,'Salem',25),(1193,'Sankarankoil',25),(1194,'Sankari',25),(1195,'Sathyamangalam',25),(1196,'Sattur',25),(1197,'Shenkottai',25),(1198,'Sholavandan',25),(1199,'Sholingur',25),(1200,'Sirkali',25),(1201,'Sivaganga',25),(1202,'Sivagiri',25),(1203,'Sivakasi',25),(1204,'Srivilliputhur',25),(1205,'Surandai',25),(1206,'Suriyampalayam',25),(1207,'Tenkasi',25),(1208,'Thammampatti',25),(1209,'Thanjavur',25),(1210,'Tharamangalam',25),(1211,'Tharangambadi',25),(1212,'Theni Allinagaram',25),(1213,'Thirumangalam',25),(1214,'Thirunindravur',25),(1215,'Thiruparappu',25),(1216,'Thirupuvanam',25),(1217,'Thiruthuraipoondi',25),(1218,'Thiruvallur',25),(1219,'Thiruvarur',25),(1220,'Thoothukudi',25),(1221,'Thuraiyur',25),(1222,'Tindivanam',25),(1223,'Tiruchendur',25),(1224,'Tiruchengode',25),(1225,'Tiruchirappalli',25),(1226,'Tirukalukundram',25),(1227,'Tirukkoyilur',25),(1228,'Tirunelveli',25),(1229,'Tirupathur',25),(1230,'Tirupathur',25),(1231,'Tiruppur',25),(1232,'Tiruttani',25),(1233,'Tiruvannamalai',25),(1234,'Tiruvethipuram',25),(1235,'Tittakudi',25),(1236,'Udhagamandalam',25),(1237,'Udumalaipettai',25),(1238,'Unnamalaikadai',25),(1239,'Usilampatti',25),(1240,'Uthamapalayam',25),(1241,'Uthiramerur',25),(1242,'Vadakkuvalliyur',25),(1243,'Vadalur',25),(1244,'Vadipatti',25),(1245,'Valparai',25),(1246,'Vandavasi',25),(1247,'Vaniyambadi',25),(1248,'Vedaranyam',25),(1249,'Vellakoil',25),(1250,'Vellore',25),(1251,'Vikramasingapuram',25),(1252,'Viluppuram',25),(1253,'Virudhachalam',25),(1254,'Virudhunagar',25),(1255,'Viswanatham',25),(1256,'Agartala',26),(1257,'Badharghat',26),(1258,'Dharmanagar',26),(1259,'Indranagar',26),(1260,'Jogendranagar',26),(1261,'Kailasahar',26),(1262,'Khowai',26),(1263,'Pratapgarh',26),(1264,'Udaipur',26),(1265,'Achhnera',28),(1266,'Adari',28),(1267,'Agra',28),(1268,'Aligarh',28),(1269,'Allahabad',28),(1270,'Amroha',28),(1271,'Azamgarh',28),(1272,'Bahraich',28),(1273,'Ballia',28),(1274,'Balrampur',28),(1275,'Banda',28),(1276,'Bareilly',28),(1277,'Chandausi',28),(1278,'Dadri',28),(1279,'Deoria',28),(1280,'Etawah',28),(1281,'Fatehabad',28),(1282,'Fatehpur',28),(1283,'Fatehpur',28),(1284,'Greater Noida',28),(1285,'Hamirpur',28),(1286,'Hardoi',28),(1287,'Jajmau',28),(1288,'Jaunpur',28),(1289,'Jhansi',28),(1290,'Kalpi',28),(1291,'Kanpur',28),(1292,'Kota',28),(1293,'Laharpur',28),(1294,'Lakhimpur',28),(1295,'Lal Gopalganj Nindaura',28),(1296,'Lalganj',28),(1297,'Lalitpur',28),(1298,'Lar',28),(1299,'Loni',28),(1300,'Lucknow',28),(1301,'Mathura',28),(1302,'Meerut',28),(1303,'Modinagar',28),(1304,'Muradnagar',28),(1305,'Nagina',28),(1306,'Najibabad',28),(1307,'Nakur',28),(1308,'Nanpara',28),(1309,'Naraura',28),(1310,'Naugawan Sadat',28),(1311,'Nautanwa',28),(1312,'Nawabganj',28),(1313,'Nehtaur',28),(1314,'NOIDA',28),(1315,'Noorpur',28),(1316,'Obra',28),(1317,'Orai',28),(1318,'Padrauna',28),(1319,'Palia Kalan',28),(1320,'Parasi',28),(1321,'Phulpur',28),(1322,'Pihani',28),(1323,'Pilibhit',28),(1324,'Pilkhuwa',28),(1325,'Powayan',28),(1326,'Pukhrayan',28),(1327,'Puranpur',28),(1328,'Purquazi',28),(1329,'Purwa',28),(1330,'Rae Bareli',28),(1331,'Rampur',28),(1332,'Rampur Maniharan',28),(1333,'Rasra',28),(1334,'Rath',28),(1335,'Renukoot',28),(1336,'Reoti',28),(1337,'Robertsganj',28),(1338,'Rudauli',28),(1339,'Rudrapur',28),(1340,'Sadabad',28),(1341,'Safipur',28),(1342,'Saharanpur',28),(1343,'Sahaspur',28),(1344,'Sahaswan',28),(1345,'Sahawar',28),(1346,'Sahjanwa',28),(1347,'Ghazipur',28),(1348,'Sambhal',28),(1349,'Samdhan',28),(1350,'Samthar',28),(1351,'Sandi',28),(1352,'Sandila',28),(1353,'Sardhana',28),(1354,'Seohara',28),(1355,'Shahabad',28),(1356,'Shahganj',28),(1357,'Shahjahanpur',28),(1358,'Shamli',28),(1359,'Shamsabad',28),(1360,'Shamsabad',28),(1361,'Sherkot',28),(1362,'Shikarpur',28),(1363,'Shikohabad',28),(1364,'Shishgarh',28),(1365,'Siana',28),(1366,'Sikanderpur',28),(1367,'Sikandra Rao',28),(1368,'Sikandrabad',28),(1369,'Sirsaganj',28),(1370,'Sirsi',28),(1371,'Sitapur',28),(1372,'Soron',28),(1373,'Suar',28),(1374,'Sultanpur',28),(1375,'Sumerpur',28),(1376,'Tanda',28),(1377,'Tanda',28),(1378,'Tetri Bazar',28),(1379,'Thakurdwara',28),(1380,'Thana Bhawan',28),(1381,'Tilhar',28),(1382,'Tirwaganj',28),(1383,'Tulsipur',28),(1384,'Tundla',28),(1385,'Unnao',28),(1386,'Utraula',28),(1387,'Varanasi',28),(1388,'Vrindavan',28),(1389,'Warhapur',28),(1390,'Zaidpur',28),(1391,'Zamania',28),(1392,'Almora',27),(1393,'Bazpur',27),(1394,'Chamba',27),(1395,'Dehradun',27),(1396,'Haldwani',27),(1397,'Haridwar',27),(1398,'Jaspur',27),(1399,'Kashipur',27),(1400,'kichha',27),(1401,'Kotdwara',27),(1402,'Manglaur',27),(1403,'Mussoorie',27),(1404,'Nagla',27),(1405,'Nainital',27),(1406,'Pauri',27),(1407,'Pithoragarh',27),(1408,'Ramnagar',27),(1409,'Rishikesh',27),(1410,'Roorkee',27),(1411,'Rudrapur',27),(1412,'Sitarganj',27),(1413,'Tehri',27),(1414,'Muzaffarnagar',28),(1415,'Adra',29),(1416,'Alipurduar',29),(1417,'Arambagh',29),(1418,'Asansol',29),(1419,'Baharampur',29),(1420,'Bally',29),(1421,'Balurghat',29),(1422,'Bankura',29),(1423,'Barakar',29),(1424,'Barasat',29),(1425,'Bardhaman',29),(1426,'Bidhan Nagar',29),(1427,'Calcutta',29),(1428,'Chinsura',29),(1429,'Contai',29),(1430,'Cooch Behar',29),(1431,'Darjeeling',29),(1432,'Durgapur',29),(1433,'Haldia',29),(1434,'Howrah',29),(1435,'Islampur',29),(1436,'Jhargram',29),(1437,'Kharagpur',29),(1438,'Kolkata',29),(1439,'Mainaguri',29),(1440,'Mal',29),(1441,'Mathabhanga',29),(1442,'Medinipur',29),(1443,'Memari',29),(1444,'Monoharpur',29),(1445,'Murshidabad',29),(1446,'Nabadwip',29),(1447,'Naihati',29),(1448,'Panchla',29),(1449,'Pandua',29),(1450,'Paschim Punropara',29),(1451,'Purulia',29),(1452,'Raghunathpur',29),(1453,'Raiganj',29),(1454,'Rampurhat',29),(1455,'Ranaghat',29),(1456,'Sainthia',29),(1457,'Santipur',29),(1458,'Siliguri',29),(1459,'Sonamukhi',29),(1460,'Srirampore',29),(1461,'Suri',29),(1462,'Taki',29),(1463,'Tamluk',29),(1464,'Tarakeswar',29),(1465,'Chikmagalur',13),(1466,'Davanagere',13),(1467,'Dharwad',13),(1468,'Gadag',13);
/*!40000 ALTER TABLE `device_city` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `activity_stream_activitystreamaction`
--

DROP TABLE IF EXISTS `activity_stream_activitystreamaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_stream_activitystreamaction` (
  `action_ptr_id` int(11) NOT NULL,
  `action_string` varchar(50) NOT NULL,
  PRIMARY KEY (`action_ptr_id`),
  CONSTRAINT `action_ptr_id_refs_id_b6467e8e` FOREIGN KEY (`action_ptr_id`) REFERENCES `actstream_action` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_stream_activitystreamaction`
--

LOCK TABLES `activity_stream_activitystreamaction` WRITE;
/*!40000 ALTER TABLE `activity_stream_activitystreamaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `activity_stream_activitystreamaction` ENABLE KEYS */;
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
  `device_icon` varchar(200) DEFAULT NULL,
  `device_gmap_icon` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicetype`
--

LOCK TABLES `device_devicetype` WRITE;
/*!40000 ALTER TABLE `device_devicetype` DISABLE KEYS */;
INSERT INTO `device_devicetype` VALUES (1,'Default','Default',NULL,NULL),(2,'Radwin2KSS','Radwin2KSS',NULL,NULL),(3,'Radwin2KBS','Radwin2KBS',NULL,NULL),(4,'StarmaxIDU','StarmaxIDU',NULL,NULL),(5,'StarmaxSS','StarmaxSS',NULL,NULL),(6,'CanopyPM100AP','CanopyPM100AP',NULL,NULL),(7,'CanopyPM100SS','CanopyPM100SS',NULL,NULL),(8,'CanopySM100AP','CanopySM100AP',NULL,NULL),(9,'CanopySM100SS','CanopySM100SS',NULL,NULL);
/*!40000 ALTER TABLE `device_devicetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_devicetype_frequency`
--

DROP TABLE IF EXISTS `device_devicetype_frequency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetype_frequency` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `devicetype_id` int(11) NOT NULL,
  `devicefrequency_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `devicetype_id` (`devicetype_id`,`devicefrequency_id`),
  KEY `device_devicetype_frequency_4ad84a8d` (`devicetype_id`),
  KEY `device_devicetype_frequency_0f8b1f06` (`devicefrequency_id`),
  CONSTRAINT `devicefrequency_id_refs_id_5e59970e` FOREIGN KEY (`devicefrequency_id`) REFERENCES `device_devicefrequency` (`id`),
  CONSTRAINT `devicetype_id_refs_id_d9de052e` FOREIGN KEY (`devicetype_id`) REFERENCES `device_devicetype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicetype_frequency`
--

LOCK TABLES `device_devicetype_frequency` WRITE;
/*!40000 ALTER TABLE `device_devicetype_frequency` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_devicetype_frequency` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_substation`
--

DROP TABLE IF EXISTS `inventory_substation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_substation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `ip` char(15) NOT NULL,
  `mac` varchar(250) NOT NULL,
  `serial_no` varchar(250) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `building_height` int(11) DEFAULT NULL,
  `tower_height` int(11) DEFAULT NULL,
  `ethernet_extender` varchar(250) DEFAULT NULL,
  `city` varchar(250) NOT NULL,
  `state` varchar(250) NOT NULL,
  `address` varchar(250) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_substation`
--

LOCK TABLES `inventory_substation` WRITE;
/*!40000 ALTER TABLE `inventory_substation` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_substation` ENABLE KEYS */;
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
-- Table structure for table `service_service`
--

DROP TABLE IF EXISTS `service_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_service` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'content type','contenttypes','contenttype'),(5,'session','sessions','session'),(6,'site','sites','site'),(7,'migration history','south','migrationhistory'),(8,'user profile','user_profile','userprofile'),(9,'roles','user_profile','roles'),(10,'user group','user_group','usergroup'),(11,'country','device','country'),(12,'state','device','state'),(13,'city','device','city'),(14,'state geo info','device','stategeoinfo'),(15,'device frequency','device','devicefrequency'),(16,'device port','device','deviceport'),(17,'device type','device','devicetype'),(18,'device model','device','devicemodel'),(19,'device vendor','device','devicevendor'),(20,'device technology','device','devicetechnology'),(21,'device','device','device'),(22,'model type','device','modeltype'),(23,'vendor model','device','vendormodel'),(24,'technology vendor','device','technologyvendor'),(25,'device type fields','device','devicetypefields'),(26,'device type fields value','device','devicetypefieldsvalue'),(27,'device group','device_group','devicegroup'),(28,'inventory','inventory','inventory'),(29,'antenna','inventory','antenna'),(30,'backhaul','inventory','backhaul'),(31,'base station','inventory','basestation'),(32,'sector','inventory','sector'),(33,'customer','inventory','customer'),(34,'sub station','inventory','substation'),(35,'circuit','inventory','circuit'),(36,'organization','organization','organization'),(37,'service data source','service','servicedatasource'),(38,'service parameters','service','serviceparameters'),(39,'service','service','service'),(40,'service group','service_group','servicegroup'),(41,'command','command','command'),(42,'site instance','site_instance','siteinstance'),(43,'machine','machine','machine'),(44,'performance metric','performance','performancemetric'),(45,'log entry','admin','logentry'),(46,'activity stream action','activity_stream','activitystreamaction'),(47,'visitor','session_management','visitor'),(48,'follow','actstream','follow'),(49,'action','actstream','action');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_servicedatasource`
--

DROP TABLE IF EXISTS `service_servicedatasource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_servicedatasource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `warning` varchar(255) DEFAULT NULL,
  `critical` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_servicedatasource`
--

LOCK TABLES `service_servicedatasource` WRITE;
/*!40000 ALTER TABLE `service_servicedatasource` DISABLE KEYS */;
/*!40000 ALTER TABLE `service_servicedatasource` ENABLE KEYS */;
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
-- Table structure for table `device_country`
--

DROP TABLE IF EXISTS `device_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_country` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `country_name` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_country`
--

LOCK TABLES `device_country` WRITE;
/*!40000 ALTER TABLE `device_country` DISABLE KEYS */;
INSERT INTO `device_country` VALUES (1,'India');
/*!40000 ALTER TABLE `device_country` ENABLE KEYS */;
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
-- Table structure for table `user_group_usergroup_users`
--

DROP TABLE IF EXISTS `user_group_usergroup_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_usergroup_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usergroup_id` int(11) NOT NULL,
  `userprofile_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usergroup_id` (`usergroup_id`,`userprofile_id`),
  KEY `user_group_usergroup_users_d9f50f95` (`usergroup_id`),
  KEY `user_group_usergroup_users_1be1924f` (`userprofile_id`),
  CONSTRAINT `usergroup_id_refs_id_104f7f7d` FOREIGN KEY (`usergroup_id`) REFERENCES `user_group_usergroup` (`id`),
  CONSTRAINT `userprofile_id_refs_user_ptr_id_bbd81fa0` FOREIGN KEY (`userprofile_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_usergroup_users`
--

LOCK TABLES `user_group_usergroup_users` WRITE;
/*!40000 ALTER TABLE `user_group_usergroup_users` DISABLE KEYS */;
INSERT INTO `user_group_usergroup_users` VALUES (2,1,2),(1,1,3),(3,1,4);
/*!40000 ALTER TABLE `user_group_usergroup_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_devicefrequency`
--

DROP TABLE IF EXISTS `device_devicefrequency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicefrequency` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `frequency_name` varchar(100) NOT NULL,
  `frequency_value` varchar(50) NOT NULL,
  `color_hex_value` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicefrequency`
--

LOCK TABLES `device_devicefrequency` WRITE;
/*!40000 ALTER TABLE `device_devicefrequency` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_devicefrequency` ENABLE KEYS */;
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
  `organization_id` int(11) NOT NULL,
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
  KEY `device_group_devicegroup_de772da3` (`organization_id`),
  KEY `device_group_devicegroup_329f6fb3` (`lft`),
  KEY `device_group_devicegroup_e763210f` (`rght`),
  KEY `device_group_devicegroup_ba470c4a` (`tree_id`),
  KEY `device_group_devicegroup_20e079f4` (`level`),
  CONSTRAINT `organization_id_refs_id_2d22585d` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `parent_id_refs_id_e4aa56d8` FOREIGN KEY (`parent_id`) REFERENCES `device_group_devicegroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_group_devicegroup`
--

LOCK TABLES `device_group_devicegroup` WRITE;
/*!40000 ALTER TABLE `device_group_devicegroup` DISABLE KEYS */;
INSERT INTO `device_group_devicegroup` VALUES (1,'default','Default',NULL,1,'','',0,1,2,1,0);
/*!40000 ALTER TABLE `device_group_devicegroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `actstream_action`
--

DROP TABLE IF EXISTS `actstream_action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actstream_action` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `actor_content_type_id` int(11) NOT NULL,
  `actor_object_id` varchar(255) NOT NULL,
  `verb` varchar(255) NOT NULL,
  `description` longtext,
  `target_content_type_id` int(11) DEFAULT NULL,
  `target_object_id` varchar(255) DEFAULT NULL,
  `action_object_content_type_id` int(11) DEFAULT NULL,
  `action_object_object_id` varchar(255) DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  `public` tinyint(1) NOT NULL,
  `data` text,
  PRIMARY KEY (`id`),
  KEY `actstream_action_3df58830` (`actor_content_type_id`),
  KEY `actstream_action_276d0c93` (`target_content_type_id`),
  KEY `actstream_action_f6b51263` (`action_object_content_type_id`),
  CONSTRAINT `action_object_content_type_id_refs_id_357b994e` FOREIGN KEY (`action_object_content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `actor_content_type_id_refs_id_357b994e` FOREIGN KEY (`actor_content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `target_content_type_id_refs_id_357b994e` FOREIGN KEY (`target_content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actstream_action`
--

LOCK TABLES `actstream_action` WRITE;
/*!40000 ALTER TABLE `actstream_action` DISABLE KEYS */;
INSERT INTO `actstream_action` VALUES (1,3,'2','username : gisadmin loggedin from server name: localhost, server port: 8000',NULL,NULL,NULL,NULL,NULL,'2014-06-24 14:26:21',1,NULL),(2,3,'2','username : gisadmin loggedin from server name: localhost, server port: 8000',NULL,NULL,NULL,NULL,NULL,'2014-06-24 14:26:41',1,NULL),(3,3,'2','username : gisadmin loggedin from server name: localhost, server port: 8000',NULL,NULL,NULL,NULL,NULL,'2014-06-24 14:46:17',1,NULL),(4,3,'2','username : gisadmin loggedin from server name: localhost, server port: 8000',NULL,NULL,NULL,NULL,NULL,'2014-06-25 05:17:32',1,NULL);
/*!40000 ALTER TABLE `actstream_action` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `machine_machine`
--

DROP TABLE IF EXISTS `machine_machine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `machine_machine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `alias` varchar(255) NOT NULL,
  `machine_ip` char(15) DEFAULT NULL,
  `agent_port` int(11) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machine_machine`
--

LOCK TABLES `machine_machine` WRITE;
/*!40000 ALTER TABLE `machine_machine` DISABLE KEYS */;
INSERT INTO `machine_machine` VALUES (1,'default','Default','127.0.0.1',6556,'This is nocout\'s default machine.');
/*!40000 ALTER TABLE `machine_machine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organization_organization`
--

DROP TABLE IF EXISTS `organization_organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `organization_organization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `city` varchar(200) DEFAULT NULL,
  `state` varchar(200) DEFAULT NULL,
  `country` varchar(200) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `description` longtext,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `organization_organization_410d0aac` (`parent_id`),
  KEY `organization_organization_329f6fb3` (`lft`),
  KEY `organization_organization_e763210f` (`rght`),
  KEY `organization_organization_ba470c4a` (`tree_id`),
  KEY `organization_organization_20e079f4` (`level`),
  CONSTRAINT `parent_id_refs_id_7c6043d6` FOREIGN KEY (`parent_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organization_organization`
--

LOCK TABLES `organization_organization` WRITE;
/*!40000 ALTER TABLE `organization_organization` DISABLE KEYS */;
INSERT INTO `organization_organization` VALUES (1,'default','Default','','','',NULL,'It\'s default organization.',0,0,0,0);
/*!40000 ALTER TABLE `organization_organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_basestation`
--

DROP TABLE IF EXISTS `inventory_basestation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_basestation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `bs_site_id` varchar(250) DEFAULT NULL,
  `bs_switch_id` int(11) DEFAULT NULL,
  `backhaul_id` int(11) NOT NULL,
  `bs_type` varchar(40) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `infra_provider` varchar(100) DEFAULT NULL,
  `building_height` int(11) DEFAULT NULL,
  `tower_height` int(11) DEFAULT NULL,
  `gps_type` varchar(100) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_basestation_2d94f56c` (`bs_switch_id`),
  KEY `inventory_basestation_f4d00402` (`backhaul_id`),
  CONSTRAINT `backhaul_id_refs_id_b88aec53` FOREIGN KEY (`backhaul_id`) REFERENCES `inventory_backhaul` (`id`),
  CONSTRAINT `bs_switch_id_refs_id_519fe049` FOREIGN KEY (`bs_switch_id`) REFERENCES `device_device` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_basestation`
--

LOCK TABLES `inventory_basestation` WRITE;
/*!40000 ALTER TABLE `inventory_basestation` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_basestation` ENABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_devicetypefields`
--

LOCK TABLES `device_devicetypefields` WRITE;
/*!40000 ALTER TABLE `device_devicetypefields` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_devicetypefields` ENABLE KEYS */;
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
-- Table structure for table `site_instance_siteinstance`
--

DROP TABLE IF EXISTS `site_instance_siteinstance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `site_instance_siteinstance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `alias` varchar(255) DEFAULT NULL,
  `machine_id` int(11) DEFAULT NULL,
  `site_ip` char(15) NOT NULL,
  `live_status_tcp_port` int(11) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `site_instance_siteinstance_dbaea34e` (`machine_id`),
  CONSTRAINT `machine_id_refs_id_2f639b27` FOREIGN KEY (`machine_id`) REFERENCES `machine_machine` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site_instance_siteinstance`
--

LOCK TABLES `site_instance_siteinstance` WRITE;
/*!40000 ALTER TABLE `site_instance_siteinstance` DISABLE KEYS */;
INSERT INTO `site_instance_siteinstance` VALUES (1,'default','Default',1,'127.0.0.1',6557,'This is nocout\'s default site.');
/*!40000 ALTER TABLE `site_instance_siteinstance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session_management_visitor`
--

DROP TABLE IF EXISTS `session_management_visitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session_management_visitor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `session_key` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_8ab1e430` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_management_visitor`
--

LOCK TABLES `session_management_visitor` WRITE;
/*!40000 ALTER TABLE `session_management_visitor` DISABLE KEYS */;
/*!40000 ALTER TABLE `session_management_visitor` ENABLE KEYS */;
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
-- Table structure for table `actstream_follow`
--

DROP TABLE IF EXISTS `actstream_follow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actstream_follow` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `actor_only` tinyint(1) NOT NULL,
  `started` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`content_type_id`,`object_id`),
  KEY `actstream_follow_6340c63c` (`user_id`),
  KEY `actstream_follow_37ef4eb4` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_5cf623fd` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_40a75718` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actstream_follow`
--

LOCK TABLES `actstream_follow` WRITE;
/*!40000 ALTER TABLE `actstream_follow` DISABLE KEYS */;
/*!40000 ALTER TABLE `actstream_follow` ENABLE KEYS */;
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
-- Table structure for table `service_service_service_data_sources`
--

DROP TABLE IF EXISTS `service_service_service_data_sources`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_service_service_data_sources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `service_id` int(11) NOT NULL,
  `servicedatasource_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `service_id` (`service_id`,`servicedatasource_id`),
  KEY `service_service_service_data_sources_91a0ac17` (`service_id`),
  KEY `service_service_service_data_sources_cc67a75e` (`servicedatasource_id`),
  CONSTRAINT `servicedatasource_id_refs_id_cea890a7` FOREIGN KEY (`servicedatasource_id`) REFERENCES `service_servicedatasource` (`id`),
  CONSTRAINT `service_id_refs_id_b4f5d645` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_service_service_data_sources`
--

LOCK TABLES `service_service_service_data_sources` WRITE;
/*!40000 ALTER TABLE `service_service_service_data_sources` DISABLE KEYS */;
/*!40000 ALTER TABLE `service_service_service_data_sources` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_stategeoinfo`
--

DROP TABLE IF EXISTS `device_stategeoinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_stategeoinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `state_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_stategeoinfo_5654bf12` (`state_id`),
  CONSTRAINT `state_id_refs_id_52db8c3f` FOREIGN KEY (`state_id`) REFERENCES `device_state` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2443 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_stategeoinfo`
--

LOCK TABLES `device_stategeoinfo` WRITE;
/*!40000 ALTER TABLE `device_stategeoinfo` DISABLE KEYS */;
INSERT INTO `device_stategeoinfo` VALUES (1,19.8287253876812,78.299560546875,1),(2,19.6839702358884,78.299560546875,1),(3,19.3733407133641,78.277587890625,1),(4,19.2489223284628,78.101806640625,1),(5,19.2696652965023,77.816162109375,1),(6,18.9998028290533,77.772216796875,1),(7,18.70869162256,77.947998046875,1),(8,18.6462451426706,77.728271484375,1),(9,18.4170786586613,77.530517578125,1),(10,18.1876065524946,77.530517578125,1),(11,17.8742034396575,77.640380859375,1),(12,17.6230817913118,77.486572265625,1),(13,17.4345105515229,77.574462890625,1),(14,17.1197925007871,77.420654296875,1),(15,16.6993402345945,77.464599609375,1),(16,16.3201394531176,77.354736328125,1),(17,16.2990510145818,77.552490234375,1),(18,16.0458134537522,77.464599609375,1),(19,15.8556735099987,77.288818359375,1),(20,15.8556735099987,77.113037109375,1),(21,15.728813770534,76.981201171875,1),(22,15.2205890195781,77.091064453125,1),(23,15.0084636950049,76.981201171875,1),(24,15.0084636950049,76.761474609375,1),(25,14.7111347588707,76.761474609375,1),(26,14.3708339734068,76.959228515625,1),(27,13.9020758525005,76.981201171875,1),(28,13.9447299749202,77.222900390625,1),(29,13.688687769785,77.398681640625,1),(30,13.688687769785,77.618408203125,1),(31,13.8807458420256,77.860107421875,1),(32,13.6032781325288,78.123779296875,1),(33,13.5605617450814,78.387451171875,1),(34,13.3468650145779,78.409423828125,1),(35,13.197164523282,78.607177734375,1),(36,12.6832149118187,78.233642578125,1),(37,12.5760099120638,78.453369140625,1),(38,12.9403221283846,78.717041015625,1),(39,13.0687767343577,79.156494140625,1),(40,13.2399454992863,79.508056640625,1),(41,13.475105944335,79.947509765625,1),(42,13.4537372134192,80.343017578125,1),(43,13.6459868148753,80.299072265625,1),(44,13.7954062031328,80.233154296875,1),(45,14.0726449543803,80.123291015625,1),(46,14.3921180836617,80.233154296875,1),(47,14.7748825065163,80.123291015625,1),(48,15.1569737133777,80.057373046875,1),(49,15.4748574026872,80.255126953125,1),(50,15.7499625727488,80.408935546875,1),(51,15.8133957604606,80.650634765625,1),(52,15.728813770534,80.892333984375,1),(53,15.8556735099987,81.090087890625,1),(54,16.0458134537522,81.177978515625,1),(55,16.2779603062125,81.353759765625,1),(56,16.2779603062125,81.573486328125,1),(57,16.2779603062125,81.793212890625,1),(58,16.4044704567024,82.100830078125,1),(59,16.6151377999871,82.386474609375,1),(60,16.8045410763835,82.386474609375,1),(61,16.9937554528946,82.386474609375,1),(62,17.2037698219175,82.540283203125,1),(63,17.3506383760488,82.781982421875,1),(64,17.7486866517288,83.353271484375,1),(65,18.1249706393865,83.748779296875,1),(66,18.4379246534744,84.298095703125,1),(67,18.6670631919266,84.473876953125,1),(68,19.041348796589,84.737548828125,1),(69,19.1244095280849,84.693603515625,1),(70,18.9374644296419,84.342041015625,1),(71,18.7295019990721,84.188232421875,1),(72,18.7295019990721,83.990478515625,1),(73,18.895892559415,83.814697265625,1),(74,19.041348796589,83.660888671875,1),(75,19.041348796589,83.529052734375,1),(76,18.8751027503565,83.397216796875,1),(77,18.7295019990721,83.177490234375,1),(78,18.5837756883709,83.023681640625,1),(79,18.3545255291266,83.045654296875,1),(80,18.3545255291266,82.891845703125,1),(81,18.3545255291266,82.760009765625,1),(82,18.1667304102219,82.781982421875,1),(83,18.4379246534744,82.518310546875,1),(84,17.9787330955562,82.254638671875,1),(85,17.9787330955562,82.100830078125,1),(86,17.9787330955562,81.793212890625,1),(87,17.7696122471427,81.485595703125,1),(88,17.7696122471427,81.024169921875,1),(89,18.2084801960399,80.870361328125,1),(90,18.3545255291266,80.716552734375,1),(91,18.5212833254963,80.562744140625,1),(92,18.5837756883709,80.299072265625,1),(93,18.7503098131407,79.881591796875,1),(94,19.041348796589,79.881591796875,1),(95,19.3940678953966,79.903564453125,1),(96,19.5597901364974,79.903564453125,1),(97,19.4769502064884,79.398193359375,1),(98,19.5183754786016,79.288330078125,1),(99,19.5183754786016,79.090576171875,1),(100,19.6632802199877,78.892822265625,1),(101,19.7253422480579,78.739013671875,1),(102,19.766703551717,78.541259765625,1),(103,19.8080541280886,78.365478515625,1),(104,27.7807716433482,91.6314697265625,2),(105,27.6543381066919,91.5875244140625,2),(106,27.508271413876,91.6314697265625,2),(107,27.469287473692,91.7742919921875,2),(108,27.4400404650971,91.9281005859375,2),(109,27.4595393327179,92.0050048828125,2),(110,27.381523191705,92.0599365234375,2),(111,27.2936892248524,92.0819091796875,2),(112,27.2546295778001,92.0928955078125,2),(113,27.2643957764954,92.0599365234375,2),(114,27.1764691318989,92.0269775390625,2),(115,27.0004080035217,92.1038818359375,2),(116,26.8730809659384,92.1038818359375,2),(117,26.843677401113,92.2576904296875,2),(118,26.9220699167328,92.5433349609375,2),(119,26.9220699167328,92.6751708984375,2),(120,26.9122738266256,92.9608154296875,2),(121,26.8828804557234,93.3343505859375,2),(122,26.9220699167328,93.4881591796875,2),(123,27.0004080035217,93.7518310546875,2),(124,27.1080338014631,93.8616943359375,2),(125,27.2253258369034,93.9056396484375,2),(126,27.410785702577,94.0814208984375,2),(127,27.5569819203383,94.2242431640625,2),(128,27.5861978576927,94.4769287109375,2),(129,27.6835280837878,94.7076416015625,2),(130,27.7710511931723,94.9383544921875,2),(131,27.926474039865,95.2569580078125,2),(132,28.1204386871011,95.3668212890625,2),(133,28.256005619825,95.6195068359375,2),(134,28.2850332946407,95.8721923828125,2),(135,28.2366494440145,95.9490966796875,2),(136,28.2076085953274,96.1578369140625,2),(137,28.1979265572262,96.2567138671875,2),(138,28.130127737874,96.3995361328125,2),(139,28.0331978476764,96.5203857421875,2),(140,27.9458862217619,96.6961669921875,2),(141,27.8196447550994,96.9268798828125,2),(142,27.7418846325071,97.0587158203125,2),(143,27.8390760947778,97.1685791015625,2),(144,27.9167666412491,97.3663330078125,2),(145,27.9652949152111,97.3992919921875,2),(146,28.0525908233399,97.3663330078125,2),(147,28.1204386871011,97.2894287109375,2),(148,28.1882436418503,97.3663330078125,2),(149,28.2463279710488,97.2894287109375,2),(150,28.3430649048255,97.1575927734375,2),(151,28.3430649048255,97.0367431640625,2),(152,28.3430649048255,96.9708251953125,2),(153,28.4107283972379,96.9049072265625,2),(154,28.4880052041595,96.8719482421875,2),(155,28.5266224186481,96.7730712890625,2),(156,28.5652254906547,96.6851806640625,2),(157,28.6038144078413,96.5972900390625,2),(158,28.555576049186,96.4874267578125,2),(159,28.4107283972379,96.5423583984375,2),(160,28.5169694404011,96.4434814453125,2),(161,28.6134594240044,96.4874267578125,2),(162,28.700224692777,96.5643310546875,2),(163,28.7965462417692,96.6192626953125,2),(164,28.8735394631627,96.5203857421875,2),(165,28.9793120367225,96.4544677734375,2),(166,29.0657728884154,96.3665771484375,2),(167,29.0945770775118,96.3446044921875,2),(168,29.0465656227288,96.2347412109375,2),(169,29.0753751795583,96.2127685546875,2),(170,29.1617555153288,96.2786865234375,2),(171,29.2193020767795,96.2457275390625,2),(172,29.2959805587157,96.1688232421875,2),(173,29.3630270377838,96.1138916015625,2),(174,29.3630270377838,96.0369873046875,2),(175,29.353451668635,95.9381103515625,2),(176,29.353451668635,95.8172607421875,2),(177,29.1521612833189,95.2679443359375,2),(178,29.10417668395,95.2130126953125,2),(179,29.10417668395,95.0811767578125,2),(180,29.1521612833189,95.0372314453125,2),(181,29.1617555153288,94.8175048828125,2),(182,29.2384770859281,94.7515869140625,2),(183,29.2863988929348,94.6966552734375,2),(184,29.2480632437966,94.5318603515625,2),(185,29.1425661551071,94.4329833984375,2),(186,29.1137753951144,94.2901611328125,2),(187,29.0465656227288,94.3011474609375,2),(188,29.0081403629782,94.3560791015625,2),(189,28.9600886880068,94.2572021484375,2),(190,28.8831596093235,94.1363525390625,2),(191,28.7676591056913,93.9385986328125,2),(192,28.7291304834302,93.7847900390625,2),(193,28.6713109158808,93.5870361328125,2),(194,28.6616712164195,93.3892822265625,2),(195,28.5845217193704,93.3013916015625,2),(196,28.4203910856743,93.1695556640625,2),(197,28.3527337602378,93.0926513671875,2),(198,28.2463279710488,92.9718017578125,2),(199,28.2172897559571,92.8399658203125,2),(200,28.1495032115446,92.7410888671875,2),(201,28.130127737874,92.6861572265625,2),(202,28.0331978476764,92.7191162109375,2),(203,27.9167666412491,92.6641845703125,2),(204,27.8682165795141,92.5323486328125,2),(205,27.8196447550994,92.4444580078125,2),(206,27.8196447550994,92.3236083984375,2),(207,27.8390760947778,92.2247314453125,2),(208,27.8002099374183,92.0599365234375,2),(209,27.7418846325071,91.9171142578125,2),(210,27.7127102608875,91.8402099609375,2),(211,27.7418846325071,91.7633056640625,2),(212,27.7613298745052,91.6754150390625,2),(213,27.8002099374183,91.6534423828125,2),(214,25.5523536521655,89.8516845703125,3),(215,25.5820852787007,89.9615478515625,3),(216,25.6415263730658,89.9725341796875,3),(217,25.7603197547139,89.9066162109375,3),(218,25.9086444632913,90.0604248046875,3),(219,25.967922229034,90.3131103515625,3),(220,25.9975499195721,90.5218505859375,3),(221,25.8691093909993,90.6097412109375,3),(222,25.9284070326941,90.7415771484375,3),(223,25.9284070326941,90.9173583984375,3),(224,25.8493368917076,91.0711669921875,3),(225,25.8097819758404,91.1810302734375,3),(226,25.671235828577,91.2359619140625,3),(227,25.7998911820883,91.3238525390625,3),(228,25.8493368917076,91.5106201171875,3),(229,25.9382870749237,91.5106201171875,3),(230,26.0370418865158,91.5985107421875,3),(231,25.967922229034,91.6424560546875,3),(232,25.9284070326941,91.6754150390625,3),(233,25.9777989554644,91.7852783203125,3),(234,26.076520559857,91.8621826171875,3),(235,26.076520559857,92.1478271484375,3),(236,26.046912801684,92.2796630859375,3),(237,25.9580446733178,92.1588134765625,3),(238,25.8394494020632,92.1807861328125,3),(239,25.7504248359094,92.1478271484375,3),(240,25.7108369196406,92.1917724609375,3),(241,25.7405290927732,92.4005126953125,3),(242,25.7405290927732,92.4884033203125,3),(243,25.5721755566821,92.5653076171875,3),(244,25.5325284685344,92.6312255859375,3),(245,25.4333534278322,92.6312255859375,3),(246,25.3440260291343,92.7850341796875,3),(247,25.2049411535691,92.7850341796875,3),(248,25.1552293949406,92.6092529296875,3),(249,25.0557451170153,92.4444580078125,3),(250,24.9760994936954,92.4224853515625,3),(251,24.9362573230613,92.5433349609375,3),(252,24.8565343393107,92.5543212890625,3),(253,24.8665025269269,92.3895263671875,3),(254,24.9163314045991,92.2796630859375,3),(255,24.7168954558593,92.2686767578125,3),(256,24.5471231797308,92.2137451171875,3),(257,24.3871273246045,92.2576904296875,3),(258,24.2569813158825,92.2686767578125,3),(259,24.2569813158825,92.3895263671875,3),(260,24.1668020853032,92.4554443359375,3),(261,24.2169095377217,92.5433349609375,3),(262,24.3270765400186,92.6531982421875,3),(263,24.5071432831028,92.7740478515625,3),(264,24.3971330173911,92.8179931640625,3),(265,24.3771208396104,92.9937744140625,3),(266,24.7368534847707,93.1036376953125,3),(267,24.7867345419889,93.0816650390625,3),(268,24.8764699108315,93.2354736328125,3),(269,25.0159287633679,93.2354736328125,3),(270,25.0855988970648,93.3563232421875,3),(271,25.284437746983,93.4332275390625,3),(272,25.4234314263342,93.4661865234375,3),(273,25.5523536521655,93.3782958984375,3),(274,25.6415263730658,93.4991455078125,3),(275,25.7504248359094,93.5980224609375,3),(276,25.9086444632913,93.6749267578125,3),(277,25.9777989554644,93.8067626953125,3),(278,25.8394494020632,93.8067626953125,3),(279,25.9086444632913,93.9166259765625,3),(280,25.967922229034,93.9825439453125,3),(281,26.076520559857,93.9825439453125,3),(282,26.2441562838908,94.0484619140625,3),(283,26.3721854416956,94.2022705078125,3),(284,26.5099045314139,94.2681884765625,3),(285,26.5099045314139,94.3670654296875,3),(286,26.6081743740331,94.3890380859375,3),(287,26.7063598576335,94.5208740234375,3),(288,26.8044607665462,94.6856689453125,3),(289,26.9318651563889,94.9053955078125,3),(290,26.9808285904721,95.0482177734375,3),(291,27.0493416198703,95.2239990234375,3),(292,27.0982539061379,95.3558349609375,3),(293,27.1960143831733,95.4547119140625,3),(294,27.2546295778001,95.4986572265625,3),(295,27.2546295778001,95.5755615234375,3),(296,27.2350946077955,95.7183837890625,3),(297,27.2643957764954,95.9381103515625,3),(298,27.342494467201,96.0589599609375,3),(299,27.4302897388626,95.9600830078125,3),(300,27.4302897388626,95.8502197265625,3),(301,27.4985267227983,95.8502197265625,3),(302,27.5764600762627,95.8941650390625,3),(303,27.6446063819433,95.8172607421875,3),(304,27.7321607095809,95.7183837890625,3),(305,27.8099277809084,95.8062744140625,3),(306,27.8876392171365,95.9381103515625,3),(307,27.9652949152111,95.9930419921875,3),(308,27.9944014110461,95.8282470703125,3),(309,27.8876392171365,95.4656982421875,3),(310,27.8196447550994,95.2899169921875,3),(311,27.7904912248309,95.1031494140625,3),(312,27.7321607095809,94.7735595703125,3),(313,27.6348737913425,94.6636962890625,3),(314,27.5667214304097,94.4219970703125,3),(315,27.5472415462533,94.2681884765625,3),(316,27.4595393327179,94.1693115234375,3),(317,27.2839256002298,94.0484619140625,3),(318,27.1569204568809,93.8507080078125,3),(319,27.0199840079826,93.8177490234375,3),(320,26.9318651563889,93.3782958984375,3),(321,26.8632806267662,93.0596923828125,3),(322,26.9416595453815,92.6751708984375,3),(323,26.8632806267662,92.3675537109375,3),(324,26.85347943842,92.2137451171875,3),(325,26.85347943842,91.8072509765625,3),(326,26.7750393869996,91.6094970703125,3),(327,26.7750393869996,91.3677978515625,3),(328,26.7750393869996,91.2249755859375,3),(329,26.7750393869996,91.0272216796875,3),(330,26.7652305656975,90.6866455078125,3),(331,26.8044607665462,90.5108642578125,3),(332,26.8632806267662,90.4010009765625,3),(333,26.8338745150586,90.1702880859375,3),(334,26.7161737579341,90.0933837890625,3),(335,26.6769130831055,89.8956298828125,3),(336,26.4705730223751,89.8297119140625,3),(337,26.2638622801111,89.7528076171875,3),(338,26.2441562838908,89.6209716796875,3),(339,26.076520559857,89.8077392578125,3),(340,25.9382870749237,89.8626708984375,3),(341,25.6415263730658,89.8516845703125,3),(342,25.6217159598458,89.8516845703125,3),(343,25.5919941802547,89.8297119140625,3),(344,24.5171394505251,83.4906005859375,4),(345,24.5171394505251,83.7322998046875,4),(346,24.5271348225978,83.8531494140625,4),(347,24.6370313535095,84.0399169921875,4),(348,24.4971463205719,84.1058349609375,4),(349,24.5471231797308,84.3035888671875,4),(350,24.427145340082,84.3035888671875,4),(351,24.3270765400186,84.4354248046875,4),(352,24.2770124716641,84.5123291015625,4),(353,24.417142025372,84.5782470703125,4),(354,24.417142025372,84.6331787109375,4),(355,24.467150664739,84.7320556640625,4),(356,24.5371293990799,84.7979736328125,4),(357,24.4071379177277,84.8858642578125,4),(358,24.3270765400186,84.8858642578125,4),(359,24.3771208396104,84.9737548828125,4),(360,24.417142025372,85.0726318359375,4),(361,24.417142025372,85.1495361328125,4),(362,24.5071432831028,85.2154541015625,4),(363,24.5071432831028,85.4461669921875,4),(364,24.5471231797308,85.5120849609375,4),(365,24.5770997442894,85.6219482421875,4),(366,24.5970801370964,85.7098388671875,4),(367,24.7168954558593,85.6549072265625,4),(368,24.806681353852,85.7537841796875,4),(369,24.7967083489457,85.8416748046875,4),(370,24.7168954558593,85.8966064453125,4),(371,24.726874870507,86.0174560546875,4),(372,24.7368534847707,86.0943603515625,4),(373,24.627044746156,86.1053466796875,4),(374,24.5371293990799,86.1932373046875,4),(375,24.5371293990799,86.3140869140625,4),(376,24.3971330173911,86.3140869140625,4),(377,24.3971330173911,86.3800048828125,4),(378,24.3871273246045,86.4788818359375,4),(379,24.5171394505251,86.5118408203125,4),(380,24.5371293990799,86.6107177734375,4),(381,24.5471231797308,86.6766357421875,4),(382,24.5571161643096,86.7425537109375,4),(383,24.5870903392096,86.8853759765625,4),(384,24.5770997442894,86.9293212890625,4),(385,24.6370313535095,86.9403076171875,4),(386,24.6070691377097,87.0062255859375,4),(387,24.7069152410663,87.0831298828125,4),(388,24.8365955538912,87.0831298828125,4),(389,24.9163314045991,87.1710205078125,4),(390,25.0159287633679,87.1600341796875,4),(391,25.0756484456305,87.2479248046875,4),(392,25.0955485396043,87.3248291015625,4),(393,25.1552293949406,87.3358154296875,4),(394,25.2049411535691,87.4237060546875,4),(395,25.2049411535691,87.4896240234375,4),(396,25.2943711625882,87.4896240234375,4),(397,25.2943711625882,87.5994873046875,4),(398,25.2943711625882,87.7532958984375,4),(399,25.244695951306,87.7532958984375,4),(400,25.135339016131,87.7862548828125,4),(401,25.2148810711326,87.8961181640625,4),(402,25.3440260291343,87.8302001953125,4),(403,25.393660521998,87.7752685546875,4),(404,25.5226146476233,87.8631591796875,4),(405,25.5226146476233,87.9840087890625,4),(406,25.5424414701248,88.0938720703125,4),(407,25.6613334989527,88.0609130859375,4),(408,25.7504248359094,87.9400634765625,4),(409,25.819671943904,87.9071044921875,4),(410,25.898761936567,87.8302001953125,4),(411,25.967922229034,87.8302001953125,4),(412,26.0370418865158,87.8521728515625,4),(413,26.0962549069685,87.9290771484375,4),(414,26.1554379687135,88.0279541015625,4),(415,26.1948766757952,88.0938720703125,4),(416,26.2638622801111,88.1378173828125,4),(417,26.3721854416956,88.2586669921875,4),(418,26.4902404588696,88.2586669921875,4),(419,26.549222577692,88.2147216796875,4),(420,26.539394329017,88.1048583984375,4),(421,26.421389725295,88.0828857421875,4),(422,26.3623420689988,88.0279541015625,4),(423,26.3820279760254,87.9400634765625,4),(424,26.421389725295,87.6873779296875,4),(425,26.4017105287077,87.5885009765625,4),(426,26.4705730223751,87.4566650390625,4),(427,26.352497858154,87.3468017578125,4),(428,26.4017105287077,87.2369384765625,4),(429,26.4509022236726,87.0941162109375,4),(430,26.5590499840755,87.0721435546875,4),(431,26.5590499840755,86.9512939453125,4),(432,26.4509022236726,86.8634033203125,4),(433,26.4312280645064,86.7205810546875,4),(434,26.5099045314139,86.5008544921875,4),(435,26.6179967221168,86.2042236328125,4),(436,26.6179967221168,85.9295654296875,4),(437,26.5885271473086,85.8526611328125,4),(438,26.627818226393,85.7318115234375,4),(439,26.8240707804702,85.7318115234375,4),(440,26.8632806267662,85.5889892578125,4),(441,26.7554208973591,85.3582763671875,4),(442,26.7554208973591,85.2593994140625,4),(443,26.843677401113,85.1715087890625,4),(444,26.8926790959081,85.1275634765625,4),(445,26.8632806267662,85.0506591796875,4),(446,27.0101964319315,84.8858642578125,4),(447,27.0101964319315,84.6551513671875,4),(448,27.2253258369034,84.6551513671875,4),(449,27.3327351368591,84.6002197265625,4),(450,27.342494467201,84.4464111328125,4),(451,27.3912782225793,84.3475341796875,4),(452,27.4205381512871,84.2266845703125,4),(453,27.488781168938,84.1497802734375,4),(454,27.4790347525007,84.0289306640625,4),(455,27.410785702577,83.9190673828125,4),(456,27.3912782225793,83.8531494140625,4),(457,27.2448625214973,83.9739990234375,4),(458,27.1373683597956,83.9959716796875,4),(459,26.9220699167328,84.0838623046875,4),(460,26.8730809659384,84.1717529296875,4),(461,26.85347943842,84.2706298828125,4),(462,26.745610382199,84.2706298828125,4),(463,26.6965451115852,84.3804931640625,4),(464,26.6081743740331,84.4354248046875,4),(465,26.6081743740331,84.2926025390625,4),(466,26.6769130831055,84.1168212890625,4),(467,26.6179967221168,84.1058349609375,4),(468,26.5688765479507,84.0618896484375,4),(469,26.5295652382676,84.0069580078125,4),(470,26.5295652382676,83.9410400390625,4),(471,26.4607380431909,83.9410400390625,4),(472,26.4312280645064,83.9959716796875,4),(473,26.421389725295,84.0728759765625,4),(474,26.352497858154,84.1717529296875,4),(475,26.2343020324067,84.1168212890625,4),(476,26.1258501856804,84.0618896484375,4),(477,25.9975499195721,84.2156982421875,4),(478,25.898761936567,84.3585205078125,4),(479,25.8097819758404,84.5123291015625,4),(480,25.8097819758404,84.6221923828125,4),(481,25.7306325255319,84.6661376953125,4),(482,25.6118095210555,84.6112060546875,4),(483,25.7207351344121,84.4244384765625,4),(484,25.7899995628736,84.3914794921875,4),(485,25.7306325255319,84.3475341796875,4),(486,25.6514303470397,84.3255615234375,4),(487,25.6118095210555,84.3035888671875,4),(488,25.7405290927732,84.1497802734375,4),(489,25.7108369196406,84.1058349609375,4),(490,25.6316215772585,84.0618896484375,4),(491,25.5325284685344,83.9520263671875,4),(492,25.5127000076205,83.8861083984375,4),(493,25.4234314263342,83.8311767578125,4),(494,25.4035849731867,83.6993408203125,4),(495,25.2943711625882,83.5015869140625,4),(496,25.1651733686639,83.3477783203125,4),(497,24.966140159913,83.3697509765625,4),(498,24.8365955538912,83.4027099609375,4),(499,24.726874870507,83.4356689453125,4),(500,24.6769697982027,83.5125732421875,4),(501,24.5770997442894,83.5015869140625,4),(502,24.5571161643096,83.4796142578125,4),(503,24.0263966660173,83.287353515625,5),(504,23.9862525998418,83.155517578125,5),(505,23.865745352648,83.067626953125,5),(506,23.9460960149984,82.847900390625,5),(507,23.885837699862,82.672119140625,5),(508,23.865745352648,82.408447265625,5),(509,23.7451258657629,82.078857421875,5),(510,23.885837699862,81.727294921875,5),(511,23.885837699862,81.573486328125,5),(512,23.7048945023249,81.661376953125,5),(513,23.5639871284512,81.551513671875,5),(514,23.4632463315504,81.815185546875,5),(515,23.3019011241889,82.144775390625,5),(516,23.1201536216956,82.144775390625,5),(517,22.8774404648971,81.815185546875,5),(518,22.7356568522065,81.639404296875,5),(519,22.4719545077392,81.419677734375,5),(520,22.4719545077392,81.112060546875,5),(521,22.2077491784108,80.914306640625,5),(522,21.6982654968525,80.760498046875,5),(523,21.248422235627,80.672607421875,5),(524,21.2074587304826,80.518798828125,5),(525,20.9819567428323,80.474853515625,5),(526,20.7150151455121,80.540771484375,5),(527,20.5299331251708,80.628662109375,5),(528,20.2415828195422,80.628662109375,5),(529,20.2415828195422,80.364990234375,5),(530,20.0146454453414,80.584716796875,5),(531,19.7253422480579,80.474853515625,5),(532,19.5183754786016,80.782470703125,5),(533,19.2696652965023,80.870361328125,5),(534,19.3318784408188,80.606689453125,5),(535,19.2696652965023,80.408935546875,5),(536,18.9582464859814,80.255126953125,5),(537,18.542116654449,80.233154296875,5),(538,18.4170786586613,80.716552734375,5),(539,18.1249706393865,80.980224609375,5),(540,17.7068281240195,81.112060546875,5),(541,17.9369286375494,81.463623046875,5),(542,18.3545255291266,81.639404296875,5),(543,18.6254245407013,82.012939453125,5),(544,18.9790259532553,82.232666015625,5),(545,19.456233596018,82.210693359375,5),(546,19.7460242396254,81.968994140625,5),(547,19.9939984694855,81.837158203125,5),(548,20.1178396304916,82.012939453125,5),(549,19.9320413061155,82.254638671875,5),(550,19.7253422480579,82.562255859375,5),(551,19.9733487861106,82.716064453125,5),(552,20.0352897113524,82.452392578125,5),(553,20.4887732871098,82.430419921875,5),(554,20.8998713470764,82.342529296875,5),(555,21.0845000835174,82.738037109375,5),(556,21.1869727141238,83.067626953125,5),(557,21.3917047310366,83.375244140625,5),(558,21.9634249368442,83.551025390625,5),(559,22.289096418723,83.880615234375,5),(560,22.4516488191262,84.034423828125,5),(561,22.5937260639293,84.100341796875,5),(562,22.7761815050865,84.320068359375,5),(563,22.9988515941429,84.385986328125,5),(564,22.9988515941429,84.188232421875,5),(565,23.2413461023861,84.056396484375,5),(566,23.4027649054079,83.902587890625,5),(567,23.6646507316316,84.034423828125,5),(568,23.6445241985737,83.792724609375,5),(569,23.7652368897587,83.638916015625,5),(570,23.9460960149984,83.485107421875,5),(571,24.1267019586817,83.419189453125,5),(572,24.0464639996666,83.331298828125,5),(573,28.851890877684,77.2077941894531,6),(574,28.8639184262246,77.1830749511719,6),(575,28.859107573773,77.1446228027344,6),(576,28.868729056029,77.1034240722656,6),(577,28.880754656304,77.0787048339844,6),(578,28.8663237689591,77.0512390136719,6),(579,28.839861937968,77.0347595214844,6),(580,28.8326439065278,76.9853210449219,6),(581,28.8254253744772,76.9496154785156,6),(582,28.7917322747408,76.9413757324219,6),(583,28.7508045823501,76.9386291503906,6),(584,28.7267219726982,76.9468688964844,6),(585,28.6929969970619,76.9496154785156,6),(586,28.6568510342034,76.9166564941406,6),(587,28.6303360711089,76.9221496582031,6),(588,28.6303360711089,76.8891906738281,6),(589,28.5965800646348,76.8507385253906,6),(590,28.5531635506107,76.8452453613281,6),(591,28.5290355251072,76.8699645996094,6),(592,28.5049019748946,76.8836975097656,6),(593,28.5097291267691,76.9166564941406,6),(594,28.5073155784418,76.9551086425781,6),(595,28.5435130035673,77.0018005371094,6),(596,28.5169694404011,77.0429992675781,6),(597,28.5024883161304,77.0979309082031,6),(598,28.4735201051409,77.0951843261719,6),(599,28.4300528923357,77.1418762207031,6),(600,28.4107283972379,77.1528625488281,6),(601,28.4107283972379,77.1940612792969,6),(602,28.4397138170279,77.2544860839844,6),(603,28.459033019728,77.2297668457031,6),(604,28.4880052041595,77.2517395019531,6),(605,28.5049019748946,77.2901916503906,6),(606,28.5024883161304,77.3231506347656,6),(607,28.5145560577517,77.3478698730469,6),(608,28.557988492481,77.3121643066406,6),(609,28.5821098843565,77.2984313964844,6),(610,28.6014030154422,77.3286437988281,6),(611,28.6231035545299,77.3286437988281,6),(612,28.6399786513069,77.3149108886719,6),(613,28.6833592931406,77.3149108886719,6),(614,28.7170873748722,77.3286437988281,6),(615,28.7170873748722,77.3039245605469,6),(616,28.7098608439429,77.2901916503906,6),(617,28.7291304834302,77.2764587402344,6),(618,28.7411722045935,77.2544860839844,6),(619,28.7676591056913,77.2380065917969,6),(620,28.7845109074078,77.2160339355469,6),(621,28.8013599864818,77.1995544433594,6),(622,28.8278316074459,77.2242736816406,6),(623,28.847079468718,77.2215270996094,6),(624,28.8542964986979,77.2187805175781,6),(625,14.8386115533848,74.0972900390625,7),(626,14.9660132515672,73.9984130859375,7),(627,15.0615148910722,73.9434814453125,7),(628,15.0615148910722,73.8885498046875,7),(629,15.1357643545958,73.9324951171875,7),(630,15.2311897047672,73.9215087890625,7),(631,15.3265718014208,73.7896728515625,7),(632,15.411319377981,73.7457275390625,7),(633,15.4325008818861,73.8006591796875,7),(634,15.5277908629938,73.7457275390625,7),(635,15.7182385447349,73.6468505859375,7),(636,15.7816816476394,73.8665771484375,7),(637,15.5912930806332,74.0093994140625,7),(638,15.6441966008661,74.0753173828125,7),(639,15.6441966008661,74.2730712890625,7),(640,15.4854451794786,74.2620849609375,7),(641,15.3795430752645,74.3170166015625,7),(642,15.3053795304367,74.3170166015625,7),(643,15.2523894728256,74.2730712890625,7),(644,15.1145528719441,74.3280029296875,7),(645,14.9872395257743,74.2291259765625,7),(646,14.8067493721338,74.1632080078125,7),(647,14.7748825065163,74.1192626953125,7),(648,14.8173706201553,74.1082763671875,7),(649,24.2870268653764,68.7908935546875,8),(650,23.9862525998418,68.7359619140625,8),(651,23.9561363339693,68.5711669921875,8),(652,23.9561363339693,68.2745361328125,8),(653,23.865745352648,68.1756591796875,8),(654,23.6344597709946,68.1756591796875,8),(655,23.5639871284512,68.2305908203125,8),(656,23.5740569666427,68.3843994140625,8),(657,23.4330090774204,68.4063720703125,8),(658,23.2918105324419,68.4722900390625,8),(659,23.2312509238978,68.5931396484375,8),(660,22.9482768568809,68.9007568359375,8),(661,22.8571947009696,69.1204833984375,8),(662,22.7964393209195,69.3841552734375,8),(663,22.7660514691269,69.6807861328125,8),(664,22.8369459209439,69.9005126953125,8),(665,22.8875622151745,70.0653076171875,8),(666,22.9786239703849,70.2191162109375,8),(667,22.8976832106481,70.3289794921875,8),(668,22.7660514691269,70.2740478515625,8),(669,22.654571520099,70.1422119140625,8),(670,22.5835825377339,70.1641845703125,8),(671,22.5734382645724,70.0103759765625,8),(672,22.5734382645724,69.9005126953125,8),(673,22.5024074594977,69.7686767578125,8),(674,22.4313401563606,69.7686767578125,8),(675,22.4211847103319,69.6478271484375,8),(676,22.4211847103319,69.4720458984375,8),(677,22.3195894428339,69.4061279296875,8),(678,22.4516488191262,69.4281005859375,8),(679,22.5328537075271,69.3841552734375,8),(680,22.5328537075271,69.2962646484375,8),(681,22.4719545077392,69.1973876953125,8),(682,22.4313401563606,69.0545654296875,8),(683,22.4211847103319,68.9776611328125,8),(684,22.289096418723,68.9776611328125,8),(685,22.1263547599197,69.0545654296875,8),(686,21.9124709526803,69.2633056640625,8),(687,21.7288858739515,69.4610595703125,8),(688,21.5041855007784,69.7137451171875,8),(689,21.1972160773871,70.0213623046875,8),(690,20.9409196703946,70.2850341796875,8),(691,20.7355659052186,70.6146240234375,8),(692,20.6533461480761,70.8013916015625,8),(693,20.6739052646728,71.0540771484375,8),(694,20.7766590518788,71.1968994140625,8),(695,20.8280097629647,71.4056396484375,8),(696,20.9101344816927,71.6143798828125,8),(697,21.0024710543567,71.7242431640625,8),(698,21.1152493099638,71.9110107421875,8),(699,21.2177006731323,72.0648193359375,8),(700,21.4428431071877,72.2406005859375,8),(701,21.6165793367406,72.3065185546875,8),(702,21.8614987343726,72.3065185546875,8),(703,21.8716946351427,72.4053955078125,8),(704,22.0143606531032,72.4053955078125,8),(705,22.0347298170442,72.5042724609375,8),(706,21.8614987343726,72.4932861328125,8),(707,21.6063653172034,72.5372314453125,8),(708,21.5246272205453,72.5811767578125,8),(709,21.3303150734318,72.5811767578125,8),(710,21.1357452550306,72.6361083984375,8),(711,20.9819567428323,72.7020263671875,8),(712,20.8588117908677,72.8009033203125,8),(713,20.5710818935082,72.8668212890625,8),(714,20.437307950569,72.8118896484375,8),(715,20.3240236034225,72.9217529296875,8),(716,20.3240236034225,73.1414794921875,8),(717,20.086888505561,73.1524658203125,8),(718,20.1694112276103,73.2952880859375,8),(719,20.2725032501349,73.4381103515625,8),(720,20.3858253818743,73.3502197265625,8),(721,20.5916521208292,73.4710693359375,8),(722,20.6533461480761,73.4600830078125,8),(723,20.6225022593448,73.6138916015625,8),(724,20.5710818935082,73.8006591796875,8),(725,20.6533461480761,73.8006591796875,8),(726,20.7458402389023,73.9654541015625,8),(727,20.9101344816927,73.8775634765625,8),(728,21.1254976366063,73.7127685546875,8),(729,21.2279419050582,73.8006591796875,8),(730,21.3405484690812,73.9434814453125,8),(731,21.4735175333498,74.3389892578125,8),(732,21.5348470020488,74.2950439453125,8),(733,21.5348470020488,74.0423583984375,8),(734,21.5348470020488,73.8446044921875,8),(735,21.6063653172034,73.8116455078125,8),(736,21.6982654968525,73.9215087890625,8),(737,21.8003080509726,73.8446044921875,8),(738,21.8716946351427,73.9984130859375,8),(739,21.9226632093259,74.1412353515625,8),(740,22.004174972902,74.1302490234375,8),(741,22.0856399016503,74.1632080078125,8),(742,22.1467077800126,74.1082763671875,8),(743,22.217920166311,74.1082763671875,8),(744,22.268764039074,74.0533447265625,8),(745,22.3195894428339,74.0643310546875,8),(746,22.3195894428339,74.1741943359375,8),(747,22.3297523043765,74.2620849609375,8),(748,22.3907139168385,74.2620849609375,8),(749,22.4110285215587,74.1412353515625,8),(750,22.4516488191262,74.0863037109375,8),(751,22.5227057034825,74.0753173828125,8),(752,22.5227057034825,74.1632080078125,8),(753,22.6342926937935,74.3280029296875,8),(754,22.5937260639293,74.4049072265625,8),(755,22.7964393209195,74.4488525390625,8),(756,22.9482768568809,74.3829345703125,8),(757,23.0797317624499,74.2840576171875,8),(758,23.1504620292241,74.2401123046875,8),(759,23.1504620292241,74.1302490234375,8),(760,23.251440517056,74.1302490234375,8),(761,23.3019011241889,74.0423583984375,8),(762,23.3321683063115,73.8885498046875,8),(763,23.4229284550653,73.8226318359375,8),(764,23.4229284550653,73.6688232421875,8),(765,23.5740569666427,73.6688232421875,8),(766,23.6143285949917,73.6138916015625,8),(767,23.6143285949917,73.5260009765625,8),(768,23.6847741668838,73.5260009765625,8),(769,23.7350691889594,73.4161376953125,8),(770,23.8255513068848,73.3502197265625,8),(771,23.9561363339693,73.4051513671875,8),(772,24.1467535947031,73.3282470703125,8),(773,24.1567782333034,73.1304931640625,8),(774,24.2369470039175,73.1195068359375,8),(775,24.3771208396104,73.1744384765625,8),(776,24.417142025372,73.0645751953125,8),(777,24.4971463205719,73.0645751953125,8),(778,24.427145340082,73.0096435546875,8),(779,24.3671135626513,72.9437255859375,8),(780,24.3671135626513,72.7679443359375,8),(781,24.4371478616156,72.5921630859375,8),(782,24.4371478616156,72.4713134765625,8),(783,24.4771500111487,72.3614501953125,8),(784,24.5571161643096,72.3175048828125,8),(785,24.5870903392096,72.2296142578125,8),(786,24.6669863852163,72.0538330078125,8),(787,24.6669863852163,71.9000244140625,8),(788,24.6570021732791,71.7681884765625,8),(789,24.627044746156,71.5155029296875,8),(790,24.627044746156,71.3067626953125,8),(791,24.627044746156,71.1090087890625,8),(792,24.6370313535095,71.0650634765625,8),(793,24.5371293990799,70.9881591796875,8),(794,24.4371478616156,71.1199951171875,8),(795,24.3971330173911,71.1309814453125,8),(796,24.3470966338085,70.9661865234375,8),(797,24.1968689192497,70.8013916015625,8),(798,24.2269286649764,70.6585693359375,8),(799,24.2970404693116,70.5816650390625,8),(800,24.3871273246045,70.5706787109375,8),(801,24.3871273246045,70.4937744140625,8),(802,24.3370869824105,70.2630615234375,8),(803,24.2469645543009,70.0762939453125,8),(804,24.1567782333034,69.9774169921875,8),(805,24.1467535947031,69.7576904296875,8),(806,24.2469645543009,69.6258544921875,8),(807,24.2669972884182,69.4830322265625,8),(808,24.2669972884182,69.2962646484375,8),(809,24.2469645543009,69.1204833984375,8),(810,24.206889622398,68.9996337890625,8),(811,24.2669972884182,68.9337158203125,8),(812,24.2269286649764,68.8677978515625,8),(813,24.3070532832259,68.8128662109375,8),(814,29.8501731256899,76.1956787109375,9),(815,29.7453016622136,75.4595947265625,9),(816,29.7071393481341,75.3826904296875,9),(817,29.5352295629485,75.2618408203125,9),(818,29.5543451257483,75.2178955078125,9),(819,29.6403203953514,75.1300048828125,9),(820,29.7453016622136,75.2069091796875,9),(821,29.821582720575,75.1739501953125,9),(822,29.8025179057645,75.0860595703125,9),(823,29.8692288489683,75.0750732421875,9),(824,29.8692288489683,74.9322509765625,9),(825,29.9930022845511,74.8333740234375,9),(826,29.9930022845511,74.7235107421875,9),(827,29.8597014421268,74.6026611328125,9),(828,29.7357624444491,74.4927978515625,9),(829,29.5543451257483,74.5806884765625,9),(830,29.3917477429928,74.5916748046875,9),(831,29.324720161511,74.7125244140625,9),(832,29.3821750751453,74.8333740234375,9),(833,29.2863988929348,74.9981689453125,9),(834,29.2384770859281,75.1080322265625,9),(835,29.2384770859281,75.1959228515625,9),(836,29.2768163283686,75.3277587890625,9),(837,29.1425661551071,75.4046630859375,9),(838,29.0273547804184,75.3936767578125,9),(839,28.9985318140518,75.4815673828125,9),(840,28.7869180854202,75.5145263671875,9),(841,28.574874047447,75.5584716796875,9),(842,28.4976608329635,75.7012939453125,9),(843,28.3333951691965,75.8551025390625,9),(844,28.2947074284212,76.0198974609375,9),(845,28.1688751800633,76.0418701171875,9),(846,28.1010579586694,75.9759521484375,9),(847,27.9361805667694,75.9429931640625,9),(848,27.8293608597898,75.9979248046875,9),(849,27.8293608597898,76.1407470703125,9),(850,27.8585039548412,76.1956787109375,9),(851,27.9361805667694,76.1627197265625,9),(852,27.9847001186127,76.1297607421875,9),(853,28.0428947725616,76.1846923828125,9),(854,28.0428947725616,76.2396240234375,9),(855,28.0428947725616,76.3165283203125,9),(856,28.1688751800633,76.3385009765625,9),(857,28.1398159127545,76.4593505859375,9),(858,28.0138013763807,76.4593505859375,9),(859,27.9555910046426,76.5032958984375,9),(860,27.9944014110461,76.6351318359375,9),(861,28.0719803017799,76.6351318359375,9),(862,28.1204386871011,76.7669677734375,9),(863,28.2172897559571,76.8548583984375,9),(864,28.1398159127545,76.9207763671875,9),(865,27.9847001186127,76.9537353515625,9),(866,27.8196447550994,76.8988037109375,9),(867,27.6640689653845,76.9537353515625,9),(868,27.7321607095809,77.0306396484375,9),(869,27.7516076875494,77.2393798828125,9),(870,27.8585039548412,77.4151611328125,9),(871,27.9361805667694,77.5469970703125,9),(872,28.1107487606335,77.5030517578125,9),(873,28.1882436418503,77.5030517578125,9),(874,28.256005619825,77.5360107421875,9),(875,28.323724553546,77.5140380859375,9),(876,28.3914003758178,77.4700927734375,9),(877,28.4203910856743,77.4041748046875,9),(878,28.4493738595567,77.3272705078125,9),(879,28.4397138170279,77.2174072265625,9),(880,28.555576049186,77.2943115234375,9),(881,28.6905876542507,77.3052978515625,9),(882,28.7676591056913,77.2393798828125,9),(883,29.0465656227288,77.1734619140625,9),(884,29.2288900301942,77.0965576171875,9),(885,29.3821750751453,77.1844482421875,9),(886,29.5352295629485,77.1075439453125,9),(887,29.8311137647371,77.1954345703125,9),(888,30.0881077533673,77.3382568359375,9),(889,30.1926182184993,77.4920654296875,9),(890,30.372875188118,77.5469970703125,9),(891,30.4107817908459,77.3602294921875,9),(892,30.4676141022579,77.2503662109375,9),(893,30.5338765729976,77.1405029296875,9),(894,30.581179257387,77.1405029296875,9),(895,30.7040582309195,77.1075439453125,9),(896,30.7795983966115,76.9866943359375,9),(897,30.8739402378876,76.8768310546875,9),(898,30.8739402378876,76.7889404296875,9),(899,30.8079106813665,76.7889404296875,9),(900,30.7512777762578,76.7010498046875,9),(901,30.5906370268929,76.9427490234375,9),(902,30.4676141022579,76.9317626953125,9),(903,30.4013065192036,76.8988037109375,9),(904,30.4486736792876,76.7449951171875,9),(905,30.3065032598488,76.7340087890625,9),(906,30.2780443778001,76.6461181640625,9),(907,30.1166215828194,76.6131591796875,9),(908,30.0310554265402,76.5911865234375,9),(909,30.0976132772171,76.4483642578125,9),(910,30.1071178870924,76.3494873046875,9),(911,30.0881077533673,76.2506103515625,9),(912,29.9930022845511,76.2506103515625,9),(913,29.8978056101559,76.1846923828125,9),(914,29.8406438998344,76.2176513671875,9),(915,32.2685554462148,75.6353759765625,10),(916,32.184911050518,75.6353759765625,10),(917,32.0825745595459,75.7452392578125,10),(918,31.9335167619037,75.9320068359375,10),(919,31.8588970444545,75.9429931640625,10),(920,31.7842168844874,75.9429931640625,10),(921,31.6346755495414,75.9759521484375,10),(922,31.503629305773,76.0968017578125,10),(923,31.3442544556681,76.1956787109375,10),(924,31.2973279914043,76.2506103515625,10),(925,31.4005353268639,76.2945556640625,10),(926,31.381778782111,76.4154052734375,10),(927,31.2597699873943,76.5142822265625,10),(928,31.2034049509174,76.6571044921875,10),(929,31.0623454098044,76.6351318359375,10),(930,30.8833693216923,76.7889404296875,10),(931,30.8456474201826,76.9427490234375,10),(932,30.7512777762578,76.9866943359375,10),(933,30.7040582309195,77.0965576171875,10),(934,30.6379120283411,77.1734619140625,10),(935,30.5149490451777,77.1075439453125,10),(936,30.4392020872356,77.3602294921875,10),(937,30.3633962396037,77.5360107421875,10),(938,30.4202561428452,77.6678466796875,10),(939,30.5433389542302,77.7886962890625,10),(940,30.6473642582432,77.7447509765625,10),(941,30.7323927340061,77.7227783203125,10),(942,30.8739402378876,77.7227783203125,10),(943,30.9964458974264,77.7667236328125,10),(944,31.1376032700213,77.8985595703125,10),(945,31.2034049509174,78.0743408203125,10),(946,31.2503781498557,78.2061767578125,10),(947,31.2034049509174,78.5467529296875,10),(948,31.2128014583388,78.6566162109375,10),(949,31.3161013834956,78.7994384765625,10),(950,31.4567824721143,78.7884521484375,10),(951,31.5785354264734,78.7225341796875,10),(952,31.6253212132992,78.7335205078125,10),(953,31.6253212132992,78.8543701171875,10),(954,31.8122290226407,78.7115478515625,10),(955,31.9335167619037,78.8433837890625,10),(956,32.2128010680152,78.8873291015625,10),(957,32.2871326326164,78.9202880859375,10),(958,32.389239109859,78.9202880859375,10),(959,32.6393748736067,78.7774658203125,10),(960,32.7225986040441,78.7115478515625,10),(961,32.6208701831811,78.5467529296875,10),(962,32.4541559394147,78.4368896484375,10),(963,32.5931059742653,78.3050537109375,10),(964,32.7225986040441,78.4039306640625,10),(965,32.7595620256501,78.3160400390625,10),(966,32.6301230067074,78.1182861328125,10),(967,32.6301230067074,77.9864501953125,10),(968,32.7318408968657,77.9095458984375,10),(969,32.8149783969858,77.8546142578125,10),(970,32.9164853473144,77.7777099609375,10),(971,32.9902355596511,77.7117919921875,10),(972,32.8611323228109,77.5140380859375,10),(973,32.8703602280835,77.4041748046875,10),(974,32.9625864419175,77.3492431640625,10),(975,33.0639241981206,77.2064208984375,10),(976,33.1375511923461,77.0306396484375,10),(977,33.2294981414495,76.9097900390625,10),(978,33.2754354129816,76.8328857421875,10),(979,33.2754354129816,76.6790771484375,10),(980,33.2754354129816,76.5802001953125,10),(981,33.2111164724168,76.4373779296875,10),(982,33.0362981788596,76.1846923828125,10),(983,32.9257074887604,76.0528564453125,10),(984,32.907262244883,75.9649658203125,10),(985,32.907262244883,75.8880615234375,10),(986,32.907262244883,75.8111572265625,10),(987,32.8057447329069,75.8770751953125,10),(988,32.7041111444074,75.9539794921875,10),(989,32.5468131735151,75.8990478515625,10),(990,32.5004964892448,75.7891845703125,10),(991,32.398515802474,75.7342529296875,10),(992,32.3242755888766,75.8331298828125,10),(993,32.2778445149827,75.7012939453125,10),(994,32.2592654264593,75.6573486328125,10),(995,35.5501053358855,78.057861328125,11),(996,35.4427709258577,77.618408203125,11),(997,35.5143431343182,77.332763671875,11),(998,35.6572962480963,77.420654296875,11),(999,35.7108378353001,77.156982421875,11),(1000,35.8356283888737,76.805419921875,11),(1001,36.0313317763319,76.805419921875,11),(1002,36.2088230928371,76.563720703125,11),(1003,36.4212824436495,76.212158203125,11),(1004,36.7916906190708,75.596923828125,11),(1005,36.7564903295051,75.443115234375,11),(1006,36.9323300615031,75.311279296875,11),(1007,36.985003092856,75.179443359375,11),(1008,37.0376396797714,74.893798828125,11),(1009,37.0376396797714,74.652099609375,11),(1010,37.0376396797714,74.410400390625,11),(1011,36.3505270054276,72.740478515625,11),(1012,36.1023764487364,72.542724609375,11),(1013,35.8534396195918,72.542724609375,11),(1014,35.7999939298853,73.048095703125,11),(1015,35.6037187406973,73.333740234375,11),(1016,35.5679804580121,73.685302734375,11),(1017,35.406960932702,73.773193359375,11),(1018,35.2815006578912,73.773193359375,11),(1019,35.1738083179996,74.036865234375,11),(1020,34.9760015131759,74.146728515625,11),(1021,34.8138033171132,73.992919921875,11),(1022,34.7235549270422,73.553466796875,11),(1023,34.2889918650375,73.487548828125,11),(1024,34.0708623237663,73.575439453125,11),(1025,33.7060626551012,73.575439453125,11),(1026,33.4497765831184,73.641357421875,11),(1027,33.0639241981206,73.751220703125,11),(1028,32.9164853473144,73.948974609375,11),(1029,32.7318408968657,74.432373046875,11),(1030,32.7133553531776,74.739990234375,11),(1031,32.5097617359194,74.937744140625,11),(1032,32.3242755888766,75.377197265625,11),(1033,32.2871326326164,75.443115234375,11),(1034,32.4170663284628,75.574951171875,11),(1035,32.5468131735151,75.728759765625,11),(1036,32.6393748736067,75.860595703125,11),(1037,32.8611323228109,75.882568359375,11),(1038,33.0086634945756,75.882568359375,11),(1039,33.0270875800287,76.146240234375,11),(1040,33.0823367285638,76.256103515625,11),(1041,33.2478759479244,76.431884765625,11),(1042,33.0639241981206,76.871337890625,11),(1043,32.9718037763576,77.113037109375,11),(1044,32.8795871730663,77.398681640625,11),(1045,32.8611323228109,77.640380859375,11),(1046,32.9902355596511,77.772216796875,11),(1047,32.7503226078097,77.969970703125,11),(1048,32.5838493256566,78.079833984375,11),(1049,32.7688004848817,78.431396484375,11),(1050,32.4356130411628,78.145751953125,11),(1051,32.398515802474,78.453369140625,11),(1052,32.5282893648253,78.563232421875,11),(1053,32.565333160841,78.760986328125,11),(1054,32.4170663284628,78.914794921875,11),(1055,32.4726950220615,79.024658203125,11),(1056,32.4912302879476,79.332275390625,11),(1057,32.6393748736067,79.442138671875,11),(1058,32.8795871730663,79.464111328125,11),(1059,33.0270875800287,79.398193359375,11),(1060,33.1191502267689,79.288330078125,11),(1061,33.2294981414495,79.090576171875,11),(1062,33.3764123512468,78.936767578125,11),(1063,33.6146192923338,79.024658203125,11),(1064,33.8339199536547,79.002685546875,11),(1065,33.925129700072,78.936767578125,11),(1066,33.9980272623488,78.936767578125,11),(1067,33.9980272623488,79.178466796875,11),(1068,34.0344526096764,79.486083984375,11),(1069,34.1618181612304,79.486083984375,11),(1070,34.4340978935947,79.683837890625,11),(1071,34.5246614717717,79.793701171875,11),(1072,34.6693585452454,80.079345703125,11),(1073,34.8498750319542,80.167236328125,11),(1074,35.0839555792764,80.167236328125,11),(1075,35.406960932702,80.299072265625,11),(1076,35.5322262277034,80.299072265625,11),(1077,35.5322262277034,80.035400390625,11),(1078,35.5679804580121,79.947509765625,11),(1079,35.6215818995597,79.771728515625,11),(1080,35.7465122599185,79.639892578125,11),(1081,35.8534396195918,79.464111328125,11),(1082,35.9424357525543,79.354248046875,11),(1083,35.9424357525543,79.200439453125,11),(1084,35.9424357525543,79.068603515625,11),(1085,35.9068493067712,78.804931640625,11),(1086,35.7999939298853,78.673095703125,11),(1087,35.6929946320988,78.497314453125,11),(1088,35.6394410689739,78.299560546875,11),(1089,35.5679804580121,78.189697265625,11),(1090,35.5322262277034,78.167724609375,11),(1091,24.5171394505251,83.5125732421875,12),(1092,24.5171394505251,83.7652587890625,12),(1093,24.567108352576,83.9190673828125,12),(1094,24.6370313535095,84.0179443359375,12),(1095,24.4871485631734,84.1168212890625,12),(1096,24.567108352576,84.3255615234375,12),(1097,24.4371478616156,84.2926025390625,12),(1098,24.3370869824105,84.4573974609375,12),(1099,24.2870268653764,84.5343017578125,12),(1100,24.417142025372,84.6112060546875,12),(1101,24.5271348225978,84.7979736328125,12),(1102,24.427145340082,84.8748779296875,12),(1103,24.3871273246045,85.0616455078125,12),(1104,24.4071379177277,85.1495361328125,12),(1105,24.5171394505251,85.3143310546875,12),(1106,24.5471231797308,85.5010986328125,12),(1107,24.6170573408095,85.6658935546875,12),(1108,24.8266249565622,85.7537841796875,12),(1109,24.7967083489457,85.8856201171875,12),(1110,24.726874870507,86.0394287109375,12),(1111,24.7069152410663,86.1602783203125,12),(1112,24.6070691377097,86.1602783203125,12),(1113,24.5970801370964,86.2701416015625,12),(1114,24.4571505241859,86.3250732421875,12),(1115,24.3971330173911,86.4239501953125,12),(1116,24.4771500111487,86.5118408203125,12),(1117,24.5870903392096,86.6217041015625,12),(1118,24.5870903392096,86.7425537109375,12),(1119,24.5571161643096,86.8634033203125,12),(1120,24.627044746156,86.9622802734375,12),(1121,24.627044746156,87.0831298828125,12),(1122,24.9262947663956,87.1600341796875,12),(1123,25.0756484456305,87.1600341796875,12),(1124,25.0955485396043,87.2918701171875,12),(1125,25.2546326197495,87.3358154296875,12),(1126,25.1950004243075,87.4676513671875,12),(1127,25.3340966847945,87.5445556640625,12),(1128,25.2943711625882,87.6983642578125,12),(1129,25.244695951306,87.7862548828125,12),(1130,25.0756484456305,87.8192138671875,12),(1131,24.966140159913,87.8961181640625,12),(1132,24.8764699108315,87.9290771484375,12),(1133,24.7667845228745,87.8961181640625,12),(1134,24.7867345419889,87.8411865234375,12),(1135,24.6570021732791,87.8851318359375,12),(1136,24.5471231797308,87.8631591796875,12),(1137,24.5571161643096,87.7642822265625,12),(1138,24.4471495897308,87.8082275390625,12),(1139,24.2469645543009,87.7532958984375,12),(1140,24.2369470039175,87.6214599609375,12),(1141,24.1668020853032,87.7093505859375,12),(1142,24.1567782333034,87.5665283203125,12),(1143,24.0765591202954,87.6324462890625,12),(1144,24.0765591202954,87.4896240234375,12),(1145,23.9962897906284,87.5115966796875,12),(1146,23.9962897906284,87.2589111328125,12),(1147,23.8958827036826,87.2698974609375,12),(1148,23.8556980097512,87.1710205078125,12),(1149,23.7250117359518,87.1820068359375,12),(1150,23.8356009866209,86.9403076171875,12),(1151,23.865745352648,86.8743896484375,12),(1152,23.7953975979787,86.8194580078125,12),(1153,23.7149535069903,86.8194580078125,12),(1154,23.6747128366088,86.6546630859375,12),(1155,23.5841260326441,86.3690185546875,12),(1156,23.4330090774204,86.3580322265625,12),(1157,23.4229284550653,86.2811279296875,12),(1158,23.4632463315504,86.1492919921875,12),(1159,23.5539165183216,86.1273193359375,12),(1160,23.5639871284512,86.0504150390625,12),(1161,23.4330090774204,86.0064697265625,12),(1162,23.4531680159162,85.8526611328125,12),(1163,23.3624285934088,85.8636474609375,12),(1164,23.2615341676518,85.8197021484375,12),(1165,23.1504620292241,85.9075927734375,12),(1166,23.0797317624499,86.0504150390625,12),(1167,23.0392977477697,86.1822509765625,12),(1168,22.9887381609607,86.3800048828125,12),(1169,22.9685090226739,86.5447998046875,12),(1170,22.7964393209195,86.4239501953125,12),(1171,22.6647098101768,86.5557861328125,12),(1172,22.6140108743703,86.6986083984375,12),(1173,22.5024074594977,86.7864990234375,12),(1174,22.2992614997412,86.8634033203125,12),(1175,22.2077491784108,86.8304443359375,12),(1176,22.2077491784108,86.7315673828125,12),(1177,22.3195894428339,86.5557861328125,12),(1178,22.3195894428339,86.3909912109375,12),(1179,22.4414948593803,86.2481689453125,12),(1180,22.6038688428957,86.0394287109375,12),(1181,22.5328537075271,85.9954833984375,12),(1182,22.3805555014215,86.0064697265625,12),(1183,22.2789305984119,85.9844970703125,12),(1184,22.1059987997506,86.0394287109375,12),(1185,21.9634249368442,85.9515380859375,12),(1186,21.9838014173847,85.8416748046875,12),(1187,22.0245456012403,85.7537841796875,12),(1188,22.0856399016503,85.8087158203125,12),(1189,22.0754593515469,85.6109619140625,12),(1190,22.1161771472106,85.4351806640625,12),(1191,22.0856399016503,85.3033447265625,12),(1192,22.0347298170442,85.2264404296875,12),(1193,22.0754593515469,85.0946044921875,12),(1194,22.1467077800126,85.0506591796875,12),(1195,22.4414948593803,85.0616455078125,12),(1196,22.461802035334,84.9517822265625,12),(1197,22.400871590306,84.7320556640625,12),(1198,22.3907139168385,84.4683837890625,12),(1199,22.3195894428339,84.3365478515625,12),(1200,22.3195894428339,84.1717529296875,12),(1201,22.4821062360777,84.1387939453125,12),(1202,22.4821062360777,84.0179443359375,12),(1203,22.6140108743703,84.0179443359375,12),(1204,22.6748473511885,84.1827392578125,12),(1205,22.8470706878391,84.3365478515625,12),(1206,22.9280416656518,84.3804931640625,12),(1207,22.9786239703849,84.2926025390625,12),(1208,22.9786239703849,84.1717529296875,12),(1209,23.0898383674767,84.0948486328125,12),(1210,23.130257185291,84.0618896484375,12),(1211,23.3624285934088,84.0509033203125,12),(1212,23.4330090774204,83.9849853515625,12),(1213,23.5841260326441,84.0179443359375,12),(1214,23.6445241985737,84.0069580078125,12),(1215,23.5639871284512,83.8861083984375,12),(1216,23.6042618470702,83.7762451171875,12),(1217,23.8054496123146,83.6663818359375,12),(1218,23.875791916101,83.5894775390625,12),(1219,24.0464639996666,83.5015869140625,12),(1220,24.1066471792018,83.3367919921875,12),(1221,24.2369470039175,83.3697509765625,12),(1222,24.3571054939697,83.4136962890625,12),(1223,24.4771500111487,83.3917236328125,12),(1224,24.5371293990799,83.4576416015625,12),(1225,24.5471231797308,83.5015869140625,12),(1226,14.9447848750884,74.124755859375,13),(1227,15.0296857565557,74.300537109375,13),(1228,15.3477619243469,74.322509765625,13),(1229,15.6441966008661,74.278564453125,13),(1230,15.7499625727488,74.278564453125,13),(1231,15.8556735099987,74.432373046875,13),(1232,16.1302620120348,74.476318359375,13),(1233,16.2779603062125,74.476318359375,13),(1234,16.3412256192075,74.322509765625,13),(1235,16.6993402345945,74.366455078125,13),(1236,16.5940814127185,74.608154296875,13),(1237,16.8255742587315,74.893798828125,13),(1238,16.972741019999,74.915771484375,13),(1239,16.972741019999,75.135498046875,13),(1240,16.9307050987655,75.311279296875,13),(1241,16.9307050987655,75.574951171875,13),(1242,17.0567846099426,75.662841796875,13),(1243,17.4135461143744,75.684814453125,13),(1244,17.3506383760488,75.904541015625,13),(1245,17.3296643294251,76.300048828125,13),(1246,17.5602465032949,76.365966796875,13),(1247,17.6649598305193,76.431884765625,13),(1248,17.6858951967387,76.673583984375,13),(1249,17.853290114098,76.761474609375,13),(1250,17.9787330955562,76.981201171875,13),(1251,18.104087015774,76.981201171875,13),(1252,18.1458517716945,77.113037109375,13),(1253,18.3545255291266,77.266845703125,13),(1254,18.2502199770656,77.508544921875,13),(1255,18.3545255291266,77.574462890625,13),(1256,17.9996316149119,77.618408203125,13),(1257,17.7696122471427,77.508544921875,13),(1258,17.581194026506,77.420654296875,13),(1259,17.4554725799728,77.640380859375,13),(1260,17.1827790564318,77.376708984375,13),(1261,16.972741019999,77.464599609375,13),(1262,16.5730227191828,77.332763671875,13),(1263,16.4255475069167,77.200927734375,13),(1264,16.2990510145818,77.596435546875,13),(1265,16.1091532392195,77.420654296875,13),(1266,15.9190735179824,77.508544921875,13),(1267,15.9190735179824,77.025146484375,13),(1268,15.6865095725514,77.025146484375,13),(1269,15.3053795304367,77.025146484375,13),(1270,15.1357643545958,77.156982421875,13),(1271,15.0084636950049,77.135009765625,13),(1272,15.0084636950049,76.937255859375,13),(1273,15.0721235458117,76.739501953125,13),(1274,14.923554399044,76.783447265625,13),(1275,14.8173706201553,76.805419921875,13),(1276,14.6048471550539,76.783447265625,13),(1277,14.4985081494462,76.959228515625,13),(1278,14.1365756514779,76.959228515625,13),(1279,13.8807458420256,76.981201171875,13),(1280,13.688687769785,77.113037109375,13),(1281,13.7100353424767,77.200927734375,13),(1282,14.1152674111227,77.113037109375,13),(1283,14.3282596777428,77.178955078125,13),(1284,14.3282596777428,77.464599609375,13),(1285,14.0513307435182,77.376708984375,13),(1286,13.7100353424767,77.398681640625,13),(1287,13.7954062031328,77.596435546875,13),(1288,13.8807458420256,77.926025390625,13),(1289,13.859413869074,78.013916015625,13),(1290,13.5605617450814,78.079833984375,13),(1291,13.5605617450814,78.255615234375,13),(1292,13.5605617450814,78.431396484375,13),(1293,13.3041028667671,78.431396484375,13),(1294,13.197164523282,78.585205078125,13),(1295,12.768946439456,78.255615234375,13),(1296,12.7475162749527,77.904052734375,13),(1297,12.7475162749527,77.684326171875,13),(1298,12.6832149118187,77.662353515625,13),(1299,12.3614659673474,77.574462890625,13),(1300,12.1897038040041,77.464599609375,13),(1301,12.0822958373636,77.860107421875,13),(1302,11.9318523269606,77.508544921875,13),(1303,11.6952727330294,77.376708984375,13),(1304,11.7167883899985,77.069091796875,13),(1305,11.7383023714369,76.849365234375,13),(1306,11.6307157379815,76.739501953125,13),(1307,11.6307157379815,76.585693359375,13),(1308,11.6307157379815,76.365966796875,13),(1309,11.824341483849,76.234130859375,13),(1310,11.9748447529318,76.124267578125,13),(1311,12.0178303377682,76.014404296875,13),(1312,12.0178303377682,75.794677734375,13),(1313,12.1467458145397,75.552978515625,13),(1314,12.3614659673474,75.355224609375,13),(1315,12.5331153572772,75.157470703125,13),(1316,12.6403383068468,75.003662109375,13),(1317,12.7903747876136,74.761962890625,13),(1318,13.4323665758138,74.652099609375,13),(1319,13.7100353424767,74.630126953125,13),(1320,13.9020758525005,74.630126953125,13),(1321,14.0726449543803,74.432373046875,13),(1322,14.2856773001826,74.410400390625,13),(1323,14.7961276036271,74.124755859375,13),(1324,14.8810871590907,74.124755859375,13),(1325,8.27672710116405,77.113037109375,14),(1326,8.47237228290914,77.178955078125,14),(1327,8.55929390330203,77.266845703125,14),(1328,8.81993892828315,77.156982421875,14),(1329,9.0153023334206,77.266845703125,14),(1330,9.12379205707398,77.178955078125,14),(1331,9.36235282205561,77.288818359375,14),(1332,9.44906182688142,77.354736328125,14),(1333,9.60074993224686,77.354736328125,14),(1334,9.60074993224686,77.113037109375,14),(1335,9.75237013917329,77.178955078125,14),(1336,9.90392141677498,77.244873046875,14),(1337,10.0554027365642,77.113037109375,14),(1338,10.250059987303,77.244873046875,14),(1339,10.336536087083,77.200927734375,14),(1340,10.336536087083,76.959228515625,14),(1341,10.2716812329467,76.827392578125,14),(1342,10.4662055550639,76.849365234375,14),(1343,10.6174180679503,76.849365234375,14),(1344,10.7037917116807,76.849365234375,14),(1345,10.8117241432755,76.849365234375,14),(1346,10.8764649948163,76.651611328125,14),(1347,11.0706029139778,76.783447265625,14),(1348,11.2861607687526,76.717529296875,14),(1349,11.3723387921411,76.541748046875,14),(1350,11.3938792329674,76.300048828125,14),(1351,11.4369552161432,76.234130859375,14),(1352,11.6522364041154,76.431884765625,14),(1353,11.7598146744419,76.343994140625,14),(1354,11.8673509114593,76.124267578125,14),(1355,11.9318523269606,75.904541015625,14),(1356,12.0393205575406,75.750732421875,14),(1357,12.1252642183316,75.706787109375,14),(1358,12.1682256773901,75.509033203125,14),(1359,12.2755988905617,75.421142578125,14),(1360,12.511665400971,75.267333984375,14),(1361,12.6617775103885,75.113525390625,14),(1362,12.7046505082879,74.915771484375,14),(1363,12.768946439456,74.783935546875,14),(1364,12.1897038040041,75.069580078125,14),(1365,11.4584907526539,75.684814453125,14),(1366,10.9627642563868,75.948486328125,14),(1367,10.531020008465,76.212158203125,14),(1368,10.0986701206034,76.234130859375,14),(1369,9.60074993224686,76.256103515625,14),(1370,9.10209673872646,76.453857421875,14),(1371,8.68963906812766,76.761474609375,14),(1372,8.25498270487788,77.135009765625,14),(1373,23.8255513068848,81.661376953125,15),(1374,23.6042618470702,81.573486328125,15),(1375,23.4430889311218,81.990966796875,15),(1376,23.2211549818466,82.210693359375,15),(1377,22.8571947009696,81.771240234375,15),(1378,22.5734382645724,81.661376953125,15),(1379,22.5734382645724,81.595458984375,15),(1380,22.4719545077392,81.353759765625,15),(1381,22.4719545077392,81.177978515625,15),(1382,22.1263547599197,81.046142578125,15),(1383,21.841104749065,80.848388671875,15),(1384,21.2893743558604,80.672607421875,15),(1385,21.5552844069232,80.408935546875,15),(1386,21.6574281973707,80.101318359375,15),(1387,21.5961505764614,79.661865234375,15),(1388,21.6165793367406,79.420166015625,15),(1389,21.5552844069232,79.090576171875,15),(1390,21.3712443706183,78.804931640625,15),(1391,21.4735175333498,78.475341796875,15),(1392,21.5757189324585,78.321533203125,15),(1393,21.4735175333498,77.947998046875,15),(1394,21.3098461410872,77.508544921875,15),(1395,21.4735175333498,77.420654296875,15),(1396,21.5757189324585,77.552490234375,15),(1397,21.7594997307198,77.552490234375,15),(1398,21.6778482933475,77.222900390625,15),(1399,21.4735175333498,76.783447265625,15),(1400,21.5348470020488,75.047607421875,15),(1401,21.6982654968525,74.564208984375,15),(1402,22.0245456012403,74.256591796875,15),(1403,22.0245456012403,74.080810546875,15),(1404,22.3703963443201,74.278564453125,15),(1405,22.5531474784032,74.124755859375,15),(1406,22.7559206814864,74.388427734375,15),(1407,22.9786239703849,74.388427734375,15),(1408,23.2817191756,74.761962890625,15),(1409,23.4229284550653,74.608154296875,15),(1410,23.7250117359518,74.937744140625,15),(1411,24.0063261987511,74.937744140625,15),(1412,24.3470966338085,74.739990234375,15),(1413,24.6070691377097,74.739990234375,15),(1414,24.7468312984121,74.871826171875,15),(1415,24.966140159913,75.113525390625,15),(1416,24.7069152410663,75.487060546875,15),(1417,24.6470171626304,75.750732421875,15),(1418,24.5071432831028,75.860595703125,15),(1419,24.1066471792018,75.794677734375,15),(1420,23.8456498876594,75.465087890625,15),(1421,23.7451258657629,75.662841796875,15),(1422,23.9460960149984,75.970458984375,15),(1423,24.3270765400186,76.322021484375,15),(1424,24.2469645543009,76.629638671875,15),(1425,24.1868474285212,76.893310546875,15),(1426,24.467150664739,76.871337890625,15),(1427,24.5870903392096,77.178955078125,15),(1428,24.9462190743601,76.893310546875,15),(1429,25.0457922403034,76.959228515625,15),(1430,25.0457922403034,77.442626953125,15),(1431,25.3638822727403,77.354736328125,15),(1432,25.3638822727403,76.893310546875,15),(1433,25.4432746123057,76.629638671875,15),(1434,25.6811373356853,76.541748046875,15),(1435,26.0370418865158,76.959228515625,15),(1436,26.2737140244064,77.288818359375,15),(1437,26.5295652382676,77.640380859375,15),(1438,26.7259868122718,78.123779296875,15),(1439,26.8044607665462,78.343505859375,15),(1440,26.8044607665462,78.607177734375,15),(1441,26.7063598576335,78.870849609375,15),(1442,26.5295652382676,79.046630859375,15),(1443,26.2145910237943,79.046630859375,15),(1444,26.0172975638517,78.848876953125,15),(1445,25.6217159598458,78.629150390625,15),(1446,25.4035849731867,78.277587890625,15),(1447,25.2645684753316,78.475341796875,15),(1448,24.9462190743601,78.233642578125,15),(1449,24.726874870507,78.233642578125,15),(1450,24.4871485631734,78.277587890625,15),(1451,24.206889622398,78.541259765625,15),(1452,24.1066471792018,78.826904296875,15),(1453,24.3671135626513,79.024658203125,15),(1454,24.6470171626304,78.892822265625,15),(1455,24.8266249565622,78.760986328125,15),(1456,25.0656971855359,78.651123046875,15),(1457,25.4234314263342,78.585205078125,15),(1458,25.4035849731867,78.936767578125,15),(1459,25.224820176765,78.980712890625,15),(1460,25.0855988970648,79.200439453125,15),(1461,25.284437746983,79.398193359375,15),(1462,25.1850588835807,79.530029296875,15),(1463,25.0855988970648,79.815673828125,15),(1464,25.224820176765,79.903564453125,15),(1465,25.4035849731867,80.277099609375,15),(1466,25.244695951306,80.386962890625,15),(1467,25.0457922403034,80.343017578125,15),(1468,25.0457922403034,80.848388671875,15),(1469,24.9860580211676,81.090087890625,15),(1470,25.1651733686639,81.375732421875,15),(1471,25.1651733686639,81.727294921875,15),(1472,24.8665025269269,81.903076171875,15),(1473,24.7867345419889,82.122802734375,15),(1474,24.6470171626304,82.606201171875,15),(1475,24.5271348225978,82.738037109375,15),(1476,24.3671135626513,82.760009765625,15),(1477,24.1267019586817,82.738037109375,15),(1478,24.0263966660173,82.738037109375,15),(1479,23.9260130330212,82.562255859375,15),(1480,23.8054496123146,82.144775390625,15),(1481,23.885837699862,81.881103515625,15),(1482,23.885837699862,81.683349609375,15),(1483,15.728813770534,73.663330078125,16),(1484,15.8556735099987,73.531494140625,16),(1485,16.2568673306234,73.355712890625,16),(1486,16.7414275470036,73.311767578125,16),(1487,17.4345105515229,73.223876953125,16),(1488,17.7696122471427,73.092041015625,16),(1489,18.6670631919266,72.828369140625,16),(1490,19.4355143390978,72.740478515625,16),(1491,19.8080541280886,72.652587890625,16),(1492,20.3034175184893,72.652587890625,16),(1493,20.0972062270839,73.070068359375,16),(1494,20.3652275374124,73.399658203125,16),(1495,20.612219573881,73.509521484375,16),(1496,20.7150151455121,73.509521484375,16),(1497,20.5093545887146,73.751220703125,16),(1498,20.6944615979078,73.905029296875,16),(1499,20.8177410197865,73.992919921875,16),(1500,20.9614396140968,73.861083984375,16),(1501,21.1459921649579,73.685302734375,16),(1502,21.248422235627,73.751220703125,16),(1503,21.2893743558604,73.948974609375,16),(1504,21.4121622297254,74.146728515625,16),(1505,21.5552844069232,74.278564453125,16),(1506,21.6370052111063,73.970947265625,16),(1507,21.6370052111063,73.795166015625,16),(1508,21.820707853875,73.773193359375,16),(1509,21.9634249368442,74.036865234375,16),(1510,22.004174972902,74.344482421875,16),(1511,21.820707853875,74.542236328125,16),(1512,21.5961505764614,74.608154296875,16),(1513,21.5961505764614,74.761962890625,16),(1514,21.5757189324585,75.091552734375,16),(1515,21.4530686330868,75.333251953125,16),(1516,21.2893743558604,76.651611328125,16),(1517,21.5757189324585,76.805419921875,16),(1518,21.6574281973707,77.069091796875,16),(1519,21.7186798057032,77.442626953125,16),(1520,21.5757189324585,77.574462890625,16),(1521,21.5348470020488,77.420654296875,16),(1522,21.3917047310366,77.552490234375,16),(1523,21.3917047310366,78.035888671875,16),(1524,21.5961505764614,78.277587890625,16),(1525,21.4735175333498,78.629150390625,16),(1526,21.5552844069232,78.980712890625,16),(1527,21.6982654968525,79.244384765625,16),(1528,21.6982654968525,79.442138671875,16),(1529,21.6165793367406,79.595947265625,16),(1530,21.6165793367406,79.903564453125,16),(1531,21.5961505764614,80.255126953125,16),(1532,21.3917047310366,80.540771484375,16),(1533,21.2893743558604,80.606689453125,16),(1534,21.1254976366063,80.474853515625,16),(1535,20.8177410197865,80.584716796875,16),(1536,20.5299331251708,80.584716796875,16),(1537,20.3446269438297,80.562744140625,16),(1538,20.2415828195422,80.430908203125,16),(1539,20.0972062270839,80.628662109375,16),(1540,19.9113835141555,80.474853515625,16),(1541,19.6632802199877,80.628662109375,16),(1542,19.4769502064884,80.892333984375,16),(1543,19.2489223284628,80.782470703125,16),(1544,19.3733407133641,80.562744140625,16),(1545,19.165924253628,80.299072265625,16),(1546,18.6878786860342,80.277099609375,16),(1547,18.6878786860342,80.079345703125,16),(1548,18.8543103618898,79.947509765625,16),(1549,19.041348796589,79.881591796875,16),(1550,19.3318784408188,79.969482421875,16),(1551,19.497664168139,79.881591796875,16),(1552,19.5597901364974,79.639892578125,16),(1553,19.5597901364974,79.310302734375,16),(1554,19.5597901364974,79.068603515625,16),(1555,19.5597901364974,78.936767578125,16),(1556,19.7253422480579,78.717041015625,16),(1557,19.8493939584228,78.387451171875,16),(1558,19.8080541280886,78.233642578125,16),(1559,19.4355143390978,78.233642578125,16),(1560,19.2696652965023,78.057861328125,16),(1561,19.0828843693402,77.838134765625,16),(1562,18.9166797866486,77.947998046875,16),(1563,18.6462451426706,77.794189453125,16),(1564,18.4587681200151,77.574462890625,16),(1565,18.2919497335503,77.398681640625,16),(1566,18.2919497335503,77.069091796875,16),(1567,17.9996316149119,76.849365234375,16),(1568,17.6440220278727,76.563720703125,16),(1569,17.4554725799728,76.387939453125,16),(1570,17.3506383760488,76.168212890625,16),(1571,17.3506383760488,75.816650390625,16),(1572,17.3716100241047,75.684814453125,16),(1573,17.0987922376787,75.662841796875,16),(1574,16.9307050987655,75.465087890625,16),(1575,16.9096836155586,75.157470703125,16),(1576,16.8676336168038,74.849853515625,16),(1577,16.7414275470036,74.674072265625,16),(1578,16.5940814127185,74.608154296875,16),(1579,16.5098328269058,74.454345703125,16),(1580,16.3201394531176,74.410400390625,16),(1581,16.1302620120348,74.410400390625,16),(1582,15.7922535703624,74.432373046875,16),(1583,15.6865095725514,74.212646484375,16),(1584,15.6441966008661,73.992919921875,16),(1585,15.6441966008661,73.729248046875,16),(1586,15.7499625727488,73.773193359375,16),(1587,23.9059269273147,94.141845703125,17),(1588,24.2269286649764,94.295654296875,17),(1589,24.6669863852163,94.493408203125,17),(1590,24.726874870507,94.603271484375,17),(1591,25.0656971855359,94.713134765625,17),(1592,25.2049411535691,94.603271484375,17),(1593,25.4631145292594,94.603271484375,17),(1594,25.5820852787007,94.779052734375,17),(1595,25.6415263730658,94.603271484375,17),(1596,25.5027845487553,94.295654296875,17),(1597,25.5820852787007,93.944091796875,17),(1598,25.2645684753316,93.636474609375,17),(1599,25.284437746983,93.438720703125,17),(1600,25.0457922403034,93.197021484375,17),(1601,24.8266249565622,93.197021484375,17),(1602,24.6669863852163,93.065185546875,17),(1603,24.2269286649764,92.999267578125,17),(1604,24.086589258228,93.043212890625,17),(1605,24.1066471792018,93.306884765625,17),(1606,23.9260130330212,93.548583984375,17),(1607,23.9862525998418,93.790283203125,17),(1608,23.8255513068848,94.097900390625,17),(1609,25.3241665257384,89.857177734375,18),(1610,25.224820176765,90.186767578125,18),(1611,25.1054973730147,90.999755859375,18),(1612,25.1452846106851,91.483154296875,18),(1613,25.125392611512,92.208251953125,18),(1614,25.0258840632448,92.449951171875,18),(1615,25.1850588835807,92.801513671875,18),(1616,25.3837352547069,92.691650390625,18),(1617,25.6019022611157,92.581787109375,18),(1618,25.7801071184222,92.406005859375,18),(1619,25.7009378814443,92.186279296875,18),(1620,26.0370418865158,92.186279296875,18),(1621,25.9975499195721,91.900634765625,18),(1622,26.0962549069685,91.834716796875,18),(1623,25.9777989554644,91.571044921875,18),(1624,25.819671943904,91.395263671875,18),(1625,25.7801071184222,91.197509765625,18),(1626,25.8592235547614,90.933837890625,18),(1627,26.0172975638517,90.604248046875,18),(1628,26.0172975638517,90.340576171875,18),(1629,25.8592235547614,90.098876953125,18),(1630,25.7207351344121,89.945068359375,18),(1631,25.5226146476233,89.901123046875,18),(1632,25.4035849731867,89.879150390625,18),(1633,22.004174972902,92.625732421875,19),(1634,22.0652780677658,92.735595703125,19),(1635,22.1874049913988,93.175048828125,19),(1636,22.4922572200852,93.175048828125,19),(1637,22.8774404648971,93.065185546875,19),(1638,23.0595162735093,93.197021484375,19),(1639,23.1403599878861,93.460693359375,19),(1640,23.6243945697169,93.416748046875,19),(1641,23.9862525998418,93.372802734375,19),(1642,24.0665281977269,93.131103515625,19),(1643,24.086589258228,92.955322265625,19),(1644,24.3070532832259,92.955322265625,19),(1645,24.3671135626513,92.867431640625,19),(1646,24.427145340082,92.757568359375,19),(1647,24.2469645543009,92.449951171875,19),(1648,24.206889622398,92.274169921875,19),(1649,23.9260130330212,92.362060546875,19),(1650,23.5841260326441,92.296142578125,19),(1651,23.019076187293,92.406005859375,19),(1652,22.5531474784032,92.559814453125,19),(1653,22.1263547599197,92.559814453125,19),(1654,22.0245456012403,92.559814453125,19),(1655,25.224820176765,93.592529296875,20),(1656,25.4234314263342,93.482666015625,20),(1657,25.5226146476233,93.328857421875,20),(1658,25.7603197547139,93.658447265625,20),(1659,25.8592235547614,93.900146484375,20),(1660,26.3131126376827,94.053955078125,20),(1661,26.4902404588696,94.185791015625,20),(1662,26.627818226393,94.427490234375,20),(1663,26.7259868122718,94.647216796875,20),(1664,26.8632806267662,94.757080078125,20),(1665,27.0395566021632,95.130615234375,20),(1666,26.961245770527,95.240478515625,20),(1667,26.6474587026594,95.262451171875,20),(1668,26.5885271473086,95.130615234375,20),(1669,26.4705730223751,95.042724609375,20),(1670,26.2540096998657,95.108642578125,20),(1671,26.0370418865158,95.130615234375,20),(1672,25.819671943904,95.108642578125,20),(1673,25.6217159598458,94.866943359375,20),(1674,25.4035849731867,94.625244140625,20),(1675,25.6019022611157,94.537353515625,20),(1676,25.5622650144275,94.229736328125,20),(1677,25.4432746123057,93.856201171875,20),(1678,25.224820176765,93.702392578125,20),(1679,25.3043037644036,93.658447265625,20),(1680,21.6574281973707,87.440185546875,21),(1681,21.9430455334382,87.198486328125,21),(1682,21.9430455334382,87.022705078125,21),(1683,22.1467077800126,86.846923828125,21),(1684,22.289096418723,86.627197265625,21),(1685,22.3907139168385,86.407470703125,21),(1686,22.5125569540514,85.989990234375,21),(1687,22.3094258412002,85.989990234375,21),(1688,22.0449133002457,85.902099609375,21),(1689,22.0449133002457,85.616455078125,21),(1690,22.1263547599197,85.308837890625,21),(1691,22.004174972902,85.177001953125,21),(1692,22.0245456012403,85.001220703125,21),(1693,22.2484287043836,85.067138671875,21),(1694,22.4516488191262,85.023193359375,21),(1695,22.4719545077392,84.561767578125,21),(1696,22.3703963443201,84.100341796875,21),(1697,22.4719545077392,83.990478515625,21),(1698,22.2280904167845,83.770751953125,21),(1699,21.9226632093259,83.572998046875,21),(1700,21.6982654968525,83.572998046875,21),(1701,21.2688997199677,83.309326171875,21),(1702,21.063997063246,83.133544921875,21),(1703,21.063997063246,82.694091796875,21),(1704,20.7766590518788,82.408447265625,21),(1705,20.3652275374124,82.430419921875,21),(1706,19.9733487861106,82.540283203125,21),(1707,19.870059837974,82.716064453125,21),(1708,19.7253422480579,82.628173828125,21),(1709,19.8907230239969,82.364501953125,21),(1710,19.9939984694855,81.903076171875,21),(1711,19.6839702358884,82.034912109375,21),(1712,19.1866776979578,82.166748046875,21),(1713,18.8751027503565,82.188720703125,21),(1714,18.4379246534744,81.793212890625,21),(1715,18.1876065524946,81.463623046875,21),(1716,17.8114560885645,81.463623046875,21),(1717,17.9160227038777,81.661376953125,21),(1718,17.9787330955562,82.012939453125,21),(1719,18.0205276578523,82.254638671875,21),(1720,18.542116654449,82.430419921875,21),(1721,18.1667304102219,82.694091796875,21),(1722,18.3753790940318,82.803955078125,21),(1723,18.4587681200151,83.067626953125,21),(1724,18.70869162256,83.067626953125,21),(1725,18.8127178564078,83.265380859375,21),(1726,19.1036482516636,83.419189453125,21),(1727,19.1451681962053,83.704833984375,21),(1728,18.8543103618898,83.792724609375,21),(1729,18.8543103618898,84.210205078125,21),(1730,18.9998028290533,84.495849609375,21),(1731,19.1244095280849,84.693603515625,21),(1732,19.1244095280849,84.847412109375,21),(1733,19.3733407133641,85.111083984375,21),(1734,19.6839702358884,85.550537109375,21),(1735,19.8493939584228,86.077880859375,21),(1736,19.9733487861106,86.473388671875,21),(1737,20.1590982706469,86.539306640625,21),(1738,20.468189222641,86.890869140625,21),(1739,20.612219573881,86.868896484375,21),(1740,20.7355659052186,87.132568359375,21),(1741,20.9819567428323,86.956787109375,21),(1742,21.1459921649579,86.890869140625,21),(1743,21.4735175333498,87.154541015625,21),(1744,21.5144067200303,87.374267578125,21),(1745,21.5961505764614,87.462158203125,21),(1746,29.8978056101559,74.498291015625,22),(1747,29.9930022845511,74.783935546875,22),(1748,29.878755346038,75.069580078125,22),(1749,29.6880527498568,75.223388671875,22),(1750,29.5161103860623,75.223388671875,22),(1751,29.6880527498568,75.377197265625,22),(1752,29.7834494568206,75.509033203125,22),(1753,29.7834494568206,75.728759765625,22),(1754,29.7834494568206,75.948486328125,22),(1755,29.7834494568206,76.212158203125,22),(1756,30.0120306803586,76.190185546875,22),(1757,30.1641263431611,76.343994140625,22),(1758,30.0881077533673,76.541748046875,22),(1759,30.2400863609834,76.563720703125,22),(1760,30.372875188118,76.695556640625,22),(1761,30.4107817908459,76.827392578125,22),(1762,30.3349538819886,76.981201171875,22),(1763,30.4865508425885,76.981201171875,22),(1764,30.713503990355,77.047119140625,22),(1765,30.8456474201826,76.849365234375,22),(1766,30.9399243310234,76.739501953125,22),(1767,31.0717559028201,76.563720703125,22),(1768,31.2128014583388,76.6131591796875,22),(1769,31.2879398926418,76.4923095703125,22),(1770,31.4005353268639,76.3714599609375,22),(1771,31.3161013834956,76.2945556640625,22),(1772,31.325486676507,76.1737060546875,22),(1773,31.4192881242884,76.0968017578125,22),(1774,31.4942618155327,76.1297607421875,22),(1775,31.6346755495414,76.0528564453125,22),(1776,31.7468541629214,75.9539794921875,22),(1777,31.8122290226407,75.9429931640625,22),(1778,31.8122290226407,75.9759521484375,22),(1779,32.017391599804,75.8770751953125,22),(1780,32.1104958962944,75.7012939453125,22),(1781,32.1756124784993,75.6463623046875,22),(1782,32.2964197989691,75.7012939453125,22),(1783,32.398515802474,75.9539794921875,22),(1784,32.4819631321718,75.8770751953125,22),(1785,32.537551746769,75.7891845703125,22),(1786,32.3706828661143,75.6463623046875,22),(1787,32.3706828661143,75.5694580078125,22),(1788,32.3149912772456,75.3277587890625,22),(1789,32.2313896627376,75.3497314453125,22),(1790,32.1384086967725,75.2508544921875,22),(1791,32.0918826200218,75.0860595703125,22),(1792,32.0080759592911,74.9212646484375,22),(1793,31.9614835572686,74.7564697265625,22),(1794,31.9148675032762,74.6246337890625,22),(1795,31.7001295539859,74.5037841796875,22),(1796,31.5972525617067,74.5257568359375,22),(1797,31.5504526754715,74.5697021484375,22),(1798,31.4567824721143,74.6466064453125,22),(1799,31.325486676507,74.5257568359375,22),(1800,31.128199299112,74.5037841796875,22),(1801,31.0435216306842,74.5257568359375,22),(1802,31.1187943959895,74.6246337890625,22),(1803,31.128199299112,74.6905517578125,22),(1804,31.0246941285251,74.6356201171875,22),(1805,30.8362146260648,74.3609619140625,22),(1806,30.6662659463233,74.1851806640625,22),(1807,30.5149490451777,74.0093994140625,22),(1808,30.4202561428452,73.9434814453125,22),(1809,30.3254712593281,73.8665771484375,22),(1810,30.2685562490477,73.9434814453125,22),(1811,30.154627220776,73.9654541015625,22),(1812,30.0881077533673,73.9215087890625,22),(1813,29.9834867184747,73.8995361328125,22),(1814,29.9358952133724,73.9764404296875,22),(1815,29.9263741786358,74.0423583984375,22),(1816,29.9454153371045,74.2620849609375,22),(1817,29.9454153371045,74.3499755859375,22),(1818,29.9454153371045,74.4378662109375,22),(1819,29.9168522330702,74.4268798828125,22),(1820,29.9263741786358,74.4818115234375,22),(1821,30.154627220776,73.9654541015625,23),(1822,30.0595856997082,73.8006591796875,23),(1823,29.9454153371045,73.5150146484375,23),(1824,29.8882809331593,73.3612060546875,23),(1825,29.6689625259925,73.3062744140625,23),(1826,29.4013195100415,73.1744384765625,23),(1827,29.200123477645,73.0535888671875,23),(1828,29.017748018496,72.9217529296875,23),(1829,28.8639184262246,72.6361083984375,23),(1830,28.700224692777,72.3614501953125,23),(1831,28.6134594240044,72.2406005859375,23),(1832,28.3430649048255,72.1636962890625,23),(1833,28.1688751800633,71.9439697265625,23),(1834,27.9847001186127,71.9000244140625,23),(1835,27.8973492296843,71.7022705078125,23),(1836,27.8487904598621,71.3397216796875,23),(1837,27.7613298745052,71.0430908203125,23),(1838,27.7321607095809,70.8782958984375,23),(1839,27.8293608597898,70.6695556640625,23),(1840,27.9847001186127,70.5267333984375,23),(1841,27.9944014110461,70.4388427734375,23),(1842,27.926474039865,70.2740478515625,23),(1843,27.8390760947778,70.1641845703125,23),(1844,27.7029837355259,70.1202392578125,23),(1845,27.5861978576927,70.0323486328125,23),(1846,27.488781168938,69.9334716796875,23),(1847,27.3522529380638,69.8345947265625,23),(1848,27.2253258369034,69.6258544921875,23),(1849,27.0493416198703,69.5379638671875,23),(1850,26.8632806267662,69.4720458984375,23),(1851,26.7063598576335,69.5599365234375,23),(1852,26.6179967221168,69.7796630859375,23),(1853,26.5885271473086,69.9444580078125,23),(1854,26.549222577692,70.1531982421875,23),(1855,26.3623420689988,70.1861572265625,23),(1856,26.2047342671076,70.1312255859375,23),(1857,26.0567828857788,70.1312255859375,23),(1858,25.9382870749237,70.1092529296875,23),(1859,25.8295610860535,70.1971435546875,23),(1860,25.7009378814443,70.2850341796875,23),(1861,25.6811373356853,70.4388427734375,23),(1862,25.6811373356853,70.6146240234375,23),(1863,25.6316215772585,70.7025146484375,23),(1864,25.5127000076205,70.6915283203125,23),(1865,25.3340966847945,70.6805419921875,23),(1866,25.1950004243075,70.8563232421875,23),(1867,25.0159287633679,70.9332275390625,23),(1868,24.8565343393107,70.9991455078125,23),(1869,24.6869524119992,71.1199951171875,23),(1870,24.6170573408095,71.2298583984375,23),(1871,24.6570021732791,71.5045166015625,23),(1872,24.6370313535095,71.7352294921875,23),(1873,24.6370313535095,72.0098876953125,23),(1874,24.5571161643096,72.2186279296875,23),(1875,24.5371293990799,72.3175048828125,23),(1876,24.4971463205719,72.4822998046875,23),(1877,24.467150664739,72.6470947265625,23),(1878,24.3571054939697,72.7349853515625,23),(1879,24.3571054939697,72.8448486328125,23),(1880,24.427145340082,72.9766845703125,23),(1881,24.4371478616156,73.0426025390625,23),(1882,24.3571054939697,73.1414794921875,23),(1883,24.2569813158825,73.1195068359375,23),(1884,24.1868474285212,73.1085205078125,23),(1885,23.9260130330212,73.4490966796875,23),(1886,23.8356009866209,73.3941650390625,23),(1887,23.7451258657629,73.4490966796875,23),(1888,23.5941943262038,73.5479736328125,23),(1889,23.5941943262038,73.6468505859375,23),(1890,23.4531680159162,73.7017822265625,23),(1891,23.392681978613,73.8006591796875,23),(1892,23.3422558351305,73.9434814453125,23),(1893,23.2918105324419,74.0863037109375,23),(1894,23.1504620292241,74.1961669921875,23),(1895,23.0797317624499,74.3060302734375,23),(1896,23.0797317624499,74.4049072265625,23),(1897,23.0898383674767,74.5367431640625,23),(1898,23.1706638271022,74.6905517578125,23),(1899,23.533772983256,74.8223876953125,23),(1900,23.6646507316316,74.9432373046875,23),(1901,24.1467535947031,74.9432373046875,23),(1902,24.2169095377217,74.8223876953125,23),(1903,24.6370313535095,74.7564697265625,23),(1904,24.7069152410663,74.8663330078125,23),(1905,24.627044746156,74.9652099609375,23),(1906,24.906367237908,75.0860595703125,23),(1907,24.9462190743601,75.2398681640625,23),(1908,24.9163314045991,75.3607177734375,23),(1909,24.7667845228745,75.2508544921875,23),(1910,24.7168954558593,75.4266357421875,23),(1911,24.7069152410663,75.6463623046875,23),(1912,24.7368534847707,75.8221435546875,23),(1913,24.5770997442894,75.8880615234375,23),(1914,24.4971463205719,75.9210205078125,23),(1915,24.417142025372,75.8111572265625,23),(1916,24.3270765400186,75.7452392578125,23),(1917,24.2169095377217,75.7342529296875,23),(1918,24.1567782333034,75.8001708984375,23),(1919,24.0464639996666,75.8001708984375,23),(1920,23.9862525998418,75.7342529296875,23),(1921,23.9762146266383,75.6024169921875,23),(1922,23.9762146266383,75.5364990234375,23),(1923,23.8356009866209,75.5364990234375,23),(1924,23.8456498876594,75.6903076171875,23),(1925,23.8456498876594,75.8331298828125,23),(1926,23.9862525998418,75.9979248046875,23),(1927,24.1166749617513,76.1517333984375,23),(1928,24.2870268653764,76.2615966796875,23),(1929,24.1567782333034,76.4593505859375,23),(1930,24.1868474285212,76.6021728515625,23),(1931,24.2369470039175,76.6900634765625,23),(1932,24.1467535947031,76.8109130859375,23),(1933,24.1567782333034,76.9097900390625,23),(1934,24.5471231797308,77.0526123046875,23),(1935,24.7468312984121,76.8658447265625,23),(1936,24.8365955538912,76.9317626953125,23),(1937,25.0258840632448,77.0416259765625,23),(1938,25.0258840632448,77.1405029296875,23),(1939,25.1154453970619,77.3712158203125,23),(1940,25.3142355521976,76.8658447265625,23),(1941,25.3142355521976,76.7120361328125,23),(1942,25.4234314263342,76.5911865234375,23),(1943,25.8394494020632,76.5362548828125,23),(1944,25.8789944001962,76.7120361328125,23),(1945,25.9975499195721,76.8438720703125,23),(1946,26.2244469456343,77.0745849609375,23),(1947,26.2244469456343,77.2393798828125,23),(1948,26.3328069228979,77.3602294921875,23),(1949,26.4312280645064,77.5360107421875,23),(1950,26.5099045314139,77.7227783203125,23),(1951,26.6670958011048,77.9864501953125,23),(1952,26.7750393869996,78.1622314453125,23),(1953,26.9024768862798,78.2501220703125,23),(1954,26.9122738266256,78.0963134765625,23),(1955,26.9416595453815,77.8546142578125,23),(1956,26.9024768862798,77.6568603515625,23),(1957,26.843677401113,77.5140380859375,23),(1958,26.9318651563889,77.5689697265625,23),(1959,27.0493416198703,77.7667236328125,23),(1960,27.3912782225793,77.4481201171875,23),(1961,27.5277582068619,77.3602294921875,23),(1962,27.7613298745052,77.2174072265625,23),(1963,27.7710511931723,77.1185302734375,23),(1964,27.7127102608875,77.0086669921875,23),(1965,27.6446063819433,76.9537353515625,23),(1966,28.1107487606335,76.9317626953125,23),(1967,28.1688751800633,76.8658447265625,23),(1968,28.1204386871011,76.7779541015625,23),(1969,28.0525908233399,76.7120361328125,23),(1970,27.9749979532678,76.6021728515625,23),(1971,27.9749979532678,76.4813232421875,23),(1972,28.1204386871011,76.3934326171875,23),(1973,28.0913662814069,76.3165283203125,23),(1974,28.023500048883,76.2506103515625,23),(1975,27.9944014110461,76.1956787109375,23),(1976,27.8973492296843,76.1956787109375,23),(1977,27.8390760947778,76.2396240234375,23),(1978,27.7904912248309,76.2066650390625,23),(1979,27.8682165795141,76.0308837890625,23),(1980,28.3043806829628,75.9869384765625,23),(1981,28.3527337602378,75.8770751953125,23),(1982,28.459033019728,75.6903076171875,23),(1983,28.6038144078413,75.5364990234375,23),(1984,28.9793120367225,75.4376220703125,23),(1985,29.2384770859281,75.3057861328125,23),(1986,29.2672328652009,75.1300048828125,23),(1987,29.2768163283686,74.9871826171875,23),(1988,29.353451668635,74.8773193359375,23),(1989,29.3630270377838,74.7564697265625,23),(1990,29.3342982303157,74.6026611328125,23),(1991,29.4395975666029,74.5367431640625,23),(1992,29.8501731256899,74.4927978515625,23),(1993,29.9073293768516,74.4268798828125,23),(1994,29.9168522330702,74.2950439453125,23),(1995,29.9358952133724,74.1412353515625,23),(1996,29.9454153371045,73.9874267578125,23),(1997,30.0025169385707,73.9215087890625,23),(1998,27.8876392171365,88.1597900390625,24),(1999,27.9555910046426,88.1378173828125,24),(2000,27.9555910046426,88.2476806640625,24),(2001,27.9847001186127,88.3795166015625,24),(2002,28.0622859998122,88.4893798828125,24),(2003,28.1010579586694,88.6322021484375,24),(2004,28.0719803017799,88.7640380859375,24),(2005,27.9749979532678,88.8739013671875,24),(2006,27.907058371122,88.8629150390625,24),(2007,27.8002099374183,88.8519287109375,24),(2008,27.5959347744951,88.8079833984375,24),(2009,27.5472415462533,88.7969970703125,24),(2010,27.4302897388626,88.8519287109375,24),(2011,27.3229749472457,88.9617919921875,24),(2012,27.2643957764954,88.8739013671875,24),(2013,27.1666952222531,88.7640380859375,24),(2014,27.1080338014631,88.5223388671875,24),(2015,27.1080338014631,88.3465576171875,24),(2016,27.1275910285021,88.1597900390625,24),(2017,27.2155562090297,88.0718994140625,24),(2018,27.2155562090297,87.9840087890625,24),(2019,27.3132138985683,88.0828857421875,24),(2020,27.4302897388626,88.0609130859375,24),(2021,27.5861978576927,88.0938720703125,24),(2022,27.7807716433482,88.1597900390625,24),(2023,27.8390760947778,88.1707763671875,24),(2024,27.8682165795141,88.1927490234375,24),(2025,13.4644218173885,80.3045654296875,25),(2026,13.475105944335,80.1947021484375,25),(2027,13.475105944335,80.0408935546875,25),(2028,13.5071554595363,79.9859619140625,25),(2029,13.3789316584316,79.9200439453125,25),(2030,13.2827189608964,79.7882080078125,25),(2031,13.2506395700431,79.6673583984375,25),(2032,13.293411149536,79.5355224609375,25),(2033,13.3254848855979,79.4256591796875,25),(2034,13.2613331707983,79.4256591796875,25),(2035,13.1543760554185,79.3157958984375,25),(2036,13.1222798015563,79.2388916015625,25),(2037,13.0366693231152,79.0631103515625,25),(2038,13.1008799695265,78.8763427734375,25),(2039,13.0687767343577,78.6676025390625,25),(2040,12.9831477167966,78.6126708984375,25),(2041,12.7903747876136,78.5687255859375,25),(2042,12.6510581337035,78.4259033203125,25),(2043,12.618897304044,78.2830810546875,25),(2044,12.6296180301748,78.2171630859375,25),(2045,12.7582315840698,78.2171630859375,25),(2046,12.8118013165826,78.1182861328125,25),(2047,12.8118013165826,77.9644775390625,25),(2048,12.8974891837559,77.8765869140625,25),(2049,12.854648905589,77.7996826171875,25),(2050,12.7796608407557,77.7447509765625,25),(2051,12.6296180301748,77.6898193359375,25),(2052,12.6939329358514,77.6129150390625,25),(2053,12.5009397543399,77.5799560546875,25),(2054,12.3936588623774,77.6019287109375,25),(2055,12.2541277376574,77.4920654296875,25),(2056,12.1789649579065,77.4920654296875,25),(2057,12.1789649579065,77.7667236328125,25),(2058,12.0178303377682,77.7117919921875,25),(2059,11.9211031542496,77.5250244140625,25),(2060,11.888853082976,77.4481201171875,25),(2061,11.7920799755406,77.3931884765625,25),(2062,11.7705701956252,77.2174072265625,25),(2063,11.7705701956252,76.9866943359375,25),(2064,11.7920799755406,76.9097900390625,25),(2065,11.7275455903404,76.8109130859375,25),(2066,11.576906799409,76.8548583984375,25),(2067,11.6737554034334,76.5142822265625,25),(2068,11.6307157379815,76.3824462890625,25),(2069,11.6307157379815,76.2835693359375,25),(2070,11.5230875068685,76.2286376953125,25),(2071,11.4477231892923,76.3055419921875,25),(2072,11.3938792329674,76.5032958984375,25),(2073,11.3077077077655,76.5472412109375,25),(2074,11.2538373288317,76.4593505859375,25),(2075,11.1784018737118,76.4813232421875,25),(2076,11.2107337656895,76.7230224609375,25),(2077,11.0274721941179,76.6461181640625,25),(2078,10.9627642563868,76.6571044921875,25),(2079,10.8009326406875,76.8548583984375,25),(2080,10.6066196418654,76.8218994140625,25),(2081,10.4445977228349,76.8109130859375,25),(2082,10.2068130724846,76.8988037109375,25),(2083,10.2392488109812,77.0196533203125,25),(2084,10.336536087083,77.1514892578125,25),(2085,10.3041103283294,77.2393798828125,25),(2086,10.141931686131,77.2283935546875,25),(2087,10.066220126753,77.2393798828125,25),(2088,9.7848512507506,77.1734619140625,25),(2089,9.60074993224686,77.1844482421875,25),(2090,9.57908433588253,77.3272705078125,25),(2091,9.49240815376554,77.4261474609375,25),(2092,9.2973068563276,77.2613525390625,25),(2093,9.15633256004679,77.2174072265625,25),(2094,8.88507166346899,77.1405029296875,25),(2095,8.84165112080914,77.2064208984375,25),(2096,8.71135887542651,77.1734619140625,25),(2097,8.48323856391351,77.2174072265625,25),(2098,8.39629974173801,77.1734619140625,25),(2099,8.24411005754921,77.1185302734375,25),(2100,8.16799317723188,77.2174072265625,25),(2101,8.11361508149333,77.4041748046875,25),(2102,8.0701073044391,77.5579833984375,25),(2103,8.16799317723188,77.7337646484375,25),(2104,8.33108283350031,78.0084228515625,25),(2105,8.53756535080402,78.1402587890625,25),(2106,8.70049912927583,78.1512451171875,25),(2107,8.90678000752024,78.2061767578125,25),(2108,9.04785269101114,78.3160400390625,25),(2109,9.18887008447341,78.5467529296875,25),(2110,9.23224879941867,78.7774658203125,25),(2111,9.23224879941867,78.9862060546875,25),(2112,9.23224879941867,79.2608642578125,25),(2113,9.3189901923979,79.3597412109375,25),(2114,9.3189901923979,79.1400146484375,25),(2115,9.38403210960169,78.9862060546875,25),(2116,9.52491430234589,78.9202880859375,25),(2117,9.73071430575694,79.0081787109375,25),(2118,9.88227549342994,79.1619873046875,25),(2119,10.066220126753,79.2828369140625,25),(2120,10.2176253531996,79.2828369140625,25),(2121,10.250059987303,79.3157958984375,25),(2122,10.2824913015242,79.3817138671875,25),(2123,10.2824913015242,79.5794677734375,25),(2124,10.2824913015242,79.7442626953125,25),(2125,10.2824913015242,79.8760986328125,25),(2126,10.2824913015242,79.9310302734375,25),(2127,10.3905715763377,79.8760986328125,25),(2128,10.8548862684725,79.8760986328125,25),(2129,11.3184805698943,79.8760986328125,25),(2130,11.4800246485558,79.8101806640625,25),(2131,11.609193407939,79.7662353515625,25),(2132,11.7598146744419,79.8651123046875,25),(2133,12.1145227711184,79.9749755859375,25),(2134,12.2970682928538,80.0408935546875,25),(2135,12.511665400971,80.2166748046875,25),(2136,12.8653596614089,80.2606201171875,25),(2137,13.0687767343577,80.3155517578125,25),(2138,13.3041028667671,80.3594970703125,25),(2139,13.4323665758138,80.3485107421875,25),(2140,13.4857895939085,80.3375244140625,25),(2141,24.4871485631734,92.2576904296875,26),(2142,24.5071432831028,92.1588134765625,26),(2143,24.417142025372,92.1588134765625,26),(2144,24.3270765400186,92.0709228515625,26),(2145,24.427145340082,91.9610595703125,26),(2146,24.3470966338085,91.9500732421875,26),(2147,24.206889622398,91.9061279296875,26),(2148,24.1367281697474,91.9171142578125,26),(2149,24.2269286649764,91.7852783203125,26),(2150,24.1166749617513,91.7193603515625,26),(2151,24.2169095377217,91.6754150390625,26),(2152,24.1367281697474,91.5655517578125,26),(2153,24.0665281977269,91.5106201171875,26),(2154,24.1166749617513,91.4117431640625,26),(2155,23.9862525998418,91.3897705078125,26),(2156,23.9762146266383,91.2799072265625,26),(2157,23.875791916101,91.2249755859375,26),(2158,23.8255513068848,91.2689208984375,26),(2159,23.7551817661126,91.1920166015625,26),(2160,23.7250117359518,91.1151123046875,26),(2161,23.6344597709946,91.1920166015625,26),(2162,23.4934766609609,91.2139892578125,26),(2163,23.3422558351305,91.3018798828125,26),(2164,23.0392977477697,91.4007568359375,26),(2165,23.2615341676518,91.4007568359375,26),(2166,22.9482768568809,91.6204833984375,26),(2167,23.0696243977083,91.8182373046875,26),(2168,23.2918105324419,91.7742919921875,26),(2169,23.4531680159162,91.8402099609375,26),(2170,23.4733238777712,91.9940185546875,26),(2171,23.7048945023249,91.9500732421875,26),(2172,23.6143285949917,92.1038818359375,26),(2173,23.6847741668838,92.2357177734375,26),(2174,23.6243945697169,92.2906494140625,26),(2175,23.8054496123146,92.2906494140625,26),(2176,24.016361823963,92.3565673828125,26),(2177,24.2369470039175,92.3675537109375,26),(2178,24.2469645543009,92.2137451171875,26),(2179,24.3571054939697,92.2686767578125,26),(2180,24.4371478616156,92.2906494140625,26),(2181,24.467150664739,92.2576904296875,26),(2182,30.4202561428452,77.6129150390625,27),(2183,30.3349538819886,77.7227783203125,27),(2184,30.2400863609834,77.9534912109375,27),(2185,30.1261243642246,77.8436279296875,27),(2186,29.8978056101559,77.6788330078125,27),(2187,29.7643773751631,77.7557373046875,27),(2188,29.6403203953514,77.7996826171875,27),(2189,29.6975965022832,77.9095458984375,27),(2190,29.5925654033141,77.9425048828125,27),(2191,29.5639015514144,78.0523681640625,27),(2192,29.6880527498568,78.1622314453125,27),(2193,29.7548399725109,78.3270263671875,27),(2194,29.6975965022832,78.5357666015625,27),(2195,29.4969875965358,78.7554931640625,27),(2196,29.4395975666029,78.8983154296875,27),(2197,29.2863988929348,78.7115478515625,27),(2198,29.2193020767795,78.8543701171875,27),(2199,29.1329701308786,78.9642333984375,27),(2200,29.1905328322946,79.0521240234375,27),(2201,29.10417668395,79.1290283203125,27),(2202,28.9985318140518,79.1839599609375,27),(2203,28.9793120367225,79.2718505859375,27),(2204,28.950475674848,79.3817138671875,27),(2205,28.8446736807718,79.4366455078125,27),(2206,28.8639184262246,79.5574951171875,27),(2207,28.8639184262246,79.7662353515625,27),(2208,28.7965462417692,79.8651123046875,27),(2209,28.7291304834302,80.0299072265625,27),(2210,28.9600886880068,80.0518798828125,27),(2211,28.9697008086942,80.1397705078125,27),(2212,29.1329701308786,80.1617431640625,27),(2213,29.200123477645,80.2716064453125,27),(2214,29.2863988929348,80.3155517578125,27),(2215,29.4491648269247,80.2386474609375,27),(2216,29.5925654033141,80.4254150390625,27),(2217,29.6880527498568,80.3704833984375,27),(2218,29.7739138699922,80.3704833984375,27),(2219,29.7834494568206,80.4913330078125,27),(2220,29.9739702405166,80.6231689453125,27),(2221,30.02154350974,80.7220458984375,27),(2222,30.1071178870924,80.8648681640625,27),(2223,30.259067203213,80.9747314453125,27),(2224,30.3159877185579,80.9197998046875,27),(2225,30.4676141022579,80.6671142578125,27),(2226,30.6379120283411,80.0299072265625,27),(2227,30.7418357178898,79.9749755859375,27),(2228,30.8456474201826,79.8870849609375,27),(2229,30.9399243310234,79.7222900390625,27),(2230,30.9587685707799,79.6563720703125,27),(2231,31.2691608904777,79.2828369140625,27),(2232,31.1752098283108,78.7774658203125,27),(2233,31.2221970321032,78.5906982421875,27),(2234,31.2785508589465,78.3819580078125,27),(2235,31.2503781498557,78.1842041015625,27),(2236,31.128199299112,77.9534912109375,27),(2237,31.0905740949542,77.8216552734375,27),(2238,30.9776090933487,77.7886962890625,27),(2239,30.7984741795678,77.7117919921875,27),(2240,30.7512777762578,77.7008056640625,27),(2241,30.6473642582432,77.8326416015625,27),(2242,30.5149490451777,77.7667236328125,27),(2243,30.4486736792876,77.6348876953125,27),(2244,28.8254253744772,80.123291015625,28),(2245,28.8254253744772,79.793701171875,28),(2246,28.8639184262246,79.442138671875,28),(2247,29.1905328322946,79.002685546875,28),(2248,29.2863988929348,78.673095703125,28),(2249,29.4778611958168,78.958740234375,28),(2250,29.6116701151974,78.629150390625,28),(2251,29.7643773751631,78.343505859375,28),(2252,29.5543451257483,78.013916015625,28),(2253,29.630771207229,77.860107421875,28),(2254,29.7071393481341,77.684326171875,28),(2255,30.0881077533673,77.772216796875,28),(2256,30.259067203213,77.969970703125,28),(2257,30.372875188118,77.662353515625,28),(2258,30.2400863609834,77.442626953125,28),(2259,29.8406438998344,77.200927734375,28),(2260,29.324720161511,77.135009765625,28),(2261,28.9985318140518,77.200927734375,28),(2262,28.6520306303623,77.178955078125,28),(2263,28.2656823901465,77.552490234375,28),(2264,28.0525908233399,77.552490234375,28),(2265,27.5861978576927,77.442626953125,28),(2266,27.2350946077955,77.596435546875,28),(2267,27.0004080035217,77.640380859375,28),(2268,26.8828804557234,77.442626953125,28),(2269,26.7259868122718,77.398681640625,28),(2270,26.8828804557234,77.706298828125,28),(2271,26.9416595453815,78.057861328125,28),(2272,26.8828804557234,78.365478515625,28),(2273,26.627818226393,78.892822265625,28),(2274,26.4902404588696,79.156494140625,28),(2275,26.0962549069685,79.068603515625,28),(2276,25.8592235547614,78.826904296875,28),(2277,25.5622650144275,78.497314453125,28),(2278,25.3241665257384,78.541259765625,28),(2279,25.0258840632448,78.299560546875,28),(2280,24.427145340082,78.299560546875,28),(2281,24.2669972884182,78.804931640625,28),(2282,24.567108352576,78.914794921875,28),(2283,25.0059726562392,78.563232421875,28),(2284,25.244695951306,78.629150390625,28),(2285,25.4631145292594,78.914794921875,28),(2286,25.1452846106851,78.936767578125,28),(2287,25.1452846106851,79.420166015625,28),(2288,25.0059726562392,79.859619140625,28),(2289,25.4234314263342,80.277099609375,28),(2290,24.9860580211676,80.343017578125,28),(2291,25.1054973730147,80.936279296875,28),(2292,24.8864364907877,80.980224609375,28),(2293,25.1054973730147,81.419677734375,28),(2294,24.9860580211676,81.968994140625,28),(2295,24.5870903392096,82.364501953125,28),(2296,24.627044746156,82.738037109375,28),(2297,24.0263966660173,82.738037109375,28),(2298,23.9059269273147,82.869873046875,28),(2299,23.9260130330212,83.089599609375,28),(2300,24.0665281977269,83.309326171875,28),(2301,24.5071432831028,83.419189453125,28),(2302,24.7867345419889,83.441162109375,28),(2303,25.1452846106851,83.287353515625,28),(2304,25.5622650144275,83.990478515625,28),(2305,25.6613334989527,84.210205078125,28),(2306,25.6613334989527,84.517822265625,28),(2307,25.7801071184222,84.759521484375,28),(2308,25.8789944001962,84.451904296875,28),(2309,26.1159859253335,84.100341796875,28),(2310,26.352497858154,84.100341796875,28),(2311,26.4509022236726,83.924560546875,28),(2312,26.5885271473086,83.990478515625,28),(2313,26.5885271473086,84.298095703125,28),(2314,26.6670958011048,84.364013671875,28),(2315,26.8632806267662,84.188232421875,28),(2316,27.0199840079826,84.122314453125,28),(2317,27.3132138985683,83.946533203125,28),(2318,27.3912782225793,83.924560546875,28),(2319,27.3912782225793,83.638916015625,28),(2320,27.488781168938,83.463134765625,28),(2321,27.3327351368591,83.221435546875,28),(2322,27.469287473692,83.067626953125,28),(2323,27.488781168938,82.694091796875,28),(2324,27.7029837355259,82.650146484375,28),(2325,27.7029837355259,82.320556640625,28),(2326,27.9749979532678,81.903076171875,28),(2327,27.8390760947778,81.749267578125,28),(2328,28.0331978476764,81.573486328125,28),(2329,28.1495032115446,81.397705078125,28),(2330,28.323724553546,81.199951171875,28),(2331,28.6327467992259,80.562744140625,28),(2332,28.574874047447,80.452880859375,28),(2333,28.7676591056913,80.167236328125,28),(2334,21.6370052111063,87.528076171875,29),(2335,21.820707853875,87.901611328125,29),(2336,21.820707853875,88.033447265625,29),(2337,21.5757189324585,88.143310546875,29),(2338,21.5757189324585,88.428955078125,29),(2339,21.841104749065,88.626708984375,29),(2340,21.5348470020488,88.736572265625,29),(2341,21.6574281973707,88.934326171875,29),(2342,21.7799053425296,89.066162109375,29),(2343,22.3500758061249,89.022216796875,29),(2344,22.6951201849657,88.824462890625,29),(2345,22.9583933180863,88.912353515625,29),(2346,23.2413461023861,88.934326171875,29),(2347,23.2413461023861,88.714599609375,29),(2348,23.5438451365058,88.648681640625,29),(2349,23.7853448059412,88.538818359375,29),(2350,23.9260130330212,88.714599609375,29),(2351,24.2469645543009,88.714599609375,29),(2352,24.3871273246045,88.604736328125,29),(2353,24.3470966338085,88.231201171875,29),(2354,24.567108352576,88.077392578125,29),(2355,24.7069152410663,87.945556640625,29),(2356,24.9462190743601,88.253173828125,29),(2357,25.0059726562392,88.385009765625,29),(2358,25.2049411535691,88.472900390625,29),(2359,25.1452846106851,88.780517578125,29),(2360,25.3043037644036,89.000244140625,29),(2361,25.5820852787007,88.714599609375,29),(2362,25.5027845487553,88.626708984375,29),(2363,25.7009378814443,88.363037109375,29),(2364,25.8394494020632,88.275146484375,29),(2365,25.8394494020632,88.077392578125,29),(2366,25.9975499195721,88.165283203125,29),(2367,26.2145910237943,88.231201171875,29),(2368,26.391869671769,88.516845703125,29),(2369,26.2737140244064,88.736572265625,29),(2370,26.3328069228979,89.022216796875,29),(2371,26.0370418865158,89.263916015625,29),(2372,26.0370418865158,89.549560546875,29),(2373,26.1751589901781,89.681396484375,29),(2374,26.4312280645064,89.791259765625,29),(2375,26.7259868122718,89.813232421875,29),(2376,26.8240707804702,89.417724609375,29),(2377,26.8240707804702,89.088134765625,29),(2378,27.0591257843741,88.890380859375,29),(2379,27.1373683597956,88.736572265625,29),(2380,27.1373683597956,88.406982421875,29),(2381,27.0786915529275,88.121337890625,29),(2382,26.6474587026594,88.121337890625,29),(2383,26.4312280645064,88.231201171875,29),(2384,26.1357136131739,88.055419921875,29),(2385,25.898761936567,87.813720703125,29),(2386,25.6019022611157,88.055419921875,29),(2387,25.3638822727403,87.835693359375,29),(2388,25.125392611512,87.791748046875,29),(2389,24.9262947663956,87.857666015625,29),(2390,24.4871485631734,87.769775390625,29),(2391,24.1467535947031,87.615966796875,29),(2392,24.0063261987511,87.374267578125,29),(2393,24.0063261987511,87.242431640625,29),(2394,23.7451258657629,87.154541015625,29),(2395,23.7652368897587,86.824951171875,29),(2396,23.5639871284512,86.583251953125,29),(2397,23.5438451365058,86.385498046875,29),(2398,23.4632463315504,86.143798828125,29),(2399,23.4027649054079,85.858154296875,29),(2400,23.1605633090483,85.858154296875,29),(2401,22.9786239703849,86.341552734375,29),(2402,22.7761815050865,86.495361328125,29),(2403,22.5531474784032,86.824951171875,29),(2404,22.1059987997506,86.781005859375,29),(2405,21.9226632093259,86.978759765625,29),(2406,21.8818898076293,87.286376953125,29),(2407,21.6982654968525,87.440185546875,29),(2408,21.6165793367406,87.462158203125,29),(2409,13.7100353424767,93.0706787109375,30),(2410,13.656662778922,92.9388427734375,30),(2411,13.4216805428783,92.7960205078125,30),(2412,13.0794782772264,92.7520751953125,30),(2413,12.9617358435343,92.6861572265625,30),(2414,12.8010882796743,92.6312255859375,30),(2415,12.6403383068468,92.7410888671875,30),(2416,12.4580327196349,92.6641845703125,30),(2417,12.2970682928538,92.6751708984375,30),(2418,12.0822958373636,92.5982666015625,30),(2419,11.9963384019362,92.5872802734375,30),(2420,11.8781022093766,92.4884033203125,30),(2421,11.6307157379815,92.5213623046875,30),(2422,11.4477231892923,92.5543212890625,30),(2423,11.3184805698943,92.6202392578125,30),(2424,11.3831092163533,92.7191162109375,30),(2425,11.7490587329249,92.8179931640625,30),(2426,11.9533493936434,92.7850341796875,30),(2427,12.1682256773901,92.8729248046875,30),(2428,12.0393205575406,92.9168701171875,30),(2429,11.7383023714369,93.0596923828125,30),(2430,11.9211031542496,93.1036376953125,30),(2431,12.0285756623422,92.9937744140625,30),(2432,12.1252642183316,93.1475830078125,30),(2433,12.2541277376574,93.1365966796875,30),(2434,12.3078023366229,92.9608154296875,30),(2435,12.511665400971,93.0267333984375,30),(2436,12.7368005124603,92.9937744140625,30),(2437,12.8760699599465,92.9498291015625,30),(2438,13.0901793557337,93.0926513671875,30),(2439,13.4003070504946,93.1146240234375,30),(2440,13.5392006689308,93.1146240234375,30),(2441,13.656662778922,93.0926513671875,30),(2442,13.7100353424767,93.1146240234375,30);
/*!40000 ALTER TABLE `device_stategeoinfo` ENABLE KEYS */;
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
  `parent_id` int(11) DEFAULT NULL,
  `organization_id` int(11) NOT NULL,
  `address` varchar(100) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `is_deleted` int(11) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `user_group_usergroup_410d0aac` (`parent_id`),
  KEY `user_group_usergroup_de772da3` (`organization_id`),
  KEY `user_group_usergroup_329f6fb3` (`lft`),
  KEY `user_group_usergroup_e763210f` (`rght`),
  KEY `user_group_usergroup_ba470c4a` (`tree_id`),
  KEY `user_group_usergroup_20e079f4` (`level`),
  CONSTRAINT `organization_id_refs_id_f02857e6` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `parent_id_refs_id_aa9a5c51` FOREIGN KEY (`parent_id`) REFERENCES `user_group_usergroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_usergroup`
--

LOCK TABLES `user_group_usergroup` WRITE;
/*!40000 ALTER TABLE `user_group_usergroup` DISABLE KEYS */;
INSERT INTO `user_group_usergroup` VALUES (1,'default','Default',NULL,1,'','',0,0,0,0,0);
/*!40000 ALTER TABLE `user_group_usergroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `command_command`
--

DROP TABLE IF EXISTS `command_command`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `command_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(100) DEFAULT NULL,
  `command_line` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `command_command`
--

LOCK TABLES `command_command` WRITE;
/*!40000 ALTER TABLE `command_command` DISABLE KEYS */;
INSERT INTO `command_command` VALUES (1,'ping','Ping','/omd/sites/nocout/lib/nagios/plugins/check_ping');
/*!40000 ALTER TABLE `command_command` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_antenna`
--

DROP TABLE IF EXISTS `inventory_antenna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_antenna` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `polarization` varchar(50) DEFAULT NULL,
  `tilt` int(11) DEFAULT NULL,
  `beam_width` int(11) DEFAULT NULL,
  `azimuth_angle` int(11) DEFAULT NULL,
  `splitter_installed` varchar(4) DEFAULT NULL,
  `sync_splitter_used` varchar(4) DEFAULT NULL,
  `make_of_antenna` varchar(40) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_antenna`
--

LOCK TABLES `inventory_antenna` WRITE;
/*!40000 ALTER TABLE `inventory_antenna` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_antenna` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$12000$SPMzXFDtqufn$cDLdftWoFOfUe0TniGNqg1nnodLYxOqQ8+Wp/75w9vk=','2014-06-24 08:14:52',1,'nocout','','','admin@nocout.com',1,1,'2014-05-28 14:09:12'),(2,'pbkdf2_sha256$12000$pzM0PoqRCIxZ$tKHiDncSZKXGyZUbqOkNy/86KnkbpOoDKlbV6D8M+bs=','2014-06-25 05:17:32',0,'gisadmin','GIS Admin','','default@nocout.com',0,1,'2014-05-28 15:05:51'),(3,'pbkdf2_sha256$12000$pzM0PoqRCIxZ$tKHiDncSZKXGyZUbqOkNy/86KnkbpOoDKlbV6D8M+bs=','2014-06-24 13:47:44',0,'gisoperator','GIS Operator','','defaultoperator@nocout.com',0,1,'2014-06-24 13:30:18'),(4,'pbkdf2_sha256$12000$pzM0PoqRCIxZ$tKHiDncSZKXGyZUbqOkNy/86KnkbpOoDKlbV6D8M+bs=','2014-06-24 13:31:27',0,'gisviewer','GIS Viewer','','gisviewer@nocout.com',0,1,'2014-06-24 13:31:27');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-06-25 11:25:18
