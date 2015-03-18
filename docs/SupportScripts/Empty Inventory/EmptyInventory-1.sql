-- MySQL dump 10.13  Distrib 5.6.19, for linux-glibc2.5 (x86_64)
--
-- Host: 121.244.255.107    Database: nocout_m5
-- ------------------------------------------------------
-- Server version	5.6.19-enterprise-commercial-advanced-log

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
-- Table structure for table `inventory_substation`
--

DROP TABLE IF EXISTS `inventory_substation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_substation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL DEFAULT '1',
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
-- Table structure for table `inventory_sector`
--

DROP TABLE IF EXISTS `inventory_sector`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_sector` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL DEFAULT '1',
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
-- Table structure for table `inventory_customer`
--

DROP TABLE IF EXISTS `inventory_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL DEFAULT '1',
  `address` longtext,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_customer_de772da3` (`organization_id`),
  CONSTRAINT `organization_id_refs_id_cfbc7962` FOREIGN KEY (`organization_id`) REFERENCES `organization_organization` (`id`)
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
  `organization_id` int(11) NOT NULL DEFAULT '1',
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
-- Table structure for table `inventory_basestation`
--

DROP TABLE IF EXISTS `inventory_basestation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_basestation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL DEFAULT '1',
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
-- Table structure for table `inventory_backhaul`
--

DROP TABLE IF EXISTS `inventory_backhaul`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_backhaul` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL DEFAULT '1',
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
-- Table structure for table `inventory_antenna`
--

DROP TABLE IF EXISTS `inventory_antenna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_antenna` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `alias` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL DEFAULT '1',
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
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-01-30 10:40:26
