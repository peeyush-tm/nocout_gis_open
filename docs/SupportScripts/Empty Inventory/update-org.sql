UPDATE `inventory_antenna` SET `organization_id` =1;
UPDATE `inventory_backhaul` SET `organization_id` =1;
UPDATE `inventory_basestation` SET `organization_id` =1;
UPDATE `inventory_circuit` SET `organization_id` =1;
UPDATE `inventory_customer` SET `organization_id` =1;
UPDATE `inventory_sector` SET `organization_id` =1;
UPDATE `inventory_substation` SET `organization_id` =1;


ALTER TABLE `inventory_antenna` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_backhaul` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_basestation` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_circuit` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_customer` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_sector` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_substation` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';