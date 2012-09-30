PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE "auth_permission" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL,
    "content_type_id" integer NOT NULL,
    "codename" varchar(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);
INSERT INTO "auth_permission" VALUES(1,'Can add permission',1,'add_permission');
INSERT INTO "auth_permission" VALUES(2,'Can change permission',1,'change_permission');
INSERT INTO "auth_permission" VALUES(3,'Can delete permission',1,'delete_permission');
INSERT INTO "auth_permission" VALUES(4,'Can add group',2,'add_group');
INSERT INTO "auth_permission" VALUES(5,'Can change group',2,'change_group');
INSERT INTO "auth_permission" VALUES(6,'Can delete group',2,'delete_group');
INSERT INTO "auth_permission" VALUES(7,'Can add user',3,'add_user');
INSERT INTO "auth_permission" VALUES(8,'Can change user',3,'change_user');
INSERT INTO "auth_permission" VALUES(9,'Can delete user',3,'delete_user');
INSERT INTO "auth_permission" VALUES(10,'Can add message',4,'add_message');
INSERT INTO "auth_permission" VALUES(11,'Can change message',4,'change_message');
INSERT INTO "auth_permission" VALUES(12,'Can delete message',4,'delete_message');
INSERT INTO "auth_permission" VALUES(13,'Can add content type',5,'add_contenttype');
INSERT INTO "auth_permission" VALUES(14,'Can change content type',5,'change_contenttype');
INSERT INTO "auth_permission" VALUES(15,'Can delete content type',5,'delete_contenttype');
INSERT INTO "auth_permission" VALUES(16,'Can add session',6,'add_session');
INSERT INTO "auth_permission" VALUES(17,'Can change session',6,'change_session');
INSERT INTO "auth_permission" VALUES(18,'Can delete session',6,'delete_session');
INSERT INTO "auth_permission" VALUES(19,'Can add site',7,'add_site');
INSERT INTO "auth_permission" VALUES(20,'Can change site',7,'change_site');
INSERT INTO "auth_permission" VALUES(21,'Can delete site',7,'delete_site');
INSERT INTO "auth_permission" VALUES(22,'Can add log entry',8,'add_logentry');
INSERT INTO "auth_permission" VALUES(23,'Can change log entry',8,'change_logentry');
INSERT INTO "auth_permission" VALUES(24,'Can delete log entry',8,'delete_logentry');
INSERT INTO "auth_permission" VALUES(25,'Can add profile',9,'add_profile');
INSERT INTO "auth_permission" VALUES(26,'Can change profile',9,'change_profile');
INSERT INTO "auth_permission" VALUES(27,'Can delete profile',9,'delete_profile');
INSERT INTO "auth_permission" VALUES(28,'Can add name type',10,'add_nametype');
INSERT INTO "auth_permission" VALUES(29,'Can change name type',10,'change_nametype');
INSERT INTO "auth_permission" VALUES(30,'Can delete name type',10,'delete_nametype');
INSERT INTO "auth_permission" VALUES(31,'Can add name origin type',11,'add_nameorigintype');
INSERT INTO "auth_permission" VALUES(32,'Can change name origin type',11,'change_nameorigintype');
INSERT INTO "auth_permission" VALUES(33,'Can delete name origin type',11,'delete_nameorigintype');
INSERT INTO "auth_permission" VALUES(34,'Can add attribute type',12,'add_attributetype');
INSERT INTO "auth_permission" VALUES(35,'Can change attribute type',12,'change_attributetype');
INSERT INTO "auth_permission" VALUES(36,'Can delete attribute type',12,'delete_attributetype');
INSERT INTO "auth_permission" VALUES(37,'Can add url type',13,'add_urltype');
INSERT INTO "auth_permission" VALUES(38,'Can change url type',13,'change_urltype');
INSERT INTO "auth_permission" VALUES(39,'Can delete url type',13,'delete_urltype');
INSERT INTO "auth_permission" VALUES(40,'Can add child ref type',14,'add_childreftype');
INSERT INTO "auth_permission" VALUES(41,'Can change child ref type',14,'change_childreftype');
INSERT INTO "auth_permission" VALUES(42,'Can delete child ref type',14,'delete_childreftype');
INSERT INTO "auth_permission" VALUES(43,'Can add repository type',15,'add_repositorytype');
INSERT INTO "auth_permission" VALUES(44,'Can change repository type',15,'change_repositorytype');
INSERT INTO "auth_permission" VALUES(45,'Can delete repository type',15,'delete_repositorytype');
INSERT INTO "auth_permission" VALUES(46,'Can add event type',16,'add_eventtype');
INSERT INTO "auth_permission" VALUES(47,'Can change event type',16,'change_eventtype');
INSERT INTO "auth_permission" VALUES(48,'Can delete event type',16,'delete_eventtype');
INSERT INTO "auth_permission" VALUES(49,'Can add family rel type',17,'add_familyreltype');
INSERT INTO "auth_permission" VALUES(50,'Can change family rel type',17,'change_familyreltype');
INSERT INTO "auth_permission" VALUES(51,'Can delete family rel type',17,'delete_familyreltype');
INSERT INTO "auth_permission" VALUES(52,'Can add source media type',18,'add_sourcemediatype');
INSERT INTO "auth_permission" VALUES(53,'Can change source media type',18,'change_sourcemediatype');
INSERT INTO "auth_permission" VALUES(54,'Can delete source media type',18,'delete_sourcemediatype');
INSERT INTO "auth_permission" VALUES(55,'Can add event role type',19,'add_eventroletype');
INSERT INTO "auth_permission" VALUES(56,'Can change event role type',19,'change_eventroletype');
INSERT INTO "auth_permission" VALUES(57,'Can delete event role type',19,'delete_eventroletype');
INSERT INTO "auth_permission" VALUES(58,'Can add note type',20,'add_notetype');
INSERT INTO "auth_permission" VALUES(59,'Can change note type',20,'change_notetype');
INSERT INTO "auth_permission" VALUES(60,'Can delete note type',20,'delete_notetype');
INSERT INTO "auth_permission" VALUES(61,'Can add styled text tag type',21,'add_styledtexttagtype');
INSERT INTO "auth_permission" VALUES(62,'Can change styled text tag type',21,'change_styledtexttagtype');
INSERT INTO "auth_permission" VALUES(63,'Can delete styled text tag type',21,'delete_styledtexttagtype');
INSERT INTO "auth_permission" VALUES(64,'Can add gender type',22,'add_gendertype');
INSERT INTO "auth_permission" VALUES(65,'Can change gender type',22,'change_gendertype');
INSERT INTO "auth_permission" VALUES(66,'Can delete gender type',22,'delete_gendertype');
INSERT INTO "auth_permission" VALUES(67,'Can add lds type',23,'add_ldstype');
INSERT INTO "auth_permission" VALUES(68,'Can change lds type',23,'change_ldstype');
INSERT INTO "auth_permission" VALUES(69,'Can delete lds type',23,'delete_ldstype');
INSERT INTO "auth_permission" VALUES(70,'Can add lds status',24,'add_ldsstatus');
INSERT INTO "auth_permission" VALUES(71,'Can change lds status',24,'change_ldsstatus');
INSERT INTO "auth_permission" VALUES(72,'Can delete lds status',24,'delete_ldsstatus');
INSERT INTO "auth_permission" VALUES(73,'Can add name format type',25,'add_nameformattype');
INSERT INTO "auth_permission" VALUES(74,'Can change name format type',25,'change_nameformattype');
INSERT INTO "auth_permission" VALUES(75,'Can delete name format type',25,'delete_nameformattype');
INSERT INTO "auth_permission" VALUES(76,'Can add calendar type',26,'add_calendartype');
INSERT INTO "auth_permission" VALUES(77,'Can change calendar type',26,'change_calendartype');
INSERT INTO "auth_permission" VALUES(78,'Can delete calendar type',26,'delete_calendartype');
INSERT INTO "auth_permission" VALUES(79,'Can add date modifier type',27,'add_datemodifiertype');
INSERT INTO "auth_permission" VALUES(80,'Can change date modifier type',27,'change_datemodifiertype');
INSERT INTO "auth_permission" VALUES(81,'Can delete date modifier type',27,'delete_datemodifiertype');
INSERT INTO "auth_permission" VALUES(82,'Can add date new year type',28,'add_datenewyeartype');
INSERT INTO "auth_permission" VALUES(83,'Can change date new year type',28,'change_datenewyeartype');
INSERT INTO "auth_permission" VALUES(84,'Can delete date new year type',28,'delete_datenewyeartype');
INSERT INTO "auth_permission" VALUES(85,'Can add theme type',29,'add_themetype');
INSERT INTO "auth_permission" VALUES(86,'Can change theme type',29,'change_themetype');
INSERT INTO "auth_permission" VALUES(87,'Can delete theme type',29,'delete_themetype');
INSERT INTO "auth_permission" VALUES(88,'Can add config',30,'add_config');
INSERT INTO "auth_permission" VALUES(89,'Can change config',30,'change_config');
INSERT INTO "auth_permission" VALUES(90,'Can delete config',30,'delete_config');
INSERT INTO "auth_permission" VALUES(91,'Can add tag',31,'add_tag');
INSERT INTO "auth_permission" VALUES(92,'Can change tag',31,'change_tag');
INSERT INTO "auth_permission" VALUES(93,'Can delete tag',31,'delete_tag');
INSERT INTO "auth_permission" VALUES(94,'Can add my families',32,'add_myfamilies');
INSERT INTO "auth_permission" VALUES(95,'Can change my families',32,'change_myfamilies');
INSERT INTO "auth_permission" VALUES(96,'Can delete my families',32,'delete_myfamilies');
INSERT INTO "auth_permission" VALUES(97,'Can add my parent families',33,'add_myparentfamilies');
INSERT INTO "auth_permission" VALUES(98,'Can change my parent families',33,'change_myparentfamilies');
INSERT INTO "auth_permission" VALUES(99,'Can delete my parent families',33,'delete_myparentfamilies');
INSERT INTO "auth_permission" VALUES(100,'Can add person',34,'add_person');
INSERT INTO "auth_permission" VALUES(101,'Can change person',34,'change_person');
INSERT INTO "auth_permission" VALUES(102,'Can delete person',34,'delete_person');
INSERT INTO "auth_permission" VALUES(103,'Can add family',35,'add_family');
INSERT INTO "auth_permission" VALUES(104,'Can change family',35,'change_family');
INSERT INTO "auth_permission" VALUES(105,'Can delete family',35,'delete_family');
INSERT INTO "auth_permission" VALUES(106,'Can add citation',36,'add_citation');
INSERT INTO "auth_permission" VALUES(107,'Can change citation',36,'change_citation');
INSERT INTO "auth_permission" VALUES(108,'Can delete citation',36,'delete_citation');
INSERT INTO "auth_permission" VALUES(109,'Can add source',37,'add_source');
INSERT INTO "auth_permission" VALUES(110,'Can change source',37,'change_source');
INSERT INTO "auth_permission" VALUES(111,'Can delete source',37,'delete_source');
INSERT INTO "auth_permission" VALUES(112,'Can add event',38,'add_event');
INSERT INTO "auth_permission" VALUES(113,'Can change event',38,'change_event');
INSERT INTO "auth_permission" VALUES(114,'Can delete event',38,'delete_event');
INSERT INTO "auth_permission" VALUES(115,'Can add repository',39,'add_repository');
INSERT INTO "auth_permission" VALUES(116,'Can change repository',39,'change_repository');
INSERT INTO "auth_permission" VALUES(117,'Can delete repository',39,'delete_repository');
INSERT INTO "auth_permission" VALUES(118,'Can add place',40,'add_place');
INSERT INTO "auth_permission" VALUES(119,'Can change place',40,'change_place');
INSERT INTO "auth_permission" VALUES(120,'Can delete place',40,'delete_place');
INSERT INTO "auth_permission" VALUES(121,'Can add media',41,'add_media');
INSERT INTO "auth_permission" VALUES(122,'Can change media',41,'change_media');
INSERT INTO "auth_permission" VALUES(123,'Can delete media',41,'delete_media');
INSERT INTO "auth_permission" VALUES(124,'Can add note',42,'add_note');
INSERT INTO "auth_permission" VALUES(125,'Can change note',42,'change_note');
INSERT INTO "auth_permission" VALUES(126,'Can delete note',42,'delete_note');
INSERT INTO "auth_permission" VALUES(127,'Can add surname',43,'add_surname');
INSERT INTO "auth_permission" VALUES(128,'Can change surname',43,'change_surname');
INSERT INTO "auth_permission" VALUES(129,'Can delete surname',43,'delete_surname');
INSERT INTO "auth_permission" VALUES(130,'Can add name',44,'add_name');
INSERT INTO "auth_permission" VALUES(131,'Can change name',44,'change_name');
INSERT INTO "auth_permission" VALUES(132,'Can delete name',44,'delete_name');
INSERT INTO "auth_permission" VALUES(133,'Can add lds',45,'add_lds');
INSERT INTO "auth_permission" VALUES(134,'Can change lds',45,'change_lds');
INSERT INTO "auth_permission" VALUES(135,'Can delete lds',45,'delete_lds');
INSERT INTO "auth_permission" VALUES(136,'Can add markup',46,'add_markup');
INSERT INTO "auth_permission" VALUES(137,'Can change markup',46,'change_markup');
INSERT INTO "auth_permission" VALUES(138,'Can delete markup',46,'delete_markup');
INSERT INTO "auth_permission" VALUES(139,'Can add source datamap',47,'add_sourcedatamap');
INSERT INTO "auth_permission" VALUES(140,'Can change source datamap',47,'change_sourcedatamap');
INSERT INTO "auth_permission" VALUES(141,'Can delete source datamap',47,'delete_sourcedatamap');
INSERT INTO "auth_permission" VALUES(142,'Can add citation datamap',48,'add_citationdatamap');
INSERT INTO "auth_permission" VALUES(143,'Can change citation datamap',48,'change_citationdatamap');
INSERT INTO "auth_permission" VALUES(144,'Can delete citation datamap',48,'delete_citationdatamap');
INSERT INTO "auth_permission" VALUES(145,'Can add address',49,'add_address');
INSERT INTO "auth_permission" VALUES(146,'Can change address',49,'change_address');
INSERT INTO "auth_permission" VALUES(147,'Can delete address',49,'delete_address');
INSERT INTO "auth_permission" VALUES(148,'Can add location',50,'add_location');
INSERT INTO "auth_permission" VALUES(149,'Can change location',50,'change_location');
INSERT INTO "auth_permission" VALUES(150,'Can delete location',50,'delete_location');
INSERT INTO "auth_permission" VALUES(151,'Can add url',51,'add_url');
INSERT INTO "auth_permission" VALUES(152,'Can change url',51,'change_url');
INSERT INTO "auth_permission" VALUES(153,'Can delete url',51,'delete_url');
INSERT INTO "auth_permission" VALUES(154,'Can add attribute',52,'add_attribute');
INSERT INTO "auth_permission" VALUES(155,'Can change attribute',52,'change_attribute');
INSERT INTO "auth_permission" VALUES(156,'Can delete attribute',52,'delete_attribute');
INSERT INTO "auth_permission" VALUES(157,'Can add log',53,'add_log');
INSERT INTO "auth_permission" VALUES(158,'Can change log',53,'change_log');
INSERT INTO "auth_permission" VALUES(159,'Can delete log',53,'delete_log');
INSERT INTO "auth_permission" VALUES(160,'Can add note ref',54,'add_noteref');
INSERT INTO "auth_permission" VALUES(161,'Can change note ref',54,'change_noteref');
INSERT INTO "auth_permission" VALUES(162,'Can delete note ref',54,'delete_noteref');
INSERT INTO "auth_permission" VALUES(163,'Can add event ref',55,'add_eventref');
INSERT INTO "auth_permission" VALUES(164,'Can change event ref',55,'change_eventref');
INSERT INTO "auth_permission" VALUES(165,'Can delete event ref',55,'delete_eventref');
INSERT INTO "auth_permission" VALUES(166,'Can add repository ref',56,'add_repositoryref');
INSERT INTO "auth_permission" VALUES(167,'Can change repository ref',56,'change_repositoryref');
INSERT INTO "auth_permission" VALUES(168,'Can delete repository ref',56,'delete_repositoryref');
INSERT INTO "auth_permission" VALUES(169,'Can add person ref',57,'add_personref');
INSERT INTO "auth_permission" VALUES(170,'Can change person ref',57,'change_personref');
INSERT INTO "auth_permission" VALUES(171,'Can delete person ref',57,'delete_personref');
INSERT INTO "auth_permission" VALUES(172,'Can add citation ref',58,'add_citationref');
INSERT INTO "auth_permission" VALUES(173,'Can change citation ref',58,'change_citationref');
INSERT INTO "auth_permission" VALUES(174,'Can delete citation ref',58,'delete_citationref');
INSERT INTO "auth_permission" VALUES(175,'Can add child ref',59,'add_childref');
INSERT INTO "auth_permission" VALUES(176,'Can change child ref',59,'change_childref');
INSERT INTO "auth_permission" VALUES(177,'Can delete child ref',59,'delete_childref');
INSERT INTO "auth_permission" VALUES(178,'Can add media ref',60,'add_mediaref');
INSERT INTO "auth_permission" VALUES(179,'Can change media ref',60,'change_mediaref');
INSERT INTO "auth_permission" VALUES(180,'Can delete media ref',60,'delete_mediaref');
INSERT INTO "auth_permission" VALUES(181,'Can add report',61,'add_report');
INSERT INTO "auth_permission" VALUES(182,'Can change report',61,'change_report');
INSERT INTO "auth_permission" VALUES(183,'Can delete report',61,'delete_report');
INSERT INTO "auth_permission" VALUES(184,'Can add result',62,'add_result');
INSERT INTO "auth_permission" VALUES(185,'Can change result',62,'change_result');
INSERT INTO "auth_permission" VALUES(186,'Can delete result',62,'delete_result');
CREATE TABLE "auth_group_permissions" (
    "id" integer NOT NULL PRIMARY KEY,
    "group_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("group_id", "permission_id")
);
CREATE TABLE "auth_group" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL UNIQUE
);
CREATE TABLE "auth_user_user_permissions" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("user_id", "permission_id")
);
CREATE TABLE "auth_user_groups" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id"),
    UNIQUE ("user_id", "group_id")
);
CREATE TABLE "auth_user" (
    "id" integer NOT NULL PRIMARY KEY,
    "username" varchar(30) NOT NULL UNIQUE,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL,
    "email" varchar(75) NOT NULL,
    "password" varchar(128) NOT NULL,
    "is_staff" bool NOT NULL,
    "is_active" bool NOT NULL,
    "is_superuser" bool NOT NULL,
    "last_login" datetime NOT NULL,
    "date_joined" datetime NOT NULL
);
INSERT INTO "auth_user" VALUES(1,'admin','','','bugs@gramps-project.org','sha1$248cf$71082f5ec314e2706d1cc9e44a0d63b953ba1d08',1,1,1,'2012-07-31 07:59:41.498044','2012-07-31 07:58:28.096063');
INSERT INTO "auth_user" VALUES(2,'admin1','','','bugs@gramps-project.org','sha1$bd368$2e83f9d34578f66402e62b698950adae05f4d6bf',1,1,1,'2012-07-31 07:58:37.492571','2012-07-31 07:58:37.492571');
CREATE TABLE "auth_message" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "message" text NOT NULL
);
CREATE TABLE "django_content_type" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "app_label" varchar(100) NOT NULL,
    "model" varchar(100) NOT NULL,
    UNIQUE ("app_label", "model")
);
INSERT INTO "django_content_type" VALUES(1,'permission','auth','permission');
INSERT INTO "django_content_type" VALUES(2,'group','auth','group');
INSERT INTO "django_content_type" VALUES(3,'user','auth','user');
INSERT INTO "django_content_type" VALUES(4,'message','auth','message');
INSERT INTO "django_content_type" VALUES(5,'content type','contenttypes','contenttype');
INSERT INTO "django_content_type" VALUES(6,'session','sessions','session');
INSERT INTO "django_content_type" VALUES(7,'site','sites','site');
INSERT INTO "django_content_type" VALUES(8,'log entry','admin','logentry');
INSERT INTO "django_content_type" VALUES(9,'profile','grampsdb','profile');
INSERT INTO "django_content_type" VALUES(10,'name type','grampsdb','nametype');
INSERT INTO "django_content_type" VALUES(11,'name origin type','grampsdb','nameorigintype');
INSERT INTO "django_content_type" VALUES(12,'attribute type','grampsdb','attributetype');
INSERT INTO "django_content_type" VALUES(13,'url type','grampsdb','urltype');
INSERT INTO "django_content_type" VALUES(14,'child ref type','grampsdb','childreftype');
INSERT INTO "django_content_type" VALUES(15,'repository type','grampsdb','repositorytype');
INSERT INTO "django_content_type" VALUES(16,'event type','grampsdb','eventtype');
INSERT INTO "django_content_type" VALUES(17,'family rel type','grampsdb','familyreltype');
INSERT INTO "django_content_type" VALUES(18,'source media type','grampsdb','sourcemediatype');
INSERT INTO "django_content_type" VALUES(19,'event role type','grampsdb','eventroletype');
INSERT INTO "django_content_type" VALUES(20,'note type','grampsdb','notetype');
INSERT INTO "django_content_type" VALUES(21,'styled text tag type','grampsdb','styledtexttagtype');
INSERT INTO "django_content_type" VALUES(22,'gender type','grampsdb','gendertype');
INSERT INTO "django_content_type" VALUES(23,'lds type','grampsdb','ldstype');
INSERT INTO "django_content_type" VALUES(24,'lds status','grampsdb','ldsstatus');
INSERT INTO "django_content_type" VALUES(25,'name format type','grampsdb','nameformattype');
INSERT INTO "django_content_type" VALUES(26,'calendar type','grampsdb','calendartype');
INSERT INTO "django_content_type" VALUES(27,'date modifier type','grampsdb','datemodifiertype');
INSERT INTO "django_content_type" VALUES(28,'date new year type','grampsdb','datenewyeartype');
INSERT INTO "django_content_type" VALUES(29,'theme type','grampsdb','themetype');
INSERT INTO "django_content_type" VALUES(30,'config','grampsdb','config');
INSERT INTO "django_content_type" VALUES(31,'tag','grampsdb','tag');
INSERT INTO "django_content_type" VALUES(32,'my families','grampsdb','myfamilies');
INSERT INTO "django_content_type" VALUES(33,'my parent families','grampsdb','myparentfamilies');
INSERT INTO "django_content_type" VALUES(34,'person','grampsdb','person');
INSERT INTO "django_content_type" VALUES(35,'family','grampsdb','family');
INSERT INTO "django_content_type" VALUES(36,'citation','grampsdb','citation');
INSERT INTO "django_content_type" VALUES(37,'source','grampsdb','source');
INSERT INTO "django_content_type" VALUES(38,'event','grampsdb','event');
INSERT INTO "django_content_type" VALUES(39,'repository','grampsdb','repository');
INSERT INTO "django_content_type" VALUES(40,'place','grampsdb','place');
INSERT INTO "django_content_type" VALUES(41,'media','grampsdb','media');
INSERT INTO "django_content_type" VALUES(42,'note','grampsdb','note');
INSERT INTO "django_content_type" VALUES(43,'surname','grampsdb','surname');
INSERT INTO "django_content_type" VALUES(44,'name','grampsdb','name');
INSERT INTO "django_content_type" VALUES(45,'lds','grampsdb','lds');
INSERT INTO "django_content_type" VALUES(46,'markup','grampsdb','markup');
INSERT INTO "django_content_type" VALUES(47,'source datamap','grampsdb','sourcedatamap');
INSERT INTO "django_content_type" VALUES(48,'citation datamap','grampsdb','citationdatamap');
INSERT INTO "django_content_type" VALUES(49,'address','grampsdb','address');
INSERT INTO "django_content_type" VALUES(50,'location','grampsdb','location');
INSERT INTO "django_content_type" VALUES(51,'url','grampsdb','url');
INSERT INTO "django_content_type" VALUES(52,'attribute','grampsdb','attribute');
INSERT INTO "django_content_type" VALUES(53,'log','grampsdb','log');
INSERT INTO "django_content_type" VALUES(54,'note ref','grampsdb','noteref');
INSERT INTO "django_content_type" VALUES(55,'event ref','grampsdb','eventref');
INSERT INTO "django_content_type" VALUES(56,'repository ref','grampsdb','repositoryref');
INSERT INTO "django_content_type" VALUES(57,'person ref','grampsdb','personref');
INSERT INTO "django_content_type" VALUES(58,'citation ref','grampsdb','citationref');
INSERT INTO "django_content_type" VALUES(59,'child ref','grampsdb','childref');
INSERT INTO "django_content_type" VALUES(60,'media ref','grampsdb','mediaref');
INSERT INTO "django_content_type" VALUES(61,'report','grampsdb','report');
INSERT INTO "django_content_type" VALUES(62,'result','grampsdb','result');
CREATE TABLE "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" datetime NOT NULL
);
INSERT INTO "django_session" VALUES('46ed8bcde91325679bf722ca3eb10d54','YTJkY2YzOGM0MzQ0MzY4YjExZDZhODZjOTdhZjAxMDkxNWU5MTM0NjqAAn1xAS4=
','2012-08-14 08:01:51.583296');
CREATE TABLE "django_site" (
    "id" integer NOT NULL PRIMARY KEY,
    "domain" varchar(100) NOT NULL,
    "name" varchar(50) NOT NULL
);
INSERT INTO "django_site" VALUES(1,'example.com','example.com');
CREATE TABLE "django_admin_log" (
    "id" integer NOT NULL PRIMARY KEY,
    "action_time" datetime NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "content_type_id" integer REFERENCES "django_content_type" ("id"),
    "object_id" text,
    "object_repr" varchar(200) NOT NULL,
    "action_flag" smallint unsigned NOT NULL,
    "change_message" text NOT NULL
);
CREATE TABLE "grampsdb_profile" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id"),
    "theme_type_id" integer NOT NULL
);
INSERT INTO "grampsdb_profile" VALUES(1,1,1);
INSERT INTO "grampsdb_profile" VALUES(2,2,1);
CREATE TABLE "grampsdb_nametype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_nametype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_nametype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_nametype" VALUES(3,'Also Known As',1);
INSERT INTO "grampsdb_nametype" VALUES(4,'Birth Name',2);
INSERT INTO "grampsdb_nametype" VALUES(5,'Married Name',3);
CREATE TABLE "grampsdb_nameorigintype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_nameorigintype" VALUES(1,'',1);
INSERT INTO "grampsdb_nameorigintype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_nameorigintype" VALUES(3,'Feudal',7);
INSERT INTO "grampsdb_nameorigintype" VALUES(4,'Given',3);
INSERT INTO "grampsdb_nameorigintype" VALUES(5,'Inherited',2);
INSERT INTO "grampsdb_nameorigintype" VALUES(6,'Location',12);
INSERT INTO "grampsdb_nameorigintype" VALUES(7,'Matrilineal',10);
INSERT INTO "grampsdb_nameorigintype" VALUES(8,'Matronymic',6);
INSERT INTO "grampsdb_nameorigintype" VALUES(9,'Occupation',11);
INSERT INTO "grampsdb_nameorigintype" VALUES(10,'Patrilineal',9);
INSERT INTO "grampsdb_nameorigintype" VALUES(11,'Patronymic',5);
INSERT INTO "grampsdb_nameorigintype" VALUES(12,'Pseudonym',8);
INSERT INTO "grampsdb_nameorigintype" VALUES(13,'Taken',4);
INSERT INTO "grampsdb_nameorigintype" VALUES(14,'Unknown',-1);
CREATE TABLE "grampsdb_attributetype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_attributetype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_attributetype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_attributetype" VALUES(3,'Caste',1);
INSERT INTO "grampsdb_attributetype" VALUES(4,'Description',2);
INSERT INTO "grampsdb_attributetype" VALUES(5,'Identification Number',3);
INSERT INTO "grampsdb_attributetype" VALUES(6,'National Origin',4);
INSERT INTO "grampsdb_attributetype" VALUES(7,'Number of Children',5);
INSERT INTO "grampsdb_attributetype" VALUES(8,'Social Security Number',6);
INSERT INTO "grampsdb_attributetype" VALUES(9,'Nickname',7);
INSERT INTO "grampsdb_attributetype" VALUES(10,'Cause',8);
INSERT INTO "grampsdb_attributetype" VALUES(11,'Agency',9);
INSERT INTO "grampsdb_attributetype" VALUES(12,'Age',10);
INSERT INTO "grampsdb_attributetype" VALUES(13,'Father Age',11);
INSERT INTO "grampsdb_attributetype" VALUES(14,'Mother Age',12);
INSERT INTO "grampsdb_attributetype" VALUES(15,'Witness',13);
INSERT INTO "grampsdb_attributetype" VALUES(16,'Time',14);
CREATE TABLE "grampsdb_urltype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_urltype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_urltype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_urltype" VALUES(3,'E-mail',1);
INSERT INTO "grampsdb_urltype" VALUES(4,'Web Home',2);
INSERT INTO "grampsdb_urltype" VALUES(5,'Web Search',3);
INSERT INTO "grampsdb_urltype" VALUES(6,'FTP',4);
CREATE TABLE "grampsdb_childreftype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_childreftype" VALUES(1,'None',0);
INSERT INTO "grampsdb_childreftype" VALUES(2,'Birth',1);
INSERT INTO "grampsdb_childreftype" VALUES(3,'Adopted',2);
INSERT INTO "grampsdb_childreftype" VALUES(4,'Stepchild',3);
INSERT INTO "grampsdb_childreftype" VALUES(5,'Sponsored',4);
INSERT INTO "grampsdb_childreftype" VALUES(6,'Foster',5);
INSERT INTO "grampsdb_childreftype" VALUES(7,'Unknown',6);
INSERT INTO "grampsdb_childreftype" VALUES(8,'Custom',7);
CREATE TABLE "grampsdb_repositorytype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_repositorytype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_repositorytype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_repositorytype" VALUES(3,'Library',1);
INSERT INTO "grampsdb_repositorytype" VALUES(4,'Cemetery',2);
INSERT INTO "grampsdb_repositorytype" VALUES(5,'Church',3);
INSERT INTO "grampsdb_repositorytype" VALUES(6,'Archive',4);
INSERT INTO "grampsdb_repositorytype" VALUES(7,'Album',5);
INSERT INTO "grampsdb_repositorytype" VALUES(8,'Web site',6);
INSERT INTO "grampsdb_repositorytype" VALUES(9,'Bookstore',7);
INSERT INTO "grampsdb_repositorytype" VALUES(10,'Collection',8);
INSERT INTO "grampsdb_repositorytype" VALUES(11,'Safe',9);
CREATE TABLE "grampsdb_eventtype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_eventtype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_eventtype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_eventtype" VALUES(3,'Adopted',11);
INSERT INTO "grampsdb_eventtype" VALUES(4,'Birth',12);
INSERT INTO "grampsdb_eventtype" VALUES(5,'Death',13);
INSERT INTO "grampsdb_eventtype" VALUES(6,'Adult Christening',14);
INSERT INTO "grampsdb_eventtype" VALUES(7,'Baptism',15);
INSERT INTO "grampsdb_eventtype" VALUES(8,'Bar Mitzvah',16);
INSERT INTO "grampsdb_eventtype" VALUES(9,'Bas Mitzvah',17);
INSERT INTO "grampsdb_eventtype" VALUES(10,'Blessing',18);
INSERT INTO "grampsdb_eventtype" VALUES(11,'Burial',19);
INSERT INTO "grampsdb_eventtype" VALUES(12,'Cause Of Death',20);
INSERT INTO "grampsdb_eventtype" VALUES(13,'Census',21);
INSERT INTO "grampsdb_eventtype" VALUES(14,'Christening',22);
INSERT INTO "grampsdb_eventtype" VALUES(15,'Confirmation',23);
INSERT INTO "grampsdb_eventtype" VALUES(16,'Cremation',24);
INSERT INTO "grampsdb_eventtype" VALUES(17,'Degree',25);
INSERT INTO "grampsdb_eventtype" VALUES(18,'Education',26);
INSERT INTO "grampsdb_eventtype" VALUES(19,'Elected',27);
INSERT INTO "grampsdb_eventtype" VALUES(20,'Emigration',28);
INSERT INTO "grampsdb_eventtype" VALUES(21,'First Communion',29);
INSERT INTO "grampsdb_eventtype" VALUES(22,'Immigration',30);
INSERT INTO "grampsdb_eventtype" VALUES(23,'Graduation',31);
INSERT INTO "grampsdb_eventtype" VALUES(24,'Medical Information',32);
INSERT INTO "grampsdb_eventtype" VALUES(25,'Military Service',33);
INSERT INTO "grampsdb_eventtype" VALUES(26,'Naturalization',34);
INSERT INTO "grampsdb_eventtype" VALUES(27,'Nobility Title',35);
INSERT INTO "grampsdb_eventtype" VALUES(28,'Number of Marriages',36);
INSERT INTO "grampsdb_eventtype" VALUES(29,'Occupation',37);
INSERT INTO "grampsdb_eventtype" VALUES(30,'Ordination',38);
INSERT INTO "grampsdb_eventtype" VALUES(31,'Probate',39);
INSERT INTO "grampsdb_eventtype" VALUES(32,'Property',40);
INSERT INTO "grampsdb_eventtype" VALUES(33,'Religion',41);
INSERT INTO "grampsdb_eventtype" VALUES(34,'Residence',42);
INSERT INTO "grampsdb_eventtype" VALUES(35,'Retirement',43);
INSERT INTO "grampsdb_eventtype" VALUES(36,'Will',44);
INSERT INTO "grampsdb_eventtype" VALUES(37,'Marriage',1);
INSERT INTO "grampsdb_eventtype" VALUES(38,'Marriage Settlement',2);
INSERT INTO "grampsdb_eventtype" VALUES(39,'Marriage License',3);
INSERT INTO "grampsdb_eventtype" VALUES(40,'Marriage Contract',4);
INSERT INTO "grampsdb_eventtype" VALUES(41,'Marriage Banns',5);
INSERT INTO "grampsdb_eventtype" VALUES(42,'Engagement',6);
INSERT INTO "grampsdb_eventtype" VALUES(43,'Divorce',7);
INSERT INTO "grampsdb_eventtype" VALUES(44,'Divorce Filing',8);
INSERT INTO "grampsdb_eventtype" VALUES(45,'Annulment',9);
INSERT INTO "grampsdb_eventtype" VALUES(46,'Alternate Marriage',10);
INSERT INTO "grampsdb_eventtype" VALUES(47,'',0);
CREATE TABLE "grampsdb_familyreltype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_familyreltype" VALUES(1,'Unknown',3);
INSERT INTO "grampsdb_familyreltype" VALUES(2,'Custom',4);
INSERT INTO "grampsdb_familyreltype" VALUES(3,'Civil Union',2);
INSERT INTO "grampsdb_familyreltype" VALUES(4,'Unmarried',1);
INSERT INTO "grampsdb_familyreltype" VALUES(5,'Married',0);
CREATE TABLE "grampsdb_sourcemediatype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_sourcemediatype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_sourcemediatype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_sourcemediatype" VALUES(3,'Audio',1);
INSERT INTO "grampsdb_sourcemediatype" VALUES(4,'Book',2);
INSERT INTO "grampsdb_sourcemediatype" VALUES(5,'Card',3);
INSERT INTO "grampsdb_sourcemediatype" VALUES(6,'Electronic',4);
INSERT INTO "grampsdb_sourcemediatype" VALUES(7,'Fiche',5);
INSERT INTO "grampsdb_sourcemediatype" VALUES(8,'Film',6);
INSERT INTO "grampsdb_sourcemediatype" VALUES(9,'Magazine',7);
INSERT INTO "grampsdb_sourcemediatype" VALUES(10,'Manuscript',8);
INSERT INTO "grampsdb_sourcemediatype" VALUES(11,'Map',9);
INSERT INTO "grampsdb_sourcemediatype" VALUES(12,'Newspaper',10);
INSERT INTO "grampsdb_sourcemediatype" VALUES(13,'Photo',11);
INSERT INTO "grampsdb_sourcemediatype" VALUES(14,'Tombstone',12);
INSERT INTO "grampsdb_sourcemediatype" VALUES(15,'Video',13);
CREATE TABLE "grampsdb_eventroletype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_eventroletype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_eventroletype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_eventroletype" VALUES(3,'Primary',1);
INSERT INTO "grampsdb_eventroletype" VALUES(4,'Clergy',2);
INSERT INTO "grampsdb_eventroletype" VALUES(5,'Celebrant',3);
INSERT INTO "grampsdb_eventroletype" VALUES(6,'Aide',4);
INSERT INTO "grampsdb_eventroletype" VALUES(7,'Bride',5);
INSERT INTO "grampsdb_eventroletype" VALUES(8,'Groom',6);
INSERT INTO "grampsdb_eventroletype" VALUES(9,'Witness',7);
INSERT INTO "grampsdb_eventroletype" VALUES(10,'Family',8);
INSERT INTO "grampsdb_eventroletype" VALUES(11,'Informant',9);
CREATE TABLE "grampsdb_notetype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_notetype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_notetype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_notetype" VALUES(3,'General',1);
INSERT INTO "grampsdb_notetype" VALUES(4,'Research',2);
INSERT INTO "grampsdb_notetype" VALUES(5,'Transcript',3);
INSERT INTO "grampsdb_notetype" VALUES(6,'Source text',21);
INSERT INTO "grampsdb_notetype" VALUES(7,'Citation',22);
INSERT INTO "grampsdb_notetype" VALUES(8,'Report',23);
INSERT INTO "grampsdb_notetype" VALUES(9,'Html code',24);
INSERT INTO "grampsdb_notetype" VALUES(10,'Person Note',4);
INSERT INTO "grampsdb_notetype" VALUES(11,'Name Note',20);
INSERT INTO "grampsdb_notetype" VALUES(12,'Attribute Note',5);
INSERT INTO "grampsdb_notetype" VALUES(13,'Address Note',6);
INSERT INTO "grampsdb_notetype" VALUES(14,'Association Note',7);
INSERT INTO "grampsdb_notetype" VALUES(15,'LDS Note',8);
INSERT INTO "grampsdb_notetype" VALUES(16,'Family Note',9);
INSERT INTO "grampsdb_notetype" VALUES(17,'Event Note',10);
INSERT INTO "grampsdb_notetype" VALUES(18,'Event Reference Note',11);
INSERT INTO "grampsdb_notetype" VALUES(19,'Source Note',12);
INSERT INTO "grampsdb_notetype" VALUES(20,'Source Reference Note',13);
INSERT INTO "grampsdb_notetype" VALUES(21,'Place Note',14);
INSERT INTO "grampsdb_notetype" VALUES(22,'Repository Note',15);
INSERT INTO "grampsdb_notetype" VALUES(23,'Repository Reference Note',16);
INSERT INTO "grampsdb_notetype" VALUES(24,'Media Note',17);
INSERT INTO "grampsdb_notetype" VALUES(25,'Media Reference Note',18);
INSERT INTO "grampsdb_notetype" VALUES(26,'Child Reference Note',19);
INSERT INTO "grampsdb_notetype" VALUES(27,'GEDCOM import',0);
CREATE TABLE "grampsdb_styledtexttagtype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(1,'bold',0);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(2,'italic',1);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(3,'underline',2);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(4,'fontface',3);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(5,'fontsize',4);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(6,'fontcolor',5);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(7,'highlight',6);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(8,'superscript',7);
INSERT INTO "grampsdb_styledtexttagtype" VALUES(9,'link',8);
CREATE TABLE "grampsdb_gendertype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_gendertype" VALUES(1,'Unknown',2);
INSERT INTO "grampsdb_gendertype" VALUES(2,'Male',1);
INSERT INTO "grampsdb_gendertype" VALUES(3,'Female',0);
CREATE TABLE "grampsdb_ldstype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_ldstype" VALUES(1,'Baptism',0);
INSERT INTO "grampsdb_ldstype" VALUES(2,'Endowment',1);
INSERT INTO "grampsdb_ldstype" VALUES(3,'Seal to Parents',2);
INSERT INTO "grampsdb_ldstype" VALUES(4,'Seal to Spouse',3);
INSERT INTO "grampsdb_ldstype" VALUES(5,'Confirmation',4);
CREATE TABLE "grampsdb_ldsstatus" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_ldsstatus" VALUES(1,'None',0);
INSERT INTO "grampsdb_ldsstatus" VALUES(2,'BIC',1);
INSERT INTO "grampsdb_ldsstatus" VALUES(3,'Canceled',2);
INSERT INTO "grampsdb_ldsstatus" VALUES(4,'Child',3);
INSERT INTO "grampsdb_ldsstatus" VALUES(5,'Cleared',4);
INSERT INTO "grampsdb_ldsstatus" VALUES(6,'Completed',5);
INSERT INTO "grampsdb_ldsstatus" VALUES(7,'Dns',6);
INSERT INTO "grampsdb_ldsstatus" VALUES(8,'Infant',7);
INSERT INTO "grampsdb_ldsstatus" VALUES(9,'Pre 1970',8);
INSERT INTO "grampsdb_ldsstatus" VALUES(10,'Qualified',9);
INSERT INTO "grampsdb_ldsstatus" VALUES(11,'DNSCAN',10);
INSERT INTO "grampsdb_ldsstatus" VALUES(12,'Stillborn',11);
INSERT INTO "grampsdb_ldsstatus" VALUES(13,'Submitted',12);
INSERT INTO "grampsdb_ldsstatus" VALUES(14,'Uncleared',13);
CREATE TABLE "grampsdb_nameformattype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_nameformattype" VALUES(1,'Default format',0);
INSERT INTO "grampsdb_nameformattype" VALUES(2,'Surname, Given Patronymic',1);
INSERT INTO "grampsdb_nameformattype" VALUES(3,'Given Surname',2);
INSERT INTO "grampsdb_nameformattype" VALUES(4,'Patronymic, Given',3);
CREATE TABLE "grampsdb_calendartype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
CREATE TABLE "grampsdb_datemodifiertype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
CREATE TABLE "grampsdb_datenewyeartype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
CREATE TABLE "grampsdb_themetype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_themetype" VALUES(1,'Web_Mainz.css',0);
INSERT INTO "grampsdb_themetype" VALUES(2,'Web_Basic-Ash.css',1);
INSERT INTO "grampsdb_themetype" VALUES(3,'Web_Basic-Cypress.css',2);
INSERT INTO "grampsdb_themetype" VALUES(4,'Web_Nebraska.css',3);
INSERT INTO "grampsdb_themetype" VALUES(5,'Web_Basic-Lilac.css',4);
INSERT INTO "grampsdb_themetype" VALUES(6,'Web_Print-Default.css',5);
INSERT INTO "grampsdb_themetype" VALUES(7,'Web_Basic-Peach.css',6);
INSERT INTO "grampsdb_themetype" VALUES(8,'Web_Visually.css',7);
INSERT INTO "grampsdb_themetype" VALUES(9,'Web_Basic-Spruce.css',8);
CREATE TABLE "grampsdb_config" (
    "id" integer NOT NULL PRIMARY KEY,
    "setting" varchar(50) NOT NULL,
    "description" text,
    "value_type" varchar(80) NOT NULL,
    "value" text NOT NULL
);
INSERT INTO "grampsdb_config" VALUES(1,'sitename','site name of family tree','str','Gramps-Connect');
INSERT INTO "grampsdb_config" VALUES(2,'db_version','database scheme version','str','0.6.1');
INSERT INTO "grampsdb_config" VALUES(3,'db_created','database creation date/time','str','2012-07-31 07:56');
INSERT INTO "grampsdb_config" VALUES(4,'htmlview.url-handler',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(5,'htmlview.start-url',NULL,'str','http://gramps-project.org');
INSERT INTO "grampsdb_config" VALUES(6,'paths.recent-export-dir',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(7,'paths.report-directory',NULL,'unicode','/home/dblank');
INSERT INTO "grampsdb_config" VALUES(8,'paths.quick-backup-filename',NULL,'str','%(filename)s_%(year)d-%(month)02d-%(day)02d.%(extension)s');
INSERT INTO "grampsdb_config" VALUES(9,'paths.recent-import-dir',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(10,'paths.quick-backup-directory',NULL,'unicode','/home/dblank');
INSERT INTO "grampsdb_config" VALUES(11,'paths.recent-file',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(12,'paths.website-directory',NULL,'unicode','/home/dblank');
INSERT INTO "grampsdb_config" VALUES(13,'preferences.family-warn',NULL,'bool','True');
INSERT INTO "grampsdb_config" VALUES(14,'preferences.no-surname-text',NULL,'unicode','[Missing Surname]');
INSERT INTO "grampsdb_config" VALUES(15,'preferences.family-relation-type',NULL,'int','3');
INSERT INTO "grampsdb_config" VALUES(16,'preferences.private-surname-text',NULL,'unicode','[Living]');
INSERT INTO "grampsdb_config" VALUES(17,'preferences.fprefix',NULL,'str','F%04d');
INSERT INTO "grampsdb_config" VALUES(18,'preferences.default-source',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(19,'preferences.calendar-format-report',NULL,'int','0');
INSERT INTO "grampsdb_config" VALUES(20,'preferences.oprefix',NULL,'str','O%04d');
INSERT INTO "grampsdb_config" VALUES(21,'preferences.nprefix',NULL,'str','N%04d');
INSERT INTO "grampsdb_config" VALUES(22,'preferences.use-last-view',NULL,'bool','True');
INSERT INTO "grampsdb_config" VALUES(23,'preferences.paper-preference',NULL,'str','Letter');
INSERT INTO "grampsdb_config" VALUES(24,'preferences.use-bsddb3',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(25,'preferences.hide-ep-msg',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(26,'preferences.iprefix',NULL,'str','I%04d');
INSERT INTO "grampsdb_config" VALUES(27,'preferences.rprefix',NULL,'str','R%04d');
INSERT INTO "grampsdb_config" VALUES(28,'preferences.sprefix',NULL,'str','S%04d');
INSERT INTO "grampsdb_config" VALUES(29,'preferences.no-given-text',NULL,'unicode','[Missing Given Name]');
INSERT INTO "grampsdb_config" VALUES(30,'preferences.paper-metric',NULL,'int','0');
INSERT INTO "grampsdb_config" VALUES(31,'preferences.age-display-precision',NULL,'int','1');
INSERT INTO "grampsdb_config" VALUES(32,'preferences.cprefix',NULL,'str','C%04d');
INSERT INTO "grampsdb_config" VALUES(33,'preferences.invalid-date-format',NULL,'str','<b>%s</b>');
INSERT INTO "grampsdb_config" VALUES(34,'preferences.last-views',NULL,'list','[]');
INSERT INTO "grampsdb_config" VALUES(35,'preferences.pprefix',NULL,'str','P%04d');
INSERT INTO "grampsdb_config" VALUES(36,'preferences.eprefix',NULL,'str','E%04d');
INSERT INTO "grampsdb_config" VALUES(37,'preferences.name-format',NULL,'int','1');
INSERT INTO "grampsdb_config" VALUES(38,'preferences.private-record-text',NULL,'unicode','[Private Record]');
INSERT INTO "grampsdb_config" VALUES(39,'preferences.online-maps',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(40,'preferences.no-record-text',NULL,'unicode','[Missing Record]');
INSERT INTO "grampsdb_config" VALUES(41,'preferences.date-format',NULL,'int','0');
INSERT INTO "grampsdb_config" VALUES(42,'preferences.last-view',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(43,'preferences.patronimic-surname',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(44,'preferences.private-given-text',NULL,'unicode','[Living]');
INSERT INTO "grampsdb_config" VALUES(45,'plugin.hiddenplugins',NULL,'list','[''htmlview'']');
INSERT INTO "grampsdb_config" VALUES(46,'plugin.addonplugins',NULL,'list','[]');
INSERT INTO "grampsdb_config" VALUES(47,'researcher.researcher-locality',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(48,'researcher.researcher-country',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(49,'researcher.researcher-name',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(50,'researcher.researcher-phone',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(51,'researcher.researcher-email',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(52,'researcher.researcher-state',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(53,'researcher.researcher-postal',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(54,'researcher.researcher-city',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(55,'researcher.researcher-addr',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(56,'export.proxy-order',NULL,'list','[[''privacy'', 0], [''living'', 0], [''person'', 0], [''note'', 0], [''reference'', 0]]');
INSERT INTO "grampsdb_config" VALUES(57,'behavior.use-tips',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(58,'behavior.generation-depth',NULL,'int','15');
INSERT INTO "grampsdb_config" VALUES(59,'behavior.last-check-for-updates',NULL,'str','1970/01/01');
INSERT INTO "grampsdb_config" VALUES(60,'behavior.startup',NULL,'int','0');
INSERT INTO "grampsdb_config" VALUES(61,'behavior.autoload',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(62,'behavior.pop-plugin-status',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(63,'behavior.do-not-show-previously-seen-updates',NULL,'bool','True');
INSERT INTO "grampsdb_config" VALUES(64,'behavior.check-for-updates',NULL,'int','0');
INSERT INTO "grampsdb_config" VALUES(65,'behavior.recent-export-type',NULL,'int','1');
INSERT INTO "grampsdb_config" VALUES(66,'behavior.addmedia-image-dir',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(67,'behavior.date-about-range',NULL,'int','50');
INSERT INTO "grampsdb_config" VALUES(68,'behavior.date-after-range',NULL,'int','50');
INSERT INTO "grampsdb_config" VALUES(69,'behavior.owner-warn',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(70,'behavior.date-before-range',NULL,'int','50');
INSERT INTO "grampsdb_config" VALUES(71,'behavior.min-generation-years',NULL,'int','13');
INSERT INTO "grampsdb_config" VALUES(72,'behavior.welcome',NULL,'int','100');
INSERT INTO "grampsdb_config" VALUES(73,'behavior.max-sib-age-diff',NULL,'int','20');
INSERT INTO "grampsdb_config" VALUES(74,'behavior.previously-seen-updates',NULL,'list','[]');
INSERT INTO "grampsdb_config" VALUES(75,'behavior.addmedia-relative-path',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(76,'behavior.spellcheck',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(77,'behavior.surname-guessing',NULL,'int','0');
INSERT INTO "grampsdb_config" VALUES(78,'behavior.check-for-update-types',NULL,'list','[''new'']');
INSERT INTO "grampsdb_config" VALUES(79,'behavior.avg-generation-gap',NULL,'int','20');
INSERT INTO "grampsdb_config" VALUES(80,'behavior.database-path',NULL,'unicode','/home/dblank/.gramps/grampsdb');
INSERT INTO "grampsdb_config" VALUES(81,'behavior.betawarn',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(82,'behavior.max-age-prob-alive',NULL,'int','110');
INSERT INTO "grampsdb_config" VALUES(83,'behavior.web-search-url',NULL,'str','http://google.com/#&q=%(text)s');
INSERT INTO "grampsdb_config" VALUES(84,'interface.family-height',NULL,'int','500');
INSERT INTO "grampsdb_config" VALUES(85,'interface.sidebar-text',NULL,'bool','True');
INSERT INTO "grampsdb_config" VALUES(86,'interface.source-ref-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(87,'interface.address-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(88,'interface.mapservice',NULL,'str','OpenStreetMap');
INSERT INTO "grampsdb_config" VALUES(89,'interface.pedview-layout',NULL,'int','0');
INSERT INTO "grampsdb_config" VALUES(90,'interface.family-width',NULL,'int','700');
INSERT INTO "grampsdb_config" VALUES(91,'interface.toolbar-on',NULL,'bool','True');
INSERT INTO "grampsdb_config" VALUES(92,'interface.citation-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(93,'interface.location-height',NULL,'int','250');
INSERT INTO "grampsdb_config" VALUES(94,'interface.person-ref-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(95,'interface.address-width',NULL,'int','650');
INSERT INTO "grampsdb_config" VALUES(96,'interface.edit-rule-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(97,'interface.filter-editor-width',NULL,'int','400');
INSERT INTO "grampsdb_config" VALUES(98,'interface.child-ref-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(99,'interface.person-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(100,'interface.repo-width',NULL,'int','650');
INSERT INTO "grampsdb_config" VALUES(101,'interface.pedview-tree-size',NULL,'int','5');
INSERT INTO "grampsdb_config" VALUES(102,'interface.citation-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(103,'interface.edit-rule-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(104,'interface.place-width',NULL,'int','650');
INSERT INTO "grampsdb_config" VALUES(105,'interface.place-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(106,'interface.source-ref-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(107,'interface.view',NULL,'bool','True');
INSERT INTO "grampsdb_config" VALUES(108,'interface.source-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(109,'interface.clipboard-height',NULL,'int','300');
INSERT INTO "grampsdb_config" VALUES(110,'interface.fullscreen',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(111,'interface.attribute-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(112,'interface.lds-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(113,'interface.edit-filter-width',NULL,'int','500');
INSERT INTO "grampsdb_config" VALUES(114,'interface.clipboard-width',NULL,'int','300');
INSERT INTO "grampsdb_config" VALUES(115,'interface.media-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(116,'interface.person-ref-height',NULL,'int','350');
INSERT INTO "grampsdb_config" VALUES(117,'interface.citation-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(118,'interface.person-width',NULL,'int','750');
INSERT INTO "grampsdb_config" VALUES(119,'interface.lds-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(120,'interface.name-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(121,'interface.event-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(122,'interface.child-ref-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(123,'interface.filter',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(124,'interface.repo-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(125,'interface.media-ref-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(126,'interface.family-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(127,'interface.pedview-show-marriage',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(128,'interface.height',NULL,'int','500');
INSERT INTO "grampsdb_config" VALUES(129,'interface.media-width',NULL,'int','650');
INSERT INTO "grampsdb_config" VALUES(130,'interface.event-ref-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(131,'interface.repo-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(132,'interface.media-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(133,'interface.width',NULL,'int','775');
INSERT INTO "grampsdb_config" VALUES(134,'interface.size-checked',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(135,'interface.media-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(136,'interface.source-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(137,'interface.surname-box-height',NULL,'int','150');
INSERT INTO "grampsdb_config" VALUES(138,'interface.repo-ref-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(139,'interface.name-height',NULL,'int','350');
INSERT INTO "grampsdb_config" VALUES(140,'interface.event-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(141,'interface.note-width',NULL,'int','700');
INSERT INTO "grampsdb_config" VALUES(142,'interface.statusbar',NULL,'int','1');
INSERT INTO "grampsdb_config" VALUES(143,'interface.person-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(144,'interface.note-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(145,'interface.view-categories',NULL,'list','[''Gramplets'', ''People'', ''Relationships'', ''Families'', ''Ancestry'', ''Events'', ''Places'', ''Geography'', ''Sources'', ''Citations'', ''Repositories'', ''Media'', ''Notes'']');
INSERT INTO "grampsdb_config" VALUES(146,'interface.repo-ref-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(147,'interface.event-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(148,'interface.note-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(149,'interface.person-height',NULL,'int','550');
INSERT INTO "grampsdb_config" VALUES(150,'interface.repo-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(151,'interface.attribute-height',NULL,'int','350');
INSERT INTO "grampsdb_config" VALUES(152,'interface.event-ref-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(153,'interface.source-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(154,'interface.edit-filter-height',NULL,'int','420');
INSERT INTO "grampsdb_config" VALUES(155,'interface.pedview-tree-direction',NULL,'int','2');
INSERT INTO "grampsdb_config" VALUES(156,'interface.family-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(157,'interface.source-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(158,'interface.url-height',NULL,'int','150');
INSERT INTO "grampsdb_config" VALUES(159,'interface.filter-editor-height',NULL,'int','350');
INSERT INTO "grampsdb_config" VALUES(160,'interface.media-ref-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(161,'interface.pedview-show-unknown-people',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(162,'interface.location-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(163,'interface.place-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(164,'interface.citation-sel-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(165,'interface.pedview-show-images',NULL,'bool','True');
INSERT INTO "grampsdb_config" VALUES(166,'interface.url-width',NULL,'int','600');
INSERT INTO "grampsdb_config" VALUES(167,'interface.event-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(168,'interface.note-height',NULL,'int','500');
INSERT INTO "grampsdb_config" VALUES(169,'interface.open-with-default-viewer',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(170,'interface.place-sel-height',NULL,'int','450');
INSERT INTO "grampsdb_config" VALUES(171,'interface.dont-ask',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(172,'geography.map',NULL,'str','person');
INSERT INTO "grampsdb_config" VALUES(173,'geography.zoom_when_center',NULL,'int','12');
INSERT INTO "grampsdb_config" VALUES(174,'geography.center-lon',NULL,'float','0.0');
INSERT INTO "grampsdb_config" VALUES(175,'geography.show_cross',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(176,'geography.zoom',NULL,'int','0');
INSERT INTO "grampsdb_config" VALUES(177,'geography.map_service',NULL,'int','1');
INSERT INTO "grampsdb_config" VALUES(178,'geography.lock',NULL,'bool','False');
INSERT INTO "grampsdb_config" VALUES(179,'geography.path',NULL,'str','');
INSERT INTO "grampsdb_config" VALUES(180,'geography.center-lat',NULL,'float','0.0');
CREATE TABLE "grampsdb_tag" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" text,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "name" text NOT NULL,
    "color" varchar(13),
    "priority" integer
);
CREATE TABLE "grampsdb_myfamilies" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "family_id" integer NOT NULL,
    "order" integer unsigned NOT NULL
);
INSERT INTO "grampsdb_myfamilies" VALUES(1,2,3,1);
INSERT INTO "grampsdb_myfamilies" VALUES(2,4,12,1);
INSERT INTO "grampsdb_myfamilies" VALUES(3,5,14,1);
INSERT INTO "grampsdb_myfamilies" VALUES(4,7,10,1);
INSERT INTO "grampsdb_myfamilies" VALUES(5,8,19,1);
INSERT INTO "grampsdb_myfamilies" VALUES(6,10,17,1);
INSERT INTO "grampsdb_myfamilies" VALUES(7,16,12,1);
INSERT INTO "grampsdb_myfamilies" VALUES(8,18,6,1);
INSERT INTO "grampsdb_myfamilies" VALUES(9,20,16,1);
INSERT INTO "grampsdb_myfamilies" VALUES(10,26,6,1);
INSERT INTO "grampsdb_myfamilies" VALUES(11,27,17,1);
INSERT INTO "grampsdb_myfamilies" VALUES(12,29,18,1);
INSERT INTO "grampsdb_myfamilies" VALUES(13,32,18,1);
INSERT INTO "grampsdb_myfamilies" VALUES(14,33,5,1);
INSERT INTO "grampsdb_myfamilies" VALUES(15,34,19,1);
INSERT INTO "grampsdb_myfamilies" VALUES(16,35,9,1);
INSERT INTO "grampsdb_myfamilies" VALUES(17,36,3,1);
INSERT INTO "grampsdb_myfamilies" VALUES(18,38,11,1);
INSERT INTO "grampsdb_myfamilies" VALUES(19,39,1,1);
INSERT INTO "grampsdb_myfamilies" VALUES(20,42,10,1);
INSERT INTO "grampsdb_myfamilies" VALUES(21,43,16,1);
INSERT INTO "grampsdb_myfamilies" VALUES(22,44,7,1);
INSERT INTO "grampsdb_myfamilies" VALUES(23,48,5,1);
INSERT INTO "grampsdb_myfamilies" VALUES(24,49,8,1);
INSERT INTO "grampsdb_myfamilies" VALUES(25,53,8,1);
INSERT INTO "grampsdb_myfamilies" VALUES(26,54,13,1);
INSERT INTO "grampsdb_myfamilies" VALUES(27,54,11,2);
INSERT INTO "grampsdb_myfamilies" VALUES(28,55,4,1);
INSERT INTO "grampsdb_myfamilies" VALUES(29,58,14,1);
INSERT INTO "grampsdb_myfamilies" VALUES(30,59,2,1);
INSERT INTO "grampsdb_myfamilies" VALUES(31,60,15,1);
INSERT INTO "grampsdb_myfamilies" VALUES(32,61,13,1);
INSERT INTO "grampsdb_myfamilies" VALUES(33,62,9,1);
INSERT INTO "grampsdb_myfamilies" VALUES(34,64,2,1);
INSERT INTO "grampsdb_myfamilies" VALUES(35,64,4,2);
INSERT INTO "grampsdb_myfamilies" VALUES(36,65,1,1);
INSERT INTO "grampsdb_myfamilies" VALUES(37,68,15,1);
INSERT INTO "grampsdb_myfamilies" VALUES(38,69,7,1);
CREATE TABLE "grampsdb_myparentfamilies" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "family_id" integer NOT NULL,
    "order" integer unsigned NOT NULL
);
INSERT INTO "grampsdb_myparentfamilies" VALUES(1,1,16,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(2,3,11,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(3,4,17,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(4,5,17,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(5,6,9,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(6,7,12,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(7,8,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(8,9,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(9,11,11,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(10,12,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(11,13,16,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(12,14,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(13,15,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(14,17,12,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(15,19,1,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(16,21,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(17,22,11,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(18,23,19,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(19,24,19,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(20,25,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(21,28,9,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(22,29,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(23,30,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(24,31,16,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(25,33,17,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(26,35,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(27,36,12,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(28,37,1,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(29,38,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(30,40,16,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(31,41,1,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(32,42,6,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(33,43,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(34,45,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(35,46,19,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(36,47,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(37,49,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(38,50,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(39,51,9,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(40,52,17,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(41,54,2,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(42,56,19,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(43,57,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(44,63,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(45,65,10,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(46,66,2,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(47,67,18,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(48,68,16,1);
INSERT INTO "grampsdb_myparentfamilies" VALUES(49,69,17,1);
CREATE TABLE "grampsdb_person_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "grampsdb_tag" ("id"),
    UNIQUE ("person_id", "tag_id")
);
CREATE TABLE "grampsdb_person" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "gender_type_id" integer NOT NULL REFERENCES "grampsdb_gendertype" ("id"),
    "probably_alive" bool NOT NULL,
    "birth_id" integer,
    "death_id" integer,
    "birth_ref_index" integer NOT NULL,
    "death_ref_index" integer NOT NULL
);
INSERT INTO "grampsdb_person" VALUES(1,'c38a114d1981fe7f377f3cc24ed','I0013','2012-07-31 08:09:42.381918','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxOTgxZmU3ZjM3N2YzY2MyNGVkJwpWSTAwMTMKcDEKSTEKKEkwMAoobChsTlZN
YXJrIEtlbm5lZHkKKGxwMgooVlNIUklWRVIKVgpJMDEKKEkxClYKdFYKdHAzCmFWClYKKEkyClZC
aXJ0aCBOYW1lCnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA0CihJMDAKKGwobFZjMzhhMTE0
ZDE5YTYxNWVhOTExZmZkODk1NzYKKEkxClZQcmltYXJ5CnR0cDUKYShsKGxwNgpWYzM4YTExNGQw
Y2UzNWRiNThkZmY3YTE3ZGVkCnA3CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHA4Ci4=
',2,1,7,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(2,'c38a114d71d61a4a22bec1bf058','I0058','2012-07-31 08:09:42.402644','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3MWQ2MWE0YTIyYmVjMWJmMDU4JwpWSTAwNTgKcDEKSTEKKEkwMAoobChsTlZD
aGFybGVzCnAyCihscDMKKFZCVVJLRQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRo
IE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkktMQoobChscDYKVmMzOGExMTRkNzA2M2Iw
ZjQxMWRiNDg3MDJlMApwNwphKGwobChsKGwobChsKGwobEk3NzAwMTEyMDAKKHRJMDAKKGx0cDgK
Lg==
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(3,'c38a114d6b21b50cb7fa9f2d2af','I0055','2012-07-31 08:09:42.432380','1995-04-29 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2YjIxYjUwY2I3ZmE5ZjJkMmFmJwpWSTAwNTUKcDEKSTEKKEkwMAoobChsTlZK
b2huIEZpdHpnZXJhbGQKcDIKKGxwMwooVktFTk5FRFkKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYK
KEkyClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMQoobHA2CihJMDAKKGwo
bFZjMzhhMTE0ZDZiNTc5ZWE1NWY2NmMwZDJjZjgKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwo
bFZjMzhhMTE0ZDZiNjViMTVmZWJhNDNiOTQzYjYKKEkxClZQcmltYXJ5CnR0cDgKYShJMDAKKGwo
bFZjMzhhMTE0ZDZjMTRmZDFlMDA5MWQzNmMwMTkKKEkxClZQcmltYXJ5CnR0cDkKYShsKGxwMTAK
VmMzOGExMTRkNjFjMWU0Y2JmZjQ5YTIwZDAzNwpwMTEKYShsKGwobChsKGwobChsSTc5OTEyODAw
MAoodEkwMAoobHRwMTIKLg==
',2,1,28,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(4,'c38a114d4c6256160921bcaa5f2','I0044','2012-07-31 08:09:42.477742','1994-05-29 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0YzYyNTYxNjA5MjFiY2FhNWYyJwpWSTAwNDQKcDEKSTEKKEkwMAoobChsTlZQ
YXRyaWNrIEpvc2VwaApwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgoo
STIKVkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSTEKSTAKKGxwNgooSTAwCihsKGxW
YzM4YTExNGQ0YzkzZDIwNGQ2ZTU0YjQ2YWEzCihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxW
YzM4YTExNGQ0ZDQ0N2I5YWNjYzJlNTYwODJjCihJMQpWUHJpbWFyeQp0dHA4CmEoSTAwCihsKGxW
YzM4YTExNGQ0ZDY5MzFiNTBiYjE3YjJkMDIKKEkxClZQcmltYXJ5CnR0cDkKYShJMDAKKGwobFZj
MzhhMTE0ZDRlMzI5MzU0N2Q0ZDVmZTE3MDMKKEkxClZQcmltYXJ5CnR0cDEwCmEoSTAwCihsKGxW
YzM4YTExNGQ0ZTQ1MmY4YjBhN2ZhMzY4OTVlCihJMQpWUHJpbWFyeQp0dHAxMQphKEkwMAoobChs
VmMzOGExMTRkNGU2NzAzZGYzNmE5MmM2MTEzYQooSTEKVlByaW1hcnkKdHRwMTIKYShscDEzClZj
MzhhMTE0YzE5NTY0NDgzOTBlYmRlYjc0MDIKcDE0CmEobHAxNQpWYzM4YTExNGQ0ZTczYThjN2U1
MWM4YmVkN2IKcDE2CmEobChsKGwobChsKGwobHAxNwpWYzM4YTExNGQ0ZDg3MTYxNzcyYTc4YmIz
ODAxCnAxOAphVmMzOGExMTRkNGRiMzM4OTgzMWU1M2E2YTVlOApwMTkKYVZjMzhhMTE0ZDRkZjFl
OTJkYzVjNDk0Yzg1MWMKcDIwCmFWYzM4YTExNGQ0ZTI1N2MyMWJlZTg1ZWQ2YmQ3CnAyMQphVmMz
OGExMTRkNGY2MjA3N2JhZDNmMGM4OThjYgpwMjIKYUk3NzAxODQwMDAKKHRJMDAKKGx0cDIzCi4=
',2,0,31,20,0,1);
INSERT INTO "grampsdb_person" VALUES(5,'c38a114d75c260bbb261303b25c','I0061','2012-07-31 08:09:42.506069','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3NWMyNjBiYmIyNjEzMDNiMjVjJwpWSTAwNjEKcDEKSTAKKEkwMAoobChsTlZK
b2hhbm5hCnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmly
dGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYzM4YTEx
NGQ3NWVhNWUxYWRkNTFlZDk4MDEKKEkxClZQcmltYXJ5CnR0cDcKYShscDgKVmMzOGExMTRkNzYx
MjAwMDBiN2JiZWE3ODA0ZQpwOQphKGxwMTAKVmMzOGExMTRkNGU3M2E4YzdlNTFjOGJlZDdiCnAx
MQphKGwobChsKGwobChsKGxJNzcwMDExMjAwCih0STAwCihsdHAxMgou
',3,1,81,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(6,'c38a114d4163d912f9cade9b222','I0037','2012-07-31 08:09:42.531919','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0MTYzZDkxMmY5Y2FkZTliMjIyJwpWSTAwMzcKcDEKSTEKKEkwMAoobChsTlZX
aWxsaWFtIEtlbm5lZHkKcDIKKGxwMwooVlNNSVRIClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJ
MgpWQmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxW
YzM4YTExNGQ0MTg2OTY1MjUzYzE5N2QxN2ViCihJMQpWUHJpbWFyeQp0dHA3CmEobChscDgKVmMz
OGExMTRkM2Q1NGE5NDlkYTdlZmRkMzBhZgpwOQphKGwobChsKGwobChsKGxJMAoodEkwMAoobHRw
MTAKLg==
',2,1,100,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(7,'c38a114bffb92f7d0134ab26ad','I0001','2012-07-31 08:09:42.593284','1995-01-26 00:00:00',NULL,0,1,'KFMnYzM4YTExNGJmZmI5MmY3ZDAxMzRhYjI2YWQnClZJMDAwMQpwMQpJMQooSTAwCihsKGxOVkpv
c2VwaCBQYXRyaWNrCihscDIKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpW
QmlydGggTmFtZQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA0CihJMDAKKGwobFZjMzhhMTE0
YzAwMTdmMmZhN2ZjYmQyNDM5OTAKKEkxClZQcmltYXJ5CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0
YzA1M2Q2NGExMWVlZmExMWY4NQooSTEKVlByaW1hcnkKdHRwNgphKEkwMAoobChsVmMzOGExMTRj
MTBhNzFhMzAxOTBmMTFiZmMwMgooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmMzOGExMTRj
MTI3NWE4NzZhNDVlMzU0ZWEwNAooSTEKVlByaW1hcnkKdHRwOAphKEkwMAoobChsVmMzOGExMTRj
MTJhMjQ3MWIwMTczYzgzMTM3NgooSTEKVlByaW1hcnkKdHRwOQphKEkwMAoobChsVmMzOGExMTRj
MTJjN2FiZWQ3YTE1NjRlMjZjMQooSTEKVlByaW1hcnkKdHRwMTAKYShJMDAKKGwobFZjMzhhMTE0
YzE3ODE0NzJhY2ZhMjcyNDFmZGEKKEkxClZQcmltYXJ5CnR0cDExCmEoSTAwCihsKGxWYzM4YTEx
NGMxN2QxYTViNmE5Yzc4OTU0YjQ2CihJMQpWUHJpbWFyeQp0dHAxMgphKEkwMAoobChsVmMzOGEx
MTRjMTgyNWU5MDU0MThhNmFhMjZmYQooSTEKVlByaW1hcnkKdHRwMTMKYShJMDAKKGwobFZjMzhh
MTE0YzE4OTdmNjUxM2Y1OWQ4MmJkYzMKKEkxClZQcmltYXJ5CnR0cDE0CmEoSTAwCihsKGxWYzM4
YTExNGMxOGU1MDY5OWRiYzUzZjg2ZTJiCihJMQpWUHJpbWFyeQp0dHAxNQphKGxwMTYKVmMzOGEx
MTRjMTkzMjQ2YTliMDhhZjk2ZDhjMQpwMTcKYShscDE4ClZjMzhhMTE0YzE5NTY0NDgzOTBlYmRl
Yjc0MDIKcDE5CmEobChsKGwobChsKGwobHAyMApWYzM4YTExNGMxMzI2NWZkNTZiNGI1NTQyMTQy
CnAyMQphVmMzOGExMTRjMTUzN2YzYjA1MzkxMTFjODg2MwpwMjIKYVZjMzhhMTE0YzE2MDUwZjFl
ZjJlYzUyYWE1YWYKcDIzCmFWYzM4YTExNGMxNmE0YzI2NTgyZWM4OThiYmUzCnAyNAphVmMzOGEx
MTRjMTc1NjQyNjU3NDRjMGNjYmYzYQpwMjUKYVZjMzhhMTE0Y2Y5NTNlZDllNzFkMGFmNmZjYzIK
cDI2CmFJNzkxMDk2NDAwCih0STAwCihsdHAyNwou
',2,0,86,92,0,1);
INSERT INTO "grampsdb_person" VALUES(8,'c38a114d1e31ea04ea19274e8ec','I0016','2012-07-31 08:09:42.618839','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxZTMxZWEwNGVhMTkyNzRlOGVjJwpWSTAwMTYKcDEKSTAKKEkwMAoobChsTlZQ
YXRyaWNpYQpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJp
cnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmMzOGEx
MTRkMWU2N2UwZDM3ZjFmMzhjMjQwMAooSTEKVlByaW1hcnkKdHRwNwphKGxwOApWYzM4YTExNGQx
ZGI2MDI4MTk2OTRlYmFmMzdiCnA5CmEobHAxMApWYzM4YTExNGMxOTMyNDZhOWIwOGFmOTZkOGMx
CnAxMQphKGwobChsKGwobChsKGxwMTIKVmMzOGExMTRkMWYwNmQzNDA1Y2I4ODU0MjYyYgpwMTMK
YUkwCih0STAwCihsdHAxNAou
',3,1,97,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(9,'c38a114cff6204fde64eca59001','I0003','2012-07-31 08:09:42.661796','1994-05-29 00:00:00',NULL,0,1,'KFMnYzM4YTExNGNmZjYyMDRmZGU2NGVjYTU5MDAxJwpWSTAwMDMKcDEKSTEKKEkwMAoobChsTlZK
b3NlcGggUGF0cmljawpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgoo
STIKVkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSTIKSTEKKGxwNgooSTAwCihsKGxW
YzM4YTExNGNmZjgzYjhkNThmN2ZmYmZmMWIxCihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxW
YzM4YTExNGNmZmEzM2M4ZmZiOTJjNTlmNDBlCihJMQpWUHJpbWFyeQp0dHA4CmEoSTAwCihsKGxW
YzM4YTExNGQwMDYxMzQwM2JhYzRmOTdkZTAyCihJMQpWUHJpbWFyeQp0dHA5CmEoSTAwCihsKGxW
YzM4YTExNGQwMTEyNDc4NWQxOWQ5MDgzMzAwCihJMQpWUHJpbWFyeQp0dHAxMAphKEkwMAoobChs
VmMzOGExMTRkMDEyN2Y4MTRmODliMmQxNTg3YwooSTEKVlByaW1hcnkKdHRwMTEKYShJMDAKKGwo
bFZjMzhhMTE0ZDAxYjNkMDhjNTVhZWRjNDE5NTQKKEkxClZQcmltYXJ5CnR0cDEyCmEobChscDEz
ClZjMzhhMTE0YzE5MzI0NmE5YjA4YWY5NmQ4YzEKcDE0CmEobChsKGwobChsKGwobHAxNQpWYzM4
YTExNGQwMTQ1NWQ1ZTEzYjBkZjc1MjMxCnAxNgphVmMzOGExMTRkMDE3N2ZmNTViMGMzNzk4N2Zk
MgpwMTcKYVZjMzhhMTE0ZDAxYTdjOThhYzU3ZmFlOGE1NWQKcDE4CmFWYzM4YTExNGQwMmEzYmQ4
NGZmM2RjYzQ4MDhiCnAxOQphSTc3MDE4NDAwMAoodEkwMAoobHRwMjAKLg==
',2,0,74,12,1,2);
INSERT INTO "grampsdb_person" VALUES(10,'c38a114d50f30d538e080258d45','I0046','2012-07-31 08:09:42.707085','1994-10-16 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MGYzMGQ1MzhlMDgwMjU4ZDQ1JwpWSTAwNDYKcDEKSTEKKEkwMAoobChsTlZQ
YXRyaWNrCihscDIKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGgg
TmFtZQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA0CihJMDAKKGwobFZjMzhhMTE0ZDUxMTQ2
ZjJhZjQ4OTY4NTZlMzUKKEkxClZQcmltYXJ5CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0ZDUxYjQ4
MDgxZDRiMmNhOGVjMzUKKEkxClZQcmltYXJ5CnR0cDYKYShJMDAKKGwobFZjMzhhMTE0ZDUyOTI4
NDEwZDEzMzFkMDRjZTUKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZjMzhhMTE0ZDUyYjRk
NjJmNzBkN2M5ZTIxNzIKKEkxClZQcmltYXJ5CnR0cDgKYShJMDAKKGwobFZjMzhhMTE0ZDUzMDMx
MjRiYTMzYzEzYmQ0YTcKKEkxClZQcmltYXJ5CnR0cDkKYShJMDAKKGwobFZjMzhhMTE0ZDUzMTRh
NTY1MzVkMzNkYzk0NWUKKEkxClZQcmltYXJ5CnR0cDEwCmEoSTAwCihsKGxWYzM4YTExNGQ1MzMx
Y2FmNDQxNDY4MTFlYTIwCihJMQpWUHJpbWFyeQp0dHAxMQphKGxwMTIKVmMzOGExMTRkNGU3M2E4
YzdlNTFjOGJlZDdiCnAxMwphKGwobChsKGwobChsKGwobHAxNApWYzM4YTExNGQ1MmM2MWY4MzJh
MjgyYTQzMzEzCnAxNQphVmMzOGExMTRkNTJmMWE5OThiMmFhN2RjMjQ2CnAxNgphVmMzOGExMTRk
NTM5NDY5MThmZmQ2NmRiMWI3CnAxNwphSTc4MjI4MDAwMAoodEkwMAoobHRwMTgKLg==
',2,0,38,56,0,1);
INSERT INTO "grampsdb_person" VALUES(11,'c38a114d6d519fbca490ad79612','I0056','2012-07-31 08:09:42.734414','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2ZDUxOWZiY2E0OTBhZDc5NjEyJwpWSTAwNTYKcDEKSTEKKEkwMAoobChsTlZQ
YXRyaWNrIEJvdXZpZXIKcDIKKGxwMwooVktFTk5FRFkKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYK
KEkyClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEkxCkkwCihscDYKKEkwMAoobChs
VmMzOGExMTRkNmQ4N2MyNjI2YzU4NDIxMThkYwooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChs
VmMzOGExMTRkNmUyNTQzYjI5NzQ2OGExMWRhZgooSTEKVlByaW1hcnkKdHRwOAphKGwobHA5ClZj
MzhhMTE0ZDYxYzFlNGNiZmY0OWEyMGQwMzcKcDEwCmEobChsKGwobChsKGwobEkwCih0STAwCihs
dHAxMQou
',2,0,64,106,0,1);
INSERT INTO "grampsdb_person" VALUES(12,'c38a114d3b16924381d4be9eedc','I0033','2012-07-31 08:09:42.758156','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzYjE2OTI0MzgxZDRiZTllZWRjJwpWSTAwMzMKcDEKSTAKKEkwMAoobChsTlZS
b3J5IEVsaXphYmV0aApwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgoo
STIKVkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChs
VmMzOGExMTRkM2I0YjRhNjdlZTc3OGViZWE0CihJMQpWUHJpbWFyeQp0dHA3CmEobChscDgKVmMz
OGExMTRkMjdlMzJiNGJiYTdhZGI1ZTRhCnA5CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHAx
MAou
',3,1,50,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(13,'c38a114d14832b6973ff0e74f52','I0009','2012-07-31 08:09:42.785177','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxNDgzMmI2OTczZmYwZTc0ZjUyJwpWSTAwMDkKcDEKSTEKKEkwMAoobChsTlZS
b2JlcnQgU2FyZ2VudApwMgoobHAzCihWU0hSSVZFUgpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgoo
STIKVkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkxCihscDYKKEkwMAoobChs
VmMzOGExMTRkMTRhMWI1N2E1NTI4ZjI1MGQyZgooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChs
VmMzOGExMTRkMTRiNDdjODZjM2U1NDg3YzhmNgooSTEKVlByaW1hcnkKdHRwOAphKGwobHA5ClZj
MzhhMTE0ZDBjZTM1ZGI1OGRmZjdhMTdkZWQKcDEwCmEobChsKGwobChsKGwobEkwCih0STAwCihs
dHAxMQou
',2,1,6,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(14,'c38a114d2fb124f161170e7948','I0027','2012-07-31 08:09:42.808815','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyZmIxMjRmMTYxMTcwZTc5NDgnClZJMDAyNwpwMQpJMAooSTAwCihsKGxOVk1h
cnkgQ291cnRuZXkKcDIKKGxwMwooVktFTk5FRFkKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEky
ClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZj
MzhhMTE0ZDJmZTI0NmU4OWNkZmE2YmMwNmYKKEkxClZQcmltYXJ5CnR0cDcKYShsKGxwOApWYzM4
YTExNGQyN2UzMmI0YmJhN2FkYjVlNGEKcDkKYShsKGwobChsKGwobChsSTAKKHRJMDAKKGx0cDEw
Ci4=
',3,1,48,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(15,'c38a114d380767bacbf67767efc','I0032','2012-07-31 08:09:42.832692','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzODA3NjdiYWNiZjY3NzY3ZWZjJwpWSTAwMzIKcDEKSTEKKEkwMAoobChsTlZE
b3VnbGFzIEhhcnJpbWFuCihscDIKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJ
MgpWQmlydGggTmFtZQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNAooSTAwCihsKGxWYzM4
YTExNGQzODQ1MjZkMzZhOTJiMTQ1MDIyCihJMQpWUHJpbWFyeQp0dHA1CmEobChscDYKVmMzOGEx
MTRkMjdlMzJiNGJiYTdhZGI1ZTRhCnA3CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHA4Ci4=
',2,1,136,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(16,'c38a114d4ff6dfd9314b91dd03','I0045','2012-07-31 08:09:42.860283','1994-05-29 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZmY2ZGZkOTMxNGI5MWRkMDMnClZJMDA0NQpwMQpJMAooSTAwCihsKGxOVk1h
cnkgQXVndXN0YQpwMgoobHAzCihWSElDS0VZClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpW
QmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJMApJLTEKKGxwNgooSTAwCihsKGxWYzM4
YTExNGQ1MDIxNjQ5NmJjN2IxZTY2MDMxCihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYzM4
YTExNGQ1MDM2ZjJjNWY2ZTU1MmI0NDNmCihJMQpWUHJpbWFyeQp0dHA4CmEobHA5ClZjMzhhMTE0
YzE5NTY0NDgzOTBlYmRlYjc0MDIKcDEwCmEobChsKGwobChsKGwobChsSTc3MDE4NDAwMAoodEkw
MAoobHRwMTEKLg==
',3,0,NULL,133,-1,0);
INSERT INTO "grampsdb_person" VALUES(17,'c38a114d7e9fb9a1e9797c9559','I0067','2012-07-31 08:09:42.884310','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3ZTlmYjlhMWU5Nzk3Yzk1NTknClZJMDA2NwpwMQpJMAooSTAwCihsKGxOVkxv
cmV0dGEKcDIKKGxwMwooVktFTk5FRFkKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0
aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZjMzhhMTE0
ZDdlYzY3NWQzNGNlZTUzZDNmYzUKKEkxClZQcmltYXJ5CnR0cDcKYShsKGxwOApWYzM4YTExNGMx
OTU2NDQ4MzkwZWJkZWI3NDAyCnA5CmEobChsKGwobChsKGwobEk3NzAwMTEyMDAKKHRJMDAKKGx0
cDEwCi4=
',3,1,79,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(18,'c38a114d5ca2887ed8e37c3520b','I0050','2012-07-31 08:09:42.908969','1994-11-03 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ1Y2EyODg3ZWQ4ZTM3YzM1MjBiJwpWSTAwNTAKcDEKSTEKKEkwMAoobChsTlZK
b2huIEYuCnAyCihscDMKKFZGSVRaR0VSQUxEClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpW
QmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSS0xCihscDYKKEkwMAoobChsVmMz
OGExMTRkNWNjNDYzYzVhMDMyMWMxYTYwYQooSTEKVlByaW1hcnkKdHRwNwphKGxwOApWYzM4YTEx
NGNmZGE0ZjMwOTY4ZDNmMWQxMjZhCnA5CmEobChsKGwobChsKGwobChscDEwClZjMzhhMTE0ZDVj
ZTM2YjFiZTIxMzhjNGI2MTYKcDExCmFJNzgzODM4ODAwCih0STAwCihsdHAxMgou
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(19,'c38a114d4827c99709a982c9401','I0041','2012-07-31 08:09:42.932685','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0ODI3Yzk5NzA5YTk4MmM5NDAxJwpWSTAwNDEKcDEKSTAKKEkwMAoobChsTlZL
YXJhIEFubgpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJp
cnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmMzOGEx
MTRkNDg0MWIyYjA3NDExYmEwYzRjNAooSTEKVlByaW1hcnkKdHRwNwphKGwobHA4ClZjMzhhMTE0
ZDQ1OTVhZWU4ZDYyZmVjMWQxMjQKcDkKYShsKGwobChsKGwobChsSTAKKHRJMDAKKGx0cDEwCi4=
',3,1,131,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(20,'c38a114d0bb1bab5e06ea6cebff','I0007','2012-07-31 08:09:42.960553','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQwYmIxYmFiNWUwNmVhNmNlYmZmJwpWSTAwMDcKcDEKSTEKKEkwMAoobChsTlZS
b2JlcnQgU2FyZ2VudAoobHAyCihWU0hSSVZFUgpWCkkwMQooSTEKVgp0Vgp0cDMKYVYKVgooSTIK
VkJpcnRoIE5hbWUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkxCihscDQKKEkwMAoobChsVmMzOGEx
MTRkMGJmNDE1OTQ0ZDNmZGQ2ZGY1ZAooSTEKVlByaW1hcnkKdHRwNQphKEkwMAoobChsVmMzOGEx
MTRkMGMwMTNlNGJlMjE5OWY3MzRiOQooSTEKVlByaW1hcnkKdHRwNgphKGxwNwpWYzM4YTExNGQw
Y2UzNWRiNThkZmY3YTE3ZGVkCnA4CmEobChsKGwobChsKGwobChscDkKVmMzOGExMTRkMGNkYzI0
ZWFiZDUxNmY5MmRmCnAxMAphSTc3MDAxMTIwMAoodEkwMAoobHRwMTEKLg==
',2,1,24,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(21,'c38a114d3124b6b2868d7f8b654','I0028','2012-07-31 08:09:42.984563','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzMTI0YjZiMjg2OGQ3ZjhiNjU0JwpWSTAwMjgKcDEKSTEKKEkwMAoobChsTlZN
aWNoYWVsIEwuCnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpW
QmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYzM4
YTExNGQzMTQ0YTg5M2I0OWU1NzBlMmNkCihJMQpWUHJpbWFyeQp0dHA3CmEobChscDgKVmMzOGEx
MTRkMjdlMzJiNGJiYTdhZGI1ZTRhCnA5CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHAxMAou
',2,1,105,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(22,'c38a114d683170f23a59d501795','I0054','2012-07-31 08:09:43.018229','1994-05-29 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2ODMxNzBmMjNhNTlkNTAxNzk1JwpWSTAwNTQKcDEKSTAKKEkwMAoobChsTlZD
YXJvbGluZSBCb3V2aWVyCnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwNAphVgpW
CihJMgpWQmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihs
KGxWYzM4YTExNGQ2ODY1OTVhNTg4NDZjODI5NzE2CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihs
KGxWYzM4YTExNGQ2OTI3MWYyMmIxZTM5Y2NkMzk4CihJMQpWUHJpbWFyeQp0dHA4CmEoSTAwCihs
KGxWYzM4YTExNGQ2OWM0MzY4ZTIwZDA4NDRlMmJlCihJMQpWUHJpbWFyeQp0dHA5CmEoSTAwCihs
KGxWYzM4YTExNGQ2OWQ3OThlMDA5YzRlZTFmYzRkCihJMQpWUHJpbWFyeQp0dHAxMAphKGwobHAx
MQpWYzM4YTExNGQ2MWMxZTRjYmZmNDlhMjBkMDM3CnAxMgphKGwobChsKGwobChsKGxJNzcwMTg0
MDAwCih0STAwCihsdHAxMwou
',3,1,23,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(23,'c38a114d241443fa200235f0518','I0020','2012-07-31 08:09:43.039032','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyNDE0NDNmYTIwMDIzNWYwNTE4JwpWSTAwMjAKcDEKSTAKKEkwMAoobChsTlZS
b2JpbgpwMgoobHAzCihWTEFXRk9SRApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRo
IE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkktMQoobChsKGxwNgpWYzM4YTExNGQxZGI2
MDI4MTk2OTRlYmFmMzdiCnA3CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHA4Ci4=
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(24,'c38a114d22e1fb79ac8ba484612','I0019','2012-07-31 08:09:43.060704','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyMmUxZmI3OWFjOGJhNDg0NjEyJwpWSTAwMTkKcDEKSTAKKEkwMAoobChsTlZT
eWRuZXkKKGxwMgooVkxBV0ZPUkQKVgpJMDEKKEkxClYKdFYKdHAzCmFWClYKKEkyClZCaXJ0aCBO
YW1lCnRWCkkwCkkwClYKVgpWCnQobEktMQpJLTEKKGwobChscDQKVmMzOGExMTRkMWRiNjAyODE5
Njk0ZWJhZjM3YgpwNQphKGwobChsKGwobChsKGxJMAoodEkwMAoobHRwNgou
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(25,'c38a114d2b879444d8db5c21cfd','I0024','2012-07-31 08:09:43.084700','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyYjg3OTQ0NGQ4ZGI1YzIxY2ZkJwpWSTAwMjQKcDEKSTEKKEkwMAoobChsTlZK
b3NlcGggUGF0cmljawpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgoo
STIKVkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChs
VmMzOGExMTRkMmJhMTRiOGExNWFlOWYyY2UwNAooSTEKVlByaW1hcnkKdHRwNwphKGwobHA4ClZj
MzhhMTE0ZDI3ZTMyYjRiYmE3YWRiNWU0YQpwOQphKGwobChsKGwobChsKGxJMAoodEkwMAoobHRw
MTAKLg==
',2,1,72,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(26,'c38a114d5d99b517ee2f0f1b4c','I0051','2012-07-31 08:09:43.105717','1994-11-03 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ1ZDk5YjUxN2VlMmYwZjFiNGMnClZJMDA1MQpwMQpJMAooSTAwCihsKGxOVkpv
c2VwaGluZSBNYXJ5CnAyCihscDMKKFZIQU5OT04KVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEky
ClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJLTEKKGwobHA2ClZjMzhhMTE0
Y2ZkYTRmMzA5NjhkM2YxZDEyNmEKcDcKYShsKGwobChsKGwobChsKGxJNzgzODM4ODAwCih0STAw
CihsdHA4Ci4=
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(27,'c38a114d546bc56d4a92e29efe','I0047','2012-07-31 08:09:43.143561','1994-10-16 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NDZiYzU2ZDRhOTJlMjllZmUnClZJMDA0NwpwMQpJMAooSTAwCihsKGxOVkJy
aWRnZXQKcDIKKGxwMwooVk1VUlBIWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRo
IE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSTEKSTAKKGxwNgooSTAwCihsKGxWYzM4YTExNGQ1
NDk1ZmI3M2I4YzQzNWNlYzc4CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYzM4YTExNGQ1
NGM1ZWIzZDAyMTBmMDdlMGI0CihJMQpWUHJpbWFyeQp0dHA4CmEoSTAwCihsKGxWYzM4YTExNGQ1
NTc1MGQyMGFiYzkxMjQ3ZTE3CihJMQpWUHJpbWFyeQp0dHA5CmEoSTAwCihsKGxWYzM4YTExNGQ1
NjA0NzE0NzIwNWU2Yzk3MzYxCihJMQpWUHJpbWFyeQp0dHAxMAphKEkwMAoobChsVmMzOGExMTRk
NTYzNzgxNDlmMzJhN2Y3YTVhMwooSTEKVlByaW1hcnkKdHRwMTEKYShscDEyClZjMzhhMTE0ZDRl
NzNhOGM3ZTUxYzhiZWQ3YgpwMTMKYShsKGwobChsKGwobChsKGxwMTQKVmMzOGExMTRkNTYyNGMw
NmRiZmVhZmJmMGIyNApwMTUKYUk3ODIyODAwMDAKKHRJMDAKKGx0cDE2Ci4=
',3,0,93,49,0,1);
INSERT INTO "grampsdb_person" VALUES(28,'c38a114d402dec2d4a5e510f7d','I0036','2012-07-31 08:09:43.164331','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0MDJkZWMyZDRhNWU1MTBmN2QnClZJMDAzNgpwMQpJMQooSTAwCihsKGxOVlN0
ZXBoZW4KcDIKKGxwMwooVlNNSVRIClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGgg
TmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSS0xCihsKGwobHA2ClZjMzhhMTE0ZDNkNTRh
OTQ5ZGE3ZWZkZDMwYWYKcDcKYShsKGwobChsKGwobChsSTAKKHRJMDAKKGx0cDgKLg==
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(29,'c38a114d2542b5b163afb9663ef','I0021','2012-07-31 08:09:43.204823','1994-05-29 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQyNTQyYjViMTYzYWZiOTY2M2VmJwpWSTAwMjEKcDEKSTEKKEkwMAoobChsTlZS
b2JlcnQgRnJhbmNpcwoobHAyCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDMKYVYKVgooSTIK
VkJpcnRoIE5hbWUKdFYKSTAKSTAKVgpWClYKdChsSTEKSTAKKGxwNAooSTAwCihsKGxWYzM4YTEx
NGQyNTc1NmViYzE5ZmU2MDZlY2ZlCihJMQpWUHJpbWFyeQp0dHA1CmEoSTAwCihsKGxWYzM4YTEx
NGQyNjIyMmI4NjkxMTQ5ZTdkMTY0CihJMQpWUHJpbWFyeQp0dHA2CmEoSTAwCihsKGxWYzM4YTEx
NGQyNmMzYTAxOTA2NjBhMmFkMTBhCihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYzM4YTEx
NGQyN2IxZmQ2YmRlYTY3NGVlOTk2CihJMQpWUHJpbWFyeQp0dHA4CmEoSTAwCihsKGxWYzM4YTEx
NGQyN2M2MGE0MDgxNGJhMWY2NzQ5CihJMQpWUHJpbWFyeQp0dHA5CmEobHAxMApWYzM4YTExNGQy
N2UzMmI0YmJhN2FkYjVlNGEKcDExCmEobHAxMgpWYzM4YTExNGMxOTMyNDZhOWIwOGFmOTZkOGMx
CnAxMwphKGwobChsKGwobChsKGxwMTQKVmMzOGExMTRkMjc2NzU0NjdhNzIxOGJjNmMzMApwMTUK
YVZjMzhhMTE0ZDI3YTM1NjZiMjliMGYxMTI3YTAKcDE2CmFWYzM4YTExNGQyOGQ2ZWM2MmY4OWQ2
ZGE3MTMxCnAxNwphSTc3MDE4NDAwMAoodEkwMAoobHRwMTgKLg==
',2,0,41,54,0,1);
INSERT INTO "grampsdb_person" VALUES(30,'c38a114d3623ab3c09ff7c97e86','I0031','2012-07-31 08:09:43.228734','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzNjIzYWIzYzA5ZmY3Yzk3ZTg2JwpWSTAwMzEKcDEKSTEKKEkwMAoobChsTlZN
YXR0aGV3IE1heHdlbGwgVGF5bG9yCnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRw
NAphVgpWCihJMgpWQmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgoo
STAwCihsKGxWYzM4YTExNGQzNjQ0ZjY0NDUzNTM4YzYzY2IwCihJMQpWUHJpbWFyeQp0dHA3CmEo
bChscDgKVmMzOGExMTRkMjdlMzJiNGJiYTdhZGI1ZTRhCnA5CmEobChsKGwobChsKGwobEkwCih0
STAwCihsdHAxMAou
',2,1,80,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(31,'c38a114d18461600fe2347715db','I0012','2012-07-31 08:09:43.249346','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxODQ2MTYwMGZlMjM0NzcxNWRiJwpWSTAwMTIKcDEKSTEKKEkwMAoobChsTlZU
aW1vdGh5CnAyCihscDMKKFZTSFJJVkVSClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmly
dGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSS0xCihsKGwobHA2ClZjMzhhMTE0ZDBj
ZTM1ZGI1OGRmZjdhMTdkZWQKcDcKYShsKGwobChsKGwobChsSTAKKHRJMDAKKGx0cDgKLg==
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(32,'c38a114d2972b2dd272276f49db','I0022','2012-07-31 08:09:43.273033','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyOTcyYjJkZDI3MjI3NmY0OWRiJwpWSTAwMjIKcDEKSTAKKEkwMAoobChsTlZF
dGhlbApwMgoobHAzCihWU0tBS0VMClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGgg
TmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYzM4YTExNGQy
OTk0OTlkNzA1MzRkMjgxZjU0CihJMQpWUHJpbWFyeQp0dHA3CmEobHA4ClZjMzhhMTE0ZDI3ZTMy
YjRiYmE3YWRiNWU0YQpwOQphKGwobChsKGwobChsKGwobEkwCih0STAwCihsdHAxMAou
',3,1,58,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(33,'c38a114d73840640c21fc610e8a','I0060','2012-07-31 08:09:43.298105','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3Mzg0MDY0MGMyMWZjNjEwZThhJwpWSTAwNjAKcDEKSTAKKEkwMAoobChsTlZN
YXJ5CnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGgg
TmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYzM4YTExNGQ3
M2IxMTA1NGMzZjFiOTk2ZGJlCihJMQpWUHJpbWFyeQp0dHA3CmEobHA4ClZjMzhhMTE0ZDc0NjI2
N2NiZGZkYWE1YThhYzIKcDkKYShscDEwClZjMzhhMTE0ZDRlNzNhOGM3ZTUxYzhiZWQ3YgpwMTEK
YShsKGwobChsKGwobChsSTc3MDAxMTIwMAoodEkwMAoobHRwMTIKLg==
',3,1,102,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(34,'c38a114d1d63ccf55741f242195','I0015','2012-07-31 08:09:43.321973','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxZDYzY2NmNTU3NDFmMjQyMTk1JwpWSTAwMTUKcDEKSTEKKEkwMAoobChsTlZQ
ZXRlcgoobHAyCihWTEFXRk9SRApWCkkwMQooSTEKVgp0Vgp0cDMKYVYKVgooSTIKVkJpcnRoIE5h
bWUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDQKKEkwMAoobChsVmMzOGExMTRkMWQ4NDkw
M2E1MzIzOWViMmUzMQooSTEKVlByaW1hcnkKdHRwNQphKGxwNgpWYzM4YTExNGQxZGI2MDI4MTk2
OTRlYmFmMzdiCnA3CmEobChsKGwobChsKGwobChsSTAKKHRJMDAKKGx0cDgKLg==
',2,1,57,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(35,'c38a114d3de5d6d48fb68bd8cdb','I0035','2012-07-31 08:09:43.349912','1994-05-29 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQzZGU1ZDZkNDhmYjY4YmQ4Y2RiJwpWSTAwMzUKcDEKSTAKKEkwMAoobChsTlZK
ZWFuIEFubgpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJp
cnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmMzOGEx
MTRkM2UxNzhiZjBmMzg1YjI2YjU0MQooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmMzOGEx
MTRkM2ViNWUzNDVlZTMyZTM0ZDE0OQooSTEKVlByaW1hcnkKdHRwOAphKGxwOQpWYzM4YTExNGQz
ZDU0YTk0OWRhN2VmZGQzMGFmCnAxMAphKGxwMTEKVmMzOGExMTRjMTkzMjQ2YTliMDhhZjk2ZDhj
MQpwMTIKYShsKGwobChsKGwobChsSTc3MDE4NDAwMAoodEkwMAoobHRwMTMKLg==
',3,1,46,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(36,'c38a114d7013da4ba662b980a0e','I0057','2012-07-31 08:09:43.374765','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3MDEzZGE0YmE2NjJiOTgwYTBlJwpWSTAwNTcKcDEKSTAKKEkwMAoobChsTlZN
YXJnYXJldApwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJp
cnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmMzOGEx
MTRkNzA0MWMwYWQ0OTUzZTgwMTRmMQooSTEKVlByaW1hcnkKdHRwNwphKGxwOApWYzM4YTExNGQ3
MDYzYjBmNDExZGI0ODcwMmUwCnA5CmEobHAxMApWYzM4YTExNGMxOTU2NDQ4MzkwZWJkZWI3NDAy
CnAxMQphKGwobChsKGwobChsKGxJNzcwMDExMjAwCih0STAwCihsdHAxMgou
',3,1,19,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(37,'c38a114d497105fcd4ba3863aaa','I0042','2012-07-31 08:09:43.401808','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0OTcxMDVmY2Q0YmEzODYzYWFhJwpWSTAwNDIKcDEKSTEKKEkwMAoobChsTlZF
ZHdhcmQgTW9yZQpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIK
VkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkxCihscDYKKEkwMAoobChsVmMz
OGExMTRkNDlhMmE4ZmYyMjVmZTg4MGVhNAooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmMz
OGExMTRkNDlhNDY1NjVmNjBmZjQxZTVjMQooSTEKVlByaW1hcnkKdHRwOAphKGwobHA5ClZjMzhh
MTE0ZDQ1OTVhZWU4ZDYyZmVjMWQxMjQKcDEwCmEobChsKGwobChsKGwobEkwCih0STAwCihsdHAx
MQou
',2,1,143,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(38,'c38a114d5e625e2a3e83ae24631','I0052','2012-07-31 08:09:43.450805','1995-04-29 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1ZTYyNWUyYTNlODNhZTI0NjMxJwpWSTAwNTIKcDEKSTEKKEkwMAoobChsTlZK
b2huIEZpdHpnZXJhbGQKKGxwMgooVktFTk5FRFkKVgpJMDEKKEkxClYKdFYKdHAzCmFWClYKKEky
ClZCaXJ0aCBOYW1lCnRWCkkwCkkwClYKVgpWCnQobEkxCkkwCihscDQKKEkwMAoobChsVmMzOGEx
MTRkNWU5NTdlODU0NThjZDFkNzcwNQooSTEKVlByaW1hcnkKdHRwNQphKEkwMAoobChsVmMzOGEx
MTRkNWY1MTk5YTBmNDcwM2ViYTg3YgooSTEKVlByaW1hcnkKdHRwNgphKEkwMAoobChsVmMzOGEx
MTRkNWZmNGM3NzcxMjJkOTFkMWU4OAooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmMzOGEx
MTRkNjBhNjAxNmIzN2IzMDdlNzEwOQooSTEKVlByaW1hcnkKdHRwOAphKEkwMAoobChsVmMzOGEx
MTRkNjBiNmFkYzUxMmVlNzIxMzFhNAooSTEKVlByaW1hcnkKdHRwOQphKEkwMAoobChsVmMzOGEx
MTRkNjBlMzA2ZWQxMDlmMGZmMjZiNQooSTEKVlByaW1hcnkKdHRwMTAKYShJMDAKKGwobFZjMzhh
MTE0ZDYxYjM5ZTBkOWIxZTMyYzE5ODcKKEkxClZQcmltYXJ5CnR0cDExCmEobHAxMgpWYzM4YTEx
NGQ2MWMxZTRjYmZmNDlhMjBkMDM3CnAxMwphKGxwMTQKVmMzOGExMTRjMTkzMjQ2YTliMDhhZjk2
ZDhjMQpwMTUKYShsKGwobChsKGwobChscDE2ClZjMzhhMTE0ZDYwZjRhMGUzZGFlMjYzNDk2NjkK
cDE3CmFWYzM4YTExNGQ2MTA2YTU1M2M3ZTJmZDYzNjY0CnAxOAphVmMzOGExMTRkNjE0MzZjMGI1
MTkzMWQxZGI1NgpwMTkKYVZjMzhhMTE0ZDYxNzc2YTI4ZWI5NmUwOTUyNmIKcDIwCmFWYzM4YTEx
NGQ2MWExNTQ4ZDM1OWFlMzNjNmYzCnAyMQphVmMzOGExMTRkNjJlNzQwYjY1NzA5NDZhZDVjOApw
MjIKYUk3OTkxMjgwMDAKKHRJMDAKKGx0cDIzCi4=
',2,0,117,37,0,1);
INSERT INTO "grampsdb_person" VALUES(39,'c38a114d4725c810aa2c5a4ddf8','I0040','2012-07-31 08:09:43.474625','1994-05-29 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0NzI1YzgxMGFhMmM1YTRkZGY4JwpWSTAwNDAKcDEKSTAKKEkwMAoobChsTlZW
aXJnaW5pYSBKb2FuCnAyCihscDMKKFZCRU5ORVRUClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJ
MgpWQmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSS0xCihscDYKKEkwMAoobChs
VmMzOGExMTRkNDc2NWUyY2M3YmE1MmY0OTk0MwooSTEKVlByaW1hcnkKdHRwNwphKGxwOApWYzM4
YTExNGQ0NTk1YWVlOGQ2MmZlYzFkMTI0CnA5CmEobChsKGwobChsKGwobChsSTc3MDE4NDAwMAoo
dEkwMAoobHRwMTAKLg==
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(40,'c38a114d1b8516cc94fa7c1d302','I0014','2012-07-31 08:09:43.498611','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxYjg1MTZjYzk0ZmE3YzFkMzAyJwpWSTAwMTQKcDEKSTEKKEkwMAoobChsTlZB
bnRob255IFBhdWwKcDIKKGxwMwooVlNIUklWRVIKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEky
ClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZj
MzhhMTE0ZDFiYTM0MDljOWM2NzU4Njc4YWYKKEkxClZQcmltYXJ5CnR0cDcKYShsKGxwOApWYzM4
YTExNGQwY2UzNWRiNThkZmY3YTE3ZGVkCnA5CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHAx
MAou
',2,1,125,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(41,'c38a114d4b0444bd0592d6cd594','I0043','2012-07-31 08:09:43.522453','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0YjA0NDRiZDA1OTJkNmNkNTk0JwpWSTAwNDMKcDEKSTEKKEkwMAoobChsTlZQ
YXRyaWNrIEpvc2VwaApwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgoo
STIKVkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChs
VmMzOGExMTRkNGIzNDUxMDNhOTUwZTQ2NzM0NQooSTEKVlByaW1hcnkKdHRwNwphKGwobHA4ClZj
MzhhMTE0ZDQ1OTVhZWU4ZDYyZmVjMWQxMjQKcDkKYShsKGwobChsKGwobChsSTAKKHRJMDAKKGx0
cDEwCi4=
',2,1,15,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(42,'c38a114cfa41bc8d95b299e36db','I0002','2012-07-31 08:09:43.567515','1995-01-26 00:00:00',NULL,0,1,'KFMnYzM4YTExNGNmYTQxYmM4ZDk1YjI5OWUzNmRiJwpWSTAwMDIKcDEKSTAKKEkwMAoobChsTlZS
b3NlCihscDIKKFZGSVRaR0VSQUxEClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGgg
TmFtZQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA0CihJMDAKKGwobFZjMzhhMTE0Y2ZhNzc4
OTg1OTRkNDgyY2ZjMjIKKEkxClZQcmltYXJ5CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0Y2ZiMjRl
NGM5N2I3MGU1Njg4YzcKKEkxClZQcmltYXJ5CnR0cDYKYShJMDAKKGwobFZjMzhhMTE0Y2ZiYzNk
NWNhMmJlOTVhNzdlMzIKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZjMzhhMTE0Y2ZjYTY5
NDBhYjM3OTk5ODViNjYKKEkxClZQcmltYXJ5CnR0cDgKYShJMDAKKGwobFZjMzhhMTE0Y2ZjYjU3
OTlhZjM1YzI4NGE4MTEKKEkxClZQcmltYXJ5CnR0cDkKYShJMDAKKGwobFZjMzhhMTE0Y2ZkNzY3
YjMwMzJiMWNkNzBmMTEKKEkxClZQcmltYXJ5CnR0cDEwCmEobHAxMQpWYzM4YTExNGMxOTMyNDZh
OWIwOGFmOTZkOGMxCnAxMgphKGxwMTMKVmMzOGExMTRjZmRhNGYzMDk2OGQzZjFkMTI2YQpwMTQK
YShsKGwobChsKGwobChscDE1ClZjMzhhMTE0Y2ZjZTRiYWRiMzYyMzE0YTA2NjAKcDE2CmFWYzM4
YTExNGNmZDFjMWVkZjc1MTFhNGU5MmUKcDE3CmFWYzM4YTExNGNmZDQxMjkxZmViNWEzMDkxNWMx
CnAxOAphVmMzOGExMTRjZmQ2ODUwYTA1YzhkNzkwZGY5CnAxOQphVmMzOGExMTRjZmViNWIwN2I4
N2MxMzdjZTI3MApwMjAKYUk3OTEwOTY0MDAKKHRJMDAKKGx0cDIxCi4=
',3,0,71,22,0,1);
INSERT INTO "grampsdb_person" VALUES(43,'c38a114d10d44ac89d4bdbafeea','I0008','2012-07-31 08:09:43.599014','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxMGQ0NGFjODlkNGJkYmFmZWVhJwpWSTAwMDgKcDEKSTAKKEkwMAoobChsTlZF
dW5pY2UgTWFyeQpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIK
VkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmMz
OGExMTRkMTE0MjczODQyMzA4YTQwYTViZAooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmMz
OGExMTRkMTJkMzFmMTE0MzFmOTcyNDVlNQooSTEKVlByaW1hcnkKdHRwOAphKGxwOQpWYzM4YTEx
NGQwY2UzNWRiNThkZmY3YTE3ZGVkCnAxMAphKGxwMTEKVmMzOGExMTRjMTkzMjQ2YTliMDhhZjk2
ZDhjMQpwMTIKYShsKGwobChsKGwobChscDEzClZjMzhhMTE0ZDEyMzMwZmM3ZjQwNWMyOWNhZTMK
cDE0CmFWYzM4YTExNGQxMjY1YmNmZTVhNWE5ZjlkN2UKcDE1CmFWYzM4YTExNGQxMmE0ZjQ1MDM1
NjVjNmRlODI5CnAxNgphVmMzOGExMTRkMTNmNTZhY2RmNjczMDRiODczMQpwMTcKYUkwCih0STAw
CihsdHAxOAou
',3,1,134,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(44,'c38a114d7ce4ba07be8d86bc064','I0065','2012-07-31 08:09:43.622744','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3Y2U0YmEwN2JlOGQ4NmJjMDY0JwpWSTAwNjUKcDEKSTEKKEkwMAoobChsTlZK
b2huIFQuCnAyCihscDMKKFZDQVVMRklFTEQKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZC
aXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJLTEKKGxwNgooSTAwCihsKGxWYzM4
YTExNGQ3ZDA5NTg4YzNkYmFiMmY2MDcKKEkxClZQcmltYXJ5CnR0cDcKYShscDgKVmMzOGExMTRk
N2E2NjBmMGFjMzA1OWY0Y2Y4ZQpwOQphKGwobChsKGwobChsKGwobEk3NzAwMTEyMDAKKHRJMDAK
KGx0cDEwCi4=
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(45,'c38a114d2e62e3ac83cafcc0370','I0026','2012-07-31 08:09:43.646451','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyZTYyZTNhYzgzY2FmY2MwMzcwJwpWSTAwMjYKcDEKSTEKKEkwMAoobChsTlZE
YXZpZCBBbnRob255CnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJ
MgpWQmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxW
YzM4YTExNGQyZTk3N2M2YzJmMmQxZTBhZGIxCihJMQpWUHJpbWFyeQp0dHA3CmEobChscDgKVmMz
OGExMTRkMjdlMzJiNGJiYTdhZGI1ZTRhCnA5CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHAx
MAou
',2,1,1,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(46,'c38a114d21825717cb762abe0e3','I0018','2012-07-31 08:09:43.667008','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyMTgyNTcxN2NiNzYyYWJlMGUzJwpWSTAwMTgKcDEKSTAKKEkwMAoobChsTlZW
aWN0b3JpYQpwMgoobHAzCihWTEFXRk9SRApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJp
cnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkktMQoobChsKGxwNgpWYzM4YTExNGQx
ZGI2MDI4MTk2OTRlYmFmMzdiCnA3CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHA4Ci4=
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(47,'c38a114d03383d26a218474c0d','I0004','2012-07-31 08:09:43.696854','1996-01-23 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQwMzM4M2QyNmEyMTg0NzRjMGQnClZJMDAwNApwMQpJMAooSTAwCihsKGxOVlJv
c2VtYXJ5CnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmly
dGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYzM4YTEx
NGQwMzYyNjBmNTZiZDllODYxOGEKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZjMzhhMTE0
ZDA0MTUzZTUyYjUyZTBiYWY2NzUKKEkxClZQcmltYXJ5CnR0cDgKYShsKGxwOQpWYzM4YTExNGMx
OTMyNDZhOWIwOGFmOTZkOGMxCnAxMAphKGwobChsKGwobChsKGxwMTEKVmMzOGExMTRkMDQzN2Qy
YWE0N2E3MzJmNjFlZQpwMTIKYVZjMzhhMTE0ZDA0Nzc4MGE2ZDVmNTEzNGNkZTkKcDEzCmFWYzM4
YTExNGQwNWEzNmFmMTNjYjBjZGY1NmEyCnAxNAphSTgyMjM3MzIwMAoodEkwMAoobHRwMTUKLg==
',3,1,62,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(48,'c38a114d7db56899afb4995ee51','I0066','2012-07-31 08:09:43.720726','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3ZGI1Njg5OWFmYjQ5OTVlZTUxJwpWSTAwNjYKcDEKSTEKKEkwMAoobChsTlZM
YXVyZW5jZQpwMgoobHAzCihWS0FORQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRo
IE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkktMQoobHA2CihJMDAKKGwobFZjMzhhMTE0
ZDdkZTM4NzkyNzM3ZjY2MmVhZmIKKEkxClZQcmltYXJ5CnR0cDcKYShscDgKVmMzOGExMTRkNzQ2
MjY3Y2JkZmRhYTVhOGFjMgpwOQphKGwobChsKGwobChsKGwobEk3NzAwMTEyMDAKKHRJMDAKKGx0
cDEwCi4=
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(49,'c38a114d07e6f3e77075d10c4ea','I0006','2012-07-31 08:09:43.751697','1994-05-27 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQwN2U2ZjNlNzcwNzVkMTBjNGVhJwpWSTAwMDYKcDEKSTAKKEkwMAoobChsTlZL
YXRobGVlbgpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJp
cnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSTEKSTAKKGxwNgooSTAwCihsKGxWYzM4YTEx
NGQwODBlOWY1YTZkODdkNGFjYzUKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZjMzhhMTE0
ZDA4YzJkNWNmZDVjZDMxMDZhOTkKKEkxClZQcmltYXJ5CnR0cDgKYShscDkKVmMzOGExMTRkMDc1
NDQ5ZTViODljZDg0NjEyMgpwMTAKYShscDExClZjMzhhMTE0YzE5MzI0NmE5YjA4YWY5NmQ4YzEK
cDEyCmEobChsKGwobChsKGwobHAxMwpWYzM4YTExNGQwOTY0NTU1MjBhNGIyYTNhZWM2CnAxNAph
VmMzOGExMTRkMDk4MzRiOTQ5NWY3ZjczMDY4NwpwMTUKYVZjMzhhMTE0ZDBhZTZiM2IzYzJkNTI5
N2RhN2MKcDE2CmFJNzcwMDExMjAwCih0STAwCihsdHAxNwou
',3,0,51,35,0,1);
INSERT INTO "grampsdb_person" VALUES(50,'c38a114d3404912edd1eceb7703','I0030','2012-07-31 08:09:43.775484','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzNDA0OTEyZWRkMWVjZWI3NzAzJwpWSTAwMzAKcDEKSTEKKEkwMAoobChsTlZD
aHJpc3RvcGhlciBHZW9yZ2UKcDIKKGxwMwooVktFTk5FRFkKVgpJMDEKKEkxClYKdFYKdHA0CmFW
ClYKKEkyClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAK
KGwobFZjMzhhMTE0ZDM0MjcwZmE1MzBlOTFkMGVhNjAKKEkxClZQcmltYXJ5CnR0cDcKYShsKGxw
OApWYzM4YTExNGQyN2UzMmI0YmJhN2FkYjVlNGEKcDkKYShsKGwobChsKGwobChsSTAKKHRJMDAK
KGx0cDEwCi4=
',2,1,75,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(51,'c38a114d43468a5288d0933469b','I0038','2012-07-31 08:09:43.796316','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0MzQ2OGE1Mjg4ZDA5MzM0NjliJwpWSTAwMzgKcDEKSTAKKEkwMAoobChsTlZB
bWFuZGEKcDIKKGxwMwooVlNNSVRIClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGgg
TmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSS0xCihsKGwobHA2ClZjMzhhMTE0ZDNkNTRh
OTQ5ZGE3ZWZkZDMwYWYKcDcKYShsKGwobChsKGwobChsSTAKKHRJMDAKKGx0cDgKLg==
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(52,'c38a114d7765aba20b9c474c703','I0062','2012-07-31 08:09:43.823859','1994-05-27 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQ3NzY1YWJhMjBiOWM0NzRjNzAzJwpWSTAwNjIKcDEKSTEKKEkwMAoobChsTlZK
b2huCihscDIKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGggTmFt
ZQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA0CihJMDAKKGwobFZjMzhhMTE0ZDc3ODc2NDFj
OGY3NjY1ZDE5YTQKKEkxClZQcmltYXJ5CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0ZDc4Mzc2ODQ3
YzEzNDcwYWQyYWMKKEkxClZQcmltYXJ5CnR0cDYKYShsKGxwNwpWYzM4YTExNGQ0ZTczYThjN2U1
MWM4YmVkN2IKcDgKYShsKGwobChsKGwobChsSTc3MDAxMTIwMAoodEkwMAoobHRwOQou
',2,0,113,45,0,1);
INSERT INTO "grampsdb_person" VALUES(53,'c38a114d0643421b9bf4b1363c8','I0005','2012-07-31 08:09:43.851407','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwNjQzNDIxYjliZjRiMTM2M2M4JwpWSTAwMDUKcDEKSTEKKEkwMAoobChsTlZX
aWxsaWFtIEpvaG4gUm9iZXJ0CnAyCihscDMKKFZDQVZFTkRJU0gKVgpJMDEKKEkxClYKdFYKdHA0
CmFWClYKKEkyClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEkxCkkwCihscDYKKEkw
MAoobChsVmMzOGExMTRkMDY3NTZhZTI1NDcwMjAxN2YzNwooSTEKVlByaW1hcnkKdHRwNwphKEkw
MAoobChsVmMzOGExMTRkMDY5NDQ0ZmI0NzVlOWQ5Yzg5YgooSTEKVlByaW1hcnkKdHRwOAphKGxw
OQpWYzM4YTExNGQwNzU0NDllNWI4OWNkODQ2MTIyCnAxMAphKGwobChsKGwobChsKGwobEkwCih0
STAwCihsdHAxMQou
',2,0,103,52,0,1);
INSERT INTO "grampsdb_person" VALUES(54,'c38a114d6372dc431a965f92f46','I0053','2012-07-31 08:09:43.900291','1994-05-29 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MzcyZGM0MzFhOTY1ZjkyZjQ2JwpWSTAwNTMKcDEKSTAKKEkwMAoobChsTlZK
YWNxdWVsaW5lCnAyCihscDMKKFZCT1VWSUVSClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpW
QmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA2CihJMDAKKGwobFZjMzhh
MTE0ZDYzYTU2N2U4MjMzY2ExY2ZiMjMKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZjMzhh
MTE0ZDY0MzJiYmEzODY2NmJiMjJjYzYKKEkxClZQcmltYXJ5CnR0cDgKYShJMDAKKGwobFZjMzhh
MTE0ZDY0ZDEzYjM3NDY0NTM4NWM4MQooSTEKVlByaW1hcnkKdHRwOQphKEkwMAoobChsVmMzOGEx
MTRkNjU4M2I4NzIzMmJjZjkwOTI5CihJMQpWUHJpbWFyeQp0dHAxMAphKEkwMAoobChsVmMzOGEx
MTRkNjYyMWYwZDcxZTY4Mjc2YTNmZAooSTEKVlByaW1hcnkKdHRwMTEKYShJMDAKKGwobFZjMzhh
MTE0ZDY2MzViYTBhZGY2ZDkxYzhhOWMKKEkxClZQcmltYXJ5CnR0cDEyCmEoSTAwCihsKGxWYzM4
YTExNGQ2NjQzMmQ1MDJiYmQ4NGM5NmQKKEkxClZQcmltYXJ5CnR0cDEzCmEobHAxNApWYzM4YTEx
NGQ2NjYzMzA3OTgyMWNlNzA2NWRjCnAxNQphVmMzOGExMTRkNjFjMWU0Y2JmZjQ5YTIwZDAzNwpw
MTYKYShscDE3ClZjMzhhMTE0ZDU4YzdkMmYwMDc3YjhhODFmZTEKcDE4CmEobChsKGwobChsKGwo
bHAxOQpWYzM4YTExNGQ2NTk0YTNlOTg2ZWQwNDliNTA5CnAyMAphVmMzOGExMTRkNjViMTBhMDdj
Y2Y2ZjdmOGM2MgpwMjEKYVZjMzhhMTE0ZDY1ZTlkYjJjODVmNDc1YWFlNApwMjIKYVZjMzhhMTE0
ZDY2MTI0MGY5ODBmYTdhYWQzODUKcDIzCmFWYzM4YTExNGQ2Nzc0ZjMyZGVhZTQxZTBkNTM3CnAy
NAphSTc3MDE4NDAwMAoodEkwMAoobHRwMjUKLg==
',3,0,3,68,0,1);
INSERT INTO "grampsdb_person" VALUES(55,'c38a114d8235a1fd4299b4bbe5d','I0069','2012-07-31 08:09:43.921160','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ4MjM1YTFmZDQyOTliNGJiZTVkJwpWSTAwNjkKcDEKSTEKKEkwMAoobChsTlZI
dWdoCihscDIKKFZBQ0hJTkNMT1NTClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGgg
TmFtZQp0VgpJMApJMApWClYKVgp0KGxJLTEKSS0xCihsKGxwNApWYzM4YTExNGQ1YmQ3MjU4Zjdk
MDEyODg5OTUzCnA1CmEobChsKGwobChsKGwobChsSTc3MDAxMTIwMAoodEkwMAoobHRwNgou
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(56,'c38a114d2035792880a4d87f632','I0017','2012-07-31 08:09:43.941846','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyMDM1NzkyODgwYTRkODdmNjMyJwpWSTAwMTcKcDEKSTEKKEkwMAoobChsTlZD
aHJpc3RvcGhlcgpwMgoobHAzCihWTEFXRk9SRApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIK
VkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkktMQoobChsKGxwNgpWYzM4YTEx
NGQxZGI2MDI4MTk2OTRlYmFmMzdiCnA3CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHA4Ci4=
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(57,'c38a114d3282089665da658ea7f','I0029','2012-07-31 08:09:43.965601','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzMjgyMDg5NjY1ZGE2NThlYTdmJwpWSTAwMjkKcDEKSTAKKEkwMAoobChsTlZN
YXJ5IEtlcnJ5CnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpW
QmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYzM4
YTExNGQzMmE2OTQ2YWVhM2I3N2NlZDU3CihJMQpWUHJpbWFyeQp0dHA3CmEobChscDgKVmMzOGEx
MTRkMjdlMzJiNGJiYTdhZGI1ZTRhCnA5CmEobChsKGwobChsKGwobEkwCih0STAwCihsdHAxMAou
',3,1,26,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(58,'c38a114d7bf77736e2ca476de9c','I0064','2012-07-31 08:09:43.989371','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3YmY3NzczNmUyY2E0NzZkZTljJwpWSTAwNjQKcDEKSTEKKEkwMAoobChsTlZI
dW1waHJleQpwMgoobHAzCihWTUFIT05FWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJp
cnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkktMQoobHA2CihJMDAKKGwobFZjMzhh
MTE0ZDdjMjE4MjYzYThiN2JlMzQzY2UKKEkxClZQcmltYXJ5CnR0cDcKYShscDgKVmMzOGExMTRk
NzYxMjAwMDBiN2JiZWE3ODA0ZQpwOQphKGwobChsKGwobChsKGwobEk3NzAwMTEyMDAKKHRJMDAK
KGx0cDEwCi4=
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(59,'c38a114d56f77ee5da10a49ba53','I0048','2012-07-31 08:09:44.028988','1994-06-30 00:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NmY3N2VlNWRhMTBhNDliYTUzJwpWSTAwNDgKcDEKSTEKKEkwMAoobChsTlZK
b2huIFZlcm5vdQoobHAyCihWQk9VVklFUgpWCkkwMQooSTEKVgp0Vgp0cDMKYVYKVgooSTIKVkJp
cnRoIE5hbWUKdFYKSTAKSTAKVgpWClYKdChsSTEKSS0xCihscDQKKEkwMAoobChsVmMzOGExMTRk
NTcyNGUyMjQ3NzY4MDc0NzllNwooSTEKVlByaW1hcnkKdHRwNQphKEkwMAoobChsVmMzOGExMTRk
NTczMjk4ZDhjM2Q4NjBkYjA0ZAooSTEKVlByaW1hcnkKdHRwNgphKEkwMAoobChsVmMzOGExMTRk
NTdkNDI5Y2UwMTI5ZmUwMzcyNwooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmMzOGExMTRk
NTg2M2IxNzBlNDkxMzUyNWJmNgooSTEKVlByaW1hcnkKdHRwOAphKEkwMAoobChsVmMzOGExMTRk
NThiMTU2ZjFkZWEyNzg0MjA5NwooSTEKVlByaW1hcnkKdHRwOQphKGxwMTAKVmMzOGExMTRkNThj
N2QyZjAwNzdiOGE4MWZlMQpwMTEKYShsKGwobChsKGwobChsKGxwMTIKVmMzOGExMTRkNTg3MWYw
YzU3MjcwZjIyMDg0NApwMTMKYVZjMzhhMTE0ZDU4YTVhZWU3MjlmY2M0MmYxMDUKcDE0CmFWYzM4
YTExNGQ1OTI3NGY2ZjQ4NTg1ZjlmYjYzCnAxNQphSTc3Mjk0ODgwMAoodEkwMAoobHRwMTYKLg==
',2,0,NULL,114,-1,1);
INSERT INTO "grampsdb_person" VALUES(60,'c38a114d15e46138478ec346ba9','I0010','2012-07-31 08:09:44.052845','1994-10-16 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQxNWU0NjEzODQ3OGVjMzQ2YmE5JwpWSTAwMTAKcDEKSTEKKEkwMAoobChsTlZB
cm5vbGQKcDIKKGxwMwooVlNDSFdBUlpFTkVHR0VSClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJ
MgpWQmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSS0xCihscDYKKEkwMAoobChs
VmMzOGExMTRkMTYxNjI3MzhlNGVhYmVjNjYxZQooSTEKVlByaW1hcnkKdHRwNwphKGxwOApWYzM4
YTExNGQxNjE2MGZlMTY4ZmMzYWQ0N2E3CnA5CmEobChsKGwobChsKGwobChsSTc4MjI4MDAwMAoo
dEkwMAoobHRwMTAKLg==
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(61,'c38a114d72b426bb2b3f422e375','I0059','2012-07-31 08:09:44.074761','1994-05-29 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3MmI0MjZiYjJiM2Y0MjJlMzc1JwpWSTAwNTkKcDEKSTEKKEkwMAoobChsTlZB
cmlzdG90bGUKcDIKKGxwMwooVk9OQVNTSVMKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZC
aXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJLTEKKGwobHA2ClZjMzhhMTE0ZDY2
NjMzMDc5ODIxY2U3MDY1ZGMKcDcKYShsKGwobChsKGwobChsKGxJNzcwMTg0MDAwCih0STAwCihs
dHA4Ci4=
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(62,'c38a114d3d3748582dd3b615387','I0034','2012-07-31 08:09:44.095661','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzZDM3NDg1ODJkZDNiNjE1Mzg3JwpWSTAwMzQKcDEKSTEKKEkwMAoobChsTlZT
dGVwaGVuIEVkd2FyZApwMgoobHAzCihWU01JVEgKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEky
ClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJLTEKKGwobHA2ClZjMzhhMTE0
ZDNkNTRhOTQ5ZGE3ZWZkZDMwYWYKcDcKYShsKGwobChsKGwobChsKGxJMAoodEkwMAoobHRwOAou
',2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(63,'c38a114d2a340a5585b42b08873','I0023','2012-07-31 08:09:44.119521','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyYTM0MGE1NTg1YjQyYjA4ODczJwpWSTAwMjMKcDEKSTAKKEkwMAoobChsTlZL
YXRobGVlbiBIYXJ0aW5ndG9uCnAyCihscDMKKFZLRU5ORURZClYKSTAxCihJMQpWCnRWCnRwNAph
VgpWCihJMgpWQmlydGggTmFtZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAw
CihsKGxWYzM4YTExNGQyYTYyMjM0NzRlMTJlYjc5ZTFjCihJMQpWUHJpbWFyeQp0dHA3CmEobChs
cDgKVmMzOGExMTRkMjdlMzJiNGJiYTdhZGI1ZTRhCnA5CmEobChsKGwobChsKGwobEkwCih0STAw
CihsdHAxMAou
',3,1,121,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(64,'c38a114d5b83c0aa73d2f28869c','I0049','2012-07-31 08:09:44.144526','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ1YjgzYzBhYTczZDJmMjg4NjljJwpWSTAwNDkKcDEKSTAKKEkwMAoobChsTlZK
YW5ldApwMgoobHAzCihWTEVFClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFt
ZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSS0xCihscDYKKEkwMAoobChsVmMzOGExMTRkNWJi
MzM5NzRkZjhkZDExYmM4NwooSTEKVlByaW1hcnkKdHRwNwphKGxwOApWYzM4YTExNGQ1OGM3ZDJm
MDA3N2I4YTgxZmUxCnA5CmFWYzM4YTExNGQ1YmQ3MjU4ZjdkMDEyODg5OTUzCnAxMAphKGwobChs
KGwobChsKGwobEk3NzAwMTEyMDAKKHRJMDAKKGx0cDExCi4=
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(65,'c38a114d447760f3f08fdcdfd9e','I0039','2012-07-31 08:09:44.175311','1994-05-29 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0NDc3NjBmM2YwOGZkY2RmZDllJwpWSTAwMzkKcDEKSTEKKEkwMAoobChsTlZF
ZHdhcmQgTW9vcmUKcDIKKGxwMwooVktFTk5FRFkKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEky
ClZCaXJ0aCBOYW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZj
MzhhMTE0ZDQ0YTZhYTA2YjU2NDI3ZWY5YwooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmMz
OGExMTRkNDU4NTljMDRjN2ZiMzEyNTdhNwooSTEKVlByaW1hcnkKdHRwOAphKGxwOQpWYzM4YTEx
NGQ0NTk1YWVlOGQ2MmZlYzFkMTI0CnAxMAphKGxwMTEKVmMzOGExMTRjMTkzMjQ2YTliMDhhZjk2
ZDhjMQpwMTIKYShsKGwobChsKGwobChscDEzClZjMzhhMTE0ZDQ1NDUwZTI2YzhiZWNkYWM0ZjEK
cDE0CmFWYzM4YTExNGQ0NTYxZDM4NTcyNDJmNTQwMGNhCnAxNQphVmMzOGExMTRkNDY5NTExYmEy
ZGMzNDFhMDVmMwpwMTYKYUk3NzAxODQwMDAKKHRJMDAKKGx0cDE3Ci4=
',2,1,47,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(66,'c38a114d80a63c25cbae55b27c0','I0068','2012-07-31 08:09:44.196207','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ4MGE2M2MyNWNiYWU1NWIyN2MwJwpWSTAwNjgKcDEKSTAKKEkwMAoobChsTlZM
ZWUKcDIKKGxwMwooVkJPVVZJRVIKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBO
YW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJLTEKKGwobChscDYKVmMzOGExMTRkNThjN2Qy
ZjAwNzdiOGE4MWZlMQpwNwphKGwobChsKGwobChsKGxJNzcwMDExMjAwCih0STAwCihsdHA4Ci4=
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(67,'c38a114d2cd53749ec8335f2c8c','I0025','2012-07-31 08:09:44.222902','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyY2Q1Mzc0OWVjODMzNWYyYzhjJwpWSTAwMjUKcDEKSTEKKEkwMAoobChsTlZS
b2JlcnQgRnJhbmNpcwpwMgoobHAzCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgoo
STIKVkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkxCihscDYKKEkwMAoobChs
VmMzOGExMTRkMmQwNThlODdmYTVkNzc5YmMxYgooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChs
VmMzOGExMTRkMmQxMzcyNDVhMDhiNWNjMmEwYwooSTEKVlByaW1hcnkKdHRwOAphKGwobHA5ClZj
MzhhMTE0ZDI3ZTMyYjRiYmE3YWRiNWU0YQpwMTAKYShsKGwobChsKGwobChsSTAKKHRJMDAKKGx0
cDExCi4=
',2,1,2,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(68,'c38a114d16d101b6e1dbbbb704e','I0011','2012-07-31 08:09:44.247541','1994-06-30 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQxNmQxMDFiNmUxZGJiYmI3MDRlJwpWSTAwMTEKcDEKSTAKKEkwMAoobChsTlZN
YXJpYQpwMgoobHAzCihWU0hSSVZFUgpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRo
IE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkktMQoobHA2CihJMDAKKGwobFZjMzhhMTE0
ZDE3MDU2YTljNjU0OTdlMTgwNDMKKEkxClZQcmltYXJ5CnR0cDcKYShscDgKVmMzOGExMTRkMTYx
NjBmZTE2OGZjM2FkNDdhNwpwOQphKGxwMTAKVmMzOGExMTRkMGNlMzVkYjU4ZGZmN2ExN2RlZApw
MTEKYShsKGwobChsKGwobChsSTc3Mjk0ODgwMAoodEkwMAoobHRwMTIKLg==
',3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(69,'c38a114d798541deea603887194','I0063','2012-07-31 08:09:44.272277','1994-05-27 00:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3OTg1NDFkZWVhNjAzODg3MTk0JwpWSTAwNjMKcDEKSTAKKEkwMAoobChsTlZN
YXJnYXJldAoobHAyCihWS0VOTkVEWQpWCkkwMQooSTEKVgp0Vgp0cDMKYVYKVgooSTIKVkJpcnRo
IE5hbWUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDQKKEkwMAoobChsVmMzOGExMTRkNzli
NjA5MTliYjIzZmFjZmE0NgooSTEKVlByaW1hcnkKdHRwNQphKGxwNgpWYzM4YTExNGQ3YTY2MGYw
YWMzMDU5ZjRjZjhlCnA3CmEobHA4ClZjMzhhMTE0ZDRlNzNhOGM3ZTUxYzhiZWQ3YgpwOQphKGwo
bChsKGwobChsKGxJNzcwMDExMjAwCih0STAwCihsdHAxMAou
',3,1,60,NULL,0,-1);
CREATE TABLE "grampsdb_family_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "family_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "grampsdb_tag" ("id"),
    UNIQUE ("family_id", "tag_id")
);
CREATE TABLE "grampsdb_family" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "father_id" integer REFERENCES "grampsdb_person" ("id"),
    "mother_id" integer REFERENCES "grampsdb_person" ("id"),
    "family_rel_type_id" integer NOT NULL REFERENCES "grampsdb_familyreltype" ("id")
);
INSERT INTO "grampsdb_family" VALUES(1,'c38a114d4595aee8d62fec1d124','F0008','2012-07-31 08:09:44.302925','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0NTk1YWVlOGQ2MmZlYzFkMTI0JwpWRjAwMDgKcDEKVmMzOGExMTRkNDQ3NzYw
ZjNmMDhmZGNkZmQ5ZQpwMgpWYzM4YTExNGQ0NzI1YzgxMGFhMmM1YTRkZGY4CnAzCihscDQKKEkw
MAoobChsVmMzOGExMTRkNDgyN2M5OTcwOWE5ODJjOTQwMQooSTEKVkJpcnRoCnQoSTEKVkJpcnRo
CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0ZDQ5NzEwNWZjZDRiYTM4NjNhYWEKKEkxClZCaXJ0aAp0
KEkxClZCaXJ0aAp0dHA2CmEoSTAwCihsKGxWYzM4YTExNGQ0YjA0NDRiZDA1OTJkNmNkNTk0CihJ
MQpWQmlydGgKdChJMQpWQmlydGgKdHRwNwphKEkwClZNYXJyaWVkCnA4CnQobHA5CihJMDAKKGwo
bFZjMzhhMTE0ZGFmZjQyNjI5MDIwZDQ0Y2VjYjMKKEk4ClZGYW1pbHkKdHRwMTAKYShsKGwobChs
KGxJMAoodEkwMAp0cDExCi4=
',65,39,5);
INSERT INTO "grampsdb_family" VALUES(2,'c38a114d58c7d2f0077b8a81fe1','F0011','2012-07-31 08:09:44.324668','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ1OGM3ZDJmMDA3N2I4YTgxZmUxJwpWRjAwMTEKcDEKVmMzOGExMTRkNTZmNzdl
ZTVkYTEwYTQ5YmE1MwpwMgpWYzM4YTExNGQ1YjgzYzBhYTczZDJmMjg4NjljCnAzCihscDQKKEkw
MAoobChsVmMzOGExMTRkNjM3MmRjNDMxYTk2NWY5MmY0NgooSTEKVkJpcnRoCnQoSTEKVkJpcnRo
CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0ZDgwYTYzYzI1Y2JhZTU1YjI3YzAKKEkxClZCaXJ0aAp0
KEkxClZCaXJ0aAp0dHA2CmEoSTMKVlVua25vd24KcDcKdChscDgKKEkwMAoobChsVmMzOGExMTRk
Yjk5MTlhOGE0MWY2N2M3ZWE5ZQooSTgKVkZhbWlseQp0dHA5CmEobChsKGwobChsSTAKKHRJMDAK
dHAxMAou
',59,64,1);
INSERT INTO "grampsdb_family" VALUES(3,'c38a114d7063b0f411db48702e0','F0014','2012-07-31 08:09:44.334991','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3MDYzYjBmNDExZGI0ODcwMmUwJwpWRjAwMTQKcDEKVmMzOGExMTRkNzFkNjFh
NGEyMmJlYzFiZjA1OApwMgpWYzM4YTExNGQ3MDEzZGE0YmE2NjJiOTgwYTBlCnAzCihsKEkzClZV
bmtub3duCnA0CnQobChsKGwobChsKGxJMAoodEkwMAp0cDUKLg==
',2,36,1);
INSERT INTO "grampsdb_family" VALUES(4,'c38a114d5bd7258f7d012889953','F0019','2012-07-31 08:09:44.348511','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ1YmQ3MjU4ZjdkMDEyODg5OTUzJwpWRjAwMTkKcDEKVmMzOGExMTRkODIzNWEx
ZmQ0Mjk5YjRiYmU1ZApwMgpWYzM4YTExNGQ1YjgzYzBhYTczZDJmMjg4NjljCnAzCihsKEkwClZN
YXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZjMzhhMTE0ZGM0MzIwMjg5YzAyZTJiZjg0MWQKKEk4
ClZGYW1pbHkKdHRwNgphKGwobChsKGwobEkwCih0STAwCnRwNwou
',55,64,5);
INSERT INTO "grampsdb_family" VALUES(5,'c38a114d746267cbdfdaa5a8ac2','F0016','2012-07-31 08:09:44.362322','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3NDYyNjdjYmRmZGFhNWE4YWMyJwpWRjAwMTYKcDEKVmMzOGExMTRkN2RiNTY4
OTlhZmI0OTk1ZWU1MQpwMgpWYzM4YTExNGQ3Mzg0MDY0MGMyMWZjNjEwZThhCnAzCihsKEkwClZN
YXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZjMzhhMTE0ZGMwNDFhMzJhMGU0ZGRkMDY2MjQKKEk4
ClZGYW1pbHkKdHRwNgphKGwobChsKGwobEkwCih0STAwCnRwNwou
',48,33,5);
INSERT INTO "grampsdb_family" VALUES(6,'c38a114cfda4f30968d3f1d126a','F0012','2012-07-31 08:09:44.376757','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGNmZGE0ZjMwOTY4ZDNmMWQxMjZhJwpWRjAwMTIKcDEKVmMzOGExMTRkNWNhMjg4
N2VkOGUzN2MzNTIwYgpwMgpWYzM4YTExNGQ1ZDk5YjUxN2VlMmYwZjFiNGMKcDMKKGxwNAooSTAw
CihsKGxWYzM4YTExNGNmYTQxYmM4ZDk1YjI5OWUzNmRiCihJMQpWQmlydGgKdChJMQpWQmlydGgK
dHRwNQphKEkzClZVbmtub3duCnA2CnQobChsKGwobChsKGxJMAoodEkwMAp0cDcKLg==
',18,26,1);
INSERT INTO "grampsdb_family" VALUES(7,'c38a114d7a660f0ac3059f4cf8e','F0018','2012-07-31 08:09:44.390192','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3YTY2MGYwYWMzMDU5ZjRjZjhlJwpWRjAwMTgKcDEKVmMzOGExMTRkN2NlNGJh
MDdiZThkODZiYzA2NApwMgpWYzM4YTExNGQ3OTg1NDFkZWVhNjAzODg3MTk0CnAzCihsKEkwClZN
YXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZjMzhhMTE0ZGMyZjE4OTI5YTRkMmRiMTgwZjAKKEk4
ClZGYW1pbHkKdHRwNgphKGwobChsKGwobEkwCih0STAwCnRwNwou
',44,69,5);
INSERT INTO "grampsdb_family" VALUES(8,'c38a114d075449e5b89cd846122','F0002','2012-07-31 08:09:44.406860','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwNzU0NDllNWI4OWNkODQ2MTIyJwpWRjAwMDIKcDEKVmMzOGExMTRkMDY0MzQy
MWI5YmY0YjEzNjNjOApwMgpWYzM4YTExNGQwN2U2ZjNlNzcwNzVkMTBjNGVhCnAzCihsKEkwClZN
YXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZjMzhhMTE0ZDk5NjM3ODk2ODU5MmM5Nzg2YTIKKEk4
ClZGYW1pbHkKdHRwNgphKGwobChsKGwobEkwCih0STAwCnRwNwou
',53,49,5);
INSERT INTO "grampsdb_family" VALUES(9,'c38a114d3d54a949da7efdd30af','F0007','2012-07-31 08:09:44.432352','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzZDU0YTk0OWRhN2VmZGQzMGFmJwpWRjAwMDcKcDEKVmMzOGExMTRkM2QzNzQ4
NTgyZGQzYjYxNTM4NwpwMgpWYzM4YTExNGQzZGU1ZDZkNDhmYjY4YmQ4Y2RiCnAzCihscDQKKEkw
MAoobChsVmMzOGExMTRkNDAyZGVjMmQ0YTVlNTEwZjdkCihJMQpWQmlydGgKdChJMQpWQmlydGgK
dHRwNQphKEkwMAoobChsVmMzOGExMTRkNDE2M2Q5MTJmOWNhZGU5YjIyMgooSTEKVkJpcnRoCnQo
STEKVkJpcnRoCnR0cDYKYShJMDAKKGwobFZjMzhhMTE0ZDQzNDY4YTUyODhkMDkzMzQ2OWIKKEkx
ClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA3CmEoSTAKVk1hcnJpZWQKcDgKdChscDkKKEkwMAoobChs
VmMzOGExMTRkYWQyMTNkM2JkODgwN2VmYTE2MgooSTgKVkZhbWlseQp0dHAxMAphKGwobChsKGwo
bEkwCih0STAwCnRwMTEKLg==
',62,35,5);
INSERT INTO "grampsdb_family" VALUES(10,'c38a114c193246a9b08af96d8c1','F0001','2012-07-31 08:09:44.483414','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxOTMyNDZhOWIwOGFmOTZkOGMxJwpWRjAwMDEKcDEKVmMzOGExMTRiZmZiOTJm
N2QwMTM0YWIyNmFkCnAyClZjMzhhMTE0Y2ZhNDFiYzhkOTViMjk5ZTM2ZGIKcDMKKGxwNAooSTAw
CihsKGxWYzM4YTExNGNmZjYyMDRmZGU2NGVjYTU5MDAxCihJMQpWQmlydGgKdChJMQpWQmlydGgK
dHRwNQphKEkwMAoobChsVmMzOGExMTRkNWU2MjVlMmEzZTgzYWUyNDYzMQooSTEKVkJpcnRoCnQo
STEKVkJpcnRoCnR0cDYKYShJMDAKKGwobFZjMzhhMTE0ZDAzMzgzZDI2YTIxODQ3NGMwZAooSTEK
VkJpcnRoCnQoSTEKVkJpcnRoCnR0cDcKYShJMDAKKGwobFZjMzhhMTE0ZDA3ZTZmM2U3NzA3NWQx
MGM0ZWEKKEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA4CmEoSTAwCihsKGxWYzM4YTExNGQxMGQ0
NGFjODlkNGJkYmFmZWVhCihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwOQphKEkwMAoobChsVmMz
OGExMTRkMWUzMWVhMDRlYTE5Mjc0ZThlYwooSTEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDEwCmEo
STAwCihsKGxWYzM4YTExNGQyNTQyYjViMTYzYWZiOTY2M2VmCihJMQpWQmlydGgKdChJMQpWQmly
dGgKdHRwMTEKYShJMDAKKGwobFZjMzhhMTE0ZDNkZTVkNmQ0OGZiNjhiZDhjZGIKKEkxClZCaXJ0
aAp0KEkxClZCaXJ0aAp0dHAxMgphKEkwMAoobChsVmMzOGExMTRkNDQ3NzYwZjNmMDhmZGNkZmQ5
ZQooSTEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDEzCmEoSTAKVk1hcnJpZWQKcDE0CnQobHAxNQoo
STAwCihsKGxWYzM4YTExNGQ5N2YyYWY2MTg5NGU4MjVmYTAzCihJOApWRmFtaWx5CnR0cDE2CmEo
bChsKGwobChsSTAKKHRJMDAKdHAxNwou
',7,42,5);
INSERT INTO "grampsdb_family" VALUES(11,'c38a114d61c1e4cbff49a20d037','F0013','2012-07-31 08:09:44.511999','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MWMxZTRjYmZmNDlhMjBkMDM3JwpWRjAwMTMKcDEKVmMzOGExMTRkNWU2MjVl
MmEzZTgzYWUyNDYzMQpwMgpWYzM4YTExNGQ2MzcyZGM0MzFhOTY1ZjkyZjQ2CnAzCihscDQKKEkw
MAoobChsVmMzOGExMTRkNjgzMTcwZjIzYTU5ZDUwMTc5NQooSTEKVkJpcnRoCnQoSTEKVkJpcnRo
CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0ZDZiMjFiNTBjYjdmYTlmMmQyYWYKKEkxClZCaXJ0aAp0
KEkxClZCaXJ0aAp0dHA2CmEoSTAwCihsKGxWYzM4YTExNGQ2ZDUxOWZiY2E0OTBhZDc5NjEyCihJ
MQpWQmlydGgKdChJMQpWQmlydGgKdHRwNwphKEkwClZNYXJyaWVkCnA4CnQobHA5CihJMDAKKGwo
bFZjMzhhMTE0ZGJkYzI1MTJjZGI3YmQyOWIwMAooSTgKVkZhbWlseQp0dHAxMAphKGwobChsKGwo
bEkwCih0STAwCnRwMTEKLg==
',38,54,5);
INSERT INTO "grampsdb_family" VALUES(12,'c38a114c1956448390ebdeb7402','F0009','2012-07-31 08:09:44.540262','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxOTU2NDQ4MzkwZWJkZWI3NDAyJwpWRjAwMDkKcDEKVmMzOGExMTRkNGM2MjU2
MTYwOTIxYmNhYTVmMgpwMgpWYzM4YTExNGQ0ZmY2ZGZkOTMxNGI5MWRkMDMKcDMKKGxwNAooSTAw
CihsKGxWYzM4YTExNGJmZmI5MmY3ZDAxMzRhYjI2YWQKKEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0
dHA1CmEoSTAwCihsKGxWYzM4YTExNGQ3ZTlmYjlhMWU5Nzk3Yzk1NTkKKEkxClZCaXJ0aAp0KEkx
ClZCaXJ0aAp0dHA2CmEoSTAwCihsKGxWYzM4YTExNGQ3MDEzZGE0YmE2NjJiOTgwYTBlCihJMQpW
QmlydGgKdChJMQpWQmlydGgKdHRwNwphKEkwClZNYXJyaWVkCnA4CnQobHA5CihJMDAKKGwobFZj
MzhhMTE0ZGIyYzI2MTI4MmU4YjhmOTFkNjYKKEk4ClZGYW1pbHkKdHRwMTAKYShsKGwobChsKGxJ
MAoodEkwMAp0cDExCi4=
',4,16,5);
INSERT INTO "grampsdb_family" VALUES(13,'c38a114d66633079821ce7065dc','F0015','2012-07-31 08:09:44.553282','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NjYzMzA3OTgyMWNlNzA2NWRjJwpWRjAwMTUKcDEKVmMzOGExMTRkNzJiNDI2
YmIyYjNmNDIyZTM3NQpwMgpWYzM4YTExNGQ2MzcyZGM0MzFhOTY1ZjkyZjQ2CnAzCihsKEkzClZV
bmtub3duCnA0CnQobChsKGwobChsKGxJMAoodEkwMAp0cDUKLg==
',61,54,1);
INSERT INTO "grampsdb_family" VALUES(14,'c38a114d76120000b7bbea7804e','F0017','2012-07-31 08:09:44.566656','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3NjEyMDAwMGI3YmJlYTc4MDRlJwpWRjAwMTcKcDEKVmMzOGExMTRkN2JmNzc3
MzZlMmNhNDc2ZGU5YwpwMgpWYzM4YTExNGQ3NWMyNjBiYmIyNjEzMDNiMjVjCnAzCihsKEkwClZN
YXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZjMzhhMTE0ZGMxOTYwNTYwZmI4MGNmYmM0MzAKKEk4
ClZGYW1pbHkKdHRwNgphKGwobChsKGwobEkwCih0STAwCnRwNwou
',58,5,5);
INSERT INTO "grampsdb_family" VALUES(15,'c38a114d16160fe168fc3ad47a7','F0004','2012-07-31 08:09:44.576826','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxNjE2MGZlMTY4ZmMzYWQ0N2E3JwpWRjAwMDQKcDEKVmMzOGExMTRkMTVlNDYx
Mzg0NzhlYzM0NmJhOQpwMgpWYzM4YTExNGQxNmQxMDFiNmUxZGJiYmI3MDRlCnAzCihsKEkzClZV
bmtub3duCnA0CnQobChsKGwobChsKGxJMAoodEkwMAp0cDUKLg==
',60,68,1);
INSERT INTO "grampsdb_family" VALUES(16,'c38a114d0ce35db58dff7a17ded','F0003','2012-07-31 08:09:44.610591','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwY2UzNWRiNThkZmY3YTE3ZGVkJwpWRjAwMDMKcDEKVmMzOGExMTRkMGJiMWJh
YjVlMDZlYTZjZWJmZgpwMgpWYzM4YTExNGQxMGQ0NGFjODlkNGJkYmFmZWVhCnAzCihscDQKKEkw
MAoobChsVmMzOGExMTRkMTQ4MzJiNjk3M2ZmMGU3NGY1MgooSTEKVkJpcnRoCnQoSTEKVkJpcnRo
CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0ZDE2ZDEwMWI2ZTFkYmJiYjcwNGUKKEkxClZCaXJ0aAp0
KEkxClZCaXJ0aAp0dHA2CmEoSTAwCihsKGxWYzM4YTExNGQxODQ2MTYwMGZlMjM0NzcxNWRiCihJ
MQpWQmlydGgKdChJMQpWQmlydGgKdHRwNwphKEkwMAoobChsVmMzOGExMTRkMTk4MWZlN2YzNzdm
M2NjMjRlZAooSTEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDgKYShJMDAKKGwobFZjMzhhMTE0ZDFi
ODUxNmNjOTRmYTdjMWQzMDIKKEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA5CmEoSTAKVk1hcnJp
ZWQKcDEwCnQobHAxMQooSTAwCihsKGxWYzM4YTExNGQ5ZGUxZjU1NWRmZmQ1ZDhkOTYxCihJOApW
RmFtaWx5CnR0cDEyCmEobChsKGwobChsSTAKKHRJMDAKdHAxMwou
',20,43,5);
INSERT INTO "grampsdb_family" VALUES(17,'c38a114d4e73a8c7e51c8bed7b','F0010','2012-07-31 08:09:44.646814','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZTczYThjN2U1MWM4YmVkN2InClZGMDAxMApwMQpWYzM4YTExNGQ1MGYzMGQ1
MzhlMDgwMjU4ZDQ1CnAyClZjMzhhMTE0ZDU0NmJjNTZkNGE5MmUyOWVmZQpwMwoobHA0CihJMDAK
KGwobFZjMzhhMTE0ZDczODQwNjQwYzIxZmM2MTBlOGEKKEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0
dHA1CmEoSTAwCihsKGxWYzM4YTExNGQ3NWMyNjBiYmIyNjEzMDNiMjVjCihJMQpWQmlydGgKdChJ
MQpWQmlydGgKdHRwNgphKEkwMAoobChsVmMzOGExMTRkNzc2NWFiYTIwYjljNDc0YzcwMwooSTEK
VkJpcnRoCnQoSTEKVkJpcnRoCnR0cDcKYShJMDAKKGwobFZjMzhhMTE0ZDc5ODU0MWRlZWE2MDM4
ODcxOTQKKEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA4CmEoSTAwCihsKGxWYzM4YTExNGQ0YzYy
NTYxNjA5MjFiY2FhNWYyCihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwOQphKEkwClZNYXJyaWVk
CnAxMAp0KGxwMTEKKEkwMAoobChsVmMzOGExMTRkYjZlMWM1NzZhMjVhOWM5Y2YwNwooSTgKVkZh
bWlseQp0dHAxMgphKGwobChsKGwobEkwCih0STAwCnRwMTMKLg==
',10,27,5);
INSERT INTO "grampsdb_family" VALUES(18,'c38a114d27e32b4bba7adb5e4a','F0006','2012-07-31 08:09:44.705056','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyN2UzMmI0YmJhN2FkYjVlNGEnClZGMDAwNgpwMQpWYzM4YTExNGQyNTQyYjVi
MTYzYWZiOTY2M2VmCnAyClZjMzhhMTE0ZDI5NzJiMmRkMjcyMjc2ZjQ5ZGIKcDMKKGxwNAooSTAw
CihsKGxWYzM4YTExNGQyYTM0MGE1NTg1YjQyYjA4ODczCihJMQpWQmlydGgKdChJMQpWQmlydGgK
dHRwNQphKEkwMAoobChsVmMzOGExMTRkMmI4Nzk0NDRkOGRiNWMyMWNmZAooSTEKVkJpcnRoCnQo
STEKVkJpcnRoCnR0cDYKYShJMDAKKGwobFZjMzhhMTE0ZDJjZDUzNzQ5ZWM4MzM1ZjJjOGMKKEkx
ClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA3CmEoSTAwCihsKGxWYzM4YTExNGQyZTYyZTNhYzgzY2Fm
Y2MwMzcwCihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwOAphKEkwMAoobChsVmMzOGExMTRkMmZi
MTI0ZjE2MTE3MGU3OTQ4CihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwOQphKEkwMAoobChsVmMz
OGExMTRkMzEyNGI2YjI4NjhkN2Y4YjY1NAooSTEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDEwCmEo
STAwCihsKGxWYzM4YTExNGQzMjgyMDg5NjY1ZGE2NThlYTdmCihJMQpWQmlydGgKdChJMQpWQmly
dGgKdHRwMTEKYShJMDAKKGwobFZjMzhhMTE0ZDM0MDQ5MTJlZGQxZWNlYjc3MDMKKEkxClZCaXJ0
aAp0KEkxClZCaXJ0aAp0dHAxMgphKEkwMAoobChsVmMzOGExMTRkMzYyM2FiM2MwOWZmN2M5N2U4
NgooSTEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDEzCmEoSTAwCihsKGxWYzM4YTExNGQzODA3Njdi
YWNiZjY3NzY3ZWZjCihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwMTQKYShJMDAKKGwobFZjMzhh
MTE0ZDNiMTY5MjQzODFkNGJlOWVlZGMKKEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHAxNQphKEkw
ClZNYXJyaWVkCnAxNgp0KGxwMTcKKEkwMAoobChsVmMzOGExMTRkYTlkNjI4YWU4NWMyYmIzZGNh
YQooSTgKVkZhbWlseQp0dHAxOAphKGwobChsKGwobEkwCih0STAwCnRwMTkKLg==
',29,32,5);
INSERT INTO "grampsdb_family" VALUES(19,'c38a114d1db602819694ebaf37b','F0005','2012-07-31 08:09:44.734728','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxZGI2MDI4MTk2OTRlYmFmMzdiJwpWRjAwMDUKcDEKVmMzOGExMTRkMWQ2M2Nj
ZjU1NzQxZjI0MjE5NQpwMgpWYzM4YTExNGQxZTMxZWEwNGVhMTkyNzRlOGVjCnAzCihscDQKKEkw
MAoobChsVmMzOGExMTRkMjAzNTc5Mjg4MGE0ZDg3ZjYzMgooSTEKVkJpcnRoCnQoSTEKVkJpcnRo
CnR0cDUKYShJMDAKKGwobFZjMzhhMTE0ZDIxODI1NzE3Y2I3NjJhYmUwZTMKKEkxClZCaXJ0aAp0
KEkxClZCaXJ0aAp0dHA2CmEoSTAwCihsKGxWYzM4YTExNGQyMmUxZmI3OWFjOGJhNDg0NjEyCihJ
MQpWQmlydGgKdChJMQpWQmlydGgKdHRwNwphKEkwMAoobChsVmMzOGExMTRkMjQxNDQzZmEyMDAy
MzVmMDUxOAooSTEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDgKYShJMwpWVW5rbm93bgpwOQp0KGxw
MTAKKEkwMAoobChsVmMzOGExMTRkYTFlMmNmOWE4ZDFkNTIyZDEwNQooSTgKVkZhbWlseQp0dHAx
MQphKGwobChsKGwobEkwCih0STAwCnRwMTIKLg==
',34,8,1);
CREATE TABLE "grampsdb_citation" (
    "calendar" integer NOT NULL,
    "modifier" integer NOT NULL,
    "quality" integer NOT NULL,
    "day1" integer NOT NULL,
    "month1" integer NOT NULL,
    "year1" integer NOT NULL,
    "slash1" bool NOT NULL,
    "day2" integer,
    "month2" integer,
    "year2" integer,
    "slash2" bool,
    "text" varchar(80) NOT NULL,
    "sortval" integer NOT NULL,
    "newyear" integer NOT NULL,
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "confidence" integer,
    "page" varchar(50),
    "source_id" integer
);
CREATE TABLE "grampsdb_source" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "title" varchar(50),
    "author" varchar(50),
    "pubinfo" varchar(50),
    "abbrev" varchar(50)
);
INSERT INTO "grampsdb_source" VALUES(1,'c38a114d8814b63920822f2f29f','S0006','2012-07-31 08:09:44.743194','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4ODE0YjYzOTIwODIyZjJmMjlmJwpWUzAwMDYKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDYKcDIKVgpWCihscDMKVmMzOGExMTRkODg5MWY5ZTNmZDk5YzlmMzFiOQpwNAphKGxWCkkw
CihkKGxJMDAKdHA1Ci4=
','No title - ID S0006','','','');
INSERT INTO "grampsdb_source" VALUES(2,'c38a114d8b043818246b4992582','S0009','2012-07-31 08:09:44.748861','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4YjA0MzgxODI0NmI0OTkyNTgyJwpWUzAwMDkKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDkKcDIKVgpWCihscDMKVmMzOGExMTRkOGI2MThkNGEyYjAzOGZkNDljOApwNAphKGxWCkkw
CihkKGxJMDAKdHA1Ci4=
','No title - ID S0009','','','');
INSERT INTO "grampsdb_source" VALUES(3,'c38a114d851147e39a312fa7514','S0003','2012-07-31 08:09:44.754469','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4NTExNDdlMzlhMzEyZmE3NTE0JwpWUzAwMDMKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDMKcDIKVgpWCihscDMKVmMzOGExMTRkODU4MzIzZmNmMmZkZDBlMDdiCnA0CmEobFYKSTAK
KGQobEkwMAp0cDUKLg==
','No title - ID S0003','','','');
INSERT INTO "grampsdb_source" VALUES(4,'c38a114d8326b4ba015f61c98b9','S0001','2012-07-31 08:09:44.759980','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4MzI2YjRiYTAxNWY2MWM5OGI5JwpWUzAwMDEKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDEKcDIKVgpWCihscDMKVmMzOGExMTRkODM5N2U5NTU5ZjA5MjhhZGU3MQpwNAphKGxWCkkw
CihkKGxJMDAKdHA1Ci4=
','No title - ID S0001','','','');
INSERT INTO "grampsdb_source" VALUES(5,'c38a114d8bf51f016eebb0da9be','S0010','2012-07-31 08:09:44.765585','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4YmY1MWYwMTZlZWJiMGRhOWJlJwpWUzAwMTAKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMTAKcDIKVgpWCihscDMKVmMzOGExMTRkOGM1NGE5ZmE0ZDcwYjcyODIzNgpwNAphKGxWCkkw
CihkKGxJMDAKdHA1Ci4=
','No title - ID S0010','','','');
INSERT INTO "grampsdb_source" VALUES(6,'c38a114d84228b2104ff66cc120','S0002','2012-07-31 08:09:44.771104','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4NDIyOGIyMTA0ZmY2NmNjMTIwJwpWUzAwMDIKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDIKcDIKVgpWCihscDMKVmMzOGExMTRkODQ4M2M3MjRjOWE4NzY2N2ExYwpwNAphKGxWCkkw
CihkKGxJMDAKdHA1Ci4=
','No title - ID S0002','','','');
INSERT INTO "grampsdb_source" VALUES(7,'c38a114d8a1403bace9ca6b14b4','S0008','2012-07-31 08:09:44.776633','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4YTE0MDNiYWNlOWNhNmIxNGI0JwpWUzAwMDgKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDgKcDIKVgpWCihscDMKVmMzOGExMTRkOGE3ZjMxZDllYmQ2NDg1MjVkCnA0CmEobFYKSTAK
KGQobEkwMAp0cDUKLg==
','No title - ID S0008','','','');
INSERT INTO "grampsdb_source" VALUES(8,'c38a114d861483e0ced6f173f45','S0004','2012-07-31 08:09:44.782158','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4NjE0ODNlMGNlZDZmMTczZjQ1JwpWUzAwMDQKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDQKcDIKVgpWCihscDMKVmMzOGExMTRkODY3MTM0MGI3MTA4M2Q0ZmE1NQpwNAphKGxWCkkw
CihkKGxJMDAKdHA1Ci4=
','No title - ID S0004','','','');
INSERT INTO "grampsdb_source" VALUES(9,'c38a114d86f500717d7c4a275aa','S0005','2012-07-31 08:09:44.787812','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4NmY1MDA3MTdkN2M0YTI3NWFhJwpWUzAwMDUKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDUKcDIKVgpWCihscDMKVmMzOGExMTRkODc2MjQ5YjhmZjMzMmU1N2FhZgpwNAphKGxWCkkw
CihkKGxJMDAKdHA1Ci4=
','No title - ID S0005','','','');
INSERT INTO "grampsdb_source" VALUES(10,'c38a114d89211aa7b6d74b4c8e6','S0007','2012-07-31 08:09:44.793350','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4OTIxMWFhN2I2ZDc0YjRjOGU2JwpWUzAwMDcKcDEKVk5vIHRpdGxlIC0gSUQg
UzAwMDcKcDIKVgpWCihscDMKVmMzOGExMTRkODk5NWEwYjcwZDg4NjJkNmI2NwpwNAphKGxWCkkw
CihkKGxJMDAKdHA1Ci4=
','No title - ID S0007','','','');
INSERT INTO "grampsdb_source" VALUES(11,'c38a114d8cd87e16608c276546','S0011','2012-07-31 08:09:44.798894','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4Y2Q4N2UxNjYwOGMyNzY1NDYnClZTMDAxMQpwMQpWTm8gdGl0bGUgLSBJRCBT
MDAxMQpwMgpWClYKKGxwMwpWYzM4YTExNGQ4ZDQ2YzFjMzBmZGRiOGNmZmRmCnA0CmEobFYKSTAK
KGQobEkwMAp0cDUKLg==
','No title - ID S0011','','','');
CREATE TABLE "grampsdb_event" (
    "calendar" integer NOT NULL,
    "modifier" integer NOT NULL,
    "quality" integer NOT NULL,
    "day1" integer NOT NULL,
    "month1" integer NOT NULL,
    "year1" integer NOT NULL,
    "slash1" bool NOT NULL,
    "day2" integer,
    "month2" integer,
    "year2" integer,
    "slash2" bool,
    "text" varchar(80) NOT NULL,
    "sortval" integer NOT NULL,
    "newyear" integer NOT NULL,
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "event_type_id" integer NOT NULL REFERENCES "grampsdb_eventtype" ("id"),
    "description" varchar(50) NOT NULL,
    "place_id" integer
);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1954,0,0,0,0,0,'1954',2434744,0,1,'c38a114d2e977c6c2f2d1e0adb1','E0051','2012-07-31 08:09:44.815730','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyZTk3N2M2YzJmMmQxZTBhZGIxJwpWRTAwNTEKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5NTQKSTAwCnRWMTk1NApwMwpJMjQzNDc0NApJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1953,0,0,0,0,0,'1953',2434379,0,2,'c38a114d2d137245a08b5cc2a0c','E0050','2012-07-31 08:09:44.823822','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyZDEzNzI0NWEwOGI1Y2MyYTBjJwpWRTAwNTAKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5NTMKSTAwCnRWMTk1MwpwMwpJMjQzNDM3OQpJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,7,1929,0,0,0,0,0,'28 JUL 1929',2425821,0,3,'c38a114d63a567e8233ca1cfb23','E0103','2012-07-31 08:09:44.833117','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2M2E1NjdlODIzM2NhMWNmYjIzJwpWRTAxMDMKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTI4Ckk3CkkxOTI5CkkwMAp0VjI4IEpVTCAxOTI5CnAzCkkyNDI1ODIxCkkw
CnRWClZjMzhhMTE0ZDY0MTdmZjY3NjFmZGZjYmJkZApwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',4,'',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,4,'c38a114d17056a9c65497e18043','E0036','2012-07-31 08:09:44.841457','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxNzA1NmE5YzY1NDk3ZTE4MDQzJwpWRTAwMzYKcDEKKEkyNgpWRWR1Y2F0aW9u
CnAyCnROVkdlb3JnZXRvd24gVW5pdmVyc2l0eQpwMwpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',18,'Georgetown University',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,5,'c38a114d57d429ce0129fe03727','E0091','2012-07-31 08:09:44.850282','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1N2Q0MjljZTAxMjlmZTAzNzI3JwpWRTAwOTEKcDEKKEkxOQpWQnVyaWFsCnAy
CnROVgpWYzM4YTExNGQ1ODRmZTJiNGJjNWVhMjYzNGYKcDMKKGwobChsKGxJMApJMDAKdHA0Ci4=
',11,'',11);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1954,0,0,0,0,0,'1954',2434744,0,6,'c38a114d14b47c86c3e5487c8f6','E0034','2012-07-31 08:09:44.858275','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxNGI0N2M4NmMzZTU0ODdjOGY2JwpWRTAwMzQKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5NTQKSTAwCnRWMTk1NApwMwpJMjQzNDc0NApJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,2,1964,0,0,0,0,0,'FEB 1964',2438427,0,7,'c38a114d19a615ea911ffd89576','E0037','2012-07-31 08:09:44.867004','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxOWE2MTVlYTkxMWZmZDg5NTc2JwpWRTAwMzcKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTIKSTE5NjQKSTAwCnRWRkVCIDE5NjQKcDMKSTI0Mzg0MjcKSTAKdFYK
VmMzOGExMTRkMWE0MWUxYjJhZWI2Yjc4ZjJiNApwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',4,'',27);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,8,'c38a114d4e452f8b0a7fa36895e','E0073','2012-07-31 08:09:44.874903','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZTQ1MmY4YjBhN2ZhMzY4OTVlJwpWRTAwNzMKcDEKKEkwClYKdE5WV2Vic3Rl
ciBTdC4sIEJvc3RvbiwgTUEKcDIKUycnCihsKGwobChsSTAKSTAwCnRwMwou
',47,'Webster St., Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,5,1994,0,0,0,0,0,'23 MAY 1994',2449496,0,9,'c38a114d64d13b374645385c81','E0105','2012-07-31 08:09:44.883646','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NGQxM2IzNzQ2NDUzODVjODEnClZFMDEwNQpwMQooSTE5ClZCdXJpYWwKcDIK
dChJMApJMApJMAooSTIzCkk1CkkxOTk0CkkwMAp0VjIzIE1BWSAxOTk0CnAzCkkyNDQ5NDk2Ckkw
CnRWClZjMzhhMTE0ZDI3NWExNDFjNGM1ZGViY2JjYwpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',11,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,10,'c38a114d7d09588c3dbab2f607','E0126','2012-07-31 08:09:44.891665','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3ZDA5NTg4YzNkYmFiMmY2MDcnClZFMDEyNgpwMQooSTM3ClZPY2N1cGF0aW9u
CnAyCnROVkNsZXJrCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',29,'Clerk',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,5,1953,0,0,0,0,0,'23 MAY 1953',2434521,0,11,'c38a114d9de1f555dffd5d8d961','E0131','2012-07-31 08:09:44.899573','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ5ZGUxZjU1NWRmZmQ1ZDhkOTYxJwpWRTAxMzEKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMjMKSTUKSTE5NTMKSTAwCnRWMjMgTUFZIDE5NTMKcDMKSTI0MzQ1MjEK
STAKdFYKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,8,1944,0,0,0,0,0,'2 AUG 1944',2431305,0,12,'c38a114d00613403bac4f97de02','E0019','2012-07-31 08:09:44.908392','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMDYxMzQwM2JhYzRmOTdkZTAyJwpWRTAwMTkKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTIKSTgKSTE5NDQKSTAwCnRWMiBBVUcgMTk0NApwMwpJMjQzMTMwNQpJMAp0
VgpWYzM4YTExNGQwMGY0NmIyNjQyMjAwNWRlM2Y3CnA0CihsKGwobChsSTAKSTAwCnRwNQou
',5,'',14);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,13,'c38a114d7de38792737f662eafb','E0127','2012-07-31 08:09:44.916610','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3ZGUzODc5MjczN2Y2NjJlYWZiJwpWRTAxMjcKcDEKKEkzNwpWT2NjdXBhdGlv
bgpwMgp0TlZUZWFtc3RlcgpwMwpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',29,'Teamster',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,14,'c38a114d12d31f11431f97245e5','E0032','2012-07-31 08:09:44.924522','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxMmQzMWYxMTQzMWY5NzI0NWU1JwpWRTAwMzIKcDEKKEkwClYKdE5WVGltYmVy
bGF3biwgTUQKcDIKUycnCihsKGwobChsSTAKSTAwCnRwMwou
',47,'Timberlawn, MD',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,8,1963,0,0,0,0,0,'AUG 1963',2438243,0,15,'c38a114d4b345103a950e467345','E0068','2012-07-31 08:09:44.932402','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0YjM0NTEwM2E5NTBlNDY3MzQ1JwpWRTAwNjgKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTgKSTE5NjMKSTAwCnRWQVVHIDE5NjMKcDMKSTI0MzgyNDMKSTAKdFYK
UycnCihsKGwobChsSTAKSTAwCnRwNAou
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,16,'c38a114d16162738e4eabec661e','E0035','2012-07-31 08:09:44.940328','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxNjE2MjczOGU0ZWFiZWM2NjFlJwpWRTAwMzUKcDEKKEkzNwpWT2NjdXBhdGlv
bgpwMgp0TlZBY3RvcgpwMwpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',29,'Actor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,17,'c38a114d6c14fd1e0091d36c019','E0116','2012-07-31 08:09:44.948219','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2YzE0ZmQxZTAwOTFkMzZjMDE5JwpWRTAxMTYKcDEKKEkyNgpWRWR1Y2F0aW9u
CnAyCnROVkJyb3duIFVuaXYKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',18,'Brown Univ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,18,'c38a114d58b156f1dea27842097','E0093','2012-07-31 08:09:44.956162','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1OGIxNTZmMWRlYTI3ODQyMDk3JwpWRTAwOTMKcDEKKEkwClYKdE5WRWFzdCBI
YW1wdG9uLCBOWQpwMgpTJycKKGwobChsKGxJMApJMDAKdHAzCi4=
',47,'East Hampton, NY',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1898,0,0,0,0,0,'1898',2414291,0,19,'c38a114d7041c0ad4953e8014f1','E0119','2012-07-31 08:09:44.964046','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3MDQxYzBhZDQ5NTNlODAxNGYxJwpWRTAxMTkKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE4OTgKSTAwCnRWMTg5OApwMwpJMjQxNDI5MQpJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,5,1929,0,0,0,0,0,'MAY 1929',2425733,0,20,'c38a114d4d447b9accc2e56082c','E0070','2012-07-31 08:09:44.972062','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZDQ0N2I5YWNjYzJlNTYwODJjJwpWRTAwNzAKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTAKSTUKSTE5MjkKSTAwCnRWTUFZIDE5MjkKcDMKSTI0MjU3MzMKSTAKdFYK
UycnCihsKGwobChsSTAKSTAwCnRwNAou
',5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,21,'c38a114c1781472acfa27241fda','E0006','2012-07-31 08:09:44.979961','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxNzgxNDcyYWNmYTI3MjQxZmRhJwpWRTAwMDYKcDEKKEkwClYKdE5WQnJvbnh2
aWxsZSwgTUEKcDIKUycnCihsKGwobChsSTAKSTAwCnRwMwou
',47,'Bronxville, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,1,1995,0,0,0,0,0,'22 JAN 1995',2449740,0,22,'c38a114cfb24e4c97b70e5688c7','E0012','2012-07-31 08:09:44.988787','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmYjI0ZTRjOTdiNzBlNTY4OGM3JwpWRTAwMTIKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTIyCkkxCkkxOTk1CkkwMAp0VjIyIEpBTiAxOTk1CnAzCkkyNDQ5NzQwCkkw
CnRWClZjMzhhMTE0Y2ZiYTRiNTkwYWU4NGEyZjZjMTAKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',5,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,11,1957,0,0,0,0,0,'27 NOV 1957',2436170,0,23,'c38a114d686595a58846c829716','E0110','2012-07-31 08:09:44.997574','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2ODY1OTVhNTg4NDZjODI5NzE2JwpWRTAxMTAKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTI3CkkxMQpJMTk1NwpJMDAKdFYyNyBOT1YgMTk1NwpwMwpJMjQzNjE3MApJ
MAp0VgpWYzM4YTExNGQzNmMxZTgwYzBjMmU4YTFkOGUwCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',4,'',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,11,1915,0,0,0,0,0,'9 NOV 1915',2420811,0,24,'c38a114d0c013e4be2199f734b9','E0030','2012-07-31 08:09:45.006323','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwYzAxM2U0YmUyMTk5ZjczNGI5JwpWRTAwMzAKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTkKSTExCkkxOTE1CkkwMAp0VjkgTk9WIDE5MTUKcDMKSTI0MjA4MTEKSTAK
dFYKVmMzOGExMTRkMGNhMWZiYjliNmFmZWE5ZDczZApwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',4,'',15);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,9,1849,0,0,0,0,0,'28 SEP 1849',2396664,0,25,'c38a114db6e1c576a25a9c9cf07','E0137','2012-07-31 08:09:45.015323','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRiNmUxYzU3NmEyNWE5YzljZjA3JwpWRTAxMzcKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMjgKSTkKSTE4NDkKSTAwCnRWMjggU0VQIDE4NDkKcDMKSTIzOTY2NjQK
STAKdFYKVmMzOGExMTRkYjc4NDBjMjk2NThlZmFjMzYzNwpwNAoobChsKGwobEkwCkkwMAp0cDUK
Lg==
',37,'',28);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1958,0,0,0,0,0,'1958',2436205,0,26,'c38a114d32a6946aea3b77ced57','E0054','2012-07-31 08:09:45.023273','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzMmE2OTQ2YWVhM2I3N2NlZDU3JwpWRTAwNTQKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5NTgKSTAwCnRWMTk1OApwMwpJMjQzNjIwNQpJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,27,'c38a114d69c4368e20d0844e2be','E0112','2012-07-31 08:09:45.031179','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2OWM0MzY4ZTIwZDA4NDRlMmJlJwpWRTAxMTIKcDEKKEkyNgpWRWR1Y2F0aW9u
CnAyCnROVkJyZWFybHkgU2Nob29sCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',18,'Brearly School',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,11,1960,0,0,0,0,0,'25 NOV 1960',2437264,0,28,'c38a114d6b65b15feba43b943b6','E0115','2012-07-31 08:09:45.039866','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2YjY1YjE1ZmViYTQzYjk0M2I2JwpWRTAxMTUKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTI1CkkxMQpJMTk2MApJMDAKdFYyNSBOT1YgMTk2MApwMwpJMjQzNzI2NApJ
MAp0VgpWYzM4YTExNGQxYTQxZTFiMmFlYjZiNzhmMmI0CnA0CihsKGwobChsSTAKSTAwCnRwNQou
',4,'',27);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,5,1944,0,0,0,0,0,'6 MAY 1944',2431217,0,29,'c38a114d996378968592c9786a2','E0130','2012-07-31 08:09:45.048680','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ5OTYzNzg5Njg1OTJjOTc4NmEyJwpWRTAxMzAKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJNgpJNQpJMTk0NApJMDAKdFY2IE1BWSAxOTQ0CnAzCkkyNDMxMjE3Ckkw
CnRWClZjMzhhMTE0ZDk5ZTE5OTY1ZDU4ZjhlZjU2ZWQKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',37,'',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,30,'c38a114d0127f814f89b2d1587c','E0021','2012-07-31 08:09:45.056657','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMTI3ZjgxNGY4OWIyZDE1ODdjJwpWRTAwMjEKcDEKKEkwClYKdE5WSGUgc3Vm
ZmVyZWQgMiBjYXNlcyBvZiBKYXVuZGljZSBkdXJpbmcgaGlzIGJlZ2lubmluZyB5ZWFycyBhCnAy
ClMnJwoobChsKGwobEkwCkkwMAp0cDMKLg==
',47,'He suffered 2 cases of Jaundice during his beginning years a',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,1,1858,0,0,0,0,0,'14 JAN 1858',2399694,0,31,'c38a114d4c93d204d6e54b46aa3','E0069','2012-07-31 08:09:45.065418','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0YzkzZDIwNGQ2ZTU0YjQ2YWEzJwpWRTAwNjkKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTE0CkkxCkkxODU4CkkwMAp0VjE0IEpBTiAxODU4CnAzCkkyMzk5Njk0Ckkw
CnRWClZjMzhhMTE0YzA0YjQ5NDU1OGZjNTFmMTlhZQpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,9,1872,0,0,0,0,0,'22 SEP 1872',2405059,0,32,'c38a114dc1960560fb80cfbc430','E0141','2012-07-31 08:09:45.074508','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRjMTk2MDU2MGZiODBjZmJjNDMwJwpWRTAxNDEKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMjIKSTkKSTE4NzIKSTAwCnRWMjIgU0VQIDE4NzIKcDMKSTI0MDUwNTkK
STAKdFYKVmMzOGExMTRjMDRiNDk0NTU4ZmM1MWYxOWFlCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',37,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,33,'c38a114d66432d502bbd84c96d','E0109','2012-07-31 08:09:45.082423','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NjQzMmQ1MDJiYmQ4NGM5NmQnClZFMDEwOQpwMQooSTQxClZSZWxpZ2lvbgpw
Mgp0TlZSb21hbiBDYXRob2xpYwpwMwpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,12,1957,0,0,0,0,0,'13 DEC 1957',2436186,0,34,'c38a114d69271f22b1e39ccd398','E0111','2012-07-31 08:09:45.091299','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2OTI3MWYyMmIxZTM5Y2NkMzk4JwpWRTAxMTEKcDEKKEkyMgpWQ2hyaXN0ZW5p
bmcKcDIKdChJMApJMApJMAooSTEzCkkxMgpJMTk1NwpJMDAKdFYxMyBERUMgMTk1NwpwMwpJMjQz
NjE4NgpJMAp0VgpWYzM4YTExNGQ2OWExZjczYTY5NjRlOGYxMDY3CnA0CihsKGwobChsSTAKSTAw
CnRwNQou
',14,'',5);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,5,1948,0,0,0,0,0,'13 MAY 1948',2432685,0,35,'c38a114d08c2d5cfd5cd3106a99','E0028','2012-07-31 08:09:45.100077','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwOGMyZDVjZmQ1Y2QzMTA2YTk5JwpWRTAwMjgKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTEzCkk1CkkxOTQ4CkkwMAp0VjEzIE1BWSAxOTQ4CnAzCkkyNDMyNjg1Ckkw
CnRWClZjMzhhMTE0ZDA5NGM4ZGRhNDIxZDVkMGM3YgpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',5,'',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,10,1914,0,0,0,0,0,'7 OCT 1914',2420413,0,36,'c38a114d97f2af61894e825fa03','E0129','2012-07-31 08:09:45.108809','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ5N2YyYWY2MTg5NGU4MjVmYTAzJwpWRTAxMjkKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJNwpJMTAKSTE5MTQKSTAwCnRWNyBPQ1QgMTkxNApwMwpJMjQyMDQxMwpJ
MAp0VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',37,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1963,0,0,0,0,0,'22 NOV 1963',2438356,0,37,'c38a114d5f5199a0f4703eba87b','E0097','2012-07-31 08:09:45.117734','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1ZjUxOTlhMGY0NzAzZWJhODdiJwpWRTAwOTcKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTIyCkkxMQpJMTk2MwpJMDAKdFYyMiBOT1YgMTk2MwpwMwpJMjQzODM1NgpJ
MAp0VgpWYzM4YTExNGQ1ZmRmNDFiMGYyOTE0NmIwMgpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',5,'',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1823,0,0,0,0,0,'1823',2386897,0,38,'c38a114d51146f2af4896856e35','E0077','2012-07-31 08:09:45.126709','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MTE0NmYyYWY0ODk2ODU2ZTM1JwpWRTAwNzcKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE4MjMKSTAwCnRWMTgyMwpwMwpJMjM4Njg5NwpJMAp0VgpWYzM4
YTExNGQ1MWE3YWRlZWYxY2M1NDFlNzQ0CnA0CihsKGwobChsSTAKSTAwCnRwNQou
',4,'',24);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1883,0,0,0,0,0,'1883',2408812,0,39,'c38a114dc041a32a0e4ddd06624','E0140','2012-07-31 08:09:45.135861','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRjMDQxYTMyYTBlNGRkZDA2NjI0JwpWRTAxNDAKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMApJMApJMTg4MwpJMDAKdFYxODgzCnAzCkkyNDA4ODEyCkkwCnRWClZj
MzhhMTE0YzA0YjQ5NDU1OGZjNTFmMTlhZQpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',37,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,40,'c38a114d52b4d62f70d7c9e2172','E0080','2012-07-31 08:09:45.143842','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MmI0ZDYyZjcwZDdjOWUyMTcyJwpWRTAwODAKcDEKKEkwClYKdE5WSGUgZGll
ZCBvZiBhbiBvdXRicmVhayBvZiBDaG9sZXJhLgpwMgpTJycKKGwobChsKGxJMApJMDAKdHAzCi4=
',47,'He died of an outbreak of Cholera.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,11,1925,0,0,0,0,0,'20 NOV 1925',2424475,0,41,'c38a114d25756ebc19fe606ecfe','E0041','2012-07-31 08:09:45.152573','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyNTc1NmViYzE5ZmU2MDZlY2ZlJwpWRTAwNDEKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTIwCkkxMQpJMTkyNQpJMDAKdFYyMCBOT1YgMTkyNQpwMwpJMjQyNDQ3NQpJ
MAp0VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,42,'c38a114c18e50699dbc53f86e2b','E0010','2012-07-31 08:09:45.160528','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxOGU1MDY5OWRiYzUzZjg2ZTJiJwpWRTAwMTAKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,43,'c38a114d55750d20abc91247e17','E0086','2012-07-31 08:09:45.169364','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NTc1MGQyMGFiYzkxMjQ3ZTE3JwpWRTAwODYKcDEKKEkxOQpWQnVyaWFsCnAy
CnROVgpWYzM4YTExNGQ1NWYyMjgxZTQwYjAxNWI2ZDNkCnAzCihsKGwobChsSTAKSTAwCnRwNAou
',11,'',4);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,44,'c38a114d49a2a8ff225fe880ea4','E0066','2012-07-31 08:09:45.177307','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0OWEyYThmZjIyNWZlODgwZWE0JwpWRTAwNjYKcDEKKEkzNQpWTm9iaWxpdHkg
VGl0bGUKcDIKdE5WSnIuCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,9,1855,0,0,0,0,0,'24 SEP 1855',2398851,0,45,'c38a114d78376847c13470ad2ac','E0123','2012-07-31 08:09:45.185149','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ3ODM3Njg0N2MxMzQ3MGFkMmFjJwpWRTAxMjMKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTI0Ckk5CkkxODU1CkkwMAp0VjI0IFNFUCAxODU1CnAzCkkyMzk4ODUxCkkw
CnRWClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,2,1928,0,0,0,0,0,'FEB 1928',2425278,0,46,'c38a114d3e178bf0f385b26b541','E0059','2012-07-31 08:09:45.193996','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzZTE3OGJmMGYzODViMjZiNTQxJwpWRTAwNTkKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTIKSTE5MjgKSTAwCnRWRkVCIDE5MjgKcDMKSTI0MjUyNzgKSTAKdFYK
VmMzOGExMTRjMDRiNDk0NTU4ZmM1MWYxOWFlCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,2,1932,0,0,0,0,0,'22 FEB 1932',2426760,0,47,'c38a114d44a6aa06b56427ef9c','E0062','2012-07-31 08:09:45.202731','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0NGE2YWEwNmI1NjQyN2VmOWMnClZFMDA2MgpwMQooSTEyClZCaXJ0aApwMgp0
KEkwCkkwCkkwCihJMjIKSTIKSTE5MzIKSTAwCnRWMjIgRkVCIDE5MzIKcDMKSTI0MjY3NjAKSTAK
dFYKVmMzOGExMTRkNDUyMzg4MTJhY2QwMjhlY2FlMQpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',4,'',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1955,0,0,0,0,0,'1955',2435109,0,48,'c38a114d2fe246e89cdfa6bc06f','E0052','2012-07-31 08:09:45.210638','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyZmUyNDZlODljZGZhNmJjMDZmJwpWRTAwNTIKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5NTUKSTAwCnRWMTk1NQpwMwpJMjQzNTEwOQpJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,12,1888,0,0,0,0,0,'20 DEC 1888',2410992,0,49,'c38a114d54c5eb3d0210f07e0b4','E0085','2012-07-31 08:09:45.219590','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NGM1ZWIzZDAyMTBmMDdlMGI0JwpWRTAwODUKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTIwCkkxMgpJMTg4OApJMDAKdFYyMCBERUMgMTg4OApwMwpJMjQxMDk5MgpJ
MAp0VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',5,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,12,1968,0,0,0,0,0,'12 DEC 1968',2440203,0,50,'c38a114d3b4b4a67ee778ebea4','E0058','2012-07-31 08:09:45.228325','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzYjRiNGE2N2VlNzc4ZWJlYTQnClZFMDA1OApwMQooSTEyClZCaXJ0aApwMgp0
KEkwCkkwCkkwCihJMTIKSTEyCkkxOTY4CkkwMAp0VjEyIERFQyAxOTY4CnAzCkkyNDQwMjAzCkkw
CnRWClZjMzhhMTE0ZDFhNDFlMWIyYWViNmI3OGYyYjQKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',27);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1920,0,0,0,0,0,'1920',2422325,0,51,'c38a114d080e9f5a6d87d4acc5','E0027','2012-07-31 08:09:45.237063','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwODBlOWY1YTZkODdkNGFjYzUnClZFMDAyNwpwMQooSTEyClZCaXJ0aApwMgp0
KEkwCkkwCkkwCihJMApJMApJMTkyMApJMDAKdFYxOTIwCnAzCkkyNDIyMzI1CkkwCnRWClZjMzhh
MTE0YzA0YjQ5NDU1OGZjNTFmMTlhZQpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,9,1944,0,0,0,0,0,'10 SEP 1944',2431344,0,52,'c38a114d069444fb475e9d9c89b','E0026','2012-07-31 08:09:45.245836','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwNjk0NDRmYjQ3NWU5ZDljODliJwpWRTAwMjYKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTEwCkk5CkkxOTQ0CkkwMAp0VjEwIFNFUCAxOTQ0CnAzCkkyNDMxMzQ0Ckkw
CnRWClZjMzhhMTE0ZDA3MzYwMmI3MjdjYzQwODhjODkKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',5,'',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,53,'c38a114c12a2471b0173c831376','E0004','2012-07-31 08:09:45.253735','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxMmEyNDcxYjAxNzNjODMxMzc2JwpWRTAwMDQKcDEKKEkyNgpWRWR1Y2F0aW9u
CnAyCnROVkhhcnZhcmQgR3JhZHVhdGUKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',18,'Harvard Graduate',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,6,1968,0,0,0,0,0,'6 JUN 1968',2440014,0,54,'c38a114d26222b8691149e7d164','E0042','2012-07-31 08:09:45.262544','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyNjIyMmI4NjkxMTQ5ZTdkMTY0JwpWRTAwNDIKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTYKSTYKSTE5NjgKSTAwCnRWNiBKVU4gMTk2OApwMwpJMjQ0MDAxNApJMAp0
VgpWYzM4YTExNGQyNjk0YjJlNGYzMWY5MjdjZGZjCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',5,'',9);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,11,1958,0,0,0,0,0,'29 NOV 1958',2436537,0,55,'c38a114daff42629020d44cecb3','E0135','2012-07-31 08:09:45.270450','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRhZmY0MjYyOTAyMGQ0NGNlY2IzJwpWRTAxMzUKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMjkKSTExCkkxOTU4CkkwMAp0VjI5IE5PViAxOTU4CnAzCkkyNDM2NTM3
CkkwCnRWClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1858,0,0,0,0,0,'22 NOV 1858',2400006,0,56,'c38a114d51b48081d4b2ca8ec35','E0078','2012-07-31 08:09:45.279147','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MWI0ODA4MWQ0YjJjYThlYzM1JwpWRTAwNzgKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTIyCkkxMQpJMTg1OApJMDAKdFYyMiBOT1YgMTg1OApwMwpJMjQwMDAwNgpJ
MAp0VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',5,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,9,1923,0,0,0,0,0,'7 SEP 1923',2423670,0,57,'c38a114d1d84903a53239eb2e31','E0039','2012-07-31 08:09:45.287100','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxZDg0OTAzYTUzMjM5ZWIyZTMxJwpWRTAwMzkKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTcKSTkKSTE5MjMKSTAwCnRWNyBTRVAgMTkyMwpwMwpJMjQyMzY3MApJMAp0
VgpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1928,0,0,0,0,0,'1928',2425247,0,58,'c38a114d299499d70534d281f54','E0046','2012-07-31 08:09:45.295104','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyOTk0OTlkNzA1MzRkMjgxZjU0JwpWRTAwNDYKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5MjgKSTAwCnRWMTkyOApwMwpJMjQyNTI0NwpJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,59,'c38a114cfcb5799af35c284a811','E0015','2012-07-31 08:09:45.302965','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmY2I1Nzk5YWYzNWMyODRhODExJwpWRTAwMTUKcDEKKEkwClYKdE5WRGllZCBv
ZiBjb21wbGljYXRpb25zIGR1ZSB0byBwbmV1bW9uaWEuIApwMgpTJycKKGwobChsKGxJMApJMDAK
dHAzCi4=
',47,'Died of complications due to pneumonia. ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,7,1855,0,0,0,0,0,'18 JUL 1855',2398783,0,60,'c38a114d79b60919bb23facfa46','E0124','2012-07-31 08:09:45.311699','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3OWI2MDkxOWJiMjNmYWNmYTQ2JwpWRTAxMjQKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTE4Ckk3CkkxODU1CkkwMAp0VjE4IEpVTCAxODU1CnAzCkkyMzk4NzgzCkkw
CnRWClZjMzhhMTE0YzA0YjQ5NDU1OGZjNTFmMTlhZQpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,61,'c38a114d60a6016b37b307e7109','E0099','2012-07-31 08:09:45.319588','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MGE2MDE2YjM3YjMwN2U3MTA5JwpWRTAwOTkKcDEKKEkzNwpWT2NjdXBhdGlv
bgpwMgp0TlZTZW5hdG9yCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',29,'Senator',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,9,1918,0,0,0,0,0,'SEP 1918',2421838,0,62,'c38a114d036260f56bd9e8618a','E0023','2012-07-31 08:09:45.328442','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwMzYyNjBmNTZiZDllODYxOGEnClZFMDAyMwpwMQooSTEyClZCaXJ0aApwMgp0
KEkwCkkwCkkwCihJMApJOQpJMTkxOApJMDAKdFZTRVAgMTkxOApwMwpJMjQyMTgzOApJMAp0VgpW
YzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,63,'c38a114c1275a876a45e354ea04','E0003','2012-07-31 08:09:45.336505','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxMjc1YTg3NmE0NWUzNTRlYTA0JwpWRTAwMDMKcDEKKEkzNwpWT2NjdXBhdGlv
bgpwMgp0TlZCYW5rIFByZXNpZGVudCwgQW1iYXNzYWRvcgpwMwpTJycKKGwobChsKGxJMApJMDAK
dHA0Ci4=
',29,'Bank President, Ambassador',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,8,1963,0,0,0,0,0,'7 AUG 1963',2438249,0,64,'c38a114d6d87c2626c5842118dc','E0117','2012-07-31 08:09:45.345394','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2ZDg3YzI2MjZjNTg0MjExOGRjJwpWRTAxMTcKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTcKSTgKSTE5NjMKSTAwCnRWNyBBVUcgMTk2MwpwMwpJMjQzODI0OQpJMAp0
VgpWYzM4YTExNGQ2ZTA2MzcxNWVjYjQ3YmQ3NWMKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',16);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,65,'c38a114d6b579ea55f66c0d2cf8','E0114','2012-07-31 08:09:45.354546','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2YjU3OWVhNTVmNjZjMGQyY2Y4JwpWRTAxMTQKcDEKKEkzNQpWTm9iaWxpdHkg
VGl0bGUKcDIKdE5WSnIuCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,66,'c38a114d4d6931b50bb17b2d02','E0071','2012-07-31 08:09:45.362644','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZDY5MzFiNTBiYjE3YjJkMDInClZFMDA3MQpwMQooSTM3ClZPY2N1cGF0aW9u
CnAyCnROVkRvY2toYW5kLCBTYWxvb25rZWVwZXIsIFNlbmF0b3IsIEJhbmsgUHJlc2lkZW50CnAz
ClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',29,'Dockhand, Saloonkeeper, Senator, Bank President',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1956,0,0,0,0,0,'1956',2435474,0,67,'c38a114dad213d3bd8807efa162','E0134','2012-07-31 08:09:45.370812','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRhZDIxM2QzYmQ4ODA3ZWZhMTYyJwpWRTAxMzQKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMApJMApJMTk1NgpJMDAKdFYxOTU2CnAzCkkyNDM1NDc0CkkwCnRWClMn
JwoobChsKGwobEkwCkkwMAp0cDQKLg==
',37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,19,5,1994,0,0,0,0,0,'19 MAY 1994',2449492,0,68,'c38a114d6432bba38666bb22cc6','E0104','2012-07-31 08:09:45.379724','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NDMyYmJhMzg2NjZiYjIyY2M2JwpWRTAxMDQKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTE5Ckk1CkkxOTk0CkkwMAp0VjE5IE1BWSAxOTk0CnAzCkkyNDQ5NDkyCkkw
CnRWClZjMzhhMTE0ZDY0YjYyNWY4YjA4Yjk3OTBkMGEKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',5,'',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,69,'c38a114d45859c04c7fb31257a7','E0063','2012-07-31 08:09:45.387735','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0NTg1OWMwNGM3ZmIzMTI1N2E3JwpWRTAwNjMKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,70,'c38a114d01124785d19d9083300','E0020','2012-07-31 08:09:45.395675','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMTEyNDc4NWQxOWQ5MDgzMzAwJwpWRTAwMjAKcDEKKEkyNgpWRWR1Y2F0aW9u
CnAyCnROVkhhcnZhcmQgVW5pdmVyc2l0eSwgSGFydmFyZCBMYXcgU2Nob29sCnAzClMnJwoobChs
KGwobEkwCkkwMAp0cDQKLg==
',18,'Harvard University, Harvard Law School',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,7,1890,0,0,0,0,0,'22 JUL 1890',2411571,0,71,'c38a114cfa77898594d482cfc22','E0011','2012-07-31 08:09:45.404409','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmYTc3ODk4NTk0ZDQ4MmNmYzIyJwpWRTAwMTEKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTIyCkk3CkkxODkwCkkwMAp0VjIyIEpVTCAxODkwCnAzCkkyNDExNTcxCkkw
CnRWClZjMzhhMTE0Y2ZiMDU0YjI2ZWM3MjQ5MWU0MTcKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',26);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1952,0,0,0,0,0,'1952',2434013,0,72,'c38a114d2ba14b8a15ae9f2ce04','E0048','2012-07-31 08:09:45.412295','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyYmExNGI4YTE1YWU5ZjJjZTA0JwpWRTAwNDgKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5NTIKSTAwCnRWMTk1MgpwMwpJMjQzNDAxMwpJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1882,0,0,0,0,0,'1882',2408447,0,73,'c38a114dc2f18929a4d2db180f0','E0142','2012-07-31 08:09:45.422178','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRjMmYxODkyOWE0ZDJkYjE4MGYwJwpWRTAxNDIKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMApJMApJMTg4MgpJMDAKdFYxODgyCnAzCkkyNDA4NDQ3CkkwCnRWClZj
MzhhMTE0YzA0YjQ5NDU1OGZjNTFmMTlhZQpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',37,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1915,0,0,0,0,0,'JUL 1915',2420680,0,74,'c38a114cffa33c8ffb92c59f40e','E0018','2012-07-31 08:09:45.431218','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmZmEzM2M4ZmZiOTJjNTlmNDBlJwpWRTAwMTgKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTcKSTE5MTUKSTAwCnRWSlVMIDE5MTUKcDMKSTI0MjA2ODAKSTAKdFYK
VmMzOGExMTRjMDRiNDk0NTU4ZmM1MWYxOWFlCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,6,1963,0,0,0,0,0,'4 JUN 1963',2438185,0,75,'c38a114d34270fa530e91d0ea60','E0055','2012-07-31 08:09:45.440047','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzNDI3MGZhNTMwZTkxZDBlYTYwJwpWRTAwNTUKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTQKSTYKSTE5NjMKSTAwCnRWNCBKVU4gMTk2MwpwMwpJMjQzODE4NQpJMAp0
VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,76,'c38a114d56047147205e6c97361','E0087','2012-07-31 08:09:45.448014','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NjA0NzE0NzIwNWU2Yzk3MzYxJwpWRTAwODcKcDEKKEkwClYKdE5WSGVyIGRl
YXRoIHdhcyBjYXVzZWQgYnkgYSBjZXJlYnJhbCBoZW1vcnJoYWdlLgpwMgpTJycKKGwobChsKGxJ
MApJMDAKdHAzCi4=
',47,'Her death was caused by a cerebral hemorrhage.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,77,'c38a114d4e3293547d4d5fe1703','E0072','2012-07-31 08:09:45.455949','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZTMyOTM1NDdkNGQ1ZmUxNzAzJwpWRTAwNzIKcDEKKEkwClYKdE5WTWVyaWRp
YW4gU3QuLCBFYXN0IEJvc3RvbiwgTUEKcDIKUycnCihsKGwobChsSTAKSTAwCnRwMwou
',47,'Meridian St., East Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,78,'c38a114d01b3d08c55aedc41954','E0022','2012-07-31 08:09:45.463904','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMWIzZDA4YzU1YWVkYzQxOTU0JwpWRTAwMjIKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1892,0,0,0,0,0,'1892',2412099,0,79,'c38a114d7ec675d34cee53d3fc5','E0128','2012-07-31 08:09:45.472696','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3ZWM2NzVkMzRjZWU1M2QzZmM1JwpWRTAxMjgKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE4OTIKSTAwCnRWMTg5MgpwMwpJMjQxMjA5OQpJMAp0VgpWYzM4
YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,1,1965,0,0,0,0,0,'9 JAN 1965',2438770,0,80,'c38a114d3644f64453538c63cb0','E0056','2012-07-31 08:09:45.481481','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzNjQ0ZjY0NDUzNTM4YzYzY2IwJwpWRTAwNTYKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTkKSTEKSTE5NjUKSTAwCnRWOSBKQU4gMTk2NQpwMwpJMjQzODc3MApJMAp0
VgpWYzM4YTExNGQzNmMxZTgwYzBjMmU4YTFkOGUwCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',4,'',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,12,1852,0,0,0,0,0,'4 DEC 1852',2397827,0,81,'c38a114d75ea5e1add51ed9801','E0121','2012-07-31 08:09:45.489463','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3NWVhNWUxYWRkNTFlZDk4MDEnClZFMDEyMQpwMQooSTEyClZCaXJ0aApwMgp0
KEkwCkkwCkkwCihJNApJMTIKSTE4NTIKSTAwCnRWNCBERUMgMTg1MgpwMwpJMjM5NzgyNwpJMAp0
VgpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,82,'c38a114d6635ba0adf6d91c8a9c','E0108','2012-07-31 08:09:45.497383','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NjM1YmEwYWRmNmQ5MWM4YTljJwpWRTAxMDgKcDEKKEkwClYKdE5WTWFydGhh
J3MgVmluZXlhcmQgCnAyClMnJwoobChsKGwobEkwCkkwMAp0cDMKLg==
',47,'Martha''s Vineyard ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,83,'c38a114d7c218263a8b7be343ce','E0125','2012-07-31 08:09:45.505350','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3YzIxODI2M2E4YjdiZTM0M2NlJwpWRTAxMjUKcDEKKEkzNwpWT2NjdXBhdGlv
bgpwMgp0TlZKYW5pdG9yCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',29,'Janitor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,84,'c38a114d5036f2c5f6e552b443f','E0076','2012-07-31 08:09:45.513311','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MDM2ZjJjNWY2ZTU1MmI0NDNmJwpWRTAwNzYKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,85,'c38a114d61b39e0d9b1e32c1987','E0102','2012-07-31 08:09:45.521289','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MWIzOWUwZDliMWUzMmMxOTg3JwpWRTAxMDIKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,9,1888,0,0,0,0,0,'6 SEP 1888',2410887,0,86,'c38a114c0017f2fa7fcbd243990','E0000','2012-07-31 08:09:45.530216','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMwMDE3ZjJmYTdmY2JkMjQzOTkwJwpWRTAwMDAKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTYKSTkKSTE4ODgKSTAwCnRWNiBTRVAgMTg4OApwMwpJMjQxMDg4NwpJMAp0
VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,87,'c38a114d4e6703df36a92c6113a','E0074','2012-07-31 08:09:45.538155','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZTY3MDNkZjM2YTkyYzYxMTNhJwpWRTAwNzQKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,17,6,1950,0,0,0,0,0,'17 JUN 1950',2433450,0,88,'c38a114da9d628ae85c2bb3dcaa','E0133','2012-07-31 08:09:45.546943','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRhOWQ2MjhhZTg1YzJiYjNkY2FhJwpWRTAxMzMKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMTcKSTYKSTE5NTAKSTAwCnRWMTcgSlVOIDE5NTAKcDMKSTI0MzM0NTAK
STAKdFYKVmMzOGExMTRkYWE2MWE2NmY2YjQ0YzQ2ZDgyNwpwNAoobChsKGwobEkwCkkwMAp0cDUK
Lg==
',37,'',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,89,'c38a114d5303124ba33c13bd4a7','E0081','2012-07-31 08:09:45.554845','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MzAzMTI0YmEzM2MxM2JkNGE3JwpWRTAwODEKcDEKKEkwClYKdE5WRHVnYW5z
dG93biwgSXJlbGFuZApwMgpTJycKKGwobChsKGxJMApJMDAKdHAzCi4=
',47,'Duganstown, Ireland',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,90,'c38a114c17d1a5b6a9c78954b46','E0007','2012-07-31 08:09:45.562759','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxN2QxYTViNmE5Yzc4OTU0YjQ2JwpWRTAwMDcKcDEKKEkwClYKdE5WSHlhbm5p
cywgTUEKcDIKUycnCihsKGwobChsSTAKSTAwCnRwMwou
',47,'Hyannis, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,11,1963,0,0,0,0,0,'25 NOV 1963',2438359,0,91,'c38a114d5ff4c777122d91d1e88','E0098','2012-07-31 08:09:45.571660','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1ZmY0Yzc3NzEyMmQ5MWQxZTg4JwpWRTAwOTgKcDEKKEkxOQpWQnVyaWFsCnAy
CnQoSTAKSTAKSTAKKEkyNQpJMTEKSTE5NjMKSTAwCnRWMjUgTk9WIDE5NjMKcDMKSTI0MzgzNTkK
STAKdFYKVmMzOGExMTRkMjc1YTE0MWM0YzVkZWJjYmNjCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',11,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,11,1969,0,0,0,0,0,'18 NOV 1969',2440544,0,92,'c38a114c053d64a11eefa11f85','E0001','2012-07-31 08:09:45.580393','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMwNTNkNjRhMTFlZWZhMTFmODUnClZFMDAwMQpwMQooSTEzClZEZWF0aApwMgp0
KEkwCkkwCkkwCihJMTgKSTExCkkxOTY5CkkwMAp0VjE4IE5PViAxOTY5CnAzCkkyNDQwNTQ0Ckkw
CnRWClZjMzhhMTE0YzEwNTJiYTViNjhjN2JhNjBiZmQKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',5,'',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1821,0,0,0,0,0,'1821',2386167,0,93,'c38a114d5495fb73b8c435cec78','E0084','2012-07-31 08:09:45.588315','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NDk1ZmI3M2I4YzQzNWNlYzc4JwpWRTAwODQKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE4MjEKSTAwCnRWMTgyMQpwMwpJMjM4NjE2NwpJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1940,0,0,0,0,0,'JUL 1940',2429812,0,94,'c38a114db9919a8a41f67c7ea9e','E0138','2012-07-31 08:09:45.596319','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRiOTkxOWE4YTQxZjY3YzdlYTllJwpWRTAxMzgKcDEKKEk3ClZEaXZvcmNlCnAy
CnQoSTAKSTAKSTAKKEkwCkk3CkkxOTQwCkkwMAp0VkpVTCAxOTQwCnAzCkkyNDI5ODEyCkkwCnRW
ClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',43,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,95,'c38a114d14a1b57a5528f250d2f','E0033','2012-07-31 08:09:45.604206','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxNGExYjU3YTU1MjhmMjUwZDJmJwpWRTAwMzMKcDEKKEkzNQpWTm9iaWxpdHkg
VGl0bGUKcDIKdE5WSUlJCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',27,'III',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,96,'c38a114d3eb5e345ee32e34d149','E0060','2012-07-31 08:09:45.612057','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzZWI1ZTM0NWVlMzJlMzRkMTQ5JwpWRTAwNjAKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,5,1924,0,0,0,0,0,'6 MAY 1924',2423912,0,97,'c38a114d1e67e0d37f1f38c2400','E0040','2012-07-31 08:09:45.620766','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxZTY3ZTBkMzdmMWYzOGMyNDAwJwpWRTAwNDAKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTYKSTUKSTE5MjQKSTAwCnRWNiBNQVkgMTkyNApwMwpJMjQyMzkxMgpJMAp0
VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,98,'c38a114c12c7abed7a1564e26c1','E0005','2012-07-31 08:09:45.628799','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxMmM3YWJlZDdhMTU2NGUyNmMxJwpWRTAwMDUKcDEKKEkwClYKdE5WSm9lIEtl
bm5lZHkgd2FzIGEgdmVyeSBoYXJkIHdvcmtlciwgd2hpY2ggb2Z0ZW4gZGV0ZXJpb3JhdGVkCnAy
ClMnJwoobChsKGwobEkwCkkwMAp0cDMKLg==
',47,'Joe Kennedy was a very hard worker, which often deteriorated',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,99,'c38a114d69d798e009c4ee1fc4d','E0113','2012-07-31 08:09:45.636676','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ2OWQ3OThlMDA5YzRlZTFmYzRkJwpWRTAxMTMKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,9,1960,0,0,0,0,0,'SEP 1960',2437179,0,100,'c38a114d4186965253c197d17eb','E0061','2012-07-31 08:09:45.645396','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0MTg2OTY1MjUzYzE5N2QxN2ViJwpWRTAwNjEKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTkKSTE5NjAKSTAwCnRWU0VQIDE5NjAKcDMKSTI0MzcxNzkKSTAKdFYK
VmMzOGExMTRjMDRiNDk0NTU4ZmM1MWYxOWFlCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,8,6,1968,0,0,0,0,0,'8 JUN 1968',2440016,0,101,'c38a114d26c3a0190660a2ad10a','E0043','2012-07-31 08:09:45.655383','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyNmMzYTAxOTA2NjBhMmFkMTBhJwpWRTAwNDMKcDEKKEkxOQpWQnVyaWFsCnAy
CnQoSTAKSTAKSTAKKEk4Ckk2CkkxOTY4CkkwMAp0VjggSlVOIDE5NjgKcDMKSTI0NDAwMTYKSTAK
dFYKVmMzOGExMTRkMjc1YTE0MWM0YzVkZWJjYmNjCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',11,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,8,1851,0,0,0,0,0,'9 AUG 1851',2397344,0,102,'c38a114d73b11054c3f1b996dbe','E0120','2012-07-31 08:09:45.664170','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ3M2IxMTA1NGMzZjFiOTk2ZGJlJwpWRTAxMjAKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTkKSTgKSTE4NTEKSTAwCnRWOSBBVUcgMTg1MQpwMwpJMjM5NzM0NApJMAp0
VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,12,1917,0,0,0,0,0,'10 DEC 1917',2421573,0,103,'c38a114d06756ae254702017f37','E0025','2012-07-31 08:09:45.672146','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwNjc1NmFlMjU0NzAyMDE3ZjM3JwpWRTAwMjUKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTEwCkkxMgpJMTkxNwpJMDAKdFYxMCBERUMgMTkxNwpwMwpJMjQyMTU3MwpJ
MAp0VgpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,9,1953,0,0,0,0,0,'12 SEP 1953',2434633,0,104,'c38a114dbdc2512cdb7bd29b00','E0139','2012-07-31 08:09:45.680953','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRiZGMyNTEyY2RiN2JkMjliMDAnClZFMDEzOQpwMQooSTEKVk1hcnJpYWdlCnAy
CnQoSTAKSTAKSTAKKEkxMgpJOQpJMTk1MwpJMDAKdFYxMiBTRVAgMTk1MwpwMwpJMjQzNDYzMwpJ
MAp0VgpWYzM4YTExNGRiZTY1NmM5MjBkNTAxZDI1MTFjCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',37,'',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1957,0,0,0,0,0,'1957',2435840,0,105,'c38a114d3144a893b49e570e2cd','E0053','2012-07-31 08:09:45.689083','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzMTQ0YTg5M2I0OWU1NzBlMmNkJwpWRTAwNTMKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5NTcKSTAwCnRWMTk1NwpwMwpJMjQzNTg0MApJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,8,1963,0,0,0,0,0,'9 AUG 1963',2438251,0,106,'c38a114d6e2543b297468a11daf','E0118','2012-07-31 08:09:45.697948','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2ZTI1NDNiMjk3NDY4YTExZGFmJwpWRTAxMTgKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTkKSTgKSTE5NjMKSTAwCnRWOSBBVUcgMTk2MwpwMwpJMjQzODI1MQpJMAp0
VgpWYzM4YTExNGQ2ZWUyZGJmM2ZhMTRiMGNkYjU2CnA0CihsKGwobChsSTAKSTAwCnRwNQou
',5,'',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,6,1942,0,0,0,0,0,'JUN 1942',2430512,0,107,'c38a114dc4320289c02e2bf841d','E0143','2012-07-31 08:09:45.705859','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRjNDMyMDI4OWMwMmUyYmY4NDFkJwpWRTAxNDMKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMApJNgpJMTk0MgpJMDAKdFZKVU4gMTk0MgpwMwpJMjQzMDUxMgpJMAp0
VgpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,108,'c38a114d5863b170e4913525bf6','E0092','2012-07-31 08:09:45.713769','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1ODYzYjE3MGU0OTEzNTI1YmY2JwpWRTAwOTIKcDEKKEkwClYKdE5WRGllZCBv
ZiBjYW5jZXIuCnAyClMnJwoobChsKGwobEkwCkkwMAp0cDMKLg==
',47,'Died of cancer.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,109,'c38a114d04153e52b52e0baf675','E0024','2012-07-31 08:09:45.721655','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwNDE1M2U1MmI1MmUwYmFmNjc1JwpWRTAwMjQKcDEKKEkwClYKdE5WSW4gMTk0
MSBzaGUgaGFkIGEgZnJvbnRhbCBsb2JvdG9teS4KcDIKUycnCihsKGwobChsSTAKSTAwCnRwMwou
',47,'In 1941 she had a frontal lobotomy.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,110,'c38a114c1825e905418a6aa26fa','E0008','2012-07-31 08:09:45.729568','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxODI1ZTkwNTQxOGE2YWEyNmZhJwpWRTAwMDgKcDEKKEkwClYKdE5WUGFsbSBC
ZWFjaCwgRkwKcDIKUycnCihsKGwobChsSTAKSTAwCnRwMwou
',47,'Palm Beach, FL',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,111,'c38a114d5724e224776807479e7','E0089','2012-07-31 08:09:45.737635','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NzI0ZTIyNDc3NjgwNzQ3OWU3JwpWRTAwODkKcDEKKEkzNQpWTm9iaWxpdHkg
VGl0bGUKcDIKdE5WSUlJCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',27,'III',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,112,'c38a114cff83b8d58f7ffbff1b1','E0017','2012-07-31 08:09:45.745550','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmZjgzYjhkNThmN2ZmYmZmMWIxJwpWRTAwMTcKcDEKKEkzNQpWTm9iaWxpdHkg
VGl0bGUKcDIKdE5WSnIuCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,1,1854,0,0,0,0,0,'4 JAN 1854',2398223,0,113,'c38a114d7787641c8f7665d19a4','E0122','2012-07-31 08:09:45.754299','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ3Nzg3NjQxYzhmNzY2NWQxOWE0JwpWRTAxMjIKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTQKSTEKSTE4NTQKSTAwCnRWNCBKQU4gMTg1NApwMwpJMjM5ODIyMwpJMAp0
VgpWYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,8,1957,0,0,0,0,0,'AUG 1957',2436052,0,114,'c38a114d573298d8c3d860db04d','E0090','2012-07-31 08:09:45.763073','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NzMyOThkOGMzZDg2MGRiMDRkJwpWRTAwOTAKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTAKSTgKSTE5NTcKSTAwCnRWQVVHIDE5NTcKcDMKSTI0MzYwNTIKSTAKdFYK
VmMzOGExMTRkNTdjNjQ3NDQ5YmQwZDZkOTVlYgpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',5,'',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,115,'c38a114d4765e2cc7ba52f49943','E0064','2012-07-31 08:09:45.771139','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0NzY1ZTJjYzdiYTUyZjQ5OTQzJwpWRTAwNjQKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,116,'c38a114d56378149f32a7f7a5a3','E0088','2012-07-31 08:09:45.779085','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NjM3ODE0OWYzMmE3ZjdhNWEzJwpWRTAwODgKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,5,1917,0,0,0,0,0,'29 MAY 1917',2421378,0,117,'c38a114d5e957e85458cd1d7705','E0096','2012-07-31 08:09:45.787827','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1ZTk1N2U4NTQ1OGNkMWQ3NzA1JwpWRTAwOTYKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTI5Ckk1CkkxOTE3CkkwMAp0VjI5IE1BWSAxOTE3CnAzCkkyNDIxMzc4Ckkw
CnRWClZjMzhhMTE0ZDQ1MjM4ODEyYWNkMDI4ZWNhZTEKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,118,'c38a114c10a71a30190f11bfc02','E0002','2012-07-31 08:09:45.796731','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxMGE3MWEzMDE5MGYxMWJmYzAyJwpWRTAwMDIKcDEKKEkxOQpWQnVyaWFsCnAy
CnROVgpWYzM4YTExNGMxMjQxZDc3ZjAwYzgyMmU0YjU4CnAzCihsKGwobChsSTAKSTAwCnRwNAou
',11,'',6);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,119,'c38a114d5cc463c5a0321c1a60a','E0095','2012-07-31 08:09:45.804641','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ1Y2M0NjNjNWEwMzIxYzFhNjBhJwpWRTAwOTUKcDEKKEkzNwpWT2NjdXBhdGlv
bgpwMgp0TlZNYXlvcgpwMwpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',29,'Mayor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,120,'c38a114d5314a56535d33dc945e','E0082','2012-07-31 08:09:45.812512','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MzE0YTU2NTM1ZDMzZGM5NDVlJwpWRTAwODIKcDEKKEkwClYKdE5WTGl2ZXJw
b29sIFN0LiwgRWFzdCBCb3N0b24sIE1BCnAyClMnJwoobChsKGwobEkwCkkwMAp0cDMKLg==
',47,'Liverpool St., East Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,7,1951,0,0,0,0,0,'4 JUL 1951',2433832,0,121,'c38a114d2a6223474e12eb79e1c','E0047','2012-07-31 08:09:45.820404','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyYTYyMjM0NzRlMTJlYjc5ZTFjJwpWRTAwNDcKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTQKSTcKSTE5NTEKSTAwCnRWNCBKVUwgMTk1MQpwMwpJMjQzMzgzMgpJMAp0
VgpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,122,'c38a114d5bb33974df8dd11bc87','E0094','2012-07-31 08:09:45.828272','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ1YmIzMzk3NGRmOGRkMTFiYzg3JwpWRTAwOTQKcDEKKEkwClYKdE5WTmV3cG9y
dCwgUkkKcDIKUycnCihsKGwobChsSTAKSTAwCnRwMwou
',47,'Newport, RI',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,123,'c38a114cfca6940ab3799985b66','E0014','2012-07-31 08:09:45.836323','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmY2E2OTQwYWIzNzk5OTg1YjY2JwpWRTAwMTQKcDEKKEkyNgpWRWR1Y2F0aW9u
CnAyCnROVkRvcmNoZXN0ZXIgSGlnaCBTY2hvb2wsIFNhY3JlZCBIZWFydCBDb252ZW50CnAzClMn
JwoobChsKGwobEkwCkkwMAp0cDQKLg==
',18,'Dorchester High School, Sacred Heart Convent',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,124,'c38a114d52928410d1331d04ce5','E0079','2012-07-31 08:09:45.844268','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MjkyODQxMGQxMzMxZDA0Y2U1JwpWRTAwNzkKcDEKKEkzNwpWT2NjdXBhdGlv
bgpwMgp0TlZDb29wZXIsIFdhcmQgQm9zcwpwMwpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',29,'Cooper, Ward Boss',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,7,1965,0,0,0,0,0,'20 JUL 1965',2438962,0,125,'c38a114d1ba3409c9c6758678af','E0038','2012-07-31 08:09:45.853065','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxYmEzNDA5YzljNjc1ODY3OGFmJwpWRTAwMzgKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTIwCkk3CkkxOTY1CkkwMAp0VjIwIEpVTCAxOTY1CnAzCkkyNDM4OTYyCkkw
CnRWClZjMzhhMTE0YzA0YjQ5NDU1OGZjNTFmMTlhZQpwNAoobChsKGwobEkwCkkwMAp0cDUKLg==
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,126,'c38a114d0bf415944d3fdd6df5d','E0029','2012-07-31 08:09:45.861006','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwYmY0MTU5NDRkM2ZkZDZkZjVkJwpWRTAwMjkKcDEKKEkzNQpWTm9iaWxpdHkg
VGl0bGUKcDIKdE5WSnIuCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1887,0,0,0,0,0,'1887',2410273,0,127,'c38a114db2c261282e8b8f91d66','E0136','2012-07-31 08:09:45.868883','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRiMmMyNjEyODJlOGI4ZjkxZDY2JwpWRTAxMzYKcDEKKEkxClZNYXJyaWFnZQpw
Mgp0KEkwCkkwCkkwCihJMApJMApJMTg4NwpJMDAKdFYxODg3CnAzCkkyNDEwMjczCkkwCnRWClMn
JwoobChsKGwobEkwCkkwMAp0cDQKLg==
',37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,128,'c38a114d60e306ed109f0ff26b5','E0101','2012-07-31 08:09:45.881256','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MGUzMDZlZDEwOWYwZmYyNmI1JwpWRTAxMDEKcDEKKEkwClYKdE5WTGF0ZXIg
b24gaW4gbGlmZSBoZSBmYWNlZCBzZXJpb3VzIGJhY2sgc3VyZ2VyeSB0d28gdGltZXMsIG9uCnAy
ClMnJwoobChsKGwobEkwCkkwMAp0cDMKLg==
',47,'Later on in life he faced serious back surgery two times, on',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,129,'c38a114d5331caf44146811ea20','E0083','2012-07-31 08:09:45.892827','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MzMxY2FmNDQxNDY4MTFlYTIwJwpWRTAwODMKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,130,'c38a114d60b6adc512ee72131a4','E0100','2012-07-31 08:09:45.901816','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MGI2YWRjNTEyZWU3MjEzMWE0JwpWRTAxMDAKcDEKKEkyNgpWRWR1Y2F0aW9u
CnAyCnROVkNob2F0ZSwgTG9uZG9uIFNjaC4gT2YgRWNvbi4sIFByaW5jZXRvbiwgSGFydmFyZApw
MwpTJycKKGwobChsKGxJMApJMDAKdHA0Ci4=
',18,'Choate, London Sch. Of Econ., Princeton, Harvard',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,3,1960,0,0,0,0,0,'MAR 1960',2436995,0,131,'c38a114d4841b2b07411ba0c4c4','E0065','2012-07-31 08:09:45.910007','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0ODQxYjJiMDc0MTFiYTBjNGM0JwpWRTAwNjUKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTMKSTE5NjAKSTAwCnRWTUFSIDE5NjAKcDMKSTI0MzY5OTUKSTAKdFYK
UycnCihsKGwobChsSTAKSTAwCnRwNAou
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,132,'c38a114d6583b87232bcf90929','E0106','2012-07-31 08:09:45.917977','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NTgzYjg3MjMyYmNmOTA5MjknClZFMDEwNgpwMQooSTAKVgp0TlZJbiAxOTU1
IEphY2tpZSBzdWZmZXJlZCBhIG1pc2NhcnJpYWdlCnAyClMnJwoobChsKGwobEkwCkkwMAp0cDMK
Lg==
',47,'In 1955 Jackie suffered a miscarriage',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1923,0,0,0,0,0,'1923',2423421,0,133,'c38a114d50216496bc7b1e66031','E0075','2012-07-31 08:09:45.925869','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MDIxNjQ5NmJjN2IxZTY2MDMxJwpWRTAwNzUKcDEKKEkxMwpWRGVhdGgKcDIK
dChJMApJMApJMAooSTAKSTAKSTE5MjMKSTAwCnRWMTkyMwpwMwpJMjQyMzQyMQpJMAp0VgpTJycK
KGwobChsKGxJMApJMDAKdHA0Ci4=
',5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1921,0,0,0,0,0,'JUL 1921',2422872,0,134,'c38a114d114273842308a40a5bd','E0031','2012-07-31 08:09:45.934680','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxMTQyNzM4NDIzMDhhNDBhNWJkJwpWRTAwMzEKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTAKSTcKSTE5MjEKSTAwCnRWSlVMIDE5MjEKcDMKSTI0MjI4NzIKSTAKdFYK
VmMzOGExMTRjMDRiNDk0NTU4ZmM1MWYxOWFlCnA0CihsKGwobChsSTAKSTAwCnRwNQou
',4,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,135,'c38a114d2d058e87fa5d779bc1b','E0049','2012-07-31 08:09:45.942799','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQyZDA1OGU4N2ZhNWQ3NzliYzFiJwpWRTAwNDkKcDEKKEkzNQpWTm9iaWxpdHkg
VGl0bGUKcDIKdE5WSnIuCnAzClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,3,1967,0,0,0,0,0,'24 MAR 1967',2439574,0,136,'c38a114d384526d36a92b145022','E0057','2012-07-31 08:09:45.951546','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQzODQ1MjZkMzZhOTJiMTQ1MDIyJwpWRTAwNTcKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTI0CkkzCkkxOTY3CkkwMAp0VjI0IE1BUiAxOTY3CnAzCkkyNDM5NTc0Ckkw
CnRWClZjMzhhMTE0ZDFhNDFlMWIyYWViNmI3OGYyYjQKcDQKKGwobChsKGxJMApJMDAKdHA1Ci4=
',4,'',27);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,137,'c38a114cfd767b3032b1cd70f11','E0016','2012-07-31 08:09:45.959478','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmZDc2N2IzMDMyYjFjZDcwZjExJwpWRTAwMTYKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,138,'c38a114c1897f6513f59d82bdc3','E0009','2012-07-31 08:09:45.967466','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxODk3ZjY1MTNmNTlkODJiZGMzJwpWRTAwMDkKcDEKKEkwClYKdE5WQnJvb2ts
aW5lLCBNQQpwMgpTJycKKGwobChsKGxJMApJMDAKdHAzCi4=
',47,'Brookline, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,139,'c38a114d27c60a40814ba1f6749','E0045','2012-07-31 08:09:45.975460','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyN2M2MGE0MDgxNGJhMWY2NzQ5JwpWRTAwNDUKcDEKKEk0MQpWUmVsaWdpb24K
cDIKdE5WUm9tYW4gQ2F0aG9saWMKcDMKUycnCihsKGwobChsSTAKSTAwCnRwNAou
',33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,140,'c38a114d27b1fd6bdea674ee996','E0044','2012-07-31 08:09:45.983382','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyN2IxZmQ2YmRlYTY3NGVlOTk2JwpWRTAwNDQKcDEKKEkwClYKdE5WSGlja29y
eSBIaWxsCnAyClMnJwoobChsKGwobEkwCkkwMAp0cDMKLg==
',47,'Hickory Hill',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1965,0,0,0,0,0,'1965',2438762,0,141,'c38a114da1e2cf9a8d1d522d105','E0132','2012-07-31 08:09:45.991308','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRhMWUyY2Y5YThkMWQ1MjJkMTA1JwpWRTAxMzIKcDEKKEk3ClZEaXZvcmNlCnAy
CnQoSTAKSTAKSTAKKEkwCkkwCkkxOTY1CkkwMAp0VjE5NjUKcDMKSTI0Mzg3NjIKSTAKdFYKUycn
CihsKGwobChsSTAKSTAwCnRwNAou
',43,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,1,1995,0,0,0,0,0,'25 JAN 1995',2449743,0,142,'c38a114cfbc3d5ca2be95a77e32','E0013','2012-07-31 08:09:46.000037','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmYmMzZDVjYTJiZTk1YTc3ZTMyJwpWRTAwMTMKcDEKKEkxOQpWQnVyaWFsCnAy
CnQoSTAKSTAKSTAKKEkyNQpJMQpJMTk5NQpJMDAKdFYyNSBKQU4gMTk5NQpwMwpJMjQ0OTc0MwpJ
MAp0VgpWYzM4YTExNGMxMjQxZDc3ZjAwYzgyMmU0YjU4CnA0CihsKGwobChsSTAKSTAwCnRwNQou
',11,'',6);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,9,1961,0,0,0,0,0,'26 SEP 1961',2437569,0,143,'c38a114d49a46565f60ff41e5c1','E0067','2012-07-31 08:09:46.007951','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0OWE0NjU2NWY2MGZmNDFlNWMxJwpWRTAwNjcKcDEKKEkxMgpWQmlydGgKcDIK
dChJMApJMApJMAooSTI2Ckk5CkkxOTYxCkkwMAp0VjI2IFNFUCAxOTYxCnAzCkkyNDM3NTY5Ckkw
CnRWClMnJwoobChsKGwobEkwCkkwMAp0cDQKLg==
',4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,144,'c38a114d6621f0d71e68276a3fd','E0107','2012-07-31 08:09:46.016016','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NjIxZjBkNzFlNjgyNzZhM2ZkJwpWRTAxMDcKcDEKKEkwClYKdE5WNXRoIEF2
ZW51ZSwgTllDLCBOWQpwMgpTJycKKGwobChsKGxJMApJMDAKdHAzCi4=
',47,'5th Avenue, NYC, NY',NULL);
CREATE TABLE "grampsdb_repository" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "repository_type_id" integer NOT NULL REFERENCES "grampsdb_repositorytype" ("id"),
    "name" text NOT NULL
);
CREATE TABLE "grampsdb_place" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "title" text NOT NULL,
    "long" text NOT NULL,
    "lat" text NOT NULL
);
INSERT INTO "grampsdb_place" VALUES(1,'c38a114d45238812acd028ecae1','P0013','2012-07-31 08:09:46.026467','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0NTIzODgxMmFjZDAyOGVjYWUxJwpWUDAwMTMKcDEKVkJyb29rbGluZSwgTUEK
cDIKVgpWCk4obChsKGwobChsSTAKSTAwCnRwMwou
','Brookline, MA','','');
INSERT INTO "grampsdb_place" VALUES(2,'c38a114d36c1e80c0c2e8a1d8e0','P0012','2012-07-31 08:09:46.032409','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQzNmMxZTgwYzBjMmU4YTFkOGUwJwpWUDAwMTIKcDEKVk5ldyBZb3JrCnAyClYK
VgpOKGwobChsKGwobEkwCkkwMAp0cDMKLg==
','New York','','');
INSERT INTO "grampsdb_place" VALUES(3,'c38a114dbe656c920d501d2511c','P0027','2012-07-31 08:09:46.038386','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRiZTY1NmM5MjBkNTAxZDI1MTFjJwpWUDAwMjcKcDEKVk5ld3BvcnQsIFJJCnAy
ClYKVgpOKGwobChsKGwobEkwCkkwMAp0cDMKLg==
','Newport, RI','','');
INSERT INTO "grampsdb_place" VALUES(4,'c38a114d55f2281e40b015b6d3d','P0015','2012-07-31 08:09:46.044196','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NWYyMjgxZTQwYjAxNWI2ZDNkJwpWUDAwMTUKcDEKVkNhdGhlZHJhbCBPZiBU
aGUgSG9seSBDcm9zcywgTUEKcDIKVgpWCk4obChsKGwobChsSTAKSTAwCnRwMwou
','Cathedral Of The Holy Cross, MA','','');
INSERT INTO "grampsdb_place" VALUES(5,'c38a114d69a1f73a6964e8f1067','P0021','2012-07-31 08:09:46.049997','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2OWExZjczYTY5NjRlOGYxMDY3JwpWUDAwMjEKcDEKVlN0LiBQYXRyaWNrcyBD
YXRoZWRyYWwKcDIKVgpWCk4obChsKGwobChsSTAKSTAwCnRwMwou
','St. Patricks Cathedral','','');
INSERT INTO "grampsdb_place" VALUES(6,'c38a114c1241d77f00c822e4b58','P0002','2012-07-31 08:09:46.055805','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxMjQxZDc3ZjAwYzgyMmU0YjU4JwpWUDAwMDIKcDEKVkhvbHlob29kIENlbWV0
ZXJ5LCBCcm9va2xpbmUsIE1BIApwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Holyhood Cemetery, Brookline, MA ','','');
INSERT INTO "grampsdb_place" VALUES(7,'c38a114daa61a66f6b44c46d827','P0025','2012-07-31 08:09:46.061591','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRhYTYxYTY2ZjZiNDRjNDZkODI3JwpWUDAwMjUKcDEKVkdyZWVud2ljaCwgQ29u
bmVjdGljdXQKcDIKVgpWCk4obChsKGwobChsSTAKSTAwCnRwMwou
','Greenwich, Connecticut','','');
INSERT INTO "grampsdb_place" VALUES(8,'c38a114d99e19965d58f8ef56ed','P0024','2012-07-31 08:09:46.067403','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ5OWUxOTk2NWQ1OGY4ZWY1NmVkJwpWUDAwMjQKcDEKVkxvbmRvbgpwMgpWClYK
TihsKGwobChsKGxJMApJMDAKdHAzCi4=
','London','','');
INSERT INTO "grampsdb_place" VALUES(9,'c38a114d2694b2e4f31f927cdfc','P0010','2012-07-31 08:09:46.073233','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyNjk0YjJlNGYzMWY5MjdjZGZjJwpWUDAwMTAKcDEKVkxvcyBBbmdlbGVzLCBD
QQpwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Los Angeles, CA','','');
INSERT INTO "grampsdb_place" VALUES(10,'c38a114c04b494558fc51f19ae','P0000','2012-07-31 08:09:46.079299','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMwNGI0OTQ1NThmYzUxZjE5YWUnClZQMDAwMApwMQpWQm9zdG9uLCBNQQpwMgpW
ClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Boston, MA','','');
INSERT INTO "grampsdb_place" VALUES(11,'c38a114d584fe2b4bc5ea2634f','P0017','2012-07-31 08:09:46.085083','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1ODRmZTJiNGJjNWVhMjYzNGYnClZQMDAxNwpwMQpWU3QuIFBoaWxvbWVuYSdz
IENlbWV0ZXJ5LCBOWQpwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','St. Philomena''s Cemetery, NY','','');
INSERT INTO "grampsdb_place" VALUES(12,'c38a114c1052ba5b68c7ba60bfd','P0001','2012-07-31 08:09:46.090870','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxMDUyYmE1YjY4YzdiYTYwYmZkJwpWUDAwMDEKcDEKVkh5YW5uaXMgUG9ydCwg
TUEKcDIKVgpWCk4obChsKGwobChsSTAKSTAwCnRwMwou
','Hyannis Port, MA','','');
INSERT INTO "grampsdb_place" VALUES(13,'c38a114d6417ff6761fdfcbbdd','P0019','2012-07-31 08:09:46.096741','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NDE3ZmY2NzYxZmRmY2JiZGQnClZQMDAxOQpwMQpWU291dGhhbXB0b24sIExv
bmcgSXNsYW5kLCBOWQpwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Southampton, Long Island, NY','','');
INSERT INTO "grampsdb_place" VALUES(14,'c38a114d00f46b26422005de3f7','P0005','2012-07-31 08:09:46.102546','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMGY0NmIyNjQyMjAwNWRlM2Y3JwpWUDAwMDUKcDEKVlN1ZmZvbGssIEVuZ2xh
bmQKcDIKVgpWCk4obChsKGwobChsSTAKSTAwCnRwMwou
','Suffolk, England','','');
INSERT INTO "grampsdb_place" VALUES(15,'c38a114d0ca1fbb9b6afea9d73d','P0008','2012-07-31 08:09:46.108316','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwY2ExZmJiOWI2YWZlYTlkNzNkJwpWUDAwMDgKcDEKVldlc3RtaW5zdGVyLCBN
RApwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Westminster, MD','','');
INSERT INTO "grampsdb_place" VALUES(16,'c38a114d6e063715ecb47bd75c','P0022','2012-07-31 08:09:46.114195','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2ZTA2MzcxNWVjYjQ3YmQ3NWMnClZQMDAyMgpwMQpWT3RpcyBBaXIgRm9yY2Ug
QiwgTWFzcwpwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Otis Air Force B, Mass','','');
INSERT INTO "grampsdb_place" VALUES(17,'c38a114d57c647449bd0d6d95eb','P0016','2012-07-31 08:09:46.120039','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1N2M2NDc0NDliZDBkNmQ5NWViJwpWUDAwMTYKcDEKVkxlbm5veCBIaWxsIEhv
c3AuLCBOWQpwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Lennox Hill Hosp., NY','','');
INSERT INTO "grampsdb_place" VALUES(18,'c38a114d64b625f8b08b9790d0a','P0020','2012-07-31 08:09:46.125833','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NGI2MjVmOGIwOGI5NzkwZDBhJwpWUDAwMjAKcDEKVk5ZQywgTlkKcDIKVgpW
Ck4obChsKGwobChsSTAKSTAwCnRwMwou
','NYC, NY','','');
INSERT INTO "grampsdb_place" VALUES(19,'c38a114cfba4b590ae84a2f6c10','P0004','2012-07-31 08:09:46.131618','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmYmE0YjU5MGFlODRhMmY2YzEwJwpWUDAwMDQKcDEKVkh5YW5uaXMgUG9ydCwg
TUEgCnAyClYKVgpOKGwobChsKGwobEkwCkkwMAp0cDMKLg==
','Hyannis Port, MA ','','');
INSERT INTO "grampsdb_place" VALUES(20,'c38a114d073602b727cc4088c89','P0006','2012-07-31 08:09:46.137755','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwNzM2MDJiNzI3Y2M0MDg4Yzg5JwpWUDAwMDYKcDEKVkJlbGdpdW0KcDIKVgpW
Ck4obChsKGwobChsSTAKSTAwCnRwMwou
','Belgium','','');
INSERT INTO "grampsdb_place" VALUES(21,'c38a114d275a141c4c5debcbcc','P0011','2012-07-31 08:09:46.143770','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyNzVhMTQxYzRjNWRlYmNiY2MnClZQMDAxMQpwMQpWQXJsaW5ndG9uIE5hdGlv
bmFsLCBWQQpwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Arlington National, VA','','');
INSERT INTO "grampsdb_place" VALUES(22,'c38a114d094c8dda421d5d0c7b','P0007','2012-07-31 08:09:46.149619','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwOTRjOGRkYTQyMWQ1ZDBjN2InClZQMDAwNwpwMQpWRnJhbmNlCnAyClYKVgpO
KGwobChsKGwobEkwCkkwMAp0cDMKLg==
','France','','');
INSERT INTO "grampsdb_place" VALUES(23,'c38a114d6ee2dbf3fa14b0cdb56','P0023','2012-07-31 08:09:46.155635','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2ZWUyZGJmM2ZhMTRiMGNkYjU2JwpWUDAwMjMKcDEKVkJvc3RvbiwgTWFzcwpw
MgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','Boston, Mass','','');
INSERT INTO "grampsdb_place" VALUES(24,'c38a114d51a7adeef1cc541e744','P0014','2012-07-31 08:09:46.161425','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MWE3YWRlZWYxY2M1NDFlNzQ0JwpWUDAwMTQKcDEKVkR1bmdhbnN0b3duLCBJ
cmVsYW5kCnAyClYKVgpOKGwobChsKGwobEkwCkkwMAp0cDMKLg==
','Dunganstown, Ireland','','');
INSERT INTO "grampsdb_place" VALUES(25,'c38a114d5fdf41b0f29146b02','P0018','2012-07-31 08:09:46.167263','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1ZmRmNDFiMGYyOTE0NmIwMicKVlAwMDE4CnAxClZEYWxsYXMsIFRYCnAyClYK
VgpOKGwobChsKGwobEkwCkkwMAp0cDMKLg==
','Dallas, TX','','');
INSERT INTO "grampsdb_place" VALUES(26,'c38a114cfb054b26ec72491e417','P0003','2012-07-31 08:09:46.173057','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmYjA1NGIyNmVjNzI0OTFlNDE3JwpWUDAwMDMKcDEKVk5vcnRoIEVuZCwgQm9z
dG9uLCBNQQpwMgpWClYKTihsKGwobChsKGxJMApJMDAKdHAzCi4=
','North End, Boston, MA','','');
INSERT INTO "grampsdb_place" VALUES(27,'c38a114d1a41e1b2aeb6b78f2b4','P0009','2012-07-31 08:09:46.178894','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQxYTQxZTFiMmFlYjZiNzhmMmI0JwpWUDAwMDkKcDEKVldhc2hpbmd0b24sIERD
CnAyClYKVgpOKGwobChsKGwobEkwCkkwMAp0cDMKLg==
','Washington, DC','','');
INSERT INTO "grampsdb_place" VALUES(28,'c38a114db7840c29658efac3637','P0026','2012-07-31 08:09:46.184658','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGRiNzg0MGMyOTY1OGVmYWMzNjM3JwpWUDAwMjYKcDEKVkhvbHkgQ3Jvc3MgQ2F0
aGVkcmFsLCBCb3N0b24sIE1BCnAyClYKVgpOKGwobChsKGwobEkwCkkwMAp0cDMKLg==
','Holy Cross Cathedral, Boston, MA','','');
CREATE TABLE "grampsdb_media_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "media_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "grampsdb_tag" ("id"),
    UNIQUE ("media_id", "tag_id")
);
CREATE TABLE "grampsdb_media" (
    "calendar" integer NOT NULL,
    "modifier" integer NOT NULL,
    "quality" integer NOT NULL,
    "day1" integer NOT NULL,
    "month1" integer NOT NULL,
    "year1" integer NOT NULL,
    "slash1" bool NOT NULL,
    "day2" integer,
    "month2" integer,
    "year2" integer,
    "slash2" bool,
    "text" varchar(80) NOT NULL,
    "sortval" integer NOT NULL,
    "newyear" integer NOT NULL,
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "path" text NOT NULL,
    "mime" text,
    "desc" text NOT NULL
);
CREATE TABLE "grampsdb_note_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "note_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "grampsdb_tag" ("id"),
    UNIQUE ("note_id", "tag_id")
);
CREATE TABLE "grampsdb_note" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "public" bool NOT NULL,
    "cache" text,
    "note_type_id" integer NOT NULL REFERENCES "grampsdb_notetype" ("id"),
    "text" text NOT NULL,
    "preformatted" bool NOT NULL
);
INSERT INTO "grampsdb_note" VALUES(1,'c38a114cfeb5b07b87c137ce270','N0010','2012-07-31 08:09:41.919317','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmZWI1YjA3Yjg3YzEzN2NlMjcwJwpWTjAwMTAKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwMDI6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDU4OiAxIE5P
VEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDYwOiAx
IE5PVEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDYy
OiAxIE5PVEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUK
KEkwCkkyMjcKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0
cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0002:

Empty note ignored                 Line    58: 1 NOTE 
Empty note ignored                 Line    60: 1 NOTE 
Empty note ignored                 Line    62: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(2,'c38a114d5871f0c57270f220844','N0042','2012-07-31 08:09:41.925334','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1ODcxZjBjNTcyNzBmMjIwODQ0JwpWTjAwNDIKcDEKKGxwMgpWSGUgd2FzIGtu
b3duIGFzICJCbGFjayBKYWNrLiIKcDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUKdEkwCih0
STAwCnRwNgou
',3,'He was known as "Black Jack."',0);
INSERT INTO "grampsdb_note" VALUES(3,'c38a114cfce4badb362314a0660','N0006','2012-07-31 08:09:41.935057','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmY2U0YmFkYjM2MjMxNGEwNjYwJwpWTjAwMDYKcDEKKGxwMgpWU2hlIHdhcyBj
b25zaWRlcmVkIHRoZSBmbG93ZXIgb2YgQm9zdG9uIElyaXNoIHNvY2lldHkuCnAzCmEobHA0CmFJ
MDAKKEkxClZHZW5lcmFsCnA1CnRJMAoodEkwMAp0cDYKLg==
',3,'She was considered the flower of Boston Irish society.',0);
INSERT INTO "grampsdb_note" VALUES(4,'c38a114d90617a60ef9e9e3c1','N0073','2012-07-31 08:09:41.939848','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ5MDYxN2E2MGVmOWU5ZTNjMScKVk4wMDczCnAxCihscDIKVlJlY29yZHMgbm90
IGltcG9ydGVkIGludG8gVG9wIExldmVsOlx1MDAwYVx1MDAwYUxpbmUgaWdub3JlZCBhcyBub3Qg
dW5kZXJzdG9vZCAgICAgTGluZSAgIDcyNjogMCBDNiBDU1RBXHUwMDBhU2tpcHBlZCBzdWJvcmRp
bmF0ZSBsaW5lICAgICAgICAgICBMaW5lICAgNzI3OiAxIE5BTUUgRm9zdGVyXHUwMDBhCnAzCmEo
bHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkxNTYKdHA2CmF0cDcKYWFJ
MDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into Top Level:

Line ignored as not understood     Line   726: 0 C6 CSTA
Skipped subordinate line           Line   727: 1 NAME Foster
',0);
INSERT INTO "grampsdb_note" VALUES(5,'c38a114d8c54a9fa4d70b728236','N0066','2012-07-31 08:09:41.946957','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4YzU0YTlmYTRkNzBiNzI4MjM2JwpWTjAwNjYKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAxMDpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA3MTM6IDEgTkFNRSBD
QlMgVGhpcyBNb3JuaW5nIHNob3cuXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9u
b3NwYWNlCihscDUKKEkwCkkxMzUKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4
CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into SOUR (source) Gramps ID S0010:

Line ignored as not understood     Line   713: 1 NAME CBS This Morning show.
',0);
INSERT INTO "grampsdb_note" VALUES(6,'c38a114d876249b8ff332e57aaf','N0061','2012-07-31 08:09:41.953207','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4NzYyNDliOGZmMzMyZTU3YWFmJwpWTjAwNjEKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAwNTpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA3MDM6IDEgTkFNRSBO
ZXcgWW9yayBXb3JsZCBUZWxlZ3JhbSBhbmQgU3VuLCBPY3QgMTEsIDE5NTcsIHBnLiAxLlx1MDAw
YQpwMwphKGxwNAooKEkzClZmb250ZmFjZQp0Vk1vbm9zcGFjZQoobHA1CihJMApJMTY2CnRwNgph
dHA3CmFhSTAwCihJMApWR0VEQ09NIGltcG9ydApwOAp0STAKKHRJMDAKdHA5Ci4=
',27,'Records not imported into SOUR (source) Gramps ID S0005:

Line ignored as not understood     Line   703: 1 NAME New York World Telegram and Sun, Oct 11, 1957, pg. 1.
',0);
INSERT INTO "grampsdb_note" VALUES(7,'c38a114cf953ed9e71d0af6fcc2','N0005','2012-07-31 08:09:41.959557','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmOTUzZWQ5ZTcxZDBhZjZmY2MyJwpWTjAwMDUKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwMDE6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDI2OiAxIE5P
VEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDI4OiAx
IE5PVEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDMw
OiAxIE5PVEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAg
IDMyOiAxIE5PVEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihs
cDUKKEkwCkkyODIKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkw
MAp0cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0001:

Empty note ignored                 Line    26: 1 NOTE 
Empty note ignored                 Line    28: 1 NOTE 
Empty note ignored                 Line    30: 1 NOTE 
Empty note ignored                 Line    32: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(8,'c38a114d661240f980fa7aad385','N0055','2012-07-31 08:09:41.965220','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NjEyNDBmOTgwZmE3YWFkMzg1JwpWTjAwNTUKcDEKKGxwMgpWU2hlIHdhcyBz
YWlkIHRvIGJlIHRoZSBvbmx5IEZpcnN0IExhZHkgdG8gcmVzZW1ibGUgcm95YWx0eS4gU2hlIHNo
dW5uZWQgdGhlIG1lZGlhIGFuZCBuZXZlciBwdWJsaWNseSBkaXNjdXNzZWQgdGhlIGFzc2Fzc2lu
YXRpb24gb2YgSkZLLCBob3cgc2hlIGZlbHQgYWJvdXQgaXQsIG9yIHRoZSBhbGxlZ2VkIGFmZmFp
cnMgb2YgaGVyIGZpcnN0IGh1c2JhbmQuCnAzCmEobHA0CmFJMDAKKEkxClZHZW5lcmFsCnA1CnRJ
MAoodEkwMAp0cDYKLg==
',3,'She was said to be the only First Lady to resemble royalty. She shunned the media and never publicly discussed the assassination of JFK, how she felt about it, or the alleged affairs of her first husband.',0);
INSERT INTO "grampsdb_note" VALUES(9,'c38a114d6106a553c7e2fd63664','N0047','2012-07-31 08:09:41.970753','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MTA2YTU1M2M3ZTJmZDYzNjY0JwpWTjAwNDcKcDEKKGxwMgpWSW4gMTk2MCBo
ZSBiZWNhbWUgUHJlc2lkZW50IG9mIHRoZSBVbml0ZWQgU3RhdGVzLgpwMwphKGxwNAphSTAwCihJ
MQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'In 1960 he became President of the United States.',0);
INSERT INTO "grampsdb_note" VALUES(10,'c38a114d1265bcfe5a5a9f9d7e','N0023','2012-07-31 08:09:41.976131','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxMjY1YmNmZTVhNWE5ZjlkN2UnClZOMDAyMwpwMQoobHAyClZTaGUgcmFuIGEg
c3VtbWVyIGhvbWUgZm9yIHJldGFyZGVkIGNoaWxkcmVuLgpwMwphKGxwNAphSTAwCihJMQpWR2Vu
ZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'She ran a summer home for retarded children.',0);
INSERT INTO "grampsdb_note" VALUES(11,'c38a114d65b10a07ccf6f7f8c62','N0053','2012-07-31 08:09:41.981541','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NWIxMGEwN2NjZjZmN2Y4YzYyJwpWTjAwNTMKcDEKKGxwMgpWQmVmb3JlIG1h
cnJ5aW5nIEpGSywgSmFja2llIHdvcmtlZCBhcyBhIHBob3RvIGpvdXJuYWxpc3QgaW4gV2FzaGlu
Z3RvbiBEQy4KcDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'Before marrying JFK, Jackie worked as a photo journalist in Washington DC.',0);
INSERT INTO "grampsdb_note" VALUES(12,'c38a114d0cdc24eabd516f92df','N0021','2012-07-31 08:09:41.987079','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwY2RjMjRlYWJkNTE2ZjkyZGYnClZOMDAyMQpwMQoobHAyClYxOTcyIHdhcyB0
aGUgdmljZSBwcmVzaWRlbnRpYWwgY2FuZGlkYXRlLgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJh
bApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'1972 was the vice presidential candidate.',0);
INSERT INTO "grampsdb_note" VALUES(13,'c38a114d8ee2980167c585827c','N0070','2012-07-31 08:09:41.991734','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4ZWUyOTgwMTY3YzU4NTgyN2MnClZOMDA3MApwMQoobHAyClZSZWNvcmRzIG5v
dCBpbXBvcnRlZCBpbnRvIFRvcCBMZXZlbDpcdTAwMGFcdTAwMGFMaW5lIGlnbm9yZWQgYXMgbm90
IHVuZGVyc3Rvb2QgICAgIExpbmUgICA3MjA6IDAgQzMgQ1NUQVx1MDAwYVNraXBwZWQgc3Vib3Jk
aW5hdGUgbGluZSAgICAgICAgICAgTGluZSAgIDcyMTogMSBOQU1FIElsbGVnaXRpbWF0ZVx1MDAw
YQpwMwphKGxwNAooKEkzClZmb250ZmFjZQp0Vk1vbm9zcGFjZQoobHA1CihJMApJMTYyCnRwNgph
dHA3CmFhSTAwCihJMApWR0VEQ09NIGltcG9ydApwOAp0STAKKHRJMDAKdHA5Ci4=
',27,'Records not imported into Top Level:

Line ignored as not understood     Line   720: 0 C3 CSTA
Skipped subordinate line           Line   721: 1 NAME Illegitimate
',0);
INSERT INTO "grampsdb_note" VALUES(14,'c38a114d02a3bd84ff3dcc4808b','N0014','2012-07-31 08:09:41.998034','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMmEzYmQ4NGZmM2RjYzQ4MDhiJwpWTjAwMTQKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwMDM6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDgyOiAxIE5P
VEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDg0OiAx
IE5PVEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkw
CkkxNzIKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkK
Lg==
',27,'Records not imported into INDI (individual) Gramps ID I0003:

Empty note ignored                 Line    82: 1 NOTE 
Empty note ignored                 Line    84: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(15,'c38a114d61436c0b51931d1db56','N0048','2012-07-31 08:09:42.003433','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MTQzNmMwYjUxOTMxZDFkYjU2JwpWTjAwNDgKcDEKKGxwMgpWSGUgd3JvdGUg
MiBib29rcywgaW5jbHVkaW5nICJQcm9maWxlcyBpbiBDb3VyYWdlIiwgd2hpY2ggd29uIGhpbSBh
IFB1bGl0emVyIFByaXplLgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAK
dHA2Ci4=
',3,'He wrote 2 books, including "Profiles in Courage", which won him a Pulitzer Prize.',0);
INSERT INTO "grampsdb_note" VALUES(16,'c38a114d0437d2aa47a732f61ee','N0015','2012-07-31 08:09:42.009171','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwNDM3ZDJhYTQ3YTczMmY2MWVlJwpWTjAwMTUKcDEKKGxwMgpWU2hlIHdhcyBi
b3JuIHNldmVyZWx5IG1lbnRhbGx5IHJldGFyZGVkLiBGb3IgeWVhcnMgaGVyIHBhcmVudHMgd2Vy
ZSBhc2hhbWVkIG9mIGhlciBhbmQgbmV2ZXIgdG9sZCBhbnlvbmUgYWJvdXQgaGVyIHByb2JsZW1z
LgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'She was born severely mentally retarded. For years her parents were ashamed of her and never told anyone about her problems.',0);
INSERT INTO "grampsdb_note" VALUES(17,'c38a114cfd1c1edf7511a4e92e','N0007','2012-07-31 08:09:42.014764','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmZDFjMWVkZjc1MTFhNGU5MmUnClZOMDAwNwpwMQoobHAyClZTaGUgZ3JhZHVh
dGVkIGZyb20gaGlnaCBzY2hvb2wsIG9uZSBvZiB0aGUgdGhyZWUgaGlnaGVzdCBpbiBhIGNsYXNz
IG9mIDI4NS4gU2hlIHdhcyB0aGVuIHNlbnQgdG8gZmluaXNoIHNjaG9vbCBpbiBFdXJvcGUgZm9y
IHR3byB5ZWFycy4KcDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'She graduated from high school, one of the three highest in a class of 285. She was then sent to finish school in Europe for two years.',0);
INSERT INTO "grampsdb_note" VALUES(18,'c38a114d5ce36b1be2138c4b616','N0045','2012-07-31 08:09:42.020204','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ1Y2UzNmIxYmUyMTM4YzRiNjE2JwpWTjAwNDUKcDEKKGxwMgpWSGUgd2FzIGtu
b3duIGFzICJIb25leSBGaXR6Ii4KcDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUKdEkwCih0
STAwCnRwNgou
',3,'He was known as "Honey Fitz".',0);
INSERT INTO "grampsdb_note" VALUES(19,'c38a114d52f1a998b2aa7dc246','N0039','2012-07-31 08:09:42.025596','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MmYxYTk5OGIyYWE3ZGMyNDYnClZOMDAzOQpwMQoobHAyClZVcG9uIFBhdHJp
Y2sncyBhcnJpdmFsIGluIEJvc3RvbiwgaGUgaW1tZWRpYXRlbHkgYmVjYW1lIGludm9sdmVkIGlu
IHBvbGl0aWNzLiBIZSB3YXMga25vd24gYXMgYSBXYXJkIEJvc3MgaW4gQm9zdG9uLCBsb29raW5n
IG91dCBmb3IgdGhlIG90aGVyIElyaXNoIGltbWlncmFudHMgYW5kIHRyeWluZyB0byBpbXByb3Zl
IHRoZSBjb25kaXRpb25zIGluIHRoZSBjb21tdW5pdHkuCnAzCmEobHA0CmFJMDAKKEkxClZHZW5l
cmFsCnA1CnRJMAoodEkwMAp0cDYKLg==
',3,'Upon Patrick''s arrival in Boston, he immediately became involved in politics. He was known as a Ward Boss in Boston, looking out for the other Irish immigrants and trying to improve the conditions in the community.',0);
INSERT INTO "grampsdb_note" VALUES(20,'c38a114cfd6850a05c8d790df9','N0009','2012-07-31 08:09:42.031029','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmZDY4NTBhMDVjOGQ3OTBkZjknClZOMDAwOQpwMQoobHAyClZTaGUgd2FzIHZl
cnkgZGVkaWNhdGVkIHRvIGhlciBmYW1pbHksIHdoaWNoIHdhcyBldmlkZW50IGJ5IHRoZSBzdHJv
bmcgc3VwcG9ydCBzaGUgZ2F2ZSBoZXIgc29ucyBpbiB0aGVpciBwb2xpdGljYWwgY2FtcGFpZ25z
LgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'She was very dedicated to her family, which was evident by the strong support she gave her sons in their political campaigns.',0);
INSERT INTO "grampsdb_note" VALUES(21,'c38a114d4d87161772a78bb3801','N0033','2012-07-31 08:09:42.036411','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZDg3MTYxNzcyYTc4YmIzODAxJwpWTjAwMzMKcDEKKGxwMgpWQXMgYSB5b3Vu
ZyBtYW4sIFBhdHJpY2sgZHJvcHBlZCBvdXQgb2Ygc2Nob29sIHRvIHdvcmsgb24gdGhlIGRvY2tz
IG9mIEJvc3Rvbi4KcDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'As a young man, Patrick dropped out of school to work on the docks of Boston.',0);
INSERT INTO "grampsdb_note" VALUES(22,'c38a114d8d46c1c30fddb8cffdf','N0067','2012-07-31 08:09:42.042689','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4ZDQ2YzFjMzBmZGRiOGNmZmRmJwpWTjAwNjcKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAxMTpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA3MTU6IDEgTkFNRSBI
YXJyaXNidXJnIFBhdHJpb3QgTmV3cywgSmFudWFyeSAyNSwgMTk5NS5cdTAwMGEKcDMKYShscDQK
KChJMwpWZm9udGZhY2UKdFZNb25vc3BhY2UKKGxwNQooSTAKSTE1NQp0cDYKYXRwNwphYUkwMAoo
STAKVkdFRENPTSBpbXBvcnQKcDgKdEkwCih0STAwCnRwOQou
',27,'Records not imported into SOUR (source) Gramps ID S0011:

Line ignored as not understood     Line   715: 1 NAME Harrisburg Patriot News, January 25, 1995.
',0);
INSERT INTO "grampsdb_note" VALUES(23,'c38a114cfd41291feb5a30915c1','N0008','2012-07-31 08:09:42.048243','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGNmZDQxMjkxZmViNWEzMDkxNWMxJwpWTjAwMDgKcDEKKGxwMgpWU2hlIHdhcyBj
b3VydGVkIGJ5IHNvbWUgb2YgdGhlIGZpbmVzdCB5b3VuZyBtZW4sIG5vdCBvbmx5IEJvc3Rvbidz
IElyaXNoLCBidXQgbWVtYmVycyBvZiB0aGUgRW5nbGlzaCBub2JpbGl0eSBhcyB3ZWxsLgpwMwph
KGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'She was courted by some of the finest young men, not only Boston''s Irish, but members of the English nobility as well.',0);
INSERT INTO "grampsdb_note" VALUES(24,'c38a114c13265fd56b4b5542142','N0000','2012-07-31 08:09:42.053657','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxMzI2NWZkNTZiNGI1NTQyMTQyJwpWTjAwMDAKcDEKKGxwMgpWRnJvbSB0aGUg
dGltZSBoZSB3YXMgYSBzY2hvb2wgYm95IGhlIHdhcyBpbnRlcmVzdGVkIGluIG1ha2luZyBtb25l
eS4KcDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'From the time he was a school boy he was interested in making money.',0);
INSERT INTO "grampsdb_note" VALUES(25,'c38a114d27a3566b29b0f1127a0','N0028','2012-07-31 08:09:42.059044','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyN2EzNTY2YjI5YjBmMTEyN2EwJwpWTjAwMjgKcDEKKGxwMgpWSGUgd2FzIHZl
cnkgZGVkaWNhdGVkIHRvIGhpcyBjaGlsZHJlbiBhbmQgZXZlcnkgZXZlbmluZyBoYWQgcHJheWVy
cyB3aXRoIHRoZW0sIGVhY2ggb2YgdGhlbSBzYXlpbmcgdGhlIFJvc2FyeS4KcDMKYShscDQKYUkw
MAooSTEKVkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'He was very dedicated to his children and every evening had prayers with them, each of them saying the Rosary.',0);
INSERT INTO "grampsdb_note" VALUES(26,'c38a114d59274f6f48585f9fb63','N0044','2012-07-31 08:09:42.065304','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1OTI3NGY2ZjQ4NTg1ZjlmYjYzJwpWTjAwNDQKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwNDg6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNDczOiAxIE5P
VEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkx
MTcKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0048:

Empty note ignored                 Line   473: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(27,'c38a114d58a5aee729fcc42f105','N0043','2012-07-31 08:09:42.070826','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1OGE1YWVlNzI5ZmNjNDJmMTA1JwpWTjAwNDMKcDEKKGxwMgpWSGUgd2FzIGtu
b3duIHRvIGRyaW5rIGFsY29ob2wgZXhjZXNzaXZlbHkuCnAzCmEobHA0CmFJMDAKKEkxClZHZW5l
cmFsCnA1CnRJMAoodEkwMAp0cDYKLg==
',3,'He was known to drink alcohol excessively.',0);
INSERT INTO "grampsdb_note" VALUES(28,'c38a114d8995a0b70d8862d6b67','N0063','2012-07-31 08:09:42.077062','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4OTk1YTBiNzBkODg2MmQ2YjY3JwpWTjAwNjMKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAwNzpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA3MDc6IDEgTkFNRSBH
cm93aW5nIFVwIEtlbm5lZHksIEhhcnJpc29uIFJhaW5lIGFuZCBKb2huIFF1aW5uLlx1MDAwYQpw
MwphKGxwNAooKEkzClZmb250ZmFjZQp0Vk1vbm9zcGFjZQoobHA1CihJMApJMTYzCnRwNgphdHA3
CmFhSTAwCihJMApWR0VEQ09NIGltcG9ydApwOAp0STAKKHRJMDAKdHA5Ci4=
',27,'Records not imported into SOUR (source) Gramps ID S0007:

Line ignored as not understood     Line   707: 1 NAME Growing Up Kennedy, Harrison Raine and John Quinn.
',0);
INSERT INTO "grampsdb_note" VALUES(29,'c38a114d8fe3343819eedb14ce6','N0072','2012-07-31 08:09:42.081786','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4ZmUzMzQzODE5ZWVkYjE0Y2U2JwpWTjAwNzIKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBUb3AgTGV2ZWw6XHUwMDBhXHUwMDBhTGluZSBpZ25vcmVkIGFzIG5v
dCB1bmRlcnN0b29kICAgICBMaW5lICAgNzI0OiAwIEM1IENTVEFcdTAwMGFTa2lwcGVkIHN1Ym9y
ZGluYXRlIGxpbmUgICAgICAgICAgIExpbmUgICA3MjU6IDEgTkFNRSBTdGlsbGJvcm5cdTAwMGEK
cDMKYShscDQKKChJMwpWZm9udGZhY2UKdFZNb25vc3BhY2UKKGxwNQooSTAKSTE1OQp0cDYKYXRw
NwphYUkwMAooSTAKVkdFRENPTSBpbXBvcnQKcDgKdEkwCih0STAwCnRwOQou
',27,'Records not imported into Top Level:

Line ignored as not understood     Line   724: 0 C5 CSTA
Skipped subordinate line           Line   725: 1 NAME Stillborn
',0);
INSERT INTO "grampsdb_note" VALUES(30,'c38a114d4561d3857242f5400ca','N0031','2012-07-31 08:09:42.087193','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0NTYxZDM4NTcyNDJmNTQwMGNhJwpWTjAwMzEKcDEKKGxwMgpWV2FzIGtub3du
IGFzICJUZWRkeSIuCnAzCmEobHA0CmFJMDAKKEkxClZHZW5lcmFsCnA1CnRJMAoodEkwMAp0cDYK
Lg==
',3,'Was known as "Teddy".',0);
INSERT INTO "grampsdb_note" VALUES(31,'c38a114d469511ba2dc341a05f3','N0032','2012-07-31 08:09:42.093618','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0Njk1MTFiYTJkYzM0MWEwNWYzJwpWTjAwMzIKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwMzk6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgMzU5OiAxIE5P
VEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkx
MTcKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0039:

Empty note ignored                 Line   359: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(32,'c38a114d0177ff55b0c37987fd2','N0012','2012-07-31 08:09:42.099108','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMTc3ZmY1NWIwYzM3OTg3ZmQyJwpWTjAwMTIKcDEKKGxwMgpWSGUgZW5saXN0
ZWQgaW4gdGhlIE5hdnkgZHVyaW5nIFdvcmxkIFdhciBJSSwgYW5kIGRpZWQgZHVyaW5nIGEgbmF2
YWwgZmxpZ2h0LgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'He enlisted in the Navy during World War II, and died during a naval flight.',0);
INSERT INTO "grampsdb_note" VALUES(33,'c38a114d8b618d4a2b038fd49c8','N0065','2012-07-31 08:09:42.105369','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4YjYxOGQ0YTJiMDM4ZmQ0OWM4JwpWTjAwNjUKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAwOTpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA3MTE6IDEgTkFNRSBI
YXJyaXNidXJnIFBhdHJpb3QgTmV3cywgMjMgTWF5IDE5OTQuXHUwMDBhCnAzCmEobHA0CigoSTMK
VmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkxNTAKdHA2CmF0cDcKYWFJMDAKKEkwClZH
RURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into SOUR (source) Gramps ID S0009:

Line ignored as not understood     Line   711: 1 NAME Harrisburg Patriot News, 23 May 1994.
',0);
INSERT INTO "grampsdb_note" VALUES(34,'c38a114d5624c06dbfeafbf0b24','N0041','2012-07-31 08:09:42.110851','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1NjI0YzA2ZGJmZWFmYmYwYjI0JwpWTjAwNDEKcDEKKGxwMgpWQWZ0ZXIgaGVy
IGh1c2JhbmQgZGllZCwgc2hlIG9wZW5lZCB1cCBhICJOb3Rpb25zIFNob3AiIHRvIHByb3ZpZGUg
Zm9yIGhlciBmYW1pbHkuCnAzCmEobHA0CmFJMDAKKEkxClZHZW5lcmFsCnA1CnRJMAoodEkwMAp0
cDYKLg==
',3,'After her husband died, she opened up a "Notions Shop" to provide for her family.',0);
INSERT INTO "grampsdb_note" VALUES(35,'c38a114d6774f32deae41e0d537','N0056','2012-07-31 08:09:42.117109','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2Nzc0ZjMyZGVhZTQxZTBkNTM3JwpWTjAwNTYKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwNTM6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNTQ0OiAxIE5P
VEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNTQ2OiAx
IE5PVEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkw
CkkxNzIKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkK
Lg==
',27,'Records not imported into INDI (individual) Gramps ID I0053:

Empty note ignored                 Line   544: 1 NOTE 
Empty note ignored                 Line   546: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(36,'c38a114d09834b9495f7f730687','N0019','2012-07-31 08:09:42.122518','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwOTgzNGI5NDk1ZjdmNzMwNjg3JwpWTjAwMTkKcDEKKGxwMgpWU2VydmVkIHdp
dGggdGhlIFJlZCBDcm9zcyBpbiBFbmdsYW5kIGR1cmluZyB0aGUgd2FyLgpwMwphKGxwNAphSTAw
CihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'Served with the Red Cross in England during the war.',0);
INSERT INTO "grampsdb_note" VALUES(37,'c38a114d52c61f832a282a43313','N0038','2012-07-31 08:09:42.128147','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1MmM2MWY4MzJhMjgyYTQzMzEzJwpWTjAwMzgKcDEKKGxwMgpWVGhlIHBvdGF0
byBmYW1pbmUgb2YgMTg0NS00OCwgcGxhZ3VlZCB0aGUgY291bnRyeSBvZiBJcmVsYW5kIGFuZCBw
dXNoZWQgbWFueSBJcmlzaG1lbiB0byBmbGVlIHRvIHRoZSBsYW5kIG9mIHByb21pc2UsIHRoZSBV
U0EuIFBhdHJpY2sgS2VubmVkeSB3YXMgYW1vbmcgdGhvc2UgdG8gbGVhdmUgaGlzIGhvbWUgaW4g
V2V4Zm9yZCBDb3VudHksIElyZWxhbmQsIGluIDE4NDgsIGluIGhvcGVzIG9mIGZpbmRpbmcgYSBi
ZXR0ZXJcdTAwMGFsaWZlIGluIHRoZSBVUy4gT25jZSBoZSBhcnJpdmVkIGluIHRoZSBVUywgaGUg
c2V0dGxlZCBpbiBFYXN0IEJvc3Rvbiwgd2hlcmUgaGUgcmVtYWluZWQgZm9yIHRoZSByZXN0IG9m
IGhpcyBsaWZlLgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'The potato famine of 1845-48, plagued the country of Ireland and pushed many Irishmen to flee to the land of promise, the USA. Patrick Kennedy was among those to leave his home in Wexford County, Ireland, in 1848, in hopes of finding a better
life in the US. Once he arrived in the US, he settled in East Boston, where he remained for the rest of his life.',0);
INSERT INTO "grampsdb_note" VALUES(38,'c38a114c16050f1ef2ec52aa5af','N0002','2012-07-31 08:09:42.133685','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxNjA1MGYxZWYyZWM1MmFhNWFmJwpWTjAwMDIKcDEKKGxwMgpWSm9lIHdhcyBh
IHBvb3Igc3R1ZGVudCwgYnV0IGdvb2QgYXQgYXRobGV0aWNzIGFuZCBoYWQgYW4gYXR0cmFjdGl2
ZSBwZXJzb25hbGl0eS4gSGUgd2FzIGFibGUgdG8gb3ZlcmNvbWUgbWFueSBldGhuaWMgYmFycmll
cnMgZHVyaW5nIGhpcyBzY2hvb2wgeWVhcnMgYXQgQm9zdG9uIExhdGluLCBhIHByb3Rlc3RhbnQg
YW5kIHByaW1hcmlseSBZYW5rZWUgc2Nob29sLgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApw
NQp0STAKKHRJMDAKdHA2Ci4=
',3,'Joe was a poor student, but good at athletics and had an attractive personality. He was able to overcome many ethnic barriers during his school years at Boston Latin, a protestant and primarily Yankee school.',0);
INSERT INTO "grampsdb_note" VALUES(39,'c38a114d61776a28eb96e09526b','N0049','2012-07-31 08:09:42.139101','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MTc3NmEyOGViOTZlMDk1MjZiJwpWTjAwNDkKcDEKKGxwMgpWSGUgaGFkIHBl
cnNvbmFsIGZpbmFuY2VzIHRoYXQgd2VyZSBlc3RpbWF0ZWQgdG8gYmUgYXJvdW5kICQxMCBtaWxs
aW9uIHdoaWxlIGluIHRoZSBQcmVzaWRlbmN5LgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApw
NQp0STAKKHRJMDAKdHA2Ci4=
',3,'He had personal finances that were estimated to be around $10 million while in the Presidency.',0);
INSERT INTO "grampsdb_note" VALUES(40,'c38a114d61a1548d359ae33c6f3','N0050','2012-07-31 08:09:42.144498','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MWExNTQ4ZDM1OWFlMzNjNmYzJwpWTjAwNTAKcDEKKGxwMgpWSGUgd2FzIGFz
c2Fzc2luYXRlZCBpbiBEYWxsYXMsIFRYLgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0
STAKKHRJMDAKdHA2Ci4=
',3,'He was assassinated in Dallas, TX.',0);
INSERT INTO "grampsdb_note" VALUES(41,'c38a114d65e9db2c85f475aae4','N0054','2012-07-31 08:09:42.150047','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NWU5ZGIyYzg1ZjQ3NWFhZTQnClZOMDA1NApwMQoobHAyClZXaGlsZSBkYXRp
bmcgSkZLLCBKYWNraWUgZGlkIG5vdCB3YW50IGhpbSB0byBrbm93IHRoYXQgc2hlIHdhcyBub3Qg
cmljaCBhbmQgdGhpbmsgdGhhdCBzaGUgd2FzIG9ubHkgbWFycnlpbmcgaGltIGZvciBoaXMgbW9u
ZXkuIFNvLCBzaGUgd2VudCB0byBncmVhdCBsZW5ndGhzIHRvIGFwcGVhciByaWNoLgpwMwphKGxw
NAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'While dating JFK, Jackie did not want him to know that she was not rich and think that she was only marrying him for his money. So, she went to great lengths to appear rich.',0);
INSERT INTO "grampsdb_note" VALUES(42,'c38a114d01a7c98ac57fae8a55d','N0013','2012-07-31 08:09:42.155470','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMWE3Yzk4YWM1N2ZhZThhNTVkJwpWTjAwMTMKcDEKKGxwMgpWSGUgd2FzIGtu
b3duIGFzIEphY2suCnAzCmEobHA0CmFJMDAKKEkxClZHZW5lcmFsCnA1CnRJMAoodEkwMAp0cDYK
Lg==
',3,'He was known as Jack.',0);
INSERT INTO "grampsdb_note" VALUES(43,'c38a114d096455520a4b2a3aec6','N0018','2012-07-31 08:09:42.160837','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwOTY0NTU1MjBhNGIyYTNhZWM2JwpWTjAwMTgKcDEKKGxwMgpWRGllZCBpbiBh
biBhaXJwbGFuZSBjcmFzaCB3aXRoIGhlciBsb3ZlciBpbiBGcmFuY2UgdGhyZWUgeWVhcnMgYWZ0
ZXIgaGVyIG9sZGVyIGJyb3RoZXIgSm9zZXBoJ3MgZGVhdGguCnAzCmEobHA0CmFJMDAKKEkxClZH
ZW5lcmFsCnA1CnRJMAoodEkwMAp0cDYKLg==
',3,'Died in an airplane crash with her lover in France three years after her older brother Joseph''s death.',0);
INSERT INTO "grampsdb_note" VALUES(44,'c38a114d27675467a7218bc6c30','N0027','2012-07-31 08:09:42.166358','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyNzY3NTQ2N2E3MjE4YmM2YzMwJwpWTjAwMjcKcDEKKGxwMgpWUm9iZXJ0IEZy
YW5jaXMgd2FzIGFzc2Fzc2luYXRlZCBpbiBDYWxpZm9ybmlhIGR1cmluZyBoaXMgMTk2OCBwcmVz
aWRlbnRpYWwgY2FtcGFpZ24uCnAzCmEobHA0CmFJMDAKKEkxClZHZW5lcmFsCnA1CnRJMAoodEkw
MAp0cDYKLg==
',3,'Robert Francis was assassinated in California during his 1968 presidential campaign.',0);
INSERT INTO "grampsdb_note" VALUES(45,'c38a114d8f62c15d94ace762cc7','N0071','2012-07-31 08:09:42.171073','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4ZjYyYzE1ZDk0YWNlNzYyY2M3JwpWTjAwNzEKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBUb3AgTGV2ZWw6XHUwMDBhXHUwMDBhTGluZSBpZ25vcmVkIGFzIG5v
dCB1bmRlcnN0b29kICAgICBMaW5lICAgNzIyOiAwIEM0IENTVEFcdTAwMGFTa2lwcGVkIHN1Ym9y
ZGluYXRlIGxpbmUgICAgICAgICAgIExpbmUgICA3MjM6IDEgTkFNRSBEdXBsaWNhdGVcdTAwMGEK
cDMKYShscDQKKChJMwpWZm9udGZhY2UKdFZNb25vc3BhY2UKKGxwNQooSTAKSTE1OQp0cDYKYXRw
NwphYUkwMAooSTAKVkdFRENPTSBpbXBvcnQKcDgKdEkwCih0STAwCnRwOQou
',27,'Records not imported into Top Level:

Line ignored as not understood     Line   722: 0 C4 CSTA
Skipped subordinate line           Line   723: 1 NAME Duplicate
',0);
INSERT INTO "grampsdb_note" VALUES(46,'c38a114d45450e26c8becdac4f1','N0030','2012-07-31 08:09:42.176562','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQ0NTQ1MGUyNmM4YmVjZGFjNGYxJwpWTjAwMzAKcDEKKGxwMgpWRW5saXN0ZWQg
aW4gdGhlIE5hdnkgZHVyaW5nIFdvcmxkIFdhciBJSS4KcDMKYShscDQKYUkwMAooSTEKVkdlbmVy
YWwKcDUKdEkwCih0STAwCnRwNgou
',3,'Enlisted in the Navy during World War II.',0);
INSERT INTO "grampsdb_note" VALUES(47,'c38a114d28d6ec62f89d6da7131','N0029','2012-07-31 08:09:42.182818','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQyOGQ2ZWM2MmY4OWQ2ZGE3MTMxJwpWTjAwMjkKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwMjE6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgMjM3OiAxIE5P
VEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkx
MTcKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0021:

Empty note ignored                 Line   237: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(48,'c38a114d05a36af13cb0cdf56a2','N0017','2012-07-31 08:09:42.189062','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwNWEzNmFmMTNjYjBjZGY1NmEyJwpWTjAwMTcKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwMDQ6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgIDk4OiAxIE5P
VEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkx
MTcKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0004:

Empty note ignored                 Line    98: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(49,'c38a114d12330fc7f405c29cae3','N0022','2012-07-31 08:09:42.194481','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxMjMzMGZjN2Y0MDVjMjljYWUzJwpWTjAwMjIKcDEKKGxwMgpWU2hlIGhlbHBl
ZCBpbiB0aGUgbWFueSBwb2xpdGljYWwgY2FtcGFpZ25zIG9mIGhlciBicm90aGVyLCBKb2huIEZp
dHpnZXJhbGQuCnAzCmEobHA0CmFJMDAKKEkxClZHZW5lcmFsCnA1CnRJMAoodEkwMAp0cDYKLg==
',3,'She helped in the many political campaigns of her brother, John Fitzgerald.',0);
INSERT INTO "grampsdb_note" VALUES(50,'c38a114d8a7f31d9ebd648525d','N0064','2012-07-31 08:09:42.200721','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4YTdmMzFkOWViZDY0ODUyNWQnClZOMDA2NApwMQoobHAyClZSZWNvcmRzIG5v
dCBpbXBvcnRlZCBpbnRvIFNPVVIgKHNvdXJjZSkgR3JhbXBzIElEIFMwMDA4Olx1MDAwYVx1MDAw
YUxpbmUgaWdub3JlZCBhcyBub3QgdW5kZXJzdG9vZCAgICAgTGluZSAgIDcwOTogMSBOQU1FIE5l
dyBZb3JrIFRpbWVzLCBOb3YuIDIyLCAxOTYzLlx1MDAwYQpwMwphKGxwNAooKEkzClZmb250ZmFj
ZQp0Vk1vbm9zcGFjZQoobHA1CihJMApJMTQzCnRwNgphdHA3CmFhSTAwCihJMApWR0VEQ09NIGlt
cG9ydApwOAp0STAKKHRJMDAKdHA5Ci4=
',27,'Records not imported into SOUR (source) Gramps ID S0008:

Line ignored as not understood     Line   709: 1 NAME New York Times, Nov. 22, 1963.
',0);
INSERT INTO "grampsdb_note" VALUES(51,'c38a114d4e257c21bee85ed6bd7','N0036','2012-07-31 08:09:42.206135','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZTI1N2MyMWJlZTg1ZWQ2YmQ3JwpWTjAwMzYKcDEKKGxwMgpWSGlzIHBlcnNv
bmFsaXR5IHdhcyBtaWxkLW1hbm5lcmVkLCBxdWlldCBhbmQgcmVzZXJ2ZWQsIGFuZCBoZSB3YXMg
dmlld2VkIGFzIGEgbWFuIG9mIG1vZGVyYXRlIGhhYml0cy4KcDMKYShscDQKYUkwMAooSTEKVkdl
bmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'His personality was mild-mannered, quiet and reserved, and he was viewed as a man of moderate habits.',0);
INSERT INTO "grampsdb_note" VALUES(52,'c38a114d62e740b6570946ad5c8','N0051','2012-07-31 08:09:42.212448','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MmU3NDBiNjU3MDk0NmFkNWM4JwpWTjAwNTEKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwNTI6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNTE4OiAxIE5P
VEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNTIwOiAx
IE5PVEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNTIy
OiAxIE5PVEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUK
KEkwCkkyMjcKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0
cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0052:

Empty note ignored                 Line   518: 1 NOTE 
Empty note ignored                 Line   520: 1 NOTE 
Empty note ignored                 Line   522: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(53,'c38a114d0ae6b3b3c2d5297da7c','N0020','2012-07-31 08:09:42.218729','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwYWU2YjNiM2MyZDUyOTdkYTdjJwpWTjAwMjAKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwMDY6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgMTIyOiAxIE5P
VEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkx
MTcKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0006:

Empty note ignored                 Line   122: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(54,'c38a114d4df1e92dc5c494c851c','N0035','2012-07-31 08:09:42.224156','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZGYxZTkyZGM1YzQ5NGM4NTFjJwpWTjAwMzUKcDEKKGxwMgpWUGF0cmljayBs
YXRlciBiZWNhbWUgYSB2ZXJ5IHN1Y2Nlc3NmdWwgYnVzaW5lc3NtYW4gZ2V0dGluZyBpbnRvIHdo
b2xlc2FsZSBsaXF1b3Igc2FsZXMsIG93bmluZyBhIGNvYWwgY29tcGFueSBhbmQgYmVjb21pbmcg
dGhlIHByZXNpZGVudCBvZiBhIGJhbmsuCnAzCmEobHA0CmFJMDAKKEkxClZHZW5lcmFsCnA1CnRJ
MAoodEkwMAp0cDYKLg==
',3,'Patrick later became a very successful businessman getting into wholesale liquor sales, owning a coal company and becoming the president of a bank.',0);
INSERT INTO "grampsdb_note" VALUES(55,'c38a114d6594a3e986ed049b509','N0052','2012-07-31 08:09:42.229609','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2NTk0YTNlOTg2ZWQwNDliNTA5JwpWTjAwNTIKcDEKKGxwMgpWPGltZyBzcmM9
Imh0dHA6Ly93d3cuamFjcXVlc2xvd2UuY29tL2h0bWwvcGhvdG9ncmFwaHMvamFja2llL2ltYWdl
cy9KYWNreTAxYncuanBnIiBib3JkZXI9MT4KcDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUK
dEkwCih0STAwCnRwNgou
',3,'<img src="http://www.jacqueslowe.com/html/photographs/jackie/images/Jacky01bw.jpg" border=1>',0);
INSERT INTO "grampsdb_note" VALUES(56,'c38a114d4db3389831e53a6a5e8','N0034','2012-07-31 08:09:42.235015','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZGIzMzg5ODMxZTUzYTZhNWU4JwpWTjAwMzQKcDEKKGxwMgpWUGF0cmljayB3
YXMgYWJsZSB0byB3b3JrIGhpcyB3YXkgZnJvbSBiZWluZyBhIFNhbG9vbktlZXBlciB0byBiZWNv
bWluZyBhIFdhcmQgQm9zcywgaGVscGluZyBvdXQgb3RoZXIgSXJpc2ggaW1taWdyYW50cy4gSGlz
IHBvcHVsYXJpdHkgIHJvc2UgYW5kIGF0IHRoZSBhZ2Ugb2YgdGhpcnR5IGhlIGhhZCBiZWNvbWUg
YSBwb3dlciBpbiBCb3N0b24gcG9saXRpY3MuIEluIDE4OTIgYW5kIDE4OTMgaGUgd2FzIGVsZWN0
ZWQgdG9cdTAwMGF0aGUgTWFzc2FjaHVzZXR0cyBTZW5hdGUuCnAzCmEobHA0CmFJMDAKKEkxClZH
ZW5lcmFsCnA1CnRJMAoodEkwMAp0cDYKLg==
',3,'Patrick was able to work his way from being a SaloonKeeper to becoming a Ward Boss, helping out other Irish immigrants. His popularity  rose and at the age of thirty he had become a power in Boston politics. In 1892 and 1893 he was elected to
the Massachusetts Senate.',0);
INSERT INTO "grampsdb_note" VALUES(57,'c38a114d047780a6d5f5134cde9','N0016','2012-07-31 08:09:42.240403','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQwNDc3ODBhNmQ1ZjUxMzRjZGU5JwpWTjAwMTYKcDEKKGxwMgpWSW4gMTk0NiBo
ZXIgZmF0aGVyIGdhdmUgJDYwMCwwMDAgZm9yIHRoZSBjb25zdHJ1Y3Rpb24gb2YgdGhlIEpvc2Vw
aCBQLiBLZW5uZWR5IEpyLiBDb252YWxlc2NlbnQgSG9tZSBmb3IgZGlzYWR2YW50YWdlZCBjaGls
ZHJlbiwgYmVjYXVzZSBvZiBSb3NlbWFyeSdzIGNvbmRpdGlvbi4KcDMKYShscDQKYUkwMAooSTEK
VkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'In 1946 her father gave $600,000 for the construction of the Joseph P. Kennedy Jr. Convalescent Home for disadvantaged children, because of Rosemary''s condition.',0);
INSERT INTO "grampsdb_note" VALUES(58,'c38a114d90e625739a3f8aa4fab','N0074','2012-07-31 08:09:42.245084','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ5MGU2MjU3MzlhM2Y4YWE0ZmFiJwpWTjAwNzQKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBUb3AgTGV2ZWw6XHUwMDBhXHUwMDBhTGluZSBpZ25vcmVkIGFzIG5v
dCB1bmRlcnN0b29kICAgICBMaW5lICAgNzI4OiAwIEM3IENTVEFcdTAwMGFTa2lwcGVkIHN1Ym9y
ZGluYXRlIGxpbmUgICAgICAgICAgIExpbmUgICA3Mjk6IDEgTkFNRSBBZG9wdGVkIFR3aW5cdTAw
MGEKcDMKYShscDQKKChJMwpWZm9udGZhY2UKdFZNb25vc3BhY2UKKGxwNQooSTAKSTE2Mgp0cDYK
YXRwNwphYUkwMAooSTAKVkdFRENPTSBpbXBvcnQKcDgKdEkwCih0STAwCnRwOQou
',27,'Records not imported into Top Level:

Line ignored as not understood     Line   728: 0 C7 CSTA
Skipped subordinate line           Line   729: 1 NAME Adopted Twin
',0);
INSERT INTO "grampsdb_note" VALUES(59,'c38a114d1f06d3405cb8854262b','N0026','2012-07-31 08:09:42.250664','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxZjA2ZDM0MDVjYjg4NTQyNjJiJwpWTjAwMjYKcDEKKGxwMgpWV2FzIGEgaGVs
cCB0byBoZXIgYnJvdGhlciBKb2huIEYuIGR1cmluZyBoaXMgcG9saXRpY2FsIGNhbXBhaWducy4K
cDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'Was a help to her brother John F. during his political campaigns.',0);
INSERT INTO "grampsdb_note" VALUES(60,'c38a114d12a4f4503565c6de829','N0024','2012-07-31 08:09:42.256068','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxMmE0ZjQ1MDM1NjVjNmRlODI5JwpWTjAwMjQKcDEKKGxwMgpWQWZ0ZXIgaGVy
IG1vdGhlciwgRXVuaWNlIHdhcyBjb25zaWRlcmVkIHRoZSBmYW1pbHkncyBtb2RlbCB3b21hbi4K
cDMKYShscDQKYUkwMAooSTEKVkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'After her mother, Eunice was considered the family''s model woman.',0);
INSERT INTO "grampsdb_note" VALUES(61,'c38a114d60f4a0e3dae26349669','N0046','2012-07-31 08:09:42.261489','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ2MGY0YTBlM2RhZTI2MzQ5NjY5JwpWTjAwNDYKcDEKKGxwMgpWPGltZyBzcmM9
Imh0dHA6Ly93d3cuamFjcXVlc2xvd2UuY29tL2h0bWwvcGhvdG9ncmFwaHMvamZrL2ltYWdlcy9q
ZmtwNTJidy5qcGciIGJvcmRlcj0xPgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAK
KHRJMDAKdHA2Ci4=
',3,'<img src="http://www.jacqueslowe.com/html/photographs/jfk/images/jfkp52bw.jpg" border=1>',0);
INSERT INTO "grampsdb_note" VALUES(62,'c38a114d8397e9559f0928ade71','N0057','2012-07-31 08:09:42.267763','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4Mzk3ZTk1NTlmMDkyOGFkZTcxJwpWTjAwNTcKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAwMTpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA2OTU6IDEgTkFNRSBK
b3NlcGggUC4gS2VubmVkeSwgQSBMaWZlIGFuZCBUaW1lcywgYnkgRGF2aWQgRS4gS29za29mZi5c
dTAwMGEKcDMKYShscDQKKChJMwpWZm9udGZhY2UKdFZNb25vc3BhY2UKKGxwNQooSTAKSTE3MAp0
cDYKYXRwNwphYUkwMAooSTAKVkdFRENPTSBpbXBvcnQKcDgKdEkwCih0STAwCnRwOQou
',27,'Records not imported into SOUR (source) Gramps ID S0001:

Line ignored as not understood     Line   695: 1 NAME Joseph P. Kennedy, A Life and Times, by David E. Koskoff.
',0);
INSERT INTO "grampsdb_note" VALUES(63,'c38a114c1537f3b0539111c8863','N0001','2012-07-31 08:09:42.273311','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxNTM3ZjNiMDUzOTExMWM4ODYzJwpWTjAwMDEKcDEKKGxwMgpWSGUgaGFkIGFu
IGludGVyZXN0aW5nIGhvYmJ5IG9mIHRpbmtlcmluZyB3aXRoIGNsb2Nrcy4KcDMKYShscDQKYUkw
MAooSTEKVkdlbmVyYWwKcDUKdEkwCih0STAwCnRwNgou
',3,'He had an interesting hobby of tinkering with clocks.',0);
INSERT INTO "grampsdb_note" VALUES(64,'c38a114c17564265744c0ccbf3a','N0004','2012-07-31 08:09:42.278748','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxNzU2NDI2NTc0NGMwY2NiZjNhJwpWTjAwMDQKcDEKKGxwMgpWSGUgd2FzIGZp
ZXJjZWx5IHByb3VkIG9mIGhpcyBmYW1pbHkuIEhlIHdhcyBxdW90ZWQgYXMgaGF2aW5nIHNhaWQg
aGlzIGZhbWlseSB3YXMgdGhlIGZpbmVzdCB0aGluZyBpbiBoaXMgbGlmZS4gCnAzCmEobHA0CmFJ
MDAKKEkxClZHZW5lcmFsCnA1CnRJMAoodEkwMAp0cDYKLg==
',3,'He was fiercely proud of his family. He was quoted as having said his family was the finest thing in his life. ',0);
INSERT INTO "grampsdb_note" VALUES(65,'c38a114d4f62077bad3f0c898cb','N0037','2012-07-31 08:09:42.285016','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ0ZjYyMDc3YmFkM2YwYzg5OGNiJwpWTjAwMzcKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwNDQ6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNDAyOiAxIE5P
VEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNDA1OiAx
IE5PVEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgNDA3
OiAxIE5PVEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUK
KEkwCkkyMjcKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0
cDkKLg==
',27,'Records not imported into INDI (individual) Gramps ID I0044:

Empty note ignored                 Line   402: 1 NOTE 
Empty note ignored                 Line   405: 1 NOTE 
Empty note ignored                 Line   407: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(66,'c38a114d8671340b71083d4fa55','N0060','2012-07-31 08:09:42.291272','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4NjcxMzQwYjcxMDgzZDRmYTU1JwpWTjAwNjAKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAwNDpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA3MDE6IDEgTkFNRSBO
ZXcgWW9yayBUaW1lcywgTWFyY2ggNiwgMTk0Ni5cdTAwMGEKcDMKYShscDQKKChJMwpWZm9udGZh
Y2UKdFZNb25vc3BhY2UKKGxwNQooSTAKSTE0Mwp0cDYKYXRwNwphYUkwMAooSTAKVkdFRENPTSBp
bXBvcnQKcDgKdEkwCih0STAwCnRwOQou
',27,'Records not imported into SOUR (source) Gramps ID S0004:

Line ignored as not understood     Line   701: 1 NAME New York Times, March 6, 1946.
',0);
INSERT INTO "grampsdb_note" VALUES(67,'c38a114d8483c724c9a87667a1c','N0058','2012-07-31 08:09:42.297549','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4NDgzYzcyNGM5YTg3NjY3YTFjJwpWTjAwNTgKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAwMjpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA2OTc6IDEgTkFNRSBS
b3NlLCBieSBHYWlsIENhbWVyb24uXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9u
b3NwYWNlCihscDUKKEkwCkkxMzUKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4
CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into SOUR (source) Gramps ID S0002:

Line ignored as not understood     Line   697: 1 NAME Rose, by Gail Cameron.
',0);
INSERT INTO "grampsdb_note" VALUES(68,'c38a114d8dc21cee5fd07fbb7c0','N0068','2012-07-31 08:09:42.302243','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4ZGMyMWNlZTVmZDA3ZmJiN2MwJwpWTjAwNjgKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBUb3AgTGV2ZWw6XHUwMDBhXHUwMDBhTGluZSBpZ25vcmVkIGFzIG5v
dCB1bmRlcnN0b29kICAgICBMaW5lICAgNzE2OiAwIEMxIENTVEFcdTAwMGFTa2lwcGVkIHN1Ym9y
ZGluYXRlIGxpbmUgICAgICAgICAgIExpbmUgICA3MTc6IDEgTkFNRSBUd2luXHUwMDBhCnAzCmEo
bHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkxNTQKdHA2CmF0cDcKYWFJ
MDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into Top Level:

Line ignored as not understood     Line   716: 0 C1 CSTA
Skipped subordinate line           Line   717: 1 NAME Twin
',0);
INSERT INTO "grampsdb_note" VALUES(69,'c38a114d13f56acdf67304b8731','N0025','2012-07-31 08:09:42.308537','1969-12-31 19:00:00',NULL,0,0,'KFMnYzM4YTExNGQxM2Y1NmFjZGY2NzMwNGI4NzMxJwpWTjAwMjUKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBJTkRJIChpbmRpdmlkdWFsKSBHcmFtcHMgSUQgSTAwMDg6XHUwMDBh
XHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgMTQ2OiAxIE5P
VEUgXHUwMDBhRW1wdHkgbm90ZSBpZ25vcmVkICAgICAgICAgICAgICAgICBMaW5lICAgMTQ4OiAx
IE5PVEUgXHUwMDBhCnAzCmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkw
CkkxNzIKdHA2CmF0cDcKYWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkK
Lg==
',27,'Records not imported into INDI (individual) Gramps ID I0008:

Empty note ignored                 Line   146: 1 NOTE 
Empty note ignored                 Line   148: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(70,'c38a114d858323fcf2fdd0e07b','N0059','2012-07-31 08:09:42.314956','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4NTgzMjNmY2YyZmRkMGUwN2InClZOMDA1OQpwMQoobHAyClZSZWNvcmRzIG5v
dCBpbXBvcnRlZCBpbnRvIFNPVVIgKHNvdXJjZSkgR3JhbXBzIElEIFMwMDAzOlx1MDAwYVx1MDAw
YUxpbmUgaWdub3JlZCBhcyBub3QgdW5kZXJzdG9vZCAgICAgTGluZSAgIDY5OTogMSBOQU1FIE5l
dyBZb3JrIFRpbWVzLCBNYXJjaCA0LCAxOTQ2LCBwcC4gMSwzLlx1MDAwYQpwMwphKGxwNAooKEkz
ClZmb250ZmFjZQp0Vk1vbm9zcGFjZQoobHA1CihJMApJMTUyCnRwNgphdHA3CmFhSTAwCihJMApW
R0VEQ09NIGltcG9ydApwOAp0STAKKHRJMDAKdHA5Ci4=
',27,'Records not imported into SOUR (source) Gramps ID S0003:

Line ignored as not understood     Line   699: 1 NAME New York Times, March 4, 1946, pp. 1,3.
',0);
INSERT INTO "grampsdb_note" VALUES(71,'c38a114d01455d5e13b0df75231','N0011','2012-07-31 08:09:42.320453','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQwMTQ1NWQ1ZTEzYjBkZjc1MjMxJwpWTjAwMTEKcDEKKGxwMgpWSm9zZXBoIFBh
dHJpY2sgd2FzIHdlbGwgbGlrZWQsIHF1aWNrIHRvIHNtaWxlLCBhbmQgaGFkIGEgdHJlbWVuZG91
cyBkb3NlIG9mIElyaXNoIGNoYXJtLgpwMwphKGxwNAphSTAwCihJMQpWR2VuZXJhbApwNQp0STAK
KHRJMDAKdHA2Ci4=
',3,'Joseph Patrick was well liked, quick to smile, and had a tremendous dose of Irish charm.',0);
INSERT INTO "grampsdb_note" VALUES(72,'c38a114d8891f9e3fd99c9f31b9','N0062','2012-07-31 08:09:42.326863','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4ODkxZjllM2ZkOTljOWYzMWI5JwpWTjAwNjIKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBTT1VSIChzb3VyY2UpIEdyYW1wcyBJRCBTMDAwNjpcdTAwMGFcdTAw
MGFMaW5lIGlnbm9yZWQgYXMgbm90IHVuZGVyc3Rvb2QgICAgIExpbmUgICA3MDU6IDEgTkFNRSBU
aGUgS2VubmVkeXMgRHluYXN0eSBhbmQgRGlzYXN0ZXIgMTg0OC0xOTgzLCBieSBKb2huIEguIERh
dmlzLlx1MDAwYQpwMwphKGxwNAooKEkzClZmb250ZmFjZQp0Vk1vbm9zcGFjZQoobHA1CihJMApJ
MTc1CnRwNgphdHA3CmFhSTAwCihJMApWR0VEQ09NIGltcG9ydApwOAp0STAKKHRJMDAKdHA5Ci4=
',27,'Records not imported into SOUR (source) Gramps ID S0006:

Line ignored as not understood     Line   705: 1 NAME The Kennedys Dynasty and Disaster 1848-1983, by John H. Davis.
',0);
INSERT INTO "grampsdb_note" VALUES(73,'c38a114d53946918ffd66db1b7','N0040','2012-07-31 08:09:42.333182','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ1Mzk0NjkxOGZmZDY2ZGIxYjcnClZOMDA0MApwMQoobHAyClZSZWNvcmRzIG5v
dCBpbXBvcnRlZCBpbnRvIElOREkgKGluZGl2aWR1YWwpIEdyYW1wcyBJRCBJMDA0NjpcdTAwMGFc
dTAwMGFFbXB0eSBub3RlIGlnbm9yZWQgICAgICAgICAgICAgICAgIExpbmUgICA0Mzg6IDEgTk9U
RSBcdTAwMGEKcDMKYShscDQKKChJMwpWZm9udGZhY2UKdFZNb25vc3BhY2UKKGxwNQooSTAKSTEx
Nwp0cDYKYXRwNwphYUkwMAooSTAKVkdFRENPTSBpbXBvcnQKcDgKdEkwCih0STAwCnRwOQou
',27,'Records not imported into INDI (individual) Gramps ID I0046:

Empty note ignored                 Line   438: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(74,'c38a114c16a4c26582ec898bbe3','N0003','2012-07-31 08:09:42.338761','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGMxNmE0YzI2NTgyZWM4OThiYmUzJwpWTjAwMDMKcDEKKGxwMgpWV2FzIG9uZSBv
ZiB0aGUgeW91bmdlc3QgQmFuayBQcmVzaWRlbnRzIGluIFVTIGhpc3RvcnkuIApwMwphKGxwNAph
STAwCihJMQpWR2VuZXJhbApwNQp0STAKKHRJMDAKdHA2Ci4=
',3,'Was one of the youngest Bank Presidents in US history. ',0);
INSERT INTO "grampsdb_note" VALUES(75,'c38a114d8e4789ce3a989567cd9','N0069','2012-07-31 08:09:42.343485','1969-12-31 19:00:00',NULL,0,1,'KFMnYzM4YTExNGQ4ZTQ3ODljZTNhOTg5NTY3Y2Q5JwpWTjAwNjkKcDEKKGxwMgpWUmVjb3JkcyBu
b3QgaW1wb3J0ZWQgaW50byBUb3AgTGV2ZWw6XHUwMDBhXHUwMDBhTGluZSBpZ25vcmVkIGFzIG5v
dCB1bmRlcnN0b29kICAgICBMaW5lICAgNzE4OiAwIEMyIENTVEFcdTAwMGFTa2lwcGVkIHN1Ym9y
ZGluYXRlIGxpbmUgICAgICAgICAgIExpbmUgICA3MTk6IDEgTkFNRSBBZG9wdGVkXHUwMDBhCnAz
CmEobHA0CigoSTMKVmZvbnRmYWNlCnRWTW9ub3NwYWNlCihscDUKKEkwCkkxNTcKdHA2CmF0cDcK
YWFJMDAKKEkwClZHRURDT00gaW1wb3J0CnA4CnRJMAoodEkwMAp0cDkKLg==
',27,'Records not imported into Top Level:

Line ignored as not understood     Line   718: 0 C2 CSTA
Skipped subordinate line           Line   719: 1 NAME Adopted
',0);
CREATE TABLE "grampsdb_surname" (
    "id" integer NOT NULL PRIMARY KEY,
    "name_origin_type_id" integer NOT NULL REFERENCES "grampsdb_nameorigintype" ("id"),
    "surname" text NOT NULL,
    "prefix" text NOT NULL,
    "primary" bool NOT NULL,
    "connector" text NOT NULL,
    "name_id" integer NOT NULL,
    "order" integer unsigned NOT NULL
);
INSERT INTO "grampsdb_surname" VALUES(1,1,'SHRIVER','',1,'',1,1);
INSERT INTO "grampsdb_surname" VALUES(2,1,'BURKE','',1,'',2,1);
INSERT INTO "grampsdb_surname" VALUES(3,1,'KENNEDY','',1,'',3,1);
INSERT INTO "grampsdb_surname" VALUES(4,1,'KENNEDY','',1,'',4,1);
INSERT INTO "grampsdb_surname" VALUES(5,1,'KENNEDY','',1,'',5,1);
INSERT INTO "grampsdb_surname" VALUES(6,1,'SMITH','',1,'',6,1);
INSERT INTO "grampsdb_surname" VALUES(7,1,'KENNEDY','',1,'',7,1);
INSERT INTO "grampsdb_surname" VALUES(8,1,'KENNEDY','',1,'',8,1);
INSERT INTO "grampsdb_surname" VALUES(9,1,'KENNEDY','',1,'',9,1);
INSERT INTO "grampsdb_surname" VALUES(10,1,'KENNEDY','',1,'',10,1);
INSERT INTO "grampsdb_surname" VALUES(11,1,'KENNEDY','',1,'',11,1);
INSERT INTO "grampsdb_surname" VALUES(12,1,'KENNEDY','',1,'',12,1);
INSERT INTO "grampsdb_surname" VALUES(13,1,'SHRIVER','',1,'',13,1);
INSERT INTO "grampsdb_surname" VALUES(14,1,'KENNEDY','',1,'',14,1);
INSERT INTO "grampsdb_surname" VALUES(15,1,'KENNEDY','',1,'',15,1);
INSERT INTO "grampsdb_surname" VALUES(16,1,'HICKEY','',1,'',16,1);
INSERT INTO "grampsdb_surname" VALUES(17,1,'KENNEDY','',1,'',17,1);
INSERT INTO "grampsdb_surname" VALUES(18,1,'FITZGERALD','',1,'',18,1);
INSERT INTO "grampsdb_surname" VALUES(19,1,'KENNEDY','',1,'',19,1);
INSERT INTO "grampsdb_surname" VALUES(20,1,'SHRIVER','',1,'',20,1);
INSERT INTO "grampsdb_surname" VALUES(21,1,'KENNEDY','',1,'',21,1);
INSERT INTO "grampsdb_surname" VALUES(22,1,'KENNEDY','',1,'',22,1);
INSERT INTO "grampsdb_surname" VALUES(23,1,'LAWFORD','',1,'',23,1);
INSERT INTO "grampsdb_surname" VALUES(24,1,'LAWFORD','',1,'',24,1);
INSERT INTO "grampsdb_surname" VALUES(25,1,'KENNEDY','',1,'',25,1);
INSERT INTO "grampsdb_surname" VALUES(26,1,'HANNON','',1,'',26,1);
INSERT INTO "grampsdb_surname" VALUES(27,1,'MURPHY','',1,'',27,1);
INSERT INTO "grampsdb_surname" VALUES(28,1,'SMITH','',1,'',28,1);
INSERT INTO "grampsdb_surname" VALUES(29,1,'KENNEDY','',1,'',29,1);
INSERT INTO "grampsdb_surname" VALUES(30,1,'KENNEDY','',1,'',30,1);
INSERT INTO "grampsdb_surname" VALUES(31,1,'SHRIVER','',1,'',31,1);
INSERT INTO "grampsdb_surname" VALUES(32,1,'SKAKEL','',1,'',32,1);
INSERT INTO "grampsdb_surname" VALUES(33,1,'KENNEDY','',1,'',33,1);
INSERT INTO "grampsdb_surname" VALUES(34,1,'LAWFORD','',1,'',34,1);
INSERT INTO "grampsdb_surname" VALUES(35,1,'KENNEDY','',1,'',35,1);
INSERT INTO "grampsdb_surname" VALUES(36,1,'KENNEDY','',1,'',36,1);
INSERT INTO "grampsdb_surname" VALUES(37,1,'KENNEDY','',1,'',37,1);
INSERT INTO "grampsdb_surname" VALUES(38,1,'KENNEDY','',1,'',38,1);
INSERT INTO "grampsdb_surname" VALUES(39,1,'BENNETT','',1,'',39,1);
INSERT INTO "grampsdb_surname" VALUES(40,1,'SHRIVER','',1,'',40,1);
INSERT INTO "grampsdb_surname" VALUES(41,1,'KENNEDY','',1,'',41,1);
INSERT INTO "grampsdb_surname" VALUES(42,1,'FITZGERALD','',1,'',42,1);
INSERT INTO "grampsdb_surname" VALUES(43,1,'KENNEDY','',1,'',43,1);
INSERT INTO "grampsdb_surname" VALUES(44,1,'CAULFIELD','',1,'',44,1);
INSERT INTO "grampsdb_surname" VALUES(45,1,'KENNEDY','',1,'',45,1);
INSERT INTO "grampsdb_surname" VALUES(46,1,'LAWFORD','',1,'',46,1);
INSERT INTO "grampsdb_surname" VALUES(47,1,'KENNEDY','',1,'',47,1);
INSERT INTO "grampsdb_surname" VALUES(48,1,'KANE','',1,'',48,1);
INSERT INTO "grampsdb_surname" VALUES(49,1,'KENNEDY','',1,'',49,1);
INSERT INTO "grampsdb_surname" VALUES(50,1,'KENNEDY','',1,'',50,1);
INSERT INTO "grampsdb_surname" VALUES(51,1,'SMITH','',1,'',51,1);
INSERT INTO "grampsdb_surname" VALUES(52,1,'KENNEDY','',1,'',52,1);
INSERT INTO "grampsdb_surname" VALUES(53,1,'CAVENDISH','',1,'',53,1);
INSERT INTO "grampsdb_surname" VALUES(54,1,'BOUVIER','',1,'',54,1);
INSERT INTO "grampsdb_surname" VALUES(55,1,'ACHINCLOSS','',1,'',55,1);
INSERT INTO "grampsdb_surname" VALUES(56,1,'LAWFORD','',1,'',56,1);
INSERT INTO "grampsdb_surname" VALUES(57,1,'KENNEDY','',1,'',57,1);
INSERT INTO "grampsdb_surname" VALUES(58,1,'MAHONEY','',1,'',58,1);
INSERT INTO "grampsdb_surname" VALUES(59,1,'BOUVIER','',1,'',59,1);
INSERT INTO "grampsdb_surname" VALUES(60,1,'SCHWARZENEGGER','',1,'',60,1);
INSERT INTO "grampsdb_surname" VALUES(61,1,'ONASSIS','',1,'',61,1);
INSERT INTO "grampsdb_surname" VALUES(62,1,'SMITH','',1,'',62,1);
INSERT INTO "grampsdb_surname" VALUES(63,1,'KENNEDY','',1,'',63,1);
INSERT INTO "grampsdb_surname" VALUES(64,1,'LEE','',1,'',64,1);
INSERT INTO "grampsdb_surname" VALUES(65,1,'KENNEDY','',1,'',65,1);
INSERT INTO "grampsdb_surname" VALUES(66,1,'BOUVIER','',1,'',66,1);
INSERT INTO "grampsdb_surname" VALUES(67,1,'KENNEDY','',1,'',67,1);
INSERT INTO "grampsdb_surname" VALUES(68,1,'SHRIVER','',1,'',68,1);
INSERT INTO "grampsdb_surname" VALUES(69,1,'KENNEDY','',1,'',69,1);
CREATE TABLE "grampsdb_name" (
    "id" integer NOT NULL PRIMARY KEY,
    "calendar" integer NOT NULL,
    "modifier" integer NOT NULL,
    "quality" integer NOT NULL,
    "day1" integer NOT NULL,
    "month1" integer NOT NULL,
    "year1" integer NOT NULL,
    "slash1" bool NOT NULL,
    "day2" integer,
    "month2" integer,
    "year2" integer,
    "slash2" bool,
    "text" varchar(80) NOT NULL,
    "sortval" integer NOT NULL,
    "newyear" integer NOT NULL,
    "private" bool NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "order" integer unsigned NOT NULL,
    "name_type_id" integer NOT NULL REFERENCES "grampsdb_nametype" ("id"),
    "preferred" bool NOT NULL,
    "first_name" text NOT NULL,
    "suffix" text NOT NULL,
    "title" text NOT NULL,
    "call" text NOT NULL,
    "nick" text NOT NULL,
    "famnick" text NOT NULL,
    "group_as" text NOT NULL,
    "sort_as_id" integer NOT NULL REFERENCES "grampsdb_nameformattype" ("id"),
    "display_as_id" integer NOT NULL REFERENCES "grampsdb_nameformattype" ("id"),
    "person_id" integer NOT NULL REFERENCES "grampsdb_person" ("id")
);
INSERT INTO "grampsdb_name" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:20.840181',NULL,NULL,1,4,1,'Mark Kennedy','','','','','','',1,1,1);
INSERT INTO "grampsdb_name" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:20.889389',NULL,NULL,1,4,1,'Charles','','','','','','',1,1,2);
INSERT INTO "grampsdb_name" VALUES(3,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:20.920359',NULL,NULL,1,4,1,'John Fitzgerald','','','','','','',1,1,3);
INSERT INTO "grampsdb_name" VALUES(4,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:20.994741',NULL,NULL,1,4,1,'Patrick Joseph','','','','','','',1,1,4);
INSERT INTO "grampsdb_name" VALUES(5,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.091621',NULL,NULL,1,4,1,'Johanna','','','','','','',1,1,5);
INSERT INTO "grampsdb_name" VALUES(6,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.127404',NULL,NULL,1,4,1,'William Kennedy','','','','','','',1,1,6);
INSERT INTO "grampsdb_name" VALUES(7,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.180992',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,7);
INSERT INTO "grampsdb_name" VALUES(8,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.293480',NULL,NULL,1,4,1,'Patricia','','','','','','',1,1,8);
INSERT INTO "grampsdb_name" VALUES(9,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.324719',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,9);
INSERT INTO "grampsdb_name" VALUES(10,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.396005',NULL,NULL,1,4,1,'Patrick','','','','','','',1,1,10);
INSERT INTO "grampsdb_name" VALUES(11,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.472323',NULL,NULL,1,4,1,'Patrick Bouvier','','','','','','',1,1,11);
INSERT INTO "grampsdb_name" VALUES(12,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.515828',NULL,NULL,1,4,1,'Rory Elizabeth','','','','','','',1,1,12);
INSERT INTO "grampsdb_name" VALUES(13,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.563659',NULL,NULL,1,4,1,'Robert Sargent','','','','','','',1,1,13);
INSERT INTO "grampsdb_name" VALUES(14,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.621340',NULL,NULL,1,4,1,'Mary Courtney','','','','','','',1,1,14);
INSERT INTO "grampsdb_name" VALUES(15,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.700361',NULL,NULL,1,4,1,'Douglas Harriman','','','','','','',1,1,15);
INSERT INTO "grampsdb_name" VALUES(16,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.728949',NULL,NULL,1,4,1,'Mary Augusta','','','','','','',1,1,16);
INSERT INTO "grampsdb_name" VALUES(17,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.763620',NULL,NULL,1,4,1,'Loretta','','','','','','',1,1,17);
INSERT INTO "grampsdb_name" VALUES(18,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.786785',NULL,NULL,1,4,1,'John F.','','','','','','',1,1,18);
INSERT INTO "grampsdb_name" VALUES(19,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.823376',NULL,NULL,1,4,1,'Kara Ann','','','','','','',1,1,19);
INSERT INTO "grampsdb_name" VALUES(20,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.846127',NULL,NULL,1,4,1,'Robert Sargent','','','','','','',1,1,20);
INSERT INTO "grampsdb_name" VALUES(21,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.897536',NULL,NULL,1,4,1,'Michael L.','','','','','','',1,1,21);
INSERT INTO "grampsdb_name" VALUES(22,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.931951',NULL,NULL,1,4,1,'Caroline Bouvier','','','','','','',1,1,22);
INSERT INTO "grampsdb_name" VALUES(23,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:21.990912',NULL,NULL,1,4,1,'Robin','','','','','','',1,1,23);
INSERT INTO "grampsdb_name" VALUES(24,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.012498',NULL,NULL,1,4,1,'Sydney','','','','','','',1,1,24);
INSERT INTO "grampsdb_name" VALUES(25,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.026555',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,25);
INSERT INTO "grampsdb_name" VALUES(26,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.049680',NULL,NULL,1,4,1,'Josephine Mary','','','','','','',1,1,26);
INSERT INTO "grampsdb_name" VALUES(27,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.069036',NULL,NULL,1,4,1,'Bridget','','','','','','',1,1,27);
INSERT INTO "grampsdb_name" VALUES(28,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.141370',NULL,NULL,1,4,1,'Stephen','','','','','','',1,1,28);
INSERT INTO "grampsdb_name" VALUES(29,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.168739',NULL,NULL,1,4,1,'Robert Francis','','','','','','',1,1,29);
INSERT INTO "grampsdb_name" VALUES(30,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.234026',NULL,NULL,1,4,1,'Matthew Maxwell Taylor','','','','','','',1,1,30);
INSERT INTO "grampsdb_name" VALUES(31,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.320217',NULL,NULL,1,4,1,'Timothy','','','','','','',1,1,31);
INSERT INTO "grampsdb_name" VALUES(32,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.334333',NULL,NULL,1,4,1,'Ethel','','','','','','',1,1,32);
INSERT INTO "grampsdb_name" VALUES(33,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.360239',NULL,NULL,1,4,1,'Mary','','','','','','',1,1,33);
INSERT INTO "grampsdb_name" VALUES(34,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.395081',NULL,NULL,1,4,1,'Peter','','','','','','',1,1,34);
INSERT INTO "grampsdb_name" VALUES(35,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.438805',NULL,NULL,1,4,1,'Jean Ann','','','','','','',1,1,35);
INSERT INTO "grampsdb_name" VALUES(36,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.476864',NULL,NULL,1,4,1,'Margaret','','','','','','',1,1,36);
INSERT INTO "grampsdb_name" VALUES(37,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.518579',NULL,NULL,1,4,1,'Edward More','','','','','','',1,1,37);
INSERT INTO "grampsdb_name" VALUES(38,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.635355',NULL,NULL,1,4,1,'John Fitzgerald','','','','','','',1,1,38);
INSERT INTO "grampsdb_name" VALUES(39,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.714850',NULL,NULL,1,4,1,'Virginia Joan','','','','','','',1,1,39);
INSERT INTO "grampsdb_name" VALUES(40,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.754599',NULL,NULL,1,4,1,'Anthony Paul','','','','','','',1,1,40);
INSERT INTO "grampsdb_name" VALUES(41,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.815831',NULL,NULL,1,4,1,'Patrick Joseph','','','','','','',1,1,41);
INSERT INTO "grampsdb_name" VALUES(42,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.846814',NULL,NULL,1,4,1,'Rose','','','','','','',1,1,42);
INSERT INTO "grampsdb_name" VALUES(43,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:22.921134',NULL,NULL,1,4,1,'Eunice Mary','','','','','','',1,1,43);
INSERT INTO "grampsdb_name" VALUES(44,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.019652',NULL,NULL,1,4,1,'John T.','','','','','','',1,1,44);
INSERT INTO "grampsdb_name" VALUES(45,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.043712',NULL,NULL,1,4,1,'David Anthony','','','','','','',1,1,45);
INSERT INTO "grampsdb_name" VALUES(46,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.092705',NULL,NULL,1,4,1,'Victoria','','','','','','',1,1,46);
INSERT INTO "grampsdb_name" VALUES(47,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.165616',NULL,NULL,1,4,1,'Rosemary','','','','','','',1,1,47);
INSERT INTO "grampsdb_name" VALUES(48,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.202902',NULL,NULL,1,4,1,'Laurence','','','','','','',1,1,48);
INSERT INTO "grampsdb_name" VALUES(49,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.228272',NULL,NULL,1,4,1,'Kathleen','','','','','','',1,1,49);
INSERT INTO "grampsdb_name" VALUES(50,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.279568',NULL,NULL,1,4,1,'Christopher George','','','','','','',1,1,50);
INSERT INTO "grampsdb_name" VALUES(51,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.392887',NULL,NULL,1,4,1,'Amanda','','','','','','',1,1,51);
INSERT INTO "grampsdb_name" VALUES(52,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.418008',NULL,NULL,1,4,1,'John','','','','','','',1,1,52);
INSERT INTO "grampsdb_name" VALUES(53,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.478939',NULL,NULL,1,4,1,'William John Robert','','','','','','',1,1,53);
INSERT INTO "grampsdb_name" VALUES(54,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.530953',NULL,NULL,1,4,1,'Jacqueline','','','','','','',1,1,54);
INSERT INTO "grampsdb_name" VALUES(55,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.621547',NULL,NULL,1,4,1,'Hugh','','','','','','',1,1,55);
INSERT INTO "grampsdb_name" VALUES(56,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.673216',NULL,NULL,1,4,1,'Christopher','','','','','','',1,1,56);
INSERT INTO "grampsdb_name" VALUES(57,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.724221',NULL,NULL,1,4,1,'Mary Kerry','','','','','','',1,1,57);
INSERT INTO "grampsdb_name" VALUES(58,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.753147',NULL,NULL,1,4,1,'Humphrey','','','','','','',1,1,58);
INSERT INTO "grampsdb_name" VALUES(59,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.779103',NULL,NULL,1,4,1,'John Vernou','','','','','','',1,1,59);
INSERT INTO "grampsdb_name" VALUES(60,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.846017',NULL,NULL,1,4,1,'Arnold','','','','','','',1,1,60);
INSERT INTO "grampsdb_name" VALUES(61,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.866330',NULL,NULL,1,4,1,'Aristotle','','','','','','',1,1,61);
INSERT INTO "grampsdb_name" VALUES(62,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.887716',NULL,NULL,1,4,1,'Stephen Edward','','','','','','',1,1,62);
INSERT INTO "grampsdb_name" VALUES(63,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.959502',NULL,NULL,1,4,1,'Kathleen Hartington','','','','','','',1,1,63);
INSERT INTO "grampsdb_name" VALUES(64,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:23.985024',NULL,NULL,1,4,1,'Janet','','','','','','',1,1,64);
INSERT INTO "grampsdb_name" VALUES(65,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:24.024482',NULL,NULL,1,4,1,'Edward Moore','','','','','','',1,1,65);
INSERT INTO "grampsdb_name" VALUES(66,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:24.125775',NULL,NULL,1,4,1,'Lee','','','','','','',1,1,66);
INSERT INTO "grampsdb_name" VALUES(67,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:24.140274',NULL,NULL,1,4,1,'Robert Francis','','','','','','',1,1,67);
INSERT INTO "grampsdb_name" VALUES(68,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:24.173415',NULL,NULL,1,4,1,'Maria','','','','','','',1,1,68);
INSERT INTO "grampsdb_name" VALUES(69,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-07-31 08:00:24.206322',NULL,NULL,1,4,1,'Margaret','','','','','','',1,1,69);
CREATE TABLE "grampsdb_lds" (
    "id" integer NOT NULL PRIMARY KEY,
    "calendar" integer NOT NULL,
    "modifier" integer NOT NULL,
    "quality" integer NOT NULL,
    "day1" integer NOT NULL,
    "month1" integer NOT NULL,
    "year1" integer NOT NULL,
    "slash1" bool NOT NULL,
    "day2" integer,
    "month2" integer,
    "year2" integer,
    "slash2" bool,
    "text" varchar(80) NOT NULL,
    "sortval" integer NOT NULL,
    "newyear" integer NOT NULL,
    "private" bool NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "order" integer unsigned NOT NULL,
    "lds_type_id" integer NOT NULL REFERENCES "grampsdb_ldstype" ("id"),
    "place_id" integer REFERENCES "grampsdb_place" ("id"),
    "famc_id" integer REFERENCES "grampsdb_family" ("id"),
    "temple" text NOT NULL,
    "status_id" integer NOT NULL REFERENCES "grampsdb_ldsstatus" ("id"),
    "person_id" integer REFERENCES "grampsdb_person" ("id"),
    "family_id" integer REFERENCES "grampsdb_family" ("id")
);
CREATE TABLE "grampsdb_markup" (
    "id" integer NOT NULL PRIMARY KEY,
    "note_id" integer NOT NULL REFERENCES "grampsdb_note" ("id"),
    "styled_text_tag_type_id" integer NOT NULL REFERENCES "grampsdb_styledtexttagtype" ("id"),
    "order" integer unsigned NOT NULL,
    "string" text,
    "start_stop_list" text NOT NULL
);
INSERT INTO "grampsdb_markup" VALUES(1,1,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(2,4,4,1,'Monospace','[(0, 156)]');
INSERT INTO "grampsdb_markup" VALUES(3,5,4,1,'Monospace','[(0, 135)]');
INSERT INTO "grampsdb_markup" VALUES(4,6,4,1,'Monospace','[(0, 166)]');
INSERT INTO "grampsdb_markup" VALUES(5,7,4,1,'Monospace','[(0, 282)]');
INSERT INTO "grampsdb_markup" VALUES(6,13,4,1,'Monospace','[(0, 162)]');
INSERT INTO "grampsdb_markup" VALUES(7,14,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(8,22,4,1,'Monospace','[(0, 155)]');
INSERT INTO "grampsdb_markup" VALUES(9,26,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(10,28,4,1,'Monospace','[(0, 163)]');
INSERT INTO "grampsdb_markup" VALUES(11,29,4,1,'Monospace','[(0, 159)]');
INSERT INTO "grampsdb_markup" VALUES(12,31,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(13,33,4,1,'Monospace','[(0, 150)]');
INSERT INTO "grampsdb_markup" VALUES(14,35,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(15,45,4,1,'Monospace','[(0, 159)]');
INSERT INTO "grampsdb_markup" VALUES(16,47,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(17,48,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(18,50,4,1,'Monospace','[(0, 143)]');
INSERT INTO "grampsdb_markup" VALUES(19,52,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(20,53,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(21,58,4,1,'Monospace','[(0, 162)]');
INSERT INTO "grampsdb_markup" VALUES(22,62,4,1,'Monospace','[(0, 170)]');
INSERT INTO "grampsdb_markup" VALUES(23,65,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(24,66,4,1,'Monospace','[(0, 143)]');
INSERT INTO "grampsdb_markup" VALUES(25,67,4,1,'Monospace','[(0, 135)]');
INSERT INTO "grampsdb_markup" VALUES(26,68,4,1,'Monospace','[(0, 154)]');
INSERT INTO "grampsdb_markup" VALUES(27,69,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(28,70,4,1,'Monospace','[(0, 152)]');
INSERT INTO "grampsdb_markup" VALUES(29,72,4,1,'Monospace','[(0, 175)]');
INSERT INTO "grampsdb_markup" VALUES(30,73,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(31,75,4,1,'Monospace','[(0, 157)]');
CREATE TABLE "grampsdb_sourcedatamap" (
    "id" integer NOT NULL PRIMARY KEY,
    "key" varchar(80) NOT NULL,
    "value" varchar(80) NOT NULL,
    "source_id" integer NOT NULL REFERENCES "grampsdb_source" ("id"),
    "order" integer unsigned NOT NULL
);
CREATE TABLE "grampsdb_citationdatamap" (
    "id" integer NOT NULL PRIMARY KEY,
    "key" varchar(80) NOT NULL,
    "value" varchar(80) NOT NULL,
    "citation_id" integer NOT NULL REFERENCES "grampsdb_citation" ("id"),
    "order" integer unsigned NOT NULL
);
CREATE TABLE "grampsdb_address" (
    "id" integer NOT NULL PRIMARY KEY,
    "calendar" integer NOT NULL,
    "modifier" integer NOT NULL,
    "quality" integer NOT NULL,
    "day1" integer NOT NULL,
    "month1" integer NOT NULL,
    "year1" integer NOT NULL,
    "slash1" bool NOT NULL,
    "day2" integer,
    "month2" integer,
    "year2" integer,
    "slash2" bool,
    "text" varchar(80) NOT NULL,
    "sortval" integer NOT NULL,
    "newyear" integer NOT NULL,
    "private" bool NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "order" integer unsigned NOT NULL,
    "person_id" integer REFERENCES "grampsdb_person" ("id"),
    "repository_id" integer REFERENCES "grampsdb_repository" ("id")
);
CREATE TABLE "grampsdb_location" (
    "id" integer NOT NULL PRIMARY KEY,
    "street" text NOT NULL,
    "locality" text NOT NULL,
    "city" text NOT NULL,
    "county" text NOT NULL,
    "state" text NOT NULL,
    "country" text NOT NULL,
    "postal" text NOT NULL,
    "phone" text NOT NULL,
    "parish" text,
    "order" integer unsigned NOT NULL,
    "place_id" integer REFERENCES "grampsdb_place" ("id"),
    "address_id" integer REFERENCES "grampsdb_address" ("id")
);
CREATE TABLE "grampsdb_url" (
    "id" integer NOT NULL PRIMARY KEY,
    "private" bool NOT NULL,
    "path" text,
    "desc" text,
    "url_type_id" integer NOT NULL REFERENCES "grampsdb_urltype" ("id"),
    "order" integer unsigned NOT NULL,
    "person_id" integer REFERENCES "grampsdb_person" ("id"),
    "place_id" integer REFERENCES "grampsdb_place" ("id"),
    "repository_id" integer REFERENCES "grampsdb_repository" ("id")
);
CREATE TABLE "grampsdb_attribute" (
    "id" integer NOT NULL PRIMARY KEY,
    "private" bool NOT NULL,
    "attribute_type_id" integer NOT NULL REFERENCES "grampsdb_attributetype" ("id"),
    "value" text,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL
);
CREATE TABLE "grampsdb_log" (
    "id" integer NOT NULL PRIMARY KEY,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    "order" integer unsigned NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "log_type" varchar(10) NOT NULL,
    "reason" text NOT NULL,
    "cache" text
);
CREATE TABLE "grampsdb_noteref" (
    "id" integer NOT NULL PRIMARY KEY,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    "order" integer unsigned NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "ref_object_id" integer NOT NULL REFERENCES "grampsdb_note" ("id")
);
INSERT INTO "grampsdb_noteref" VALUES(1,37,1,1,'2012-07-31 08:00:20.830879',NULL,NULL,0,72);
INSERT INTO "grampsdb_noteref" VALUES(2,34,4,1,'2012-07-31 08:00:21.023065',NULL,NULL,0,21);
INSERT INTO "grampsdb_noteref" VALUES(3,34,4,1,'2012-07-31 08:00:21.025292',NULL,NULL,0,56);
INSERT INTO "grampsdb_noteref" VALUES(4,34,4,1,'2012-07-31 08:00:21.027663',NULL,NULL,0,54);
INSERT INTO "grampsdb_noteref" VALUES(5,34,4,1,'2012-07-31 08:00:21.030062',NULL,NULL,0,51);
INSERT INTO "grampsdb_noteref" VALUES(6,34,4,1,'2012-07-31 08:00:21.032215',NULL,NULL,0,65);
INSERT INTO "grampsdb_noteref" VALUES(7,34,7,1,'2012-07-31 08:00:21.223677',NULL,NULL,0,24);
INSERT INTO "grampsdb_noteref" VALUES(8,34,7,1,'2012-07-31 08:00:21.226141',NULL,NULL,0,63);
INSERT INTO "grampsdb_noteref" VALUES(9,34,7,1,'2012-07-31 08:00:21.228285',NULL,NULL,0,38);
INSERT INTO "grampsdb_noteref" VALUES(10,34,7,1,'2012-07-31 08:00:21.230416',NULL,NULL,0,74);
INSERT INTO "grampsdb_noteref" VALUES(11,34,7,1,'2012-07-31 08:00:21.232580',NULL,NULL,0,64);
INSERT INTO "grampsdb_noteref" VALUES(12,34,7,1,'2012-07-31 08:00:21.234834',NULL,NULL,0,7);
INSERT INTO "grampsdb_noteref" VALUES(13,34,8,1,'2012-07-31 08:00:21.306572',NULL,NULL,0,59);
INSERT INTO "grampsdb_noteref" VALUES(14,34,9,1,'2012-07-31 08:00:21.348790',NULL,NULL,0,71);
INSERT INTO "grampsdb_noteref" VALUES(15,34,9,1,'2012-07-31 08:00:21.350967',NULL,NULL,0,32);
INSERT INTO "grampsdb_noteref" VALUES(16,34,9,1,'2012-07-31 08:00:21.353104',NULL,NULL,0,42);
INSERT INTO "grampsdb_noteref" VALUES(17,34,9,1,'2012-07-31 08:00:21.355268',NULL,NULL,0,14);
INSERT INTO "grampsdb_noteref" VALUES(18,34,10,1,'2012-07-31 08:00:21.422806',NULL,NULL,0,37);
INSERT INTO "grampsdb_noteref" VALUES(19,34,10,1,'2012-07-31 08:00:21.424970',NULL,NULL,0,19);
INSERT INTO "grampsdb_noteref" VALUES(20,34,10,1,'2012-07-31 08:00:21.427128',NULL,NULL,0,73);
INSERT INTO "grampsdb_noteref" VALUES(21,37,2,1,'2012-07-31 08:00:21.606003',NULL,NULL,0,33);
INSERT INTO "grampsdb_noteref" VALUES(22,34,18,1,'2012-07-31 08:00:21.796631',NULL,NULL,0,18);
INSERT INTO "grampsdb_noteref" VALUES(23,34,20,1,'2012-07-31 08:00:21.858721',NULL,NULL,0,12);
INSERT INTO "grampsdb_noteref" VALUES(24,34,27,1,'2012-07-31 08:00:22.090285',NULL,NULL,0,34);
INSERT INTO "grampsdb_noteref" VALUES(25,37,3,1,'2012-07-31 08:00:22.131285',NULL,NULL,0,70);
INSERT INTO "grampsdb_noteref" VALUES(26,34,29,1,'2012-07-31 08:00:22.195095',NULL,NULL,0,44);
INSERT INTO "grampsdb_noteref" VALUES(27,34,29,1,'2012-07-31 08:00:22.197259',NULL,NULL,0,25);
INSERT INTO "grampsdb_noteref" VALUES(28,34,29,1,'2012-07-31 08:00:22.199417',NULL,NULL,0,47);
INSERT INTO "grampsdb_noteref" VALUES(29,34,38,1,'2012-07-31 08:00:22.665685',NULL,NULL,0,61);
INSERT INTO "grampsdb_noteref" VALUES(30,34,38,1,'2012-07-31 08:00:22.667927',NULL,NULL,0,9);
INSERT INTO "grampsdb_noteref" VALUES(31,34,38,1,'2012-07-31 08:00:22.670110',NULL,NULL,0,15);
INSERT INTO "grampsdb_noteref" VALUES(32,34,38,1,'2012-07-31 08:00:22.672256',NULL,NULL,0,39);
INSERT INTO "grampsdb_noteref" VALUES(33,34,38,1,'2012-07-31 08:00:22.674428',NULL,NULL,0,40);
INSERT INTO "grampsdb_noteref" VALUES(34,34,38,1,'2012-07-31 08:00:22.676570',NULL,NULL,0,52);
INSERT INTO "grampsdb_noteref" VALUES(35,34,42,1,'2012-07-31 08:00:22.874608',NULL,NULL,0,3);
INSERT INTO "grampsdb_noteref" VALUES(36,34,42,1,'2012-07-31 08:00:22.876792',NULL,NULL,0,17);
INSERT INTO "grampsdb_noteref" VALUES(37,34,42,1,'2012-07-31 08:00:22.878979',NULL,NULL,0,23);
INSERT INTO "grampsdb_noteref" VALUES(38,34,42,1,'2012-07-31 08:00:22.881130',NULL,NULL,0,20);
INSERT INTO "grampsdb_noteref" VALUES(39,34,42,1,'2012-07-31 08:00:22.883298',NULL,NULL,0,1);
INSERT INTO "grampsdb_noteref" VALUES(40,34,43,1,'2012-07-31 08:00:22.941789',NULL,NULL,0,49);
INSERT INTO "grampsdb_noteref" VALUES(41,34,43,1,'2012-07-31 08:00:22.945025',NULL,NULL,0,10);
INSERT INTO "grampsdb_noteref" VALUES(42,34,43,1,'2012-07-31 08:00:22.947595',NULL,NULL,0,60);
INSERT INTO "grampsdb_noteref" VALUES(43,34,43,1,'2012-07-31 08:00:22.950003',NULL,NULL,0,69);
INSERT INTO "grampsdb_noteref" VALUES(44,37,4,1,'2012-07-31 08:00:23.145325',NULL,NULL,0,62);
INSERT INTO "grampsdb_noteref" VALUES(45,34,47,1,'2012-07-31 08:00:23.180011',NULL,NULL,0,16);
INSERT INTO "grampsdb_noteref" VALUES(46,34,47,1,'2012-07-31 08:00:23.182247',NULL,NULL,0,57);
INSERT INTO "grampsdb_noteref" VALUES(47,34,47,1,'2012-07-31 08:00:23.184498',NULL,NULL,0,48);
INSERT INTO "grampsdb_noteref" VALUES(48,34,49,1,'2012-07-31 08:00:23.244158',NULL,NULL,0,43);
INSERT INTO "grampsdb_noteref" VALUES(49,34,49,1,'2012-07-31 08:00:23.246533',NULL,NULL,0,36);
INSERT INTO "grampsdb_noteref" VALUES(50,34,49,1,'2012-07-31 08:00:23.248709',NULL,NULL,0,53);
INSERT INTO "grampsdb_noteref" VALUES(51,37,5,1,'2012-07-31 08:00:23.321276',NULL,NULL,0,5);
INSERT INTO "grampsdb_noteref" VALUES(52,37,6,1,'2012-07-31 08:00:23.361927',NULL,NULL,0,67);
INSERT INTO "grampsdb_noteref" VALUES(53,37,7,1,'2012-07-31 08:00:23.369092',NULL,NULL,0,50);
INSERT INTO "grampsdb_noteref" VALUES(54,37,8,1,'2012-07-31 08:00:23.512546',NULL,NULL,0,66);
INSERT INTO "grampsdb_noteref" VALUES(55,34,54,1,'2012-07-31 08:00:23.564599',NULL,NULL,0,55);
INSERT INTO "grampsdb_noteref" VALUES(56,34,54,1,'2012-07-31 08:00:23.566889',NULL,NULL,0,11);
INSERT INTO "grampsdb_noteref" VALUES(57,34,54,1,'2012-07-31 08:00:23.569038',NULL,NULL,0,41);
INSERT INTO "grampsdb_noteref" VALUES(58,34,54,1,'2012-07-31 08:00:23.571194',NULL,NULL,0,8);
INSERT INTO "grampsdb_noteref" VALUES(59,34,54,1,'2012-07-31 08:00:23.573344',NULL,NULL,0,35);
INSERT INTO "grampsdb_noteref" VALUES(60,37,9,1,'2012-07-31 08:00:23.617292',NULL,NULL,0,6);
INSERT INTO "grampsdb_noteref" VALUES(61,34,59,1,'2012-07-31 08:00:23.800557',NULL,NULL,0,2);
INSERT INTO "grampsdb_noteref" VALUES(62,34,59,1,'2012-07-31 08:00:23.802858',NULL,NULL,0,27);
INSERT INTO "grampsdb_noteref" VALUES(63,34,59,1,'2012-07-31 08:00:23.805025',NULL,NULL,0,26);
INSERT INTO "grampsdb_noteref" VALUES(64,37,10,1,'2012-07-31 08:00:23.880854',NULL,NULL,0,28);
INSERT INTO "grampsdb_noteref" VALUES(65,37,11,1,'2012-07-31 08:00:24.017556',NULL,NULL,0,22);
INSERT INTO "grampsdb_noteref" VALUES(66,34,65,1,'2012-07-31 08:00:24.040562',NULL,NULL,0,46);
INSERT INTO "grampsdb_noteref" VALUES(67,34,65,1,'2012-07-31 08:00:24.042749',NULL,NULL,0,30);
INSERT INTO "grampsdb_noteref" VALUES(68,34,65,1,'2012-07-31 08:00:24.044894',NULL,NULL,0,31);
CREATE TABLE "grampsdb_eventref" (
    "id" integer NOT NULL PRIMARY KEY,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    "order" integer unsigned NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "ref_object_id" integer NOT NULL REFERENCES "grampsdb_event" ("id"),
    "role_type_id" integer NOT NULL REFERENCES "grampsdb_eventroletype" ("id")
);
INSERT INTO "grampsdb_eventref" VALUES(1,34,1,1,'2012-07-31 08:00:20.849235',NULL,NULL,0,7,3);
INSERT INTO "grampsdb_eventref" VALUES(2,34,3,1,'2012-07-31 08:00:20.924835',NULL,NULL,0,65,3);
INSERT INTO "grampsdb_eventref" VALUES(3,34,3,2,'2012-07-31 08:00:20.927680',NULL,NULL,0,28,3);
INSERT INTO "grampsdb_eventref" VALUES(4,34,3,3,'2012-07-31 08:00:20.930475',NULL,NULL,0,17,3);
INSERT INTO "grampsdb_eventref" VALUES(5,35,1,1,'2012-07-31 08:00:20.975432',NULL,NULL,0,55,10);
INSERT INTO "grampsdb_eventref" VALUES(6,34,4,1,'2012-07-31 08:00:20.999381',NULL,NULL,0,31,3);
INSERT INTO "grampsdb_eventref" VALUES(7,34,4,2,'2012-07-31 08:00:21.002214',NULL,NULL,0,20,3);
INSERT INTO "grampsdb_eventref" VALUES(8,34,4,3,'2012-07-31 08:00:21.005018',NULL,NULL,0,66,3);
INSERT INTO "grampsdb_eventref" VALUES(9,34,4,4,'2012-07-31 08:00:21.008130',NULL,NULL,0,77,3);
INSERT INTO "grampsdb_eventref" VALUES(10,34,4,5,'2012-07-31 08:00:21.011107',NULL,NULL,0,8,3);
INSERT INTO "grampsdb_eventref" VALUES(11,34,4,6,'2012-07-31 08:00:21.013954',NULL,NULL,0,87,3);
INSERT INTO "grampsdb_eventref" VALUES(12,35,2,1,'2012-07-31 08:00:21.087065',NULL,NULL,0,94,10);
INSERT INTO "grampsdb_eventref" VALUES(13,34,5,1,'2012-07-31 08:00:21.095861',NULL,NULL,0,81,3);
INSERT INTO "grampsdb_eventref" VALUES(14,34,6,1,'2012-07-31 08:00:21.131958',NULL,NULL,0,100,3);
INSERT INTO "grampsdb_eventref" VALUES(15,34,7,1,'2012-07-31 08:00:21.185421',NULL,NULL,0,86,3);
INSERT INTO "grampsdb_eventref" VALUES(16,34,7,2,'2012-07-31 08:00:21.188397',NULL,NULL,0,92,3);
INSERT INTO "grampsdb_eventref" VALUES(17,34,7,3,'2012-07-31 08:00:21.191239',NULL,NULL,0,118,3);
INSERT INTO "grampsdb_eventref" VALUES(18,34,7,4,'2012-07-31 08:00:21.194174',NULL,NULL,0,63,3);
INSERT INTO "grampsdb_eventref" VALUES(19,34,7,5,'2012-07-31 08:00:21.197030',NULL,NULL,0,53,3);
INSERT INTO "grampsdb_eventref" VALUES(20,34,7,6,'2012-07-31 08:00:21.199872',NULL,NULL,0,98,3);
INSERT INTO "grampsdb_eventref" VALUES(21,34,7,7,'2012-07-31 08:00:21.202830',NULL,NULL,0,21,3);
INSERT INTO "grampsdb_eventref" VALUES(22,34,7,8,'2012-07-31 08:00:21.205859',NULL,NULL,0,90,3);
INSERT INTO "grampsdb_eventref" VALUES(23,34,7,9,'2012-07-31 08:00:21.208707',NULL,NULL,0,110,3);
INSERT INTO "grampsdb_eventref" VALUES(24,34,7,10,'2012-07-31 08:00:21.211640',NULL,NULL,0,138,3);
INSERT INTO "grampsdb_eventref" VALUES(25,34,7,11,'2012-07-31 08:00:21.214505',NULL,NULL,0,42,3);
INSERT INTO "grampsdb_eventref" VALUES(26,34,8,1,'2012-07-31 08:00:21.297727',NULL,NULL,0,97,3);
INSERT INTO "grampsdb_eventref" VALUES(27,34,9,1,'2012-07-31 08:00:21.328955',NULL,NULL,0,112,3);
INSERT INTO "grampsdb_eventref" VALUES(28,34,9,2,'2012-07-31 08:00:21.331816',NULL,NULL,0,74,3);
INSERT INTO "grampsdb_eventref" VALUES(29,34,9,3,'2012-07-31 08:00:21.334622',NULL,NULL,0,12,3);
INSERT INTO "grampsdb_eventref" VALUES(30,34,9,4,'2012-07-31 08:00:21.337428',NULL,NULL,0,70,3);
INSERT INTO "grampsdb_eventref" VALUES(31,34,9,5,'2012-07-31 08:00:21.340342',NULL,NULL,0,30,3);
INSERT INTO "grampsdb_eventref" VALUES(32,34,9,6,'2012-07-31 08:00:21.343177',NULL,NULL,0,78,3);
INSERT INTO "grampsdb_eventref" VALUES(33,34,10,1,'2012-07-31 08:00:21.400203',NULL,NULL,0,38,3);
INSERT INTO "grampsdb_eventref" VALUES(34,34,10,2,'2012-07-31 08:00:21.403032',NULL,NULL,0,56,3);
INSERT INTO "grampsdb_eventref" VALUES(35,34,10,3,'2012-07-31 08:00:21.405862',NULL,NULL,0,124,3);
INSERT INTO "grampsdb_eventref" VALUES(36,34,10,4,'2012-07-31 08:00:21.408658',NULL,NULL,0,40,3);
INSERT INTO "grampsdb_eventref" VALUES(37,34,10,5,'2012-07-31 08:00:21.411569',NULL,NULL,0,89,3);
INSERT INTO "grampsdb_eventref" VALUES(38,34,10,6,'2012-07-31 08:00:21.414386',NULL,NULL,0,120,3);
INSERT INTO "grampsdb_eventref" VALUES(39,34,10,7,'2012-07-31 08:00:21.417162',NULL,NULL,0,129,3);
INSERT INTO "grampsdb_eventref" VALUES(40,35,4,1,'2012-07-31 08:00:21.467954',NULL,NULL,0,107,10);
INSERT INTO "grampsdb_eventref" VALUES(41,34,11,1,'2012-07-31 08:00:21.476447',NULL,NULL,0,64,3);
INSERT INTO "grampsdb_eventref" VALUES(42,34,11,2,'2012-07-31 08:00:21.479237',NULL,NULL,0,106,3);
INSERT INTO "grampsdb_eventref" VALUES(43,34,12,1,'2012-07-31 08:00:21.519969',NULL,NULL,0,50,3);
INSERT INTO "grampsdb_eventref" VALUES(44,34,13,1,'2012-07-31 08:00:21.567957',NULL,NULL,0,95,3);
INSERT INTO "grampsdb_eventref" VALUES(45,34,13,2,'2012-07-31 08:00:21.570879',NULL,NULL,0,6,3);
INSERT INTO "grampsdb_eventref" VALUES(46,34,14,1,'2012-07-31 08:00:21.625505',NULL,NULL,0,48,3);
INSERT INTO "grampsdb_eventref" VALUES(47,35,5,1,'2012-07-31 08:00:21.647132',NULL,NULL,0,39,10);
INSERT INTO "grampsdb_eventref" VALUES(48,34,15,1,'2012-07-31 08:00:21.704551',NULL,NULL,0,136,3);
INSERT INTO "grampsdb_eventref" VALUES(49,34,16,1,'2012-07-31 08:00:21.733196',NULL,NULL,0,133,3);
INSERT INTO "grampsdb_eventref" VALUES(50,34,16,2,'2012-07-31 08:00:21.736039',NULL,NULL,0,84,3);
INSERT INTO "grampsdb_eventref" VALUES(51,34,17,1,'2012-07-31 08:00:21.767768',NULL,NULL,0,79,3);
INSERT INTO "grampsdb_eventref" VALUES(52,34,18,1,'2012-07-31 08:00:21.790947',NULL,NULL,0,119,3);
INSERT INTO "grampsdb_eventref" VALUES(53,34,19,1,'2012-07-31 08:00:21.827523',NULL,NULL,0,131,3);
INSERT INTO "grampsdb_eventref" VALUES(54,34,20,1,'2012-07-31 08:00:21.850272',NULL,NULL,0,126,3);
INSERT INTO "grampsdb_eventref" VALUES(55,34,20,2,'2012-07-31 08:00:21.853073',NULL,NULL,0,24,3);
INSERT INTO "grampsdb_eventref" VALUES(56,34,21,1,'2012-07-31 08:00:21.902265',NULL,NULL,0,105,3);
INSERT INTO "grampsdb_eventref" VALUES(57,34,22,1,'2012-07-31 08:00:21.936230',NULL,NULL,0,23,3);
INSERT INTO "grampsdb_eventref" VALUES(58,34,22,2,'2012-07-31 08:00:21.939059',NULL,NULL,0,34,3);
INSERT INTO "grampsdb_eventref" VALUES(59,34,22,3,'2012-07-31 08:00:21.941886',NULL,NULL,0,27,3);
INSERT INTO "grampsdb_eventref" VALUES(60,34,22,4,'2012-07-31 08:00:21.944687',NULL,NULL,0,99,3);
INSERT INTO "grampsdb_eventref" VALUES(61,34,25,1,'2012-07-31 08:00:22.030822',NULL,NULL,0,72,3);
INSERT INTO "grampsdb_eventref" VALUES(62,34,27,1,'2012-07-31 08:00:22.073309',NULL,NULL,0,93,3);
INSERT INTO "grampsdb_eventref" VALUES(63,34,27,2,'2012-07-31 08:00:22.076163',NULL,NULL,0,49,3);
INSERT INTO "grampsdb_eventref" VALUES(64,34,27,3,'2012-07-31 08:00:22.078982',NULL,NULL,0,43,3);
INSERT INTO "grampsdb_eventref" VALUES(65,34,27,4,'2012-07-31 08:00:22.081895',NULL,NULL,0,76,3);
INSERT INTO "grampsdb_eventref" VALUES(66,34,27,5,'2012-07-31 08:00:22.084693',NULL,NULL,0,116,3);
INSERT INTO "grampsdb_eventref" VALUES(67,34,29,1,'2012-07-31 08:00:22.174764',NULL,NULL,0,41,3);
INSERT INTO "grampsdb_eventref" VALUES(68,34,29,2,'2012-07-31 08:00:22.177616',NULL,NULL,0,54,3);
INSERT INTO "grampsdb_eventref" VALUES(69,34,29,3,'2012-07-31 08:00:22.180410',NULL,NULL,0,101,3);
INSERT INTO "grampsdb_eventref" VALUES(70,34,29,4,'2012-07-31 08:00:22.183295',NULL,NULL,0,140,3);
INSERT INTO "grampsdb_eventref" VALUES(71,34,29,5,'2012-07-31 08:00:22.186140',NULL,NULL,0,139,3);
INSERT INTO "grampsdb_eventref" VALUES(72,34,30,1,'2012-07-31 08:00:22.238276',NULL,NULL,0,80,3);
INSERT INTO "grampsdb_eventref" VALUES(73,35,7,1,'2012-07-31 08:00:22.284812',NULL,NULL,0,73,10);
INSERT INTO "grampsdb_eventref" VALUES(74,34,32,1,'2012-07-31 08:00:22.338583',NULL,NULL,0,58,3);
INSERT INTO "grampsdb_eventref" VALUES(75,34,33,1,'2012-07-31 08:00:22.364463',NULL,NULL,0,102,3);
INSERT INTO "grampsdb_eventref" VALUES(76,34,34,1,'2012-07-31 08:00:22.399259',NULL,NULL,0,57,3);
INSERT INTO "grampsdb_eventref" VALUES(77,34,35,1,'2012-07-31 08:00:22.443120',NULL,NULL,0,46,3);
INSERT INTO "grampsdb_eventref" VALUES(78,34,35,2,'2012-07-31 08:00:22.445973',NULL,NULL,0,96,3);
INSERT INTO "grampsdb_eventref" VALUES(79,34,36,1,'2012-07-31 08:00:22.481026',NULL,NULL,0,19,3);
INSERT INTO "grampsdb_eventref" VALUES(80,35,8,1,'2012-07-31 08:00:22.508669',NULL,NULL,0,29,10);
INSERT INTO "grampsdb_eventref" VALUES(81,34,37,1,'2012-07-31 08:00:22.522699',NULL,NULL,0,44,3);
INSERT INTO "grampsdb_eventref" VALUES(82,34,37,2,'2012-07-31 08:00:22.525628',NULL,NULL,0,143,3);
INSERT INTO "grampsdb_eventref" VALUES(83,35,9,1,'2012-07-31 08:00:22.572866',NULL,NULL,0,67,10);
INSERT INTO "grampsdb_eventref" VALUES(84,35,10,1,'2012-07-31 08:00:22.622483',NULL,NULL,0,36,10);
INSERT INTO "grampsdb_eventref" VALUES(85,34,38,1,'2012-07-31 08:00:22.639637',NULL,NULL,0,117,3);
INSERT INTO "grampsdb_eventref" VALUES(86,34,38,2,'2012-07-31 08:00:22.642474',NULL,NULL,0,37,3);
INSERT INTO "grampsdb_eventref" VALUES(87,34,38,3,'2012-07-31 08:00:22.645279',NULL,NULL,0,91,3);
INSERT INTO "grampsdb_eventref" VALUES(88,34,38,4,'2012-07-31 08:00:22.648211',NULL,NULL,0,61,3);
INSERT INTO "grampsdb_eventref" VALUES(89,34,38,5,'2012-07-31 08:00:22.651060',NULL,NULL,0,130,3);
INSERT INTO "grampsdb_eventref" VALUES(90,34,38,6,'2012-07-31 08:00:22.653885',NULL,NULL,0,128,3);
INSERT INTO "grampsdb_eventref" VALUES(91,34,38,7,'2012-07-31 08:00:22.656695',NULL,NULL,0,85,3);
INSERT INTO "grampsdb_eventref" VALUES(92,34,39,1,'2012-07-31 08:00:22.719032',NULL,NULL,0,115,3);
INSERT INTO "grampsdb_eventref" VALUES(93,34,40,1,'2012-07-31 08:00:22.758815',NULL,NULL,0,125,3);
INSERT INTO "grampsdb_eventref" VALUES(94,34,41,1,'2012-07-31 08:00:22.820055',NULL,NULL,0,15,3);
INSERT INTO "grampsdb_eventref" VALUES(95,34,42,1,'2012-07-31 08:00:22.851040',NULL,NULL,0,71,3);
INSERT INTO "grampsdb_eventref" VALUES(96,34,42,2,'2012-07-31 08:00:22.854002',NULL,NULL,0,22,3);
INSERT INTO "grampsdb_eventref" VALUES(97,34,42,3,'2012-07-31 08:00:22.856830',NULL,NULL,0,142,3);
INSERT INTO "grampsdb_eventref" VALUES(98,34,42,4,'2012-07-31 08:00:22.859654',NULL,NULL,0,123,3);
INSERT INTO "grampsdb_eventref" VALUES(99,34,42,5,'2012-07-31 08:00:22.862566',NULL,NULL,0,59,3);
INSERT INTO "grampsdb_eventref" VALUES(100,34,42,6,'2012-07-31 08:00:22.865558',NULL,NULL,0,137,3);
INSERT INTO "grampsdb_eventref" VALUES(101,34,43,1,'2012-07-31 08:00:22.925273',NULL,NULL,0,134,3);
INSERT INTO "grampsdb_eventref" VALUES(102,34,43,2,'2012-07-31 08:00:22.928290',NULL,NULL,0,14,3);
INSERT INTO "grampsdb_eventref" VALUES(103,35,11,1,'2012-07-31 08:00:23.001866',NULL,NULL,0,104,10);
INSERT INTO "grampsdb_eventref" VALUES(104,34,44,1,'2012-07-31 08:00:23.024207',NULL,NULL,0,10,3);
INSERT INTO "grampsdb_eventref" VALUES(105,34,45,1,'2012-07-31 08:00:23.048345',NULL,NULL,0,1,3);
INSERT INTO "grampsdb_eventref" VALUES(106,34,47,1,'2012-07-31 08:00:23.170295',NULL,NULL,0,62,3);
INSERT INTO "grampsdb_eventref" VALUES(107,34,47,2,'2012-07-31 08:00:23.173662',NULL,NULL,0,109,3);
INSERT INTO "grampsdb_eventref" VALUES(108,34,48,1,'2012-07-31 08:00:23.207216',NULL,NULL,0,13,3);
INSERT INTO "grampsdb_eventref" VALUES(109,34,49,1,'2012-07-31 08:00:23.232410',NULL,NULL,0,51,3);
INSERT INTO "grampsdb_eventref" VALUES(110,34,49,2,'2012-07-31 08:00:23.235316',NULL,NULL,0,35,3);
INSERT INTO "grampsdb_eventref" VALUES(111,34,50,1,'2012-07-31 08:00:23.283755',NULL,NULL,0,75,3);
INSERT INTO "grampsdb_eventref" VALUES(112,35,12,1,'2012-07-31 08:00:23.316396',NULL,NULL,0,127,10);
INSERT INTO "grampsdb_eventref" VALUES(113,34,52,1,'2012-07-31 08:00:23.422301',NULL,NULL,0,113,3);
INSERT INTO "grampsdb_eventref" VALUES(114,34,52,2,'2012-07-31 08:00:23.425130',NULL,NULL,0,45,3);
INSERT INTO "grampsdb_eventref" VALUES(115,34,53,1,'2012-07-31 08:00:23.483258',NULL,NULL,0,103,3);
INSERT INTO "grampsdb_eventref" VALUES(116,34,53,2,'2012-07-31 08:00:23.486135',NULL,NULL,0,52,3);
INSERT INTO "grampsdb_eventref" VALUES(117,34,54,1,'2012-07-31 08:00:23.535228',NULL,NULL,0,3,3);
INSERT INTO "grampsdb_eventref" VALUES(118,34,54,2,'2012-07-31 08:00:23.538088',NULL,NULL,0,68,3);
INSERT INTO "grampsdb_eventref" VALUES(119,34,54,3,'2012-07-31 08:00:23.540899',NULL,NULL,0,9,3);
INSERT INTO "grampsdb_eventref" VALUES(120,34,54,4,'2012-07-31 08:00:23.543750',NULL,NULL,0,132,3);
INSERT INTO "grampsdb_eventref" VALUES(121,34,54,5,'2012-07-31 08:00:23.546684',NULL,NULL,0,144,3);
INSERT INTO "grampsdb_eventref" VALUES(122,34,54,6,'2012-07-31 08:00:23.549513',NULL,NULL,0,82,3);
INSERT INTO "grampsdb_eventref" VALUES(123,34,54,7,'2012-07-31 08:00:23.552316',NULL,NULL,0,33,3);
INSERT INTO "grampsdb_eventref" VALUES(124,35,14,1,'2012-07-31 08:00:23.660936',NULL,NULL,0,32,10);
INSERT INTO "grampsdb_eventref" VALUES(125,34,57,1,'2012-07-31 08:00:23.728411',NULL,NULL,0,26,3);
INSERT INTO "grampsdb_eventref" VALUES(126,34,58,1,'2012-07-31 08:00:23.757305',NULL,NULL,0,83,3);
INSERT INTO "grampsdb_eventref" VALUES(127,34,59,1,'2012-07-31 08:00:23.783483',NULL,NULL,0,111,3);
INSERT INTO "grampsdb_eventref" VALUES(128,34,59,2,'2012-07-31 08:00:23.786338',NULL,NULL,0,114,3);
INSERT INTO "grampsdb_eventref" VALUES(129,34,59,3,'2012-07-31 08:00:23.789175',NULL,NULL,0,5,3);
INSERT INTO "grampsdb_eventref" VALUES(130,34,59,4,'2012-07-31 08:00:23.792102',NULL,NULL,0,108,3);
INSERT INTO "grampsdb_eventref" VALUES(131,34,59,5,'2012-07-31 08:00:23.794953',NULL,NULL,0,18,3);
INSERT INTO "grampsdb_eventref" VALUES(132,34,60,1,'2012-07-31 08:00:23.850238',NULL,NULL,0,16,3);
INSERT INTO "grampsdb_eventref" VALUES(133,35,16,1,'2012-07-31 08:00:23.922087',NULL,NULL,0,11,10);
INSERT INTO "grampsdb_eventref" VALUES(134,35,17,1,'2012-07-31 08:00:23.955125',NULL,NULL,0,25,10);
INSERT INTO "grampsdb_eventref" VALUES(135,34,63,1,'2012-07-31 08:00:23.963658',NULL,NULL,0,121,3);
INSERT INTO "grampsdb_eventref" VALUES(136,34,64,1,'2012-07-31 08:00:23.989297',NULL,NULL,0,122,3);
INSERT INTO "grampsdb_eventref" VALUES(137,34,65,1,'2012-07-31 08:00:24.028739',NULL,NULL,0,47,3);
INSERT INTO "grampsdb_eventref" VALUES(138,34,65,2,'2012-07-31 08:00:24.031610',NULL,NULL,0,69,3);
INSERT INTO "grampsdb_eventref" VALUES(139,35,18,1,'2012-07-31 08:00:24.105025',NULL,NULL,0,88,10);
INSERT INTO "grampsdb_eventref" VALUES(140,34,67,1,'2012-07-31 08:00:24.144554',NULL,NULL,0,135,3);
INSERT INTO "grampsdb_eventref" VALUES(141,34,67,2,'2012-07-31 08:00:24.147387',NULL,NULL,0,2,3);
INSERT INTO "grampsdb_eventref" VALUES(142,34,68,1,'2012-07-31 08:00:24.177586',NULL,NULL,0,4,3);
INSERT INTO "grampsdb_eventref" VALUES(143,34,69,1,'2012-07-31 08:00:24.211105',NULL,NULL,0,60,3);
INSERT INTO "grampsdb_eventref" VALUES(144,35,19,1,'2012-07-31 08:00:24.271336',NULL,NULL,0,141,10);
CREATE TABLE "grampsdb_repositoryref" (
    "id" integer NOT NULL PRIMARY KEY,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    "order" integer unsigned NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "ref_object_id" integer NOT NULL REFERENCES "grampsdb_repository" ("id"),
    "source_media_type_id" integer NOT NULL REFERENCES "grampsdb_sourcemediatype" ("id"),
    "call_number" varchar(50) NOT NULL
);
CREATE TABLE "grampsdb_personref" (
    "id" integer NOT NULL PRIMARY KEY,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    "order" integer unsigned NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "ref_object_id" integer NOT NULL REFERENCES "grampsdb_person" ("id"),
    "description" varchar(50)
);
CREATE TABLE "grampsdb_citationref" (
    "id" integer NOT NULL PRIMARY KEY,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    "order" integer unsigned NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "citation_id" integer NOT NULL REFERENCES "grampsdb_citation" ("id")
);
CREATE TABLE "grampsdb_childref" (
    "id" integer NOT NULL PRIMARY KEY,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    "order" integer unsigned NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "father_rel_type_id" integer NOT NULL REFERENCES "grampsdb_childreftype" ("id"),
    "mother_rel_type_id" integer NOT NULL REFERENCES "grampsdb_childreftype" ("id"),
    "ref_object_id" integer NOT NULL REFERENCES "grampsdb_person" ("id")
);
INSERT INTO "grampsdb_childref" VALUES(1,35,1,1,'2012-07-31 08:00:20.965339',NULL,NULL,0,2,2,19);
INSERT INTO "grampsdb_childref" VALUES(2,35,1,2,'2012-07-31 08:00:20.969028',NULL,NULL,0,2,2,37);
INSERT INTO "grampsdb_childref" VALUES(3,35,1,3,'2012-07-31 08:00:20.972479',NULL,NULL,0,2,2,41);
INSERT INTO "grampsdb_childref" VALUES(4,35,2,1,'2012-07-31 08:00:21.080656',NULL,NULL,0,2,2,54);
INSERT INTO "grampsdb_childref" VALUES(5,35,2,2,'2012-07-31 08:00:21.084137',NULL,NULL,0,2,2,66);
INSERT INTO "grampsdb_childref" VALUES(6,35,6,1,'2012-07-31 08:00:21.986535',NULL,NULL,0,2,2,42);
INSERT INTO "grampsdb_childref" VALUES(7,35,9,1,'2012-07-31 08:00:22.563023',NULL,NULL,0,2,2,28);
INSERT INTO "grampsdb_childref" VALUES(8,35,9,2,'2012-07-31 08:00:22.566562',NULL,NULL,0,2,2,6);
INSERT INTO "grampsdb_childref" VALUES(9,35,9,3,'2012-07-31 08:00:22.569992',NULL,NULL,0,2,2,51);
INSERT INTO "grampsdb_childref" VALUES(10,35,10,1,'2012-07-31 08:00:22.591504',NULL,NULL,0,2,2,9);
INSERT INTO "grampsdb_childref" VALUES(11,35,10,2,'2012-07-31 08:00:22.594928',NULL,NULL,0,2,2,38);
INSERT INTO "grampsdb_childref" VALUES(12,35,10,3,'2012-07-31 08:00:22.598454',NULL,NULL,0,2,2,47);
INSERT INTO "grampsdb_childref" VALUES(13,35,10,4,'2012-07-31 08:00:22.602056',NULL,NULL,0,2,2,49);
INSERT INTO "grampsdb_childref" VALUES(14,35,10,5,'2012-07-31 08:00:22.605598',NULL,NULL,0,2,2,43);
INSERT INTO "grampsdb_childref" VALUES(15,35,10,6,'2012-07-31 08:00:22.609155',NULL,NULL,0,2,2,8);
INSERT INTO "grampsdb_childref" VALUES(16,35,10,7,'2012-07-31 08:00:22.612600',NULL,NULL,0,2,2,29);
INSERT INTO "grampsdb_childref" VALUES(17,35,10,8,'2012-07-31 08:00:22.616031',NULL,NULL,0,2,2,35);
INSERT INTO "grampsdb_childref" VALUES(18,35,10,9,'2012-07-31 08:00:22.619578',NULL,NULL,0,2,2,65);
INSERT INTO "grampsdb_childref" VALUES(19,35,11,1,'2012-07-31 08:00:22.987325',NULL,NULL,0,2,2,22);
INSERT INTO "grampsdb_childref" VALUES(20,35,11,2,'2012-07-31 08:00:22.992404',NULL,NULL,0,2,2,3);
INSERT INTO "grampsdb_childref" VALUES(21,35,11,3,'2012-07-31 08:00:22.997541',NULL,NULL,0,2,2,11);
INSERT INTO "grampsdb_childref" VALUES(22,35,12,1,'2012-07-31 08:00:23.305897',NULL,NULL,0,2,2,7);
INSERT INTO "grampsdb_childref" VALUES(23,35,12,2,'2012-07-31 08:00:23.309482',NULL,NULL,0,2,2,17);
INSERT INTO "grampsdb_childref" VALUES(24,35,12,3,'2012-07-31 08:00:23.313498',NULL,NULL,0,2,2,36);
INSERT INTO "grampsdb_childref" VALUES(25,35,16,1,'2012-07-31 08:00:23.905330',NULL,NULL,0,2,2,13);
INSERT INTO "grampsdb_childref" VALUES(26,35,16,2,'2012-07-31 08:00:23.908767',NULL,NULL,0,2,2,68);
INSERT INTO "grampsdb_childref" VALUES(27,35,16,3,'2012-07-31 08:00:23.912194',NULL,NULL,0,2,2,31);
INSERT INTO "grampsdb_childref" VALUES(28,35,16,4,'2012-07-31 08:00:23.915730',NULL,NULL,0,2,2,1);
INSERT INTO "grampsdb_childref" VALUES(29,35,16,5,'2012-07-31 08:00:23.919194',NULL,NULL,0,2,2,40);
INSERT INTO "grampsdb_childref" VALUES(30,35,17,1,'2012-07-31 08:00:23.938407',NULL,NULL,0,2,2,33);
INSERT INTO "grampsdb_childref" VALUES(31,35,17,2,'2012-07-31 08:00:23.941842',NULL,NULL,0,2,2,5);
INSERT INTO "grampsdb_childref" VALUES(32,35,17,3,'2012-07-31 08:00:23.945262',NULL,NULL,0,2,2,52);
INSERT INTO "grampsdb_childref" VALUES(33,35,17,4,'2012-07-31 08:00:23.948791',NULL,NULL,0,2,2,69);
INSERT INTO "grampsdb_childref" VALUES(34,35,17,5,'2012-07-31 08:00:23.952237',NULL,NULL,0,2,2,4);
INSERT INTO "grampsdb_childref" VALUES(35,35,18,1,'2012-07-31 08:00:24.067046',NULL,NULL,0,2,2,63);
INSERT INTO "grampsdb_childref" VALUES(36,35,18,2,'2012-07-31 08:00:24.070608',NULL,NULL,0,2,2,25);
INSERT INTO "grampsdb_childref" VALUES(37,35,18,3,'2012-07-31 08:00:24.074031',NULL,NULL,0,2,2,67);
INSERT INTO "grampsdb_childref" VALUES(38,35,18,4,'2012-07-31 08:00:24.077463',NULL,NULL,0,2,2,45);
INSERT INTO "grampsdb_childref" VALUES(39,35,18,5,'2012-07-31 08:00:24.080972',NULL,NULL,0,2,2,14);
INSERT INTO "grampsdb_childref" VALUES(40,35,18,6,'2012-07-31 08:00:24.084403',NULL,NULL,0,2,2,21);
INSERT INTO "grampsdb_childref" VALUES(41,35,18,7,'2012-07-31 08:00:24.087839',NULL,NULL,0,2,2,57);
INSERT INTO "grampsdb_childref" VALUES(42,35,18,8,'2012-07-31 08:00:24.091385',NULL,NULL,0,2,2,50);
INSERT INTO "grampsdb_childref" VALUES(43,35,18,9,'2012-07-31 08:00:24.094850',NULL,NULL,0,2,2,30);
INSERT INTO "grampsdb_childref" VALUES(44,35,18,10,'2012-07-31 08:00:24.098293',NULL,NULL,0,2,2,15);
INSERT INTO "grampsdb_childref" VALUES(45,35,18,11,'2012-07-31 08:00:24.102065',NULL,NULL,0,2,2,12);
INSERT INTO "grampsdb_childref" VALUES(46,35,19,1,'2012-07-31 08:00:24.256136',NULL,NULL,0,2,2,56);
INSERT INTO "grampsdb_childref" VALUES(47,35,19,2,'2012-07-31 08:00:24.260043',NULL,NULL,0,2,2,46);
INSERT INTO "grampsdb_childref" VALUES(48,35,19,3,'2012-07-31 08:00:24.264008',NULL,NULL,0,2,2,24);
INSERT INTO "grampsdb_childref" VALUES(49,35,19,4,'2012-07-31 08:00:24.268035',NULL,NULL,0,2,2,23);
CREATE TABLE "grampsdb_mediaref" (
    "id" integer NOT NULL PRIMARY KEY,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    "order" integer unsigned NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "x1" integer NOT NULL,
    "y1" integer NOT NULL,
    "x2" integer NOT NULL,
    "y2" integer NOT NULL,
    "ref_object_id" integer NOT NULL REFERENCES "grampsdb_media" ("id")
);
CREATE TABLE "grampsdb_report" (
    "id" integer NOT NULL PRIMARY KEY,
    "gramps_id" text,
    "name" text,
    "handle" text,
    "report_type" text,
    "options" text
);
INSERT INTO "grampsdb_report" VALUES(1,'R0001','Ahnentafel Report','ancestor_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(2,'R0002','birthday_report','birthday_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(3,'R0003','custom_text','custom_text','report',NULL);
INSERT INTO "grampsdb_report" VALUES(4,'R0004','descend_report','descend_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(5,'R0005','det_ancestor_report','det_ancestor_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(6,'R0006','det_descendant_report','det_descendant_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(7,'R0007','endofline_report','endofline_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(8,'R0008','family_group','family_group','report',NULL);
INSERT INTO "grampsdb_report" VALUES(9,'R0009','indiv_complete','indiv_complete','report',NULL);
INSERT INTO "grampsdb_report" VALUES(10,'R0010','kinship_report','kinship_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(11,'R0011','tag_report','tag_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(12,'R0012','number_of_ancestors_report','number_of_ancestors_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(13,'R0013','place_report','place_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(14,'R0014','simple_book_title','simple_book_title','report',NULL);
INSERT INTO "grampsdb_report" VALUES(15,'R0015','summary','summary','report',NULL);
INSERT INTO "grampsdb_report" VALUES(16,'R0016','Export','gedcom_export','export','off=ged');
INSERT INTO "grampsdb_report" VALUES(17,'R0017','Gramps XML Export','ex_gpkg','export','off=gramps');
INSERT INTO "grampsdb_report" VALUES(18,'R0018','Import','im_ged','import','iff=ged
i=http://arborvita.free.fr/Kennedy/Kennedy.ged');
INSERT INTO "grampsdb_report" VALUES(19,'R0019','Gramps package (portable XML) Import','im_gpkg','import','iff=gramps
i=http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/example/gramps/example.gramps');
CREATE TABLE "grampsdb_result" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" text,
    "filename" text,
    "run_on" datetime NOT NULL,
    "run_by" text,
    "status" text
);
CREATE INDEX grampsdb_noteref_object_id_object_type_id 
       ON grampsdb_noteref (object_id, object_type_id);
CREATE INDEX grampsdb_eventref_object_id_object_type_id 
       ON grampsdb_eventref (object_id, object_type_id);
CREATE INDEX grampsdb_childref_object_id_object_type_id 
       ON grampsdb_childref (object_id, object_type_id);
CREATE INDEX "auth_permission_e4470c6e" ON "auth_permission" ("content_type_id");
CREATE INDEX "auth_group_permissions_bda51c3c" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_1e014c8f" ON "auth_group_permissions" ("permission_id");
CREATE INDEX "auth_user_user_permissions_fbfc09f1" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_1e014c8f" ON "auth_user_user_permissions" ("permission_id");
CREATE INDEX "auth_user_groups_fbfc09f1" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_bda51c3c" ON "auth_user_groups" ("group_id");
CREATE INDEX "auth_message_fbfc09f1" ON "auth_message" ("user_id");
CREATE INDEX "django_session_c25c2c28" ON "django_session" ("expire_date");
CREATE INDEX "django_admin_log_fbfc09f1" ON "django_admin_log" ("user_id");
CREATE INDEX "django_admin_log_e4470c6e" ON "django_admin_log" ("content_type_id");
CREATE INDEX "grampsdb_profile_71d2bf68" ON "grampsdb_profile" ("theme_type_id");
CREATE INDEX "grampsdb_myfamilies_21b911c5" ON "grampsdb_myfamilies" ("person_id");
CREATE INDEX "grampsdb_myfamilies_ccf20756" ON "grampsdb_myfamilies" ("family_id");
CREATE INDEX "grampsdb_myparentfamilies_21b911c5" ON "grampsdb_myparentfamilies" ("person_id");
CREATE INDEX "grampsdb_myparentfamilies_ccf20756" ON "grampsdb_myparentfamilies" ("family_id");
CREATE INDEX "grampsdb_person_tags_21b911c5" ON "grampsdb_person_tags" ("person_id");
CREATE INDEX "grampsdb_person_tags_3747b463" ON "grampsdb_person_tags" ("tag_id");
CREATE INDEX "grampsdb_person_79775e9" ON "grampsdb_person" ("gender_type_id");
CREATE INDEX "grampsdb_person_3a672176" ON "grampsdb_person" ("birth_id");
CREATE INDEX "grampsdb_person_f406392b" ON "grampsdb_person" ("death_id");
CREATE INDEX "grampsdb_family_tags_ccf20756" ON "grampsdb_family_tags" ("family_id");
CREATE INDEX "grampsdb_family_tags_3747b463" ON "grampsdb_family_tags" ("tag_id");
CREATE INDEX "grampsdb_family_656bfb9c" ON "grampsdb_family" ("father_id");
CREATE INDEX "grampsdb_family_3800eb51" ON "grampsdb_family" ("mother_id");
CREATE INDEX "grampsdb_family_8a163760" ON "grampsdb_family" ("family_rel_type_id");
CREATE INDEX "grampsdb_citation_89f89e85" ON "grampsdb_citation" ("source_id");
CREATE INDEX "grampsdb_event_cb60d07f" ON "grampsdb_event" ("event_type_id");
CREATE INDEX "grampsdb_event_c4391d6c" ON "grampsdb_event" ("place_id");
CREATE INDEX "grampsdb_repository_5f9de118" ON "grampsdb_repository" ("repository_type_id");
CREATE INDEX "grampsdb_media_tags_11f50c51" ON "grampsdb_media_tags" ("media_id");
CREATE INDEX "grampsdb_media_tags_3747b463" ON "grampsdb_media_tags" ("tag_id");
CREATE INDEX "grampsdb_note_tags_14a186ec" ON "grampsdb_note_tags" ("note_id");
CREATE INDEX "grampsdb_note_tags_3747b463" ON "grampsdb_note_tags" ("tag_id");
CREATE INDEX "grampsdb_note_8e504316" ON "grampsdb_note" ("note_type_id");
CREATE INDEX "grampsdb_surname_5489fd8b" ON "grampsdb_surname" ("name_origin_type_id");
CREATE INDEX "grampsdb_surname_632e075f" ON "grampsdb_surname" ("name_id");
CREATE INDEX "grampsdb_name_bbd280b5" ON "grampsdb_name" ("name_type_id");
CREATE INDEX "grampsdb_name_af013a48" ON "grampsdb_name" ("sort_as_id");
CREATE INDEX "grampsdb_name_f5d4d029" ON "grampsdb_name" ("display_as_id");
CREATE INDEX "grampsdb_name_21b911c5" ON "grampsdb_name" ("person_id");
CREATE INDEX "grampsdb_lds_a9c5135e" ON "grampsdb_lds" ("lds_type_id");
CREATE INDEX "grampsdb_lds_c4391d6c" ON "grampsdb_lds" ("place_id");
CREATE INDEX "grampsdb_lds_5934a803" ON "grampsdb_lds" ("famc_id");
CREATE INDEX "grampsdb_lds_44224078" ON "grampsdb_lds" ("status_id");
CREATE INDEX "grampsdb_lds_21b911c5" ON "grampsdb_lds" ("person_id");
CREATE INDEX "grampsdb_lds_ccf20756" ON "grampsdb_lds" ("family_id");
CREATE INDEX "grampsdb_markup_14a186ec" ON "grampsdb_markup" ("note_id");
CREATE INDEX "grampsdb_markup_b91c6fdf" ON "grampsdb_markup" ("styled_text_tag_type_id");
CREATE INDEX "grampsdb_sourcedatamap_89f89e85" ON "grampsdb_sourcedatamap" ("source_id");
CREATE INDEX "grampsdb_citationdatamap_958eecfd" ON "grampsdb_citationdatamap" ("citation_id");
CREATE INDEX "grampsdb_address_21b911c5" ON "grampsdb_address" ("person_id");
CREATE INDEX "grampsdb_address_6a730446" ON "grampsdb_address" ("repository_id");
CREATE INDEX "grampsdb_location_c4391d6c" ON "grampsdb_location" ("place_id");
CREATE INDEX "grampsdb_location_b213c1e9" ON "grampsdb_location" ("address_id");
CREATE INDEX "grampsdb_url_9655b856" ON "grampsdb_url" ("url_type_id");
CREATE INDEX "grampsdb_url_21b911c5" ON "grampsdb_url" ("person_id");
CREATE INDEX "grampsdb_url_c4391d6c" ON "grampsdb_url" ("place_id");
CREATE INDEX "grampsdb_url_6a730446" ON "grampsdb_url" ("repository_id");
CREATE INDEX "grampsdb_attribute_ec24ebcd" ON "grampsdb_attribute" ("attribute_type_id");
CREATE INDEX "grampsdb_attribute_ae71a55b" ON "grampsdb_attribute" ("object_type_id");
CREATE INDEX "grampsdb_log_ae71a55b" ON "grampsdb_log" ("object_type_id");
CREATE INDEX "grampsdb_noteref_ae71a55b" ON "grampsdb_noteref" ("object_type_id");
CREATE INDEX "grampsdb_noteref_d8532d97" ON "grampsdb_noteref" ("ref_object_id");
CREATE INDEX "grampsdb_eventref_ae71a55b" ON "grampsdb_eventref" ("object_type_id");
CREATE INDEX "grampsdb_eventref_d8532d97" ON "grampsdb_eventref" ("ref_object_id");
CREATE INDEX "grampsdb_eventref_6ae08856" ON "grampsdb_eventref" ("role_type_id");
CREATE INDEX "grampsdb_repositoryref_ae71a55b" ON "grampsdb_repositoryref" ("object_type_id");
CREATE INDEX "grampsdb_repositoryref_d8532d97" ON "grampsdb_repositoryref" ("ref_object_id");
CREATE INDEX "grampsdb_repositoryref_4fd76720" ON "grampsdb_repositoryref" ("source_media_type_id");
CREATE INDEX "grampsdb_personref_ae71a55b" ON "grampsdb_personref" ("object_type_id");
CREATE INDEX "grampsdb_personref_d8532d97" ON "grampsdb_personref" ("ref_object_id");
CREATE INDEX "grampsdb_citationref_ae71a55b" ON "grampsdb_citationref" ("object_type_id");
CREATE INDEX "grampsdb_citationref_958eecfd" ON "grampsdb_citationref" ("citation_id");
CREATE INDEX "grampsdb_childref_ae71a55b" ON "grampsdb_childref" ("object_type_id");
CREATE INDEX "grampsdb_childref_6f3234de" ON "grampsdb_childref" ("father_rel_type_id");
CREATE INDEX "grampsdb_childref_de957003" ON "grampsdb_childref" ("mother_rel_type_id");
CREATE INDEX "grampsdb_childref_d8532d97" ON "grampsdb_childref" ("ref_object_id");
CREATE INDEX "grampsdb_mediaref_ae71a55b" ON "grampsdb_mediaref" ("object_type_id");
CREATE INDEX "grampsdb_mediaref_d8532d97" ON "grampsdb_mediaref" ("ref_object_id");
COMMIT;
