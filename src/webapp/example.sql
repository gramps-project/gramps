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
INSERT INTO "auth_permission" VALUES(94,'Can add person',32,'add_person');
INSERT INTO "auth_permission" VALUES(95,'Can change person',32,'change_person');
INSERT INTO "auth_permission" VALUES(96,'Can delete person',32,'delete_person');
INSERT INTO "auth_permission" VALUES(97,'Can add family',33,'add_family');
INSERT INTO "auth_permission" VALUES(98,'Can change family',33,'change_family');
INSERT INTO "auth_permission" VALUES(99,'Can delete family',33,'delete_family');
INSERT INTO "auth_permission" VALUES(100,'Can add citation',34,'add_citation');
INSERT INTO "auth_permission" VALUES(101,'Can change citation',34,'change_citation');
INSERT INTO "auth_permission" VALUES(102,'Can delete citation',34,'delete_citation');
INSERT INTO "auth_permission" VALUES(103,'Can add source',35,'add_source');
INSERT INTO "auth_permission" VALUES(104,'Can change source',35,'change_source');
INSERT INTO "auth_permission" VALUES(105,'Can delete source',35,'delete_source');
INSERT INTO "auth_permission" VALUES(106,'Can add event',36,'add_event');
INSERT INTO "auth_permission" VALUES(107,'Can change event',36,'change_event');
INSERT INTO "auth_permission" VALUES(108,'Can delete event',36,'delete_event');
INSERT INTO "auth_permission" VALUES(109,'Can add repository',37,'add_repository');
INSERT INTO "auth_permission" VALUES(110,'Can change repository',37,'change_repository');
INSERT INTO "auth_permission" VALUES(111,'Can delete repository',37,'delete_repository');
INSERT INTO "auth_permission" VALUES(112,'Can add place',38,'add_place');
INSERT INTO "auth_permission" VALUES(113,'Can change place',38,'change_place');
INSERT INTO "auth_permission" VALUES(114,'Can delete place',38,'delete_place');
INSERT INTO "auth_permission" VALUES(115,'Can add media',39,'add_media');
INSERT INTO "auth_permission" VALUES(116,'Can change media',39,'change_media');
INSERT INTO "auth_permission" VALUES(117,'Can delete media',39,'delete_media');
INSERT INTO "auth_permission" VALUES(118,'Can add note',40,'add_note');
INSERT INTO "auth_permission" VALUES(119,'Can change note',40,'change_note');
INSERT INTO "auth_permission" VALUES(120,'Can delete note',40,'delete_note');
INSERT INTO "auth_permission" VALUES(121,'Can add surname',41,'add_surname');
INSERT INTO "auth_permission" VALUES(122,'Can change surname',41,'change_surname');
INSERT INTO "auth_permission" VALUES(123,'Can delete surname',41,'delete_surname');
INSERT INTO "auth_permission" VALUES(124,'Can add name',42,'add_name');
INSERT INTO "auth_permission" VALUES(125,'Can change name',42,'change_name');
INSERT INTO "auth_permission" VALUES(126,'Can delete name',42,'delete_name');
INSERT INTO "auth_permission" VALUES(127,'Can add lds',43,'add_lds');
INSERT INTO "auth_permission" VALUES(128,'Can change lds',43,'change_lds');
INSERT INTO "auth_permission" VALUES(129,'Can delete lds',43,'delete_lds');
INSERT INTO "auth_permission" VALUES(130,'Can add markup',44,'add_markup');
INSERT INTO "auth_permission" VALUES(131,'Can change markup',44,'change_markup');
INSERT INTO "auth_permission" VALUES(132,'Can delete markup',44,'delete_markup');
INSERT INTO "auth_permission" VALUES(133,'Can add source datamap',45,'add_sourcedatamap');
INSERT INTO "auth_permission" VALUES(134,'Can change source datamap',45,'change_sourcedatamap');
INSERT INTO "auth_permission" VALUES(135,'Can delete source datamap',45,'delete_sourcedatamap');
INSERT INTO "auth_permission" VALUES(136,'Can add citation datamap',46,'add_citationdatamap');
INSERT INTO "auth_permission" VALUES(137,'Can change citation datamap',46,'change_citationdatamap');
INSERT INTO "auth_permission" VALUES(138,'Can delete citation datamap',46,'delete_citationdatamap');
INSERT INTO "auth_permission" VALUES(139,'Can add address',47,'add_address');
INSERT INTO "auth_permission" VALUES(140,'Can change address',47,'change_address');
INSERT INTO "auth_permission" VALUES(141,'Can delete address',47,'delete_address');
INSERT INTO "auth_permission" VALUES(142,'Can add location',48,'add_location');
INSERT INTO "auth_permission" VALUES(143,'Can change location',48,'change_location');
INSERT INTO "auth_permission" VALUES(144,'Can delete location',48,'delete_location');
INSERT INTO "auth_permission" VALUES(145,'Can add url',49,'add_url');
INSERT INTO "auth_permission" VALUES(146,'Can change url',49,'change_url');
INSERT INTO "auth_permission" VALUES(147,'Can delete url',49,'delete_url');
INSERT INTO "auth_permission" VALUES(148,'Can add attribute',50,'add_attribute');
INSERT INTO "auth_permission" VALUES(149,'Can change attribute',50,'change_attribute');
INSERT INTO "auth_permission" VALUES(150,'Can delete attribute',50,'delete_attribute');
INSERT INTO "auth_permission" VALUES(151,'Can add note ref',51,'add_noteref');
INSERT INTO "auth_permission" VALUES(152,'Can change note ref',51,'change_noteref');
INSERT INTO "auth_permission" VALUES(153,'Can delete note ref',51,'delete_noteref');
INSERT INTO "auth_permission" VALUES(154,'Can add event ref',52,'add_eventref');
INSERT INTO "auth_permission" VALUES(155,'Can change event ref',52,'change_eventref');
INSERT INTO "auth_permission" VALUES(156,'Can delete event ref',52,'delete_eventref');
INSERT INTO "auth_permission" VALUES(157,'Can add repository ref',53,'add_repositoryref');
INSERT INTO "auth_permission" VALUES(158,'Can change repository ref',53,'change_repositoryref');
INSERT INTO "auth_permission" VALUES(159,'Can delete repository ref',53,'delete_repositoryref');
INSERT INTO "auth_permission" VALUES(160,'Can add person ref',54,'add_personref');
INSERT INTO "auth_permission" VALUES(161,'Can change person ref',54,'change_personref');
INSERT INTO "auth_permission" VALUES(162,'Can delete person ref',54,'delete_personref');
INSERT INTO "auth_permission" VALUES(163,'Can add citation ref',55,'add_citationref');
INSERT INTO "auth_permission" VALUES(164,'Can change citation ref',55,'change_citationref');
INSERT INTO "auth_permission" VALUES(165,'Can delete citation ref',55,'delete_citationref');
INSERT INTO "auth_permission" VALUES(166,'Can add child ref',56,'add_childref');
INSERT INTO "auth_permission" VALUES(167,'Can change child ref',56,'change_childref');
INSERT INTO "auth_permission" VALUES(168,'Can delete child ref',56,'delete_childref');
INSERT INTO "auth_permission" VALUES(169,'Can add media ref',57,'add_mediaref');
INSERT INTO "auth_permission" VALUES(170,'Can change media ref',57,'change_mediaref');
INSERT INTO "auth_permission" VALUES(171,'Can delete media ref',57,'delete_mediaref');
INSERT INTO "auth_permission" VALUES(172,'Can add report',58,'add_report');
INSERT INTO "auth_permission" VALUES(173,'Can change report',58,'change_report');
INSERT INTO "auth_permission" VALUES(174,'Can delete report',58,'delete_report');
INSERT INTO "auth_permission" VALUES(175,'Can add result',59,'add_result');
INSERT INTO "auth_permission" VALUES(176,'Can change result',59,'change_result');
INSERT INTO "auth_permission" VALUES(177,'Can delete result',59,'delete_result');
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
INSERT INTO "auth_user" VALUES(1,'admin','','','bugs@gramps-project.org','sha1$28213$1af0843de942e46b52d35ccd4d6abba8d3e6ec0f',1,1,1,'2012-05-29 10:40:31.683403','2012-05-29 10:36:56.848133');
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
INSERT INTO "django_content_type" VALUES(32,'person','grampsdb','person');
INSERT INTO "django_content_type" VALUES(33,'family','grampsdb','family');
INSERT INTO "django_content_type" VALUES(34,'citation','grampsdb','citation');
INSERT INTO "django_content_type" VALUES(35,'source','grampsdb','source');
INSERT INTO "django_content_type" VALUES(36,'event','grampsdb','event');
INSERT INTO "django_content_type" VALUES(37,'repository','grampsdb','repository');
INSERT INTO "django_content_type" VALUES(38,'place','grampsdb','place');
INSERT INTO "django_content_type" VALUES(39,'media','grampsdb','media');
INSERT INTO "django_content_type" VALUES(40,'note','grampsdb','note');
INSERT INTO "django_content_type" VALUES(41,'surname','grampsdb','surname');
INSERT INTO "django_content_type" VALUES(42,'name','grampsdb','name');
INSERT INTO "django_content_type" VALUES(43,'lds','grampsdb','lds');
INSERT INTO "django_content_type" VALUES(44,'markup','grampsdb','markup');
INSERT INTO "django_content_type" VALUES(45,'source datamap','grampsdb','sourcedatamap');
INSERT INTO "django_content_type" VALUES(46,'citation datamap','grampsdb','citationdatamap');
INSERT INTO "django_content_type" VALUES(47,'address','grampsdb','address');
INSERT INTO "django_content_type" VALUES(48,'location','grampsdb','location');
INSERT INTO "django_content_type" VALUES(49,'url','grampsdb','url');
INSERT INTO "django_content_type" VALUES(50,'attribute','grampsdb','attribute');
INSERT INTO "django_content_type" VALUES(51,'note ref','grampsdb','noteref');
INSERT INTO "django_content_type" VALUES(52,'event ref','grampsdb','eventref');
INSERT INTO "django_content_type" VALUES(53,'repository ref','grampsdb','repositoryref');
INSERT INTO "django_content_type" VALUES(54,'person ref','grampsdb','personref');
INSERT INTO "django_content_type" VALUES(55,'citation ref','grampsdb','citationref');
INSERT INTO "django_content_type" VALUES(56,'child ref','grampsdb','childref');
INSERT INTO "django_content_type" VALUES(57,'media ref','grampsdb','mediaref');
INSERT INTO "django_content_type" VALUES(58,'report','grampsdb','report');
INSERT INTO "django_content_type" VALUES(59,'result','grampsdb','result');
CREATE TABLE "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" datetime NOT NULL
);
INSERT INTO "django_session" VALUES('ab7e9cdb5b50c75d3b771b1e9f56ead3','MmU1MjliMDM2NzcyODdjNmJlOTgzMGFiYzc2MjFkMmViYWFiOTIzMjqAAn1xAShVEl9hdXRoX3Vz
ZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED
VQ1fYXV0aF91c2VyX2lkcQRLAXUu
','2012-06-12 10:40:31.799239');
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
    "css_theme" varchar(40) NOT NULL
);
INSERT INTO "grampsdb_profile" VALUES(1,1,'Web_Mainz.css');
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
INSERT INTO "grampsdb_eventtype" VALUES(47,'Immi',0);
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
CREATE TABLE "grampsdb_config" (
    "id" integer NOT NULL PRIMARY KEY,
    "setting" varchar(25) NOT NULL,
    "description" text NOT NULL,
    "value_type" varchar(25) NOT NULL,
    "value" text NOT NULL
);
INSERT INTO "grampsdb_config" VALUES(1,'sitename','site name of family tree','str','Gramps-Connect');
INSERT INTO "grampsdb_config" VALUES(2,'db_version','database scheme version','str','0.6.0');
INSERT INTO "grampsdb_config" VALUES(3,'db_created','database creation date/time','str','2012-05-29 10:29');
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
CREATE TABLE "grampsdb_person_families" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "family_id" integer NOT NULL,
    UNIQUE ("person_id", "family_id")
);
INSERT INTO "grampsdb_person_families" VALUES(1,1,10);
INSERT INTO "grampsdb_person_families" VALUES(2,2,10);
INSERT INTO "grampsdb_person_families" VALUES(3,3,15);
INSERT INTO "grampsdb_person_families" VALUES(4,4,1);
INSERT INTO "grampsdb_person_families" VALUES(5,5,5);
INSERT INTO "grampsdb_person_families" VALUES(6,7,1);
INSERT INTO "grampsdb_person_families" VALUES(7,8,6);
INSERT INTO "grampsdb_person_families" VALUES(8,9,3);
INSERT INTO "grampsdb_person_families" VALUES(9,10,11);
INSERT INTO "grampsdb_person_families" VALUES(10,11,13);
INSERT INTO "grampsdb_person_families" VALUES(11,13,14);
INSERT INTO "grampsdb_person_families" VALUES(12,14,2);
INSERT INTO "grampsdb_person_families" VALUES(13,15,11);
INSERT INTO "grampsdb_person_families" VALUES(14,17,12);
INSERT INTO "grampsdb_person_families" VALUES(15,20,6);
INSERT INTO "grampsdb_person_families" VALUES(16,21,3);
INSERT INTO "grampsdb_person_families" VALUES(17,24,7);
INSERT INTO "grampsdb_person_families" VALUES(18,26,9);
INSERT INTO "grampsdb_person_families" VALUES(19,27,4);
INSERT INTO "grampsdb_person_families" VALUES(20,29,13);
INSERT INTO "grampsdb_person_families" VALUES(21,31,9);
INSERT INTO "grampsdb_person_families" VALUES(22,32,8);
INSERT INTO "grampsdb_person_families" VALUES(23,33,4);
INSERT INTO "grampsdb_person_families" VALUES(24,35,2);
INSERT INTO "grampsdb_person_families" VALUES(25,36,12);
INSERT INTO "grampsdb_person_families" VALUES(26,39,14);
INSERT INTO "grampsdb_person_families" VALUES(27,40,15);
INSERT INTO "grampsdb_person_families" VALUES(28,41,5);
INSERT INTO "grampsdb_person_families" VALUES(29,41,7);
INSERT INTO "grampsdb_person_families" VALUES(30,42,8);
CREATE TABLE "grampsdb_person_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "grampsdb_tag" ("id"),
    UNIQUE ("person_id", "tag_id")
);
CREATE TABLE "grampsdb_person_parent_families" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "family_id" integer NOT NULL,
    UNIQUE ("person_id", "family_id")
);
INSERT INTO "grampsdb_person_parent_families" VALUES(1,2,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(2,6,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(3,7,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(4,8,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(5,9,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(6,10,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(7,11,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(8,12,9);
INSERT INTO "grampsdb_person_parent_families" VALUES(9,13,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(10,14,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(11,16,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(12,18,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(13,19,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(14,22,9);
INSERT INTO "grampsdb_person_parent_families" VALUES(15,23,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(16,25,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(17,26,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(18,28,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(19,30,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(20,34,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(21,36,4);
INSERT INTO "grampsdb_person_parent_families" VALUES(22,37,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(23,38,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(24,40,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(25,41,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(26,42,11);
CREATE TABLE "grampsdb_person" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "cache" text,
    "gender_type_id" integer NOT NULL REFERENCES "grampsdb_gendertype" ("id"),
    "probably_alive" bool NOT NULL,
    "birth_id" integer,
    "death_id" integer,
    "birth_ref_index" integer NOT NULL,
    "death_ref_index" integer NOT NULL
);
INSERT INTO "grampsdb_person" VALUES(1,'3XMT6DJVLX4BSJ8T9B','I0038','2012-05-29 11:56:37.345806','2007-12-20 19:35:26',NULL,0,'KFMnM1hNVDZESlZMWDRCU0o4VDlCJwpWSTAwMzgKcDEKSTAKKEkwMAoobChsTlZLZXJzdGluYQpw
MgoobHAzCihWSGFuc2RvdHRlcgpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5h
bWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSTEKSTAKKGxwNgooSTAwCihsKGxWYTcwMWU4ZmU3ZTA0
YzZhOGNkNgooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmE3MDFlOGZlODAzNjZlYjA2ZGQK
KEkxClZQcmltYXJ5CnR0cDgKYShscDkKVkdZTVQ2RDhXWVJPRVVIWDBJTgpwMTAKYShsKGwobChs
KGwobChsKGxJMTE5ODE5NzMyNgoodEkwMAoobHRwMTEKLg==
',3,0,38,56,0,1);
INSERT INTO "grampsdb_person" VALUES(2,'9YNT6DXDSDPO56MX19','I0022','2012-05-29 11:56:37.401534','2007-12-20 19:35:26',NULL,0,'KFMnOVlOVDZEWERTRFBPNTZNWDE5JwpWSTAwMjIKcDEKSTEKKEkwMAoobChsTlZNYXJ0aW4KcDIK
KGxwMwooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFtZQpwNQp0
VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZGYzOTY0OTkwOGE0
CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmRmNTIyNGZiZGM5ZQooSTEKVlBy
aW1hcnkKdHRwOAphKEkwMAoobChsVmE3MDFlOGZkZjZkNmI1MWU3YWQKKEkxClZQcmltYXJ5CnR0
cDkKYShscDEwClZHWU1UNkQ4V1lST0VVSFgwSU4KcDExCmEobHAxMgpWTkJNVDZENldCWk9ESlJY
T0cKcDEzCmEobChsKGwobChsKGwobHAxNApWYWVmMzA3OGE0NTc1N2M3OWMyMgpwMTUKYUkxMTk4
MTk3MzI2Cih0STAwCihsdHAxNgou
',2,0,85,5,0,1);
INSERT INTO "grampsdb_person" VALUES(3,'VNMT6DM95BAHK1X04I','I0031','2012-05-29 11:56:37.450365','2007-12-20 19:35:26',NULL,0,'KFMnVk5NVDZETTk1QkFISzFYMDRJJwpWSTAwMzEKcDEKSTAKKEkwMAoobChsTlZNYXJqb3JpZQpw
MgoobHAzCihWT2htYW4KVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1lCnA1
CnRWCkkwCkkwClYKVgpWCnQobEkxCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlNDU3NzM3YWIx
MTQKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZhNzAxZThmZTQ3YTBlZjgzNDQ5CihJMQpW
UHJpbWFyeQp0dHA4CmEobHA5ClZVR01UNkRVODJCUDVEM0lQTzMKcDEwCmEobChsKGwobChsKGwo
bChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDExCi4=
',3,0,23,9,0,1);
INSERT INTO "grampsdb_person" VALUES(4,'Y5NT6DLKFG3SBM9QQ4','I0034','2012-05-29 11:56:37.494193','2007-12-20 19:35:26',NULL,0,'KFMnWTVOVDZETEtGRzNTQk05UVE0JwpWSTAwMzQKcDEKSTAKKEkwMAoobChsTlZBbGljZSBQYXVs
YQoobHAyCihWUGVya2lucwpWCkkwMQooSTEKVgp0Vgp0cDMKYVYKVgooSTIKVkJpcnRoIE5hbWUK
dFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDQKKEkwMAoobChsVmE3MDFlOGZlNTljNzIzMGIz
YmQKKEkxClZQcmltYXJ5CnR0cDUKYShscDYKVjFITVQ2RE5XVFNQWElMMkZETQpwNwphKGwobChs
KGwobChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHA4Ci4=
',3,1,54,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(5,'ZBMT6DX6U16KP4ESHL','I0016','2012-05-29 11:56:37.542548','2007-12-20 19:35:26',NULL,0,'KFMnWkJNVDZEWDZVMTZLUDRFU0hMJwpWSTAwMTYKcDEKSTAKKEkwMAoobChsTlZKZW5uaWZlcgpw
MgoobHAzCihWQW5kZXJzb24KVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1l
CnA1CnRWCkkwCkkwClYKVgpWCnQobEkxCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZkYzJhMGY2
YTA3YmEKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZhNzAxZThmZGM0NDRlY2JmYTNjCihJ
MQpWUHJpbWFyeQp0dHA4CmEobHA5ClZHRE1UNkQ2Q1dNVTlOVzVCT04KcDEwCmEobChsKGwobChs
KGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDExCi4=
',3,0,81,68,0,1);
INSERT INTO "grampsdb_person" VALUES(6,'0ONT6DJS5KD5W6EA1P','I0004','2012-05-29 11:56:37.585113','2007-12-20 19:35:26',NULL,0,'KFMnME9OVDZESlM1S0Q1VzZFQTFQJwpWSTAwMDQKcDEKSTEKKEkwMAoobChsTlZJbmdlbWFuCnAy
CihscDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUKcDUK
dFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlOGVhMDZjN2Zi
YTQKKEkxClZQcmltYXJ5CnR0cDcKYShsKGxwOApWTkJNVDZENldCWk9ESlJYT0cKcDkKYShsKGwo
bChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDEwCi4=
',2,1,39,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(7,'2GMT6DXW6RJVMKLQEH','I0018','2012-05-29 11:56:37.628363','2007-12-20 19:35:26',NULL,0,'KFMnMkdNVDZEWFc2UkpWTUtMUUVIJwpWSTAwMTgKcDEKSTEKKEkwMAoobChsTlZKb2huIEhqYWxt
YXIKcDIKKGxwMwooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFt
ZQpwNQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYTcwMWU4ZmRkMGY1
MjBjNmQ4NwooSTEKVlByaW1hcnkKdHRwNwphKGxwOApWMUhNVDZETldUU1BYSUwyRkRNCnA5CmEo
bHAxMApWVUdNVDZEVTgyQlA1RDNJUE8zCnAxMQphKGwobChsKGwobChsKGxJMTE5ODE5NzMyNgoo
dEkwMAoobHRwMTIKLg==
',2,1,17,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(8,'CLMT6DTNTB1PFIXZPC','I0015','2012-05-29 11:56:37.676524','2007-12-20 19:35:26',NULL,0,'KFMnQ0xNVDZEVE5UQjFQRklYWlBDJwpWSTAwMTUKcDEKSTEKKEkwMAoobChsTlZHdXMKcDIKKGxw
MwooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFtZQpwNQp0VgpJ
MApJMApWClYKVgp0KGxJMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZGJiOTE2ZWUyNDFiCihJ
MQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmRiZDQyYWY4NTVjMgooSTEKVlByaW1h
cnkKdHRwOAphKGxwOQpWTU1NVDZENk5HTk81WUVSU0xNCnAxMAphKGxwMTEKVktLTVQ2RDVLV0Yx
VlAwM0s0QgpwMTIKYShsKGwobChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDEzCi4=
',2,0,80,33,0,1);
INSERT INTO "grampsdb_person" VALUES(9,'DJNT6D3IOTYV1HTLO1','I0003','2012-05-29 11:56:37.725453','2007-12-20 19:35:26',NULL,0,'KFMnREpOVDZEM0lPVFlWMUhUTE8xJwpWSTAwMDMKcDEKSTEKKEkwMAoobChsTlZNYWduZXMKcDIK
KGxwMwooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFtZQpwNQp0
VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZTM1NTIzMzVjOGM2
CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmUzNzAwOWI3OTUwNgooSTEKVlBy
aW1hcnkKdHRwOAphKGxwOQpWRlpMVDZEMFFVME1DMjAwUDFPCnAxMAphKGxwMTEKVkdZTVQ2RDhX
WVJPRVVIWDBJTgpwMTIKYShsKGwobChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDEzCi4=
',2,0,20,21,0,1);
INSERT INTO "grampsdb_person" VALUES(10,'J0NT6D9BY50LEA4VGY','I0024','2012-05-29 11:56:37.798247','2007-12-20 19:35:26',NULL,0,'KFMnSjBOVDZEOUJZNTBMRUE0VkdZJwpWSTAwMjQKcDEKSTEKKEkwMAoobChsTlZHdXN0YWYKcDIK
KGxwMwooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwNAphVlNyLgpwNQpWCihJMgpWQmlydGggTmFt
ZQpwNgp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA3CihJMDAKKGwobFZhNzAxZThmZTA1MDdh
YzA0MTM3CihJMQpWUHJpbWFyeQp0dHA4CmEoSTAwCihsKGxWYTcwMWU4ZmUwNzE1NTE0YzE1ZQoo
STEKVlByaW1hcnkKdHRwOQphKEkwMAoobChsVmE3MDFlOGZlMDhiNGM1MTJkYmQKKEkxClZQcmlt
YXJ5CnR0cDEwCmEoSTAwCihsKGxWYTcwMWU4ZmUwYTgwYjIyZmQ3YgooSTEKVlByaW1hcnkKdHRw
MTEKYShscDEyClZLS01UNkQ1S1dGMVZQMDNLNEIKcDEzCmEobHAxNApWR1lNVDZEOFdZUk9FVUhY
MElOCnAxNQphKGxwMTYKKEkwMAoobChsKGxWVzJOVDZEODdTUEk5VjdHMjdQCihJMApJMApJMApJ
MAp0dHAxNwphKEkwMAoobChsKGxWNDNOVDZESEgwVEJOMFBLVkMKKEkwCkkwCkkwCkkwCnR0cDE4
CmEobChsKGwobChsKGxJMTE5ODE5NzMyNgoodEkwMAoobHRwMTkKLg==
',2,0,35,6,0,1);
INSERT INTO "grampsdb_person" VALUES(11,'RDMT6D6113RO3X299I','I0019','2012-05-29 11:56:37.840054','2007-12-20 19:35:26',NULL,0,'KFMnUkRNVDZENjExM1JPM1gyOTlJJwpWSTAwMTkKcDEKSTEKKEkwMAoobChsTlZFcmljIExsb3lk
CnAyCihscDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUK
cDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZkZDgyNTg4
YTIxMTAKKEkxClZQcmltYXJ5CnR0cDcKYShscDgKVlJGTVQ2RDZYQjczRUZXRkhBQQpwOQphKGxw
MTAKVlM3TVQ2RDFKU0dYOVBaTzI3RgpwMTEKYShsKGwobChsKGwobChsSTExOTgxOTczMjYKKHRJ
MDAKKGx0cDEyCi4=
',2,1,4,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(12,'SKNT6D7FA4WHUUE7Z6','I0002','2012-05-29 11:56:37.887519','2007-12-20 19:35:26',NULL,0,'KFMnU0tOVDZEN0ZBNFdIVVVFN1o2JwpWSTAwMDIKcDEKSTAKKEkwMAoobChsTlZBbWJlciBNYXJp
ZQpwMgoobHAzCihWU21pdGgKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1l
CnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZGRlMzA3
ODZiNDhiCihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmRkZmUzM2M0MTg0MAoo
STEKVlByaW1hcnkKdHRwOAphKGwobHA5ClZDR05UNkRWMDJEMENRVEdCQU8KcDEwCmEobChsKGwo
bChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMQou
',3,1,82,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(13,'SQNT6DPEBXJPNWNCPX','I0033','2012-05-29 11:56:37.929142','2007-12-20 19:35:26',NULL,0,'KFMnU1FOVDZEUEVCWEpQTldOQ1BYJwpWSTAwMzMKcDEKSTEKKEkwMAoobChsTlZMbG95ZApwMgoo
bHAzCihWU21pdGgKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1lCnA1CnRW
CkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZTUzYTc2ZTE1YzM5
CihJMQpWUHJpbWFyeQp0dHA3CmEobHA4ClZTN01UNkQxSlNHWDlQWk8yN0YKcDkKYShscDEwClZN
VU1UNkRPSEtNV0w3TExRVkEKcDExCmEobChsKGwobChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihs
dHAxMgou
',2,1,53,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(14,'SYMT6DIHTYHLWHEE2K','I0026','2012-05-29 11:56:37.975809','2007-12-20 19:35:26',NULL,0,'KFMnU1lNVDZESUhUWUhMV0hFRTJLJwpWSTAwMjYKcDEKSTAKKEkwMAoobChsTlZLaXJzdGkgTWFy
aWUKcDIKKGxwMwooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFt
ZQpwNQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZTE4MTIz
MDBhZmE3CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmUxOWE1NTkwOGY1MQoo
STEKVlByaW1hcnkKdHRwOAphKGxwOQpWODBOVDZEUzZMS0lMVExFWklHCnAxMAphKGxwMTEKVktL
TVQ2RDVLV0YxVlAwM0s0QgpwMTIKYShsKGwobChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0
cDEzCi4=
',3,0,49,19,0,1);
INSERT INTO "grampsdb_person" VALUES(15,'VHNT6DQCEELKZP0M2W','I0000','2012-05-29 11:56:38.022349','2007-12-20 19:35:26',NULL,0,'KFMnVkhOVDZEUUNFRUxLWlAwTTJXJwpWSTAwMDAKcDEKSTAKKEkwMAoobChsTlZBbm5hCnAyCihs
cDMKKFZIYW5zZG90dGVyClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFtZQpw
NQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZDhlYTI3Zjk5
NzA0CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmQ5MDY3MmJiNGVjZQooSTEK
VlByaW1hcnkKdHRwOAphKGxwOQpWS0tNVDZENUtXRjFWUDAzSzRCCnAxMAphKGwobChsKGwobChs
KGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMQou
',3,0,1,79,0,1);
INSERT INTO "grampsdb_person" VALUES(16,'W6NT6DAWXC9FUOHYI2','I0009','2012-05-29 11:56:38.064990','2007-12-20 19:35:26',NULL,0,'KFMnVzZOVDZEQVdYQzlGVU9IWUkyJwpWSTAwMDkKcDEKSTEKKEkwMAoobChsTlZFbWlsCnAyCihs
cDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUKcDUKdFYK
STAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlYzA5NTA3OWU2YmUK
KEkxClZQcmltYXJ5CnR0cDcKYShsKGxwOApWR1lNVDZEOFdZUk9FVUhYMElOCnA5CmEobChsKGwo
bChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMAou
',2,1,13,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(17,'XBNT6DUEXL3CM228BN','I0036','2012-05-29 11:56:38.116620','2007-12-20 19:35:26',NULL,0,'KFMnWEJOVDZEVUVYTDNDTTIyOEJOJwpWSTAwMzYKcDEKSTAKKEkwMAoobChsTlZFbG5hCnAyCihs
cDMKKFZKZWZmZXJzb24KVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1lCnA1
CnRWCkkwCkkwClYKVgpWCnQobEkxCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlNjYyMGI3ZTA3
ZDQKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZhNzAxZThmZTY3YTNiOTc2M2Y5CihJMQpW
UHJpbWFyeQp0dHA4CmEoSTAwCihsKGxWYTcwMWU4ZmU2OTc2Njc5MmIxMgooSTEKVlByaW1hcnkK
dHRwOQphKGxwMTAKVk5CTVQ2RDZXQlpPREpSWE9HCnAxMQphKGwobChsKGwobChsKGwobEkxMTk4
MTk3MzI2Cih0STAwCihsdHAxMgou
',3,0,10,72,0,1);
INSERT INTO "grampsdb_person" VALUES(18,'XWNT6DP0HAPXFDCGY8','I0021','2012-05-29 11:56:38.163215','2007-12-20 19:35:26',NULL,0,'KFMnWFdOVDZEUDBIQVBYRkRDR1k4JwpWSTAwMjEKcDEKSTEKKEkwMAoobChsTlZIamFsbWFyCnAy
CihscDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUKcDUK
dFYKSTAKSTAKVgpWClYKdChsSTEKSTAKKGxwNgooSTAwCihsKGxWYTcwMWU4ZmRlY2IzYWJjZjg2
ZAooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmE3MDFlOGZkZWU0MmE0Y2E0ZmIKKEkxClZQ
cmltYXJ5CnR0cDgKYShsKGxwOQpWS0tNVDZENUtXRjFWUDAzSzRCCnAxMAphKGwobChsKGwobChs
KGxJMTE5ODE5NzMyNgoodEkwMAoobHRwMTEKLg==
',2,0,47,84,0,1);
INSERT INTO "grampsdb_person" VALUES(19,'YMMT6DJYFFJ38JZTNN','I0014','2012-05-29 11:56:38.204969','2007-12-20 19:35:26',NULL,0,'KFMnWU1NVDZESllGRkozOEpaVE5OJwpWSTAwMTQKcDEKSTAKKEkwMAoobChsTlZNYXJqb3JpZSBM
ZWUKKGxwMgooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGggTmFtZQp0
VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNAooSTAwCihsKGxWYTcwMWU4ZmRiNWM0Mjg5NzEz
NgooSTEKVlByaW1hcnkKdHRwNQphKGwobHA2ClZVR01UNkRVODJCUDVEM0lQTzMKcDcKYShsKGwo
bChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDgKLg==
',3,1,32,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(20,'ZUMT6D4W8L3JZLJ5I1','I0013','2012-05-29 11:56:38.246794','2007-12-20 19:35:26',NULL,0,'KFMnWlVNVDZENFc4TDNKWkxKNUkxJwpWSTAwMTMKcDEKSTAKKEkwMAoobChsTlZFdmVseW4KcDIK
KGxwMwooVk1pY2hhZWxzClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFtZQpw
NQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYTcwMWU4ZmRiMGEyZmFh
NTRiNQooSTEKVlByaW1hcnkKdHRwNwphKGxwOApWTU1NVDZENk5HTk81WUVSU0xNCnA5CmEobChs
KGwobChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDEwCi4=
',3,1,16,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(21,'5XLT6DXJ1J9NNI3QNT','I0028','2012-05-29 11:56:38.293493','2007-12-20 19:35:26',NULL,0,'KFMnNVhMVDZEWEoxSjlOTkkzUU5UJwpWSTAwMjgKcDEKSTAKKEkwMAoobChsTlZBbm5hCnAyCihs
cDMKKFZTdHJlaWZmZXJ0ClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFtZQpw
NQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZTI2NTBlNGM0
NzU0CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmUyODA3NzY0OGQzOQooSTEK
VlByaW1hcnkKdHRwOAphKGxwOQpWRlpMVDZEMFFVME1DMjAwUDFPCnAxMAphKGwobChsKGwobChs
KGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMQou
',3,0,7,88,0,1);
INSERT INTO "grampsdb_person" VALUES(22,'EMNT6DXUP8PCCU5MQG','I0005','2012-05-29 11:56:38.345689','2007-12-20 19:35:26',NULL,0,'KFMnRU1OVDZEWFVQOFBDQ1U1TVFHJwpWSTAwMDUKcDEKSTEKKEkwMAoobChsTlZNYXNvbiBNaWNo
YWVsCnAyCihscDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5h
bWUKcDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlOWY4
MTc3YjNhOGEKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZhNzAxZThmZWExODFkMGI0ZWNm
CihJMQpWUHJpbWFyeQp0dHA4CmEobChscDkKVkNHTlQ2RFYwMkQwQ1FUR0JBTwpwMTAKYShscDEx
CihJMDAKKGwobChsVk1OTlQ2RDI3RzNMOFNHVlFKVgooSTAKSTAKSTAKSTAKdHRwMTIKYShsKGwo
bChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMwou
',2,1,40,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(23,'K3NT6DMBYAXNTXOO3F','I0020','2012-05-29 11:56:38.392870','2007-12-20 19:35:26',NULL,0,'KFMnSzNOVDZETUJZQVhOVFhPTzNGJwpWSTAwMjAKcDEKSTEKKEkwMAoobChsTlZDYXJsIEVtaWwK
KGxwMgooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGggTmFtZQp0VgpJ
MApJMApWClYKVgp0KGxJMQpJMAoobHA0CihJMDAKKGwobFZhNzAxZThmZGU1ZDBjYzY0ODRlCihJ
MQpWUHJpbWFyeQp0dHA1CmEoSTAwCihsKGxWYTcwMWU4ZmRlNzU3MjNkMGM4NQooSTEKVlByaW1h
cnkKdHRwNgphKGwobHA3ClZLS01UNkQ1S1dGMVZQMDNLNEIKcDgKYShsKGwobChsKGwobChsSTEx
OTgxOTczMjYKKHRJMDAKKGx0cDkKLg==
',2,0,46,83,0,1);
INSERT INTO "grampsdb_person" VALUES(24,'NDNT6D8O7D3QRKP07N','I0017','2012-05-29 11:56:38.445670','2007-12-20 19:35:26',NULL,0,'KFMnTkROVDZEOE83RDNRUktQMDdOJwpWSTAwMTcKcDEKSTAKKEkwMAoobChsTlZMaWxsaWUgSGFy
cmlldApwMgoobHAzCihWSm9uZXMKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBO
YW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEkxCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZkYzlj
NzZlZGUyNDAKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZhNzAxZThmZGNiYjE1MGQ4Yzg5
CihJMQpWUHJpbWFyeQp0dHA4CmEobHA5ClZNVU1UNkRPSEtNV0w3TExRVkEKcDEwCmEobChsKGwo
bChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDExCi4=
',3,0,34,44,0,1);
INSERT INTO "grampsdb_person" VALUES(25,'PGNT6DESJOESEQNP22','I0001','2012-05-29 11:56:38.493176','2007-12-20 19:35:26',NULL,0,'KFMnUEdOVDZERVNKT0VTRVFOUDIyJwpWSTAwMDEKcDEKSTEKKEkwMAoobChsTlZLZWl0aCBMbG95
ZApwMgoobHAzCihWU21pdGgKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1l
CnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZDk2MzI0
NWViZmVmCihJMQpWUHJpbWFyeQp0dHA3CmEobChscDgKVlM3TVQ2RDFKU0dYOVBaTzI3RgpwOQph
KGxwMTAKKEkwMAoobChsKGxWSEhOVDZENzNRUEtDMEtXSzJZCihJMApJMApJMApJMAp0dHAxMQph
KGwobChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDEyCi4=
',2,1,14,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(26,'PSNT6D0DDHJOBCFJWX','I0037','2012-05-29 11:56:38.562679','2007-12-20 19:35:26',NULL,0,'KFMnUFNOVDZEMERESEpPQkNGSldYJwpWSTAwMzcKcDEKSTEKKEkwMAoobHAyClZjMmJmZDE5MmU1
ZTMyYTBjMzc1CnAzCmEobE5WRWR3aW4gTWljaGFlbAoobHA0CihWU21pdGgKVgpJMDEKKEkxClYK
dFYKdHA1CmFWClYKKEkyClZCaXJ0aCBOYW1lCnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2
CihJMDAKKGwobFZhNzAxZThmZTcwMzc0N2RiODlkCihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihs
KGxwOAooSTAwCihsKGwoSTEwClZBZ2UKdFYyMwp0cDkKYVZhNzAxZThmZTczMzRhYWI3NDlkCihJ
MQpWUHJpbWFyeQp0dHAxMAphKEkwMAoobChsVmE3MDFlOGZlNzViNDc0ZjE4NTMKKEkxClZQcmlt
YXJ5CnR0cDExCmEoSTAwCihsKGxWYTcwMWU4ZmU3Nzc0MDRhYzIzMAooSTEKVlByaW1hcnkKdHRw
MTIKYShscDEzClZDR05UNkRWMDJEMENRVEdCQU8KcDE0CmEobHAxNQpWMUhNVDZETldUU1BYSUwy
RkRNCnAxNgphKGxwMTcKKEkwMAoobChsKGxWQ1ZOVDZESEc1SUNaMVVHVU85CihJMApJMApJMApJ
MAp0dHAxOAphKGwobChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDE5Ci4=
',2,1,37,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(27,'RRNT6D5K0MU6QUAMAY','I0025','2012-05-29 11:56:38.604227','2007-12-20 19:35:26',NULL,0,'KFMnUlJOVDZENUswTVU2UVVBTUFZJwpWSTAwMjUKcDEKSTAKKEkwMAoobChsTlZNYXJ0YQpwMgoo
bHAzCihWRXJpY3Nkb3R0ZXIKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1l
CnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZTExZjBh
NTU0Yjc2CihJMQpWUHJpbWFyeQp0dHA3CmEobHA4ClZHQk1UNkRKVUdKOTQ1M1JXNUkKcDkKYShs
KGwobChsKGwobChsKGxJMTE5ODE5NzMyNgoodEkwMAoobHRwMTAKLg==
',3,1,87,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(28,'RZLT6DH4XGWLSK1Q0Z','I0029','2012-05-29 11:56:38.650885','2007-12-20 19:35:26',NULL,0,'KFMnUlpMVDZESDRYR1dMU0sxUTBaJwpWSTAwMjkKcDEKSTEKKEkwMAoobChsTlZDcmFpZyBQZXRl
cgpwMgoobHAzCihWU21pdGgKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1l
CnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZTJlMjc2
NjIwODVmCihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmUyZmIyZTg0NWU2OQoo
STEKVlByaW1hcnkKdHRwOAphKGwobHA5ClZTN01UNkQxSlNHWDlQWk8yN0YKcDEwCmEobChsKGwo
bChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMQou
',2,1,36,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(29,'SVNT6DMAE9YEH6MICF','I0032','2012-05-29 11:56:38.692824','2007-12-20 19:35:26',NULL,0,'KFMnU1ZOVDZETUFFOVlFSDZNSUNGJwpWSTAwMzIKcDEKSTAKKEkwMAoobChsTlZEYXJjeQoobHAy
CihWSG9ybmUKVgpJMDEKKEkxClYKdFYKdHAzCmFWClYKKEkyClZCaXJ0aCBOYW1lCnRWCkkwCkkw
ClYKVgpWCnQobEktMQpJMAoobHA0CihJMDAKKGwobFZhNzAxZThmZTRkZTJkNTI0ZmI1CihJMQpW
UHJpbWFyeQp0dHA1CmEobHA2ClZSRk1UNkQ2WEI3M0VGV0ZIQUEKcDcKYShsKGwobChsKGwobChs
KGxJMTE5ODE5NzMyNgoodEkwMAoobHRwOAou
',3,1,71,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(30,'UANT6D04R90NFDKTBP','I0035','2012-05-29 11:56:38.734282','2007-12-20 19:35:26',NULL,0,'KFMnVUFOVDZEMDRSOTBORkRLVEJQJwpWSTAwMzUKcDEKSTEKKEkwMAoobChsTlZMYXJzIFBldGVy
CnAyCihscDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUK
cDUKdFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlNWZiNmIy
Y2QwMTUKKEkxClZQcmltYXJ5CnR0cDcKYShsKGxwOApWUkZNVDZENlhCNzNFRldGSEFBCnA5CmEo
bChsKGwobChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMAou
',2,1,24,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(31,'VENT6DO89X29B69M6','I0030','2012-05-29 11:56:38.792101','2007-12-20 19:35:26',NULL,0,'KFMnVkVOVDZETzg5WDI5QjY5TTYnClZJMDAzMApwMQpJMAooSTAwCihsKGxOVkphbmljZSBBbm4K
cDIKKGxwMwooVkFkYW1zClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFtZQpw
NQp0VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNgooSTAwCihsKGxWYTcwMWU4ZmUzZDM1MTEz
YTlhNwooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmE3MDFlOGZlM2VlNTgxODAyZDgKKEkx
ClZQcmltYXJ5CnR0cDgKYShJMDAKKGwobFZhNzAxZThmZTQwNDUzYzdhOGM2CihJMQpWUHJpbWFy
eQp0dHA5CmEobHAxMApWQ0dOVDZEVjAyRDBDUVRHQkFPCnAxMQphKGwobChsKGwobChsKGwobEkx
MTk4MTk3MzI2Cih0STAwCihsdHAxMgou
',3,1,52,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(32,'VVMT6D4M4VVILJ8Q1S','I0012','2012-05-29 11:56:38.845537','2007-12-20 19:35:26',NULL,0,'KFMnVlZNVDZENE00VlZJTEo4UTFTJwpWSTAwMTIKcDEKSTEKKEkwMAoobChsTlZIZXJtYW4gSnVs
aXVzCihscDIKKFZOaWVsc2VuClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGggTmFt
ZQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA0CihJMDAKKGwobFZhNzAxZThmZGFhMjU2Yjdk
N2EwCihJMQpWUHJpbWFyeQp0dHA1CmEoSTAwCihsKGxWYTcwMWU4ZmRhYmE1MGRmYWZhMQooSTEK
VlByaW1hcnkKdHRwNgphKGxwNwpWWFJNVDZEU0FaRzJZMzdFVFE1CnA4CmEobChsKGwobChsKGwo
bChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDkKLg==
',2,0,2,3,0,1);
INSERT INTO "grampsdb_person" VALUES(33,'X4NT6DHD3QU8ADPPZT','I0027','2012-05-29 11:56:38.893735','2007-12-20 19:35:26',NULL,0,'KFMnWDROVDZESEQzUVU4QURQUFpUJwpWSTAwMjcKcDEKSTEKKEkwMAoobChsTlZJbmdlbWFuCnAy
CihscDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUKcDUK
dFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlMjA3MmMxZmE1
MzIKKEkxClZQcmltYXJ5CnR0cDcKYShscDgKVkdCTVQ2REpVR0o5NDUzUlc1SQpwOQphKGwobChs
KGwobChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMAou
',2,1,50,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(34,'YONT6DJYH1B5NKQTR7','I0007','2012-05-29 11:56:38.947152','2007-12-20 19:35:26',NULL,0,'KFMnWU9OVDZESllIMUI1TktRVFI3JwpWSTAwMDcKcDEKSTAKKEkwMAoobChsTlZJbmdhcgpwMgoo
bHAzCihWU21pdGgKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1lCnA1CnRW
CkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZWFkZjczNmQ2NWY5
CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYTcwMWU4ZmU3MzM0YWFiNzQ5ZAooSTcKVldp
dG5lc3MKdHRwOAphKGwobHA5ClZOQk1UNkQ2V0JaT0RKUlhPRwpwMTAKYShsKGwobChsKGwobChs
STExOTgxOTczMjYKKHRJMDAKKGx0cDExCi4=
',3,1,12,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(35,'YPNT6DU0BWARYZ2ZZM','I0006','2012-05-29 11:56:38.994547','2007-12-20 19:35:26',NULL,0,'KFMnWVBOVDZEVTBCV0FSWVoyWlpNJwpWSTAwMDYKcDEKSTEKKEkwMAoobChsTlZFZHdpbgpwMgoo
bHAzCihWV2lsbGFyZApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUKcDUK
dFYKSTAKSTAKVgpWClYKdChsSS0xCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlYTgwM2UwOWEw
MGEKKEkxClZQcmltYXJ5CnR0cDcKYShscDgKVjgwTlQ2RFM2TEtJTFRMRVpJRwpwOQphKGwobChs
KGwobChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMAou
',2,1,29,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(36,'48MT6DRK875RYW6APJ','I0039','2012-05-29 11:56:39.044019','2007-12-20 19:35:26',NULL,0,'KFMnNDhNVDZEUks4NzVSWVc2QVBKJwpWSTAwMzkKcDEKSTEKKEkwMAoobChsTlZNYXJ0aW4KKGxw
MgooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGggTmFtZQp0VgpJMApJ
MApWClYKVgp0KGxJMQpJMAoobHA0CihJMDAKKGwobFZhNzAxZThmZTg2NjM1OWRjN2I1CihJMQpW
UHJpbWFyeQp0dHA1CmEoSTAwCihsKGxWYTcwMWU4ZmU4ODQzOTI0ZTE3OQooSTEKVlByaW1hcnkK
dHRwNgphKGxwNwpWTkJNVDZENldCWk9ESlJYT0cKcDgKYShscDkKVkdCTVQ2REpVR0o5NDUzUlc1
SQpwMTAKYShsKGwobChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDExCi4=
',2,0,26,57,0,1);
INSERT INTO "grampsdb_person" VALUES(37,'60OT6D7XUEURYJRN78','I0040','2012-05-29 11:56:39.091230','2007-12-20 19:35:26',NULL,0,'KFMnNjBPVDZEN1hVRVVSWUpSTjc4JwpWSTAwNDAKcDEKSTAKKEkwMAoobChsTlZNYXJqb3JpZSBB
bGljZQpwMgoobHAzCihWU21pdGgKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBO
YW1lCnA1CnRWCkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZTk0
ODE5YTIyN2ViCihJMQpWUHJpbWFyeQp0dHA3CmEobChscDgKVjFITVQ2RE5XVFNQWElMMkZETQpw
OQphKGxwMTAKKEkwMAoobChsKGxWWTBPVDZETTdGVzA2QTFTTE1TCihJMApJMApJMApJMAp0dHAx
MQphKGwobChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDEyCi4=
',3,1,27,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(38,'BSMT6D9XTIXAG0TCNL','I0011','2012-05-29 11:56:39.132783','2007-12-20 19:35:26',NULL,0,'KFMnQlNNVDZEOVhUSVhBRzBUQ05MJwpWSTAwMTEKcDEKSTAKKEkwMAoobChsTlZIYW5uYQpwMgoo
bHAzCihWU21pdGgKVgpJMDEKKEkxClYKdFYKdHA0CmFWClYKKEkyClZCaXJ0aCBOYW1lCnA1CnRW
CkkwCkkwClYKVgpWCnQobEktMQpJMAoobHA2CihJMDAKKGwobFZhNzAxZThmZGE0OTQ2NzAzMGE0
CihJMQpWUHJpbWFyeQp0dHA3CmEobChscDgKVk5CTVQ2RDZXQlpPREpSWE9HCnA5CmEobChsKGwo
bChsKGwobEkxMTk4MTk3MzI2Cih0STAwCihsdHAxMAou
',3,1,15,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(39,'C1OT6DUBMZ3HAD998D','I0041','2012-05-29 11:56:39.174664','2007-12-20 19:35:26',NULL,0,'KFMnQzFPVDZEVUJNWjNIQUQ5OThEJwpWSTAwNDEKcDEKSTAKKEkwMAoobChsTlZKYW5pcyBFbGFp
bmUKKGxwMgooVkdyZWVuClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpWQmlydGggTmFtZQp0
VgpJMApJMApWClYKVgp0KGxJLTEKSTAKKGxwNAooSTAwCihsKGxWYTcwMWU4ZmU5YWIwMjYyM2Ri
MwooSTEKVlByaW1hcnkKdHRwNQphKGxwNgpWUzdNVDZEMUpTR1g5UFpPMjdGCnA3CmEobChsKGwo
bChsKGwobChsSTExOTgxOTczMjYKKHRJMDAKKGx0cDgKLg==
',3,1,28,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(40,'DHMT6D0PQJCVXWD1FT','I0008','2012-05-29 11:56:39.233545','2007-12-20 19:35:26',NULL,0,'KFMnREhNVDZEMFBRSkNWWFdEMUZUJwpWSTAwMDgKcDEKSTEKKEkwMAoobChsTlZIamFsbWFyCnAy
CihscDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUKcDUK
dFYKSTAKSTAKVgpWClYKdChsSTEKSTAKKGxwNgooSTAwCihsKGxWYTcwMWU4ZmViM2IwYzgzNDBm
NQooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmE3MDFlOGZlYjVjM2JkMjZlY2IKKEkxClZQ
cmltYXJ5CnR0cDgKYShJMDAKKGwobFZhNzAxZThmZWI3YjIwY2NmMDEwCihJMQpWUHJpbWFyeQp0
dHA5CmEoSTAwCihsKGxWYTcwMWU4ZmViOWY2NGJmY2ViMwooSTEKVlByaW1hcnkKdHRwMTAKYShs
cDExClZVR01UNkRVODJCUDVEM0lQTzMKcDEyCmEobHAxMwpWS0tNVDZENUtXRjFWUDAzSzRCCnAx
NAphKGwobChsKGwobChsKGxwMTUKVmFlZjMwNzhhOGVkNDcyZTBmOWMKcDE2CmFJMTE5ODE5NzMy
NgoodEkwMAoobHRwMTcKLg==
',2,0,30,74,0,1);
INSERT INTO "grampsdb_person" VALUES(41,'ETMT6DLEIYYGW8SHM5','I0010','2012-05-29 11:56:39.280680','2007-12-20 19:35:26',NULL,0,'KFMnRVRNVDZETEVJWVlHVzhTSE01JwpWSTAwMTAKcDEKSTEKKEkwMAoobChsTlZIYW5zIFBldGVy
CnAyCihscDMKKFZTbWl0aApWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUK
cDUKdFYKSTAKSTAKVgpWClYKdChsSTEKSTAKKGxwNgooSTAwCihsKGxWYTcwMWU4ZmQ5Y2I3Zjhk
N2VjNAooSTEKVlByaW1hcnkKdHRwNwphKEkwMAoobChsVmE3MDFlOGZkOWU1N2IzYzQ4ZmIKKEkx
ClZQcmltYXJ5CnR0cDgKYShscDkKVkdETVQ2RDZDV01VOU5XNUJPTgpwMTAKYVZNVU1UNkRPSEtN
V0w3TExRVkEKcDExCmEobHAxMgpWS0tNVDZENUtXRjFWUDAzSzRCCnAxMwphKGwobChsKGwobChs
KGxJMTE5ODE5NzMyNgoodEkwMAoobHRwMTQKLg==
',2,0,67,31,0,1);
INSERT INTO "grampsdb_person" VALUES(42,'NQMT6DX5NIOGMEGJA3','I0023','2012-05-29 11:56:39.327802','2007-12-20 19:35:26',NULL,0,'KFMnTlFNVDZEWDVOSU9HTUVHSkEzJwpWSTAwMjMKcDEKSTAKKEkwMAoobChsTlZBc3RyaWQgU2hl
cm1hbm5hIEF1Z3VzdGEKKGxwMgooVlNtaXRoClYKSTAxCihJMQpWCnRWCnRwMwphVgpWCihJMgpW
QmlydGggTmFtZQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA0CihJMDAKKGwobFZhNzAxZThm
ZGZkNTcwNmQwMDlmCihJMQpWUHJpbWFyeQp0dHA1CmEoSTAwCihsKGxWYTcwMWU4ZmRmZWQxNjY0
OGRjMwooSTEKVlByaW1hcnkKdHRwNgphKGxwNwpWWFJNVDZEU0FaRzJZMzdFVFE1CnA4CmEobHA5
ClZLS01UNkQ1S1dGMVZQMDNLNEIKcDEwCmEobChsKGwobChsKGwobEkxMTk4MTk3MzI2Cih0STAw
CihsdHAxMQou
',3,0,86,69,0,1);
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
    "cache" text,
    "father_id" integer REFERENCES "grampsdb_person" ("id"),
    "mother_id" integer REFERENCES "grampsdb_person" ("id"),
    "family_rel_type_id" integer NOT NULL REFERENCES "grampsdb_familyreltype" ("id")
);
INSERT INTO "grampsdb_family" VALUES(1,'1HMT6DNWTSPXIL2FDM','F0012','2012-05-29 11:56:39.369422','2007-12-20 19:35:26',NULL,0,'KFMnMUhNVDZETldUU1BYSUwyRkRNJwpWRjAwMTIKcDEKVjJHTVQ2RFhXNlJKVk1LTFFFSApwMgpW
WTVOVDZETEtGRzNTQk05UVE0CnAzCihscDQKKEkwMAoobChsVjYwT1Q2RDdYVUVVUllKUk43OAoo
STEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDUKYShJMDAKKGwobFZQU05UNkQwRERISk9CQ0ZKV1gK
KEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA2CmEoSTAKVk1hcnJpZWQKcDcKdChscDgKKEkwMAoo
bChsVmE3MDFlOGZlZGY4M2I2OWFjZjgKKEk4ClZGYW1pbHkKdHRwOQphKGwobChsKGwobEkxMTk4
MTk3MzI2Cih0STAwCnRwMTAKLg==
',7,4,5);
INSERT INTO "grampsdb_family" VALUES(2,'80NT6DS6LKILTLEZIG','F0004','2012-05-29 11:56:39.393066','2007-12-20 19:35:26',NULL,0,'KFMnODBOVDZEUzZMS0lMVExFWklHJwpWRjAwMDQKcDEKVllQTlQ2RFUwQldBUllaMlpaTQpwMgpW
U1lNVDZESUhUWUhMV0hFRTJLCnAzCihsKEkwClZNYXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZh
NzAxZThmZjAwNzEzZTBjNjZlCihJOApWRmFtaWx5CnR0cDYKYShsKGwobChsKGxJMTE5ODE5NzMy
NgoodEkwMAp0cDcKLg==
',35,14,5);
INSERT INTO "grampsdb_family" VALUES(3,'FZLT6D0QU0MC200P1O','F0011','2012-05-29 11:56:39.416797','2007-12-20 19:35:26',NULL,0,'KFMnRlpMVDZEMFFVME1DMjAwUDFPJwpWRjAwMTEKcDEKVkRKTlQ2RDNJT1RZVjFIVExPMQpwMgpW
NVhMVDZEWEoxSjlOTkkzUU5UCnAzCihsKEkwClZNYXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZh
NzAxZThmZWQ5ZDE4ZDczMDJmCihJOApWRmFtaWx5CnR0cDYKYShsKGwobChsKGxJMTE5ODE5NzMy
NgoodEkwMAp0cDcKLg==
',9,21,5);
INSERT INTO "grampsdb_family" VALUES(4,'GBMT6DJUGJ9453RW5I','F0001','2012-05-29 11:56:39.447322','2007-12-20 19:35:26',NULL,0,'KFMnR0JNVDZESlVHSjk0NTNSVzVJJwpWRjAwMDEKcDEKVlg0TlQ2REhEM1FVOEFEUFBaVApwMgpW
UlJOVDZENUswTVU2UVVBTUFZCnAzCihscDQKKEkwMAoobChsVjQ4TVQ2RFJLODc1UllXNkFQSgoo
STEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDUKYShJMApWTWFycmllZApwNgp0KGxwNwooSTAwCihs
KGxWYTcwMWU4ZmVjZDgwNGU0YzU0NAooSTgKVkZhbWlseQp0dHA4CmEobChsKGwobChsSTExOTgx
OTczMjYKKHRJMDAKdHA5Ci4=
',33,27,5);
INSERT INTO "grampsdb_family" VALUES(5,'GDMT6D6CWMU9NW5BON','F0014','2012-05-29 11:56:39.465718','2007-12-20 19:35:26',NULL,0,'KFMnR0RNVDZENkNXTVU5Tlc1Qk9OJwpWRjAwMTQKcDEKVkVUTVQ2RExFSVlZR1c4U0hNNQpwMgpW
WkJNVDZEWDZVMTZLUDRFU0hMCnAzCihsKEkwClZNYXJyaWVkCnA0CnQobChsKGwobChsKGxJMTE5
ODE5NzMyNgoodEkwMAp0cDUKLg==
',41,5,5);
INSERT INTO "grampsdb_family" VALUES(6,'MMMT6D6NGNO5YERSLM','F0007','2012-05-29 11:56:39.489410','2007-12-20 19:35:26',NULL,0,'KFMnTU1NVDZENk5HTk81WUVSU0xNJwpWRjAwMDcKcDEKVkNMTVQ2RFROVEIxUEZJWFpQQwpwMgpW
WlVNVDZENFc4TDNKWkxKNUkxCnAzCihsKEkwClZNYXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZh
NzAxZThmZjExNTI1ZDVhYWI4CihJOApWRmFtaWx5CnR0cDYKYShsKGwobChsKGxJMTE5ODE5NzMy
NgoodEkwMAp0cDcKLg==
',8,20,5);
INSERT INTO "grampsdb_family" VALUES(7,'MUMT6DOHKMWL7LLQVA','F0009','2012-05-29 11:56:39.514696','2007-12-20 19:35:26',NULL,0,'KFMnTVVNVDZET0hLTVdMN0xMUVZBJwpWRjAwMDkKcDEKVkVUTVQ2RExFSVlZR1c4U0hNNQpwMgpW
TkROVDZEOE83RDNRUktQMDdOCnAzCihscDQKKEkwMAoobChsVlNRTlQ2RFBFQlhKUE5XTkNQWAoo
STEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDUKYShJMApWTWFycmllZApwNgp0KGwobChsKGwobChs
STExOTgxOTczMjYKKHRJMDAKdHA3Ci4=
',41,24,5);
INSERT INTO "grampsdb_family" VALUES(8,'XRMT6DSAZG2Y37ETQ5','F0005','2012-05-29 11:56:39.538374','2007-12-20 19:35:26',NULL,0,'KFMnWFJNVDZEU0FaRzJZMzdFVFE1JwpWRjAwMDUKcDEKVlZWTVQ2RDRNNFZWSUxKOFExUwpwMgpW
TlFNVDZEWDVOSU9HTUVHSkEzCnAzCihsKEkwClZNYXJyaWVkCnA0CnQobHA1CihJMDAKKGwobFZh
NzAxZThmZjA1MTRiZDQ2ZDA4CihJOApWRmFtaWx5CnR0cDYKYShsKGwobChsKGxJMTE5ODE5NzMy
NgoodEkwMAp0cDcKLg==
',32,42,5);
INSERT INTO "grampsdb_family" VALUES(9,'CGNT6DV02D0CQTGBAO','F0013','2012-05-29 11:56:39.586643','2007-12-20 19:35:26',NULL,0,'KFMnQ0dOVDZEVjAyRDBDUVRHQkFPJwpWRjAwMTMKcDEKVlBTTlQ2RDBEREhKT0JDRkpXWApwMgpW
VkVOVDZETzg5WDI5QjY5TTYKcDMKKGxwNAooSTAwCihsKGxWRU1OVDZEWFVQOFBDQ1U1TVFHCihJ
MQpWQmlydGgKdChJMQpWQmlydGgKdHRwNQphKEkwMAoobChsVlNLTlQ2RDdGQTRXSFVVRTdaNgoo
STEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDYKYShJMApWTWFycmllZApwNwp0KGxwOAooSTAwCihs
KGxWYTcwMWU4ZmVlNjc0YWExMjkzNgooSTgKVkZhbWlseQp0dHA5CmEoSTAwCihsKGxWYTcwMWU4
ZmVlOTEzOWEwM2I3ZgooSTgKVkZhbWlseQp0dHAxMAphKGxwMTEKKEkwMAoobChsKGxWTU5OVDZE
MjdHM0w4U0dWUUpWCihJMApJMApJMApJMAp0dHAxMgphKGwobChsKGxJMTE5ODE5NzMyNgoodEkw
MAp0cDEzCi4=
',26,31,5);
INSERT INTO "grampsdb_family" VALUES(10,'GYMT6D8WYROEUHX0IN','F0002','2012-05-29 11:56:39.631493','2007-12-20 19:35:26',NULL,0,'KFMnR1lNVDZEOFdZUk9FVUhYMElOJwpWRjAwMDIKcDEKVjlZTlQ2RFhEU0RQTzU2TVgxOQpwMgpW
M1hNVDZESlZMWDRCU0o4VDlCCnAzCihscDQKKEkwMAoobChsVkRKTlQ2RDNJT1RZVjFIVExPMQoo
STEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDUKYShJMDAKKGwobFZXNk5UNkRBV1hDOUZVT0hZSTIK
KEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA2CmEoSTAwCihsKGxWSjBOVDZEOUJZNTBMRUE0VkdZ
CihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwNwphKEkwClZNYXJyaWVkCnA4CnQobHA5CihJMDAK
KGwobFZhNzAxZThmZWYzMjNiZTMwNWE0CihJOApWRmFtaWx5CnR0cDEwCmEobChsKGwobChsSTEx
OTgxOTczMjYKKHRJMDAKdHAxMQou
',2,1,5);
INSERT INTO "grampsdb_family" VALUES(11,'KKMT6D5KWF1VP03K4B','F0003','2012-05-29 11:56:39.703587','2007-12-20 19:35:26',NULL,0,'KFMnS0tNVDZENUtXRjFWUDAzSzRCJwpWRjAwMDMKcDEKVkowTlQ2RDlCWTUwTEVBNFZHWQpwMgpW
VkhOVDZEUUNFRUxLWlAwTTJXCnAzCihscDQKKEkwMAoobChsVlNZTVQ2RElIVFlITFdIRUUySwoo
STEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDUKYShJMDAKKGwobFZOUU1UNkRYNU5JT0dNRUdKQTMK
KEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA2CmEoSTAwCihsKGxWWFdOVDZEUDBIQVBYRkRDR1k4
CihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwNwphKEkwMAoobChsVkRITVQ2RDBQUUpDVlhXRDFG
VAooSTEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDgKYShJMDAKKGwobFZDTE1UNkRUTlRCMVBGSVha
UEMKKEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA5CmEoSTAwCihsKGxWSzNOVDZETUJZQVhOVFhP
TzNGCihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwMTAKYShJMDAKKGwobFZFVE1UNkRMRUlZWUdX
OFNITTUKKEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHAxMQphKEkwClZNYXJyaWVkCnAxMgp0KGxw
MTMKKEkwMAoobChsVmE3MDFlOGZlZjkzNGZlMTdhNDkKKEk4ClZGYW1pbHkKdHRwMTQKYShsKGwo
bChsKGxJMTE5ODE5NzMyNgoodEkwMAp0cDE1Ci4=
',10,15,5);
INSERT INTO "grampsdb_family" VALUES(12,'NBMT6D6WBZODJRXOG','F0000','2012-05-29 11:56:39.755690','2007-12-20 19:35:26',NULL,0,'KFMnTkJNVDZENldCWk9ESlJYT0cnClZGMDAwMApwMQpWNDhNVDZEUks4NzVSWVc2QVBKCnAyClZY
Qk5UNkRVRVhMM0NNMjI4Qk4KcDMKKGxwNAooSTAwCihsKGxWQlNNVDZEOVhUSVhBRzBUQ05MCihJ
MQpWQmlydGgKdChJMQpWQmlydGgKdHRwNQphKEkwMAoobChsVllPTlQ2REpZSDFCNU5LUVRSNwoo
STEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDYKYShJMDAKKGwobFYwT05UNkRKUzVLRDVXNkVBMVAK
KEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA3CmEoSTAwCihsKGxWOVlOVDZEWERTRFBPNTZNWDE5
CihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwOAphKEkwClZNYXJyaWVkCnA5CnQobHAxMAooSTAw
CihsKGxWYTcwMWU4ZmVjNjMwZDc0NDNiZQooSTgKVkZhbWlseQp0dHAxMQphKGwobChsKGwobEkx
MTk4MTk3MzI2Cih0STAwCnRwMTIKLg==
',36,17,5);
INSERT INTO "grampsdb_family" VALUES(13,'RFMT6D6XB73EFWFHAA','F0010','2012-05-29 11:56:39.793382','2007-12-20 19:35:26',NULL,0,'KFMnUkZNVDZENlhCNzNFRldGSEFBJwpWRjAwMTAKcDEKVlJETVQ2RDYxMTNSTzNYMjk5SQpwMgpW
U1ZOVDZETUFFOVlFSDZNSUNGCnAzCihscDQKKEkwMAoobChsVlVBTlQ2RDA0UjkwTkZES1RCUAoo
STIKVkFkb3B0ZWQKdChJMgpWQWRvcHRlZAp0dHA1CmEoSTAKVk1hcnJpZWQKcDYKdChscDcKKEkw
MAoobChsVmE3MDFlOGZlZDM5NjczYzQ2MzgKKEk4ClZGYW1pbHkKdHRwOAphKGwobChsKGwobEkx
MTk4MTk3MzI2Cih0STAwCnRwOQou
',11,29,5);
INSERT INTO "grampsdb_family" VALUES(14,'S7MT6D1JSGX9PZO27F','F0008','2012-05-29 11:56:39.843999','2007-12-20 19:35:26',NULL,0,'KFMnUzdNVDZEMUpTR1g5UFpPMjdGJwpWRjAwMDgKcDEKVlNRTlQ2RFBFQlhKUE5XTkNQWApwMgpW
QzFPVDZEVUJNWjNIQUQ5OThECnAzCihscDQKKEkwMAoobChsVlJETVQ2RDYxMTNSTzNYMjk5SQoo
STIKVkFkb3B0ZWQKdChJMgpWQWRvcHRlZAp0dHA1CmEoSTAwCihsKGxWUEdOVDZERVNKT0VTRVFO
UDIyCihJMQpWQmlydGgKdChJMQpWQmlydGgKdHRwNgphKEkwMAoobChsVlJaTFQ2REg0WEdXTFNL
MVEwWgooSTEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDcKYShJMApWTWFycmllZApwOAp0KGxwOQoo
STAwCihsKGxWYTcwMWU4ZmYxNWMyMDQ1ZTc1ZAooSTgKVkZhbWlseQp0dHAxMAphKGwobChsKGwo
bEkxMTk4MTk3MzI2Cih0STAwCnRwMTEKLg==
',13,39,5);
INSERT INTO "grampsdb_family" VALUES(15,'UGMT6DU82BP5D3IPO3','F0006','2012-05-29 11:56:39.884025','2007-12-20 19:35:26',NULL,0,'KFMnVUdNVDZEVTgyQlA1RDNJUE8zJwpWRjAwMDYKcDEKVkRITVQ2RDBQUUpDVlhXRDFGVApwMgpW
Vk5NVDZETTk1QkFISzFYMDRJCnAzCihscDQKKEkwMAoobChsVjJHTVQ2RFhXNlJKVk1LTFFFSAoo
STEKVkJpcnRoCnQoSTEKVkJpcnRoCnR0cDUKYShJMDAKKGwobFZZTU1UNkRKWUZGSjM4SlpUTk4K
KEkxClZCaXJ0aAp0KEkxClZCaXJ0aAp0dHA2CmEoSTAKVk1hcnJpZWQKcDcKdChscDgKKEkwMAoo
bChsVmE3MDFlOGZmMGI0NmNlYWJmYWIKKEk4ClZGYW1pbHkKdHRwOQphKGwobChsKGwobEkxMTk4
MTk3MzI2Cih0STAwCnRwMTAKLg==
',40,3,5);
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
    "cache" text,
    "confidence" integer,
    "page" varchar(50),
    "source_id" integer
);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,1,'c2bfd1928a72cb5efbf','BC0001','2012-05-29 11:56:36.648431','2012-05-29 11:55:41',NULL,0,NULL,2,'',3);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,2,'c2bfd192e5e32a0c375','BC0002','2012-05-29 11:56:36.655074','2012-05-29 11:55:41',NULL,0,NULL,2,'',1);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,3,'c2bfd1926771fca3f3e','BC0000','2012-05-29 11:56:36.661739','2012-05-29 11:55:41',NULL,0,NULL,2,'',4);
CREATE TABLE "grampsdb_source" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "cache" text,
    "title" varchar(50),
    "author" varchar(50),
    "pubinfo" varchar(50),
    "abbrev" varchar(50)
);
INSERT INTO "grampsdb_source" VALUES(1,'4TNT6DX8JM3BW08CUR','S0001','2012-05-29 11:56:39.894513','2007-12-20 19:35:26',NULL,0,'KFMnNFROVDZEWDhKTTNCVzA4Q1VSJwpWUzAwMDEKcDEKVkJpcnRoIENlcnRpZmljYXRlCnAyClYK
VgoobChsVgpJMTE5ODE5NzMyNgooZChsSTAwCnRwMwou
','Birth Certificate','','','');
INSERT INTO "grampsdb_source" VALUES(2,'ADOT6D7LW5QJGMWY1V','S0002','2012-05-29 11:56:39.902905','2007-12-20 19:35:26',NULL,0,'KFMnQURPVDZEN0xXNVFKR01XWTFWJwpWUzAwMDIKcDEKVkJpcnRoIFJlY29yZHMKcDIKVgpWCihs
KGxWCkkxMTk4MTk3MzI2CihkKGxJMDAKdHAzCi4=
','Birth Records','','','');
INSERT INTO "grampsdb_source" VALUES(3,'H9OT6DH812QJAQS5A8','S0000','2012-05-29 11:56:39.923375','2007-12-20 19:35:26',NULL,0,'KFMnSDlPVDZESDgxMlFKQVFTNUE4JwpWUzAwMDAKcDEKVk1hcnJpYWdlIENlcnRpZmljYWUKcDIK
VgpWCihscDMKVmFlZjMwNzhhYjFlMzdkNjAxODYKcDQKYShsVgpJMTE5ODE5NzMyNgooZChscDUK
KChsVmE3MDFlOTlmOTNlNTQzNGY2ZjMKVndoYXQtMzIxLWV2ZXIKKEkxMQpWUGhvdG8KdEkwMAp0
cDYKYSgobFZhNzAxZWFkMTI4NDE1MjFjZDRkClZub3RoaW5nLTAKKEk4ClZNYW51c2NyaXB0CnRJ
MDAKdHA3CmFJMDAKdHA4Ci4=
','Marriage Certificae','','','');
INSERT INTO "grampsdb_source" VALUES(4,'VTNT6DYLDJMSJSCJMU','S0003','2012-05-29 11:56:39.937748','2007-12-20 19:35:26',NULL,0,'KFMnVlROVDZEWUxESk1TSlNDSk1VJwpWUzAwMDMKcDEKVkJpcnRoLCBEZWF0aCBhbmQgTWFycmlh
Z2UgUmVjb3JkcwpwMgpWClYKKGxwMwpWYWVmMzA3OGFiNWMxOWFjZTZlMgpwNAphKGxWCkkxMTk4
MTk3MzI2CihkKGxwNQooKGxWYTcwMWU5OWY5M2U1NDM0ZjZmMwpWQ0EtMTIzLUxMLTQ1Nl9OdW0v
YmVyCihJNgpWRmlsbQp0STAwCnRwNgphSTAwCnRwNwou
','Birth, Death and Marriage Records','','','');
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
    "cache" text,
    "event_type_id" integer NOT NULL REFERENCES "grampsdb_eventtype" ("id"),
    "description" varchar(50) NOT NULL,
    "place_id" integer
);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,10,1864,0,0,0,0,0,'',2402147,0,1,'a701e8fd8ea27f99704','E0000','2012-05-29 11:56:39.959300','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmQ4ZWEyN2Y5OTcwNCcKVkUwMDAwCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyCkkxMApJMTg2NApJMDAKdFYKSTI0MDIxNDcKSTAKdFZCaXJ0aCBvZiBBbm5hIEhhbnNk
b3R0ZXIKcDMKVkhJTlQ2RFA4SkdHTDBLS0I4SgpwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0
cDUKLg==
',4,'Birth of Anna Hansdotter',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,8,1889,0,0,0,0,0,'',2411246,0,2,'a701e8fdaa256b7d7a0','E0006','2012-05-29 11:56:39.971521','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRhYTI1NmI3ZDdhMCcKVkUwMDA2CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkzMQpJOApJMTg4OQpJMDAKdFYKSTI0MTEyNDYKSTAKdFZCaXJ0aCBvZiBIZXJtYW4gSnVs
aXVzIE5pZWxzZW4KcDMKVjRaTFQ2RFZDV1Q5TFRaUkRDUwpwNAoobChsKGwobEkxMTk4MTk3MzI2
CkkwMAp0cDUKLg==
',4,'Birth of Herman Julius Nielsen',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1945,0,0,0,0,0,'',2431457,0,3,'a701e8fdaba50dfafa1','E0007','2012-05-29 11:56:39.982135','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRhYmE1MGRmYWZhMScKVkUwMDA3CnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkwCkkwCkkxOTQ1CkkwMAp0VgpJMjQzMTQ1NwpJMAp0VkRlYXRoIG9mIEhlcm1hbiBKdWxp
dXMgTmllbHNlbgpwMwpTJycKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA0Ci4=
',5,'Death of Herman Julius Nielsen',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,8,1963,0,0,0,0,0,'',2438270,0,4,'a701e8fdd82588a2110','E0017','2012-05-29 11:56:39.994707','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRkODI1ODhhMjExMCcKVkUwMDE3CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyOApJOApJMTk2MwpJMDAKdFYKSTI0MzgyNzAKSTAKdFZCaXJ0aCBvZiBFcmljIExsb3lk
IFNtaXRoCnAzClY2N01UNkRCNktXT1ZNQkFYU1kKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',4,'Birth of Eric Lloyd Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1899,0,0,0,1905,0,'',2414656,0,5,'a701e8fdf5224fbdc9e','E0025','2012-05-29 11:56:40.006896','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRmNTIyNGZiZGM5ZScKVkUwMDI1CnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTQK
STAKKEkwCkkwCkkxODk5CkkwMApJMApJMApJMTkwNQpJMDAKdFYKSTI0MTQ2NTYKSTAKdFZEZWF0
aCBvZiBNYXJ0aW4gU21pdGgKcDMKVkE5TVQ2REhWV0dXUlA1OURFVgpwNAoobChsKGwobEkxMTk4
MTk3MzI2CkkwMAp0cDUKLg==
',5,'Death of Martin Smith',13);
INSERT INTO "grampsdb_event" VALUES(0,1,0,23,7,1930,0,0,0,0,0,'',2426181,0,6,'a701e8fe0715514c15e','E0030','2012-05-29 11:56:40.019705','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUwNzE1NTE0YzE1ZScKVkUwMDMwCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTEK
STAKKEkyMwpJNwpJMTkzMApJMDAKdFYKSTI0MjYxODEKSTAKdFZEZWF0aCBvZiBHdXN0YWYgU21p
dGgsIFNyLgpwMwpWUzFOVDZEUE9CWUMxSkdNUjFQCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAw
CnRwNQou
',5,'Death of Gustaf Smith, Sr.',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,9,1860,0,0,0,0,0,'',2400677,0,7,'a701e8fe2650e4c4754','E0037','2012-05-29 11:56:40.031907','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUyNjUwZTRjNDc1NCcKVkUwMDM3CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyMwpJOQpJMTg2MApJMDAKdFYKSTI0MDA2NzcKSTAKdFZCaXJ0aCBvZiBBbm5hIFN0cmVp
ZmZlcnQKcDMKVkRZTFQ2REY0RFgyTU5aSUNKOApwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0
cDUKLg==
',4,'Birth of Anna Streiffert',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,8,'a701e8fe3ee581802d8','E0044','2012-05-29 11:56:40.042494','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUzZWU1ODE4MDJkOCcKVkUwMDQ0CnAxCihJMzcKVk9jY3VwYXRpb24KcDIKdE5W
UmV0YWlsIE1hbmFnZXIKcDMKUycnCihsKGwobChsSTExOTgxOTczMjYKSTAwCnRwNAou
',29,'Retail Manager',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,6,1980,0,0,0,0,0,'',2444413,0,9,'a701e8fe47a0ef83449','E0047','2012-05-29 11:56:40.054695','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU0N2EwZWY4MzQ0OScKVkUwMDQ3CnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyMgpJNgpJMTk4MApJMDAKdFYKSTI0NDQ0MTMKSTAKdFZEZWF0aCBvZiBNYXJqb3JpZSBP
aG1hbgpwMwpWN0pNVDZETjJMT0Y1NEtYSFRVCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAwCnRw
NQou
',5,'Death of Marjorie Ohman',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,9,1800,0,0,0,0,0,'',2378753,0,10,'a701e8fe6620b7e07d4','E0052','2012-05-29 11:56:40.066995','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU2NjIwYjdlMDdkNCcKVkUwMDUyCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxNApJOQpJMTgwMApJMDAKdFYKSTIzNzg3NTMKSTAKdFZCaXJ0aCBvZiBFbG5hIEplZmZl
cnNvbgpwMwpWWFNNVDZETklTSFlSQ1IxRTc4CnA0CihsKGwobChsSTExOTgxOTczMjYKSTAwCnRw
NQou
',4,'Birth of Elna Jefferson',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,11,'a701e8fe7334aab749d','E0056','2012-05-29 11:56:40.079324','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU3MzM0YWFiNzQ5ZCcKVkUwMDU2CnAxCihJMzcKVk9jY3VwYXRpb24KcDIKdE5W
U29mdHdhcmUgRW5naW5lZXIKcDMKUycnCihsKGxwNApWYWVmMzA3ODllYTczZTliNWIxMApwNQph
KGwobEkxMTk4MTk3MzI2CkkwMAp0cDYKLg==
',29,'Software Engineer',NULL);
INSERT INTO "grampsdb_event" VALUES(0,2,0,0,0,1823,0,0,0,0,0,'',2386897,0,12,'a701e8feadf736d65f9','E0069','2012-05-29 11:56:40.092209','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVhZGY3MzZkNjVmOScKVkUwMDY5CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTIK
STAKKEkwCkkwCkkxODIzCkkwMAp0VgpJMjM4Njg5NwpJMAp0VkJpcnRoIG9mIEluZ2FyIFNtaXRo
CnAzClZYU01UNkROSVNIWVJDUjFFNzgKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',4,'Birth of Ingar Smith',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,9,1860,0,0,0,0,0,'',2400681,0,13,'a701e8fec095079e6be','E0074','2012-05-29 11:56:40.104530','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVjMDk1MDc5ZTZiZScKVkUwMDc0CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyNwpJOQpJMTg2MApJMDAKdFYKSTI0MDA2ODEKSTAKdFZCaXJ0aCBvZiBFbWlsIFNtaXRo
CnAzClZBQU5UNkQwMjZPNVNITlVDREgKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',4,'Birth of Emil Smith',14);
INSERT INTO "grampsdb_event" VALUES(0,0,0,11,8,1966,0,0,0,0,0,'',2439349,0,14,'a701e8fd963245ebfef','E0002','2012-05-29 11:56:40.116955','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmQ5NjMyNDVlYmZlZicKVkUwMDAyCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxMQpJOApJMTk2NgpJMDAKdFYKSTI0MzkzNDkKSTAKdFZCaXJ0aCBvZiBLZWl0aCBMbG95
ZCBTbWl0aApwMwpWNjdNVDZEQjZLV09WTUJBWFNZCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAw
CnRwNQou
',4,'Birth of Keith Lloyd Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1821,0,0,0,0,0,'',2386195,0,15,'a701e8fda49467030a4','E0005','2012-05-29 11:56:40.129074','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRhNDk0NjcwMzBhNCcKVkUwMDA1CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyOQpJMQpJMTgyMQpJMDAKdFYKSTIzODYxOTUKSTAKdFZCaXJ0aCBvZiBIYW5uYSBTbWl0
aApwMwpWWFNNVDZETklTSFlSQ1IxRTc4CnA0CihsKGwobChsSTExOTgxOTczMjYKSTAwCnRwNQou
',4,'Birth of Hanna Smith',25);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1897,0,0,0,0,0,'',2413926,0,16,'a701e8fdb0a2faa54b5','E0008','2012-05-29 11:56:40.139652','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRiMGEyZmFhNTRiNScKVkUwMDA4CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTMK
STAKKEkwCkkwCkkxODk3CkkwMAp0VgpJMjQxMzkyNgpJMAp0VkJpcnRoIG9mIEV2ZWx5biBNaWNo
YWVscwpwMwpTJycKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA0Ci4=
',4,'Birth of Evelyn Michaels',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,30,1,1932,0,0,0,0,0,'',2426737,0,17,'a701e8fdd0f520c6d87','E0016','2012-05-29 11:56:40.151755','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRkMGY1MjBjNmQ4NycKVkUwMDE2CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkzMApJMQpJMTkzMgpJMDAKdFYKSTI0MjY3MzcKSTAKdFZCaXJ0aCBvZiBKb2huIEhqYWxt
YXIgU21pdGgKcDMKVjY3TVQ2REI2S1dPVk1CQVhTWQpwNAoobChsKGwobEkxMTk4MTk3MzI2Ckkw
MAp0cDUKLg==
',4,'Birth of John Hjalmar Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,11,1830,0,0,0,0,0,'',2389780,0,18,'a701e8fdf6d6b51e7ad','E0026','2012-05-29 11:56:40.163813','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRmNmQ2YjUxZTdhZCcKVkUwMDI2CnAxCihJMTUKVkJhcHRpc20KcDIKdChJMApJ
MApJMAooSTIzCkkxMQpJMTgzMApJMDAKdFYKSTIzODk3ODAKSTAKdFZCYXB0aXNtIG9mIE1hcnRp
biBTbWl0aApwMwpWWFNNVDZETklTSFlSQ1IxRTc4CnA0CihsKGwobChsSTExOTgxOTczMjYKSTAw
CnRwNQou
',7,'Baptism of Martin Smith',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,7,1966,0,0,0,0,0,'',2439325,0,19,'a701e8fe19a55908f51','E0035','2012-05-29 11:56:40.175968','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUxOWE1NTkwOGY1MScKVkUwMDM1CnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkxOApJNwpJMTk2NgpJMDAKdFYKSTI0MzkzMjUKSTAKdFZEZWF0aCBvZiBLaXJzdGkgTWFy
aWUgU21pdGgKcDMKVjY3TVQ2REI2S1dPVk1CQVhTWQpwNAoobChsKGwobEkxMTk4MTk3MzI2Ckkw
MAp0cDUKLg==
',5,'Death of Kirsti Marie Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,10,1858,0,0,0,0,0,'',2399959,0,20,'a701e8fe3552335c8c6','E0041','2012-05-29 11:56:40.188315','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUzNTUyMzM1YzhjNicKVkUwMDQxCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEk2CkkxMApJMTg1OApJMDAKdFYKSTIzOTk5NTkKSTAKdFZCaXJ0aCBvZiBNYWduZXMgU21p
dGgKcDMKVkFBTlQ2RDAyNk81U0hOVUNESApwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUK
Lg==
',4,'Birth of Magnes Smith',14);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,2,1910,0,0,0,0,0,'',2418723,0,21,'a701e8fe37009b79506','E0042','2012-05-29 11:56:40.200729','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUzNzAwOWI3OTUwNicKVkUwMDQyCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyMApJMgpJMTkxMApJMDAKdFYKSTI0MTg3MjMKSTAKdFZEZWF0aCBvZiBNYWduZXMgU21p
dGgKcDMKVjRaTFQ2RFZDV1Q5TFRaUkRDUwpwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUK
Lg==
',5,'Death of Magnes Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1988,0,0,0,0,0,'',2447162,0,22,'a701e8fe40453c7a8c6','E0045','2012-05-29 11:56:40.211348','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU0MDQ1M2M3YThjNicKVkUwMDQ1CnAxCihJMjUKVkRlZ3JlZQpwMgp0KEkwCkkw
CkkwCihJMApJMApJMTk4OApJMDAKdFYKSTI0NDcxNjIKSTAKdFZCdXNpbmVzcyBNYW5hZ2VtZW50
CnAzClMnJwoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDQKLg==
',17,'Business Management',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,3,6,1903,0,0,0,0,0,'',2416269,0,23,'a701e8fe457737ab114','E0046','2012-05-29 11:56:40.223437','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU0NTc3MzdhYjExNCcKVkUwMDQ2CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkzCkk2CkkxOTAzCkkwMAp0VgpJMjQxNjI2OQpJMAp0VkJpcnRoIG9mIE1hcmpvcmllIE9o
bWFuCnAzClZSUE1UNkRUUVI4SjdMSzk4SEoKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1
Ci4=
',4,'Birth of Marjorie Ohman',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,16,9,1991,0,0,0,0,0,'',2448516,0,24,'a701e8fe5fb6b2cd015','E0051','2012-05-29 11:56:40.235537','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU1ZmI2YjJjZDAxNScKVkUwMDUxCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxNgpJOQpJMTk5MQpJMDAKdFYKSTI0NDg1MTYKSTAKdFZCaXJ0aCBvZiBMYXJzIFBldGVy
IFNtaXRoCnAzClZGQk5UNkRMOTJORFkwWjVTR1AKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',4,'Birth of Lars Peter Smith',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1984,0,0,0,0,0,'',2445701,0,25,'a701e8fe777404ac230','E0058','2012-05-29 11:56:40.245967','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU3Nzc0MDRhYzIzMCcKVkUwMDU4CnAxCihJMjUKVkRlZ3JlZQpwMgp0KEkwCkkw
CkkwCihJMApJMApJMTk4NApJMDAKdFYKSTI0NDU3MDEKSTAKdFZCLlMuRS5FLgpwMwpTJycKKGwo
bChsKGxJMTE5ODE5NzMyNgpJMDAKdHA0Ci4=
',17,'B.S.E.E.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1794,0,0,0,1796,0,'',2376306,0,26,'a701e8fe866359dc7b5','E0061','2012-05-29 11:56:40.258255','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU4NjYzNTlkYzdiNScKVkUwMDYxCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTQK
STAKKEkwCkkwCkkxNzk0CkkwMApJMApJMApJMTc5NgpJMDAKdFYKSTIzNzYzMDYKSTAKdFZCaXJ0
aCBvZiBNYXJ0aW4gU21pdGgKcDMKVlI4TVQ2RFJJWlZOUllESzBWTgpwNAoobChsKGwobEkxMTk4
MTk3MzI2CkkwMAp0cDUKLg==
',4,'Birth of Martin Smith',9);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,2,1960,0,0,0,0,0,'',2436970,0,27,'a701e8fe94819a227eb','E0064','2012-05-29 11:56:40.270426','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU5NDgxOWEyMjdlYicKVkUwMDY0CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEk1CkkyCkkxOTYwCkkwMAp0VgpJMjQzNjk3MApJMAp0VkJpcnRoIG9mIE1hcmpvcmllIEFs
aWNlIFNtaXRoCnAzClZMVE5UNkRLWjVDUjhQWlNWVVMKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJ
MDAKdHA1Ci4=
',4,'Birth of Marjorie Alice Smith',6);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,12,1935,0,0,0,0,0,'',2428139,0,28,'a701e8fe9ab02623db3','E0065','2012-05-29 11:56:40.281019','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU5YWIwMjYyM2RiMycKVkUwMDY1CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyCkkxMgpJMTkzNQpJMDAKdFYKSTI0MjgxMzkKSTAKdFZCaXJ0aCBvZiBKYW5pcyBFbGFp
bmUgR3JlZW4KcDMKUycnCihsKGwobChsSTExOTgxOTczMjYKSTAwCnRwNAou
',4,'Birth of Janis Elaine Green',NULL);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1886,0,0,0,0,0,'',2409908,0,29,'a701e8fea803e09a00a','E0068','2012-05-29 11:56:40.291757','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVhODAzZTA5YTAwYScKVkUwMDY4CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTMK
STAKKEkwCkkwCkkxODg2CkkwMAp0VgpJMjQwOTkwOApJMAp0VkJpcnRoIG9mIEVkd2luIFdpbGxh
cmQKcDMKUycnCihsKGwobChsSTExOTgxOTczMjYKSTAwCnRwNAou
',4,'Birth of Edwin Willard',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,4,1895,0,0,0,0,0,'',2413291,0,30,'a701e8feb3b0c8340f5','E0070','2012-05-29 11:56:40.303957','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmViM2IwYzgzNDBmNScKVkUwMDcwCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEk3Ckk0CkkxODk1CkkwMAp0VgpJMjQxMzI5MQpJMAp0VkJpcnRoIG9mIEhqYWxtYXIgU21p
dGgKcDMKVjRaTFQ2RFZDV1Q5TFRaUkRDUwpwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUK
Lg==
',4,'Birth of Hjalmar Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1977,0,0,0,0,0,'',2443173,0,31,'a701e8fd9e57b3c48fb','E0004','2012-05-29 11:56:40.316095','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmQ5ZTU3YjNjNDhmYicKVkUwMDA0CnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyOQpJMQpJMTk3NwpJMDAKdFYKSTI0NDMxNzMKSTAKdFZEZWF0aCBvZiBIYW5zIFBldGVy
IFNtaXRoCnAzClY2N01UNkRCNktXT1ZNQkFYU1kKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',5,'Death of Hans Peter Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,11,1934,0,0,0,0,0,'',2427746,0,32,'a701e8fdb5c42897136','E0009','2012-05-29 11:56:40.328175','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRiNWM0Mjg5NzEzNicKVkUwMDA5CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEk0CkkxMQpJMTkzNApJMDAKdFYKSTI0Mjc3NDYKSTAKdFZCaXJ0aCBvZiBNYXJqb3JpZSBM
ZWUgU21pdGgKcDMKVjdKTVQ2RE4yTE9GNTRLWEhUVQpwNAoobChsKGwobEkxMTk4MTk3MzI2Ckkw
MAp0cDUKLg==
',4,'Birth of Marjorie Lee Smith',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,10,1963,0,0,0,0,0,'',2438324,0,33,'a701e8fdbd42af855c2','E0011','2012-05-29 11:56:40.340528','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRiZDQyYWY4NTVjMicKVkUwMDExCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyMQpJMTAKSTE5NjMKSTAwCnRWCkkyNDM4MzI0CkkwCnRWRGVhdGggb2YgR3VzIFNtaXRo
CnAzClY2N01UNkRCNktXT1ZNQkFYU1kKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',5,'Death of Gus Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,5,1910,0,0,0,0,0,'',2418794,0,34,'a701e8fdc9c76ede240','E0014','2012-05-29 11:56:40.352681','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRjOWM3NmVkZTI0MCcKVkUwMDE0CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyCkk1CkkxOTEwCkkwMAp0VgpJMjQxODc5NApJMAp0VkJpcnRoIG9mIExpbGxpZSBIYXJy
aWV0IEpvbmVzCnAzClY0WkxUNkRWQ1dUOUxUWlJEQ1MKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJ
MDAKdHA1Ci4=
',4,'Birth of Lillie Harriet Jones',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,11,1862,0,0,0,0,0,'',2401473,0,35,'a701e8fe0507ac04137','E0029','2012-05-29 11:56:40.364783','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUwNTA3YWMwNDEzNycKVkUwMDI5CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyOApJMTEKSTE4NjIKSTAwCnRWCkkyNDAxNDczCkkwCnRWQmlydGggb2YgR3VzdGFmIFNt
aXRoLCBTci4KcDMKVjYxTlQ2RDNHMUpNT1RPNlo3WQpwNAoobChsKGwobEkxMTk4MTk3MzI2Ckkw
MAp0cDUKLg==
',4,'Birth of Gustaf Smith, Sr.',11);
INSERT INTO "grampsdb_event" VALUES(0,2,0,0,0,1966,0,0,0,0,0,'',2439127,0,36,'a701e8fe2e27662085f','E0039','2012-05-29 11:56:40.376859','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUyZTI3NjYyMDg1ZicKVkUwMDM5CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTIK
STAKKEkwCkkwCkkxOTY2CkkwMAp0VgpJMjQzOTEyNwpJMAp0VkJpcnRoIG9mIENyYWlnIFBldGVy
IFNtaXRoCnAzClY2N01UNkRCNktXT1ZNQkFYU1kKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',4,'Birth of Craig Peter Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,5,1961,0,0,0,0,0,'',2437444,0,37,'a701e8fe703747db89d','E0055','2012-05-29 11:56:40.391398','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU3MDM3NDdkYjg5ZCcKVkUwMDU1CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyNApJNQpJMTk2MQpJMDAKdFYKSTI0Mzc0NDQKSTAKdFZCaXJ0aCBvZiBFZHdpbiBNaWNo
YWVsIFNtaXRoCnAzClZMVE5UNkRLWjVDUjhQWlNWVVMKcDQKKGxwNQpWYzJiZmQxOTI2NzcxZmNh
M2YzZQpwNgphKGwobChsSTExOTgxOTczMjYKSTAwCnRwNwou
',4,'Birth of Edwin Michael Smith',6);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,11,1832,0,0,0,0,0,'',2390517,0,38,'a701e8fe7e04c6a8cd6','E0059','2012-05-29 11:56:40.403611','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU3ZTA0YzZhOGNkNicKVkUwMDU5CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyOQpJMTEKSTE4MzIKSTAwCnRWCkkyMzkwNTE3CkkwCnRWQmlydGggb2YgS2Vyc3RpbmEg
SGFuc2RvdHRlcgpwMwpWUFhNVDZEQkwwV1NCTDc2V0Q3CnA0CihsKGwobChsSTExOTgxOTczMjYK
STAwCnRwNQou
',4,'Birth of Kerstina Hansdotter',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1826,0,0,0,0,0,'',2388021,0,39,'a701e8fe8ea06c7fba4','E0063','2012-05-29 11:56:40.415842','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU4ZWEwNmM3ZmJhNCcKVkUwMDYzCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyOQpJMQpJMTgyNgpJMDAKdFYKSTIzODgwMjEKSTAKdFZCaXJ0aCBvZiBJbmdlbWFuIFNt
aXRoCnAzClZYU01UNkROSVNIWVJDUjFFNzgKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1
Ci4=
',4,'Birth of Ingeman Smith',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1996,0,0,0,0,0,'',2450261,0,40,'a701e8fe9f8177b3a8a','E0066','2012-05-29 11:56:40.427932','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU5ZjgxNzdiM2E4YScKVkUwMDY2CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyNgpJNgpJMTk5NgpJMDAKdFYKSTI0NTAyNjEKSTAKdFZCaXJ0aCBvZiBNYXNvbiBNaWNo
YWVsIFNtaXRoCnAzClZFTE5UNkRTOEdOOFdJN1o0U08KcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJ
MDAKdHA1Ci4=
',4,'Birth of Mason Michael Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,7,1996,0,0,0,0,0,'',2450275,0,41,'a701e8fea181d0b4ecf','E0067','2012-05-29 11:56:40.440066','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVhMTgxZDBiNGVjZicKVkUwMDY3CnAxCihJMjIKVkNocmlzdGVuaW5nCnAyCnQo
STAKSTAKSTAKKEkxMApJNwpJMTk5NgpJMDAKdFYKSTI0NTAyNzUKSTAKdFZDaHJpc3RlbmluZyBv
ZiBNYXNvbiBNaWNoYWVsIFNtaXRoCnAzClZYTE5UNkRVT05JVEZQUEVHVkgKcDQKKGwobChsKGxJ
MTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',14,'Christening of Mason Michael Smith',24);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1910,0,0,0,0,0,'',2418673,0,42,'a701e8ff00713e0c66e','E0084','2012-05-29 11:56:40.450674','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmYwMDcxM2UwYzY2ZScKVkUwMDg0CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MwpJMAooSTAKSTAKSTE5MTAKSTAwCnRWCkkyNDE4NjczCkkwCnRWTWFycmlhZ2Ugb2YgRWR3aW4g
V2lsbGFyZCBhbmQgS2lyc3RpIE1hcmllIFNtaXRoCnAzClMnJwoobChsKGwobEkxMTk4MTk3MzI2
CkkwMAp0cDQKLg==
',37,'Marriage of Edwin Willard and Kirsti Marie Smith',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,10,1927,0,0,0,0,0,'',2425185,0,43,'a701e8ff0b46ceabfab','E0086','2012-05-29 11:56:40.462872','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmYwYjQ2Y2VhYmZhYicKVkUwMDg2CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MApJMAooSTMxCkkxMApJMTkyNwpJMDAKdFYKSTI0MjUxODUKSTAKdFZNYXJyaWFnZSBvZiBIamFs
bWFyIFNtaXRoIGFuZCBNYXJqb3JpZSBPaG1hbgpwMwpWN0pNVDZETjJMT0Y1NEtYSFRVCnA0Cihs
KGwobChsSTExOTgxOTczMjYKSTAwCnRwNQou
',37,'Marriage of Hjalmar Smith and Marjorie Ohman',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1990,0,0,0,0,0,'',2448069,0,44,'a701e8fdcbb150d8c89','E0015','2012-05-29 11:56:40.473406','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRjYmIxNTBkOGM4OScKVkUwMDE1CnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyNgpJNgpJMTk5MApJMDAKdFYKSTI0NDgwNjkKSTAKdFZEZWF0aCBvZiBMaWxsaWUgSGFy
cmlldCBKb25lcwpwMwpTJycKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA0Ci4=
',5,'Death of Lillie Harriet Jones',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,4,1998,0,0,0,0,0,'',2450930,0,45,'a701e8fddfe33c41840','E0019','2012-05-29 11:56:40.485608','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRkZmUzM2M0MTg0MCcKVkUwMDE5CnAxCihJMjIKVkNocmlzdGVuaW5nCnAyCnQo
STAKSTAKSTAKKEkyNgpJNApJMTk5OApJMDAKdFYKSTI0NTA5MzAKSTAKdFZDaHJpc3RlbmluZyBv
ZiBBbWJlciBNYXJpZSBTbWl0aApwMwpWWExOVDZEVU9OSVRGUFBFR1ZICnA0CihsKGwobChsSTEx
OTgxOTczMjYKSTAwCnRwNQou
',14,'Christening of Amber Marie Smith',24);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,12,1899,0,0,0,0,0,'',2415009,0,46,'a701e8fde5d0cc6484e','E0020','2012-05-29 11:56:40.498006','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRlNWQwY2M2NDg0ZScKVkUwMDIwCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyMApJMTIKSTE4OTkKSTAwCnRWCkkyNDE1MDA5CkkwCnRWQmlydGggb2YgQ2FybCBFbWls
IFNtaXRoCnAzClY0WkxUNkRWQ1dUOUxUWlJEQ1MKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',4,'Birth of Carl Emil Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,1,1893,0,0,0,0,0,'',2412495,0,47,'a701e8fdecb3abcf86d','E0022','2012-05-29 11:56:40.510319','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRlY2IzYWJjZjg2ZCcKVkUwMDIyCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkzMQpJMQpJMTg5MwpJMDAKdFYKSTI0MTI0OTUKSTAKdFZCaXJ0aCBvZiBIamFsbWFyIFNt
aXRoCnAzClY0WkxUNkRWQ1dUOUxUWlJEQ1MKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1
Ci4=
',4,'Birth of Hjalmar Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,12,1862,0,0,0,0,0,'',2401482,0,48,'a701e8fe0a80b22fd7b','E0032','2012-05-29 11:56:40.522633','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUwYTgwYjIyZmQ3YicKVkUwMDMyCnAxCihJMjIKVkNocmlzdGVuaW5nCnAyCnQo
STAKSTAKSTAKKEk3CkkxMgpJMTg2MgpJMDAKdFYKSTI0MDE0ODIKSTAKdFZDaHJpc3RlbmluZyBv
ZiBHdXN0YWYgU21pdGgsIFNyLgpwMwpWWFNNVDZETklTSFlSQ1IxRTc4CnA0CihsKGwobChsSTEx
OTgxOTczMjYKSTAwCnRwNQou
',14,'Christening of Gustaf Smith, Sr.',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,15,12,1886,0,0,0,0,0,'',2410256,0,49,'a701e8fe1812300afa7','E0034','2012-05-29 11:56:40.534726','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUxODEyMzAwYWZhNycKVkUwMDM0CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxNQpJMTIKSTE4ODYKSTAwCnRWCkkyNDEwMjU2CkkwCnRWQmlydGggb2YgS2lyc3RpIE1h
cmllIFNtaXRoCnAzClY0WkxUNkRWQ1dUOUxUWlJEQ1MKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJ
MDAKdHA1Ci4=
',4,'Birth of Kirsti Marie Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1770,0,0,0,0,0,'',2367540,0,50,'a701e8fe2072c1fa532','E0036','2012-05-29 11:56:40.546887','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUyMDcyYzFmYTUzMicKVkUwMDM2CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTMK
STAKKEkwCkkwCkkxNzcwCkkwMAp0VgpJMjM2NzU0MApJMAp0VkJpcnRoIG9mIEluZ2VtYW4gU21p
dGgKcDMKVkE5TVQ2REhWV0dXUlA1OURFVgpwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUK
Lg==
',4,'Birth of Ingeman Smith',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,51,'a701e8fe2fb2e845e69','E0040','2012-05-29 11:56:40.559098','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUyZmIyZTg0NWU2OScKVkUwMDQwCnAxCihJMjEKVkNlbnN1cwpwMgp0TlZDZW5z
dXMgb2YgQ3JhaWcgUGV0ZXIgU21pdGgKcDMKUycnCihsKGxwNApWYWVmMzA3ODlkM2QyMDkwYWJl
MgpwNQphKGwobEkxMTk4MTk3MzI2CkkwMAp0cDYKLg==
',13,'Census of Craig Peter Smith',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,8,1965,0,0,0,0,0,'',2438999,0,52,'a701e8fe3d35113a9a7','E0043','2012-05-29 11:56:40.571231','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUzZDM1MTEzYTlhNycKVkUwMDQzCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyNgpJOApJMTk2NQpJMDAKdFYKSTI0Mzg5OTkKSTAKdFZCaXJ0aCBvZiBKYW5pY2UgQW5u
IEFkYW1zCnAzClZIRk5UNkQxMlpDMEtPV1k2OVQKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',4,'Birth of Janice Ann Adams',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,3,1935,0,0,0,0,0,'',2427875,0,53,'a701e8fe53a76e15c39','E0049','2012-05-29 11:56:40.583444','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU1M2E3NmUxNWMzOScKVkUwMDQ5CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxMwpJMwpJMTkzNQpJMDAKdFYKSTI0Mjc4NzUKSTAKdFZCaXJ0aCBvZiBMbG95ZCBTbWl0
aApwMwpWNjdNVDZEQjZLV09WTUJBWFNZCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAwCnRwNQou
',4,'Birth of Lloyd Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1933,0,0,0,0,0,'',2427399,0,54,'a701e8fe59c7230b3bd','E0050','2012-05-29 11:56:40.595867','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU1OWM3MjMwYjNiZCcKVkUwMDUwCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyMgpJMTEKSTE5MzMKSTAwCnRWCkkyNDI3Mzk5CkkwCnRWQmlydGggb2YgQWxpY2UgUGF1
bGEgUGVya2lucwpwMwpWUzFOVDZEUE9CWUMxSkdNUjFQCnA0CihsKGwobChsSTExOTgxOTczMjYK
STAwCnRwNQou
',4,'Birth of Alice Paula Perkins',23);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1979,0,0,0,1984,0,'',2443875,0,55,'a701e8fe75b474f1853','E0057','2012-05-29 11:56:40.608042','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU3NWI0NzRmMTg1MycKVkUwMDU3CnAxCihJMjYKVkVkdWNhdGlvbgpwMgp0KEkw
Ckk0CkkwCihJMApJMApJMTk3OQpJMDAKSTAKSTAKSTE5ODQKSTAwCnRWCkkyNDQzODc1CkkwCnRW
RWR1Y2F0aW9uIG9mIEVkd2luIE1pY2hhZWwgU21pdGgKcDMKVlBVTlQ2RDFYSFMwREpXOVFQNgpw
NAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUKLg==
',18,'Education of Edwin Michael Smith',7);
INSERT INTO "grampsdb_event" VALUES(0,1,0,0,0,1908,0,0,0,0,0,'',2417942,0,56,'a701e8fe80366eb06dd','E0060','2012-05-29 11:56:40.620285','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU4MDM2NmViMDZkZCcKVkUwMDYwCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTEK
STAKKEkwCkkwCkkxOTA4CkkwMAp0VgpJMjQxNzk0MgpJMAp0VkRlYXRoIG9mIEtlcnN0aW5hIEhh
bnNkb3R0ZXIKcDMKVkE5TVQ2REhWV0dXUlA1OURFVgpwNAoobChsKGwobEkxMTk4MTk3MzI2Ckkw
MAp0cDUKLg==
',5,'Death of Kerstina Hansdotter',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,57,'a701e8fe8843924e179','E0062','2012-05-29 11:56:40.632345','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU4ODQzOTI0ZTE3OScKVkUwMDYyCnAxCihJMTMKVkRlYXRoCnAyCnROVkRlYXRo
IG9mIE1hcnRpbiBTbWl0aApwMwpWQTlNVDZESFZXR1dSUDU5REVWCnA0CihsKGwobChsSTExOTgx
OTczMjYKSTAwCnRwNQou
',5,'Death of Martin Smith',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,3,6,1895,0,0,0,0,0,'',2413348,0,58,'a701e8feb7b20ccf010','E0072','2012-05-29 11:56:40.644527','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmViN2IyMGNjZjAxMCcKVkUwMDcyCnAxCihJMTUKVkJhcHRpc20KcDIKdChJMApJ
MApJMAooSTMKSTYKSTE4OTUKSTAwCnRWCkkyNDEzMzQ4CkkwCnRWQmFwdGlzbSBvZiBIamFsbWFy
IFNtaXRoCnAzClZRSk1UNkRHSUkyOUZXQ1BYMkUKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',7,'Baptism of Hjalmar Smith',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,11,1912,0,0,0,0,0,'',2419721,0,59,'a701e8feb9f64bfceb3','E0073','2012-05-29 11:56:40.656803','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmViOWY2NGJmY2ViMycKVkUwMDczCnAxCihJMApWSW1taQpwMgp0KEkwCkkwCkkw
CihJMTQKSTExCkkxOTEyCkkwMAp0VgpJMjQxOTcyMQpJMAp0VgpWQUtNVDZETUVZWkRURzlKNkRT
CnAzCihsKGwobChsSTExOTgxOTczMjYKSTAwCnRwNAou
',47,'',15);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1790,0,0,0,0,0,'',2374845,0,60,'a701e8fecd804e4c544','E0076','2012-05-29 11:56:40.669069','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVjZDgwNGU0YzU0NCcKVkUwMDc2CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MwpJMAooSTAKSTAKSTE3OTAKSTAwCnRWCkkyMzc0ODQ1CkkwCnRWTWFycmlhZ2Ugb2YgSW5nZW1h
biBTbWl0aCBhbmQgTWFydGEgRXJpY3Nkb3R0ZXIKcDMKVkE5TVQ2REhWV0dXUlA1OURFVgpwNAoo
bChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUKLg==
',37,'Marriage of Ingeman Smith and Marta Ericsdotter',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,7,1986,0,0,0,0,0,'',2446624,0,61,'a701e8fed39673c4638','E0077','2012-05-29 11:56:40.681197','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVkMzk2NzNjNDYzOCcKVkUwMDc3CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MApJMAooSTEyCkk3CkkxOTg2CkkwMAp0VgpJMjQ0NjYyNApJMAp0Vk1hcnJpYWdlIG9mIEVyaWMg
TGxveWQgU21pdGggYW5kIERhcmN5IEhvcm5lCnAzClZRQk9UNkRON1VDQ1RaUTA1NQpwNAoobChs
KGwobEkxMTk4MTk3MzI2CkkwMAp0cDUKLg==
',37,'Marriage of Eric Lloyd Smith and Darcy Horne',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,6,1954,0,0,0,0,0,'',2434898,0,62,'a701e8fedf83b69acf8','E0079','2012-05-29 11:56:40.695823','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVkZjgzYjY5YWNmOCcKVkUwMDc5CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MApJMAooSTQKSTYKSTE5NTQKSTAwCnRWCkkyNDM0ODk4CkkwCnRWTWFycmlhZ2Ugb2YgSm9obiBI
amFsbWFyIFNtaXRoIGFuZCBBbGljZSBQYXVsYSBQZXJraW5zCnAzClZTMU5UNkRQT0JZQzFKR01S
MVAKcDQKKGxwNQpWYzJiZmQxOTI4YTcyY2I1ZWZiZgpwNgphKGwobChsSTExOTgxOTczMjYKSTAw
CnRwNwou
',37,'Marriage of John Hjalmar Smith and Alice Paula Perkins',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,10,1994,0,0,0,0,0,'',2449631,0,63,'a701e8fee9139a03b7f','E0081','2012-05-29 11:56:40.708082','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVlOTEzOWEwM2I3ZicKVkUwMDgxCnAxCihJNgpWRW5nYWdlbWVudApwMgp0KEkw
CkkwCkkwCihJNQpJMTAKSTE5OTQKSTAwCnRWCkkyNDQ5NjMxCkkwCnRWRW5nYWdlbWVudCBvZiBF
ZHdpbiBNaWNoYWVsIFNtaXRoIGFuZCBKYW5pY2UgQW5uIEFkYW1zCnAzClY2N01UNkRCNktXT1ZN
QkFYU1kKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',42,'Engagement of Edwin Michael Smith and Janice Ann Adams',12);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1856,0,0,0,0,0,'',2398950,0,64,'a701e8fef323be305a4','E0082','2012-05-29 11:56:40.718828','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVmMzIzYmUzMDVhNCcKVkUwMDgyCnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MwpJMAooSTAKSTAKSTE4NTYKSTAwCnRWCkkyMzk4OTUwCkkwCnRWTWFycmlhZ2Ugb2YgTWFydGlu
IFNtaXRoIGFuZCBLZXJzdGluYSBIYW5zZG90dGVyCnAzClMnJwoobChsKGwobEkxMTk4MTk3MzI2
CkkwMAp0cDQKLg==
',37,'Marriage of Martin Smith and Kerstina Hansdotter',NULL);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1920,0,0,0,0,0,'',2422325,0,65,'a701e8ff11525d5aab8','E0087','2012-05-29 11:56:40.729317','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmYxMTUyNWQ1YWFiOCcKVkUwMDg3CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MwpJMAooSTAKSTAKSTE5MjAKSTAwCnRWCkkyNDIyMzI1CkkwCnRWTWFycmlhZ2Ugb2YgR3VzIFNt
aXRoIGFuZCBFdmVseW4gTWljaGFlbHMKcDMKUycnCihsKGwobChsSTExOTgxOTczMjYKSTAwCnRw
NAou
',37,'Marriage of Gus Smith and Evelyn Michaels',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,8,1958,0,0,0,0,0,'',2436426,0,66,'a701e8ff15c2045e75d','E0088','2012-05-29 11:56:40.741488','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmYxNWMyMDQ1ZTc1ZCcKVkUwMDg4CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MApJMAooSTEwCkk4CkkxOTU4CkkwMAp0VgpJMjQzNjQyNgpJMAp0Vk1hcnJpYWdlIG9mIExsb3lk
IFNtaXRoIGFuZCBKYW5pcyBFbGFpbmUgR3JlZW4KcDMKVjY3TVQ2REI2S1dPVk1CQVhTWQpwNAoo
bChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUKLg==
',37,'Marriage of Lloyd Smith and Janis Elaine Green',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,17,4,1904,0,0,0,0,0,'',2416588,0,67,'a701e8fd9cb7f8d7ec4','E0003','2012-05-29 11:56:40.753750','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmQ5Y2I3ZjhkN2VjNCcKVkUwMDAzCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxNwpJNApJMTkwNApJMDAKdFYKSTI0MTY1ODgKSTAKdFZCaXJ0aCBvZiBIYW5zIFBldGVy
IFNtaXRoCnAzClY0WkxUNkRWQ1dUOUxUWlJEQ1MKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',4,'Birth of Hans Peter Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,5,1985,0,0,0,0,0,'',2446215,0,68,'a701e8fdc444ecbfa3c','E0013','2012-05-29 11:56:40.765902','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRjNDQ0ZWNiZmEzYycKVkUwMDEzCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyOQpJNQpJMTk4NQpJMDAKdFYKSTI0NDYyMTUKSTAKdFZEZWF0aCBvZiBKZW5uaWZlciBB
bmRlcnNvbgpwMwpWNjdNVDZEQjZLV09WTUJBWFNZCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAw
CnRwNQou
',5,'Death of Jennifer Anderson',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,12,1963,0,0,0,0,0,'',2438385,0,69,'a701e8fdfed16648dc3','E0028','2012-05-29 11:56:40.778355','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRmZWQxNjY0OGRjMycKVkUwMDI4CnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyMQpJMTIKSTE5NjMKSTAwCnRWCkkyNDM4Mzg1CkkwCnRWRGVhdGggb2YgQXN0cmlkIFNo
ZXJtYW5uYSBBdWd1c3RhIFNtaXRoCnAzClY2N01UNkRCNktXT1ZNQkFYU1kKcDQKKGwobChsKGxJ
MTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',5,'Death of Astrid Shermanna Augusta Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,5,1908,0,0,0,0,0,'',2418083,0,70,'a701e8fe08b4c512dbd','E0031','2012-05-29 11:56:40.790507','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUwOGI0YzUxMmRiZCcKVkUwMDMxCnAxCihJMApWSW1taQpwMgp0KEkwCkkwCkkw
CihJMjEKSTUKSTE5MDgKSTAwCnRWCkkyNDE4MDgzCkkwCnRWClZBS01UNkRNRVlaRFRHOUo2RFMK
cDMKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA0Ci4=
',47,'',15);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,7,1966,0,0,0,0,0,'',2439309,0,71,'a701e8fe4de2d524fb5','E0048','2012-05-29 11:56:40.802984','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU0ZGUyZDUyNGZiNScKVkUwMDQ4CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkyCkk3CkkxOTY2CkkwMAp0VgpJMjQzOTMwOQpJMAp0VkJpcnRoIG9mIERhcmN5IEhvcm5l
CnAzClZHV05UNkQxMlpWMDZQSzk2OVgKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',4,'Birth of Darcy Horne',4);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,72,'a701e8fe67a3b9763f9','E0053','2012-05-29 11:56:40.815180','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU2N2EzYjk3NjNmOScKVkUwMDUzCnAxCihJMTMKVkRlYXRoCnAyCnROVkRlYXRo
IG9mIEVsbmEgSmVmZmVyc29uCnAzClZBOU1UNkRIVldHV1JQNTlERVYKcDQKKGwobChsKGxJMTE5
ODE5NzMyNgpJMDAKdHA1Ci4=
',5,'Death of Elna Jefferson',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,16,9,1800,0,0,0,0,0,'',2378755,0,73,'a701e8fe69766792b12','E0054','2012-05-29 11:56:40.827453','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmU2OTc2Njc5MmIxMicKVkUwMDU0CnAxCihJMjIKVkNocmlzdGVuaW5nCnAyCnQo
STAKSTAKSTAKKEkxNgpJOQpJMTgwMApJMDAKdFYKSTIzNzg3NTUKSTAKdFZDaHJpc3RlbmluZyBv
ZiBFbG5hIEplZmZlcnNvbgpwMwpWWFNNVDZETklTSFlSQ1IxRTc4CnA0CihsKGwobChsSTExOTgx
OTczMjYKSTAwCnRwNQou
',14,'Christening of Elna Jefferson',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1975,0,0,0,0,0,'',2442590,0,74,'a701e8feb5c3bd26ecb','E0071','2012-05-29 11:56:40.839594','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmViNWMzYmQyNmVjYicKVkUwMDcxCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyNgpJNgpJMTk3NQpJMDAKdFYKSTI0NDI1OTAKSTAKdFZEZWF0aCBvZiBIamFsbWFyIFNt
aXRoCnAzClY3Sk1UNkROMkxPRjU0S1hIVFUKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1
Ci4=
',5,'Death of Hjalmar Smith',1);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1816,0,0,0,0,0,'',2384340,0,75,'a701e8fec630d7443be','E0075','2012-05-29 11:56:40.851810','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVjNjMwZDc0NDNiZScKVkUwMDc1CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MwpJMAooSTAKSTAKSTE4MTYKSTAwCnRWCkkyMzg0MzQwCkkwCnRWTWFycmlhZ2Ugb2YgTWFydGlu
IFNtaXRoIGFuZCBFbG5hIEplZmZlcnNvbgpwMwpWWFNNVDZETklTSFlSQ1IxRTc4CnA0CihsKGwo
bChsSTExOTgxOTczMjYKSTAwCnRwNQou
',37,'Marriage of Martin Smith and Elna Jefferson',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,5,1995,0,0,0,0,0,'',2449865,0,76,'a701e8fee674aa12936','E0080','2012-05-29 11:56:40.863915','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVlNjc0YWExMjkzNicKVkUwMDgwCnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MApJMAooSTI3Ckk1CkkxOTk1CkkwMAp0VgpJMjQ0OTg2NQpJMAp0Vk1hcnJpYWdlIG9mIEVkd2lu
IE1pY2hhZWwgU21pdGggYW5kIEphbmljZSBBbm4gQWRhbXMKcDMKVkJBT1Q2RDFXWTZKNE80QVJS
TgpwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUKLg==
',37,'Marriage of Edwin Michael Smith and Janice Ann Adams',16);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,11,1885,0,0,0,0,0,'',2409873,0,77,'a701e8fef934fe17a49','E0083','2012-05-29 11:56:40.876047','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVmOTM0ZmUxN2E0OScKVkUwMDgzCnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MApJMAooSTI3CkkxMQpJMTg4NQpJMDAKdFYKSTI0MDk4NzMKSTAKdFZNYXJyaWFnZSBvZiBHdXN0
YWYgU21pdGgsIFNyLiBhbmQgQW5uYSBIYW5zZG90dGVyCnAzClY0WkxUNkRWQ1dUOUxUWlJEQ1MK
cDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',37,'Marriage of Gustaf Smith, Sr. and Anna Hansdotter',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,30,11,1912,0,0,0,0,0,'',2419737,0,78,'a701e8ff0514bd46d08','E0085','2012-05-29 11:56:40.888286','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmYwNTE0YmQ0NmQwOCcKVkUwMDg1CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MApJMAooSTMwCkkxMQpJMTkxMgpJMDAKdFYKSTI0MTk3MzcKSTAKdFZNYXJyaWFnZSBvZiBIZXJt
YW4gSnVsaXVzIE5pZWxzZW4gYW5kIEFzdHJpZCBTaGVybWFubmEgQXVndXN0YSBTbWl0aApwMwpW
NFpMVDZEVkNXVDlMVFpSRENTCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAwCnRwNQou
',37,'Marriage of Herman Julius Nielsen and Astrid Shermanna Augusta Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,9,1945,0,0,0,0,0,'',2431728,0,79,'a701e8fd90672bb4ece','E0001','2012-05-29 11:56:40.900765','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmQ5MDY3MmJiNGVjZScKVkUwMDAxCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyOQpJOQpJMTk0NQpJMDAKdFYKSTI0MzE3MjgKSTAKdFZEZWF0aCBvZiBBbm5hIEhhbnNk
b3R0ZXIKcDMKVlMxTlQ2RFBPQllDMUpHTVIxUApwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0
cDUKLg==
',5,'Death of Anna Hansdotter',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,11,9,1897,0,0,0,0,0,'',2414179,0,80,'a701e8fdbb916ee241b','E0010','2012-05-29 11:56:40.912922','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRiYjkxNmVlMjQxYicKVkUwMDEwCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxMQpJOQpJMTg5NwpJMDAKdFYKSTI0MTQxNzkKSTAKdFZCaXJ0aCBvZiBHdXMgU21pdGgK
cDMKVjRaTFQ2RFZDV1Q5TFRaUkRDUwpwNAoobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDUKLg==
',4,'Birth of Gus Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,11,1907,0,0,0,0,0,'',2417885,0,81,'a701e8fdc2a0f6a07ba','E0012','2012-05-29 11:56:40.925095','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRjMmEwZjZhMDdiYScKVkUwMDEyCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEk1CkkxMQpJMTkwNwpJMDAKdFYKSTI0MTc4ODUKSTAKdFZCaXJ0aCBvZiBKZW5uaWZlciBB
bmRlcnNvbgpwMwpWNFpMVDZEVkNXVDlMVFpSRENTCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAw
CnRwNQou
',4,'Birth of Jennifer Anderson',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,4,1998,0,0,0,0,0,'',2450916,0,82,'a701e8fdde30786b48b','E0018','2012-05-29 11:56:40.937212','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRkZTMwNzg2YjQ4YicKVkUwMDE4CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxMgpJNApJMTk5OApJMDAKdFYKSTI0NTA5MTYKSTAKdFZCaXJ0aCBvZiBBbWJlciBNYXJp
ZSBTbWl0aApwMwpWRUxOVDZEUzhHTjhXSTdaNFNPCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAw
CnRwNQou
',4,'Birth of Amber Marie Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,1,1959,0,0,0,0,0,'',2436597,0,83,'a701e8fde75723d0c85','E0021','2012-05-29 11:56:40.953653','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRlNzU3MjNkMGM4NScKVkUwMDIxCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyOApJMQpJMTk1OQpJMDAKdFYKSTI0MzY1OTcKSTAKdFZEZWF0aCBvZiBDYXJsIEVtaWwg
U21pdGgKcDMKVjdKTVQ2RE4yTE9GNTRLWEhUVQpwNAoobChsKGwobHA1CihJMDAKKGwobChJOApW
Q2F1c2UKdFZCYWQgYnJlYXRoCnRwNgphSTExOTgxOTczMjYKSTAwCnRwNwou
',5,'Death of Carl Emil Smith',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,9,1894,0,0,0,0,0,'',2413097,0,84,'a701e8fdee42a4ca4fb','E0023','2012-05-29 11:56:40.965772','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRlZTQyYTRjYTRmYicKVkUwMDIzCnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyNQpJOQpJMTg5NApJMDAKdFYKSTI0MTMwOTcKSTAKdFZEZWF0aCBvZiBIamFsbWFyIFNt
aXRoCnAzClY0WkxUNkRWQ1dUOUxUWlJEQ1MKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1
Ci4=
',5,'Death of Hjalmar Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,19,11,1830,0,0,0,0,0,'',2389776,0,85,'a701e8fdf39649908a4','E0024','2012-05-29 11:56:40.977872','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRmMzk2NDk5MDhhNCcKVkUwMDI0CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkxOQpJMTEKSTE4MzAKSTAwCnRWCkkyMzg5Nzc2CkkwCnRWQmlydGggb2YgTWFydGluIFNt
aXRoCnAzClZYU01UNkROSVNIWVJDUjFFNzgKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1
Ci4=
',4,'Birth of Martin Smith',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,1,1889,0,0,0,0,0,'',2411034,0,86,'a701e8fdfd5706d009f','E0027','2012-05-29 11:56:40.990177','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmRmZDU3MDZkMDA5ZicKVkUwMDI3CnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTAK
STAKKEkzMQpJMQpJMTg4OQpJMDAKdFYKSTI0MTEwMzQKSTAKdFZCaXJ0aCBvZiBBc3RyaWQgU2hl
cm1hbm5hIEF1Z3VzdGEgU21pdGgKcDMKVjRaTFQ2RFZDV1Q5TFRaUkRDUwpwNAoobChsKGwobEkx
MTk4MTk3MzI2CkkwMAp0cDUKLg==
',4,'Birth of Astrid Shermanna Augusta Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1775,0,0,0,0,0,'',2369366,0,87,'a701e8fe11f0a554b76','E0033','2012-05-29 11:56:41.002866','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUxMWYwYTU1NGI3NicKVkUwMDMzCnAxCihJMTIKVkJpcnRoCnAyCnQoSTAKSTMK
STAKKEkwCkkwCkkxNzc1CkkwMAp0VgpJMjM2OTM2NgpJMAp0VkJpcnRoIG9mIE1hcnRhIEVyaWNz
ZG90dGVyCnAzClZBOU1UNkRIVldHV1JQNTlERVYKcDQKKGwobChsKGxJMTE5ODE5NzMyNgpJMDAK
dHA1Ci4=
',4,'Birth of Marta Ericsdotter',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,2,1927,0,0,0,0,0,'',2424914,0,88,'a701e8fe28077648d39','E0038','2012-05-29 11:56:41.015138','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmUyODA3NzY0OGQzOScKVkUwMDM4CnAxCihJMTMKVkRlYXRoCnAyCnQoSTAKSTAK
STAKKEkyCkkyCkkxOTI3CkkwMAp0VgpJMjQyNDkxNApJMAp0VkRlYXRoIG9mIEFubmEgU3RyZWlm
ZmVydApwMwpWNFpMVDZEVkNXVDlMVFpSRENTCnA0CihsKGwobChsSTExOTgxOTczMjYKSTAwCnRw
NQou
',5,'Death of Anna Streiffert',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,8,1884,0,0,0,0,0,'',2409413,0,89,'a701e8fed9d18d7302f','E0078','2012-05-29 11:56:41.027210','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU4ZmVkOWQxOGQ3MzAyZicKVkUwMDc4CnAxCihJMQpWTWFycmlhZ2UKcDIKdChJMApJ
MApJMAooSTI0Ckk4CkkxODg0CkkwMAp0VgpJMjQwOTQxMwpJMAp0Vk1hcnJpYWdlIG9mIE1hZ25l
cyBTbWl0aCBhbmQgQW5uYSBTdHJlaWZmZXJ0CnAzClY0WkxUNkRWQ1dUOUxUWlJEQ1MKcDQKKGwo
bChsKGxJMTE5ODE5NzMyNgpJMDAKdHA1Ci4=
',37,'Marriage of Magnes Smith and Anna Streiffert',10);
CREATE TABLE "grampsdb_repository" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "cache" text,
    "repository_type_id" integer NOT NULL REFERENCES "grampsdb_repositorytype" ("id"),
    "name" text NOT NULL
);
INSERT INTO "grampsdb_repository" VALUES(1,'a701e99f93e5434f6f3','R0002','2012-05-29 11:56:41.045788','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWU5OWY5M2U1NDM0ZjZmMycKVlIwMDAyCnAxCihJMQpWTGlicmFyeQpwMgp0Vk5ldyBZ
b3JrIFB1YmxpYyBMaWJyYXJ5CnAzCihsKGxwNAooSTAwCihsKGxOKFY1dGggQXZlIGF0IDQyIHN0
cmVldApWClZOZXcgWW9yawpWClZOZXcgWW9yawpWVVNBClYxMTExMQpWCnR0cDUKYShsSTExOTgx
OTczMjYKSTAwCnRwNgou
',3,'New York Public Library');
INSERT INTO "grampsdb_repository" VALUES(2,'a701ead12841521cd4d','R0003','2012-05-29 11:56:41.063468','2007-12-20 19:35:26',NULL,0,'KFMnYTcwMWVhZDEyODQxNTIxY2Q0ZCcKVlIwMDAzCnAxCihJOApWQ29sbGVjdGlvbgpwMgp0VkF1
bnQgTWFydGhhJ3MgQXR0aWMKcDMKKGxwNApWYWVmMzA3OGFjYmIxZGYwMTgyYQpwNQphKGxwNgoo
STAwCihsKGxOKFYxMjMgTWFpbiBTdApWClZTb21ldmlsbGUKVgpWU1QKVlVTQQpWClYKdHRwNwph
KGxwOAooSTAwClZodHRwOi8vbGlicmFyeS5ncmFtcHMtcHJvamVjdC5vcmcKVgooSTIKVldlYiBI
b21lCnR0cDkKYUkxMTk4MTk3MzI2CkkwMAp0cDEwCi4=
',10,'Aunt Martha''s Attic');
CREATE TABLE "grampsdb_place" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "cache" text,
    "title" text NOT NULL,
    "long" text NOT NULL,
    "lat" text NOT NULL
);
INSERT INTO "grampsdb_place" VALUES(1,'7JMT6DN2LOF54KXHTU','P0010','2012-05-29 11:56:41.078504','2007-12-20 19:35:26',NULL,0,'KFMnN0pNVDZETjJMT0Y1NEtYSFRVJwpWUDAwMTAKcDEKVlJlbm8sIFdhc2hvZSBDby4sIE5WCnAy
ClYKVgpOKGwobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDMKLg==
','Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(2,'DYLT6DF4DX2MNZICJ8','P0014','2012-05-29 11:56:41.089441','2007-12-20 19:35:26',NULL,0,'KFMnRFlMVDZERjREWDJNTlpJQ0o4JwpWUDAwMTQKcDEKVkhveWEvSm9uYS9Ib2lhLCBTd2VkZW4K
cDIKVgpWCk4obChsKGwobChsSTExOTgxOTczMjYKSTAwCnRwMwou
','Hoya/Jona/Hoia, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(3,'ELNT6DS8GN8WI7Z4SO','P0008','2012-05-29 11:56:41.100623','2007-12-20 19:35:26',NULL,0,'KFMnRUxOVDZEUzhHTjhXSTdaNFNPJwpWUDAwMDgKcDEKVkhheXdhcmQsIEFsYW1lZGEgQ28uLCBD
QQpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Hayward, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(4,'GWNT6D12ZV06PK969X','P0020','2012-05-29 11:56:41.111535','2007-12-20 19:35:26',NULL,0,'KFMnR1dOVDZEMTJaVjA2UEs5NjlYJwpWUDAwMjAKcDEKVlNhY3JhbWVudG8sIFNhY3JhbWVudG8g
Q28uLCBDQQpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Sacramento, Sacramento Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(5,'IEOT6DOW3RE8AQ94HH','P0025','2012-05-29 11:56:41.124283','2007-12-20 19:35:26',NULL,0,'KFMnSUVPVDZET1czUkU4QVE5NEhIJwpWUDAwMjUKcDEKVkLtCnAyClYKVgpOKGwobChsKGwobEkx
MTk4MTk3MzI2CkkwMAp0cDMKLg==
','Bí','','');
INSERT INTO "grampsdb_place" VALUES(6,'LTNT6DKZ5CR8PZSVUS','P0022','2012-05-29 11:56:41.135198','2007-12-20 19:35:26',NULL,0,'KFMnTFROVDZES1o1Q1I4UFpTVlVTJwpWUDAwMjIKcDEKVlNhbiBKb3NlLCBTYW50YSBDbGFyYSBD
by4sIENBCnAyClYKVgpOKGwobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDMKLg==
','San Jose, Santa Clara Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(7,'PUNT6D1XHS0DJW9QP6','P0024','2012-05-29 11:56:41.146242','2007-12-20 19:35:26',NULL,0,'KFMnUFVOVDZEMVhIUzBESlc5UVA2JwpWUDAwMjQKcDEKVlVDIEJlcmtlbGV5CnAyClYKVgpOKGwo
bChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDMKLg==
','UC Berkeley','','');
INSERT INTO "grampsdb_place" VALUES(8,'PXMT6DBL0WSBL76WD7','P0026','2012-05-29 11:56:41.156935','2007-12-20 19:35:26',NULL,0,'KFMnUFhNVDZEQkwwV1NCTDc2V0Q3JwpWUDAwMjYKcDEKVlNtZXN0b3JwLCBLcmlzdGlhbnN0YWQg
TGFuLCBTd2VkZW4KcDIKVgpWCk4obChsKGwobChsSTExOTgxOTczMjYKSTAwCnRwMwou
','Smestorp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(9,'R8MT6DRIZVNRYDK0VN','P0027','2012-05-29 11:56:41.167638','2007-12-20 19:35:26',NULL,0,'KFMnUjhNVDZEUklaVk5SWURLMFZOJwpWUDAwMjcKcDEKVlRvbW1hcnAsIEtyaXN0aWFuc3RhZCBM
YW4sIFN3ZWRlbgpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Tommarp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(10,'4ZLT6DVCWT9LTZRDCS','P0003','2012-05-29 11:56:41.178323','2007-12-20 19:35:26',NULL,0,'KFMnNFpMVDZEVkNXVDlMVFpSRENTJwpWUDAwMDMKcDEKVlJvbm5lLCBCb3JuaG9sbSwgRGVubWFy
awpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(11,'61NT6D3G1JMOTO6Z7Y','P0012','2012-05-29 11:56:41.188990','2007-12-20 19:35:26',NULL,0,'KFMnNjFOVDZEM0cxSk1PVE82WjdZJwpWUDAwMTIKcDEKVkdyb3N0b3JwLCBLcmlzdGlhbnN0YWQg
TGFuLCBTd2VkZW4KcDIKVgpWCk4obChsKGwobChsSTExOTgxOTczMjYKSTAwCnRwMwou
','Grostorp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(12,'67MT6DB6KWOVMBAXSY','P0002','2012-05-29 11:56:41.199720','2007-12-20 19:35:26',NULL,0,'KFMnNjdNVDZEQjZLV09WTUJBWFNZJwpWUDAwMDIKcDEKVlNhbiBGcmFuY2lzY28sIFNhbiBGcmFu
Y2lzY28gQ28uLCBDQQpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(13,'A9MT6DHVWGWRP59DEV','P0011','2012-05-29 11:56:41.210483','2007-12-20 19:35:26',NULL,0,'KFMnQTlNVDZESFZXR1dSUDU5REVWJwpWUDAwMTEKcDEKVlN3ZWRlbgpwMgpWClYKTihsKGwobChs
KGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Sweden','','');
INSERT INTO "grampsdb_place" VALUES(14,'AANT6D026O5SHNUCDH','P0015','2012-05-29 11:56:41.221113','2007-12-20 19:35:26',NULL,0,'KFMnQUFOVDZEMDI2TzVTSE5VQ0RIJwpWUDAwMTUKcDEKVlNpbXJpc2hhbW4sIEtyaXN0aWFuc3Rh
ZCBMYW4sIFN3ZWRlbgpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Simrishamn, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(15,'AKMT6DMEYZDTG9J6DS','P0013','2012-05-29 11:56:41.231771','2007-12-20 19:35:26',NULL,0,'KFMnQUtNVDZETUVZWkRURzlKNkRTJwpWUDAwMTMKcDEKVkNvcGVuaGFnZW4sIERlbm1hcmsKcDIK
VgpWCk4obChsKGwobChsSTExOTgxOTczMjYKSTAwCnRwMwou
','Copenhagen, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(16,'BAOT6D1WY6J4O4ARRN','P0030','2012-05-29 11:56:41.242475','2007-12-20 19:35:26',NULL,0,'KFMnQkFPVDZEMVdZNko0TzRBUlJOJwpWUDAwMzAKcDEKVlNhbiBSYW1vbiwgQ29udGEgQ29zdGEg
Q28uLCBDQQpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','San Ramon, Conta Costa Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(17,'FBNT6DL92NDY0Z5SGP','P0021','2012-05-29 11:56:41.253114','2007-12-20 19:35:26',NULL,0,'KFMnRkJOVDZETDkyTkRZMFo1U0dQJwpWUDAwMjEKcDEKVlNhbnRhIFJvc2EsIFNvbm9tYSBDby4s
IENBCnAyClYKVgpOKGwobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDMKLg==
','Santa Rosa, Sonoma Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(18,'HFNT6D12ZC0KOWY69T','P0016','2012-05-29 11:56:41.263707','2007-12-20 19:35:26',NULL,0,'KFMnSEZOVDZEMTJaQzBLT1dZNjlUJwpWUDAwMTYKcDEKVkZyZW1vbnQsIEFsYW1lZGEgQ28uLCBD
QQpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Fremont, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(19,'HINT6DP8JGGL0KKB8J','P0000','2012-05-29 11:56:41.274536','2007-12-20 19:35:26',NULL,0,'KFMnSElOVDZEUDhKR0dMMEtLQjhKJwpWUDAwMDAKcDEKVkxvZGVydXAsIE1hbG1vdXMgTGFuLCBT
d2VkZW4KcDIKVgpWCk4obChsKGwobChsSTExOTgxOTczMjYKSTAwCnRwMwou
','Loderup, Malmous Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(20,'QBOT6DN7UCCTZQ055','P0029','2012-05-29 11:56:41.285468','2007-12-20 19:35:26',NULL,0,'KFMnUUJPVDZETjdVQ0NUWlEwNTUnClZQMDAyOQpwMQpWV29vZGxhbmQsIFlvbG8gQ28uLCBDQQpw
MgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Woodland, Yolo Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(21,'QJMT6DGII29FWCPX2E','P0028','2012-05-29 11:56:41.296125','2007-12-20 19:35:26',NULL,0,'KFMnUUpNVDZER0lJMjlGV0NQWDJFJwpWUDAwMjgKcDEKVlJvbm5lIEJvcm5ob2xtLCBEZW5tYXJr
CnAyClYKVgpOKGwobChsKGwobEkxMTk4MTk3MzI2CkkwMAp0cDMKLg==
','Ronne Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(22,'RPMT6DTQR8J7LK98HJ','P0019','2012-05-29 11:56:41.306791','2007-12-20 19:35:26',NULL,0,'KFMnUlBNVDZEVFFSOEo3TEs5OEhKJwpWUDAwMTkKcDEKVkRlbnZlciwgRGVudmVyIENvLiwgQ08K
cDIKVgpWCk4obChsKGwobChsSTExOTgxOTczMjYKSTAwCnRwMwou
','Denver, Denver Co., CO','','');
INSERT INTO "grampsdb_place" VALUES(23,'S1NT6DPOBYC1JGMR1P','P0001','2012-05-29 11:56:41.317476','2007-12-20 19:35:26',NULL,0,'KFMnUzFOVDZEUE9CWUMxSkdNUjFQJwpWUDAwMDEKcDEKVlNwYXJrcywgV2FzaG9lIENvLiwgTlYK
cDIKVgpWCk4obChsKGwobChsSTExOTgxOTczMjYKSTAwCnRwMwou
','Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(24,'XLNT6DUONITFPPEGVH','P0009','2012-05-29 11:56:41.328146','2007-12-20 19:35:26',NULL,0,'KFMnWExOVDZEVU9OSVRGUFBFR1ZIJwpWUDAwMDkKcDEKVkNvbW11bml0eSBQcmVzYnl0ZXJpYW4g
Q2h1cmNoLCBEYW52aWxsZSwgQ0EKcDIKVgpWCk4obChsKGwobChsSTExOTgxOTczMjYKSTAwCnRw
Mwou
','Community Presbyterian Church, Danville, CA','','');
INSERT INTO "grampsdb_place" VALUES(25,'XSMT6DNISHYRCR1E78','P0004','2012-05-29 11:56:41.338809','2007-12-20 19:35:26',NULL,0,'KFMnWFNNVDZETklTSFlSQ1IxRTc4JwpWUDAwMDQKcDEKVkdsYWRzYXgsIEtyaXN0aWFuc3RhZCBM
YW4sIFN3ZWRlbgpwMgpWClYKTihsKGwobChsKGxJMTE5ODE5NzMyNgpJMDAKdHAzCi4=
','Gladsax, Kristianstad Lan, Sweden','','');
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
    "cache" text,
    "path" text NOT NULL,
    "mime" text,
    "desc" text NOT NULL
);
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,1,'W2NT6D87SPI9V7G27P','O0001','2012-05-29 11:56:41.347475','2012-05-29 11:55:53',NULL,0,'KFMnVzJOVDZEODdTUEk5VjdHMjdQJwpWTzAwMDEKcDEKVk8xLmpwZwpwMgpWaW1hZ2UvanBlZwpw
MwpWQXJyaXZpbmcgMTkxMApwNAoobChsKGxJMTMzODMwNjk1MwpOKHRJMDAKdHA1Ci4=
','O1.jpg','image/jpeg','Arriving 1910');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,2,'Y0OT6DM7FW06A1SLMS','O0004','2012-05-29 11:56:41.355105','2012-05-29 11:55:53',NULL,0,'KFMnWTBPVDZETTdGVzA2QTFTTE1TJwpWTzAwMDQKcDEKVk80LmpwZwpwMgpWaW1hZ2UvanBlZwpw
MwpWTWFyam9yaWUgQWxpY2UgU21pdGgKcDQKKGwobChsSTEzMzgzMDY5NTMKTih0STAwCnRwNQou
','O4.jpg','image/jpeg','Marjorie Alice Smith');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,3,'43NT6DHH0TBN0PKVC','O0002','2012-05-29 11:56:41.362695','2012-05-29 11:55:53',NULL,0,'KFMnNDNOVDZESEgwVEJOMFBLVkMnClZPMDAwMgpwMQpWTzIuanBnCnAyClZpbWFnZS9qcGVnCnAz
ClZFbWlsICYgR3VzdGFmIFNtaXRoCnA0CihsKGwobEkxMzM4MzA2OTUzCk4odEkwMAp0cDUKLg==
','O2.jpg','image/jpeg','Emil & Gustaf Smith');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,4,'CVNT6DHG5ICZ1UGUO9','O0003','2012-05-29 11:56:41.370262','2012-05-29 11:55:53',NULL,0,'KFMnQ1ZOVDZESEc1SUNaMVVHVU85JwpWTzAwMDMKcDEKVk8zLmpwZwpwMgpWaW1hZ2UvanBlZwpw
MwpWRWR3aW4gTWljaGFlbCBTbWl0aApwNAoobChsKGxJMTMzODMwNjk1MwpOKHRJMDAKdHA1Ci4=
','O3.jpg','image/jpeg','Edwin Michael Smith');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,5,'HHNT6D73QPKC0KWK2Y','O0000','2012-05-29 11:56:41.377840','2012-05-29 11:55:53',NULL,0,'KFMnSEhOVDZENzNRUEtDMEtXSzJZJwpWTzAwMDAKcDEKVk8wLmpwZwpwMgpWaW1hZ2UvanBlZwpw
MwpWS2VpdGggTGxveWQgU21pdGgKcDQKKGwobChsSTEzMzgzMDY5NTMKTih0STAwCnRwNQou
','O0.jpg','image/jpeg','Keith Lloyd Smith');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,6,'MNNT6D27G3L8SGVQJV','O0005','2012-05-29 11:56:41.385451','2012-05-29 11:55:53',NULL,0,'KFMnTU5OVDZEMjdHM0w4U0dWUUpWJwpWTzAwMDUKcDEKVk81LmpwZwpwMgpWaW1hZ2UvanBlZwpw
MwpWRWR3aW4gJiBKYW5pY2UgU21pdGgKcDQKKGwobChsSTEzMzgzMDY5NTMKTih0STAwCnRwNQou
','O5.jpg','image/jpeg','Edwin & Janice Smith');
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
    "cache" text,
    "note_type_id" integer NOT NULL REFERENCES "grampsdb_notetype" ("id"),
    "text" text NOT NULL,
    "preformatted" bool NOT NULL
);
INSERT INTO "grampsdb_note" VALUES(1,'aef3078a8ed472e0f9c','N0003','2012-05-29 11:56:41.393279','2007-12-20 19:35:26',NULL,0,'KFMnYWVmMzA3OGE4ZWQ0NzJlMGY5YycKVk4wMDAzCnAxCihscDIKVkJJT0dSQVBIWVx1MDAwYVx1
MDAwYUhqYWxtYXIgc2FpbGVkIGZyb20gQ29wZW5oYWdlbiwgRGVubWFyayBvbiB0aGUgT1NDQVIg
SUksIDE0IE5vdmVtYmVyIDE5MTIgYXJyaXZpbmcgaW4gTmV3IFlvcmsgMjcgTm92ZW1iZXIgMTkx
Mi4gSGUgd2FzIHNldmVudGVlbiB5ZWFycyBvbGQuIE9uIHRoZSBzaGlwIHBhc3NlbmdlciBsaXN0
IGhpcyB0cmFkZSB3YXMgbGlzdGVkIGFzIGEgQmxhY2tzbWl0aC4gIEhlIGNhbWUgdG8gUmVubywg
TmV2YWRhIGFuZCBsaXZlZCB3aXRoIGhpcyBzaXN0ZXIgTWFyaWUgZm9yIGEgdGltZSBiZWZvcmUg
c2V0dGxpbmcgaW4gU3BhcmtzLiBIZSB3b3JrZWQgZm9yIFNvdXRoZXJuIFBhY2lmaWMgUmFpbHJv
YWQgYXMgYSBjYXIgaW5zcGVjdG9yIGZvciBhIHRpbWUsIHRoZW4gd2VudCB0byB3b3JrIGZvciBT
dGFuZGFyZCBPaWxcdTAwMGFDb21wYW55LiBIZSBlbmxpc3RlZCBpbiB0aGUgYXJteSBhdCBTcGFy
a3MgNyBEZWNlbWJlciAxOTE3IGFuZCBzZXJ2ZWQgYXMgYSBDb3Jwb3JhbCBpbiB0aGUgTWVkaWNh
bCBDb3JwIHVudGlsIGhpcyBkaXNjaGFyZ2UgMTIgQXVndXN0IDE5MTkgYXQgdGhlIFByZXNpZGlv
IGluIFNhbiBGcmFuY2lzY28sIENhbGlmb3JuaWEuIEJvdGggaGUgYW5kIE1hcmpvcmllIGFyZSBi
dXJpZWQgaW4gdGhlIE1hc29uaWMgTWVtb3JpYWwgR2FyZGVucyBNYXVzb2xldW0gaW4gUmVubywg
aGUgdGhlIDMwdGggSnVuZSAxOTc1LCBhbmQgc2hlIHRoZSAyNXRoIG9mIEp1bmUgMTk4MC4KcDMK
YShscDQKYUkwMAooSTQKVlBlcnNvbiBOb3RlCnA1CnRJMTE5ODE5NzMyNgoodEkwMAp0cDYKLg==
',10,'BIOGRAPHY

Hjalmar sailed from Copenhagen, Denmark on the OSCAR II, 14 November 1912 arriving in New York 27 November 1912. He was seventeen years old. On the ship passenger list his trade was listed as a Blacksmith.  He came to Reno, Nevada and lived with his sister Marie for a time before settling in Sparks. He worked for Southern Pacific Railroad as a car inspector for a time, then went to work for Standard Oil
Company. He enlisted in the army at Sparks 7 December 1917 and served as a Corporal in the Medical Corp until his discharge 12 August 1919 at the Presidio in San Francisco, California. Both he and Marjorie are buried in the Masonic Memorial Gardens Mausoleum in Reno, he the 30th June 1975, and she the 25th of June 1980.',0);
INSERT INTO "grampsdb_note" VALUES(2,'aef3078ab1e37d60186','N0004','2012-05-29 11:56:41.399469','2007-12-20 19:35:26',NULL,0,'KFMnYWVmMzA3OGFiMWUzN2Q2MDE4NicKVk4wMDA0CnAxCihscDIKVkJ1dCBBdW50IE1hcnRoYSBz
dGlsbCBrZWVwcyB0aGUgb3JpZ2luYWwhCnAzCmEobHA0CmFJMDAKKEkxMgpWU291cmNlIE5vdGUK
cDUKdEkxMTk4MTk3MzI2Cih0STAwCnRwNgou
',19,'But Aunt Martha still keeps the original!',0);
INSERT INTO "grampsdb_note" VALUES(3,'aef30789d3d2090abe2','N0000','2012-05-29 11:56:41.405548','2007-12-20 19:35:26',NULL,0,'KFMnYWVmMzA3ODlkM2QyMDkwYWJlMicKVk4wMDAwCnAxCihscDIKVldpdG5lc3MgbmFtZTogSm9o
biBEb2VcdTAwMGFXaXRuZXNzIGNvbW1lbnQ6IFRoaXMgaXMgYSBzaW1wbGUgdGVzdC4KcDMKYShs
cDQKYUkwMAooSTEwClZFdmVudCBOb3RlCnA1CnRJMTE5ODE5NzMyNgoodEkwMAp0cDYKLg==
',17,'Witness name: John Doe
Witness comment: This is a simple test.',0);
INSERT INTO "grampsdb_note" VALUES(4,'aef30789ea73e9b5b10','N0001','2012-05-29 11:56:41.411614','2007-12-20 19:35:26',NULL,0,'KFMnYWVmMzA3ODllYTczZTliNWIxMCcKVk4wMDAxCnAxCihscDIKVldpdG5lc3MgbmFtZTogTm8g
TmFtZQpwMwphKGxwNAphSTAwCihJMTAKVkV2ZW50IE5vdGUKcDUKdEkxMTk4MTk3MzI2Cih0STAw
CnRwNgou
',17,'Witness name: No Name',0);
INSERT INTO "grampsdb_note" VALUES(5,'aef3078a45757c79c22','N0002','2012-05-29 11:56:41.417657','2007-12-20 19:35:26',NULL,0,'KFMnYWVmMzA3OGE0NTc1N2M3OWMyMicKVk4wMDAyCnAxCihscDIKVkJJT0dSQVBIWVx1MDAwYU1h
cnRpbiB3YXMgbGlzdGVkIGFzIGJlaW5nIGEgSHVzbWFuLCAob3duaW5nIGEgaG91c2UgYXMgb3Bw
b3NlZCB0byBhIGZhcm0pIGluIHRoZSBob3VzZSByZWNvcmRzIG9mIEdsYWRzYXguCnAzCmEobHA0
CmFJMDAKKEk0ClZQZXJzb24gTm90ZQpwNQp0STExOTgxOTczMjYKKHRJMDAKdHA2Ci4=
',10,'BIOGRAPHY
Martin was listed as being a Husman, (owning a house as opposed to a farm) in the house records of Gladsax.',0);
INSERT INTO "grampsdb_note" VALUES(6,'aef3078ab5c19ace6e2','N0005','2012-05-29 11:56:41.423730','2007-12-20 19:35:26',NULL,0,'KFMnYWVmMzA3OGFiNWMxOWFjZTZlMicKVk4wMDA1CnAxCihscDIKVlRoZSByZXBvc2l0b3J5IHJl
ZmVyZW5jZSBmcm9tIHRoZSBzb3VyY2UgaXMgaW1wb3J0YW50CnAzCmEobHA0CmFJMDAKKEkxMgpW
U291cmNlIE5vdGUKcDUKdEkxMTk4MTk3MzI2Cih0STAwCnRwNgou
',19,'The repository reference from the source is important',0);
INSERT INTO "grampsdb_note" VALUES(7,'aef3078acbb1df0182a','N0006','2012-05-29 11:56:41.429756','2007-12-20 19:35:26',NULL,0,'KFMnYWVmMzA3OGFjYmIxZGYwMTgyYScKVk4wMDA2CnAxCihscDIKVlNvbWUgbm90ZSBvbiB0aGUg
cmVwbwpwMwphKGxwNAphSTAwCihJMTUKVlJlcG9zaXRvcnkgTm90ZQpwNQp0STExOTgxOTczMjYK
KHRJMDAKdHA2Ci4=
',22,'Some note on the repo',0);
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
INSERT INTO "grampsdb_surname" VALUES(1,1,'Hansdotter','',1,'',1,1);
INSERT INTO "grampsdb_surname" VALUES(2,1,'Smith','',1,'',2,1);
INSERT INTO "grampsdb_surname" VALUES(3,1,'Ohman','',1,'',3,1);
INSERT INTO "grampsdb_surname" VALUES(4,1,'Perkins','',1,'',4,1);
INSERT INTO "grampsdb_surname" VALUES(5,1,'Anderson','',1,'',5,1);
INSERT INTO "grampsdb_surname" VALUES(6,1,'Smith','',1,'',6,1);
INSERT INTO "grampsdb_surname" VALUES(7,1,'Smith','',1,'',7,1);
INSERT INTO "grampsdb_surname" VALUES(8,1,'Smith','',1,'',8,1);
INSERT INTO "grampsdb_surname" VALUES(9,1,'Smith','',1,'',9,1);
INSERT INTO "grampsdb_surname" VALUES(10,1,'Smith','',1,'',10,1);
INSERT INTO "grampsdb_surname" VALUES(11,1,'Smith','',1,'',11,1);
INSERT INTO "grampsdb_surname" VALUES(12,1,'Smith','',1,'',12,1);
INSERT INTO "grampsdb_surname" VALUES(13,1,'Smith','',1,'',13,1);
INSERT INTO "grampsdb_surname" VALUES(14,1,'Smith','',1,'',14,1);
INSERT INTO "grampsdb_surname" VALUES(15,1,'Hansdotter','',1,'',15,1);
INSERT INTO "grampsdb_surname" VALUES(16,1,'Smith','',1,'',16,1);
INSERT INTO "grampsdb_surname" VALUES(17,1,'Jefferson','',1,'',17,1);
INSERT INTO "grampsdb_surname" VALUES(18,1,'Smith','',1,'',18,1);
INSERT INTO "grampsdb_surname" VALUES(19,1,'Smith','',1,'',19,1);
INSERT INTO "grampsdb_surname" VALUES(20,1,'Michaels','',1,'',20,1);
INSERT INTO "grampsdb_surname" VALUES(21,1,'Streiffert','',1,'',21,1);
INSERT INTO "grampsdb_surname" VALUES(22,1,'Smith','',1,'',22,1);
INSERT INTO "grampsdb_surname" VALUES(23,1,'Smith','',1,'',23,1);
INSERT INTO "grampsdb_surname" VALUES(24,1,'Jones','',1,'',24,1);
INSERT INTO "grampsdb_surname" VALUES(25,1,'Smith','',1,'',25,1);
INSERT INTO "grampsdb_surname" VALUES(26,1,'Smith','',1,'',26,1);
INSERT INTO "grampsdb_surname" VALUES(27,1,'Ericsdotter','',1,'',27,1);
INSERT INTO "grampsdb_surname" VALUES(28,1,'Smith','',1,'',28,1);
INSERT INTO "grampsdb_surname" VALUES(29,1,'Horne','',1,'',29,1);
INSERT INTO "grampsdb_surname" VALUES(30,1,'Smith','',1,'',30,1);
INSERT INTO "grampsdb_surname" VALUES(31,1,'Adams','',1,'',31,1);
INSERT INTO "grampsdb_surname" VALUES(32,1,'Nielsen','',1,'',32,1);
INSERT INTO "grampsdb_surname" VALUES(33,1,'Smith','',1,'',33,1);
INSERT INTO "grampsdb_surname" VALUES(34,1,'Smith','',1,'',34,1);
INSERT INTO "grampsdb_surname" VALUES(35,1,'Willard','',1,'',35,1);
INSERT INTO "grampsdb_surname" VALUES(36,1,'Smith','',1,'',36,1);
INSERT INTO "grampsdb_surname" VALUES(37,1,'Smith','',1,'',37,1);
INSERT INTO "grampsdb_surname" VALUES(38,1,'Smith','',1,'',38,1);
INSERT INTO "grampsdb_surname" VALUES(39,1,'Green','',1,'',39,1);
INSERT INTO "grampsdb_surname" VALUES(40,1,'Smith','',1,'',40,1);
INSERT INTO "grampsdb_surname" VALUES(41,1,'Smith','',1,'',41,1);
INSERT INTO "grampsdb_surname" VALUES(42,1,'Smith','',1,'',42,1);
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
INSERT INTO "grampsdb_name" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:33.901477',NULL,NULL,1,4,1,'Kerstina','','','','','','',1,1,1);
INSERT INTO "grampsdb_name" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:33.974097',NULL,NULL,1,4,1,'Martin','','','','','','',1,1,2);
INSERT INTO "grampsdb_name" VALUES(3,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.056076',NULL,NULL,1,4,1,'Marjorie','','','','','','',1,1,3);
INSERT INTO "grampsdb_name" VALUES(4,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.114418',NULL,NULL,1,4,1,'Alice Paula','','','','','','',1,1,4);
INSERT INTO "grampsdb_name" VALUES(5,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.155766',NULL,NULL,1,4,1,'Jennifer','','','','','','',1,1,5);
INSERT INTO "grampsdb_name" VALUES(6,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.214107',NULL,NULL,1,4,1,'Ingeman','','','','','','',1,1,6);
INSERT INTO "grampsdb_name" VALUES(7,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.255723',NULL,NULL,1,4,1,'John Hjalmar','','','','','','',1,1,7);
INSERT INTO "grampsdb_name" VALUES(8,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.303780',NULL,NULL,1,4,1,'Gus','','','','','','',1,1,8);
INSERT INTO "grampsdb_name" VALUES(9,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.368677',NULL,NULL,1,4,1,'Magnes','','','','','','',1,1,9);
INSERT INTO "grampsdb_name" VALUES(10,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.434069',NULL,NULL,1,4,1,'Gustaf','Sr.','','','','','',1,1,10);
INSERT INTO "grampsdb_name" VALUES(11,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.530583',NULL,NULL,1,4,1,'Eric Lloyd','','','','','','',1,1,11);
INSERT INTO "grampsdb_name" VALUES(12,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.578564',NULL,NULL,1,4,1,'Amber Marie','','','','','','',1,1,12);
INSERT INTO "grampsdb_name" VALUES(13,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.630023',NULL,NULL,1,4,1,'Lloyd','','','','','','',1,1,13);
INSERT INTO "grampsdb_name" VALUES(14,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.678113',NULL,NULL,1,4,1,'Kirsti Marie','','','','','','',1,1,14);
INSERT INTO "grampsdb_name" VALUES(15,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.754642',NULL,NULL,1,4,1,'Anna','','','','','','',1,1,15);
INSERT INTO "grampsdb_name" VALUES(16,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.813409',NULL,NULL,1,4,1,'Emil','','','','','','',1,1,16);
INSERT INTO "grampsdb_name" VALUES(17,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.855133',NULL,NULL,1,4,1,'Elna','','','','','','',1,1,17);
INSERT INTO "grampsdb_name" VALUES(18,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.923683',NULL,NULL,1,4,1,'Hjalmar','','','','','','',1,1,18);
INSERT INTO "grampsdb_name" VALUES(19,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:34.982071',NULL,NULL,1,4,1,'Marjorie Lee','','','','','','',1,1,19);
INSERT INTO "grampsdb_name" VALUES(20,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.023332',NULL,NULL,1,4,1,'Evelyn','','','','','','',1,1,20);
INSERT INTO "grampsdb_name" VALUES(21,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.064589',NULL,NULL,1,4,1,'Anna','','','','','','',1,1,21);
INSERT INTO "grampsdb_name" VALUES(22,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.122947',NULL,NULL,1,4,1,'Mason Michael','','','','','','',1,1,22);
INSERT INTO "grampsdb_name" VALUES(23,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.178742',NULL,NULL,1,4,1,'Carl Emil','','','','','','',1,1,23);
INSERT INTO "grampsdb_name" VALUES(24,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.237229',NULL,NULL,1,4,1,'Lillie Harriet','','','','','','',1,1,24);
INSERT INTO "grampsdb_name" VALUES(25,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.295761',NULL,NULL,1,4,1,'Keith Lloyd','','','','','','',1,1,25);
INSERT INTO "grampsdb_name" VALUES(26,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.341227',NULL,NULL,1,4,1,'Edwin Michael','','','','','','',1,1,26);
INSERT INTO "grampsdb_name" VALUES(27,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.438891',NULL,NULL,1,4,1,'Marta','','','','','','',1,1,27);
INSERT INTO "grampsdb_name" VALUES(28,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.480242',NULL,NULL,1,4,1,'Craig Peter','','','','','','',1,1,28);
INSERT INTO "grampsdb_name" VALUES(29,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.531860',NULL,NULL,1,4,1,'Darcy','','','','','','',1,1,29);
INSERT INTO "grampsdb_name" VALUES(30,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.573060',NULL,NULL,1,4,1,'Lars Peter','','','','','','',1,1,30);
INSERT INTO "grampsdb_name" VALUES(31,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.614351',NULL,NULL,1,4,1,'Janice Ann','','','','','','',1,1,31);
INSERT INTO "grampsdb_name" VALUES(32,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.675613',NULL,NULL,1,4,1,'Herman Julius','','','','','','',1,1,32);
INSERT INTO "grampsdb_name" VALUES(33,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.735402',NULL,NULL,1,4,1,'Ingeman','','','','','','',1,1,33);
INSERT INTO "grampsdb_name" VALUES(34,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.777843',NULL,NULL,1,4,1,'Ingar','','','','','','',1,1,34);
INSERT INTO "grampsdb_name" VALUES(35,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.830937',NULL,NULL,1,4,1,'Edwin','','','','','','',1,1,35);
INSERT INTO "grampsdb_name" VALUES(36,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.873874',NULL,NULL,1,4,1,'Martin','','','','','','',1,1,36);
INSERT INTO "grampsdb_name" VALUES(37,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.940970',NULL,NULL,1,4,1,'Marjorie Alice','','','','','','',1,1,37);
INSERT INTO "grampsdb_name" VALUES(38,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:35.987776',NULL,NULL,1,4,1,'Hanna','','','','','','',1,1,38);
INSERT INTO "grampsdb_name" VALUES(39,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:36.030848',NULL,NULL,1,4,1,'Janis Elaine','','','','','','',1,1,39);
INSERT INTO "grampsdb_name" VALUES(40,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:36.073015',NULL,NULL,1,4,1,'Hjalmar','','','','','','',1,1,40);
INSERT INTO "grampsdb_name" VALUES(41,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:36.164806',NULL,NULL,1,4,1,'Hans Peter','','','','','','',1,1,41);
INSERT INTO "grampsdb_name" VALUES(42,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:36.239162',NULL,NULL,1,4,1,'Astrid Shermanna Augusta','','','','','','',1,1,42);
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
    "source_id" integer NOT NULL REFERENCES "grampsdb_source" ("id")
);
CREATE TABLE "grampsdb_citationdatamap" (
    "id" integer NOT NULL PRIMARY KEY,
    "key" varchar(80) NOT NULL,
    "value" varchar(80) NOT NULL,
    "citation_id" integer NOT NULL REFERENCES "grampsdb_citation" ("id")
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
INSERT INTO "grampsdb_address" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:37.228354',NULL,NULL,1,NULL,1);
INSERT INTO "grampsdb_address" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-29 11:56:37.243966',NULL,NULL,1,NULL,2);
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
INSERT INTO "grampsdb_location" VALUES(1,'5th Ave at 42 street','','New York','','New York','USA','11111','',NULL,1,NULL,1);
INSERT INTO "grampsdb_location" VALUES(2,'123 Main St','','Someville','','ST','USA','','',NULL,1,NULL,2);
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
INSERT INTO "grampsdb_url" VALUES(1,0,'http://library.gramps-project.org','',4,1,NULL,NULL,2);
CREATE TABLE "grampsdb_attribute" (
    "id" integer NOT NULL PRIMARY KEY,
    "private" bool NOT NULL,
    "attribute_type_id" integer NOT NULL REFERENCES "grampsdb_attributetype" ("id"),
    "value" text,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL
);
INSERT INTO "grampsdb_attribute" VALUES(1,0,12,'23',52,47);
INSERT INTO "grampsdb_attribute" VALUES(2,0,10,'Bad breath',36,83);
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
INSERT INTO "grampsdb_noteref" VALUES(1,32,2,1,'2012-05-29 11:56:34.010926',NULL,NULL,0,5);
INSERT INTO "grampsdb_noteref" VALUES(2,32,40,1,'2012-05-29 11:56:36.113455',NULL,NULL,0,1);
INSERT INTO "grampsdb_noteref" VALUES(3,35,3,1,'2012-05-29 11:56:36.672908',NULL,NULL,0,2);
INSERT INTO "grampsdb_noteref" VALUES(4,35,4,1,'2012-05-29 11:56:36.690747',NULL,NULL,0,6);
INSERT INTO "grampsdb_noteref" VALUES(5,36,11,1,'2012-05-29 11:56:36.758362',NULL,NULL,0,4);
INSERT INTO "grampsdb_noteref" VALUES(6,36,51,1,'2012-05-29 11:56:36.982543',NULL,NULL,0,3);
INSERT INTO "grampsdb_noteref" VALUES(7,37,2,1,'2012-05-29 11:56:37.237020',NULL,NULL,0,7);
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
INSERT INTO "grampsdb_eventref" VALUES(1,32,1,1,'2012-05-29 11:56:33.916673',NULL,NULL,0,38,3);
INSERT INTO "grampsdb_eventref" VALUES(2,32,1,1,'2012-05-29 11:56:33.921835',NULL,NULL,0,56,3);
INSERT INTO "grampsdb_eventref" VALUES(3,32,2,1,'2012-05-29 11:56:33.981231',NULL,NULL,0,85,3);
INSERT INTO "grampsdb_eventref" VALUES(4,32,2,1,'2012-05-29 11:56:33.986073',NULL,NULL,0,5,3);
INSERT INTO "grampsdb_eventref" VALUES(5,32,2,1,'2012-05-29 11:56:33.990908',NULL,NULL,0,18,3);
INSERT INTO "grampsdb_eventref" VALUES(6,32,3,1,'2012-05-29 11:56:34.063206',NULL,NULL,0,23,3);
INSERT INTO "grampsdb_eventref" VALUES(7,32,3,1,'2012-05-29 11:56:34.068065',NULL,NULL,0,9,3);
INSERT INTO "grampsdb_eventref" VALUES(8,32,4,1,'2012-05-29 11:56:34.121548',NULL,NULL,0,54,3);
INSERT INTO "grampsdb_eventref" VALUES(9,32,5,1,'2012-05-29 11:56:34.162921',NULL,NULL,0,81,3);
INSERT INTO "grampsdb_eventref" VALUES(10,32,5,1,'2012-05-29 11:56:34.167777',NULL,NULL,0,68,3);
INSERT INTO "grampsdb_eventref" VALUES(11,32,6,1,'2012-05-29 11:56:34.221246',NULL,NULL,0,39,3);
INSERT INTO "grampsdb_eventref" VALUES(12,32,7,1,'2012-05-29 11:56:34.262977',NULL,NULL,0,17,3);
INSERT INTO "grampsdb_eventref" VALUES(13,32,8,1,'2012-05-29 11:56:34.310911',NULL,NULL,0,80,3);
INSERT INTO "grampsdb_eventref" VALUES(14,32,8,1,'2012-05-29 11:56:34.315778',NULL,NULL,0,33,3);
INSERT INTO "grampsdb_eventref" VALUES(15,32,9,1,'2012-05-29 11:56:34.375832',NULL,NULL,0,20,3);
INSERT INTO "grampsdb_eventref" VALUES(16,32,9,1,'2012-05-29 11:56:34.380722',NULL,NULL,0,21,3);
INSERT INTO "grampsdb_eventref" VALUES(17,32,10,1,'2012-05-29 11:56:34.441188',NULL,NULL,0,35,3);
INSERT INTO "grampsdb_eventref" VALUES(18,32,10,1,'2012-05-29 11:56:34.446027',NULL,NULL,0,6,3);
INSERT INTO "grampsdb_eventref" VALUES(19,32,10,1,'2012-05-29 11:56:34.450857',NULL,NULL,0,70,3);
INSERT INTO "grampsdb_eventref" VALUES(20,32,10,1,'2012-05-29 11:56:34.455686',NULL,NULL,0,48,3);
INSERT INTO "grampsdb_eventref" VALUES(21,32,11,1,'2012-05-29 11:56:34.537712',NULL,NULL,0,4,3);
INSERT INTO "grampsdb_eventref" VALUES(22,32,12,1,'2012-05-29 11:56:34.585734',NULL,NULL,0,82,3);
INSERT INTO "grampsdb_eventref" VALUES(23,32,12,1,'2012-05-29 11:56:34.590616',NULL,NULL,0,45,3);
INSERT INTO "grampsdb_eventref" VALUES(24,32,13,1,'2012-05-29 11:56:34.637221',NULL,NULL,0,53,3);
INSERT INTO "grampsdb_eventref" VALUES(25,32,14,1,'2012-05-29 11:56:34.685273',NULL,NULL,0,49,3);
INSERT INTO "grampsdb_eventref" VALUES(26,32,14,1,'2012-05-29 11:56:34.690136',NULL,NULL,0,19,3);
INSERT INTO "grampsdb_eventref" VALUES(27,32,15,1,'2012-05-29 11:56:34.761887',NULL,NULL,0,1,3);
INSERT INTO "grampsdb_eventref" VALUES(28,32,15,1,'2012-05-29 11:56:34.766812',NULL,NULL,0,79,3);
INSERT INTO "grampsdb_eventref" VALUES(29,32,16,1,'2012-05-29 11:56:34.820581',NULL,NULL,0,13,3);
INSERT INTO "grampsdb_eventref" VALUES(30,32,17,1,'2012-05-29 11:56:34.862335',NULL,NULL,0,10,3);
INSERT INTO "grampsdb_eventref" VALUES(31,32,17,1,'2012-05-29 11:56:34.867213',NULL,NULL,0,72,3);
INSERT INTO "grampsdb_eventref" VALUES(32,32,17,1,'2012-05-29 11:56:34.872062',NULL,NULL,0,73,3);
INSERT INTO "grampsdb_eventref" VALUES(33,32,18,1,'2012-05-29 11:56:34.930858',NULL,NULL,0,47,3);
INSERT INTO "grampsdb_eventref" VALUES(34,32,18,1,'2012-05-29 11:56:34.935727',NULL,NULL,0,84,3);
INSERT INTO "grampsdb_eventref" VALUES(35,32,19,1,'2012-05-29 11:56:34.989213',NULL,NULL,0,32,3);
INSERT INTO "grampsdb_eventref" VALUES(36,32,20,1,'2012-05-29 11:56:35.030471',NULL,NULL,0,16,3);
INSERT INTO "grampsdb_eventref" VALUES(37,32,21,1,'2012-05-29 11:56:35.071762',NULL,NULL,0,7,3);
INSERT INTO "grampsdb_eventref" VALUES(38,32,21,1,'2012-05-29 11:56:35.076645',NULL,NULL,0,88,3);
INSERT INTO "grampsdb_eventref" VALUES(39,32,22,1,'2012-05-29 11:56:35.130065',NULL,NULL,0,40,3);
INSERT INTO "grampsdb_eventref" VALUES(40,32,22,1,'2012-05-29 11:56:35.134952',NULL,NULL,0,41,3);
INSERT INTO "grampsdb_eventref" VALUES(41,32,23,1,'2012-05-29 11:56:35.185888',NULL,NULL,0,46,3);
INSERT INTO "grampsdb_eventref" VALUES(42,32,23,1,'2012-05-29 11:56:35.190749',NULL,NULL,0,83,3);
INSERT INTO "grampsdb_eventref" VALUES(43,32,24,1,'2012-05-29 11:56:35.244393',NULL,NULL,0,34,3);
INSERT INTO "grampsdb_eventref" VALUES(44,32,24,1,'2012-05-29 11:56:35.249246',NULL,NULL,0,44,3);
INSERT INTO "grampsdb_eventref" VALUES(45,32,25,1,'2012-05-29 11:56:35.302924',NULL,NULL,0,14,3);
INSERT INTO "grampsdb_eventref" VALUES(46,32,26,1,'2012-05-29 11:56:35.355340',NULL,NULL,0,37,3);
INSERT INTO "grampsdb_eventref" VALUES(47,32,26,1,'2012-05-29 11:56:35.360204',NULL,NULL,0,11,3);
INSERT INTO "grampsdb_eventref" VALUES(48,32,26,1,'2012-05-29 11:56:35.367703',NULL,NULL,0,55,3);
INSERT INTO "grampsdb_eventref" VALUES(49,32,26,1,'2012-05-29 11:56:35.372568',NULL,NULL,0,25,3);
INSERT INTO "grampsdb_eventref" VALUES(50,32,27,1,'2012-05-29 11:56:35.446043',NULL,NULL,0,87,3);
INSERT INTO "grampsdb_eventref" VALUES(51,32,28,1,'2012-05-29 11:56:35.487386',NULL,NULL,0,36,3);
INSERT INTO "grampsdb_eventref" VALUES(52,32,28,1,'2012-05-29 11:56:35.492260',NULL,NULL,0,51,3);
INSERT INTO "grampsdb_eventref" VALUES(53,32,29,1,'2012-05-29 11:56:35.539023',NULL,NULL,0,71,3);
INSERT INTO "grampsdb_eventref" VALUES(54,32,30,1,'2012-05-29 11:56:35.580229',NULL,NULL,0,24,3);
INSERT INTO "grampsdb_eventref" VALUES(55,32,31,1,'2012-05-29 11:56:35.621485',NULL,NULL,0,52,3);
INSERT INTO "grampsdb_eventref" VALUES(56,32,31,1,'2012-05-29 11:56:35.626351',NULL,NULL,0,8,3);
INSERT INTO "grampsdb_eventref" VALUES(57,32,31,1,'2012-05-29 11:56:35.631227',NULL,NULL,0,22,3);
INSERT INTO "grampsdb_eventref" VALUES(58,32,32,1,'2012-05-29 11:56:35.682782',NULL,NULL,0,2,3);
INSERT INTO "grampsdb_eventref" VALUES(59,32,32,2,'2012-05-29 11:56:35.687647',NULL,NULL,0,3,3);
INSERT INTO "grampsdb_eventref" VALUES(60,32,33,1,'2012-05-29 11:56:35.742828',NULL,NULL,0,50,3);
INSERT INTO "grampsdb_eventref" VALUES(61,32,34,1,'2012-05-29 11:56:35.785684',NULL,NULL,0,12,3);
INSERT INTO "grampsdb_eventref" VALUES(62,32,34,1,'2012-05-29 11:56:35.790604',NULL,NULL,0,11,9);
INSERT INTO "grampsdb_eventref" VALUES(63,32,35,1,'2012-05-29 11:56:35.838236',NULL,NULL,0,29,3);
INSERT INTO "grampsdb_eventref" VALUES(64,32,36,1,'2012-05-29 11:56:35.881116',NULL,NULL,0,26,3);
INSERT INTO "grampsdb_eventref" VALUES(65,32,36,1,'2012-05-29 11:56:35.886444',NULL,NULL,0,57,3);
INSERT INTO "grampsdb_eventref" VALUES(66,32,37,1,'2012-05-29 11:56:35.948356',NULL,NULL,0,27,3);
INSERT INTO "grampsdb_eventref" VALUES(67,32,38,1,'2012-05-29 11:56:35.995661',NULL,NULL,0,15,3);
INSERT INTO "grampsdb_eventref" VALUES(68,32,39,1,'2012-05-29 11:56:36.038109',NULL,NULL,0,28,3);
INSERT INTO "grampsdb_eventref" VALUES(69,32,40,1,'2012-05-29 11:56:36.080353',NULL,NULL,0,30,3);
INSERT INTO "grampsdb_eventref" VALUES(70,32,40,1,'2012-05-29 11:56:36.085702',NULL,NULL,0,74,3);
INSERT INTO "grampsdb_eventref" VALUES(71,32,40,1,'2012-05-29 11:56:36.090731',NULL,NULL,0,58,3);
INSERT INTO "grampsdb_eventref" VALUES(72,32,40,1,'2012-05-29 11:56:36.095600',NULL,NULL,0,59,3);
INSERT INTO "grampsdb_eventref" VALUES(73,32,41,1,'2012-05-29 11:56:36.172190',NULL,NULL,0,67,3);
INSERT INTO "grampsdb_eventref" VALUES(74,32,41,1,'2012-05-29 11:56:36.177430',NULL,NULL,0,31,3);
INSERT INTO "grampsdb_eventref" VALUES(75,32,42,1,'2012-05-29 11:56:36.246393',NULL,NULL,0,86,3);
INSERT INTO "grampsdb_eventref" VALUES(76,32,42,1,'2012-05-29 11:56:36.251450',NULL,NULL,0,69,3);
INSERT INTO "grampsdb_eventref" VALUES(77,33,1,1,'2012-05-29 11:56:36.327302',NULL,NULL,0,62,10);
INSERT INTO "grampsdb_eventref" VALUES(78,33,2,1,'2012-05-29 11:56:36.339439',NULL,NULL,0,42,10);
INSERT INTO "grampsdb_eventref" VALUES(79,33,3,1,'2012-05-29 11:56:36.351672',NULL,NULL,0,89,10);
INSERT INTO "grampsdb_eventref" VALUES(80,33,4,1,'2012-05-29 11:56:36.369818',NULL,NULL,0,60,10);
INSERT INTO "grampsdb_eventref" VALUES(81,33,6,1,'2012-05-29 11:56:36.389447',NULL,NULL,0,65,10);
INSERT INTO "grampsdb_eventref" VALUES(82,33,8,1,'2012-05-29 11:56:36.414948',NULL,NULL,0,78,10);
INSERT INTO "grampsdb_eventref" VALUES(83,33,9,1,'2012-05-29 11:56:36.443168',NULL,NULL,0,76,10);
INSERT INTO "grampsdb_eventref" VALUES(84,33,9,1,'2012-05-29 11:56:36.448278',NULL,NULL,0,63,10);
INSERT INTO "grampsdb_eventref" VALUES(85,33,10,1,'2012-05-29 11:56:36.478565',NULL,NULL,0,64,10);
INSERT INTO "grampsdb_eventref" VALUES(86,33,11,1,'2012-05-29 11:56:36.533158',NULL,NULL,0,77,10);
INSERT INTO "grampsdb_eventref" VALUES(87,33,12,1,'2012-05-29 11:56:36.569394',NULL,NULL,0,75,10);
INSERT INTO "grampsdb_eventref" VALUES(88,33,13,1,'2012-05-29 11:56:36.587820',NULL,NULL,0,61,10);
INSERT INTO "grampsdb_eventref" VALUES(89,33,14,1,'2012-05-29 11:56:36.618093',NULL,NULL,0,66,10);
INSERT INTO "grampsdb_eventref" VALUES(90,33,15,1,'2012-05-29 11:56:36.642516',NULL,NULL,0,43,10);
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
INSERT INTO "grampsdb_repositoryref" VALUES(1,35,3,1,'2012-05-29 11:56:36.679837',NULL,NULL,0,1,13,'what-321-ever');
INSERT INTO "grampsdb_repositoryref" VALUES(2,35,3,1,'2012-05-29 11:56:36.685133',NULL,NULL,0,2,10,'nothing-0');
INSERT INTO "grampsdb_repositoryref" VALUES(3,35,4,1,'2012-05-29 11:56:36.695576',NULL,NULL,0,1,8,'CA-123-LL-456_Num/ber');
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
    "description" varchar(50) NOT NULL
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
INSERT INTO "grampsdb_citationref" VALUES(1,42,26,1,'2012-05-29 11:56:35.350273',NULL,NULL,0,2);
INSERT INTO "grampsdb_citationref" VALUES(2,36,37,1,'2012-05-29 11:56:36.903968',NULL,NULL,0,3);
INSERT INTO "grampsdb_citationref" VALUES(3,36,62,1,'2012-05-29 11:56:37.056844',NULL,NULL,0,1);
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
INSERT INTO "grampsdb_childref" VALUES(1,33,1,1,'2012-05-29 11:56:36.315738',NULL,NULL,0,2,2,37);
INSERT INTO "grampsdb_childref" VALUES(2,33,1,1,'2012-05-29 11:56:36.322097',NULL,NULL,0,2,2,26);
INSERT INTO "grampsdb_childref" VALUES(3,33,4,1,'2012-05-29 11:56:36.364890',NULL,NULL,0,2,2,36);
INSERT INTO "grampsdb_childref" VALUES(4,33,7,1,'2012-05-29 11:56:36.402567',NULL,NULL,0,2,2,13);
INSERT INTO "grampsdb_childref" VALUES(5,33,9,1,'2012-05-29 11:56:36.427962',NULL,NULL,0,2,2,22);
INSERT INTO "grampsdb_childref" VALUES(6,33,9,1,'2012-05-29 11:56:36.433958',NULL,NULL,0,2,2,12);
INSERT INTO "grampsdb_childref" VALUES(7,33,10,1,'2012-05-29 11:56:36.461307',NULL,NULL,0,2,2,9);
INSERT INTO "grampsdb_childref" VALUES(8,33,10,1,'2012-05-29 11:56:36.467370',NULL,NULL,0,2,2,16);
INSERT INTO "grampsdb_childref" VALUES(9,33,10,1,'2012-05-29 11:56:36.473368',NULL,NULL,0,2,2,10);
INSERT INTO "grampsdb_childref" VALUES(10,33,11,1,'2012-05-29 11:56:36.491888',NULL,NULL,0,2,2,14);
INSERT INTO "grampsdb_childref" VALUES(11,33,11,1,'2012-05-29 11:56:36.497950',NULL,NULL,0,2,2,42);
INSERT INTO "grampsdb_childref" VALUES(12,33,11,1,'2012-05-29 11:56:36.503927',NULL,NULL,0,2,2,18);
INSERT INTO "grampsdb_childref" VALUES(13,33,11,1,'2012-05-29 11:56:36.510065',NULL,NULL,0,2,2,40);
INSERT INTO "grampsdb_childref" VALUES(14,33,11,1,'2012-05-29 11:56:36.516175',NULL,NULL,0,2,2,8);
INSERT INTO "grampsdb_childref" VALUES(15,33,11,1,'2012-05-29 11:56:36.522092',NULL,NULL,0,2,2,23);
INSERT INTO "grampsdb_childref" VALUES(16,33,11,1,'2012-05-29 11:56:36.528111',NULL,NULL,0,2,2,41);
INSERT INTO "grampsdb_childref" VALUES(17,33,12,1,'2012-05-29 11:56:36.546440',NULL,NULL,0,2,2,38);
INSERT INTO "grampsdb_childref" VALUES(18,33,12,1,'2012-05-29 11:56:36.552315',NULL,NULL,0,2,2,34);
INSERT INTO "grampsdb_childref" VALUES(19,33,12,1,'2012-05-29 11:56:36.558258',NULL,NULL,0,2,2,6);
INSERT INTO "grampsdb_childref" VALUES(20,33,12,1,'2012-05-29 11:56:36.564272',NULL,NULL,0,2,2,2);
INSERT INTO "grampsdb_childref" VALUES(21,33,13,1,'2012-05-29 11:56:36.582457',NULL,NULL,0,3,3,30);
INSERT INTO "grampsdb_childref" VALUES(22,33,14,1,'2012-05-29 11:56:36.600993',NULL,NULL,0,3,3,11);
INSERT INTO "grampsdb_childref" VALUES(23,33,14,1,'2012-05-29 11:56:36.607081',NULL,NULL,0,2,2,25);
INSERT INTO "grampsdb_childref" VALUES(24,33,14,1,'2012-05-29 11:56:36.612969',NULL,NULL,0,2,2,28);
INSERT INTO "grampsdb_childref" VALUES(25,33,15,1,'2012-05-29 11:56:36.631494',NULL,NULL,0,2,2,7);
INSERT INTO "grampsdb_childref" VALUES(26,33,15,1,'2012-05-29 11:56:36.637541',NULL,NULL,0,2,2,19);
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
INSERT INTO "grampsdb_mediaref" VALUES(1,32,10,1,'2012-05-29 11:56:34.476193',NULL,NULL,0,0,0,0,0,1);
INSERT INTO "grampsdb_mediaref" VALUES(2,32,10,1,'2012-05-29 11:56:34.480487',NULL,NULL,0,0,0,0,0,3);
INSERT INTO "grampsdb_mediaref" VALUES(3,32,22,1,'2012-05-29 11:56:35.145709',NULL,NULL,0,0,0,0,0,6);
INSERT INTO "grampsdb_mediaref" VALUES(4,32,25,1,'2012-05-29 11:56:35.313708',NULL,NULL,0,0,0,0,0,5);
INSERT INTO "grampsdb_mediaref" VALUES(5,32,26,1,'2012-05-29 11:56:35.390110',NULL,NULL,0,0,0,0,0,4);
INSERT INTO "grampsdb_mediaref" VALUES(6,32,37,1,'2012-05-29 11:56:35.959351',NULL,NULL,0,0,0,0,0,2);
INSERT INTO "grampsdb_mediaref" VALUES(7,33,9,1,'2012-05-29 11:56:36.438033',NULL,NULL,0,0,0,0,0,6);
CREATE TABLE "grampsdb_report" (
    "id" integer NOT NULL PRIMARY KEY,
    "gramps_id" text,
    "name" text,
    "handle" text,
    "report_type" text,
    "options" text
);
INSERT INTO "grampsdb_report" VALUES(1,'R0001','Ahnentafel Report','ancestor_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(2,'R0002','birthday_report','birthday_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(3,'R0003','custom_text','custom_text','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(4,'R0004','descend_report','descend_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(5,'R0005','det_ancestor_report','det_ancestor_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(6,'R0006','det_descendant_report','det_descendant_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(7,'R0007','endofline_report','endofline_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(8,'R0008','family_group','family_group','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(9,'R0009','indiv_complete','indiv_complete','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(10,'R0010','kinship_report','kinship_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(11,'R0011','tag_report','tag_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(12,'R0012','number_of_ancestors_report','number_of_ancestors_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(13,'R0013','place_report','place_report','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(14,'R0014','simple_book_title','simple_book_title','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(15,'R0015','summary','summary','textreport',NULL);
INSERT INTO "grampsdb_report" VALUES(16,'R0016','Export','gedcom_export','export','off=ged');
INSERT INTO "grampsdb_report" VALUES(17,'R0017','Gramps XML Export','ex_gpkg','export','off=gramps');
INSERT INTO "grampsdb_report" VALUES(18,'R0018','Import','im_ged','import','iff=ged i=http://arborvita.free.fr/Kennedy/Kennedy.ged');
INSERT INTO "grampsdb_report" VALUES(19,'R0019','Gramps package (portable XML) Import','im_gpkg','import','iff=gramps i=http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/example/gramps/example.gramps?revision=18333');
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
CREATE INDEX "auth_permission_1bb8f392" ON "auth_permission" ("content_type_id");
CREATE INDEX "auth_group_permissions_425ae3c4" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_1e014c8f" ON "auth_group_permissions" ("permission_id");
CREATE INDEX "auth_user_user_permissions_403f60f" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_1e014c8f" ON "auth_user_user_permissions" ("permission_id");
CREATE INDEX "auth_user_groups_403f60f" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_425ae3c4" ON "auth_user_groups" ("group_id");
CREATE INDEX "auth_message_403f60f" ON "auth_message" ("user_id");
CREATE INDEX "django_session_3da3d3d8" ON "django_session" ("expire_date");
CREATE INDEX "django_admin_log_403f60f" ON "django_admin_log" ("user_id");
CREATE INDEX "django_admin_log_1bb8f392" ON "django_admin_log" ("content_type_id");
CREATE INDEX "grampsdb_person_families_21b911c5" ON "grampsdb_person_families" ("person_id");
CREATE INDEX "grampsdb_person_families_330df8aa" ON "grampsdb_person_families" ("family_id");
CREATE INDEX "grampsdb_person_tags_21b911c5" ON "grampsdb_person_tags" ("person_id");
CREATE INDEX "grampsdb_person_tags_3747b463" ON "grampsdb_person_tags" ("tag_id");
CREATE INDEX "grampsdb_person_parent_families_21b911c5" ON "grampsdb_person_parent_families" ("person_id");
CREATE INDEX "grampsdb_person_parent_families_330df8aa" ON "grampsdb_person_parent_families" ("family_id");
CREATE INDEX "grampsdb_person_79775e9" ON "grampsdb_person" ("gender_type_id");
CREATE INDEX "grampsdb_person_3a672176" ON "grampsdb_person" ("birth_id");
CREATE INDEX "grampsdb_person_bf9c6d5" ON "grampsdb_person" ("death_id");
CREATE INDEX "grampsdb_family_tags_330df8aa" ON "grampsdb_family_tags" ("family_id");
CREATE INDEX "grampsdb_family_tags_3747b463" ON "grampsdb_family_tags" ("tag_id");
CREATE INDEX "grampsdb_family_656bfb9c" ON "grampsdb_family" ("father_id");
CREATE INDEX "grampsdb_family_3800eb51" ON "grampsdb_family" ("mother_id");
CREATE INDEX "grampsdb_family_75e9c8a0" ON "grampsdb_family" ("family_rel_type_id");
CREATE INDEX "grampsdb_citation_7607617b" ON "grampsdb_citation" ("source_id");
CREATE INDEX "grampsdb_event_349f2f81" ON "grampsdb_event" ("event_type_id");
CREATE INDEX "grampsdb_event_3bc6e294" ON "grampsdb_event" ("place_id");
CREATE INDEX "grampsdb_repository_5f9de118" ON "grampsdb_repository" ("repository_type_id");
CREATE INDEX "grampsdb_media_tags_11f50c51" ON "grampsdb_media_tags" ("media_id");
CREATE INDEX "grampsdb_media_tags_3747b463" ON "grampsdb_media_tags" ("tag_id");
CREATE INDEX "grampsdb_note_tags_14a186ec" ON "grampsdb_note_tags" ("note_id");
CREATE INDEX "grampsdb_note_tags_3747b463" ON "grampsdb_note_tags" ("tag_id");
CREATE INDEX "grampsdb_note_71afbcea" ON "grampsdb_note" ("note_type_id");
CREATE INDEX "grampsdb_surname_5489fd8b" ON "grampsdb_surname" ("name_origin_type_id");
CREATE INDEX "grampsdb_surname_632e075f" ON "grampsdb_surname" ("name_id");
CREATE INDEX "grampsdb_name_442d7f4b" ON "grampsdb_name" ("name_type_id");
CREATE INDEX "grampsdb_name_50fec5b8" ON "grampsdb_name" ("sort_as_id");
CREATE INDEX "grampsdb_name_a2b2fd7" ON "grampsdb_name" ("display_as_id");
CREATE INDEX "grampsdb_name_21b911c5" ON "grampsdb_name" ("person_id");
CREATE INDEX "grampsdb_lds_563aeca2" ON "grampsdb_lds" ("lds_type_id");
CREATE INDEX "grampsdb_lds_3bc6e294" ON "grampsdb_lds" ("place_id");
CREATE INDEX "grampsdb_lds_5934a803" ON "grampsdb_lds" ("famc_id");
CREATE INDEX "grampsdb_lds_44224078" ON "grampsdb_lds" ("status_id");
CREATE INDEX "grampsdb_lds_21b911c5" ON "grampsdb_lds" ("person_id");
CREATE INDEX "grampsdb_lds_330df8aa" ON "grampsdb_lds" ("family_id");
CREATE INDEX "grampsdb_markup_14a186ec" ON "grampsdb_markup" ("note_id");
CREATE INDEX "grampsdb_markup_46e39021" ON "grampsdb_markup" ("styled_text_tag_type_id");
CREATE INDEX "grampsdb_sourcedatamap_7607617b" ON "grampsdb_sourcedatamap" ("source_id");
CREATE INDEX "grampsdb_citationdatamap_6a711303" ON "grampsdb_citationdatamap" ("citation_id");
CREATE INDEX "grampsdb_address_21b911c5" ON "grampsdb_address" ("person_id");
CREATE INDEX "grampsdb_address_6a730446" ON "grampsdb_address" ("repository_id");
CREATE INDEX "grampsdb_location_3bc6e294" ON "grampsdb_location" ("place_id");
CREATE INDEX "grampsdb_location_4dec3e17" ON "grampsdb_location" ("address_id");
CREATE INDEX "grampsdb_url_69aa47aa" ON "grampsdb_url" ("url_type_id");
CREATE INDEX "grampsdb_url_21b911c5" ON "grampsdb_url" ("person_id");
CREATE INDEX "grampsdb_url_3bc6e294" ON "grampsdb_url" ("place_id");
CREATE INDEX "grampsdb_url_6a730446" ON "grampsdb_url" ("repository_id");
CREATE INDEX "grampsdb_attribute_13db1433" ON "grampsdb_attribute" ("attribute_type_id");
CREATE INDEX "grampsdb_attribute_518e5aa5" ON "grampsdb_attribute" ("object_type_id");
CREATE INDEX "grampsdb_noteref_518e5aa5" ON "grampsdb_noteref" ("object_type_id");
CREATE INDEX "grampsdb_noteref_27acd269" ON "grampsdb_noteref" ("ref_object_id");
CREATE INDEX "grampsdb_eventref_518e5aa5" ON "grampsdb_eventref" ("object_type_id");
CREATE INDEX "grampsdb_eventref_27acd269" ON "grampsdb_eventref" ("ref_object_id");
CREATE INDEX "grampsdb_eventref_6ae08856" ON "grampsdb_eventref" ("role_type_id");
CREATE INDEX "grampsdb_repositoryref_518e5aa5" ON "grampsdb_repositoryref" ("object_type_id");
CREATE INDEX "grampsdb_repositoryref_27acd269" ON "grampsdb_repositoryref" ("ref_object_id");
CREATE INDEX "grampsdb_repositoryref_4fd76720" ON "grampsdb_repositoryref" ("source_media_type_id");
CREATE INDEX "grampsdb_personref_518e5aa5" ON "grampsdb_personref" ("object_type_id");
CREATE INDEX "grampsdb_personref_27acd269" ON "grampsdb_personref" ("ref_object_id");
CREATE INDEX "grampsdb_citationref_518e5aa5" ON "grampsdb_citationref" ("object_type_id");
CREATE INDEX "grampsdb_citationref_6a711303" ON "grampsdb_citationref" ("citation_id");
CREATE INDEX "grampsdb_childref_518e5aa5" ON "grampsdb_childref" ("object_type_id");
CREATE INDEX "grampsdb_childref_6f3234de" ON "grampsdb_childref" ("father_rel_type_id");
CREATE INDEX "grampsdb_childref_216a8ffd" ON "grampsdb_childref" ("mother_rel_type_id");
CREATE INDEX "grampsdb_childref_27acd269" ON "grampsdb_childref" ("ref_object_id");
CREATE INDEX "grampsdb_mediaref_518e5aa5" ON "grampsdb_mediaref" ("object_type_id");
CREATE INDEX "grampsdb_mediaref_27acd269" ON "grampsdb_mediaref" ("ref_object_id");
COMMIT;
