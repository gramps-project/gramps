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
INSERT INTO "auth_user" VALUES(1,'admin','','','bugs@gramps-project.org','sha1$e6c7c$4b1fb71d557b37a04eecffaf9c61f086b1ca35f5',1,1,1,'2012-08-10 08:16:43.964714','2012-08-10 08:16:43.964714');
INSERT INTO "auth_user" VALUES(2,'admin1','','','bugs@gramps-project.org','sha1$f466d$20b08567aa61bd56d523ee497f215119ffe8c4fa',1,1,1,'2012-08-10 08:16:49.093450','2012-08-10 08:16:49.093450');
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
INSERT INTO "grampsdb_config" VALUES(3,'db_created','database creation date/time','str','2012-08-10 08:12');
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
CREATE TABLE "grampsdb_myparentfamilies" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "family_id" integer NOT NULL,
    "order" integer unsigned NOT NULL
);
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
INSERT INTO "grampsdb_report" VALUES(12,'R0012','number_of_ancestors','number_of_ancestors','report',NULL);
INSERT INTO "grampsdb_report" VALUES(13,'R0013','place_report','place_report','report',NULL);
INSERT INTO "grampsdb_report" VALUES(14,'R0014','simple_book_title','simple_book_title','report',NULL);
INSERT INTO "grampsdb_report" VALUES(15,'R0015','summary','summary','report',NULL);
INSERT INTO "grampsdb_report" VALUES(16,'R0016','Export','gedcom_export','export','off=ged');
INSERT INTO "grampsdb_report" VALUES(17,'R0017','Gramps XML Export','ex_gpkg','export','off=gramps');
INSERT INTO "grampsdb_report" VALUES(18,'R0018','Import','im_ged','import','iff=ged
i=http://arborvita.free.fr/Kennedy/Kennedy.ged');
INSERT INTO "grampsdb_report" VALUES(19,'R0019','Gramps package (portable XML) Import','im_gpkg','import','iff=gramps
i=http://svn.code.sf.net/p/gramps/code/trunk/example/gramps/example.gramps');
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
