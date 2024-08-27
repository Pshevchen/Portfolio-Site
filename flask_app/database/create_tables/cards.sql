CREATE TABLE IF NOT EXISTS `cards` (
`card_id` int(11) NOT NULL AUTO_INCREMENT,
`column_id` int(11) NOT NULL,
`card_content` text,
PRIMARY KEY (`card_id`),
FOREIGN KEY (`column_id`) REFERENCES columns(column_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;