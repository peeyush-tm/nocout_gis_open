ALTER TABLE `inventory_antenna` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_backhaul` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_basestation` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_circuit` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_customer` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_sector` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `inventory_substation` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
