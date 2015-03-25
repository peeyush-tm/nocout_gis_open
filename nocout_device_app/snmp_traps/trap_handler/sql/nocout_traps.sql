-- MySQL dump 10.13  Distrib 5.5.38, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: nocout_traps
-- ------------------------------------------------------
-- Server version	5.5.38-0ubuntu0.12.04.1

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
-- Table structure for table `activity_stream_useraction`
--

DROP TABLE IF EXISTS `activity_stream_useraction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_stream_useraction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `action` longtext NOT NULL,
  `module` varchar(128) NOT NULL,
  `logged_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alarm_escalation_escalationlevel`
--

DROP TABLE IF EXISTS `alarm_escalation_escalationlevel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alarm_escalation_escalationlevel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` smallint(5) unsigned NOT NULL,
  `region_name` varchar(50) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `emails` longtext NOT NULL,
  `phones` longtext NOT NULL,
  `device_type_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `service_data_source_id` int(11) NOT NULL,
  `alarm_age` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `alarm_escalation_escalationlevel_de772da3` (`organization_id`),
  KEY `alarm_escalation_escalationlevel_d8be8594` (`device_type_id`),
  KEY `alarm_escalation_escalationlevel_91a0ac17` (`service_id`),
  KEY `alarm_escalation_escalationlevel_bcdd1c1a` (`service_data_source_id`),
  CONSTRAINT `device_type_id_refs_id_9fc6e07a` FOREIGN KEY (`device_type_id`) REFERENCES `device_devicetype` (`id`),
  CONSTRAINT `organization_id_refs_id_c696e307` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `service_data_source_id_refs_id_f62cda5b` FOREIGN KEY (`service_data_source_id`) REFERENCES `service_servicedatasource` (`id`),
  CONSTRAINT `service_id_refs_id_a2f17a90` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alarm_escalation_escalationstatus`
--

DROP TABLE IF EXISTS `alarm_escalation_escalationstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alarm_escalation_escalationstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `organization_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `service_data_source_id` int(11) NOT NULL,
  `ip` char(15) NOT NULL,
  `l1_email_status` int(11) NOT NULL,
  `l1_phone_status` int(11) NOT NULL,
  `l2_email_status` int(11) NOT NULL,
  `l2_phone_status` int(11) NOT NULL,
  `l3_email_status` int(11) NOT NULL,
  `l3_phone_status` int(11) NOT NULL,
  `l4_email_status` int(11) NOT NULL,
  `l4_phone_status` int(11) NOT NULL,
  `l5_email_status` int(11) NOT NULL,
  `l5_phone_status` int(11) NOT NULL,
  `l6_email_status` int(11) NOT NULL,
  `l6_phone_status` int(11) NOT NULL,
  `l7_email_status` int(11) NOT NULL,
  `l7_phone_status` int(11) NOT NULL,
  `status_since` datetime NOT NULL,
  `severity` varchar(20) NOT NULL,
  `old_status` int(11) NOT NULL,
  `new_status` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `alarm_escalation_escalationstatus_de772da3` (`organization_id`),
  KEY `alarm_escalation_escalationstatus_b6860804` (`device_id`),
  KEY `alarm_escalation_escalationstatus_91a0ac17` (`service_id`),
  KEY `alarm_escalation_escalationstatus_bcdd1c1a` (`service_data_source_id`),
  CONSTRAINT `device_id_refs_id_c5ead8ca` FOREIGN KEY (`device_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `organization_id_refs_id_2afd4188` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `service_data_source_id_refs_id_d02338ba` FOREIGN KEY (`service_data_source_id`) REFERENCES `service_servicedatasource` (`id`),
  CONSTRAINT `service_id_refs_id_74e9e12a` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=502 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `capacity_management_backhaulcapacitystatus`
--

DROP TABLE IF EXISTS `capacity_management_backhaulcapacitystatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `capacity_management_backhaulcapacitystatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `backhaul_id` int(11) NOT NULL,
  `basestation_id` int(11) NOT NULL,
  `bh_port_name` varchar(64) DEFAULT NULL,
  `backhaul_capacity` double NOT NULL,
  `current_in_per` double NOT NULL,
  `current_in_val` double NOT NULL,
  `avg_in_per` double NOT NULL,
  `avg_in_val` double NOT NULL,
  `peak_in_per` double NOT NULL,
  `peak_in_val` double NOT NULL,
  `peak_in_timestamp` int(11) NOT NULL,
  `current_out_per` double NOT NULL,
  `current_out_val` double NOT NULL,
  `avg_out_per` double NOT NULL,
  `avg_out_val` double NOT NULL,
  `peak_out_per` double NOT NULL,
  `peak_out_val` double NOT NULL,
  `peak_out_timestamp` int(11) NOT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `age` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `capacity_management_backhaulcapacitystatus_f4d00402` (`backhaul_id`),
  KEY `capacity_management_backhaulcapacitystatus_91731efc` (`basestation_id`),
  KEY `capacity_management_backhaulcapacitystatus_685bf038` (`bh_port_name`),
  KEY `capacity_management_backhaulcapacitystatus_996f8b64` (`sys_timestamp`),
  KEY `capacity_management_backhaulcapacitystatus_de772da3` (`organization_id`),
  CONSTRAINT `backhaul_id_refs_id_55fa1dcb` FOREIGN KEY (`backhaul_id`) REFERENCES `inventory_backhaul` (`id`),
  CONSTRAINT `basestation_id_refs_id_5fd037cf` FOREIGN KEY (`basestation_id`) REFERENCES `inventory_basestation` (`id`),
  CONSTRAINT `organization_id_refs_id_52c19515` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `capacity_management_sectorcapacitystatus`
--

DROP TABLE IF EXISTS `capacity_management_sectorcapacitystatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `capacity_management_sectorcapacitystatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sector_id` int(11) NOT NULL,
  `sector_sector_id` varchar(64) DEFAULT NULL,
  `sector_capacity` double NOT NULL,
  `sector_capacity_in` double NOT NULL,
  `sector_capacity_out` double NOT NULL,
  `current_in_per` double NOT NULL,
  `current_in_val` double NOT NULL,
  `avg_in_per` double NOT NULL,
  `avg_in_val` double NOT NULL,
  `peak_in_per` double NOT NULL,
  `peak_in_val` double NOT NULL,
  `peak_in_timestamp` int(11) NOT NULL,
  `current_out_per` double NOT NULL,
  `current_out_val` double NOT NULL,
  `avg_out_per` double NOT NULL,
  `avg_out_val` double NOT NULL,
  `peak_out_per` double NOT NULL,
  `peak_out_val` double NOT NULL,
  `peak_out_timestamp` int(11) NOT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `age` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sector_sector_id` (`sector_sector_id`),
  KEY `capacity_management_sectorcapacitystatus_663ed8c9` (`sector_id`),
  KEY `capacity_management_sectorcapacitystatus_996f8b64` (`sys_timestamp`),
  KEY `capacity_management_sectorcapacitystatus_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_834df252` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `sector_id_refs_id_165a19df` FOREIGN KEY (`sector_id`) REFERENCES `inventory_sector` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `celery_taskmeta`
--

