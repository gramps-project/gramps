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
INSERT INTO "auth_user" VALUES(1,'admin','','','doug.blank@gmail.com','sha1$e702c$76d3a7dfc417b4e80faa6a032a54220d270eeda5',1,1,1,'2012-05-19 07:46:29.382382','2012-05-19 07:40:35.640321');
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
INSERT INTO "django_session" VALUES('167d76a77237d0e4975e8a70d52498e9','MmU1MjliMDM2NzcyODdjNmJlOTgzMGFiYzc2MjFkMmViYWFiOTIzMjqAAn1xAShVEl9hdXRoX3Vz
ZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED
VQ1fYXV0aF91c2VyX2lkcQRLAXUu
','2012-06-02 07:46:29.649866');
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
INSERT INTO "grampsdb_notetype" VALUES(27,'GEDCOM import',0);
CREATE TABLE "grampsdb_markuptype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL,
    "val" integer NOT NULL
);
INSERT INTO "grampsdb_markuptype" VALUES(1,'',3);
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
INSERT INTO "grampsdb_config" VALUES(3,'db_created','database creation date/time','str','2012-05-19 07:39');
CREATE TABLE "grampsdb_tag" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "name" text NOT NULL,
    "color" varchar(13) NOT NULL,
    "priority" integer NOT NULL
);
CREATE TABLE "grampsdb_person_families" (
    "id" integer NOT NULL PRIMARY KEY,
    "person_id" integer NOT NULL,
    "family_id" integer NOT NULL,
    UNIQUE ("person_id", "family_id")
);
INSERT INTO "grampsdb_person_families" VALUES(1,3,13);
INSERT INTO "grampsdb_person_families" VALUES(2,9,5);
INSERT INTO "grampsdb_person_families" VALUES(3,10,1);
INSERT INTO "grampsdb_person_families" VALUES(4,11,5);
INSERT INTO "grampsdb_person_families" VALUES(5,14,9);
INSERT INTO "grampsdb_person_families" VALUES(6,15,13);
INSERT INTO "grampsdb_person_families" VALUES(7,18,15);
INSERT INTO "grampsdb_person_families" VALUES(8,19,9);
INSERT INTO "grampsdb_person_families" VALUES(9,21,1);
INSERT INTO "grampsdb_person_families" VALUES(10,33,15);
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
INSERT INTO "grampsdb_person_parent_families" VALUES(1,1,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(2,2,6);
INSERT INTO "grampsdb_person_parent_families" VALUES(3,3,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(4,5,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(5,7,2);
INSERT INTO "grampsdb_person_parent_families" VALUES(6,8,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(7,11,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(8,13,4);
INSERT INTO "grampsdb_person_parent_families" VALUES(9,16,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(10,19,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(11,20,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(12,21,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(13,22,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(14,23,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(15,24,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(16,25,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(17,26,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(18,28,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(19,29,2);
INSERT INTO "grampsdb_person_parent_families" VALUES(20,30,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(21,31,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(22,32,6);
INSERT INTO "grampsdb_person_parent_families" VALUES(23,33,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(24,36,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(25,39,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(26,41,6);
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
INSERT INTO "grampsdb_person" VALUES(1,'c29f1441e5d7d2d5ef07413260b','I0011','2012-05-19 07:51:26.992435','2007-12-21 01:35:26',NULL,0,NULL,3,1,52,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(2,'c29f1441fdc19bb38987f68463b','I0019','2012-05-19 07:51:27.355615','2007-12-21 01:35:26',NULL,0,NULL,2,1,38,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(3,'c29f1441115147b9a6ef4d8edc2','I0010','2012-05-19 07:51:27.723339','2007-12-21 01:35:26',NULL,0,NULL,2,0,60,21,0,1);
INSERT INTO "grampsdb_person" VALUES(4,'c29f144221ed389dabe7f8160a','I0031','2012-05-19 07:51:28.102944','2007-12-21 01:35:26',NULL,0,NULL,3,0,39,27,0,1);
INSERT INTO "grampsdb_person" VALUES(5,'c29f14424297c4603d00b9848c0','I0008','2012-05-19 07:51:28.402670','2007-12-21 01:35:26',NULL,0,NULL,2,0,59,62,0,1);
INSERT INTO "grampsdb_person" VALUES(6,'c29f1441fa05948c4458634e735','I0017','2012-05-19 07:51:28.764233','2007-12-21 01:35:26',NULL,0,NULL,3,0,55,86,0,1);
INSERT INTO "grampsdb_person" VALUES(7,'c29f1441f0e3354b9bca1878a09','I0014','2012-05-19 07:51:29.134405','2007-12-21 01:35:26',NULL,0,NULL,3,1,31,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(8,'c29f1442063140358f1bedad24','I0021','2012-05-19 07:51:29.407196','2007-12-21 01:35:26',NULL,0,NULL,2,0,75,42,0,1);
INSERT INTO "grampsdb_person" VALUES(9,'c29f1441eef4815735309b25326','I0013','2012-05-19 07:51:29.678798','2007-12-21 01:35:26',NULL,0,NULL,3,1,33,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(10,'c29f1441eb0deb8d781eb177a','I0012','2012-05-19 07:51:29.953158','2007-12-21 01:35:26',NULL,0,NULL,2,0,87,66,0,1);
INSERT INTO "grampsdb_person" VALUES(11,'c29f1441f367a545ea12a71e1f5','I0015','2012-05-19 07:51:30.236128','2007-12-21 01:35:26',NULL,0,NULL,2,0,36,44,0,1);
INSERT INTO "grampsdb_person" VALUES(12,'c29f144217514606fc39265864d','I0027','2012-05-19 07:51:30.507242','2007-12-21 01:35:26',NULL,0,NULL,2,1,57,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(13,'c29f14422923c3e4b5847998b74','I0035','2012-05-19 07:51:30.773322','2007-12-21 01:35:26',NULL,0,NULL,2,1,65,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(14,'c29f14423f856e814d19521658d','I0006','2012-05-19 07:51:31.040502','2007-12-21 01:35:26',NULL,0,NULL,2,1,91,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(15,'c29f1441f71556e705b5d8fc91e','I0016','2012-05-19 07:51:31.309719','2007-12-21 01:35:26',NULL,0,NULL,3,0,26,53,0,1);
INSERT INTO "grampsdb_person" VALUES(16,'c29f1442259117ccdae8078bc','I0033','2012-05-19 07:51:31.584996','2007-12-21 01:35:26',NULL,0,NULL,2,1,7,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(17,'c29f14422bd5d4a4b985e2b6619','I0036','2012-05-19 07:51:31.914447','2007-12-21 01:35:26',NULL,0,NULL,3,0,83,40,0,1);
INSERT INTO "grampsdb_person" VALUES(18,'c29f144218d59cf6405219a72ef','I0028','2012-05-19 07:51:32.257310','2007-12-21 01:35:26',NULL,0,NULL,3,0,48,89,0,1);
INSERT INTO "grampsdb_person" VALUES(19,'c29f144214a6f52821c12cafe97','I0026','2012-05-19 07:51:32.614684','2007-12-21 01:35:26',NULL,0,NULL,3,0,51,47,0,1);
INSERT INTO "grampsdb_person" VALUES(20,'c29f144200928f6f9f58cebd7dd','I0002','2012-05-19 07:51:33.051537','2007-12-21 01:35:26',NULL,0,NULL,3,1,45,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(21,'c29f14420c54a7217d0757e8d0c','I0023','2012-05-19 07:51:33.303471','2007-12-21 01:35:26',NULL,0,NULL,3,0,49,88,0,1);
INSERT INTO "grampsdb_person" VALUES(22,'c29f144239c55d012426131d82f','I0040','2012-05-19 07:51:33.567821','2007-12-21 01:35:26',NULL,0,NULL,3,1,16,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(23,'c29f144208e611b408f6a45e418','I0022','2012-05-19 07:51:33.825142','2007-12-21 01:35:26',NULL,0,NULL,2,0,15,76,0,1);
INSERT INTO "grampsdb_person" VALUES(24,'c29f14420f15777f1196d45d68b','I0024','2012-05-19 07:51:34.102644','2007-12-21 01:35:26',NULL,0,NULL,2,0,5,58,0,1);
INSERT INTO "grampsdb_person" VALUES(25,'c29f144240852e5bf8b3a190017','I0007','2012-05-19 07:51:34.400406','2007-12-21 01:35:26',NULL,0,NULL,3,1,61,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(26,'c29f144246d39a6b3af4d0f797f','I0009','2012-05-19 07:51:34.662622','2007-12-21 01:35:26',NULL,0,NULL,2,1,30,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(27,'c29f14423bc6041eb102338e2f8','I0041','2012-05-19 07:51:34.923234','2007-12-21 01:35:26',NULL,0,NULL,3,1,18,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(28,'c29f14423cc6feaf585f1e47d5d','I0005','2012-05-19 07:51:35.356625','2007-12-21 01:35:26',NULL,0,NULL,2,1,78,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(29,'c29f1441fbbe41026a71573856','I0018','2012-05-19 07:51:35.678813','2007-12-21 01:35:26',NULL,0,NULL,2,1,74,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(30,'c29f144237a77238c83b697451b','I0004','2012-05-19 07:51:35.966964','2007-12-21 01:35:26',NULL,0,NULL,2,1,67,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(31,'c29f1442350474511a4f1faa03d','I0039','2012-05-19 07:51:36.219752','2007-12-21 01:35:26',NULL,0,NULL,2,0,79,64,0,1);
INSERT INTO "grampsdb_person" VALUES(32,'c29f14410485e293f6f5c7792fe','I0001','2012-05-19 07:51:36.477786','2007-12-21 01:35:26',NULL,0,NULL,2,1,23,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(33,'c29f14421d5d771ed87de7d643','I0003','2012-05-19 07:51:36.725654','2007-12-21 01:35:26',NULL,0,NULL,2,0,28,2,0,1);
INSERT INTO "grampsdb_person" VALUES(34,'c29f144224117e408d0b35a118e','I0032','2012-05-19 07:51:36.973150','2007-12-21 01:35:26',NULL,0,NULL,3,1,34,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(35,'c29f1442201540035ac066a0f4f','I0030','2012-05-19 07:51:37.218059','2007-12-21 01:35:26',NULL,0,NULL,3,1,14,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(36,'c29f1442034735181412a6ec9ca','I0020','2012-05-19 07:51:37.458975','2007-12-21 01:35:26',NULL,0,NULL,2,0,84,90,0,1);
INSERT INTO "grampsdb_person" VALUES(37,'c29f1440f476dd1cc753e57ae4e','I0000','2012-05-19 07:51:37.703406','2007-12-21 01:35:26',NULL,0,NULL,3,0,80,35,0,1);
INSERT INTO "grampsdb_person" VALUES(38,'c29f144232e7bc46ac96d6739fb','I0038','2012-05-19 07:51:37.948534','2007-12-21 01:35:26',NULL,0,NULL,3,0,82,25,0,1);
INSERT INTO "grampsdb_person" VALUES(39,'c29f14422e9634b1d7423c8f5c2','I0037','2012-05-19 07:51:38.233698','2007-12-21 01:35:26',NULL,0,NULL,2,1,85,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(40,'c29f1442130262ca5ca512d2dd6','I0025','2012-05-19 07:51:38.478853','2007-12-21 01:35:26',NULL,0,NULL,3,1,12,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(41,'c29f14421b261c2f460502cd78f','I0029','2012-05-19 07:51:38.733718','2007-12-21 01:35:26',NULL,0,NULL,2,1,71,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(42,'c29f144227a7f81c1676480bc7c','I0034','2012-05-19 07:51:39.064778','2007-12-21 01:35:26',NULL,0,NULL,3,1,46,NULL,0,-1);
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
INSERT INTO "grampsdb_family" VALUES(1,'c29f1441ec43975b500f9c592fa','F0005','2012-05-19 07:49:50.516102','2007-12-21 01:35:26',NULL,0,NULL,10,21,5);
INSERT INTO "grampsdb_family" VALUES(2,'c29f1441f1d2346cc468f3dcb7','F0006','2012-05-19 07:49:51.014851','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(3,'c29f144213e4126ed5d805863bd','F0001','2012-05-19 07:49:51.539054','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(4,'c29f1441ffd24d240749ae733c7','F0010','2012-05-19 07:50:04.083922','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(5,'c29f1441ef755a1cf7844940ceb','F0007','2012-05-19 07:50:11.828789','2007-12-21 01:35:26',NULL,0,NULL,11,9,5);
INSERT INTO "grampsdb_family" VALUES(6,'c29f14410657b8efd3ce4f58254','F0008','2012-05-19 07:50:12.444265','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(7,'c29f144202111a00faee0ff583','F0013','2012-05-19 07:50:19.549179','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(8,'c29f1441fd1738c704ee3a839f2','F0012','2012-05-19 07:50:23.619081','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(9,'c29f144216a1df76acdbff9d063','F0004','2012-05-19 07:50:33.424521','2007-12-21 01:35:26',NULL,0,NULL,14,19,5);
INSERT INTO "grampsdb_family" VALUES(10,'c29f1440f9963215b35cda3c79','F0003','2012-05-19 07:50:34.804159','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(11,'c29f14420b966b32d52b5efb252','F0002','2012-05-19 07:50:41.466294','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(12,'c29f1441e3e4e7feee7c5da7025','F0009','2012-05-19 07:50:52.148643','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(13,'c29f1441e40183a287708cb3e8f','F0014','2012-05-19 07:51:05.470118','2007-12-21 01:35:26',NULL,0,NULL,3,15,1);
INSERT INTO "grampsdb_family" VALUES(14,'c29f1441e7b21f9f3392486f1eb','F0000','2012-05-19 07:51:15.108851','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(15,'c29f14421a745375629b52f7f02','F0011','2012-05-19 07:51:22.592948','2007-12-21 01:35:26',NULL,0,NULL,33,18,5);
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
    "confidence" integer NOT NULL,
    "page" varchar(50) NOT NULL,
    "source_id" integer
);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,1,'c29f14425301b7779d231923d80','C0002','2012-05-19 07:50:21.974576','1969-12-31 19:00:00',NULL,0,NULL,2,'',2);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,2,'c29f14422f6e3a4df3f3a1719f','C0000','2012-05-19 07:50:34.281472','1969-12-31 19:00:00',NULL,0,NULL,2,'',1);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,3,'c29f1442309204ae7b409462b2a','C0001','2012-05-19 07:50:38.384041','1969-12-31 19:00:00',NULL,0,NULL,2,'',4);
CREATE TABLE "grampsdb_source" (
    "id" integer NOT NULL PRIMARY KEY,
    "handle" varchar(19) NOT NULL UNIQUE,
    "gramps_id" varchar(25) NOT NULL,
    "last_saved" datetime NOT NULL,
    "last_changed" datetime,
    "last_changed_by" text,
    "private" bool NOT NULL,
    "cache" text,
    "title" varchar(50) NOT NULL,
    "author" varchar(50) NOT NULL,
    "pubinfo" varchar(50) NOT NULL,
    "abbrev" varchar(50) NOT NULL
);
INSERT INTO "grampsdb_source" VALUES(1,'c29f14422f572315982ba539bcf','S0001','2012-05-19 07:48:25.264534','1969-12-31 19:00:00',NULL,0,NULL,'@S1@','','','');
INSERT INTO "grampsdb_source" VALUES(2,'c29f144252f61f69676e6755e18','S0000','2012-05-19 07:48:41.841881','1969-12-31 19:00:00',NULL,0,NULL,'@S0@','','','');
INSERT INTO "grampsdb_source" VALUES(3,'c29f14426b42720ec016f07a016','S0002','2012-05-19 07:48:45.786185','2007-12-21 01:35:26',NULL,0,NULL,'Birth Records','','','');
INSERT INTO "grampsdb_source" VALUES(4,'c29f14423086d1ef960b5fa035e','S0003','2012-05-19 07:49:09.168711','1969-12-31 19:00:00',NULL,0,NULL,'@S3@','','','');
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
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1790,0,0,0,0,0,'ABT 1790',2374845,0,1,'c29f14424c963511fe3f360315b','E0078','2012-05-19 07:49:30.245628','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Ingeman Smith and Marta Ericsdotter',65);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,2,1910,0,0,0,0,0,'20 FEB 1910',2418723,0,2,'c29f14421e249931744bf3012c4','E0043','2012-05-19 07:49:30.596333','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Magnes Smith',19);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1816,0,0,0,0,0,'ABT 1816',2384340,0,3,'c29f144248f74e2178479fe8873','E0077','2012-05-19 07:49:30.968248','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Martin Smith and Elna Jefferson',29);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,11,1830,0,0,0,0,0,'23 NOV 1830',2389780,0,4,'c29f14420a6556264f5edff218d','E0027','2012-05-19 07:49:31.240948','1969-12-31 19:00:00',NULL,0,NULL,7,'Baptism of Martin Smith',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,11,1862,0,0,0,0,0,'28 NOV 1862',2401473,0,5,'c29f14420f450ff5d54c7570a74','E0030','2012-05-19 07:49:33.464216','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Gustaf Smith, Sr.',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,10,1994,0,0,0,0,0,'5 OCT 1994',2449631,0,6,'c29f14425571bdda44491bfbb4e','E0083','2012-05-19 07:49:33.717768','1969-12-31 19:00:00',NULL,0,NULL,42,'Engagement of Edwin Michael Smith and Janice Ann Adams',50);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,3,1935,0,0,0,0,0,'13 MAR 1935',2427875,0,7,'c29f144225b41a3aa5977a506c6','E0050','2012-05-19 07:49:33.986307','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Lloyd Smith',62);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,7,1986,0,0,0,0,0,'12 JUL 1986',2446624,0,8,'c29f14424e9291dc2544ca88522','E0079','2012-05-19 07:49:46.162808','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Eric Lloyd Smith and Darcy Horne',57);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1984,0,0,0,0,0,'1984',2445701,0,9,'c29f14423166e4a3025f45366d9','E0060','2012-05-19 07:48:25.772136','1969-12-31 19:00:00',NULL,0,NULL,17,'B.S.E.E.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,5,1908,0,0,0,0,0,'21 MAY 1908',2418083,0,10,'c29f1442108311071885561e6fc','E0032','2012-05-19 07:49:55.721496','1969-12-31 19:00:00',NULL,0,NULL,47,'',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,11,'c29f14422a031c7b27e85f1c764','E0053','2012-05-19 07:48:30.677419','1969-12-31 19:00:00',NULL,0,NULL,3,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1775,0,0,0,0,0,'ABT 1775',2369366,0,12,'c29f14421345cb61a0cd78a22','E0034','2012-05-19 07:49:58.094637','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Marta Ericsdotter',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,10,1927,0,0,0,0,0,'31 OCT 1927',2425185,0,13,'c29f144261e6daf895cce7acce6','E0088','2012-05-19 07:50:00.503740','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Hjalmar Smith and Marjorie Ohman',56);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,8,1965,0,0,0,0,0,'26 AUG 1965',2438999,0,14,'c29f14422042e49f7e27599c6e7','E0044','2012-05-19 07:50:00.843022','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Janice Ann Adams',71);
INSERT INTO "grampsdb_event" VALUES(0,0,0,19,11,1830,0,0,0,0,0,'19 NOV 1830',2389776,0,15,'c29f14420914c9db3461df57fb8','E0025','2012-05-19 07:50:01.257022','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Martin Smith',28);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,2,1960,0,0,0,0,0,'5 FEB 1960',2436970,0,16,'c29f144239f461733820e51d748','E0066','2012-05-19 07:50:01.584844','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Marjorie Alice Smith',74);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,6,1954,0,0,0,0,0,'4 JUN 1954',2434898,0,17,'c29f144251f1a8e704abe870d6e','E0081','2012-05-19 07:50:04.616670','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of John Hjalmar Smith and Alice Paula Perkins',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,12,1935,0,0,0,0,0,'2 DEC 1935',2428139,0,18,'c29f14423bf6bc7358c99069eb8','E0067','2012-05-19 07:48:35.713000','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Janis Elaine Green',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,11,1912,0,0,0,0,0,'14 NOV 1912',2419721,0,19,'c29f144244d68993373e2e0adbe','E0075','2012-05-19 07:50:06.793989','1969-12-31 19:00:00',NULL,0,NULL,47,'',47);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,8,1958,0,0,0,0,0,'10 AUG 1958',2436426,0,20,'c29f1442652762979f4a91df37c','E0090','2012-05-19 07:50:07.067884','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Lloyd Smith and Janis Elaine Green',41);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1977,0,0,0,0,0,'29 JAN 1977',2443173,0,21,'c29f144112d19c1ae9fa300f02','E0004','2012-05-19 07:50:07.349399','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Hans Peter Smith',31);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1856,0,0,0,0,0,'ABT 1856',2398950,0,22,'c29f14425881a79020294cf6bdc','E0084','2012-05-19 07:48:37.832076','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Martin Smith and Kerstina Hansdotter',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,11,8,1966,0,0,0,0,0,'11 AUG 1966',2439349,0,23,'c29f14410506b866171e5e8a28d','E0002','2012-05-19 07:50:07.725929','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Keith Lloyd Smith',43);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,24,'c29f144220f1ccfcdc580f050bc','E0045','2012-05-19 07:48:39.060025','1969-12-31 19:00:00',NULL,0,NULL,29,'Retail Manager',NULL);
INSERT INTO "grampsdb_event" VALUES(0,1,0,0,0,1908,0,0,0,0,0,'BEF 1908',2417942,0,25,'c29f144233b679aa7809effe784','E0062','2012-05-19 07:50:07.982910','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Kerstina Hansdotter',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,11,1907,0,0,0,0,0,'5 NOV 1907',2417885,0,26,'c29f1441f78433414b32a035a5a','E0012','2012-05-19 07:50:08.252232','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Jennifer Anderson',46);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,6,1980,0,0,0,0,0,'22 JUN 1980',2444413,0,27,'c29f144222c65cc9e6c077e40f1','E0048','2012-05-19 07:50:08.612057','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Marjorie Ohman',51);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,10,1858,0,0,0,0,0,'6 OCT 1858',2399959,0,28,'c29f14421d87d952082714a3c1f','E0042','2012-05-19 07:50:09.068853','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Magnes Smith',73);
INSERT INTO "grampsdb_event" VALUES(0,0,0,30,11,1912,0,0,0,0,0,'30 NOV 1912',2419737,0,29,'c29f144260820c4e9070e686b41','E0087','2012-05-19 07:50:09.395234','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Herman Julius Nielsen and Astrid Shermanna Augusta Smith',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,9,1860,0,0,0,0,0,'27 SEP 1860',2400681,0,30,'c29f144247028bd39d5e4347bf8','E0076','2012-05-19 07:50:11.322968','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Emil Smith',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,11,1934,0,0,0,0,0,'4 NOV 1934',2427746,0,31,'c29f1441f117a935867363ab17b','E0009','2012-05-19 07:50:11.573394','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Marjorie Lee Smith',75);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,8,1884,0,0,0,0,0,'24 AUG 1884',2409413,0,32,'c29f14425082f8d4914c95ebc5a','E0080','2012-05-19 07:50:13.162500','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Magnes Smith and Anna Streiffert',67);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1897,0,0,0,0,0,'ABT 1897',2413926,0,33,'c29f1441ef35958fdd081c9627c','E0008','2012-05-19 07:48:43.916017','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Evelyn Michaels',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,7,1966,0,0,0,0,0,'2 JUL 1966',2439309,0,34,'c29f144224419fbb66fb710f670','E0049','2012-05-19 07:50:18.606179','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Darcy Horne',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,9,1945,0,0,0,0,0,'29 SEP 1945',2431728,0,35,'c29f1440f77199aa46219d9058','E0001','2012-05-19 07:50:18.940260','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Anna Hansdotter',68);
INSERT INTO "grampsdb_event" VALUES(0,0,0,11,9,1897,0,0,0,0,0,'11 SEP 1897',2414179,0,36,'c29f1441f3a7d02030da9d65474','E0010','2012-05-19 07:50:19.262431','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Gus Smith',35);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,37,'c29f14421bf220ad690f5c1a2f2','E0041','2012-05-19 07:48:47.310452','1969-12-31 19:00:00',NULL,0,NULL,13,'Census of Craig Peter Smith',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,8,1963,0,0,0,0,0,'28 AUG 1963',2438270,0,38,'c29f1441fdf5eab349890423a09','E0017','2012-05-19 07:50:22.517715','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Eric Lloyd Smith',58);
INSERT INTO "grampsdb_event" VALUES(0,0,0,3,6,1903,0,0,0,0,0,'3 JUN 1903',2416269,0,39,'c29f1442221713e90c7f0b97302','E0047','2012-05-19 07:50:23.120398','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Marjorie Ohman',69);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,40,'c29f14422ca3be082ecbf59ec68','E0055','2012-05-19 07:50:23.365512','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Elna Jefferson',36);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1910,0,0,0,0,0,'ABT 1910',2418673,0,41,'c29f14425fa1dc783253ec3aac1','E0086','2012-05-19 07:48:49.870803','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Edwin Willard and Kirsti Marie Smith',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,9,1894,0,0,0,0,0,'25 SEP 1894',2413097,0,42,'c29f14420706f2b40b2e81ae3b3','E0024','2012-05-19 07:50:24.152144','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Hjalmar Smith',1);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1920,0,0,0,0,0,'ABT 1920',2422325,0,43,'c29f14426442de9350a78a856c3','E0089','2012-05-19 07:48:52.769844','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Gus Smith and Evelyn Michaels',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,10,1963,0,0,0,0,0,'21 OCT 1963',2438324,0,44,'c29f1441f476257490486633756','E0011','2012-05-19 07:50:27.320079','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Gus Smith',60);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,4,1998,0,0,0,0,0,'12 APR 1998',2450916,0,45,'c29f144200c1eaa713e40d81baf','E0019','2012-05-19 07:50:27.583429','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Amber Marie Smith',42);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1933,0,0,0,0,0,'22 NOV 1933',2427399,0,46,'c29f144227d7f836c0f9fe87ab8','E0051','2012-05-19 07:50:29.350294','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Alice Paula Perkins',55);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,7,1966,0,0,0,0,0,'18 JUL 1966',2439325,0,47,'c29f1442157425d9bdde9afc47c','E0036','2012-05-19 07:50:29.607222','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Kirsti Marie Smith',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,9,1860,0,0,0,0,0,'23 SEP 1860',2400677,0,48,'c29f14421901ef4b6a71f7bcf3d','E0038','2012-05-19 07:50:29.861400','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Anna Streiffert',38);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,1,1889,0,0,0,0,0,'31 JAN 1889',2411034,0,49,'c29f14420c868cf8d69edf4e878','E0028','2012-05-19 07:50:32.889025','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Astrid Shermanna Augusta Smith',59);
INSERT INTO "grampsdb_event" VALUES(0,0,0,16,9,1800,0,0,0,0,0,'16 SEP 1800',2378755,0,50,'c29f14422d4468f24b2843ac11f','E0056','2012-05-19 07:50:33.145708','1969-12-31 19:00:00',NULL,0,NULL,14,'Christening of Elna Jefferson',49);
INSERT INTO "grampsdb_event" VALUES(0,0,0,15,12,1886,0,0,0,0,0,'15 DEC 1886',2410256,0,51,'c29f144214d6000562cf7e3571c','E0035','2012-05-19 07:50:33.933965','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Kirsti Marie Smith',53);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1821,0,0,0,0,0,'29 JAN 1821',2386195,0,52,'c29f1441e64342e9d29e84736ab','E0005','2012-05-19 07:50:34.534996','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Hanna Smith',15);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,5,1985,0,0,0,0,0,'29 MAY 1985',2446215,0,53,'c29f1441f865dcdc0ab882830ec','E0013','2012-05-19 07:50:38.050016','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Jennifer Anderson',70);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,11,1885,0,0,0,0,0,'27 NOV 1885',2409873,0,54,'c29f14425ad706d77532fc06e02','E0085','2012-05-19 07:50:38.745322','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Gustaf Smith, Sr. and Anna Hansdotter',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,5,1910,0,0,0,0,0,'2 MAY 1910',2418794,0,55,'c29f1441fa3617d5ff2ae2b7690','E0014','2012-05-19 07:50:39.072796','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Lillie Harriet Jones',66);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,5,1995,0,0,0,0,0,'27 MAY 1995',2449865,0,56,'c29f144254d3dd7367ef94a791b','E0082','2012-05-19 07:50:39.339629','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Edwin Michael Smith and Janice Ann Adams',76);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1770,0,0,0,0,0,'ABT 1770',2367540,0,57,'c29f1442178747db796e14603c3','E0037','2012-05-19 07:50:39.619019','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Ingeman Smith',8);
INSERT INTO "grampsdb_event" VALUES(0,1,0,23,7,1930,0,0,0,0,0,'BEF 23 JUL 1930',2426181,0,58,'c29f14420fe39b11376553f9701','E0031','2012-05-19 07:50:42.012412','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Gustaf Smith, Sr.',14);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,4,1895,0,0,0,0,0,'7 APR 1895',2413291,0,59,'c29f144242c47008d61a6d8bd9','E0072','2012-05-19 07:50:42.278980','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Hjalmar Smith',6);
INSERT INTO "grampsdb_event" VALUES(0,0,0,17,4,1904,0,0,0,0,0,'17 APR 1904',2416588,0,60,'c29f144111a6f537adb6faf17c1','E0003','2012-05-19 07:50:42.543515','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Hans Peter Smith',39);
INSERT INTO "grampsdb_event" VALUES(0,2,0,0,0,1823,0,0,0,0,0,'AFT 1823',2386897,0,61,'c29f144240b1182f19edfc31312','E0071','2012-05-19 07:50:42.939876','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Ingar Smith',9);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1975,0,0,0,0,0,'26 JUN 1975',2442590,0,62,'c29f1442437230c612545b5576e','E0073','2012-05-19 07:50:45.087854','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Hjalmar Smith',45);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1979,0,0,0,1984,0,'BET 1979 AND 1984',2443875,0,63,'c29f144230c3a957e7edf3fbaae','E0059','2012-05-19 07:50:48.104922','1969-12-31 19:00:00',NULL,0,NULL,18,'Education of Edwin Michael Smith',11);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,64,'c29f144235d7172f5709d2527f3','E0064','2012-05-19 07:50:50.439635','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Martin Smith',27);
INSERT INTO "grampsdb_event" VALUES(0,0,0,16,9,1991,0,0,0,0,0,'16 SEP 1991',2448516,0,65,'c29f144229539982c7db5ad9e9a','E0052','2012-05-19 07:50:50.817323','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Lars Peter Smith',64);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1945,0,0,0,0,0,'1945',2431457,0,66,'c29f1441ec16b7d65d72a669353','E0007','2012-05-19 07:49:05.704587','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Herman Julius Nielsen',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1826,0,0,0,0,0,'29 JAN 1826',2388021,0,67,'c29f144237e663a096a1a6869b1','E0065','2012-05-19 07:50:51.089619','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Ingeman Smith',44);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,4,1998,0,0,0,0,0,'26 APR 1998',2450930,0,68,'c29f144201777fe6e1229fd21c6','E0020','2012-05-19 07:50:51.339354','1969-12-31 19:00:00',NULL,0,NULL,14,'Christening of Amber Marie Smith',33);
INSERT INTO "grampsdb_event" VALUES(0,0,0,3,6,1895,0,0,0,0,0,'3 JUN 1895',2413348,0,69,'c29f1442443717661b672fe3d60','E0074','2012-05-19 07:50:51.605934','1969-12-31 19:00:00',NULL,0,NULL,7,'Baptism of Hjalmar Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1988,0,0,0,0,0,'1988',2447162,0,70,'c29f144221174a4cc9e19962a16','E0046','2012-05-19 07:49:08.032159','1969-12-31 19:00:00',NULL,0,NULL,17,'Business Management',NULL);
INSERT INTO "grampsdb_event" VALUES(0,2,0,0,0,1966,0,0,0,0,0,'AFT 1966',2439127,0,71,'c29f14421b52cc3fc304fc9c964','E0040','2012-05-19 07:50:51.874845','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Craig Peter Smith',24);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,7,1996,0,0,0,0,0,'10 JUL 1996',2450275,0,72,'c29f14423da3f82cbd305cb2182','E0069','2012-05-19 07:50:58.178389','1969-12-31 19:00:00',NULL,0,NULL,14,'Christening of Mason Michael Smith',26);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,73,'c29f14423097ac14d5f0492355c','E0058','2012-05-19 07:49:11.103723','1969-12-31 19:00:00',NULL,0,NULL,29,'Software Engineer',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,30,1,1932,0,0,0,0,0,'30 JAN 1932',2426737,0,74,'c29f1441fbe4d858ff99782b900','E0016','2012-05-19 07:51:00.228067','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of John Hjalmar Smith',72);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,1,1893,0,0,0,0,0,'31 JAN 1893',2412495,0,75,'c29f14420665e31fb31eec7d21e','E0023','2012-05-19 07:51:00.500108','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Hjalmar Smith',32);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1899,0,0,0,1905,0,'BET 1899 AND 1905',2414656,0,76,'c29f144209c443ce22118f2b129','E0026','2012-05-19 07:51:04.018117','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Martin Smith',54);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,12,1862,0,0,0,0,0,'7 DEC 1862',2401482,0,77,'c29f14421134eae059aa99c64e2','E0033','2012-05-19 07:51:04.366970','1969-12-31 19:00:00',NULL,0,NULL,14,'Christening of Gustaf Smith, Sr.',16);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1996,0,0,0,0,0,'26 JUN 1996',2450261,0,78,'c29f14423cf3f4074cb6fa4464f','E0068','2012-05-19 07:51:04.745205','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Mason Michael Smith',40);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1794,0,0,0,1796,0,'BET 1794 AND 1796',2376306,0,79,'c29f144235232a2dcfa97c32fd6','E0063','2012-05-19 07:51:05.106070','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Martin Smith',5);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,10,1864,0,0,0,0,0,'2 OCT 1864',2402147,0,80,'c29f1440f4f165fc3fc2a411760','E0000','2012-05-19 07:51:05.828627','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Anna Hansdotter',48);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,81,'c29f1441fea27b43db5ccb90080','E0018','2012-05-19 07:49:17.565864','1969-12-31 19:00:00',NULL,0,NULL,3,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,11,1832,0,0,0,0,0,'29 NOV 1832',2390517,0,82,'c29f14423317098f46199f0e8b8','E0061','2012-05-19 07:51:06.198241','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Kerstina Hansdotter',30);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,9,1800,0,0,0,0,0,'14 SEP 1800',2378753,0,83,'c29f14422c0339470b69e079cc6','E0054','2012-05-19 07:51:07.804858','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Elna Jefferson',52);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,12,1899,0,0,0,0,0,'20 DEC 1899',2415009,0,84,'c29f1442038d823ef5d3b8b1ac','E0021','2012-05-19 07:51:08.079723','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Carl Emil Smith',4);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,5,1961,0,0,0,0,0,'24 MAY 1961',2437444,0,85,'c29f14422f77a952809ba36695f','E0057','2012-05-19 07:51:10.532601','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Edwin Michael Smith',61);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1990,0,0,0,0,0,'26 JUN 1990',2448069,0,86,'c29f1441fad5aa736ae01ca32b3','E0015','2012-05-19 07:49:20.782167','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Lillie Harriet Jones',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,8,1889,0,0,0,0,0,'31 AUG 1889',2411246,0,87,'c29f1441eb5684db6d556a96e8b','E0006','2012-05-19 07:51:14.372611','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Herman Julius Nielsen',37);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,12,1963,0,0,0,0,0,'21 DEC 1963',2438385,0,88,'c29f14420d21766d4dd012ade04','E0029','2012-05-19 07:51:14.732822','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Astrid Shermanna Augusta Smith',63);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,2,1927,0,0,0,0,0,'2 FEB 1927',2424914,0,89,'c29f144219b373bda1540f3f78f','E0039','2012-05-19 07:51:18.422240','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Anna Streiffert',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,1,1959,0,0,0,0,0,'28 JAN 1959',2436597,0,90,'c29f144204492593d511c93956','E0022','2012-05-19 07:51:23.171319','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Carl Emil Smith',34);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1886,0,0,0,0,0,'ABT 1886',2409908,0,91,'c29f14423fb64a4e8af3f32bb89','E0070','2012-05-19 07:49:27.392477','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Edwin Willard',NULL);
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
INSERT INTO "grampsdb_repository" VALUES(1,'c29f14426e834243344de3c0bb4','R0003','2012-05-19 07:49:00.759300','1969-12-31 19:00:00',NULL,0,NULL,3,'Aunt Martha''s Attic');
INSERT INTO "grampsdb_repository" VALUES(2,'c29f144269b6d2dd80f951d90b0','R0002','2012-05-19 07:49:24.288103','1969-12-31 19:00:00',NULL,0,NULL,3,'New York Public Library');
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
INSERT INTO "grampsdb_place" VALUES(1,'c29f144207811f8c8452c0ccb82','P0028','2012-05-19 07:48:20.125029','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(2,'c29f144213d3fcc7c8bfc98e256','P0041','2012-05-19 07:48:21.002952','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(3,'c29f144224df2f7bd2afcae202','P0058','2012-05-19 07:48:21.508979','1969-12-31 19:00:00',NULL,0,NULL,'Sacramento, Sacramento Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(4,'c29f144204368224268da843ff7','P0025','2012-05-19 07:48:22.286600','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(5,'c29f144235c3307d5080ea0c49d','P0074','2012-05-19 07:48:26.586678','1969-12-31 19:00:00',NULL,0,NULL,'Tommarp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(6,'c29f14424351263b930a24b3f4a','P0081','2012-05-19 07:48:27.842287','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(7,'c29f14425272a5830075ac74169','P0092','2012-05-19 07:48:28.087055','1969-12-31 19:00:00',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(8,'c29f14421813553b4228d4b24ed','P0044','2012-05-19 07:48:28.353778','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(9,'c29f144241474d5b20da07403e7','P0080','2012-05-19 07:48:29.113954','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(10,'c29f14425b617ed3abe3e163ed2','P0096','2012-05-19 07:48:29.664330','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(11,'c29f144231559ae25f9a3c1a168','P0069','2012-05-19 07:48:29.897584','1969-12-31 19:00:00',NULL,0,NULL,'UC Berkeley','','');
INSERT INTO "grampsdb_place" VALUES(12,'c29f144244b45950e34d11f8153','P0084','2012-05-19 07:48:31.164369','1969-12-31 19:00:00',NULL,0,NULL,'Ronne Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(13,'c29f14421113c3618b08b5054cb','P0039','2012-05-19 07:48:31.897741','1969-12-31 19:00:00',NULL,0,NULL,'Copenhagen, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(14,'c29f144210738afd2325dd8b500','P0037','2012-05-19 07:48:32.153276','1969-12-31 19:00:00',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(15,'c29f1441e771c0e22b2f9e369d3','P0010','2012-05-19 07:48:32.408626','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(16,'c29f144211c241cb9fbe0fd33f7','P0040','2012-05-19 07:48:32.664211','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(17,'c29f14421a5777323230b4f11cf','P0047','2012-05-19 07:48:33.419957','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(18,'c29f14423441408d4ef35d28c42','P0072','2012-05-19 07:48:34.430893','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(19,'c29f14421eb4aa349a69393c09f','P0051','2012-05-19 07:48:36.137449','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(20,'c29f14420ae382d9a6e72514ac','P0032','2012-05-19 07:48:37.008611','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(21,'c29f144261145afb963600d567a','P0097','2012-05-19 07:48:37.258044','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(22,'c29f144216016647d2dab1f22c9','P0043','2012-05-19 07:48:38.208565','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(23,'c29f14424794adfed7c09343348','P0086','2012-05-19 07:48:38.813650','1969-12-31 19:00:00',NULL,0,NULL,'Simrishamn, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(24,'c29f14421be491c5e183dfa83e1','P0048','2012-05-19 07:48:39.569126','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(25,'c29f14420fd2ec26416bfa2ee97','P0036','2012-05-19 07:48:41.208712','1969-12-31 19:00:00',NULL,0,NULL,'Grostorp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(26,'c29f14423e330e7ebb2ccc16de0','P0079','2012-05-19 07:48:41.530729','1969-12-31 19:00:00',NULL,0,NULL,'Community Presbyterian Church, Danville, CA','','');
INSERT INTO "grampsdb_place" VALUES(27,'c29f14423654b6e2a979798c5fa','P0075','2012-05-19 07:48:45.530777','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(28,'c29f14420992aa86b78c9d7a326','P0029','2012-05-19 07:48:46.042145','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(29,'c29f14424992f8a87ea74518b62','P0087','2012-05-19 07:48:46.575050','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(30,'c29f1442339235383f2df55b587','P0071','2012-05-19 07:48:48.069006','1969-12-31 19:00:00',NULL,0,NULL,'Smestorp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(31,'c29f1441e233ceda8f25ff35947','P0008','2012-05-19 07:48:48.791202','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(32,'c29f144206e4f4367a4de3fea5d','P0027','2012-05-19 07:48:49.152903','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(33,'c29f144201f441ac153a0e09c8d','P0024','2012-05-19 07:48:50.419399','1969-12-31 19:00:00',NULL,0,NULL,'Community Presbyterian Church, Danville, CA','','');
INSERT INTO "grampsdb_place" VALUES(34,'c29f144204d19efcd9b6263f878','P0026','2012-05-19 07:48:50.919272','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(35,'c29f1441f453a7ac88df18d8542','P0014','2012-05-19 07:48:51.425351','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(36,'c29f14422d154d4e9701a565be3','P0064','2012-05-19 07:48:51.691114','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(37,'c29f1441ec038d3199ca52eb8bb','P0011','2012-05-19 07:48:51.946737','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(38,'c29f1442198176f2ebd5d214c0','P0046','2012-05-19 07:48:52.235949','1969-12-31 19:00:00',NULL,0,NULL,'Hoya/Jona/Hoia, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(39,'c29f14411297a022bd019e123f5','P0007','2012-05-19 07:48:56.357929','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(40,'c29f14423d899b7c12b30d175c','P0078','2012-05-19 07:48:57.346676','1969-12-31 19:00:00',NULL,0,NULL,'Hayward, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(41,'c29f144265b62c5f0be3fe627e6','P0099','2012-05-19 07:48:58.652788','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(42,'c29f14420153bfa62167ca0f3c6','P0022','2012-05-19 07:48:59.868919','1969-12-31 19:00:00',NULL,0,NULL,'Hayward, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(43,'c29f1441062407fb2e6c7c4ec04','P0005','2012-05-19 07:49:03.013234','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(44,'c29f1442386287b229545c3c8d3','P0076','2012-05-19 07:49:03.346478','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(45,'c29f14424413a3e7815d5593c40','P0082','2012-05-19 07:49:05.141327','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(46,'c29f1441f8445d252cf00e6434','P0016','2012-05-19 07:49:06.213252','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(47,'c29f14424561b0faf3844125cbc','P0085','2012-05-19 07:49:06.452383','1969-12-31 19:00:00',NULL,0,NULL,'Copenhagen, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(48,'c29f1440f742c9dee5d891a8cae','P0001','2012-05-19 07:49:07.424351','1969-12-31 19:00:00',NULL,0,NULL,'Loderup, Malmous Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(49,'c29f14422dc10eccec0a43ce36a','P0065','2012-05-19 07:49:07.701880','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(50,'c29f14425605d5f78afa25c62d5','P0095','2012-05-19 07:49:08.912986','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(51,'c29f14422345a7404a6daab6c8e','P0056','2012-05-19 07:49:09.408256','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(52,'c29f14422c8101eb9c55ba84aad','P0063','2012-05-19 07:49:10.835151','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(53,'c29f1442155574dd7efd336e003','P0042','2012-05-19 07:49:11.368446','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(54,'c29f14420a4d725519088fe297','P0031','2012-05-19 07:49:11.635167','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(55,'c29f1442286f6aa2a614e89db1','P0060','2012-05-19 07:49:11.901781','1969-12-31 19:00:00',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(56,'c29f144262744da1b280ee40562','P0098','2012-05-19 07:49:12.735435','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(57,'c29f14424f349fbd9b4af1f959c','P0090','2012-05-19 07:49:14.496714','1969-12-31 19:00:00',NULL,0,NULL,'Woodland, Yolo Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(58,'c29f1441fe858d5a3e681de55f5','P0020','2012-05-19 07:49:14.746394','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(59,'c29f14420d17d4a9848d794ce54','P0033','2012-05-19 07:49:15.990665','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(60,'c29f1441f525ded7b972a5e74d7','P0015','2012-05-19 07:49:16.241229','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(61,'c29f14423005b2baf02629521bb','P0067','2012-05-19 07:49:16.752358','1969-12-31 19:00:00',NULL,0,NULL,'San Jose, Santa Clara Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(62,'c29f14422654829cbc7f814bb41','P0059','2012-05-19 07:49:17.324026','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(63,'c29f14420db2937254e345a1267','P0034','2012-05-19 07:49:18.090811','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(64,'c29f144229e7bf26c3c988e20a5','P0062','2012-05-19 07:49:18.874529','1969-12-31 19:00:00',NULL,0,NULL,'Santa Rosa, Sonoma Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(65,'c29f14424d25c1ec7e82765aefc','P0088','2012-05-19 07:49:19.385494','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(66,'c29f1441fac788507a96f6552c3','P0018','2012-05-19 07:49:20.446330','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(67,'c29f14425112bf132acab47d217','P0091','2012-05-19 07:49:21.396744','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(68,'c29f1440f97360df8530f9d7eb2','P0003','2012-05-19 07:49:21.657382','1969-12-31 19:00:00',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(69,'c29f144222a19f3300c8c1b44f1','P0055','2012-05-19 07:49:23.068516','1969-12-31 19:00:00',NULL,0,NULL,'Denver, Denver Co., CO','','');
INSERT INTO "grampsdb_place" VALUES(70,'c29f1441f91614bc48aed119ee2','P0017','2012-05-19 07:49:23.579477','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(71,'c29f144220d2897ca49a9e9277d','P0053','2012-05-19 07:49:23.868492','1969-12-31 19:00:00',NULL,0,NULL,'Fremont, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(72,'c29f1441fc6655416c483a04dbb','P0019','2012-05-19 07:49:25.229832','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(73,'c29f14421e1594bbf29e078e9ad','P0050','2012-05-19 07:49:26.063253','1969-12-31 19:00:00',NULL,0,NULL,'Simrishamn, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(74,'c29f14423a833ee45f820d97876','P0077','2012-05-19 07:49:26.523689','1969-12-31 19:00:00',NULL,0,NULL,'San Jose, Santa Clara Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(75,'c29f1441f1b3cea6dbfa491c9a1','P0013','2012-05-19 07:49:27.657108','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(76,'c29f144255577a48ebec4bce96c','P0094','2012-05-19 07:49:28.368649','1969-12-31 19:00:00',NULL,0,NULL,'San Ramon, Conta Costa Co., CA','','');
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
INSERT INTO "grampsdb_note" VALUES(1,'c29f14424625ce37b05bee55632','N0003','2012-05-19 07:48:17.477318','1969-12-31 19:00:00',NULL,0,NULL,3,'BIOGRAPHY

Hjalmar sailed from Copenhagen, Denmark on the OSCAR II, 14 November 1912 arriving in New York 27 November 1912. He was seventeen years old. On the ship passenger list his trade was listed as a Blacksmith.  He came to Reno, Nevada and lived with his sister Marie for a time before settling in Sparks. He worked for Southern Pacific Railroad as a car inspector for a time, then went to work for Standard Oil
Company. He enlisted in the army at Sparks 7 December 1917 and served as a Corporal in the Medical Corp until his discharge 12 August 1919 at the Presidio in San Francisco, California. Both he and Marjorie are buried in the Masonic Memorial Gardens Mausoleum in Reno, he the 30th June 1975, and she the 25th of June 1980.',0);
INSERT INTO "grampsdb_note" VALUES(2,'c29f1440f2a2a8a78b7e7cff665','N0000','2012-05-19 07:48:18.242473','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SUBM (Submitter): @SUBM@:

Warn: ADDR overwritten             Line    19: 2 ADR1 Not Provided
',0);
INSERT INTO "grampsdb_note" VALUES(3,'c29f14426f037f74f77f09566a0','N0002','2012-05-19 07:48:21.777613','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into REPO (repository) Gramps ID R0003:

Warn: ADDR overwritten             Line   918: 2 ADR1 123 Main St
',0);
INSERT INTO "grampsdb_note" VALUES(4,'c29f14427074ec2e6d0ff3d98e1','N0003','2012-05-19 07:48:23.432364','1969-12-31 19:00:00',NULL,0,NULL,3,'Objects referenced by this note were missing in a file imported on 05/19/2012 07:48:16 AM.',0);
INSERT INTO "grampsdb_note" VALUES(5,'c29f14426ed7859ef33525b8a63','N0006','2012-05-19 07:48:24.493894','1969-12-31 19:00:00',NULL,0,NULL,3,'Some note on the repo',0);
INSERT INTO "grampsdb_note" VALUES(6,'c29f14426dfcddb30c826e5574','N0001','2012-05-19 07:48:27.344001','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into REPO (repository) Gramps ID R0002:

Warn: ADDR overwritten             Line   910: 2 ADR1 5th Ave at 42 street
',0);
INSERT INTO "grampsdb_note" VALUES(7,'c29f14420ba7960337f89e790d0','N0002','2012-05-19 07:48:50.160068','1969-12-31 19:00:00',NULL,0,NULL,3,'BIOGRAPHY
Martin was listed as being a Husman, (owning a house as opposed to a farm) in the house records of Gladsax.',0);
INSERT INTO "grampsdb_note" VALUES(8,'c29f144269d2545181ab67e323d','N0004','2012-05-19 07:48:53.571227','1969-12-31 19:00:00',NULL,0,NULL,3,'But Aunt Martha still keeps the original!',0);
INSERT INTO "grampsdb_note" VALUES(9,'c29f14421c0716a73524c02c98e','N0000','2012-05-19 07:49:05.953821','1969-12-31 19:00:00',NULL,0,NULL,3,'Witness name: John Doe
Witness comment: This is a simple test.',0);
INSERT INTO "grampsdb_note" VALUES(10,'c29f144230b6df0c40758ab67e7','N0001','2012-05-19 07:49:19.904141','1969-12-31 19:00:00',NULL,0,NULL,3,'Witness name: No Name',0);
INSERT INTO "grampsdb_note" VALUES(11,'c29f14426cd3cb5dfac631ddabf','N0005','2012-05-19 07:49:24.981495','1969-12-31 19:00:00',NULL,0,NULL,3,'The repository reference from the source is important',0);
CREATE TABLE "grampsdb_surname" (
    "id" integer NOT NULL PRIMARY KEY,
    "name_origin_type_id" integer NOT NULL REFERENCES "grampsdb_nameorigintype" ("id"),
    "surname" text NOT NULL,
    "prefix" text NOT NULL,
    "primary" bool NOT NULL,
    "connector" text NOT NULL,
    "name_id" integer NOT NULL
);
INSERT INTO "grampsdb_surname" VALUES(1,1,'Smith','',1,'',1);
INSERT INTO "grampsdb_surname" VALUES(2,1,'Smith','',1,'',2);
INSERT INTO "grampsdb_surname" VALUES(3,1,'Smith','',1,'',3);
INSERT INTO "grampsdb_surname" VALUES(4,1,'Ohman','',1,'',4);
INSERT INTO "grampsdb_surname" VALUES(5,1,'Smith','',1,'',5);
INSERT INTO "grampsdb_surname" VALUES(6,1,'Jones','',1,'',6);
INSERT INTO "grampsdb_surname" VALUES(7,1,'Smith','',1,'',7);
INSERT INTO "grampsdb_surname" VALUES(8,1,'Smith','',1,'',8);
INSERT INTO "grampsdb_surname" VALUES(9,1,'Michaels','',1,'',9);
INSERT INTO "grampsdb_surname" VALUES(10,1,'Nielsen','',1,'',10);
INSERT INTO "grampsdb_surname" VALUES(11,1,'Smith','',1,'',11);
INSERT INTO "grampsdb_surname" VALUES(12,1,'Smith','',1,'',12);
INSERT INTO "grampsdb_surname" VALUES(13,1,'Smith','',1,'',13);
INSERT INTO "grampsdb_surname" VALUES(14,1,'Willard','',1,'',14);
INSERT INTO "grampsdb_surname" VALUES(15,1,'Anderson','',1,'',15);
INSERT INTO "grampsdb_surname" VALUES(16,1,'Smith','',1,'',16);
INSERT INTO "grampsdb_surname" VALUES(17,1,'Jefferson','',1,'',17);
INSERT INTO "grampsdb_surname" VALUES(18,1,'Streiffert','',1,'',18);
INSERT INTO "grampsdb_surname" VALUES(19,1,'Smith','',1,'',19);
INSERT INTO "grampsdb_surname" VALUES(20,1,'Smith','',1,'',20);
INSERT INTO "grampsdb_surname" VALUES(21,1,'Smith','',1,'',21);
INSERT INTO "grampsdb_surname" VALUES(22,1,'Smith','',1,'',22);
INSERT INTO "grampsdb_surname" VALUES(23,1,'Smith','',1,'',23);
INSERT INTO "grampsdb_surname" VALUES(24,1,'Smith','',1,'',24);
INSERT INTO "grampsdb_surname" VALUES(25,1,'Smith','',1,'',25);
INSERT INTO "grampsdb_surname" VALUES(26,1,'Smith','',1,'',26);
INSERT INTO "grampsdb_surname" VALUES(27,1,'Green','',1,'',27);
INSERT INTO "grampsdb_surname" VALUES(28,1,'Smith','',1,'',28);
INSERT INTO "grampsdb_surname" VALUES(29,1,'Smith','',1,'',29);
INSERT INTO "grampsdb_surname" VALUES(30,1,'Smith','',1,'',30);
INSERT INTO "grampsdb_surname" VALUES(31,1,'Smith','',1,'',31);
INSERT INTO "grampsdb_surname" VALUES(32,1,'Smith','',1,'',32);
INSERT INTO "grampsdb_surname" VALUES(33,1,'Smith','',1,'',33);
INSERT INTO "grampsdb_surname" VALUES(34,1,'Horne','',1,'',34);
INSERT INTO "grampsdb_surname" VALUES(35,1,'Adams','',1,'',35);
INSERT INTO "grampsdb_surname" VALUES(36,1,'Smith','',1,'',36);
INSERT INTO "grampsdb_surname" VALUES(37,1,'Hansdotter','',1,'',37);
INSERT INTO "grampsdb_surname" VALUES(38,1,'Hansdotter','',1,'',38);
INSERT INTO "grampsdb_surname" VALUES(39,1,'Smith','',1,'',39);
INSERT INTO "grampsdb_surname" VALUES(40,1,'Ericsdotter','',1,'',40);
INSERT INTO "grampsdb_surname" VALUES(41,1,'Smith','',1,'',41);
INSERT INTO "grampsdb_surname" VALUES(42,1,'Perkins','',1,'',42);
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
INSERT INTO "grampsdb_name" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:28.615353',NULL,NULL,1,4,1,'Hanna','','','','','','',1,1,1);
INSERT INTO "grampsdb_name" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:31.516736',NULL,NULL,1,4,1,'Eric Lloyd','','','','','','',1,1,2);
INSERT INTO "grampsdb_name" VALUES(3,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:34.268793',NULL,NULL,1,4,1,'Hans Peter','','','','','','',1,1,3);
INSERT INTO "grampsdb_name" VALUES(4,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:37.064884',NULL,NULL,1,4,1,'Marjorie','','','','','','',1,1,4);
INSERT INTO "grampsdb_name" VALUES(5,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:38.674510',NULL,NULL,1,4,1,'Hjalmar','','','','','','',1,1,5);
INSERT INTO "grampsdb_name" VALUES(6,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:41.333793',NULL,NULL,1,4,1,'Lillie Harriet','','','','','','',1,1,6);
INSERT INTO "grampsdb_name" VALUES(7,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:42.669978',NULL,NULL,1,4,1,'Marjorie Lee','','','','','','',1,1,7);
INSERT INTO "grampsdb_name" VALUES(8,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:44.333073',NULL,NULL,1,4,1,'Hjalmar','','','','','','',1,1,8);
INSERT INTO "grampsdb_name" VALUES(9,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:46.445858',NULL,NULL,1,4,1,'Evelyn','','','','','','',1,1,9);
INSERT INTO "grampsdb_name" VALUES(10,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:48.249672',NULL,NULL,1,4,1,'Herman Julius','','','','','','',1,1,10);
INSERT INTO "grampsdb_name" VALUES(11,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:52.124806',NULL,NULL,1,4,1,'Gus','','','','','','',1,1,11);
INSERT INTO "grampsdb_name" VALUES(12,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:54.573103',NULL,NULL,1,4,1,'Ingeman','','','','','','',1,1,12);
INSERT INTO "grampsdb_name" VALUES(13,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:56.061203',NULL,NULL,1,4,1,'Lars Peter','','','','','','',1,1,13);
INSERT INTO "grampsdb_name" VALUES(14,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:49:58.433073',NULL,NULL,1,4,1,'Edwin','','','','','','',1,1,14);
INSERT INTO "grampsdb_name" VALUES(15,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:01.925742',NULL,NULL,1,4,1,'Jennifer','','','','','','',1,1,15);
INSERT INTO "grampsdb_name" VALUES(16,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:05.171731',NULL,NULL,1,4,1,'Lloyd','','','','','','',1,1,16);
INSERT INTO "grampsdb_name" VALUES(17,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:09.718094',NULL,NULL,1,4,1,'Elna','','','','','','',1,1,17);
INSERT INTO "grampsdb_name" VALUES(18,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:13.631138',NULL,NULL,1,4,1,'Anna','','','','','','',1,1,18);
INSERT INTO "grampsdb_name" VALUES(19,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:15.902014',NULL,NULL,1,4,1,'Kirsti Marie','','','','','','',1,1,19);
INSERT INTO "grampsdb_name" VALUES(20,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:20.111507',NULL,NULL,1,4,1,'Amber Marie','','','','','','',1,1,20);
INSERT INTO "grampsdb_name" VALUES(21,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:24.419169',NULL,NULL,1,4,1,'Astrid Shermanna Augusta','','','','','','',1,1,21);
INSERT INTO "grampsdb_name" VALUES(22,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:27.854737',NULL,NULL,1,4,1,'Marjorie Alice','','','','','','',1,1,22);
INSERT INTO "grampsdb_name" VALUES(23,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:30.126881',NULL,NULL,1,4,1,'Martin','','','','','','',1,1,23);
INSERT INTO "grampsdb_name" VALUES(24,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:35.336994',NULL,NULL,1,4,1,'Gustaf','Sr.','','','','','',1,1,24);
INSERT INTO "grampsdb_name" VALUES(25,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:43.205078',NULL,NULL,1,4,1,'Ingar','','','','','','',1,1,25);
INSERT INTO "grampsdb_name" VALUES(26,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:45.441100',NULL,NULL,1,4,1,'Emil','','','','','','',1,1,26);
INSERT INTO "grampsdb_name" VALUES(27,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:47.060157',NULL,NULL,1,4,1,'Janis Elaine','','','','','','',1,1,27);
INSERT INTO "grampsdb_name" VALUES(28,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:48.354748',NULL,NULL,1,4,1,'Mason Michael','','','','','','',1,1,28);
INSERT INTO "grampsdb_name" VALUES(29,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:52.716160',NULL,NULL,1,4,1,'John Hjalmar','','','','','','',1,1,29);
INSERT INTO "grampsdb_name" VALUES(30,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:54.560074',NULL,NULL,1,4,1,'Ingeman','','','','','','',1,1,30);
INSERT INTO "grampsdb_name" VALUES(31,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:56.154251',NULL,NULL,1,4,1,'Martin','','','','','','',1,1,31);
INSERT INTO "grampsdb_name" VALUES(32,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:58.710592',NULL,NULL,1,4,1,'Keith Lloyd','','','','','','',1,1,32);
INSERT INTO "grampsdb_name" VALUES(33,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:00.764508',NULL,NULL,1,4,1,'Magnes','','','','','','',1,1,33);
INSERT INTO "grampsdb_name" VALUES(34,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:06.556209',NULL,NULL,1,4,1,'Darcy','','','','','','',1,1,34);
INSERT INTO "grampsdb_name" VALUES(35,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:08.363376',NULL,NULL,1,4,1,'Janice Ann','','','','','','',1,1,35);
INSERT INTO "grampsdb_name" VALUES(36,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:11.062229',NULL,NULL,1,4,1,'Carl Emil','','','','','','',1,1,36);
INSERT INTO "grampsdb_name" VALUES(37,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:13.017436',NULL,NULL,1,4,1,'Anna','','','','','','',1,1,37);
INSERT INTO "grampsdb_name" VALUES(38,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:15.883595',NULL,NULL,1,4,1,'Kerstina','','','','','','',1,1,38);
INSERT INTO "grampsdb_name" VALUES(39,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:18.685983',NULL,NULL,1,4,1,'Edwin Michael','','','','','','',1,1,39);
INSERT INTO "grampsdb_name" VALUES(40,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:21.519781',NULL,NULL,1,4,1,'Marta','','','','','','',1,1,40);
INSERT INTO "grampsdb_name" VALUES(41,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:23.721879',NULL,NULL,1,4,1,'Craig Peter','','','','','','',1,1,41);
INSERT INTO "grampsdb_name" VALUES(42,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:25.652622',NULL,NULL,1,4,1,'Alice Paula','','','','','','',1,1,42);
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
INSERT INTO "grampsdb_markup" VALUES(1,2,1,1,'Monospace','[(0, 120)]');
INSERT INTO "grampsdb_markup" VALUES(2,3,1,1,'Monospace','[(0, 128)]');
INSERT INTO "grampsdb_markup" VALUES(3,6,1,1,'Monospace','[(0, 137)]');
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
INSERT INTO "grampsdb_address" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:50:41.208301',NULL,NULL,1,NULL,1);
INSERT INTO "grampsdb_address" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-19 07:51:18.167439',NULL,NULL,1,NULL,2);
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
INSERT INTO "grampsdb_attribute" VALUES(1,0,12,'23',52,74);
INSERT INTO "grampsdb_attribute" VALUES(2,0,10,'Bad breath',36,90);
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
INSERT INTO "grampsdb_noteref" VALUES(1,32,5,1,'2012-05-19 07:49:40.764259',NULL,NULL,0,1);
INSERT INTO "grampsdb_noteref" VALUES(2,36,37,1,'2012-05-19 07:50:22.240970',NULL,NULL,0,9);
INSERT INTO "grampsdb_noteref" VALUES(3,32,23,1,'2012-05-19 07:50:32.233558',NULL,NULL,0,7);
INSERT INTO "grampsdb_noteref" VALUES(4,37,1,1,'2012-05-19 07:50:39.882104',NULL,NULL,0,5);
INSERT INTO "grampsdb_noteref" VALUES(5,37,1,1,'2012-05-19 07:50:40.155881',NULL,NULL,0,3);
INSERT INTO "grampsdb_noteref" VALUES(6,36,73,1,'2012-05-19 07:50:58.447482',NULL,NULL,0,10);
INSERT INTO "grampsdb_noteref" VALUES(7,37,2,1,'2012-05-19 07:51:17.287538',NULL,NULL,0,6);
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
INSERT INTO "grampsdb_eventref" VALUES(1,32,1,1,'2012-05-19 07:49:29.166961',NULL,NULL,0,52,3);
INSERT INTO "grampsdb_eventref" VALUES(2,32,2,1,'2012-05-19 07:49:32.024469',NULL,NULL,0,38,3);
INSERT INTO "grampsdb_eventref" VALUES(3,32,2,1,'2012-05-19 07:49:32.283920',NULL,NULL,0,81,3);
INSERT INTO "grampsdb_eventref" VALUES(4,32,3,1,'2012-05-19 07:49:34.772722',NULL,NULL,0,60,3);
INSERT INTO "grampsdb_eventref" VALUES(5,32,3,1,'2012-05-19 07:49:35.007629',NULL,NULL,0,21,3);
INSERT INTO "grampsdb_eventref" VALUES(6,32,4,1,'2012-05-19 07:49:37.735520',NULL,NULL,0,39,3);
INSERT INTO "grampsdb_eventref" VALUES(7,32,4,1,'2012-05-19 07:49:38.084470',NULL,NULL,0,27,3);
INSERT INTO "grampsdb_eventref" VALUES(8,32,5,1,'2012-05-19 07:49:39.207865',NULL,NULL,0,59,3);
INSERT INTO "grampsdb_eventref" VALUES(9,32,5,1,'2012-05-19 07:49:39.474588',NULL,NULL,0,62,3);
INSERT INTO "grampsdb_eventref" VALUES(10,32,5,1,'2012-05-19 07:49:39.752181',NULL,NULL,0,69,3);
INSERT INTO "grampsdb_eventref" VALUES(11,32,5,1,'2012-05-19 07:49:40.028907',NULL,NULL,0,19,3);
INSERT INTO "grampsdb_eventref" VALUES(12,32,6,1,'2012-05-19 07:49:41.840457',NULL,NULL,0,55,3);
INSERT INTO "grampsdb_eventref" VALUES(13,32,6,1,'2012-05-19 07:49:42.114067',NULL,NULL,0,86,3);
INSERT INTO "grampsdb_eventref" VALUES(14,32,7,1,'2012-05-19 07:49:43.190819',NULL,NULL,0,31,3);
INSERT INTO "grampsdb_eventref" VALUES(15,32,8,1,'2012-05-19 07:49:44.851260',NULL,NULL,0,75,3);
INSERT INTO "grampsdb_eventref" VALUES(16,32,8,1,'2012-05-19 07:49:45.118932',NULL,NULL,0,42,3);
INSERT INTO "grampsdb_eventref" VALUES(17,32,9,1,'2012-05-19 07:49:46.962511',NULL,NULL,0,33,3);
INSERT INTO "grampsdb_eventref" VALUES(18,32,10,1,'2012-05-19 07:49:48.963113',NULL,NULL,0,87,3);
INSERT INTO "grampsdb_eventref" VALUES(19,32,10,1,'2012-05-19 07:49:49.250862',NULL,NULL,0,66,3);
INSERT INTO "grampsdb_eventref" VALUES(20,33,1,1,'2012-05-19 07:49:50.771746',NULL,NULL,0,29,10);
INSERT INTO "grampsdb_eventref" VALUES(21,32,11,1,'2012-05-19 07:49:52.635842',NULL,NULL,0,36,3);
INSERT INTO "grampsdb_eventref" VALUES(22,32,11,1,'2012-05-19 07:49:52.913125',NULL,NULL,0,44,3);
INSERT INTO "grampsdb_eventref" VALUES(23,32,12,1,'2012-05-19 07:49:55.091513',NULL,NULL,0,57,3);
INSERT INTO "grampsdb_eventref" VALUES(24,32,13,1,'2012-05-19 07:49:56.696057',NULL,NULL,0,65,3);
INSERT INTO "grampsdb_eventref" VALUES(25,32,13,1,'2012-05-19 07:49:56.962324',NULL,NULL,0,11,3);
INSERT INTO "grampsdb_eventref" VALUES(26,32,14,1,'2012-05-19 07:49:59.123895',NULL,NULL,0,91,3);
INSERT INTO "grampsdb_eventref" VALUES(27,32,15,1,'2012-05-19 07:50:02.501655',NULL,NULL,0,26,3);
INSERT INTO "grampsdb_eventref" VALUES(28,32,15,1,'2012-05-19 07:50:02.768094',NULL,NULL,0,53,3);
INSERT INTO "grampsdb_eventref" VALUES(29,32,16,1,'2012-05-19 07:50:05.690524',NULL,NULL,0,7,3);
INSERT INTO "grampsdb_eventref" VALUES(30,32,17,1,'2012-05-19 07:50:10.234832',NULL,NULL,0,83,3);
INSERT INTO "grampsdb_eventref" VALUES(31,32,17,1,'2012-05-19 07:50:10.502053',NULL,NULL,0,40,3);
INSERT INTO "grampsdb_eventref" VALUES(32,32,17,1,'2012-05-19 07:50:10.772447',NULL,NULL,0,50,3);
INSERT INTO "grampsdb_eventref" VALUES(33,33,5,1,'2012-05-19 07:50:12.084946',NULL,NULL,0,43,10);
INSERT INTO "grampsdb_eventref" VALUES(34,32,18,1,'2012-05-19 07:50:14.424558',NULL,NULL,0,48,3);
INSERT INTO "grampsdb_eventref" VALUES(35,32,18,1,'2012-05-19 07:50:14.801748',NULL,NULL,0,89,3);
INSERT INTO "grampsdb_eventref" VALUES(36,32,19,1,'2012-05-19 07:50:16.579337',NULL,NULL,0,51,3);
INSERT INTO "grampsdb_eventref" VALUES(37,32,19,1,'2012-05-19 07:50:16.844831',NULL,NULL,0,47,3);
INSERT INTO "grampsdb_eventref" VALUES(38,32,20,1,'2012-05-19 07:50:20.629251',NULL,NULL,0,45,3);
INSERT INTO "grampsdb_eventref" VALUES(39,32,20,1,'2012-05-19 07:50:20.905978',NULL,NULL,0,68,3);
INSERT INTO "grampsdb_eventref" VALUES(40,32,21,1,'2012-05-19 07:50:25.051496',NULL,NULL,0,49,3);
INSERT INTO "grampsdb_eventref" VALUES(41,32,21,1,'2012-05-19 07:50:25.412156',NULL,NULL,0,88,3);
INSERT INTO "grampsdb_eventref" VALUES(42,32,22,1,'2012-05-19 07:50:28.372990',NULL,NULL,0,16,3);
INSERT INTO "grampsdb_eventref" VALUES(43,32,23,1,'2012-05-19 07:50:30.634345',NULL,NULL,0,15,3);
INSERT INTO "grampsdb_eventref" VALUES(44,32,23,1,'2012-05-19 07:50:30.906796',NULL,NULL,0,76,3);
INSERT INTO "grampsdb_eventref" VALUES(45,32,23,1,'2012-05-19 07:50:31.263977',NULL,NULL,0,4,3);
INSERT INTO "grampsdb_eventref" VALUES(46,33,9,1,'2012-05-19 07:50:33.686894',NULL,NULL,0,41,10);
INSERT INTO "grampsdb_eventref" VALUES(47,32,24,1,'2012-05-19 07:50:35.846853',NULL,NULL,0,5,3);
INSERT INTO "grampsdb_eventref" VALUES(48,32,24,1,'2012-05-19 07:50:36.116360',NULL,NULL,0,58,3);
INSERT INTO "grampsdb_eventref" VALUES(49,32,24,1,'2012-05-19 07:50:36.368469',NULL,NULL,0,10,3);
INSERT INTO "grampsdb_eventref" VALUES(50,32,24,1,'2012-05-19 07:50:36.617261',NULL,NULL,0,77,3);
INSERT INTO "grampsdb_eventref" VALUES(51,32,25,1,'2012-05-19 07:50:43.834876',NULL,NULL,0,61,3);
INSERT INTO "grampsdb_eventref" VALUES(52,32,26,1,'2012-05-19 07:50:45.990476',NULL,NULL,0,30,3);
INSERT INTO "grampsdb_eventref" VALUES(53,32,27,1,'2012-05-19 07:50:47.574825',NULL,NULL,0,18,3);
INSERT INTO "grampsdb_eventref" VALUES(54,32,28,1,'2012-05-19 07:50:48.828980',NULL,NULL,0,78,3);
INSERT INTO "grampsdb_eventref" VALUES(55,32,28,1,'2012-05-19 07:50:49.139781',NULL,NULL,0,72,3);
INSERT INTO "grampsdb_eventref" VALUES(56,32,29,1,'2012-05-19 07:50:53.472734',NULL,NULL,0,74,3);
INSERT INTO "grampsdb_eventref" VALUES(57,32,30,1,'2012-05-19 07:50:55.072763',NULL,NULL,0,67,3);
INSERT INTO "grampsdb_eventref" VALUES(58,32,31,1,'2012-05-19 07:50:56.660918',NULL,NULL,0,79,3);
INSERT INTO "grampsdb_eventref" VALUES(59,32,31,1,'2012-05-19 07:50:56.927981',NULL,NULL,0,64,3);
INSERT INTO "grampsdb_eventref" VALUES(60,32,32,1,'2012-05-19 07:50:59.195322',NULL,NULL,0,23,3);
INSERT INTO "grampsdb_eventref" VALUES(61,32,33,1,'2012-05-19 07:51:01.422755',NULL,NULL,0,28,3);
INSERT INTO "grampsdb_eventref" VALUES(62,32,33,1,'2012-05-19 07:51:01.734762',NULL,NULL,0,2,3);
INSERT INTO "grampsdb_eventref" VALUES(63,32,34,1,'2012-05-19 07:51:07.250202',NULL,NULL,0,34,3);
INSERT INTO "grampsdb_eventref" VALUES(64,32,35,1,'2012-05-19 07:51:09.300543',NULL,NULL,0,14,3);
INSERT INTO "grampsdb_eventref" VALUES(65,32,35,1,'2012-05-19 07:51:09.704668',NULL,NULL,0,24,3);
INSERT INTO "grampsdb_eventref" VALUES(66,32,35,1,'2012-05-19 07:51:10.005395',NULL,NULL,0,70,3);
INSERT INTO "grampsdb_eventref" VALUES(67,32,36,1,'2012-05-19 07:51:11.668686',NULL,NULL,0,84,3);
INSERT INTO "grampsdb_eventref" VALUES(68,32,36,1,'2012-05-19 07:51:11.923527',NULL,NULL,0,90,3);
INSERT INTO "grampsdb_eventref" VALUES(69,32,37,1,'2012-05-19 07:51:13.523301',NULL,NULL,0,80,3);
INSERT INTO "grampsdb_eventref" VALUES(70,32,37,1,'2012-05-19 07:51:13.794817',NULL,NULL,0,35,3);
INSERT INTO "grampsdb_eventref" VALUES(71,32,38,1,'2012-05-19 07:51:16.478906',NULL,NULL,0,82,3);
INSERT INTO "grampsdb_eventref" VALUES(72,32,38,1,'2012-05-19 07:51:16.760687',NULL,NULL,0,25,3);
INSERT INTO "grampsdb_eventref" VALUES(73,32,39,1,'2012-05-19 07:51:19.466735',NULL,NULL,0,85,3);
INSERT INTO "grampsdb_eventref" VALUES(74,32,39,1,'2012-05-19 07:51:19.739565',NULL,NULL,0,73,3);
INSERT INTO "grampsdb_eventref" VALUES(75,32,39,1,'2012-05-19 07:51:20.244672',NULL,NULL,0,63,3);
INSERT INTO "grampsdb_eventref" VALUES(76,32,39,1,'2012-05-19 07:51:20.500943',NULL,NULL,0,9,3);
INSERT INTO "grampsdb_eventref" VALUES(77,32,40,1,'2012-05-19 07:51:22.025547',NULL,NULL,0,12,3);
INSERT INTO "grampsdb_eventref" VALUES(78,33,15,1,'2012-05-19 07:51:22.904482',NULL,NULL,0,32,10);
INSERT INTO "grampsdb_eventref" VALUES(79,32,41,1,'2012-05-19 07:51:24.312676',NULL,NULL,0,71,3);
INSERT INTO "grampsdb_eventref" VALUES(80,32,41,1,'2012-05-19 07:51:24.582785',NULL,NULL,0,37,3);
INSERT INTO "grampsdb_eventref" VALUES(81,32,42,1,'2012-05-19 07:51:26.167304',NULL,NULL,0,46,3);
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
INSERT INTO "grampsdb_citationref" VALUES(1,36,17,1,'2012-05-19 07:50:04.902644',NULL,NULL,0,1);
INSERT INTO "grampsdb_citationref" VALUES(2,36,85,1,'2012-05-19 07:51:10.799213',NULL,NULL,0,3);
INSERT INTO "grampsdb_citationref" VALUES(3,42,39,1,'2012-05-19 07:51:19.205827',NULL,NULL,0,2);
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
INSERT INTO "grampsdb_childref" VALUES(1,33,2,1,'2012-05-19 07:49:51.294596',NULL,NULL,0,2,2,7);
INSERT INTO "grampsdb_childref" VALUES(2,33,3,1,'2012-05-19 07:49:51.790807',NULL,NULL,0,2,2,31);
INSERT INTO "grampsdb_childref" VALUES(3,33,4,1,'2012-05-19 07:50:04.358764',NULL,NULL,0,3,3,13);
INSERT INTO "grampsdb_childref" VALUES(4,33,6,1,'2012-05-19 07:50:12.848083',NULL,NULL,0,2,2,32);
INSERT INTO "grampsdb_childref" VALUES(5,33,7,1,'2012-05-19 07:50:19.830608',NULL,NULL,0,2,2,20);
INSERT INTO "grampsdb_childref" VALUES(6,33,8,1,'2012-05-19 07:50:23.875476',NULL,NULL,0,2,2,39);
INSERT INTO "grampsdb_childref" VALUES(7,33,10,1,'2012-05-19 07:50:35.067361',NULL,NULL,0,2,2,3);
INSERT INTO "grampsdb_childref" VALUES(8,33,11,1,'2012-05-19 07:50:41.740891',NULL,NULL,0,2,2,24);
INSERT INTO "grampsdb_childref" VALUES(9,33,12,1,'2012-05-19 07:50:52.427365',NULL,NULL,0,2,2,16);
INSERT INTO "grampsdb_childref" VALUES(10,33,14,1,'2012-05-19 07:51:15.473547',NULL,NULL,0,2,2,1);
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
