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
INSERT INTO "auth_permission" VALUES(61,'Can add markup type',21,'add_markuptype');
INSERT INTO "auth_permission" VALUES(62,'Can change markup type',21,'change_markuptype');
INSERT INTO "auth_permission" VALUES(63,'Can delete markup type',21,'delete_markuptype');
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
INSERT INTO "auth_user" VALUES(1,'admin','','','bugs@gramps-project.org','sha1$61e84$9f92d64496a8785f9a398a1e1a2e9bc9bdc6f3b0',1,1,1,'2012-05-27 15:07:35.340745','2012-05-26 14:00:59.964988');
INSERT INTO "auth_user" VALUES(2,'admin1','Regular','User','bugs@gramps-project.org','sha1$10320$09720d341391749d5fad46aad6dc1d81d689a628',0,1,0,'2012-05-27 15:07:00.552571','2012-05-27 15:06:23');
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
INSERT INTO "django_content_type" VALUES(21,'markup type','grampsdb','markuptype');
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
INSERT INTO "django_session" VALUES('ff61fbd3ff9efe61263f3a19d8b288e3','MmU1MjliMDM2NzcyODdjNmJlOTgzMGFiYzc2MjFkMmViYWFiOTIzMjqAAn1xAShVEl9hdXRoX3Vz
ZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED
VQ1fYXV0aF91c2VyX2lkcQRLAXUu
','2012-06-10 15:07:35.594186');
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
INSERT INTO "django_admin_log" VALUES(1,'2012-05-27 15:06:23.550452',1,3,'2','admin1',1,'');
INSERT INTO "django_admin_log" VALUES(2,'2012-05-27 15:06:45.913479',1,3,'2','admin1',2,'Changed first_name, last_name and email.');
CREATE TABLE "grampsdb_profile" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id"),
    "css_theme" varchar(40) NOT NULL
);
INSERT INTO "grampsdb_profile" VALUES(1,1,'Web_Mainz.css');
INSERT INTO "grampsdb_profile" VALUES(2,2,'Web_Mainz.css');
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
CREATE TABLE "grampsdb_markuptype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
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
INSERT INTO "grampsdb_config" VALUES(2,'db_version','database scheme version','str','0.5.1');
INSERT INTO "grampsdb_config" VALUES(3,'db_created','database creation date/time','str','2012-05-26 14:00');
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
INSERT INTO "grampsdb_tag" VALUES(1,'c2b9ce225642d2f033f5604ca10','','2012-05-27 15:05:29.553890','2012-05-27 15:05:29.552959','admin','ToDo','',NULL);
INSERT INTO "grampsdb_tag" VALUES(2,'c2b9ce592663703fd17ee360f52','','2012-05-27 15:05:41.796669','2012-05-27 15:05:41.796611','admin','Completed','',NULL);
CREATE TABLE "grampsdb_person_families" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "family_id" integer NOT NULL,
    UNIQUE ("person_id", "family_id")
);
INSERT INTO "grampsdb_person_families" VALUES(1,1,6);
INSERT INTO "grampsdb_person_families" VALUES(2,2,9);
INSERT INTO "grampsdb_person_families" VALUES(3,3,7);
INSERT INTO "grampsdb_person_families" VALUES(5,6,5);
INSERT INTO "grampsdb_person_families" VALUES(6,7,14);
INSERT INTO "grampsdb_person_families" VALUES(7,8,5);
INSERT INTO "grampsdb_person_families" VALUES(8,10,1);
INSERT INTO "grampsdb_person_families" VALUES(9,11,13);
INSERT INTO "grampsdb_person_families" VALUES(10,13,11);
INSERT INTO "grampsdb_person_families" VALUES(11,14,9);
INSERT INTO "grampsdb_person_families" VALUES(12,16,10);
INSERT INTO "grampsdb_person_families" VALUES(13,17,11);
INSERT INTO "grampsdb_person_families" VALUES(14,19,2);
INSERT INTO "grampsdb_person_families" VALUES(15,20,10);
INSERT INTO "grampsdb_person_families" VALUES(16,21,3);
INSERT INTO "grampsdb_person_families" VALUES(17,22,8);
INSERT INTO "grampsdb_person_families" VALUES(18,26,4);
INSERT INTO "grampsdb_person_families" VALUES(19,28,13);
INSERT INTO "grampsdb_person_families" VALUES(20,29,14);
INSERT INTO "grampsdb_person_families" VALUES(21,30,1);
INSERT INTO "grampsdb_person_families" VALUES(22,31,2);
INSERT INTO "grampsdb_person_families" VALUES(23,32,6);
INSERT INTO "grampsdb_person_families" VALUES(24,35,15);
INSERT INTO "grampsdb_person_families" VALUES(25,37,7);
INSERT INTO "grampsdb_person_families" VALUES(26,39,4);
INSERT INTO "grampsdb_person_families" VALUES(27,40,12);
INSERT INTO "grampsdb_person_families" VALUES(28,41,12);
INSERT INTO "grampsdb_person_families" VALUES(29,41,15);
INSERT INTO "grampsdb_person_families" VALUES(30,42,8);
CREATE TABLE "grampsdb_person_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "grampsdb_tag" ("id"),
    UNIQUE ("person_id", "tag_id")
);
INSERT INTO "grampsdb_person_tags" VALUES(1,4,2);
CREATE TABLE "grampsdb_person_parent_families" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "family_id" integer NOT NULL,
    UNIQUE ("person_id", "family_id")
);
INSERT INTO "grampsdb_person_parent_families" VALUES(1,5,6);
INSERT INTO "grampsdb_person_parent_families" VALUES(2,6,2);
INSERT INTO "grampsdb_person_parent_families" VALUES(3,9,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(4,12,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(5,15,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(6,17,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(7,18,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(8,20,6);
INSERT INTO "grampsdb_person_parent_families" VALUES(9,21,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(10,22,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(11,23,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(12,24,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(13,25,6);
INSERT INTO "grampsdb_person_parent_families" VALUES(14,26,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(15,27,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(16,28,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(17,29,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(18,30,2);
INSERT INTO "grampsdb_person_parent_families" VALUES(19,31,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(20,32,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(21,33,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(22,34,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(23,36,2);
INSERT INTO "grampsdb_person_parent_families" VALUES(24,37,9);
INSERT INTO "grampsdb_person_parent_families" VALUES(25,38,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(26,41,1);
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
INSERT INTO "grampsdb_person" VALUES(1,'C1OT6DUBMZ3HAD998D','I0041','2012-05-27 14:42:38.734353','2007-12-20 19:35:26',NULL,0,NULL,3,1,36,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(2,'X4NT6DHD3QU8ADPPZT','I0027','2012-05-27 14:42:38.984052','2007-12-20 19:35:26',NULL,0,NULL,2,1,51,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(3,'XBNT6DUEXL3CM228BN','I0036','2012-05-27 14:42:39.241347','2007-12-20 19:35:26',NULL,0,NULL,3,0,29,77,0,1);
INSERT INTO "grampsdb_person" VALUES(4,'VENT6DO89X29B69M6','I0030','2012-05-27 15:06:03.581046','2012-05-27 15:06:01.843428','admin',0,'KFMnVkVOVDZETzg5WDI5QjY5TTYnClZJMDAzMApwMQpJMAooSTAwCihsKGwoSTAKSTAKSTAKKEkw
CkkwCkkwCkkwMApOTk5OdFYKSTAKSTAKdFZKYW5pY2UgQW5uCnAyCihscDMKKFZBZGFtcwpWCkkw
MQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUKcDUKdFYKSTAKSTAKVgpWClYKdChs
SS0xCkkwCihscDYKKEkwMAoobChsVmE3MDFlOGZlM2QzNTExM2E5YTcKKEkxClZQcmltYXJ5CnR0
cDcKYShJMDAKKGwobFZhNzAxZThmZTNlZTU4MTgwMmQ4CihJMQpWUHJpbWFyeQp0dHA4CmEoSTAw
CihsKGxWYTcwMWU4ZmU0MDQ1M2M3YThjNgooSTEKVlByaW1hcnkKdHRwOQphKGwobChsKGwobChs
KGwobChsSTEzMzgxNDU1NjEKKHRJMDAKKGx0cDEwCi4=
',3,1,62,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(5,'RZLT6DH4XGWLSK1Q0Z','I0029','2012-05-27 14:42:39.761271','2007-12-20 19:35:26',NULL,0,NULL,2,1,67,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(6,'DJNT6D3IOTYV1HTLO1','I0003','2012-05-27 14:42:40.019129','2007-12-20 19:35:26',NULL,0,NULL,2,0,8,15,0,1);
INSERT INTO "grampsdb_person" VALUES(7,'YPNT6DU0BWARYZ2ZZM','I0006','2012-05-27 14:42:40.290687','2007-12-20 19:35:26',NULL,0,NULL,2,1,76,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(8,'5XLT6DXJ1J9NNI3QNT','I0028','2012-05-27 14:42:40.559004','2007-12-20 19:35:26',NULL,0,NULL,3,0,27,4,0,1);
INSERT INTO "grampsdb_person" VALUES(9,'XWNT6DP0HAPXFDCGY8','I0021','2012-05-27 14:42:40.819306','2007-12-20 19:35:26',NULL,0,NULL,2,0,33,25,0,1);
INSERT INTO "grampsdb_person" VALUES(10,'VHNT6DQCEELKZP0M2W','I0000','2012-05-27 14:42:41.092359','2007-12-20 19:35:26',NULL,0,NULL,3,0,74,86,0,1);
INSERT INTO "grampsdb_person" VALUES(11,'VNMT6DM95BAHK1X04I','I0031','2012-05-27 14:42:41.364222','2007-12-20 19:35:26',NULL,0,NULL,3,0,45,32,0,1);
INSERT INTO "grampsdb_person" VALUES(12,'YMMT6DJYFFJ38JZTNN','I0014','2012-05-27 14:42:41.634427','2007-12-20 19:35:26',NULL,0,NULL,3,1,22,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(13,'ZUMT6D4W8L3JZLJ5I1','I0013','2012-05-27 14:42:41.895232','2007-12-20 19:35:26',NULL,0,NULL,3,1,83,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(14,'RRNT6D5K0MU6QUAMAY','I0025','2012-05-27 14:42:42.145510','2007-12-20 19:35:26',NULL,0,NULL,3,1,20,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(15,'SKNT6D7FA4WHUUE7Z6','I0002','2012-05-27 14:42:42.395102','2007-12-20 19:35:26',NULL,0,NULL,3,1,42,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(16,'SVNT6DMAE9YEH6MICF','I0032','2012-05-27 14:42:42.661154','2007-12-20 19:35:26',NULL,0,NULL,3,1,9,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(17,'CLMT6DTNTB1PFIXZPC','I0015','2012-05-27 14:42:42.908030','2007-12-20 19:35:26',NULL,0,NULL,2,0,47,53,0,1);
INSERT INTO "grampsdb_person" VALUES(18,'0ONT6DJS5KD5W6EA1P','I0004','2012-05-27 14:42:43.161179','2007-12-20 19:35:26',NULL,0,NULL,2,1,58,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(19,'3XMT6DJVLX4BSJ8T9B','I0038','2012-05-27 14:42:43.407803','2007-12-20 19:35:26',NULL,0,NULL,3,0,30,46,0,1);
INSERT INTO "grampsdb_person" VALUES(20,'RDMT6D6113RO3X299I','I0019','2012-05-27 14:42:43.638928','2007-12-20 19:35:26',NULL,0,NULL,2,1,12,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(21,'PSNT6D0DDHJOBCFJWX','I0037','2012-05-27 14:42:43.883401','2007-12-20 19:35:26',NULL,0,NULL,2,1,38,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(22,'2GMT6DXW6RJVMKLQEH','I0018','2012-05-27 14:42:44.128484','2007-12-20 19:35:26',NULL,0,NULL,2,1,1,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(23,'BSMT6D9XTIXAG0TCNL','I0011','2012-05-27 14:42:44.383246','2007-12-20 19:35:26',NULL,0,NULL,3,1,37,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(24,'EMNT6DXUP8PCCU5MQG','I0005','2012-05-27 14:42:44.638862','2007-12-20 19:35:26',NULL,0,NULL,2,1,24,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(25,'PGNT6DESJOESEQNP22','I0001','2012-05-27 14:42:44.894705','2007-12-20 19:35:26',NULL,0,NULL,2,1,44,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(26,'NQMT6DX5NIOGMEGJA3','I0023','2012-05-27 14:42:45.152311','2007-12-20 19:35:26',NULL,0,NULL,3,0,49,71,0,1);
INSERT INTO "grampsdb_person" VALUES(27,'K3NT6DMBYAXNTXOO3F','I0020','2012-05-27 14:42:45.408803','2007-12-20 19:35:26',NULL,0,NULL,2,0,43,39,0,1);
INSERT INTO "grampsdb_person" VALUES(28,'DHMT6D0PQJCVXWD1FT','I0008','2012-05-27 14:42:45.674639','2007-12-20 19:35:26',NULL,0,NULL,2,0,18,10,0,1);
INSERT INTO "grampsdb_person" VALUES(29,'SYMT6DIHTYHLWHEE2K','I0026','2012-05-27 14:42:45.952372','2007-12-20 19:35:26',NULL,0,NULL,3,0,78,3,0,1);
INSERT INTO "grampsdb_person" VALUES(30,'J0NT6D9BY50LEA4VGY','I0024','2012-05-27 14:42:46.230816','2007-12-20 19:35:26',NULL,0,NULL,2,0,69,2,0,1);
INSERT INTO "grampsdb_person" VALUES(31,'9YNT6DXDSDPO56MX19','I0022','2012-05-27 14:42:46.518847','2007-12-20 19:35:26',NULL,0,NULL,2,0,60,68,0,1);
INSERT INTO "grampsdb_person" VALUES(32,'SQNT6DPEBXJPNWNCPX','I0033','2012-05-27 14:42:46.783285','2007-12-20 19:35:26',NULL,0,NULL,2,1,82,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(33,'60OT6D7XUEURYJRN78','I0040','2012-05-27 14:42:47.116687','2007-12-20 19:35:26',NULL,0,NULL,3,1,73,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(34,'YONT6DJYH1B5NKQTR7','I0007','2012-05-27 14:42:47.383148','2007-12-20 19:35:26',NULL,0,NULL,3,1,19,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(35,'NDNT6D8O7D3QRKP07N','I0017','2012-05-27 14:42:47.652352','2007-12-20 19:35:26',NULL,0,NULL,3,0,59,35,0,1);
INSERT INTO "grampsdb_person" VALUES(36,'W6NT6DAWXC9FUOHYI2','I0009','2012-05-27 14:42:47.956549','2007-12-20 19:35:26',NULL,0,NULL,2,1,41,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(37,'48MT6DRK875RYW6APJ','I0039','2012-05-27 14:42:48.296749','2007-12-20 19:35:26',NULL,0,NULL,2,0,28,89,0,1);
INSERT INTO "grampsdb_person" VALUES(38,'UANT6D04R90NFDKTBP','I0035','2012-05-27 14:42:48.641802','2007-12-20 19:35:26',NULL,0,NULL,2,1,7,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(39,'VVMT6D4M4VVILJ8Q1S','I0012','2012-05-27 14:42:49.019995','2007-12-20 19:35:26',NULL,0,NULL,2,0,23,84,0,1);
INSERT INTO "grampsdb_person" VALUES(40,'ZBMT6DX6U16KP4ESHL','I0016','2012-05-27 14:42:49.352411','2007-12-20 19:35:26',NULL,0,NULL,3,0,16,5,0,1);
INSERT INTO "grampsdb_person" VALUES(41,'ETMT6DLEIYYGW8SHM5','I0010','2012-05-27 14:42:49.814525','2007-12-20 19:35:26',NULL,0,NULL,2,0,48,6,0,1);
INSERT INTO "grampsdb_person" VALUES(42,'Y5NT6DLKFG3SBM9QQ4','I0034','2012-05-27 14:42:50.072420','2007-12-20 19:35:26',NULL,0,NULL,3,1,50,NULL,0,-1);
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
INSERT INTO "grampsdb_family" VALUES(1,'KKMT6D5KWF1VP03K4B','F0003','2012-05-27 14:42:36.495583','2007-12-20 19:35:26',NULL,0,NULL,30,10,5);
INSERT INTO "grampsdb_family" VALUES(2,'GYMT6D8WYROEUHX0IN','F0002','2012-05-27 14:42:36.544641','2007-12-20 19:35:26',NULL,0,NULL,31,19,5);
INSERT INTO "grampsdb_family" VALUES(3,'CGNT6DV02D0CQTGBAO','F0013','2012-05-27 14:42:36.676499','2007-12-20 19:35:26',NULL,0,NULL,21,4,5);
INSERT INTO "grampsdb_family" VALUES(4,'XRMT6DSAZG2Y37ETQ5','F0005','2012-05-27 14:42:36.949658','2007-12-20 19:35:26',NULL,0,NULL,39,26,5);
INSERT INTO "grampsdb_family" VALUES(5,'FZLT6D0QU0MC200P1O','F0011','2012-05-27 14:42:37.002760','2007-12-20 19:35:26',NULL,0,NULL,6,8,5);
INSERT INTO "grampsdb_family" VALUES(6,'S7MT6D1JSGX9PZO27F','F0008','2012-05-27 14:42:37.178769','2007-12-20 19:35:26',NULL,0,NULL,32,1,5);
INSERT INTO "grampsdb_family" VALUES(7,'NBMT6D6WBZODJRXOG','F0000','2012-05-27 14:42:37.196104','2007-12-20 19:35:26',NULL,0,NULL,37,3,5);
INSERT INTO "grampsdb_family" VALUES(8,'1HMT6DNWTSPXIL2FDM','F0012','2012-05-27 14:42:37.223797','2007-12-20 19:35:26',NULL,0,NULL,22,42,5);
INSERT INTO "grampsdb_family" VALUES(9,'GBMT6DJUGJ9453RW5I','F0001','2012-05-27 14:42:37.249032','2007-12-20 19:35:26',NULL,0,NULL,2,14,5);
INSERT INTO "grampsdb_family" VALUES(10,'RFMT6D6XB73EFWFHAA','F0010','2012-05-27 14:42:37.610071','2007-12-20 19:35:26',NULL,0,NULL,20,16,5);
INSERT INTO "grampsdb_family" VALUES(11,'MMMT6D6NGNO5YERSLM','F0007','2012-05-27 14:42:37.958179','2007-12-20 19:35:26',NULL,0,NULL,17,13,5);
INSERT INTO "grampsdb_family" VALUES(12,'GDMT6D6CWMU9NW5BON','F0014','2012-05-27 14:42:37.980631','2007-12-20 19:35:26',NULL,0,NULL,41,40,5);
INSERT INTO "grampsdb_family" VALUES(13,'UGMT6DU82BP5D3IPO3','F0006','2012-05-27 14:42:38.109518','2007-12-20 19:35:26',NULL,0,NULL,28,11,5);
INSERT INTO "grampsdb_family" VALUES(14,'80NT6DS6LKILTLEZIG','F0004','2012-05-27 14:42:38.274539','2007-12-20 19:35:26',NULL,0,NULL,7,29,5);
INSERT INTO "grampsdb_family" VALUES(15,'MUMT6DOHKMWL7LLQVA','F0009','2012-05-27 14:42:38.323102','2007-12-20 19:35:26',NULL,0,NULL,41,35,5);
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
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,1,'c2b9c122036e680b782fdd2683','C0002','2012-05-27 14:42:36.703194','1969-12-31 19:00:00',NULL,0,NULL,2,'',1);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,2,'c2b9c121d692cbaec9885fc51e5','C0001','2012-05-27 14:42:37.953942','1969-12-31 19:00:00',NULL,0,NULL,2,'',3);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,3,'c2b9c121bdb969190c2e1bb86a','C0000','2012-05-27 14:42:37.987473','1969-12-31 19:00:00',NULL,0,NULL,2,'',4);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',1721426,0,4,'c2b9cd5f3f3674551f1c2ccef4f','S0004','2012-05-27 15:04:00.292998','2012-05-27 15:03:59.797457','admin',0,'KFMnYzJiOWNkNWYzZjM2NzQ1NTFmMWMyY2NlZjRmJwpwMQpWUzAwMDQKcDIKKEkwCkkwCkkwCihJ
MApJMApJMApJMDAKdFYKSTE3MjE0MjYKSTAKdFYKTlMnYzJiOWNkNWYzZWQxZWQyOTM4YmZkZTli
N2JlJwpwMwoobChsKGRJMTMzODE0NTQzOQpJMDAKdHA0Ci4=
',NULL,'',5);
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
INSERT INTO "grampsdb_source" VALUES(1,'4TNT6DX8JM3BW08CUR','S0001','2012-05-27 14:42:36.238431','2007-12-20 19:35:26',NULL,0,NULL,'Birth Certificate','','','');
INSERT INTO "grampsdb_source" VALUES(2,'ADOT6D7LW5QJGMWY1V','S0002','2012-05-27 14:42:36.244635','2007-12-20 19:35:26',NULL,0,NULL,'Birth Records','','','');
INSERT INTO "grampsdb_source" VALUES(3,'H9OT6DH812QJAQS5A8','S0000','2012-05-27 14:42:36.251198','2007-12-20 19:35:26',NULL,0,NULL,'Marriage Certificae','','','');
INSERT INTO "grampsdb_source" VALUES(4,'VTNT6DYLDJMSJSCJMU','S0003','2012-05-27 14:42:36.439671','2007-12-20 19:35:26',NULL,0,NULL,'Birth, Death and Marriage Records','','','');
INSERT INTO "grampsdb_source" VALUES(5,'c2b9cd5f3ed1ed2938bfde9b7be','S0004','2012-05-27 15:04:00.041255','2012-05-27 15:03:59.438303','admin',0,'KFMnYzJiOWNkNWYzZWQxZWQyOTM4YmZkZTliN2JlJwpwMQpWUzAwMDQKcDIKVgpWClYKKGwobFYK
STEzMzgxNDU0MzkKKGQobEkwMAp0cDMKLg==
','','','','');
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
INSERT INTO "grampsdb_event" VALUES(0,0,0,30,1,1932,0,0,0,0,0,'',2426737,0,1,'a701e8fdd0f520c6d87','E0016','2012-05-27 14:42:36.487770','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of John Hjalmar Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,1,0,23,7,1930,0,0,0,0,0,'',2426181,0,2,'a701e8fe0715514c15e','E0030','2012-05-27 14:42:36.491335','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Gustaf Smith, Sr.',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,7,1966,0,0,0,0,0,'',2439325,0,3,'a701e8fe19a55908f51','E0035','2012-05-27 14:42:36.527969','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Kirsti Marie Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,2,1927,0,0,0,0,0,'',2424914,0,4,'a701e8fe28077648d39','E0038','2012-05-27 14:42:36.561065','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Anna Streiffert',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,5,1985,0,0,0,0,0,'',2446215,0,5,'a701e8fdc444ecbfa3c','E0013','2012-05-27 14:42:36.564565','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Jennifer Anderson',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1977,0,0,0,0,0,'',2443173,0,6,'a701e8fd9e57b3c48fb','E0004','2012-05-27 14:42:36.629511','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Hans Peter Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,16,9,1991,0,0,0,0,0,'',2448516,0,7,'a701e8fe5fb6b2cd015','E0051','2012-05-27 14:42:36.633025','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Lars Peter Smith',16);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,10,1858,0,0,0,0,0,'',2399959,0,8,'a701e8fe3552335c8c6','E0041','2012-05-27 14:42:36.672234','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Magnes Smith',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,7,1966,0,0,0,0,0,'',2439309,0,9,'a701e8fe4de2d524fb5','E0048','2012-05-27 14:42:36.697488','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Darcy Horne',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1975,0,0,0,0,0,'',2442590,0,10,'a701e8feb5c3bd26ecb','E0071','2012-05-27 14:42:36.707747','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Hjalmar Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,8,1958,0,0,0,0,0,'',2436426,0,11,'a701e8ff15c2045e75d','E0088','2012-05-27 14:42:36.711293','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Lloyd Smith and Janis Elaine Green',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,8,1963,0,0,0,0,0,'',2438270,0,12,'a701e8fdd82588a2110','E0017','2012-05-27 14:42:36.725406','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Eric Lloyd Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,7,1986,0,0,0,0,0,'',2446624,0,13,'a701e8fed39673c4638','E0077','2012-05-27 14:42:36.757736','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Eric Lloyd Smith and Darcy Horne',4);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1920,0,0,0,0,0,'',2422325,0,14,'a701e8ff11525d5aab8','E0087','2012-05-27 14:42:36.258503','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Gus Smith and Evelyn Michaels',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,2,1910,0,0,0,0,0,'',2418723,0,15,'a701e8fe37009b79506','E0042','2012-05-27 14:42:36.799043','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Magnes Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,11,1907,0,0,0,0,0,'',2417885,0,16,'a701e8fdc2a0f6a07ba','E0012','2012-05-27 14:42:36.802528','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Jennifer Anderson',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,10,1927,0,0,0,0,0,'',2425185,0,17,'a701e8ff0b46ceabfab','E0086','2012-05-27 14:42:36.861930','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Hjalmar Smith and Marjorie Ohman',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,4,1895,0,0,0,0,0,'',2413291,0,18,'a701e8feb3b0c8340f5','E0070','2012-05-27 14:42:36.865466','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Hjalmar Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,2,0,0,0,1823,0,0,0,0,0,'',2386897,0,19,'a701e8feadf736d65f9','E0069','2012-05-27 14:42:36.869034','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Ingar Smith',18);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1775,0,0,0,0,0,'',2369366,0,20,'a701e8fe11f0a554b76','E0033','2012-05-27 14:42:36.872541','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Marta Ericsdotter',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,12,1862,0,0,0,0,0,'',2401482,0,21,'a701e8fe0a80b22fd7b','E0032','2012-05-27 14:42:36.941963','2007-12-20 19:35:26',NULL,0,NULL,14,'Christening of Gustaf Smith, Sr.',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,11,1934,0,0,0,0,0,'',2427746,0,22,'a701e8fdb5c42897136','E0009','2012-05-27 14:42:36.945458','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Marjorie Lee Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,8,1889,0,0,0,0,0,'',2411246,0,23,'a701e8fdaa256b7d7a0','E0006','2012-05-27 14:42:36.988070','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Herman Julius Nielsen',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1996,0,0,0,0,0,'',2450261,0,24,'a701e8fe9f8177b3a8a','E0066','2012-05-27 14:42:36.991585','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Mason Michael Smith',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,9,1894,0,0,0,0,0,'',2413097,0,25,'a701e8fdee42a4ca4fb','E0023','2012-05-27 14:42:36.995080','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Hjalmar Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1816,0,0,0,0,0,'',2384340,0,26,'a701e8fec630d7443be','E0075','2012-05-27 14:42:36.998562','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Martin Smith and Elna Jefferson',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,9,1860,0,0,0,0,0,'',2400677,0,27,'a701e8fe2650e4c4754','E0037','2012-05-27 14:42:37.009791','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Anna Streiffert',23);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1794,0,0,0,1796,0,'',2376306,0,28,'a701e8fe866359dc7b5','E0061','2012-05-27 14:42:37.035669','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Martin Smith',5);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,9,1800,0,0,0,0,0,'',2378753,0,29,'a701e8fe6620b7e07d4','E0052','2012-05-27 14:42:37.039227','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Elna Jefferson',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,11,1832,0,0,0,0,0,'',2390517,0,30,'a701e8fe7e04c6a8cd6','E0059','2012-05-27 14:42:37.042759','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Kerstina Hansdotter',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,3,6,1895,0,0,0,0,0,'',2413348,0,31,'a701e8feb7b20ccf010','E0072','2012-05-27 14:42:37.069434','2007-12-20 19:35:26',NULL,0,NULL,7,'Baptism of Hjalmar Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,6,1980,0,0,0,0,0,'',2444413,0,32,'a701e8fe47a0ef83449','E0047','2012-05-27 14:42:37.072965','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Marjorie Ohman',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,1,1893,0,0,0,0,0,'',2412495,0,33,'a701e8fdecb3abcf86d','E0022','2012-05-27 14:42:37.098808','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Hjalmar Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,7,1996,0,0,0,0,0,'',2450275,0,34,'a701e8fea181d0b4ecf','E0067','2012-05-27 14:42:37.102312','2007-12-20 19:35:26',NULL,0,NULL,14,'Christening of Mason Michael Smith',11);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1990,0,0,0,0,0,'',2448069,0,35,'a701e8fdcbb150d8c89','E0015','2012-05-27 14:42:36.307460','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Lillie Harriet Jones',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,12,1935,0,0,0,0,0,'',2428139,0,36,'a701e8fe9ab02623db3','E0065','2012-05-27 14:42:36.308902','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Janis Elaine Green',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1821,0,0,0,0,0,'',2386195,0,37,'a701e8fda49467030a4','E0005','2012-05-27 14:42:37.162190','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Hanna Smith',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,5,1961,0,0,0,0,0,'',2437444,0,38,'a701e8fe703747db89d','E0055','2012-05-27 14:42:37.165699','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Edwin Michael Smith',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,1,1959,0,0,0,0,0,'',2436597,0,39,'a701e8fde75723d0c85','E0021','2012-05-27 14:42:37.173004','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Carl Emil Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,30,11,1912,0,0,0,0,0,'',2419737,0,40,'a701e8ff0514bd46d08','E0085','2012-05-27 14:42:37.216054','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Herman Julius Nielsen and Astrid Shermanna Augusta Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,9,1860,0,0,0,0,0,'',2400681,0,41,'a701e8fec095079e6be','E0074','2012-05-27 14:42:37.219589','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Emil Smith',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,4,1998,0,0,0,0,0,'',2450916,0,42,'a701e8fdde30786b48b','E0018','2012-05-27 14:42:37.236950','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Amber Marie Smith',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,12,1899,0,0,0,0,0,'',2415009,0,43,'a701e8fde5d0cc6484e','E0020','2012-05-27 14:42:37.240545','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Carl Emil Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,11,8,1966,0,0,0,0,0,'',2439349,0,44,'a701e8fd963245ebfef','E0002','2012-05-27 14:42:37.244050','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Keith Lloyd Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,3,6,1903,0,0,0,0,0,'',2416269,0,45,'a701e8fe457737ab114','E0046','2012-05-27 14:42:37.260921','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Marjorie Ohman',6);
INSERT INTO "grampsdb_event" VALUES(0,1,0,0,0,1908,0,0,0,0,0,'',2417942,0,46,'a701e8fe80366eb06dd','E0060','2012-05-27 14:42:37.265329','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Kerstina Hansdotter',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,11,9,1897,0,0,0,0,0,'',2414179,0,47,'a701e8fdbb916ee241b','E0010','2012-05-27 14:42:37.269587','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Gus Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,17,4,1904,0,0,0,0,0,'',2416588,0,48,'a701e8fd9cb7f8d7ec4','E0003','2012-05-27 14:42:37.273091','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Hans Peter Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,1,1889,0,0,0,0,0,'',2411034,0,49,'a701e8fdfd5706d009f','E0027','2012-05-27 14:42:37.335066','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Astrid Shermanna Augusta Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1933,0,0,0,0,0,'',2427399,0,50,'a701e8fe59c7230b3bd','E0050','2012-05-27 14:42:37.398751','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Alice Paula Perkins',20);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1770,0,0,0,0,0,'',2367540,0,51,'a701e8fe2072c1fa532','E0036','2012-05-27 14:42:37.486404','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Ingeman Smith',17);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1910,0,0,0,0,0,'',2418673,0,52,'a701e8ff00713e0c66e','E0084','2012-05-27 14:42:36.350233','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Edwin Willard and Kirsti Marie Smith',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,10,1963,0,0,0,0,0,'',2438324,0,53,'a701e8fdbd42af855c2','E0011','2012-05-27 14:42:37.605691','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Gus Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1979,0,0,0,1984,0,'',2443875,0,54,'a701e8fe75b474f1853','E0057','2012-05-27 14:42:37.652439','2007-12-20 19:35:26',NULL,0,NULL,18,'Education of Edwin Michael Smith',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,16,9,1800,0,0,0,0,0,'',2378755,0,55,'a701e8fe69766792b12','E0054','2012-05-27 14:42:37.707315','2007-12-20 19:35:26',NULL,0,NULL,14,'Christening of Elna Jefferson',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,56,'a701e8fe7334aab749d','E0056','2012-05-27 14:42:36.366990','2007-12-20 19:35:26',NULL,0,NULL,29,'Software Engineer',NULL);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1856,0,0,0,0,0,'',2398950,0,57,'a701e8fef323be305a4','E0082','2012-05-27 14:42:36.370968','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Martin Smith and Kerstina Hansdotter',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1826,0,0,0,0,0,'',2388021,0,58,'a701e8fe8ea06c7fba4','E0063','2012-05-27 14:42:37.804749','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Ingeman Smith',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,5,1910,0,0,0,0,0,'',2418794,0,59,'a701e8fdc9c76ede240','E0014','2012-05-27 14:42:37.808272','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Lillie Harriet Jones',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,19,11,1830,0,0,0,0,0,'',2389776,0,60,'a701e8fdf39649908a4','E0024','2012-05-27 14:42:37.908064','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Martin Smith',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,5,1995,0,0,0,0,0,'',2449865,0,61,'a701e8fee674aa12936','E0080','2012-05-27 14:42:37.911586','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Edwin Michael Smith and Janice Ann Adams',14);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,8,1965,0,0,0,0,0,'',2438999,0,62,'a701e8fe3d35113a9a7','E0043','2012-05-27 14:42:37.915100','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Janice Ann Adams',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,4,1998,0,0,0,0,0,'',2450930,0,63,'a701e8fddfe33c41840','E0019','2012-05-27 14:42:37.918607','2007-12-20 19:35:26',NULL,0,NULL,14,'Christening of Amber Marie Smith',11);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,5,1908,0,0,0,0,0,'',2418083,0,64,'a701e8fe08b4c512dbd','E0031','2012-05-27 14:42:37.922102','2007-12-20 19:35:26',NULL,0,NULL,47,'',15);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,11,1885,0,0,0,0,0,'',2409873,0,65,'a701e8fef934fe17a49','E0083','2012-05-27 14:42:37.965905','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Gustaf Smith, Sr. and Anna Hansdotter',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,10,1994,0,0,0,0,0,'',2449631,0,66,'a701e8fee9139a03b7f','E0081','2012-05-27 14:42:37.969429','2007-12-20 19:35:26',NULL,0,NULL,42,'Engagement of Edwin Michael Smith and Janice Ann Adams',3);
INSERT INTO "grampsdb_event" VALUES(0,2,0,0,0,1966,0,0,0,0,0,'',2439127,0,67,'a701e8fe2e27662085f','E0039','2012-05-27 14:42:37.972941','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Craig Peter Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1899,0,0,0,1905,0,'',2414656,0,68,'a701e8fdf5224fbdc9e','E0025','2012-05-27 14:42:37.976444','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Martin Smith',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,11,1862,0,0,0,0,0,'',2401473,0,69,'a701e8fe0507ac04137','E0029','2012-05-27 14:42:37.983930','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Gustaf Smith, Sr.',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,8,1884,0,0,0,0,0,'',2409413,0,70,'a701e8fed9d18d7302f','E0078','2012-05-27 14:42:38.023923','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Magnes Smith and Anna Streiffert',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,12,1963,0,0,0,0,0,'',2438385,0,71,'a701e8fdfed16648dc3','E0028','2012-05-27 14:42:38.027427','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Astrid Shermanna Augusta Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,6,1954,0,0,0,0,0,'',2434898,0,72,'a701e8fedf83b69acf8','E0079','2012-05-27 14:42:38.030908','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of John Hjalmar Smith and Alice Paula Perkins',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,2,1960,0,0,0,0,0,'',2436970,0,73,'a701e8fe94819a227eb','E0064','2012-05-27 14:42:38.036629','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Marjorie Alice Smith',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,10,1864,0,0,0,0,0,'',2402147,0,74,'a701e8fd8ea27f99704','E0000','2012-05-27 14:42:38.040113','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Anna Hansdotter',9);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1790,0,0,0,0,0,'',2374845,0,75,'a701e8fecd804e4c544','E0076','2012-05-27 14:42:38.067163','2007-12-20 19:35:26',NULL,0,NULL,37,'Marriage of Ingeman Smith and Marta Ericsdotter',17);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1886,0,0,0,0,0,'',2409908,0,76,'a701e8fea803e09a00a','E0068','2012-05-27 14:42:36.424243','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Edwin Willard',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,77,'a701e8fe67a3b9763f9','E0053','2012-05-27 14:42:38.123541','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Elna Jefferson',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,15,12,1886,0,0,0,0,0,'',2410256,0,78,'a701e8fe1812300afa7','E0034','2012-05-27 14:42:38.127061','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Kirsti Marie Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1984,0,0,0,0,0,'',2445701,0,79,'a701e8fe777404ac230','E0058','2012-05-27 14:42:36.429879','2007-12-20 19:35:26',NULL,0,NULL,17,'B.S.E.E.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,11,1912,0,0,0,0,0,'',2419721,0,80,'a701e8feb9f64bfceb3','E0073','2012-05-27 14:42:38.153763','2007-12-20 19:35:26',NULL,0,NULL,47,'',15);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1988,0,0,0,0,0,'',2447162,0,81,'a701e8fe40453c7a8c6','E0045','2012-05-27 14:42:36.434196','2007-12-20 19:35:26',NULL,0,NULL,17,'Business Management',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,3,1935,0,0,0,0,0,'',2427875,0,82,'a701e8fe53a76e15c39','E0049','2012-05-27 14:42:38.264518','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Lloyd Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1897,0,0,0,0,0,'',2413926,0,83,'a701e8fdb0a2faa54b5','E0008','2012-05-27 14:42:36.443577','2007-12-20 19:35:26',NULL,0,NULL,4,'Birth of Evelyn Michaels',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1945,0,0,0,0,0,'',2431457,0,84,'a701e8fdaba50dfafa1','E0007','2012-05-27 14:42:36.445020','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Herman Julius Nielsen',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,85,'a701e8fe3ee581802d8','E0044','2012-05-27 14:42:36.448230','2007-12-20 19:35:26',NULL,0,NULL,29,'Retail Manager',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,9,1945,0,0,0,0,0,'',2431728,0,86,'a701e8fd90672bb4ece','E0001','2012-05-27 14:42:38.307977','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Anna Hansdotter',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,87,'a701e8fe2fb2e845e69','E0040','2012-05-27 14:42:36.451122','2007-12-20 19:35:26',NULL,0,NULL,13,'Census of Craig Peter Smith',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,11,1830,0,0,0,0,0,'',2389780,0,88,'a701e8fdf6d6b51e7ad','E0026','2012-05-27 14:42:38.315383','2007-12-20 19:35:26',NULL,0,NULL,7,'Baptism of Martin Smith',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,89,'a701e8fe8843924e179','E0062','2012-05-27 14:42:38.318894','2007-12-20 19:35:26',NULL,0,NULL,5,'Death of Martin Smith',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,2,1943,0,0,0,0,0,'Feb 2, 1943',2430758,0,90,'c2b9cd27a775d502a63c36304da','E0089','2012-05-27 15:03:37.096851','2012-05-27 15:03:36.669980','admin',0,'KFMnYzJiOWNkMjdhNzc1ZDUwMmE2M2MzNjMwNGRhJwpwMQpWRTAwODkKcDIKKEkwClZDdXN0b20K
cDMKdChJMApJMApJMAooSTIKSTIKSTE5NDMKSTAwCnRWRmViIDIsIDE5NDMKcDQKSTI0MzA3NTgK
STAKdFYKVlBVTlQ2RDFYSFMwREpXOVFQNgpwNQoobChsKGwobEkxMzM4MTQ1NDE2CkkwMAp0cDYK
Lg==
',2,'',1);
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
INSERT INTO "grampsdb_repository" VALUES(1,'a701ead12841521cd4d','R0003','2012-05-27 14:42:36.225095','2007-12-20 19:35:26',NULL,0,NULL,10,'Aunt Martha''s Attic');
INSERT INTO "grampsdb_repository" VALUES(2,'a701e99f93e5434f6f3','R0002','2012-05-27 14:42:36.306125','2007-12-20 19:35:26',NULL,0,NULL,3,'New York Public Library');
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
INSERT INTO "grampsdb_place" VALUES(1,'PUNT6D1XHS0DJW9QP6','P0024','2012-05-27 14:42:36.223464','2007-12-20 19:35:26',NULL,0,NULL,'UC Berkeley','','');
INSERT INTO "grampsdb_place" VALUES(2,'ELNT6DS8GN8WI7Z4SO','P0008','2012-05-27 14:42:36.225659','2007-12-20 19:35:26',NULL,0,NULL,'Hayward, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(3,'67MT6DB6KWOVMBAXSY','P0002','2012-05-27 14:42:36.226141','2007-12-20 19:35:26',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(4,'QBOT6DN7UCCTZQ055','P0029','2012-05-27 14:42:36.244056','2007-12-20 19:35:26',NULL,0,NULL,'Woodland, Yolo Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(5,'R8MT6DRIZVNRYDK0VN','P0027','2012-05-27 14:42:36.247770','2007-12-20 19:35:26',NULL,0,NULL,'Tommarp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(6,'RPMT6DTQR8J7LK98HJ','P0019','2012-05-27 14:42:36.255885','2007-12-20 19:35:26',NULL,0,NULL,'Denver, Denver Co., CO','','');
INSERT INTO "grampsdb_place" VALUES(7,'HFNT6D12ZC0KOWY69T','P0016','2012-05-27 14:42:36.263454','2007-12-20 19:35:26',NULL,0,NULL,'Fremont, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(8,'LTNT6DKZ5CR8PZSVUS','P0022','2012-05-27 14:42:36.272297','2007-12-20 19:35:26',NULL,0,NULL,'San Jose, Santa Clara Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(9,'HINT6DP8JGGL0KKB8J','P0000','2012-05-27 14:42:36.294229','2007-12-20 19:35:26',NULL,0,NULL,'Loderup, Malmous Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(10,'QJMT6DGII29FWCPX2E','P0028','2012-05-27 14:42:36.327335','2007-12-20 19:35:26',NULL,0,NULL,'Ronne Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(11,'XLNT6DUONITFPPEGVH','P0009','2012-05-27 14:42:36.329037','2007-12-20 19:35:26',NULL,0,NULL,'Community Presbyterian Church, Danville, CA','','');
INSERT INTO "grampsdb_place" VALUES(12,'7JMT6DN2LOF54KXHTU','P0010','2012-05-27 14:42:36.329514','2007-12-20 19:35:26',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(13,'AANT6D026O5SHNUCDH','P0015','2012-05-27 14:42:36.329992','2007-12-20 19:35:26',NULL,0,NULL,'Simrishamn, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(14,'BAOT6D1WY6J4O4ARRN','P0030','2012-05-27 14:42:36.334129','2007-12-20 19:35:26',NULL,0,NULL,'San Ramon, Conta Costa Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(15,'AKMT6DMEYZDTG9J6DS','P0013','2012-05-27 14:42:36.353358','2007-12-20 19:35:26',NULL,0,NULL,'Copenhagen, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(16,'FBNT6DL92NDY0Z5SGP','P0021','2012-05-27 14:42:36.362921','2007-12-20 19:35:26',NULL,0,NULL,'Santa Rosa, Sonoma Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(17,'A9MT6DHVWGWRP59DEV','P0011','2012-05-27 14:42:36.371561','2007-12-20 19:35:26',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(18,'XSMT6DNISHYRCR1E78','P0004','2012-05-27 14:42:36.392342','2007-12-20 19:35:26',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(19,'GWNT6D12ZV06PK969X','P0020','2012-05-27 14:42:36.392830','2007-12-20 19:35:26',NULL,0,NULL,'Sacramento, Sacramento Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(20,'S1NT6DPOBYC1JGMR1P','P0001','2012-05-27 14:42:36.413601','2007-12-20 19:35:26',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(21,'61NT6D3G1JMOTO6Z7Y','P0012','2012-05-27 14:42:36.419341','2007-12-20 19:35:26',NULL,0,NULL,'Grostorp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(22,'4ZLT6DVCWT9LTZRDCS','P0003','2012-05-27 14:42:36.420113','2007-12-20 19:35:26',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(23,'DYLT6DF4DX2MNZICJ8','P0014','2012-05-27 14:42:36.442143','2007-12-20 19:35:26',NULL,0,NULL,'Hoya/Jona/Hoia, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(24,'IEOT6DOW3RE8AQ94HH','P0025','2012-05-27 14:42:36.445617','2007-12-20 19:35:26',NULL,0,NULL,'Bí','','');
INSERT INTO "grampsdb_place" VALUES(25,'PXMT6DBL0WSBL76WD7','P0026','2012-05-27 14:42:36.451714','2007-12-20 19:35:26',NULL,0,NULL,'Smestorp, Kristianstad Lan, Sweden','','');
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
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,1,'HHNT6D73QPKC0KWK2Y','O0000','2012-05-27 14:42:36.236391','2007-12-20 19:35:26',NULL,0,NULL,'O0.jpg','image/jpeg','Keith Lloyd Smith');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',1721426,0,2,'CVNT6DHG5ICZ1UGUO9','O0003','2012-05-27 15:10:00.820991','2012-05-27 15:10:00.335411','admin',0,'KFMnQ1ZOVDZESEc1SUNaMVVHVU85JwpWTzAwMDMKcDEKVk8zLmpwZwpwMgpWClZFZHdpbiBNaWNo
YWVsIFNtaXRoCnAzCihsKGwobEkxMzM4MTQ1ODAwCihJMApJMApJMAooSTAKSTAKSTAKSTAwCnRW
CkkxNzIxNDI2CkkwCnQodEkwMAp0cDQKLg==
','O3.jpg','','Edwin Michael Smith');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,3,'W2NT6D87SPI9V7G27P','O0001','2012-05-27 14:42:36.286620','2007-12-20 19:35:26',NULL,0,NULL,'O1.jpg','image/jpeg','Arriving 1910');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',1721426,0,4,'43NT6DHH0TBN0PKVC','O0002','2012-05-27 15:09:52.181148','2012-05-27 15:09:51.783879','admin',0,'KFMnNDNOVDZESEgwVEJOMFBLVkMnClZPMDAwMgpwMQpWTzIuanBnCnAyClYKVkVtaWwgJiBHdXN0
YWYgU21pdGgKcDMKKGwobChsSTEzMzgxNDU3OTEKKEkwCkkwCkkwCihJMApJMApJMApJMDAKdFYK
STE3MjE0MjYKSTAKdCh0STAwCnRwNAou
','O2.jpg','','Emil & Gustaf Smith');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,5,'MNNT6D27G3L8SGVQJV','O0005','2012-05-27 14:42:36.437540','2007-12-20 19:35:26',NULL,0,NULL,'O5.jpg','image/jpeg','Edwin & Janice Smith');
INSERT INTO "grampsdb_media" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,6,'Y0OT6DM7FW06A1SLMS','O0004','2012-05-27 14:42:36.441560','2007-12-20 19:35:26',NULL,0,NULL,'O4.jpg','image/jpeg','Marjorie Alice Smith');
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
INSERT INTO "grampsdb_note" VALUES(1,'aef3078a45757c79c22','N0002','2012-05-27 14:42:36.247170','2007-12-20 19:35:26',NULL,0,NULL,10,'BIOGRAPHY
Martin was listed as being a Husman, (owning a house as opposed to a farm) in the house records of Gladsax.',0);
INSERT INTO "grampsdb_note" VALUES(2,'aef3078a8ed472e0f9c','N0003','2012-05-27 14:42:36.296680','2007-12-20 19:35:26',NULL,0,NULL,10,'BIOGRAPHY

Hjalmar sailed from Copenhagen, Denmark on the OSCAR II, 14 November 1912 arriving in New York 27 November 1912. He was seventeen years old. On the ship passenger list his trade was listed as a Blacksmith.  He came to Reno, Nevada and lived with his sister Marie for a time before settling in Sparks. He worked for Southern Pacific Railroad as a car inspector for a time, then went to work for Standard Oil
Company. He enlisted in the army at Sparks 7 December 1917 and served as a Corporal in the Medical Corp until his discharge 12 August 1919 at the Presidio in San Francisco, California. Both he and Marjorie are buried in the Masonic Memorial Gardens Mausoleum in Reno, he the 30th June 1975, and she the 25th of June 1980.',0);
INSERT INTO "grampsdb_note" VALUES(3,'aef3078acbb1df0182a','N0006','2012-05-27 14:42:36.302019','2007-12-20 19:35:26',NULL,0,NULL,22,'Some note on the repo',0);
INSERT INTO "grampsdb_note" VALUES(4,'aef3078ab5c19ace6e2','N0005','2012-05-27 14:42:36.357054','2007-12-20 19:35:26',NULL,0,NULL,19,'The repository reference from the source is important',0);
INSERT INTO "grampsdb_note" VALUES(5,'aef30789d3d2090abe2','N0000','2012-05-27 14:42:36.374167','2007-12-20 19:35:26',NULL,0,NULL,17,'Witness name: John Doe
Witness comment: This is a simple test.',0);
INSERT INTO "grampsdb_note" VALUES(6,'aef30789ea73e9b5b10','N0001','2012-05-27 14:42:36.390628','2007-12-20 19:35:26',NULL,0,NULL,17,'Witness name: No Name',0);
INSERT INTO "grampsdb_note" VALUES(7,'aef3078ab1e37d60186','N0004','2012-05-27 14:42:36.395449','2007-12-20 19:35:26',NULL,0,NULL,19,'But Aunt Martha still keeps the original!',0);
INSERT INTO "grampsdb_note" VALUES(8,'c2b9cdac7ba3fc7313e58501961','N0007','2012-05-27 15:04:31.481473','2012-05-27 15:04:31.074326','admin',0,'KFMnYzJiOWNkYWM3YmEzZmM3MzEzZTU4NTAxOTYxJwpwMQpWTjAwMDcKcDIKKGxwMwpWVGhpcyBp
cyBhIG5vdGUKcDQKYShscDUKYUkwMAooSTIwClZOYW1lIE5vdGUKcDYKdEkxMzM4MTQ1NDcxCih0
STAwCnRwNwou
',11,'This is a note',0);
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
INSERT INTO "grampsdb_surname" VALUES(1,1,'Green','',1,'',1,1);
INSERT INTO "grampsdb_surname" VALUES(2,1,'Smith','',1,'',2,1);
INSERT INTO "grampsdb_surname" VALUES(3,1,'Jefferson','',1,'',3,1);
INSERT INTO "grampsdb_surname" VALUES(4,1,'Adams','',1,'',4,1);
INSERT INTO "grampsdb_surname" VALUES(5,1,'Smith','',1,'',5,1);
INSERT INTO "grampsdb_surname" VALUES(6,1,'Smith','',1,'',6,1);
INSERT INTO "grampsdb_surname" VALUES(7,1,'Willard','',1,'',7,1);
INSERT INTO "grampsdb_surname" VALUES(8,1,'Streiffert','',1,'',8,1);
INSERT INTO "grampsdb_surname" VALUES(9,1,'Smith','',1,'',9,1);
INSERT INTO "grampsdb_surname" VALUES(10,1,'Hansdotter','',1,'',10,1);
INSERT INTO "grampsdb_surname" VALUES(11,1,'Ohman','',1,'',11,1);
INSERT INTO "grampsdb_surname" VALUES(12,1,'Smith','',1,'',12,1);
INSERT INTO "grampsdb_surname" VALUES(13,1,'Michaels','',1,'',13,1);
INSERT INTO "grampsdb_surname" VALUES(14,1,'Ericsdotter','',1,'',14,1);
INSERT INTO "grampsdb_surname" VALUES(15,1,'Smith','',1,'',15,1);
INSERT INTO "grampsdb_surname" VALUES(16,1,'Horne','',1,'',16,1);
INSERT INTO "grampsdb_surname" VALUES(17,1,'Smith','',1,'',17,1);
INSERT INTO "grampsdb_surname" VALUES(18,1,'Smith','',1,'',18,1);
INSERT INTO "grampsdb_surname" VALUES(19,1,'Hansdotter','',1,'',19,1);
INSERT INTO "grampsdb_surname" VALUES(20,1,'Smith','',1,'',20,1);
INSERT INTO "grampsdb_surname" VALUES(21,1,'Smith','',1,'',21,1);
INSERT INTO "grampsdb_surname" VALUES(22,1,'Smith','',1,'',22,1);
INSERT INTO "grampsdb_surname" VALUES(23,1,'Smith','',1,'',23,1);
INSERT INTO "grampsdb_surname" VALUES(24,1,'Smith','',1,'',24,1);
INSERT INTO "grampsdb_surname" VALUES(25,1,'Smith','',1,'',25,1);
INSERT INTO "grampsdb_surname" VALUES(26,1,'Smith','',1,'',26,1);
INSERT INTO "grampsdb_surname" VALUES(27,1,'Smith','',1,'',27,1);
INSERT INTO "grampsdb_surname" VALUES(28,1,'Smith','',1,'',28,1);
INSERT INTO "grampsdb_surname" VALUES(29,1,'Smith','',1,'',29,1);
INSERT INTO "grampsdb_surname" VALUES(30,1,'Smith','',1,'',30,1);
INSERT INTO "grampsdb_surname" VALUES(31,1,'Smith','',1,'',31,1);
INSERT INTO "grampsdb_surname" VALUES(32,1,'Smith','',1,'',32,1);
INSERT INTO "grampsdb_surname" VALUES(33,1,'Smith','',1,'',33,1);
INSERT INTO "grampsdb_surname" VALUES(34,1,'Smith','',1,'',34,1);
INSERT INTO "grampsdb_surname" VALUES(35,1,'Jones','',1,'',35,1);
INSERT INTO "grampsdb_surname" VALUES(36,1,'Smith','',1,'',36,1);
INSERT INTO "grampsdb_surname" VALUES(37,1,'Smith','',1,'',37,1);
INSERT INTO "grampsdb_surname" VALUES(38,1,'Smith','',1,'',38,1);
INSERT INTO "grampsdb_surname" VALUES(39,1,'Nielsen','',1,'',39,1);
INSERT INTO "grampsdb_surname" VALUES(40,1,'Anderson','',1,'',40,1);
INSERT INTO "grampsdb_surname" VALUES(41,1,'Smith','',1,'',41,1);
INSERT INTO "grampsdb_surname" VALUES(42,1,'Perkins','',1,'',42,1);
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
INSERT INTO "grampsdb_name" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.461333',NULL,NULL,1,4,1,'Janis Elaine','','','','','','',1,1,1);
INSERT INTO "grampsdb_name" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.569672',NULL,NULL,1,4,1,'Ingeman','','','','','','',1,1,2);
INSERT INTO "grampsdb_name" VALUES(3,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.592005',NULL,NULL,1,4,1,'Elna','','','','','','',1,1,3);
INSERT INTO "grampsdb_name" VALUES(4,0,0,0,0,0,0,0,NULL,NULL,NULL,NULL,'',0,0,0,'2012-05-27 15:06:03.003953','2012-05-27 15:06:03.001952','admin',1,4,1,'Janice Ann','','','','','','',1,1,4);
INSERT INTO "grampsdb_name" VALUES(5,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.730551',NULL,NULL,1,4,1,'Craig Peter','','','','','','',1,1,5);
INSERT INTO "grampsdb_name" VALUES(6,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.763576',NULL,NULL,1,4,1,'Magnes','','','','','','',1,1,6);
INSERT INTO "grampsdb_name" VALUES(7,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.807581',NULL,NULL,1,4,1,'Edwin','','','','','','',1,1,7);
INSERT INTO "grampsdb_name" VALUES(8,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.830724',NULL,NULL,1,4,1,'Anna','','','','','','',1,1,8);
INSERT INTO "grampsdb_name" VALUES(9,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.877684',NULL,NULL,1,4,1,'Hjalmar','','','','','','',1,1,9);
INSERT INTO "grampsdb_name" VALUES(10,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.911099',NULL,NULL,1,4,1,'Anna','','','','','','',1,1,10);
INSERT INTO "grampsdb_name" VALUES(11,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.957369',NULL,NULL,1,4,1,'Marjorie','','','','','','',1,1,11);
INSERT INTO "grampsdb_name" VALUES(12,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.014859',NULL,NULL,1,4,1,'Marjorie Lee','','','','','','',1,1,12);
INSERT INTO "grampsdb_name" VALUES(13,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.048605',NULL,NULL,1,4,1,'Evelyn','','','','','','',1,1,13);
INSERT INTO "grampsdb_name" VALUES(14,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.078022',NULL,NULL,1,4,1,'Marta','','','','','','',1,1,14);
INSERT INTO "grampsdb_name" VALUES(15,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.113013',NULL,NULL,1,4,1,'Amber Marie','','','','','','',1,1,15);
INSERT INTO "grampsdb_name" VALUES(16,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.141301',NULL,NULL,1,4,1,'Darcy','','','','','','',1,1,16);
INSERT INTO "grampsdb_name" VALUES(17,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.278193',NULL,NULL,1,4,1,'Gus','','','','','','',1,1,17);
INSERT INTO "grampsdb_name" VALUES(18,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.314415',NULL,NULL,1,4,1,'Ingeman','','','','','','',1,1,18);
INSERT INTO "grampsdb_name" VALUES(19,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.340280',NULL,NULL,1,4,1,'Kerstina','','','','','','',1,1,19);
INSERT INTO "grampsdb_name" VALUES(20,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.372459',NULL,NULL,1,4,1,'Eric Lloyd','','','','','','',1,1,20);
INSERT INTO "grampsdb_name" VALUES(21,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.403861',NULL,NULL,1,4,1,'Edwin Michael','','','','','','',1,1,21);
INSERT INTO "grampsdb_name" VALUES(22,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.461534',NULL,NULL,1,4,1,'John Hjalmar','','','','','','',1,1,22);
INSERT INTO "grampsdb_name" VALUES(23,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.492352',NULL,NULL,1,4,1,'Hanna','','','','','','',1,1,23);
INSERT INTO "grampsdb_name" VALUES(24,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.514705',NULL,NULL,1,4,1,'Mason Michael','','','','','','',1,1,24);
INSERT INTO "grampsdb_name" VALUES(25,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.546177',NULL,NULL,1,4,1,'Keith Lloyd','','','','','','',1,1,25);
INSERT INTO "grampsdb_name" VALUES(26,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.571025',NULL,NULL,1,4,1,'Astrid Shermanna Augusta','','','','','','',1,1,26);
INSERT INTO "grampsdb_name" VALUES(27,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.621360',NULL,NULL,1,4,1,'Carl Emil','','','','','','',1,1,27);
INSERT INTO "grampsdb_name" VALUES(28,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.658284',NULL,NULL,1,4,1,'Hjalmar','','','','','','',1,1,28);
INSERT INTO "grampsdb_name" VALUES(29,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.715523',NULL,NULL,1,4,1,'Kirsti Marie','','','','','','',1,1,29);
INSERT INTO "grampsdb_name" VALUES(30,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.751959',NULL,NULL,1,4,1,'Gustaf','Sr.','','','','','',1,1,30);
INSERT INTO "grampsdb_name" VALUES(31,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.813354',NULL,NULL,1,4,1,'Martin','','','','','','',1,1,31);
INSERT INTO "grampsdb_name" VALUES(32,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.858545',NULL,NULL,1,4,1,'Lloyd','','','','','','',1,1,32);
INSERT INTO "grampsdb_name" VALUES(33,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.884872',NULL,NULL,1,4,1,'Marjorie Alice','','','','','','',1,1,33);
INSERT INTO "grampsdb_name" VALUES(34,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.927185',NULL,NULL,1,4,1,'Ingar','','','','','','',1,1,34);
INSERT INTO "grampsdb_name" VALUES(35,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.992651',NULL,NULL,1,4,1,'Lillie Harriet','','','','','','',1,1,35);
INSERT INTO "grampsdb_name" VALUES(36,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:38.046111',NULL,NULL,1,4,1,'Emil','','','','','','',1,1,36);
INSERT INTO "grampsdb_name" VALUES(37,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:38.073832',NULL,NULL,1,4,1,'Martin','','','','','','',1,1,37);
INSERT INTO "grampsdb_name" VALUES(38,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:38.132153',NULL,NULL,1,4,1,'Lars Peter','','','','','','',1,1,38);
INSERT INTO "grampsdb_name" VALUES(39,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:38.159006',NULL,NULL,1,4,1,'Herman Julius','','','','','','',1,1,39);
INSERT INTO "grampsdb_name" VALUES(40,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:38.192162',NULL,NULL,1,4,1,'Jennifer','','','','','','',1,1,40);
INSERT INTO "grampsdb_name" VALUES(41,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:38.224684',NULL,NULL,1,4,1,'Hans Peter','','','','','','',1,1,41);
INSERT INTO "grampsdb_name" VALUES(42,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:38.286430',NULL,NULL,1,4,1,'Alice Paula','','','','','','',1,1,42);
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
    "markup_type_id" integer NOT NULL REFERENCES "grampsdb_markuptype" ("id"),
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
INSERT INTO "grampsdb_address" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:36.538817',NULL,NULL,1,NULL,1);
INSERT INTO "grampsdb_address" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-27 14:42:37.106098',NULL,NULL,1,NULL,2);
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
INSERT INTO "grampsdb_location" VALUES(1,'123 Main St','','Someville','','ST','USA','','',NULL,1,NULL,1);
INSERT INTO "grampsdb_location" VALUES(2,'5th Ave at 42 street','','New York','','New York','USA','11111','',NULL,1,NULL,2);
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
INSERT INTO "grampsdb_url" VALUES(1,0,'http://library.gramps-project.org','',4,1,NULL,NULL,1);
CREATE TABLE "grampsdb_attribute" (
    "id" integer NOT NULL PRIMARY KEY,
    "private" bool NOT NULL,
    "attribute_type_id" integer NOT NULL REFERENCES "grampsdb_attributetype" ("id"),
    "value" text,
    "object_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL
);
INSERT INTO "grampsdb_attribute" VALUES(1,0,10,'Bad breath',36,39);
INSERT INTO "grampsdb_attribute" VALUES(2,0,12,'23',52,45);
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
INSERT INTO "grampsdb_noteref" VALUES(1,37,1,1,'2012-05-27 14:42:36.534469',NULL,NULL,0,3);
INSERT INTO "grampsdb_noteref" VALUES(2,35,3,1,'2012-05-27 14:42:36.716215',NULL,NULL,0,7);
INSERT INTO "grampsdb_noteref" VALUES(3,32,28,1,'2012-05-27 14:42:37.680935',NULL,NULL,0,2);
INSERT INTO "grampsdb_noteref" VALUES(4,36,56,1,'2012-05-27 14:42:37.711283',NULL,NULL,0,6);
INSERT INTO "grampsdb_noteref" VALUES(5,32,31,1,'2012-05-27 14:42:37.833524',NULL,NULL,0,1);
INSERT INTO "grampsdb_noteref" VALUES(6,35,4,1,'2012-05-27 14:42:38.268395',NULL,NULL,0,4);
INSERT INTO "grampsdb_noteref" VALUES(7,36,87,1,'2012-05-27 14:42:38.311964',NULL,NULL,0,5);
INSERT INTO "grampsdb_noteref" VALUES(8,32,43,1,'2012-05-27 15:04:31.746988',NULL,NULL,0,8);
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
INSERT INTO "grampsdb_eventref" VALUES(1,32,1,1,'2012-05-27 14:42:36.468138',NULL,NULL,0,36,3);
INSERT INTO "grampsdb_eventref" VALUES(2,33,1,1,'2012-05-27 14:42:36.525278',NULL,NULL,0,65,10);
INSERT INTO "grampsdb_eventref" VALUES(3,33,2,1,'2012-05-27 14:42:36.558374',NULL,NULL,0,57,10);
INSERT INTO "grampsdb_eventref" VALUES(4,32,2,1,'2012-05-27 14:42:36.573765',NULL,NULL,0,51,3);
INSERT INTO "grampsdb_eventref" VALUES(5,32,3,1,'2012-05-27 14:42:36.596108',NULL,NULL,0,29,3);
INSERT INTO "grampsdb_eventref" VALUES(6,32,3,1,'2012-05-27 14:42:36.598910',NULL,NULL,0,77,3);
INSERT INTO "grampsdb_eventref" VALUES(7,32,3,1,'2012-05-27 14:42:36.601790',NULL,NULL,0,55,3);
INSERT INTO "grampsdb_eventref" VALUES(8,32,4,1,'2012-05-27 14:42:36.643256',NULL,NULL,0,62,3);
INSERT INTO "grampsdb_eventref" VALUES(9,32,4,1,'2012-05-27 14:42:36.646051',NULL,NULL,0,85,3);
INSERT INTO "grampsdb_eventref" VALUES(10,32,4,1,'2012-05-27 14:42:36.648844',NULL,NULL,0,81,3);
INSERT INTO "grampsdb_eventref" VALUES(11,33,3,1,'2012-05-27 14:42:36.691064',NULL,NULL,0,61,10);
INSERT INTO "grampsdb_eventref" VALUES(12,33,3,1,'2012-05-27 14:42:36.693880',NULL,NULL,0,66,10);
INSERT INTO "grampsdb_eventref" VALUES(13,32,5,1,'2012-05-27 14:42:36.734671',NULL,NULL,0,67,3);
INSERT INTO "grampsdb_eventref" VALUES(14,32,5,1,'2012-05-27 14:42:36.737491',NULL,NULL,0,87,3);
INSERT INTO "grampsdb_eventref" VALUES(15,32,6,1,'2012-05-27 14:42:36.767687',NULL,NULL,0,8,3);
INSERT INTO "grampsdb_eventref" VALUES(16,32,6,1,'2012-05-27 14:42:36.770495',NULL,NULL,0,15,3);
INSERT INTO "grampsdb_eventref" VALUES(17,32,7,1,'2012-05-27 14:42:36.811688',NULL,NULL,0,76,3);
INSERT INTO "grampsdb_eventref" VALUES(18,32,8,1,'2012-05-27 14:42:36.834898',NULL,NULL,0,27,3);
INSERT INTO "grampsdb_eventref" VALUES(19,32,8,1,'2012-05-27 14:42:36.837737',NULL,NULL,0,4,3);
INSERT INTO "grampsdb_eventref" VALUES(20,32,9,1,'2012-05-27 14:42:36.881834',NULL,NULL,0,33,3);
INSERT INTO "grampsdb_eventref" VALUES(21,32,9,1,'2012-05-27 14:42:36.884655',NULL,NULL,0,25,3);
INSERT INTO "grampsdb_eventref" VALUES(22,32,10,1,'2012-05-27 14:42:36.915177',NULL,NULL,0,74,3);
INSERT INTO "grampsdb_eventref" VALUES(23,32,10,1,'2012-05-27 14:42:36.918003',NULL,NULL,0,86,3);
INSERT INTO "grampsdb_eventref" VALUES(24,33,4,1,'2012-05-27 14:42:36.953143',NULL,NULL,0,40,10);
INSERT INTO "grampsdb_eventref" VALUES(25,32,11,1,'2012-05-27 14:42:36.961447',NULL,NULL,0,45,3);
INSERT INTO "grampsdb_eventref" VALUES(26,32,11,1,'2012-05-27 14:42:36.964239',NULL,NULL,0,32,3);
INSERT INTO "grampsdb_eventref" VALUES(27,33,5,1,'2012-05-27 14:42:37.006231',NULL,NULL,0,70,10);
INSERT INTO "grampsdb_eventref" VALUES(28,32,12,1,'2012-05-27 14:42:37.018945',NULL,NULL,0,22,3);
INSERT INTO "grampsdb_eventref" VALUES(29,32,13,1,'2012-05-27 14:42:37.052796',NULL,NULL,0,83,3);
INSERT INTO "grampsdb_eventref" VALUES(30,32,14,1,'2012-05-27 14:42:37.082127',NULL,NULL,0,20,3);
INSERT INTO "grampsdb_eventref" VALUES(31,32,15,1,'2012-05-27 14:42:37.117150',NULL,NULL,0,42,3);
INSERT INTO "grampsdb_eventref" VALUES(32,32,15,1,'2012-05-27 14:42:37.119944',NULL,NULL,0,63,3);
INSERT INTO "grampsdb_eventref" VALUES(33,32,16,1,'2012-05-27 14:42:37.145409',NULL,NULL,0,9,3);
INSERT INTO "grampsdb_eventref" VALUES(34,33,6,1,'2012-05-27 14:42:37.192642',NULL,NULL,0,11,10);
INSERT INTO "grampsdb_eventref" VALUES(35,33,7,1,'2012-05-27 14:42:37.213329',NULL,NULL,0,26,10);
INSERT INTO "grampsdb_eventref" VALUES(36,33,8,1,'2012-05-27 14:42:37.234118',NULL,NULL,0,72,10);
INSERT INTO "grampsdb_eventref" VALUES(37,33,9,1,'2012-05-27 14:42:37.255964',NULL,NULL,0,75,10);
INSERT INTO "grampsdb_eventref" VALUES(38,32,17,1,'2012-05-27 14:42:37.282323',NULL,NULL,0,47,3);
INSERT INTO "grampsdb_eventref" VALUES(39,32,17,1,'2012-05-27 14:42:37.285127',NULL,NULL,0,53,3);
INSERT INTO "grampsdb_eventref" VALUES(40,32,18,1,'2012-05-27 14:42:37.318491',NULL,NULL,0,58,3);
INSERT INTO "grampsdb_eventref" VALUES(41,32,19,1,'2012-05-27 14:42:37.344377',NULL,NULL,0,30,3);
INSERT INTO "grampsdb_eventref" VALUES(42,32,19,1,'2012-05-27 14:42:37.347163',NULL,NULL,0,46,3);
INSERT INTO "grampsdb_eventref" VALUES(43,32,20,1,'2012-05-27 14:42:37.376570',NULL,NULL,0,12,3);
INSERT INTO "grampsdb_eventref" VALUES(44,32,21,1,'2012-05-27 14:42:37.411085',NULL,NULL,0,38,3);
INSERT INTO "grampsdb_eventref" VALUES(45,32,21,1,'2012-05-27 14:42:37.413907',NULL,NULL,0,56,3);
INSERT INTO "grampsdb_eventref" VALUES(46,32,21,1,'2012-05-27 14:42:37.417868',NULL,NULL,0,54,3);
INSERT INTO "grampsdb_eventref" VALUES(47,32,21,1,'2012-05-27 14:42:37.420684',NULL,NULL,0,79,3);
INSERT INTO "grampsdb_eventref" VALUES(48,32,22,1,'2012-05-27 14:42:37.465663',NULL,NULL,0,1,3);
INSERT INTO "grampsdb_eventref" VALUES(49,32,23,1,'2012-05-27 14:42:37.496567',NULL,NULL,0,37,3);
INSERT INTO "grampsdb_eventref" VALUES(50,32,24,1,'2012-05-27 14:42:37.518807',NULL,NULL,0,24,3);
INSERT INTO "grampsdb_eventref" VALUES(51,32,24,1,'2012-05-27 14:42:37.521622',NULL,NULL,0,34,3);
INSERT INTO "grampsdb_eventref" VALUES(52,32,25,1,'2012-05-27 14:42:37.550366',NULL,NULL,0,44,3);
INSERT INTO "grampsdb_eventref" VALUES(53,32,26,1,'2012-05-27 14:42:37.575141',NULL,NULL,0,49,3);
INSERT INTO "grampsdb_eventref" VALUES(54,32,26,1,'2012-05-27 14:42:37.577965',NULL,NULL,0,71,3);
INSERT INTO "grampsdb_eventref" VALUES(55,33,10,1,'2012-05-27 14:42:37.617102',NULL,NULL,0,13,10);
INSERT INTO "grampsdb_eventref" VALUES(56,32,27,1,'2012-05-27 14:42:37.625468',NULL,NULL,0,43,3);
INSERT INTO "grampsdb_eventref" VALUES(57,32,27,1,'2012-05-27 14:42:37.628252',NULL,NULL,0,39,3);
INSERT INTO "grampsdb_eventref" VALUES(58,32,28,1,'2012-05-27 14:42:37.662445',NULL,NULL,0,18,3);
INSERT INTO "grampsdb_eventref" VALUES(59,32,28,1,'2012-05-27 14:42:37.665249',NULL,NULL,0,10,3);
INSERT INTO "grampsdb_eventref" VALUES(60,32,28,1,'2012-05-27 14:42:37.668039',NULL,NULL,0,31,3);
INSERT INTO "grampsdb_eventref" VALUES(61,32,28,1,'2012-05-27 14:42:37.670834',NULL,NULL,0,80,3);
INSERT INTO "grampsdb_eventref" VALUES(62,32,29,1,'2012-05-27 14:42:37.719692',NULL,NULL,0,78,3);
INSERT INTO "grampsdb_eventref" VALUES(63,32,29,1,'2012-05-27 14:42:37.722515',NULL,NULL,0,3,3);
INSERT INTO "grampsdb_eventref" VALUES(64,32,30,1,'2012-05-27 14:42:37.756046',NULL,NULL,0,69,3);
INSERT INTO "grampsdb_eventref" VALUES(65,32,30,1,'2012-05-27 14:42:37.758875',NULL,NULL,0,2,3);
INSERT INTO "grampsdb_eventref" VALUES(66,32,30,1,'2012-05-27 14:42:37.761680',NULL,NULL,0,64,3);
INSERT INTO "grampsdb_eventref" VALUES(67,32,30,1,'2012-05-27 14:42:37.764473',NULL,NULL,0,21,3);
INSERT INTO "grampsdb_eventref" VALUES(68,32,31,1,'2012-05-27 14:42:37.817480',NULL,NULL,0,60,3);
INSERT INTO "grampsdb_eventref" VALUES(69,32,31,1,'2012-05-27 14:42:37.820283',NULL,NULL,0,68,3);
INSERT INTO "grampsdb_eventref" VALUES(70,32,31,1,'2012-05-27 14:42:37.823434',NULL,NULL,0,88,3);
INSERT INTO "grampsdb_eventref" VALUES(71,32,32,1,'2012-05-27 14:42:37.862692',NULL,NULL,0,82,3);
INSERT INTO "grampsdb_eventref" VALUES(72,32,33,1,'2012-05-27 14:42:37.889015',NULL,NULL,0,73,3);
INSERT INTO "grampsdb_eventref" VALUES(73,32,34,1,'2012-05-27 14:42:37.931291',NULL,NULL,0,19,3);
INSERT INTO "grampsdb_eventref" VALUES(74,32,34,1,'2012-05-27 14:42:37.934096',NULL,NULL,0,56,9);
INSERT INTO "grampsdb_eventref" VALUES(75,33,11,1,'2012-05-27 14:42:37.961684',NULL,NULL,0,14,10);
INSERT INTO "grampsdb_eventref" VALUES(76,32,35,1,'2012-05-27 14:42:37.996897',NULL,NULL,0,59,3);
INSERT INTO "grampsdb_eventref" VALUES(77,32,35,1,'2012-05-27 14:42:37.999712',NULL,NULL,0,35,3);
INSERT INTO "grampsdb_eventref" VALUES(78,32,36,1,'2012-05-27 14:42:38.050256',NULL,NULL,0,41,3);
INSERT INTO "grampsdb_eventref" VALUES(79,32,37,1,'2012-05-27 14:42:38.078018',NULL,NULL,0,28,3);
INSERT INTO "grampsdb_eventref" VALUES(80,32,37,1,'2012-05-27 14:42:38.080843',NULL,NULL,0,89,3);
INSERT INTO "grampsdb_eventref" VALUES(81,33,13,1,'2012-05-27 14:42:38.119951',NULL,NULL,0,17,10);
INSERT INTO "grampsdb_eventref" VALUES(82,32,38,1,'2012-05-27 14:42:38.136256',NULL,NULL,0,7,3);
INSERT INTO "grampsdb_eventref" VALUES(83,32,39,1,'2012-05-27 14:42:38.163098',NULL,NULL,0,23,3);
INSERT INTO "grampsdb_eventref" VALUES(84,32,39,1,'2012-05-27 14:42:38.165913',NULL,NULL,0,84,3);
INSERT INTO "grampsdb_eventref" VALUES(85,32,40,1,'2012-05-27 14:42:38.196347',NULL,NULL,0,16,3);
INSERT INTO "grampsdb_eventref" VALUES(86,32,40,1,'2012-05-27 14:42:38.199179',NULL,NULL,0,5,3);
INSERT INTO "grampsdb_eventref" VALUES(87,32,41,1,'2012-05-27 14:42:38.228792',NULL,NULL,0,48,3);
INSERT INTO "grampsdb_eventref" VALUES(88,32,41,1,'2012-05-27 14:42:38.231593',NULL,NULL,0,6,3);
INSERT INTO "grampsdb_eventref" VALUES(89,33,14,1,'2012-05-27 14:42:38.278032',NULL,NULL,0,52,10);
INSERT INTO "grampsdb_eventref" VALUES(90,32,42,1,'2012-05-27 14:42:38.290531',NULL,NULL,0,50,3);
INSERT INTO "grampsdb_eventref" VALUES(91,32,43,1,'2012-05-27 15:03:37.498099',NULL,NULL,0,90,3);
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
INSERT INTO "grampsdb_repositoryref" VALUES(1,35,3,1,'2012-05-27 14:42:36.719673',NULL,NULL,0,2,13,'what-321-ever');
INSERT INTO "grampsdb_repositoryref" VALUES(2,35,3,1,'2012-05-27 14:42:36.722524',NULL,NULL,0,1,10,'nothing-0');
INSERT INTO "grampsdb_repositoryref" VALUES(3,35,4,1,'2012-05-27 14:42:38.271136',NULL,NULL,0,2,8,'CA-123-LL-456_Num/ber');
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
INSERT INTO "grampsdb_citationref" VALUES(1,36,38,1,'2012-05-27 14:42:37.170198',NULL,NULL,0,3);
INSERT INTO "grampsdb_citationref" VALUES(2,42,21,1,'2012-05-27 14:42:37.408232',NULL,NULL,0,1);
INSERT INTO "grampsdb_citationref" VALUES(3,36,72,1,'2012-05-27 14:42:38.033971',NULL,NULL,0,2);
INSERT INTO "grampsdb_citationref" VALUES(4,32,43,1,'2012-05-27 15:04:00.548188',NULL,NULL,0,4);
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
INSERT INTO "grampsdb_childref" VALUES(1,33,1,1,'2012-05-27 14:42:36.501336',NULL,NULL,0,2,2,29);
INSERT INTO "grampsdb_childref" VALUES(2,33,1,1,'2012-05-27 14:42:36.504901',NULL,NULL,0,2,2,26);
INSERT INTO "grampsdb_childref" VALUES(3,33,1,1,'2012-05-27 14:42:36.508305',NULL,NULL,0,2,2,9);
INSERT INTO "grampsdb_childref" VALUES(4,33,1,1,'2012-05-27 14:42:36.511887',NULL,NULL,0,2,2,28);
INSERT INTO "grampsdb_childref" VALUES(5,33,1,1,'2012-05-27 14:42:36.515279',NULL,NULL,0,2,2,17);
INSERT INTO "grampsdb_childref" VALUES(6,33,1,1,'2012-05-27 14:42:36.518691',NULL,NULL,0,2,2,27);
INSERT INTO "grampsdb_childref" VALUES(7,33,1,1,'2012-05-27 14:42:36.522430',NULL,NULL,0,2,2,41);
INSERT INTO "grampsdb_childref" VALUES(8,33,2,1,'2012-05-27 14:42:36.548714',NULL,NULL,0,2,2,6);
INSERT INTO "grampsdb_childref" VALUES(9,33,2,1,'2012-05-27 14:42:36.552106',NULL,NULL,0,2,2,36);
INSERT INTO "grampsdb_childref" VALUES(10,33,2,1,'2012-05-27 14:42:36.555511',NULL,NULL,0,2,2,30);
INSERT INTO "grampsdb_childref" VALUES(11,33,3,1,'2012-05-27 14:42:36.680572',NULL,NULL,0,2,2,24);
INSERT INTO "grampsdb_childref" VALUES(12,33,3,1,'2012-05-27 14:42:36.684043',NULL,NULL,0,2,2,15);
INSERT INTO "grampsdb_childref" VALUES(13,33,6,1,'2012-05-27 14:42:37.182872',NULL,NULL,0,3,3,20);
INSERT INTO "grampsdb_childref" VALUES(14,33,6,1,'2012-05-27 14:42:37.186296',NULL,NULL,0,2,2,25);
INSERT INTO "grampsdb_childref" VALUES(15,33,6,1,'2012-05-27 14:42:37.189717',NULL,NULL,0,2,2,5);
INSERT INTO "grampsdb_childref" VALUES(16,33,7,1,'2012-05-27 14:42:37.200175',NULL,NULL,0,2,2,23);
INSERT INTO "grampsdb_childref" VALUES(17,33,7,1,'2012-05-27 14:42:37.203596',NULL,NULL,0,2,2,34);
INSERT INTO "grampsdb_childref" VALUES(18,33,7,1,'2012-05-27 14:42:37.207030',NULL,NULL,0,2,2,18);
INSERT INTO "grampsdb_childref" VALUES(19,33,7,1,'2012-05-27 14:42:37.210453',NULL,NULL,0,2,2,31);
INSERT INTO "grampsdb_childref" VALUES(20,33,8,1,'2012-05-27 14:42:37.227844',NULL,NULL,0,2,2,33);
INSERT INTO "grampsdb_childref" VALUES(21,33,8,1,'2012-05-27 14:42:37.231276',NULL,NULL,0,2,2,21);
INSERT INTO "grampsdb_childref" VALUES(22,33,9,1,'2012-05-27 14:42:37.253124',NULL,NULL,0,2,2,37);
INSERT INTO "grampsdb_childref" VALUES(23,33,10,1,'2012-05-27 14:42:37.614217',NULL,NULL,0,3,3,38);
INSERT INTO "grampsdb_childref" VALUES(24,33,13,1,'2012-05-27 14:42:38.113637',NULL,NULL,0,2,2,22);
INSERT INTO "grampsdb_childref" VALUES(25,33,13,1,'2012-05-27 14:42:38.117105',NULL,NULL,0,2,2,12);
INSERT INTO "grampsdb_childref" VALUES(26,33,15,1,'2012-05-27 14:42:38.327173',NULL,NULL,0,2,2,32);
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
INSERT INTO "grampsdb_mediaref" VALUES(1,33,3,1,'2012-05-27 14:42:36.687989',NULL,NULL,0,0,0,0,0,5);
INSERT INTO "grampsdb_mediaref" VALUES(2,32,21,1,'2012-05-27 14:42:37.434080',NULL,NULL,0,0,0,0,0,2);
INSERT INTO "grampsdb_mediaref" VALUES(3,32,24,1,'2012-05-27 14:42:37.527860',NULL,NULL,0,0,0,0,0,5);
INSERT INTO "grampsdb_mediaref" VALUES(4,32,25,1,'2012-05-27 14:42:37.556633',NULL,NULL,0,0,0,0,0,1);
INSERT INTO "grampsdb_mediaref" VALUES(5,32,30,1,'2012-05-27 14:42:37.774667',NULL,NULL,0,0,0,0,0,3);
INSERT INTO "grampsdb_mediaref" VALUES(6,32,30,1,'2012-05-27 14:42:37.777195',NULL,NULL,0,0,0,0,0,4);
INSERT INTO "grampsdb_mediaref" VALUES(7,32,33,1,'2012-05-27 14:42:37.895290',NULL,NULL,0,0,0,0,0,6);
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
INSERT INTO "grampsdb_report" VALUES(16,'R0016','GEDCOM Export','gedcom_export','export','off=ged');
INSERT INTO "grampsdb_report" VALUES(17,'R0017','Gramps XML Export','ex_gpkg','export','off=gramps');
INSERT INTO "grampsdb_report" VALUES(18,'R0018','GEDCOM Import','im_ged','import','iff=ged i=http://arborvita.free.fr/Kennedy/Kennedy.ged');
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
CREATE INDEX "grampsdb_person_families_21b911c5" ON "grampsdb_person_families" ("person_id");
CREATE INDEX "grampsdb_person_families_ccf20756" ON "grampsdb_person_families" ("family_id");
CREATE INDEX "grampsdb_person_tags_21b911c5" ON "grampsdb_person_tags" ("person_id");
CREATE INDEX "grampsdb_person_tags_3747b463" ON "grampsdb_person_tags" ("tag_id");
CREATE INDEX "grampsdb_person_parent_families_21b911c5" ON "grampsdb_person_parent_families" ("person_id");
CREATE INDEX "grampsdb_person_parent_families_ccf20756" ON "grampsdb_person_parent_families" ("family_id");
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
CREATE INDEX "grampsdb_markup_cf03b71c" ON "grampsdb_markup" ("markup_type_id");
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
