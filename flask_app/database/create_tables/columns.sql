CREATE TABLE IF NOT EXISTS `columns` (
`column_id` int(11) NOT NULL AUTO_INCREMENT,
`board_id` int(11) NOT NULL,
`column_name` varchar(100) NOT NULL,
PRIMARY KEY (`column_id`),
FOREIGN KEY (`board_id`) REFERENCES boards(board_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;