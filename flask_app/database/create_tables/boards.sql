CREATE TABLE IF NOT EXISTS `boards` (
`board_id`        int(11)  	    NOT NULL auto_increment	  COMMENT 'the id of this user',
`name`            varchar(100)  NOT NULL                  COMMENT 'the name of the board',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`board_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site user information";