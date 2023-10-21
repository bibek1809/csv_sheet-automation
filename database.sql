DROP TABLE IF EXISTS `file_space_register`;

DROP TABLE IF EXISTS `csv_space_mapper_table`;
/*Table structure for table `account_bi_data_source` */

DROP TABLE IF EXISTS `csv_file`;

CREATE TABLE `csv_file` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `file_name` VARCHAR(255) NOT NULL,
  `s3_file_path` TEXT,
  `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `file_schema` JSON DEFAULT NULL,
  `column_mapping` JSON DEFAULT NULL,
  `file_separator` VARCHAR(5) DEFAULT ',',
  `category` VARCHAR(255) DEFAULT NULL,
  `is_deleted` BIT(1) DEFAULT b'0',
  `is_transformed` ENUM('0','1') NOT NULL DEFAULT '0',
  `link`  VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) 
;
/*Table structure for table `csv_space` */

DROP TABLE IF EXISTS `csv_space`;

CREATE TABLE `csv_space` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `space_name` VARCHAR(55) NOT NULL,
  `space_schema` JSON DEFAULT NULL,
  `s3_file_path` TEXT,
  `vds_path` VARCHAR(55) DEFAULT NULL,
  `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` BIT(1) DEFAULT b'0',
  `status` BIT(1) DEFAULT b'1',
  PRIMARY KEY (`id`)
) ;

/*Table structure for table `file_space_register` */



CREATE TABLE `file_space_register` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `file_id` INT(11) DEFAULT NULL,
  `space_id` INT(11) DEFAULT NULL,
  `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   `is_deleted` BIT(1) DEFAULT b'0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `file_space_id` (`file_id`,`space_id`),
  KEY `file_id` (`file_id`),
  KEY `space_id` (`space_id`),
  CONSTRAINT `file_space_register_ibfk_1` FOREIGN KEY (`file_id`) REFERENCES `csv_file` (`id`) ,
  CONSTRAINT `file_space_register_ibfk_2` FOREIGN KEY (`space_id`) REFERENCES `csv_space` (`id`) 
) ;



CREATE TABLE `csv_space_mapper_table` (
  `id` INT(11) NOT NULL,
  `space_id` INT(11) DEFAULT NULL,
    CONSTRAINT `space_mapper_table_ibfk_2` FOREIGN KEY (`space_id`) REFERENCES `csv_space` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ;