DROP TABLE IF EXISTS `celery_taskmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `celery_taskmeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` varchar(255) NOT NULL,
  `status` varchar(50) NOT NULL,
  `result` longtext,
  `date_done` datetime NOT NULL,
  `traceback` longtext,
  `hidden` tinyint(1) NOT NULL,
  `meta` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`),
  KEY `celery_taskmeta_2ff6b945` (`hidden`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `celery_tasksetmeta`
--

DROP TABLE IF EXISTS `celery_tasksetmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `celery_tasksetmeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taskset_id` varchar(255) NOT NULL,
  `result` longtext NOT NULL,
  `date_done` datetime NOT NULL,
  `hidden` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `taskset_id` (`taskset_id`),
  KEY `celery_tasksetmeta_2ff6b945` (`hidden`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clear_alarms`
--

DROP TABLE IF EXISTS `clear_alarms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clear_alarms` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `device_name` varchar(128) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `device_type` varchar(50) DEFAULT NULL,
  `device_technology` varchar(50) DEFAULT NULL,
  `device_vendor` varchar(50) DEFAULT NULL,
  `device_model` varchar(50) DEFAULT NULL,
  `trapoid` varchar(100) DEFAULT NULL,
  `eventname` varchar(100) DEFAULT NULL,
  `eventno` varchar(50) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `uptime` varchar(20) DEFAULT NULL,
  `traptime` varchar(30) DEFAULT NULL,
  `component_id` varchar(20) DEFAULT NULL,
  `component_name` varchar(50) DEFAULT NULL,
  `age` int(10) unsigned DEFAULT NULL,
  `description` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13909 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `command_command`
--

DROP TABLE IF EXISTS `command_command`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `command_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(100) NOT NULL,
  `command_line` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `current_alarms`
--

DROP TABLE IF EXISTS `current_alarms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `current_alarms` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `device_name` varchar(128) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `device_type` varchar(50) DEFAULT NULL,
  `device_technology` varchar(50) DEFAULT NULL,
  `device_vendor` varchar(50) DEFAULT NULL,
  `device_model` varchar(50) DEFAULT NULL,
  `trapoid` varchar(100) DEFAULT NULL,
  `eventname` varchar(100) DEFAULT NULL,
  `eventno` varchar(50) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `uptime` varchar(20) DEFAULT NULL,
  `traptime` varchar(30) DEFAULT NULL,
  `component_id` varchar(20) DEFAULT NULL,
  `component_name` varchar(50) DEFAULT NULL,
  `age` int(10) unsigned DEFAULT NULL,
  `description` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9152 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardrangestatusdaily`
--

DROP TABLE IF EXISTS `dashboard_dashboardrangestatusdaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardrangestatusdaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `range1` int(11) NOT NULL,
  `range2` int(11) NOT NULL,
  `range3` int(11) NOT NULL,
  `range4` int(11) NOT NULL,
  `range5` int(11) NOT NULL,
  `range6` int(11) NOT NULL,
  `range7` int(11) NOT NULL,
  `range8` int(11) NOT NULL,
  `range9` int(11) NOT NULL,
  `range10` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardrangestatusdaily_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardrangestatusdaily_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardrangestatusdaily_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardrangestatusdaily_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_68e4d8a8` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardrangestatushourly`
--

DROP TABLE IF EXISTS `dashboard_dashboardrangestatushourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardrangestatushourly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `range1` int(11) NOT NULL,
  `range2` int(11) NOT NULL,
  `range3` int(11) NOT NULL,
  `range4` int(11) NOT NULL,
  `range5` int(11) NOT NULL,
  `range6` int(11) NOT NULL,
  `range7` int(11) NOT NULL,
  `range8` int(11) NOT NULL,
  `range9` int(11) NOT NULL,
  `range10` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardrangestatushourly_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardrangestatushourly_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardrangestatushourly_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardrangestatushourly_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_6ab26de7` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardrangestatusmonthly`
--

DROP TABLE IF EXISTS `dashboard_dashboardrangestatusmonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardrangestatusmonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `range1` int(11) NOT NULL,
  `range2` int(11) NOT NULL,
  `range3` int(11) NOT NULL,
  `range4` int(11) NOT NULL,
  `range5` int(11) NOT NULL,
  `range6` int(11) NOT NULL,
  `range7` int(11) NOT NULL,
  `range8` int(11) NOT NULL,
  `range9` int(11) NOT NULL,
  `range10` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardrangestatusmonthly_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardrangestatusmonthly_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardrangestatusmonthly_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardrangestatusmonthly_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_2ad6fdaa` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardrangestatustimely`
--

DROP TABLE IF EXISTS `dashboard_dashboardrangestatustimely`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardrangestatustimely` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `range1` int(11) NOT NULL,
  `range2` int(11) NOT NULL,
  `range3` int(11) NOT NULL,
  `range4` int(11) NOT NULL,
  `range5` int(11) NOT NULL,
  `range6` int(11) NOT NULL,
  `range7` int(11) NOT NULL,
  `range8` int(11) NOT NULL,
  `range9` int(11) NOT NULL,
  `range10` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardrangestatustimely_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardrangestatustimely_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardrangestatustimely_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardrangestatustimely_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_cbba02db` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardrangestatusweekly`
--

DROP TABLE IF EXISTS `dashboard_dashboardrangestatusweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardrangestatusweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `range1` int(11) NOT NULL,
  `range2` int(11) NOT NULL,
  `range3` int(11) NOT NULL,
  `range4` int(11) NOT NULL,
  `range5` int(11) NOT NULL,
  `range6` int(11) NOT NULL,
  `range7` int(11) NOT NULL,
  `range8` int(11) NOT NULL,
  `range9` int(11) NOT NULL,
  `range10` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardrangestatusweekly_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardrangestatusweekly_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardrangestatusweekly_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardrangestatusweekly_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_38689b28` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardrangestatusyearly`
--

DROP TABLE IF EXISTS `dashboard_dashboardrangestatusyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardrangestatusyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `range1` int(11) NOT NULL,
  `range2` int(11) NOT NULL,
  `range3` int(11) NOT NULL,
  `range4` int(11) NOT NULL,
  `range5` int(11) NOT NULL,
  `range6` int(11) NOT NULL,
  `range7` int(11) NOT NULL,
  `range8` int(11) NOT NULL,
  `range9` int(11) NOT NULL,
  `range10` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardrangestatusyearly_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardrangestatusyearly_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardrangestatusyearly_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardrangestatusyearly_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_8a2d2597` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardsetting`
--

DROP TABLE IF EXISTS `dashboard_dashboardsetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardsetting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `page_name` varchar(30) NOT NULL,
  `technology_id` int(11) DEFAULT NULL,
  `is_bh` tinyint(1) NOT NULL,
  `name` varchar(250) NOT NULL,
  `dashboard_type` varchar(3) NOT NULL,
  `range1_start` varchar(20) DEFAULT NULL,
  `range1_end` varchar(20) DEFAULT NULL,
  `range1_color_hex_value` varchar(100) DEFAULT NULL,
  `range2_start` varchar(20) DEFAULT NULL,
  `range2_end` varchar(20) DEFAULT NULL,
  `range2_color_hex_value` varchar(100) DEFAULT NULL,
  `range3_start` varchar(20) DEFAULT NULL,
  `range3_end` varchar(20) DEFAULT NULL,
  `range3_color_hex_value` varchar(100) DEFAULT NULL,
  `range4_start` varchar(20) DEFAULT NULL,
  `range4_end` varchar(20) DEFAULT NULL,
  `range4_color_hex_value` varchar(100) DEFAULT NULL,
  `range5_start` varchar(20) DEFAULT NULL,
  `range5_end` varchar(20) DEFAULT NULL,
  `range5_color_hex_value` varchar(100) DEFAULT NULL,
  `range6_start` varchar(20) DEFAULT NULL,
  `range6_end` varchar(20) DEFAULT NULL,
  `range6_color_hex_value` varchar(100) DEFAULT NULL,
  `range7_start` varchar(20) DEFAULT NULL,
  `range7_end` varchar(20) DEFAULT NULL,
  `range7_color_hex_value` varchar(100) DEFAULT NULL,
  `range8_start` varchar(20) DEFAULT NULL,
  `range8_end` varchar(20) DEFAULT NULL,
  `range8_color_hex_value` varchar(100) DEFAULT NULL,
  `range9_start` varchar(20) DEFAULT NULL,
  `range9_end` varchar(20) DEFAULT NULL,
  `range9_color_hex_value` varchar(100) DEFAULT NULL,
  `range10_start` varchar(20) DEFAULT NULL,
  `range10_end` varchar(20) DEFAULT NULL,
  `range10_color_hex_value` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`,`page_name`,`technology_id`,`is_bh`),
  KEY `dashboard_dashboardsetting_98427941` (`technology_id`),
  CONSTRAINT `technology_id_refs_id_a155724a` FOREIGN KEY (`technology_id`) REFERENCES `device_devicetechnology` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardseveritystatusdaily`
--

DROP TABLE IF EXISTS `dashboard_dashboardseveritystatusdaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardseveritystatusdaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `warning` int(11) NOT NULL,
  `critical` int(11) NOT NULL,
  `ok` int(11) NOT NULL,
  `down` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardseveritystatusdaily_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardseveritystatusdaily_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardseveritystatusdaily_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardseveritystatusdaily_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_5e197fe4` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardseveritystatushourly`
--

DROP TABLE IF EXISTS `dashboard_dashboardseveritystatushourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardseveritystatushourly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `warning` int(11) NOT NULL,
  `critical` int(11) NOT NULL,
  `ok` int(11) NOT NULL,
  `down` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardseveritystatushourly_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardseveritystatushourly_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardseveritystatushourly_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardseveritystatushourly_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_246ec3bf` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardseveritystatusmonthly`
--

DROP TABLE IF EXISTS `dashboard_dashboardseveritystatusmonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardseveritystatusmonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `warning` int(11) NOT NULL,
  `critical` int(11) NOT NULL,
  `ok` int(11) NOT NULL,
  `down` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardseveritystatusmonthly_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardseveritystatusmonthly_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardseveritystatusmonthly_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardseveritystatusmonthly_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_7ab24bb8` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardseveritystatustimely`
--

DROP TABLE IF EXISTS `dashboard_dashboardseveritystatustimely`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardseveritystatustimely` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `warning` int(11) NOT NULL,
  `critical` int(11) NOT NULL,
  `ok` int(11) NOT NULL,
  `down` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardseveritystatustimely_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardseveritystatustimely_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardseveritystatustimely_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardseveritystatustimely_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_00a49223` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardseveritystatusweekly`
--

DROP TABLE IF EXISTS `dashboard_dashboardseveritystatusweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardseveritystatusweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `warning` int(11) NOT NULL,
  `critical` int(11) NOT NULL,
  `ok` int(11) NOT NULL,
  `down` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardseveritystatusweekly_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardseveritystatusweekly_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardseveritystatusweekly_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardseveritystatusweekly_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_7fd88448` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dashboardseveritystatusyearly`
--

DROP TABLE IF EXISTS `dashboard_dashboardseveritystatusyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dashboardseveritystatusyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dashboard_name` varchar(100) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `processed_for` datetime NOT NULL,
  `organization_id` int(11) NOT NULL,
  `warning` int(11) NOT NULL,
  `critical` int(11) NOT NULL,
  `ok` int(11) NOT NULL,
  `down` int(11) NOT NULL,
  `unknown` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dashboardseveritystatusyearly_af37e03a` (`dashboard_name`),
  KEY `dashboard_dashboardseveritystatusyearly_4d7fdddd` (`device_name`),
  KEY `dashboard_dashboardseveritystatusyearly_8ec876c9` (`reference_name`),
  KEY `dashboard_dashboardseveritystatusyearly_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_3cdadca9` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_dfrprocessed`
--

DROP TABLE IF EXISTS `dashboard_dfrprocessed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_dfrprocessed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `processed_for_id` int(11) NOT NULL,
  `processed_on` date NOT NULL,
  `processed_key` varchar(128) NOT NULL,
  `processed_value` varchar(64) NOT NULL,
  `processed_report_path` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_dfrprocessed_68926e24` (`processed_for_id`),
  CONSTRAINT `processed_for_id_refs_id_d7c7985f` FOREIGN KEY (`processed_for_id`) REFERENCES `dashboard_mfrdfrreports` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_mfrcausecode`
--

DROP TABLE IF EXISTS `dashboard_mfrcausecode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_mfrcausecode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `processed_for_id` int(11) NOT NULL,
  `processed_on` date NOT NULL,
  `processed_key` varchar(128) NOT NULL,
  `processed_value` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_mfrcausecode_68926e24` (`processed_for_id`),
  CONSTRAINT `processed_for_id_refs_id_34a4c529` FOREIGN KEY (`processed_for_id`) REFERENCES `dashboard_mfrdfrreports` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_mfrdfrreports`
--

DROP TABLE IF EXISTS `dashboard_mfrdfrreports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_mfrdfrreports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `type` varchar(8) NOT NULL,
  `is_processed` int(11) NOT NULL,
  `process_for` date NOT NULL,
  `upload_to` varchar(512) NOT NULL,
  `absolute_path` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_mfrprocessed`
--

DROP TABLE IF EXISTS `dashboard_mfrprocessed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_mfrprocessed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `processed_for_id` int(11) NOT NULL,
  `processed_on` date NOT NULL,
  `processed_key` varchar(128) NOT NULL,
  `processed_value` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_mfrprocessed_68926e24` (`processed_for_id`),
  CONSTRAINT `processed_for_id_refs_id_6a528ebb` FOREIGN KEY (`processed_for_id`) REFERENCES `dashboard_mfrdfrreports` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_city`
--

DROP TABLE IF EXISTS `device_city`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_city` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `city_name` varchar(250) NOT NULL,
  `state_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_city_5654bf12` (`state_id`),
  CONSTRAINT `state_id_refs_id_443f5d4c` FOREIGN KEY (`state_id`) REFERENCES `device_state` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_country`
--

DROP TABLE IF EXISTS `device_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_country` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `country_name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  `machine_id` int(11) DEFAULT NULL,
  `site_instance_id` int(11) DEFAULT NULL,
  `organization_id` int(11) NOT NULL,
  `device_technology` int(11) NOT NULL,
  `device_vendor` int(11) NOT NULL,
  `device_model` int(11) NOT NULL,
  `device_type` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `ip_address` char(15) NOT NULL,
  `mac_address` varchar(100) DEFAULT NULL,
  `netmask` char(15) DEFAULT NULL,
  `gateway` char(15) DEFAULT NULL,
  `dhcp_state` varchar(200) NOT NULL,
  `host_priority` varchar(200) NOT NULL,
  `host_state` varchar(200) NOT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `timezone` varchar(100) NOT NULL,
  `country_id` int(11) DEFAULT NULL,
  `state_id` int(11) DEFAULT NULL,
  `city_id` int(11) DEFAULT NULL,
  `address` longtext,
  `description` longtext,
  `is_deleted` int(11) NOT NULL,
  `is_added_to_nms` int(11) NOT NULL,
  `is_monitored_on_nms` int(11) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`),
  UNIQUE KEY `ip_address` (`ip_address`),
  KEY `device_device_dbaea34e` (`machine_id`),
  KEY `device_device_a74b81df` (`site_instance_id`),
  KEY `device_device_de772da3` (`organization_id`),
  KEY `device_device_410d0aac` (`parent_id`),
  KEY `device_device_d860be3c` (`country_id`),
  KEY `device_device_5654bf12` (`state_id`),
  KEY `device_device_b376980e` (`city_id`),
  KEY `device_device_329f6fb3` (`lft`),
  KEY `device_device_e763210f` (`rght`),
  KEY `device_device_ba470c4a` (`tree_id`),
  KEY `device_device_20e079f4` (`level`),
  CONSTRAINT `city_id_refs_id_114f58ea` FOREIGN KEY (`city_id`) REFERENCES `device_city` (`id`),
  CONSTRAINT `country_id_refs_id_c294854b` FOREIGN KEY (`country_id`) REFERENCES `device_country` (`id`),
  CONSTRAINT `machine_id_refs_id_b0012bcd` FOREIGN KEY (`machine_id`) REFERENCES `machine_machine` (`id`),
  CONSTRAINT `organization_id_refs_id_0a0a8b43` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `parent_id_refs_id_0679e3c1` FOREIGN KEY (`parent_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `site_instance_id_refs_id_7810d5e5` FOREIGN KEY (`site_instance_id`) REFERENCES `site_instance_siteinstance` (`id`),
  CONSTRAINT `state_id_refs_id_8499bec1` FOREIGN KEY (`state_id`) REFERENCES `device_state` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_device_ports`
--

DROP TABLE IF EXISTS `device_device_ports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_device_ports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `deviceport_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_id` (`device_id`,`deviceport_id`),
  KEY `device_device_ports_b6860804` (`device_id`),
  KEY `device_device_ports_4475dc69` (`deviceport_id`),
  CONSTRAINT `deviceport_id_refs_id_e8f71d1a` FOREIGN KEY (`deviceport_id`) REFERENCES `device_deviceport` (`id`),
  CONSTRAINT `device_id_refs_id_898db13c` FOREIGN KEY (`device_id`) REFERENCES `device_device` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_devicefrequency`
--

DROP TABLE IF EXISTS `device_devicefrequency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicefrequency` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(50) NOT NULL,
  `color_hex_value` varchar(100) NOT NULL,
  `frequency_radius` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_deviceport`
--

DROP TABLE IF EXISTS `device_deviceport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_deviceport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(200) NOT NULL,
  `value` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_devicesynchistory`
--

DROP TABLE IF EXISTS `device_devicesynchistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicesynchistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` int(11) DEFAULT NULL,
  `message` longtext,
  `description` longtext,
  `sync_by` varchar(100) DEFAULT NULL,
  `added_on` datetime DEFAULT NULL,
  `completed_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_devicetechnology`
--

DROP TABLE IF EXISTS `device_devicetechnology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetechnology` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_devicetype`
--

DROP TABLE IF EXISTS `device_devicetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `alias` varchar(200) NOT NULL,
  `packets` int(11) DEFAULT NULL,
  `timeout` int(11) DEFAULT NULL,
  `normal_check_interval` int(11) DEFAULT NULL,
  `rta_warning` int(11) DEFAULT NULL,
  `rta_critical` int(11) DEFAULT NULL,
  `pl_warning` int(11) DEFAULT NULL,
  `pl_critical` int(11) DEFAULT NULL,
  `agent_tag` varchar(200) DEFAULT NULL,
  `device_icon` varchar(100) NOT NULL,
  `device_gmap_icon` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `device_devicetypefields`
--

DROP TABLE IF EXISTS `device_devicetypefields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetypefields` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `field_name` varchar(100) NOT NULL,
  `field_display_name` varchar(200) NOT NULL,
  `device_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_devicetypefields_d8be8594` (`device_type_id`),
  CONSTRAINT `device_type_id_refs_id_45058c1e` FOREIGN KEY (`device_type_id`) REFERENCES `device_devicetype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `device_devicetypeservice`
--

DROP TABLE IF EXISTS `device_devicetypeservice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetypeservice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_type_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `parameter_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_devicetypeservice_d8be8594` (`device_type_id`),
  KEY `device_devicetypeservice_91a0ac17` (`service_id`),
  KEY `device_devicetypeservice_1d1f7f60` (`parameter_id`),
  CONSTRAINT `device_type_id_refs_id_3ae0af56` FOREIGN KEY (`device_type_id`) REFERENCES `device_devicetype` (`id`),
  CONSTRAINT `parameter_id_refs_id_6d70053d` FOREIGN KEY (`parameter_id`) REFERENCES `service_serviceparameters` (`id`),
  CONSTRAINT `service_id_refs_id_8c22d566` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_devicetypeservicedatasource`
--

DROP TABLE IF EXISTS `device_devicetypeservicedatasource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicetypeservicedatasource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_type_service_id` int(11) NOT NULL,
  `service_data_sources_id` int(11) NOT NULL,
  `warning` varchar(255) DEFAULT NULL,
  `critical` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_devicetypeservicedatasource_a9926bce` (`device_type_service_id`),
  KEY `device_devicetypeservicedatasource_672804af` (`service_data_sources_id`),
  CONSTRAINT `device_type_service_id_refs_id_475c0fb4` FOREIGN KEY (`device_type_service_id`) REFERENCES `device_devicetypeservice` (`id`),
  CONSTRAINT `service_data_sources_id_refs_id_e602c1ab` FOREIGN KEY (`service_data_sources_id`) REFERENCES `service_servicedatasource` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_devicevendor`
--

DROP TABLE IF EXISTS `device_devicevendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_devicevendor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `alias` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_state`
--

DROP TABLE IF EXISTS `device_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_state` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `state_name` varchar(200) NOT NULL,
  `country_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_state_d860be3c` (`country_id`),
  CONSTRAINT `country_id_refs_id_98c8d32c` FOREIGN KEY (`country_id`) REFERENCES `device_country` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device_stategeoinfo`
--

DROP TABLE IF EXISTS `device_stategeoinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_stategeoinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `state_id` int(11) NOT NULL,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device_stategeoinfo_5654bf12` (`state_id`),
  CONSTRAINT `state_id_refs_id_52db8c3f` FOREIGN KEY (`state_id`) REFERENCES `device_state` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `devicevisualization_gispointtool`
--

DROP TABLE IF EXISTS `devicevisualization_gispointtool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devicevisualization_gispointtool` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` longtext,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `icon_url` varchar(255) NOT NULL,
  `connected_point_type` varchar(255) DEFAULT NULL,
  `connected_point_info` longtext,
  `connected_lat` double DEFAULT NULL,
  `connected_lon` double DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `devicevisualization_kmzreport`
--

DROP TABLE IF EXISTS `devicevisualization_kmzreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devicevisualization_kmzreport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `filename` varchar(300) NOT NULL,
  `added_on` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `is_public` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `devicevisualization_kmzreport_6340c63c` (`user_id`),
  CONSTRAINT `user_id_refs_user_ptr_id_5897f1c4` FOREIGN KEY (`user_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=168 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `djcelery_crontabschedule`
--

DROP TABLE IF EXISTS `djcelery_crontabschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_crontabschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `minute` varchar(64) NOT NULL,
  `hour` varchar(64) NOT NULL,
  `day_of_week` varchar(64) NOT NULL,
  `day_of_month` varchar(64) NOT NULL,
  `month_of_year` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `djcelery_intervalschedule`
--

DROP TABLE IF EXISTS `djcelery_intervalschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_intervalschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `every` int(11) NOT NULL,
  `period` varchar(24) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `djcelery_periodictask`
--

DROP TABLE IF EXISTS `djcelery_periodictask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_periodictask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `task` varchar(200) NOT NULL,
  `interval_id` int(11) DEFAULT NULL,
  `crontab_id` int(11) DEFAULT NULL,
  `args` longtext NOT NULL,
  `kwargs` longtext NOT NULL,
  `queue` varchar(200) DEFAULT NULL,
  `exchange` varchar(200) DEFAULT NULL,
  `routing_key` varchar(200) DEFAULT NULL,
  `expires` datetime DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL,
  `last_run_at` datetime DEFAULT NULL,
  `total_run_count` int(10) unsigned NOT NULL,
  `date_changed` datetime NOT NULL,
  `description` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `djcelery_periodictask_8905f60d` (`interval_id`),
  KEY `djcelery_periodictask_7280124f` (`crontab_id`),
  CONSTRAINT `crontab_id_refs_id_286da0d1` FOREIGN KEY (`crontab_id`) REFERENCES `djcelery_crontabschedule` (`id`),
  CONSTRAINT `interval_id_refs_id_1829f358` FOREIGN KEY (`interval_id`) REFERENCES `djcelery_intervalschedule` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `djcelery_periodictasks`
--

DROP TABLE IF EXISTS `djcelery_periodictasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_periodictasks` (
  `ident` smallint(6) NOT NULL,
  `last_update` datetime NOT NULL,
  PRIMARY KEY (`ident`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `djcelery_taskstate`
--

DROP TABLE IF EXISTS `djcelery_taskstate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_taskstate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `state` varchar(64) NOT NULL,
  `task_id` varchar(36) NOT NULL,
  `name` varchar(200) DEFAULT NULL,
  `tstamp` datetime NOT NULL,
  `args` longtext,
  `kwargs` longtext,
  `eta` datetime DEFAULT NULL,
  `expires` datetime DEFAULT NULL,
  `result` longtext,
  `traceback` longtext,
  `runtime` double DEFAULT NULL,
  `retries` int(11) NOT NULL,
  `worker_id` int(11) DEFAULT NULL,
  `hidden` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`),
  KEY `djcelery_taskstate_5654bf12` (`state`),
  KEY `djcelery_taskstate_4da47e07` (`name`),
  KEY `djcelery_taskstate_abaacd02` (`tstamp`),
  KEY `djcelery_taskstate_cac6a03d` (`worker_id`),
  KEY `djcelery_taskstate_2ff6b945` (`hidden`),
  CONSTRAINT `worker_id_refs_id_6fd8ce95` FOREIGN KEY (`worker_id`) REFERENCES `djcelery_workerstate` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `djcelery_workerstate`
--

DROP TABLE IF EXISTS `djcelery_workerstate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_workerstate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(255) NOT NULL,
  `last_heartbeat` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`),
  KEY `djcelery_workerstate_11e400ef` (`last_heartbeat`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `download_center_processedreportdetails`
--

DROP TABLE IF EXISTS `download_center_processedreportdetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `download_center_processedreportdetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `report_name` varchar(255) NOT NULL,
  `path` varchar(512) NOT NULL,
  `created_on` datetime NOT NULL,
  `report_date` datetime DEFAULT NULL,
  `organization_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `download_center_reportsettings`
--

DROP TABLE IF EXISTS `download_center_reportsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `download_center_reportsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `page_name` varchar(128) NOT NULL,
  `report_name` varchar(255) NOT NULL,
  `report_frequency` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `history_alarms`
--

DROP TABLE IF EXISTS `history_alarms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `history_alarms` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `device_name` varchar(128) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `device_type` varchar(50) DEFAULT NULL,
  `device_technology` varchar(50) DEFAULT NULL,
  `device_vendor` varchar(50) DEFAULT NULL,
  `device_model` varchar(50) DEFAULT NULL,
  `trapoid` varchar(100) DEFAULT NULL,
  `eventname` varchar(100) DEFAULT NULL,
  `eventno` varchar(50) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `uptime` varchar(20) DEFAULT NULL,
  `traptime` varchar(30) DEFAULT NULL,
  `component_id` varchar(20) DEFAULT NULL,
  `component_name` varchar(50) DEFAULT NULL,
  `age` int(10) unsigned DEFAULT NULL,
  `description` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=947735 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_antenna`
--

DROP TABLE IF EXISTS `inventory_antenna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_antenna` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `antenna_type` varchar(100) DEFAULT NULL,
  `height` double DEFAULT NULL,
  `polarization` varchar(50) DEFAULT NULL,
  `tilt` double DEFAULT NULL,
  `gain` double DEFAULT NULL,
  `mount_type` varchar(100) DEFAULT NULL,
  `beam_width` double DEFAULT NULL,
  `azimuth_angle` double DEFAULT NULL,
  `reflector` varchar(100) DEFAULT NULL,
  `splitter_installed` varchar(4) DEFAULT NULL,
  `sync_splitter_used` varchar(4) DEFAULT NULL,
  `make_of_antenna` varchar(40) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_antenna_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_677e2570` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_backhaul`
--

DROP TABLE IF EXISTS `inventory_backhaul`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_backhaul` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `bh_configured_on_id` int(11) DEFAULT NULL,
  `bh_port_name` varchar(40) DEFAULT NULL,
  `bh_port` int(11) DEFAULT NULL,
  `bh_type` varchar(250) DEFAULT NULL,
  `bh_switch_id` int(11) DEFAULT NULL,
  `switch_port_name` varchar(40) DEFAULT NULL,
  `switch_port` int(11) DEFAULT NULL,
  `pop_id` int(11) DEFAULT NULL,
  `pop_port_name` varchar(40) DEFAULT NULL,
  `pop_port` int(11) DEFAULT NULL,
  `aggregator_id` int(11) DEFAULT NULL,
  `aggregator_port_name` varchar(40) DEFAULT NULL,
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
  KEY `inventory_backhaul_de772da3` (`organization_id`),
  KEY `inventory_backhaul_366352e4` (`bh_configured_on_id`),
  KEY `inventory_backhaul_af705a25` (`bh_switch_id`),
  KEY `inventory_backhaul_25fe84e8` (`pop_id`),
  KEY `inventory_backhaul_3fedd201` (`aggregator_id`),
  CONSTRAINT `aggregator_id_refs_id_1a6887f3` FOREIGN KEY (`aggregator_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `bh_configured_on_id_refs_id_1a6887f3` FOREIGN KEY (`bh_configured_on_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `bh_switch_id_refs_id_1a6887f3` FOREIGN KEY (`bh_switch_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `organization_id_refs_id_82871406` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `pop_id_refs_id_1a6887f3` FOREIGN KEY (`pop_id`) REFERENCES `device_device` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_basestation`
--

DROP TABLE IF EXISTS `inventory_basestation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_basestation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `bs_site_id` varchar(250) DEFAULT NULL,
  `bs_site_type` varchar(100) DEFAULT NULL,
  `bs_switch_id` int(11) DEFAULT NULL,
  `backhaul_id` int(11) DEFAULT NULL,
  `bh_port_name` varchar(40) DEFAULT NULL,
  `bh_port` int(11) DEFAULT NULL,
  `bh_capacity` int(11) DEFAULT NULL,
  `bs_type` varchar(40) DEFAULT NULL,
  `bh_bso` varchar(40) DEFAULT NULL,
  `hssu_used` varchar(40) DEFAULT NULL,
  `hssu_port` varchar(40) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `infra_provider` varchar(100) DEFAULT NULL,
  `gps_type` varchar(100) DEFAULT NULL,
  `building_height` double DEFAULT NULL,
  `tower_height` double DEFAULT NULL,
  `country_id` int(11) DEFAULT NULL,
  `state_id` int(11) DEFAULT NULL,
  `city_id` int(11) DEFAULT NULL,
  `address` longtext,
  `maintenance_status` varchar(250) DEFAULT NULL,
  `provisioning_status` varchar(250) DEFAULT NULL,
  `tag1` varchar(60) DEFAULT NULL,
  `tag2` varchar(60) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_basestation_de772da3` (`organization_id`),
  KEY `inventory_basestation_2d94f56c` (`bs_switch_id`),
  KEY `inventory_basestation_f4d00402` (`backhaul_id`),
  KEY `inventory_basestation_d860be3c` (`country_id`),
  KEY `inventory_basestation_5654bf12` (`state_id`),
  KEY `inventory_basestation_b376980e` (`city_id`),
  CONSTRAINT `backhaul_id_refs_id_b88aec53` FOREIGN KEY (`backhaul_id`) REFERENCES `inventory_backhaul` (`id`),
  CONSTRAINT `bs_switch_id_refs_id_519fe049` FOREIGN KEY (`bs_switch_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `city_id_refs_id_17679a0a` FOREIGN KEY (`city_id`) REFERENCES `device_city` (`id`),
  CONSTRAINT `country_id_refs_id_4e09c982` FOREIGN KEY (`country_id`) REFERENCES `device_country` (`id`),
  CONSTRAINT `organization_id_refs_id_75df2c48` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `state_id_refs_id_4a3e1918` FOREIGN KEY (`state_id`) REFERENCES `device_state` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_circuit`
--

DROP TABLE IF EXISTS `inventory_circuit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_circuit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `circuit_type` varchar(250) DEFAULT NULL,
  `circuit_id` varchar(250) DEFAULT NULL,
  `sector_id` int(11) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `sub_station_id` int(11) DEFAULT NULL,
  `qos_bandwidth` double DEFAULT NULL,
  `dl_rssi_during_acceptance` varchar(100) DEFAULT NULL,
  `dl_cinr_during_acceptance` varchar(100) DEFAULT NULL,
  `jitter_value_during_acceptance` varchar(100) DEFAULT NULL,
  `throughput_during_acceptance` varchar(100) DEFAULT NULL,
  `date_of_acceptance` date DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_circuit_de772da3` (`organization_id`),
  KEY `inventory_circuit_663ed8c9` (`sector_id`),
  KEY `inventory_circuit_09847825` (`customer_id`),
  KEY `inventory_circuit_abc593bb` (`sub_station_id`),
  CONSTRAINT `customer_id_refs_id_eba5adb0` FOREIGN KEY (`customer_id`) REFERENCES `inventory_customer` (`id`),
  CONSTRAINT `organization_id_refs_id_619c1ddf` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `sector_id_refs_id_1b7c0cea` FOREIGN KEY (`sector_id`) REFERENCES `inventory_sector` (`id`),
  CONSTRAINT `sub_station_id_refs_id_eedc5892` FOREIGN KEY (`sub_station_id`) REFERENCES `inventory_substation` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_circuitl2report`
--

DROP TABLE IF EXISTS `inventory_circuitl2report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_circuitl2report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `file_name` varchar(512) NOT NULL,
  `added_on` datetime DEFAULT NULL,
  `user_id_id` int(11) NOT NULL,
  `circuit_id_id` int(11) NOT NULL,
  `is_public` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_circuitl2report_1ffdedc6` (`user_id_id`),
  KEY `inventory_circuitl2report_ad93c27b` (`circuit_id_id`),
  CONSTRAINT `circuit_id_id_refs_id_2eaf58d0` FOREIGN KEY (`circuit_id_id`) REFERENCES `inventory_circuit` (`id`),
  CONSTRAINT `user_id_id_refs_user_ptr_id_e9c46260` FOREIGN KEY (`user_id_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_customer`
--

DROP TABLE IF EXISTS `inventory_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `address` longtext,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_customer_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_cfbc7962` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_gisexceldownload`
--

DROP TABLE IF EXISTS `inventory_gisexceldownload`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_gisexceldownload` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file_path` varchar(250) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `base_stations` varchar(250) DEFAULT NULL,
  `description` longtext,
  `downloaded_by` varchar(100) DEFAULT NULL,
  `added_on` datetime DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_gisinventorybulkimport`
--

DROP TABLE IF EXISTS `inventory_gisinventorybulkimport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_gisinventorybulkimport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `original_filename` varchar(250) DEFAULT NULL,
  `valid_filename` varchar(250) DEFAULT NULL,
  `invalid_filename` varchar(250) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `sheet_name` varchar(100) DEFAULT NULL,
  `technology` varchar(40) DEFAULT NULL,
  `upload_status` int(11) DEFAULT NULL,
  `description` longtext,
  `uploaded_by` varchar(100) DEFAULT NULL,
  `added_on` datetime DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_iconsettings`
--

DROP TABLE IF EXISTS `inventory_iconsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_iconsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `upload_image` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_inventory`
--

DROP TABLE IF EXISTS `inventory_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_inventory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `user_group_id` int(11) NOT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_inventory_de772da3` (`organization_id`),
  KEY `inventory_inventory_1a56174b` (`user_group_id`),
  CONSTRAINT `organization_id_refs_id_a0b4675d` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `user_group_id_refs_id_e2f206a1` FOREIGN KEY (`user_group_id`) REFERENCES `user_group_usergroup` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_livepollingsettings`
--

DROP TABLE IF EXISTS `inventory_livepollingsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_livepollingsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `technology_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `data_source_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_livepollingsettings_98427941` (`technology_id`),
  KEY `inventory_livepollingsettings_91a0ac17` (`service_id`),
  KEY `inventory_livepollingsettings_24bd1ce3` (`data_source_id`),
  CONSTRAINT `data_source_id_refs_id_4e91c717` FOREIGN KEY (`data_source_id`) REFERENCES `service_servicedatasource` (`id`),
  CONSTRAINT `service_id_refs_id_0c771cdf` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`),
  CONSTRAINT `technology_id_refs_id_af0e147f` FOREIGN KEY (`technology_id`) REFERENCES `device_devicetechnology` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_pingthematicsettings`
--

DROP TABLE IF EXISTS `inventory_pingthematicsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_pingthematicsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `technology_id` int(11) NOT NULL,
  `service` varchar(250) NOT NULL,
  `data_source` varchar(250) NOT NULL,
  `range1_start` varchar(20) DEFAULT NULL,
  `range1_end` varchar(20) DEFAULT NULL,
  `range2_start` varchar(20) DEFAULT NULL,
  `range2_end` varchar(20) DEFAULT NULL,
  `range3_start` varchar(20) DEFAULT NULL,
  `range3_end` varchar(20) DEFAULT NULL,
  `range4_start` varchar(20) DEFAULT NULL,
  `range4_end` varchar(20) DEFAULT NULL,
  `range5_start` varchar(20) DEFAULT NULL,
  `range5_end` varchar(20) DEFAULT NULL,
  `range6_start` varchar(20) DEFAULT NULL,
  `range6_end` varchar(20) DEFAULT NULL,
  `range7_start` varchar(20) DEFAULT NULL,
  `range7_end` varchar(20) DEFAULT NULL,
  `range8_start` varchar(20) DEFAULT NULL,
  `range8_end` varchar(20) DEFAULT NULL,
  `range9_start` varchar(20) DEFAULT NULL,
  `range9_end` varchar(20) DEFAULT NULL,
  `range10_start` varchar(20) DEFAULT NULL,
  `range10_end` varchar(20) DEFAULT NULL,
  `icon_settings` longtext NOT NULL,
  `is_global` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_pingthematicsettings_98427941` (`technology_id`),
  CONSTRAINT `technology_id_refs_id_1d51bee6` FOREIGN KEY (`technology_id`) REFERENCES `device_devicetechnology` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_sector`
--

DROP TABLE IF EXISTS `inventory_sector`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_sector` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `sector_id` varchar(250) DEFAULT NULL,
  `base_station_id` int(11) DEFAULT NULL,
  `bs_technology_id` int(11) DEFAULT NULL,
  `sector_configured_on_id` int(11) DEFAULT NULL,
  `sector_configured_on_port_id` int(11) DEFAULT NULL,
  `antenna_id` int(11) DEFAULT NULL,
  `dr_site` varchar(150) DEFAULT NULL,
  `dr_configured_on_id` int(11) DEFAULT NULL,
  `mrc` varchar(4) DEFAULT NULL,
  `tx_power` double DEFAULT NULL,
  `rx_power` double DEFAULT NULL,
  `rf_bandwidth` double DEFAULT NULL,
  `frame_length` double DEFAULT NULL,
  `cell_radius` double DEFAULT NULL,
  `frequency_id` int(11) DEFAULT NULL,
  `planned_frequency` varchar(250) DEFAULT NULL,
  `modulation` varchar(250) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_sector_de772da3` (`organization_id`),
  KEY `inventory_sector_2ae13a96` (`base_station_id`),
  KEY `inventory_sector_b75ab1be` (`bs_technology_id`),
  KEY `inventory_sector_b01ef1b5` (`sector_configured_on_id`),
  KEY `inventory_sector_597d1d65` (`sector_configured_on_port_id`),
  KEY `inventory_sector_c42a47b3` (`antenna_id`),
  KEY `inventory_sector_bbb371be` (`dr_configured_on_id`),
  KEY `inventory_sector_80359b49` (`frequency_id`),
  CONSTRAINT `antenna_id_refs_id_17c7ec16` FOREIGN KEY (`antenna_id`) REFERENCES `inventory_antenna` (`id`),
  CONSTRAINT `base_station_id_refs_id_623a0db0` FOREIGN KEY (`base_station_id`) REFERENCES `inventory_basestation` (`id`),
  CONSTRAINT `bs_technology_id_refs_id_353403d2` FOREIGN KEY (`bs_technology_id`) REFERENCES `device_devicetechnology` (`id`),
  CONSTRAINT `dr_configured_on_id_refs_id_589ca1cf` FOREIGN KEY (`dr_configured_on_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `frequency_id_refs_id_ce9d28af` FOREIGN KEY (`frequency_id`) REFERENCES `device_devicefrequency` (`id`),
  CONSTRAINT `organization_id_refs_id_da99cdd1` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `sector_configured_on_id_refs_id_589ca1cf` FOREIGN KEY (`sector_configured_on_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `sector_configured_on_port_id_refs_id_52f2e9fd` FOREIGN KEY (`sector_configured_on_port_id`) REFERENCES `device_deviceport` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_substation`
--

DROP TABLE IF EXISTS `inventory_substation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_substation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `device_id` int(11) DEFAULT NULL,
  `antenna_id` int(11) DEFAULT NULL,
  `version` varchar(40) DEFAULT NULL,
  `serial_no` varchar(250) DEFAULT NULL,
  `building_height` double DEFAULT NULL,
  `tower_height` double DEFAULT NULL,
  `ethernet_extender` varchar(250) DEFAULT NULL,
  `cable_length` double DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `mac_address` varchar(100) DEFAULT NULL,
  `country_id` int(11) DEFAULT NULL,
  `state_id` int(11) DEFAULT NULL,
  `city_id` int(11) DEFAULT NULL,
  `address` longtext,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_substation_de772da3` (`organization_id`),
  KEY `inventory_substation_b6860804` (`device_id`),
  KEY `inventory_substation_c42a47b3` (`antenna_id`),
  KEY `inventory_substation_d860be3c` (`country_id`),
  KEY `inventory_substation_5654bf12` (`state_id`),
  KEY `inventory_substation_b376980e` (`city_id`),
  CONSTRAINT `antenna_id_refs_id_c73aea92` FOREIGN KEY (`antenna_id`) REFERENCES `inventory_antenna` (`id`),
  CONSTRAINT `city_id_refs_id_d4c7b77f` FOREIGN KEY (`city_id`) REFERENCES `device_city` (`id`),
  CONSTRAINT `country_id_refs_id_53324901` FOREIGN KEY (`country_id`) REFERENCES `device_country` (`id`),
  CONSTRAINT `device_id_refs_id_b9846ee6` FOREIGN KEY (`device_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `organization_id_refs_id_d968c5c7` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`),
  CONSTRAINT `state_id_refs_id_80496304` FOREIGN KEY (`state_id`) REFERENCES `device_state` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_thematicsettings`
--

DROP TABLE IF EXISTS `inventory_thematicsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_thematicsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `threshold_template_id` int(11) NOT NULL,
  `icon_settings` longtext NOT NULL,
  `is_global` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_thematicsettings_935fd544` (`threshold_template_id`),
  CONSTRAINT `threshold_template_id_refs_id_147cf0f7` FOREIGN KEY (`threshold_template_id`) REFERENCES `inventory_thresholdconfiguration` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_thresholdconfiguration`
--

DROP TABLE IF EXISTS `inventory_thresholdconfiguration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_thresholdconfiguration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `service_type` varchar(3) NOT NULL,
  `live_polling_template_id` int(11) NOT NULL,
  `range1_start` varchar(20) DEFAULT NULL,
  `range1_end` varchar(20) DEFAULT NULL,
  `range2_start` varchar(20) DEFAULT NULL,
  `range2_end` varchar(20) DEFAULT NULL,
  `range3_start` varchar(20) DEFAULT NULL,
  `range3_end` varchar(20) DEFAULT NULL,
  `range4_start` varchar(20) DEFAULT NULL,
  `range4_end` varchar(20) DEFAULT NULL,
  `range5_start` varchar(20) DEFAULT NULL,
  `range5_end` varchar(20) DEFAULT NULL,
  `range6_start` varchar(20) DEFAULT NULL,
  `range6_end` varchar(20) DEFAULT NULL,
  `range7_start` varchar(20) DEFAULT NULL,
  `range7_end` varchar(20) DEFAULT NULL,
  `range8_start` varchar(20) DEFAULT NULL,
  `range8_end` varchar(20) DEFAULT NULL,
  `range9_start` varchar(20) DEFAULT NULL,
  `range9_end` varchar(20) DEFAULT NULL,
  `range10_start` varchar(20) DEFAULT NULL,
  `range10_end` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_thresholdconfiguration_e2cbd31f` (`live_polling_template_id`),
  CONSTRAINT `live_polling_template_id_refs_id_f6650396` FOREIGN KEY (`live_polling_template_id`) REFERENCES `inventory_livepollingsettings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_userpingthematicsettings`
--

DROP TABLE IF EXISTS `inventory_userpingthematicsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_userpingthematicsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_profile_id` int(11) NOT NULL,
  `thematic_template_id` int(11) NOT NULL,
  `thematic_technology_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_userpingthematicsettings_82936d91` (`user_profile_id`),
  KEY `inventory_userpingthematicsettings_60e181f1` (`thematic_template_id`),
  KEY `inventory_userpingthematicsettings_a66af0b6` (`thematic_technology_id`),
  CONSTRAINT `thematic_technology_id_refs_id_bda21817` FOREIGN KEY (`thematic_technology_id`) REFERENCES `device_devicetechnology` (`id`),
  CONSTRAINT `thematic_template_id_refs_id_c0138c1f` FOREIGN KEY (`thematic_template_id`) REFERENCES `inventory_pingthematicsettings` (`id`),
  CONSTRAINT `user_profile_id_refs_user_ptr_id_f1e4e780` FOREIGN KEY (`user_profile_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory_userthematicsettings`
--

DROP TABLE IF EXISTS `inventory_userthematicsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_userthematicsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_profile_id` int(11) NOT NULL,
  `thematic_template_id` int(11) NOT NULL,
  `thematic_technology_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_userthematicsettings_82936d91` (`user_profile_id`),
  KEY `inventory_userthematicsettings_60e181f1` (`thematic_template_id`),
  KEY `inventory_userthematicsettings_a66af0b6` (`thematic_technology_id`),
  CONSTRAINT `thematic_technology_id_refs_id_b3669baa` FOREIGN KEY (`thematic_technology_id`) REFERENCES `device_devicetechnology` (`id`),
  CONSTRAINT `thematic_template_id_refs_id_71f01e6f` FOREIGN KEY (`thematic_template_id`) REFERENCES `inventory_thematicsettings` (`id`),
  CONSTRAINT `user_profile_id_refs_user_ptr_id_bd6d08d9` FOREIGN KEY (`user_profile_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `organization_organization`
--

DROP TABLE IF EXISTS `organization_organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `organization_organization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventinventory`
--

DROP TABLE IF EXISTS `performance_eventinventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventinventory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventinventory_4d7fdddd` (`device_name`),
  KEY `performance_eventinventory_48f8ebf4` (`service_name`),
  KEY `performance_eventinventory_fea3c3b5` (`ip_address`),
  KEY `performance_eventinventory_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventinventorystatus`
--

DROP TABLE IF EXISTS `performance_eventinventorystatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventinventorystatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventinventorystatus_4d7fdddd` (`device_name`),
  KEY `performance_eventinventorystatus_48f8ebf4` (`service_name`),
  KEY `performance_eventinventorystatus_fea3c3b5` (`ip_address`),
  KEY `performance_eventinventorystatus_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventmachine`
--

DROP TABLE IF EXISTS `performance_eventmachine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventmachine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventmachine_4d7fdddd` (`device_name`),
  KEY `performance_eventmachine_48f8ebf4` (`service_name`),
  KEY `performance_eventmachine_fea3c3b5` (`ip_address`),
  KEY `performance_eventmachine_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventmachinestatus`
--

DROP TABLE IF EXISTS `performance_eventmachinestatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventmachinestatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventmachinestatus_4d7fdddd` (`device_name`),
  KEY `performance_eventmachinestatus_48f8ebf4` (`service_name`),
  KEY `performance_eventmachinestatus_fea3c3b5` (`ip_address`),
  KEY `performance_eventmachinestatus_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventnetwork`
--

DROP TABLE IF EXISTS `performance_eventnetwork`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventnetwork` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventnetwork_4d7fdddd` (`device_name`),
  KEY `performance_eventnetwork_48f8ebf4` (`service_name`),
  KEY `performance_eventnetwork_fea3c3b5` (`ip_address`),
  KEY `performance_eventnetwork_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventnetworkdaily`
--

DROP TABLE IF EXISTS `performance_eventnetworkdaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventnetworkdaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventnetworkdaily_4d7fdddd` (`device_name`),
  KEY `performance_eventnetworkdaily_48f8ebf4` (`service_name`),
  KEY `performance_eventnetworkdaily_fea3c3b5` (`ip_address`),
  KEY `performance_eventnetworkdaily_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventnetworkmonthly`
--

DROP TABLE IF EXISTS `performance_eventnetworkmonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventnetworkmonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventnetworkmonthly_4d7fdddd` (`device_name`),
  KEY `performance_eventnetworkmonthly_48f8ebf4` (`service_name`),
  KEY `performance_eventnetworkmonthly_fea3c3b5` (`ip_address`),
  KEY `performance_eventnetworkmonthly_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventnetworkstatus`
--

DROP TABLE IF EXISTS `performance_eventnetworkstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventnetworkstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventnetworkstatus_4d7fdddd` (`device_name`),
  KEY `performance_eventnetworkstatus_48f8ebf4` (`service_name`),
  KEY `performance_eventnetworkstatus_fea3c3b5` (`ip_address`),
  KEY `performance_eventnetworkstatus_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventnetworkweekly`
--

DROP TABLE IF EXISTS `performance_eventnetworkweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventnetworkweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventnetworkweekly_4d7fdddd` (`device_name`),
  KEY `performance_eventnetworkweekly_48f8ebf4` (`service_name`),
  KEY `performance_eventnetworkweekly_fea3c3b5` (`ip_address`),
  KEY `performance_eventnetworkweekly_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventnetworkyearly`
--

DROP TABLE IF EXISTS `performance_eventnetworkyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventnetworkyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventnetworkyearly_4d7fdddd` (`device_name`),
  KEY `performance_eventnetworkyearly_48f8ebf4` (`service_name`),
  KEY `performance_eventnetworkyearly_fea3c3b5` (`ip_address`),
  KEY `performance_eventnetworkyearly_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventservice`
--

DROP TABLE IF EXISTS `performance_eventservice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventservice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventservice_4d7fdddd` (`device_name`),
  KEY `performance_eventservice_48f8ebf4` (`service_name`),
  KEY `performance_eventservice_fea3c3b5` (`ip_address`),
  KEY `performance_eventservice_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventservicedaily`
--

DROP TABLE IF EXISTS `performance_eventservicedaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventservicedaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventservicedaily_4d7fdddd` (`device_name`),
  KEY `performance_eventservicedaily_48f8ebf4` (`service_name`),
  KEY `performance_eventservicedaily_fea3c3b5` (`ip_address`),
  KEY `performance_eventservicedaily_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventservicestatus`
--

DROP TABLE IF EXISTS `performance_eventservicestatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventservicestatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventservicestatus_4d7fdddd` (`device_name`),
  KEY `performance_eventservicestatus_48f8ebf4` (`service_name`),
  KEY `performance_eventservicestatus_fea3c3b5` (`ip_address`),
  KEY `performance_eventservicestatus_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventserviceweekly`
--

DROP TABLE IF EXISTS `performance_eventserviceweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventserviceweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventserviceweekly_4d7fdddd` (`device_name`),
  KEY `performance_eventserviceweekly_48f8ebf4` (`service_name`),
  KEY `performance_eventserviceweekly_fea3c3b5` (`ip_address`),
  KEY `performance_eventserviceweekly_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventserviceyearly`
--

DROP TABLE IF EXISTS `performance_eventserviceyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventserviceyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventserviceyearly_4d7fdddd` (`device_name`),
  KEY `performance_eventserviceyearly_48f8ebf4` (`service_name`),
  KEY `performance_eventserviceyearly_fea3c3b5` (`ip_address`),
  KEY `performance_eventserviceyearly_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventstatus`
--

DROP TABLE IF EXISTS `performance_eventstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventstatus_4d7fdddd` (`device_name`),
  KEY `performance_eventstatus_48f8ebf4` (`service_name`),
  KEY `performance_eventstatus_fea3c3b5` (`ip_address`),
  KEY `performance_eventstatus_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_eventstatusstatus`
--

DROP TABLE IF EXISTS `performance_eventstatusstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_eventstatusstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_eventstatusstatus_4d7fdddd` (`device_name`),
  KEY `performance_eventstatusstatus_48f8ebf4` (`service_name`),
  KEY `performance_eventstatusstatus_fea3c3b5` (`ip_address`),
  KEY `performance_eventstatusstatus_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_inventorystatus`
--

DROP TABLE IF EXISTS `performance_inventorystatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_inventorystatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`,`service_name`,`data_source`),
  KEY `performance_inventorystatus_fea3c3b5` (`ip_address`),
  KEY `performance_inventorystatus_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_machinestatus`
--

DROP TABLE IF EXISTS `performance_machinestatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_machinestatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`,`service_name`,`data_source`),
  KEY `performance_machinestatus_fea3c3b5` (`ip_address`),
  KEY `performance_machinestatus_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_networkavailabilitydaily`
--

DROP TABLE IF EXISTS `performance_networkavailabilitydaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_networkavailabilitydaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_networkavailabilitydaily_4d7fdddd` (`device_name`),
  KEY `performance_networkavailabilitydaily_48f8ebf4` (`service_name`),
  KEY `performance_networkavailabilitydaily_fea3c3b5` (`ip_address`),
  KEY `performance_networkavailabilitydaily_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_networkavailabilitymonthly`
--

DROP TABLE IF EXISTS `performance_networkavailabilitymonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_networkavailabilitymonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_networkavailabilitymonthly_4d7fdddd` (`device_name`),
  KEY `performance_networkavailabilitymonthly_48f8ebf4` (`service_name`),
  KEY `performance_networkavailabilitymonthly_fea3c3b5` (`ip_address`),
  KEY `performance_networkavailabilitymonthly_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_networkavailabilityweekly`
--

DROP TABLE IF EXISTS `performance_networkavailabilityweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_networkavailabilityweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_networkavailabilityweekly_4d7fdddd` (`device_name`),
  KEY `performance_networkavailabilityweekly_48f8ebf4` (`service_name`),
  KEY `performance_networkavailabilityweekly_fea3c3b5` (`ip_address`),
  KEY `performance_networkavailabilityweekly_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_networkavailabilityyearly`
--

DROP TABLE IF EXISTS `performance_networkavailabilityyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_networkavailabilityyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_networkavailabilityyearly_4d7fdddd` (`device_name`),
  KEY `performance_networkavailabilityyearly_48f8ebf4` (`service_name`),
  KEY `performance_networkavailabilityyearly_fea3c3b5` (`ip_address`),
  KEY `performance_networkavailabilityyearly_24bd1ce3` (`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_networkstatus`
--

DROP TABLE IF EXISTS `performance_networkstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_networkstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`,`service_name`,`data_source`),
  KEY `performance_networkstatus_fea3c3b5` (`ip_address`),
  KEY `performance_networkstatus_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceinventory`
--

DROP TABLE IF EXISTS `performance_performanceinventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceinventory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceinventory_4d7fdddd` (`device_name`),
  KEY `performance_performanceinventory_48f8ebf4` (`service_name`),
  KEY `performance_performanceinventory_fea3c3b5` (`ip_address`),
  KEY `performance_performanceinventory_24bd1ce3` (`data_source`),
  KEY `performance_performanceinventory_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceinventorydaily`
--

DROP TABLE IF EXISTS `performance_performanceinventorydaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceinventorydaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceinventorydaily_4d7fdddd` (`device_name`),
  KEY `performance_performanceinventorydaily_48f8ebf4` (`service_name`),
  KEY `performance_performanceinventorydaily_fea3c3b5` (`ip_address`),
  KEY `performance_performanceinventorydaily_24bd1ce3` (`data_source`),
  KEY `performance_performanceinventorydaily_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceinventorymonthly`
--

DROP TABLE IF EXISTS `performance_performanceinventorymonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceinventorymonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceinventorymonthly_4d7fdddd` (`device_name`),
  KEY `performance_performanceinventorymonthly_48f8ebf4` (`service_name`),
  KEY `performance_performanceinventorymonthly_fea3c3b5` (`ip_address`),
  KEY `performance_performanceinventorymonthly_24bd1ce3` (`data_source`),
  KEY `performance_performanceinventorymonthly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceinventoryweekly`
--

DROP TABLE IF EXISTS `performance_performanceinventoryweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceinventoryweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceinventoryweekly_4d7fdddd` (`device_name`),
  KEY `performance_performanceinventoryweekly_48f8ebf4` (`service_name`),
  KEY `performance_performanceinventoryweekly_fea3c3b5` (`ip_address`),
  KEY `performance_performanceinventoryweekly_24bd1ce3` (`data_source`),
  KEY `performance_performanceinventoryweekly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceinventoryyearly`
--

DROP TABLE IF EXISTS `performance_performanceinventoryyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceinventoryyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceinventoryyearly_4d7fdddd` (`device_name`),
  KEY `performance_performanceinventoryyearly_48f8ebf4` (`service_name`),
  KEY `performance_performanceinventoryyearly_fea3c3b5` (`ip_address`),
  KEY `performance_performanceinventoryyearly_24bd1ce3` (`data_source`),
  KEY `performance_performanceinventoryyearly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancemachine`
--

DROP TABLE IF EXISTS `performance_performancemachine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancemachine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancemachine_4d7fdddd` (`device_name`),
  KEY `performance_performancemachine_48f8ebf4` (`service_name`),
  KEY `performance_performancemachine_fea3c3b5` (`ip_address`),
  KEY `performance_performancemachine_24bd1ce3` (`data_source`),
  KEY `performance_performancemachine_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancemetric_4d7fdddd` (`device_name`),
  KEY `performance_performancemetric_48f8ebf4` (`service_name`),
  KEY `performance_performancemetric_fea3c3b5` (`ip_address`),
  KEY `performance_performancemetric_24bd1ce3` (`data_source`),
  KEY `performance_performancemetric_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancenetwork`
--

DROP TABLE IF EXISTS `performance_performancenetwork`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancenetwork` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancenetwork_4d7fdddd` (`device_name`),
  KEY `performance_performancenetwork_48f8ebf4` (`service_name`),
  KEY `performance_performancenetwork_fea3c3b5` (`ip_address`),
  KEY `performance_performancenetwork_24bd1ce3` (`data_source`),
  KEY `performance_performancenetwork_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancenetworkbihourly`
--

DROP TABLE IF EXISTS `performance_performancenetworkbihourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancenetworkbihourly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancenetworkbihourly_4d7fdddd` (`device_name`),
  KEY `performance_performancenetworkbihourly_48f8ebf4` (`service_name`),
  KEY `performance_performancenetworkbihourly_fea3c3b5` (`ip_address`),
  KEY `performance_performancenetworkbihourly_24bd1ce3` (`data_source`),
  KEY `performance_performancenetworkbihourly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancenetworkdaily`
--

DROP TABLE IF EXISTS `performance_performancenetworkdaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancenetworkdaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancenetworkdaily_4d7fdddd` (`device_name`),
  KEY `performance_performancenetworkdaily_48f8ebf4` (`service_name`),
  KEY `performance_performancenetworkdaily_fea3c3b5` (`ip_address`),
  KEY `performance_performancenetworkdaily_24bd1ce3` (`data_source`),
  KEY `performance_performancenetworkdaily_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancenetworkhourly`
--

DROP TABLE IF EXISTS `performance_performancenetworkhourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancenetworkhourly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancenetworkhourly_4d7fdddd` (`device_name`),
  KEY `performance_performancenetworkhourly_48f8ebf4` (`service_name`),
  KEY `performance_performancenetworkhourly_fea3c3b5` (`ip_address`),
  KEY `performance_performancenetworkhourly_24bd1ce3` (`data_source`),
  KEY `performance_performancenetworkhourly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancenetworkmonthly`
--

DROP TABLE IF EXISTS `performance_performancenetworkmonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancenetworkmonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancenetworkmonthly_4d7fdddd` (`device_name`),
  KEY `performance_performancenetworkmonthly_48f8ebf4` (`service_name`),
  KEY `performance_performancenetworkmonthly_fea3c3b5` (`ip_address`),
  KEY `performance_performancenetworkmonthly_24bd1ce3` (`data_source`),
  KEY `performance_performancenetworkmonthly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancenetworkweekly`
--

DROP TABLE IF EXISTS `performance_performancenetworkweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancenetworkweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancenetworkweekly_4d7fdddd` (`device_name`),
  KEY `performance_performancenetworkweekly_48f8ebf4` (`service_name`),
  KEY `performance_performancenetworkweekly_fea3c3b5` (`ip_address`),
  KEY `performance_performancenetworkweekly_24bd1ce3` (`data_source`),
  KEY `performance_performancenetworkweekly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancenetworkyearly`
--

DROP TABLE IF EXISTS `performance_performancenetworkyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancenetworkyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancenetworkyearly_4d7fdddd` (`device_name`),
  KEY `performance_performancenetworkyearly_48f8ebf4` (`service_name`),
  KEY `performance_performancenetworkyearly_fea3c3b5` (`ip_address`),
  KEY `performance_performancenetworkyearly_24bd1ce3` (`data_source`),
  KEY `performance_performancenetworkyearly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceservice`
--

DROP TABLE IF EXISTS `performance_performanceservice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceservice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceservice_4d7fdddd` (`device_name`),
  KEY `performance_performanceservice_48f8ebf4` (`service_name`),
  KEY `performance_performanceservice_fea3c3b5` (`ip_address`),
  KEY `performance_performanceservice_24bd1ce3` (`data_source`),
  KEY `performance_performanceservice_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceservicebihourly`
--

DROP TABLE IF EXISTS `performance_performanceservicebihourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceservicebihourly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceservicebihourly_4d7fdddd` (`device_name`),
  KEY `performance_performanceservicebihourly_48f8ebf4` (`service_name`),
  KEY `performance_performanceservicebihourly_fea3c3b5` (`ip_address`),
  KEY `performance_performanceservicebihourly_24bd1ce3` (`data_source`),
  KEY `performance_performanceservicebihourly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceservicedaily`
--

DROP TABLE IF EXISTS `performance_performanceservicedaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceservicedaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceservicedaily_4d7fdddd` (`device_name`),
  KEY `performance_performanceservicedaily_48f8ebf4` (`service_name`),
  KEY `performance_performanceservicedaily_fea3c3b5` (`ip_address`),
  KEY `performance_performanceservicedaily_24bd1ce3` (`data_source`),
  KEY `performance_performanceservicedaily_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceservicehourly`
--

DROP TABLE IF EXISTS `performance_performanceservicehourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceservicehourly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceservicehourly_4d7fdddd` (`device_name`),
  KEY `performance_performanceservicehourly_48f8ebf4` (`service_name`),
  KEY `performance_performanceservicehourly_fea3c3b5` (`ip_address`),
  KEY `performance_performanceservicehourly_24bd1ce3` (`data_source`),
  KEY `performance_performanceservicehourly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceservicemonthly`
--

DROP TABLE IF EXISTS `performance_performanceservicemonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceservicemonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceservicemonthly_4d7fdddd` (`device_name`),
  KEY `performance_performanceservicemonthly_48f8ebf4` (`service_name`),
  KEY `performance_performanceservicemonthly_fea3c3b5` (`ip_address`),
  KEY `performance_performanceservicemonthly_24bd1ce3` (`data_source`),
  KEY `performance_performanceservicemonthly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceserviceweekly`
--

DROP TABLE IF EXISTS `performance_performanceserviceweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceserviceweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceserviceweekly_4d7fdddd` (`device_name`),
  KEY `performance_performanceserviceweekly_48f8ebf4` (`service_name`),
  KEY `performance_performanceserviceweekly_fea3c3b5` (`ip_address`),
  KEY `performance_performanceserviceweekly_24bd1ce3` (`data_source`),
  KEY `performance_performanceserviceweekly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performanceserviceyearly`
--

DROP TABLE IF EXISTS `performance_performanceserviceyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performanceserviceyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performanceserviceyearly_4d7fdddd` (`device_name`),
  KEY `performance_performanceserviceyearly_48f8ebf4` (`service_name`),
  KEY `performance_performanceserviceyearly_fea3c3b5` (`ip_address`),
  KEY `performance_performanceserviceyearly_24bd1ce3` (`data_source`),
  KEY `performance_performanceserviceyearly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancestatus`
--

DROP TABLE IF EXISTS `performance_performancestatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancestatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancestatus_4d7fdddd` (`device_name`),
  KEY `performance_performancestatus_48f8ebf4` (`service_name`),
  KEY `performance_performancestatus_fea3c3b5` (`ip_address`),
  KEY `performance_performancestatus_24bd1ce3` (`data_source`),
  KEY `performance_performancestatus_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancestatusdaily`
--

DROP TABLE IF EXISTS `performance_performancestatusdaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancestatusdaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancestatusdaily_4d7fdddd` (`device_name`),
  KEY `performance_performancestatusdaily_48f8ebf4` (`service_name`),
  KEY `performance_performancestatusdaily_fea3c3b5` (`ip_address`),
  KEY `performance_performancestatusdaily_24bd1ce3` (`data_source`),
  KEY `performance_performancestatusdaily_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancestatusmonthly`
--

DROP TABLE IF EXISTS `performance_performancestatusmonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancestatusmonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancestatusmonthly_4d7fdddd` (`device_name`),
  KEY `performance_performancestatusmonthly_48f8ebf4` (`service_name`),
  KEY `performance_performancestatusmonthly_fea3c3b5` (`ip_address`),
  KEY `performance_performancestatusmonthly_24bd1ce3` (`data_source`),
  KEY `performance_performancestatusmonthly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancestatusweekly`
--

DROP TABLE IF EXISTS `performance_performancestatusweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancestatusweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancestatusweekly_4d7fdddd` (`device_name`),
  KEY `performance_performancestatusweekly_48f8ebf4` (`service_name`),
  KEY `performance_performancestatusweekly_fea3c3b5` (`ip_address`),
  KEY `performance_performancestatusweekly_24bd1ce3` (`data_source`),
  KEY `performance_performancestatusweekly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_performancestatusyearly`
--

DROP TABLE IF EXISTS `performance_performancestatusyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_performancestatusyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_performancestatusyearly_4d7fdddd` (`device_name`),
  KEY `performance_performancestatusyearly_48f8ebf4` (`service_name`),
  KEY `performance_performancestatusyearly_fea3c3b5` (`ip_address`),
  KEY `performance_performancestatusyearly_24bd1ce3` (`data_source`),
  KEY `performance_performancestatusyearly_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_rfnetworkavailability`
--

DROP TABLE IF EXISTS `performance_rfnetworkavailability`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_rfnetworkavailability` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `technology_id` int(11) NOT NULL,
  `avail` double DEFAULT NULL,
  `unavail` double DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_rfnetworkavailability_98427941` (`technology_id`),
  CONSTRAINT `technology_id_refs_id_303f79b0` FOREIGN KEY (`technology_id`) REFERENCES `device_devicetechnology` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_servicestatus`
--

DROP TABLE IF EXISTS `performance_servicestatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_servicestatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`,`service_name`,`data_source`),
  KEY `performance_servicestatus_fea3c3b5` (`ip_address`),
  KEY `performance_servicestatus_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_spotdashboard`
--

DROP TABLE IF EXISTS `performance_spotdashboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_spotdashboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sector_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `sector_sector_id` varchar(64) DEFAULT NULL,
  `sector_sector_configured_on` varchar(64) DEFAULT NULL,
  `sector_device_technology` varchar(64) DEFAULT NULL,
  `ul_issue_1` tinyint(1) NOT NULL,
  `ul_issue_2` tinyint(1) NOT NULL,
  `ul_issue_3` tinyint(1) NOT NULL,
  `ul_issue_4` tinyint(1) NOT NULL,
  `ul_issue_5` tinyint(1) NOT NULL,
  `ul_issue_6` tinyint(1) NOT NULL,
  `augment_1` tinyint(1) NOT NULL,
  `augment_2` tinyint(1) NOT NULL,
  `augment_3` tinyint(1) NOT NULL,
  `augment_4` tinyint(1) NOT NULL,
  `augment_5` tinyint(1) NOT NULL,
  `augment_6` tinyint(1) NOT NULL,
  `sia_1` tinyint(1) NOT NULL,
  `sia_2` tinyint(1) NOT NULL,
  `sia_3` tinyint(1) NOT NULL,
  `sia_4` tinyint(1) NOT NULL,
  `sia_5` tinyint(1) NOT NULL,
  `sia_6` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sector_sector_id` (`sector_sector_id`),
  KEY `performance_spotdashboard_663ed8c9` (`sector_id`),
  KEY `performance_spotdashboard_b6860804` (`device_id`),
  CONSTRAINT `device_id_refs_id_f4323869` FOREIGN KEY (`device_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `sector_id_refs_id_dff3c1d8` FOREIGN KEY (`sector_id`) REFERENCES `inventory_sector` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_status`
--

DROP TABLE IF EXISTS `performance_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`,`service_name`,`data_source`),
  KEY `performance_status_fea3c3b5` (`ip_address`),
  KEY `performance_status_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_topology`
--

DROP TABLE IF EXISTS `performance_topology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_topology` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `mac_address` varchar(20) DEFAULT NULL,
  `sector_id` varchar(32) DEFAULT NULL,
  `connected_device_ip` varchar(20) DEFAULT NULL,
  `connected_device_mac` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_topology_4d7fdddd` (`device_name`),
  KEY `performance_topology_48f8ebf4` (`service_name`),
  KEY `performance_topology_24bd1ce3` (`data_source`),
  KEY `performance_topology_fea3c3b5` (`ip_address`),
  KEY `performance_topology_938d59ed` (`mac_address`),
  KEY `performance_topology_54d73574` (`sector_id`),
  KEY `performance_topology_04b5c0cf` (`connected_device_ip`),
  KEY `performance_topology_d7fc5dad` (`connected_device_mac`),
  KEY `performance_topology_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_utilization`
--

DROP TABLE IF EXISTS `performance_utilization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_utilization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_utilization_4d7fdddd` (`device_name`),
  KEY `performance_utilization_48f8ebf4` (`service_name`),
  KEY `performance_utilization_fea3c3b5` (`ip_address`),
  KEY `performance_utilization_24bd1ce3` (`data_source`),
  KEY `performance_utilization_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_utilizationbihourly`
--

DROP TABLE IF EXISTS `performance_utilizationbihourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_utilizationbihourly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_utilizationbihourly_fea3c3b5` (`ip_address`),
  KEY `performance_utilizationbihourly_ead64ad4` (`refer`),
  KEY `performance_utilizationbihourly_ffd388bc` (`device_name`,`service_name`,`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_utilizationdaily`
--

DROP TABLE IF EXISTS `performance_utilizationdaily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_utilizationdaily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_utilizationdaily_fea3c3b5` (`ip_address`),
  KEY `performance_utilizationdaily_ead64ad4` (`refer`),
  KEY `performance_utilizationdaily_ffd388bc` (`device_name`,`service_name`,`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_utilizationhourly`
--

DROP TABLE IF EXISTS `performance_utilizationhourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_utilizationhourly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_utilizationhourly_fea3c3b5` (`ip_address`),
  KEY `performance_utilizationhourly_ead64ad4` (`refer`),
  KEY `performance_utilizationhourly_ffd388bc` (`device_name`,`service_name`,`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_utilizationmonthly`
--

DROP TABLE IF EXISTS `performance_utilizationmonthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_utilizationmonthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_utilizationmonthly_fea3c3b5` (`ip_address`),
  KEY `performance_utilizationmonthly_ead64ad4` (`refer`),
  KEY `performance_utilizationmonthly_ffd388bc` (`device_name`,`service_name`,`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_utilizationstatus`
--

DROP TABLE IF EXISTS `performance_utilizationstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_utilizationstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_name` (`device_name`,`service_name`,`data_source`),
  KEY `performance_utilizationstatus_fea3c3b5` (`ip_address`),
  KEY `performance_utilizationstatus_ead64ad4` (`refer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_utilizationweekly`
--

DROP TABLE IF EXISTS `performance_utilizationweekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_utilizationweekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_utilizationweekly_fea3c3b5` (`ip_address`),
  KEY `performance_utilizationweekly_ead64ad4` (`refer`),
  KEY `performance_utilizationweekly_ffd388bc` (`device_name`,`service_name`,`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `performance_utilizationyearly`
--

DROP TABLE IF EXISTS `performance_utilizationyearly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `performance_utilizationyearly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(100) DEFAULT NULL,
  `service_name` varchar(100) DEFAULT NULL,
  `machine_name` varchar(100) DEFAULT NULL,
  `site_name` varchar(100) DEFAULT NULL,
  `ip_address` varchar(20) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `current_value` varchar(20) DEFAULT NULL,
  `min_value` varchar(20) DEFAULT NULL,
  `max_value` varchar(20) DEFAULT NULL,
  `avg_value` varchar(20) DEFAULT NULL,
  `warning_threshold` varchar(20) DEFAULT NULL,
  `critical_threshold` varchar(20) DEFAULT NULL,
  `sys_timestamp` int(11) NOT NULL,
  `check_timestamp` int(11) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `refer` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `performance_utilizationyearly_fea3c3b5` (`ip_address`),
  KEY `performance_utilizationyearly_ead64ad4` (`refer`),
  KEY `performance_utilizationyearly_ffd388bc` (`device_name`,`service_name`,`data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduling_management_event`
--

DROP TABLE IF EXISTS `scheduling_management_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduling_management_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `repeat` varchar(10) NOT NULL,
  `repeat_every` int(11) DEFAULT NULL,
  `repeat_by` varchar(10) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `start_on` date NOT NULL,
  `start_on_time` time NOT NULL,
  `end_on_time` time NOT NULL,
  `end_never` tinyint(1) NOT NULL,
  `end_after` int(11) DEFAULT NULL,
  `end_on` date DEFAULT NULL,
  `created_by_id` int(11) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `scheduling_type` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `scheduling_management_event_0c98d849` (`created_by_id`),
  KEY `scheduling_management_event_de772da3` (`organization_id`),
  CONSTRAINT `created_by_id_refs_user_ptr_id_c0d75311` FOREIGN KEY (`created_by_id`) REFERENCES `user_profile_userprofile` (`user_ptr_id`),
  CONSTRAINT `organization_id_refs_id_c175020d` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduling_management_event_device`
--

DROP TABLE IF EXISTS `scheduling_management_event_device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduling_management_event_device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `event_id` (`event_id`,`device_id`),
  KEY `scheduling_management_event_device_a41e20fe` (`event_id`),
  KEY `scheduling_management_event_device_b6860804` (`device_id`),
  CONSTRAINT `device_id_refs_id_85b56f9b` FOREIGN KEY (`device_id`) REFERENCES `device_device` (`id`),
  CONSTRAINT `event_id_refs_id_9bcfaad1` FOREIGN KEY (`event_id`) REFERENCES `scheduling_management_event` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduling_management_event_repeat_on`
--

DROP TABLE IF EXISTS `scheduling_management_event_repeat_on`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduling_management_event_repeat_on` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` int(11) NOT NULL,
  `weekdays_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `event_id` (`event_id`,`weekdays_id`),
  KEY `scheduling_management_event_repeat_on_a41e20fe` (`event_id`),
  KEY `scheduling_management_event_repeat_on_d2ce7b61` (`weekdays_id`),
  CONSTRAINT `event_id_refs_id_3413cafd` FOREIGN KEY (`event_id`) REFERENCES `scheduling_management_event` (`id`),
  CONSTRAINT `weekdays_id_refs_id_12a4c38e` FOREIGN KEY (`weekdays_id`) REFERENCES `scheduling_management_weekdays` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduling_management_snmptrapsettings`
--

DROP TABLE IF EXISTS `scheduling_management_snmptrapsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduling_management_snmptrapsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_technology_id` int(11) DEFAULT NULL,
  `device_vendor_id` int(11) DEFAULT NULL,
  `device_model_id` int(11) DEFAULT NULL,
  `device_type_id` int(11) DEFAULT NULL,
  `name` varchar(150) NOT NULL,
  `alias` varchar(150) DEFAULT NULL,
  `trap_oid` varchar(255) DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `scheduling_management_snmptrapsettings_c80e59d5` (`device_technology_id`),
  KEY `scheduling_management_snmptrapsettings_bdc02d9a` (`device_vendor_id`),
  KEY `scheduling_management_snmptrapsettings_b7ada0de` (`device_model_id`),
  KEY `scheduling_management_snmptrapsettings_d8be8594` (`device_type_id`),
  CONSTRAINT `device_model_id_refs_id_a1a24f50` FOREIGN KEY (`device_model_id`) REFERENCES `device_devicemodel` (`id`),
  CONSTRAINT `device_technology_id_refs_id_c5e2116c` FOREIGN KEY (`device_technology_id`) REFERENCES `device_devicetechnology` (`id`),
  CONSTRAINT `device_type_id_refs_id_91026561` FOREIGN KEY (`device_type_id`) REFERENCES `device_devicetype` (`id`),
  CONSTRAINT `device_vendor_id_refs_id_4cf156e2` FOREIGN KEY (`device_vendor_id`) REFERENCES `device_devicevendor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduling_management_weekdays`
--

DROP TABLE IF EXISTS `scheduling_management_weekdays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduling_management_weekdays` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_devicepingconfiguration`
--

DROP TABLE IF EXISTS `service_devicepingconfiguration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_devicepingconfiguration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(200) DEFAULT NULL,
  `device_alias` varchar(200) DEFAULT NULL,
  `packets` int(11) DEFAULT NULL,
  `timeout` int(11) DEFAULT NULL,
  `normal_check_interval` int(11) DEFAULT NULL,
  `rta_warning` int(11) DEFAULT NULL,
  `rta_critical` int(11) DEFAULT NULL,
  `pl_warning` int(11) DEFAULT NULL,
  `pl_critical` int(11) DEFAULT NULL,
  `added_on` datetime DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_deviceserviceconfiguration`
--

DROP TABLE IF EXISTS `service_deviceserviceconfiguration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_deviceserviceconfiguration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(200) DEFAULT NULL,
  `service_name` varchar(200) DEFAULT NULL,
  `agent_tag` varchar(50) DEFAULT NULL,
  `port` int(11) DEFAULT NULL,
  `data_source` varchar(200) DEFAULT NULL,
  `version` varchar(10) DEFAULT NULL,
  `read_community` varchar(100) DEFAULT NULL,
  `svc_template` varchar(200) DEFAULT NULL,
  `normal_check_interval` int(11) DEFAULT NULL,
  `retry_check_interval` int(11) DEFAULT NULL,
  `max_check_attempts` int(11) DEFAULT NULL,
  `warning` varchar(20) DEFAULT NULL,
  `critical` varchar(20) DEFAULT NULL,
  `added_on` datetime DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `is_added` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  CONSTRAINT `servicegroup_id_refs_id_704115ab` FOREIGN KEY (`servicegroup_id`) REFERENCES `service_group_servicegroup` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_protocol`
--

DROP TABLE IF EXISTS `service_protocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_protocol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `protocol_name` varchar(255) NOT NULL,
  `port` int(11) NOT NULL,
  `version` varchar(10) NOT NULL,
  `read_community` varchar(100) NOT NULL,
  `write_community` varchar(100) DEFAULT NULL,
  `auth_password` varchar(100) DEFAULT NULL,
  `auth_protocol` varchar(100) DEFAULT NULL,
  `security_name` varchar(100) DEFAULT NULL,
  `security_level` varchar(100) DEFAULT NULL,
  `private_phase` varchar(100) DEFAULT NULL,
  `private_pass_phase` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  `parameters_id` int(11) NOT NULL,
  `command_id` int(11) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  KEY `service_service_0bd5c2c5` (`parameters_id`),
  KEY `service_service_36c081f7` (`command_id`),
  CONSTRAINT `command_id_refs_id_df37dd44` FOREIGN KEY (`command_id`) REFERENCES `command_command` (`id`),
  CONSTRAINT `parameters_id_refs_id_bce49a97` FOREIGN KEY (`parameters_id`) REFERENCES `service_serviceparameters` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  `chart_type` varchar(50) NOT NULL,
  `formula` varchar(100) DEFAULT NULL,
  `valuesuffix` varchar(100) NOT NULL,
  `valuetext` varchar(100) NOT NULL,
  `show_min` tinyint(1) NOT NULL,
  `show_max` tinyint(1) NOT NULL,
  `show_gis` tinyint(1) NOT NULL,
  `show_performance_center` tinyint(1) NOT NULL,
  `is_inverted` tinyint(1) NOT NULL,
  `data_source_type` int(11) NOT NULL,
  `warning` varchar(255) DEFAULT NULL,
  `critical` varchar(255) DEFAULT NULL,
  `chart_color` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_serviceparameters`
--

DROP TABLE IF EXISTS `service_serviceparameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_serviceparameters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parameter_description` varchar(250) NOT NULL,
  `protocol_id` int(11) NOT NULL,
  `normal_check_interval` int(11) NOT NULL,
  `retry_check_interval` int(11) NOT NULL,
  `max_check_attempts` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `service_serviceparameters_30a17921` (`protocol_id`),
  CONSTRAINT `protocol_id_refs_id_d74a2b9a` FOREIGN KEY (`protocol_id`) REFERENCES `service_protocol` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_servicespecificdatasource`
--

DROP TABLE IF EXISTS `service_servicespecificdatasource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_servicespecificdatasource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `service_data_sources_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `warning` varchar(255) DEFAULT NULL,
  `critical` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `service_servicespecificdatasource_672804af` (`service_data_sources_id`),
  KEY `service_servicespecificdatasource_91a0ac17` (`service_id`),
  CONSTRAINT `service_data_sources_id_refs_id_3557204f` FOREIGN KEY (`service_data_sources_id`) REFERENCES `service_servicedatasource` (`id`),
  CONSTRAINT `service_id_refs_id_c43d95db` FOREIGN KEY (`service_id`) REFERENCES `service_service` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `session_management_authtoken`
--

DROP TABLE IF EXISTS `session_management_authtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session_management_authtoken` (
  `key` varchar(40) NOT NULL,
  `user_id` int(11) NOT NULL,
  `updated` datetime NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_7e55844a` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `site_instance_siteinstance`
--

DROP TABLE IF EXISTS `site_instance_siteinstance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `site_instance_siteinstance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `alias` varchar(255) NOT NULL,
  `machine_id` int(11) DEFAULT NULL,
  `live_status_tcp_port` int(11) DEFAULT NULL,
  `web_service_port` int(11) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `site_instance_siteinstance_dbaea34e` (`machine_id`),
  CONSTRAINT `machine_id_refs_id_2f639b27` FOREIGN KEY (`machine_id`) REFERENCES `machine_machine` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_profile_userpasswordrecord`
--

DROP TABLE IF EXISTS `user_profile_userpasswordrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_profile_userpasswordrecord` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `password_used` varchar(100) DEFAULT NULL,
  `password_used_on` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  `password_changed_at` datetime DEFAULT NULL,
  `user_invalid_attempt` int(11) DEFAULT NULL,
  `user_invalid_attempt_at` datetime DEFAULT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-03-21 16:45:03
