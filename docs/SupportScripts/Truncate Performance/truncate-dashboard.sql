truncate table dashboard_dashboardrangestatustimely     ;
truncate table dashboard_dashboardrangestatusdaily      ;
truncate table dashboard_dashboardrangestatushourly     ;
truncate table dashboard_dashboardrangestatusmonthly    ;
truncate table dashboard_dashboardrangestatustimely     ;
truncate table dashboard_dashboardrangestatusweekly     ;
truncate table dashboard_dashboardrangestatusyearly     ;
truncate table dashboard_dashboardseveritystatusdaily   ;
truncate table dashboard_dashboardseveritystatushourly  ;
truncate table dashboard_dashboardseveritystatusmonthly ;
truncate table dashboard_dashboardseveritystatustimely  ;
truncate table dashboard_dashboardseveritystatusweekly  ;
truncate table dashboard_dashboardseveritystatusyearly  ;

ALTER TABLE `dashboard_dashboardrangestatustimely` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardrangestatushourly` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardrangestatusdaily` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardrangestatusmonthly` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardrangestatusweekly` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardrangestatusyearly` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';

ALTER TABLE `dashboard_dashboardseveritystatusdaily` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardseveritystatushourly` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardseveritystatusmonthly` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardseveritystatustimely` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardseveritystatusweekly` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
ALTER TABLE `dashboard_dashboardseveritystatusyearly` CHANGE `organization_id` `organization_id` INT( 11 ) NOT NULL DEFAULT '1';
