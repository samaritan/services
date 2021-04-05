LOCK TABLES `metric` WRITE;

INSERT IGNORE INTO `metric` VALUES
  (1,'churn','change','churn',1),
  (2,'collaboration','file','collaboration',0),
  (3,'complexity','function','complexity',1),
  (4,'contribution','file','contribution',0),
  (5,'flow','function','flow',0),
  (6,'functionchurn','change','functionchurn',1),
  (7,'hunk','change','hunk',1),
  (8,'interactivechurn','change','interactivechurn',1),
  (9,'keyword','change','keyword',1),
  (10,'loc','file','loc',1),
  (11,'loc','function','loc',1),
  (12,'messagetokens','commit','messagetokens',1),
  (13,'nesting','function','nesting',1),
  (14,'offender','file','offender',1),
  (15,'ownership','developer','ownership',1),
  (16,'pastauthors','change','pastauthors',1),
  (17,'pastchanges','change','pastchanges',1),
  (18,'patchtokens','change','patchtokens',1),
  (19,'relativechurn','change','relativechurn',1);

UNLOCK TABLES;
