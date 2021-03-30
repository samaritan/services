CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `metric` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(125) NOT NULL,
  `granularity` varchar(125) NOT NULL,
  `service` varchar(125) NOT NULL,
  `enabled` tinyint DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`,`granularity`),
  CONSTRAINT `metric_chk_1` CHECK ((`enabled` in (0,1)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `project_metric` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `enabled` tinyint DEFAULT '0',
  `metric_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`,`metric_id`),
  KEY `metric_id` (`metric_id`),
  KEY `ix_project_metric_project_id` (`project_id`),
  CONSTRAINT `project_metric_ibfk_1` FOREIGN KEY (`metric_id`) REFERENCES `metric` (`id`),
  CONSTRAINT `project_metric_chk_1` CHECK ((`enabled` in (0,1)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
