CREATE TABLE IF NOT EXISTS `boardusers` (
`boardusers_id`   int(11)  	    NOT NULL auto_increment	  COMMENT 'the id of this user',
`board_id`        int(11)       NOT NULL                  COMMENT 'the id of the board this email is a user of',
`email`           varchar(100)  NOT NULL                  COMMENT 'the email of the user',
PRIMARY KEY (`boardusers_id`),FOREIGN KEY (board_id) REFERENCES boards(board_id),UNIQUE (board_id, email)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site user information";