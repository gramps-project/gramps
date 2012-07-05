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
INSERT INTO "auth_permission" VALUES(151,'Can add log',51,'add_log');
INSERT INTO "auth_permission" VALUES(152,'Can change log',51,'change_log');
INSERT INTO "auth_permission" VALUES(153,'Can delete log',51,'delete_log');
INSERT INTO "auth_permission" VALUES(154,'Can add note ref',52,'add_noteref');
INSERT INTO "auth_permission" VALUES(155,'Can change note ref',52,'change_noteref');
INSERT INTO "auth_permission" VALUES(156,'Can delete note ref',52,'delete_noteref');
INSERT INTO "auth_permission" VALUES(157,'Can add event ref',53,'add_eventref');
INSERT INTO "auth_permission" VALUES(158,'Can change event ref',53,'change_eventref');
INSERT INTO "auth_permission" VALUES(159,'Can delete event ref',53,'delete_eventref');
INSERT INTO "auth_permission" VALUES(160,'Can add repository ref',54,'add_repositoryref');
INSERT INTO "auth_permission" VALUES(161,'Can change repository ref',54,'change_repositoryref');
INSERT INTO "auth_permission" VALUES(162,'Can delete repository ref',54,'delete_repositoryref');
INSERT INTO "auth_permission" VALUES(163,'Can add person ref',55,'add_personref');
INSERT INTO "auth_permission" VALUES(164,'Can change person ref',55,'change_personref');
INSERT INTO "auth_permission" VALUES(165,'Can delete person ref',55,'delete_personref');
INSERT INTO "auth_permission" VALUES(166,'Can add citation ref',56,'add_citationref');
INSERT INTO "auth_permission" VALUES(167,'Can change citation ref',56,'change_citationref');
INSERT INTO "auth_permission" VALUES(168,'Can delete citation ref',56,'delete_citationref');
INSERT INTO "auth_permission" VALUES(169,'Can add child ref',57,'add_childref');
INSERT INTO "auth_permission" VALUES(170,'Can change child ref',57,'change_childref');
INSERT INTO "auth_permission" VALUES(171,'Can delete child ref',57,'delete_childref');
INSERT INTO "auth_permission" VALUES(172,'Can add media ref',58,'add_mediaref');
INSERT INTO "auth_permission" VALUES(173,'Can change media ref',58,'change_mediaref');
INSERT INTO "auth_permission" VALUES(174,'Can delete media ref',58,'delete_mediaref');
INSERT INTO "auth_permission" VALUES(175,'Can add report',59,'add_report');
INSERT INTO "auth_permission" VALUES(176,'Can change report',59,'change_report');
INSERT INTO "auth_permission" VALUES(177,'Can delete report',59,'delete_report');
INSERT INTO "auth_permission" VALUES(178,'Can add result',60,'add_result');
INSERT INTO "auth_permission" VALUES(179,'Can change result',60,'change_result');
INSERT INTO "auth_permission" VALUES(180,'Can delete result',60,'delete_result');
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
INSERT INTO "auth_user" VALUES(1,'admin','','','bugs@gramps-project.org','sha1$c0530$7b8073dafe9c593d9fc0eeb4f66fd29ecaa34fc9',1,1,1,'2012-06-18 21:41:58.429589','2012-06-18 21:41:28.784226');
INSERT INTO "auth_user" VALUES(2,'admin1','','','bugs@gramps-project.org','sha1$10aef$4b8e70520ce6df429f449c36e0f732a5110b8a8d',0,1,0,'2012-06-18 21:45:47.430118','2012-06-18 21:41:33');
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
INSERT INTO "django_content_type" VALUES(51,'log','grampsdb','log');
INSERT INTO "django_content_type" VALUES(52,'note ref','grampsdb','noteref');
INSERT INTO "django_content_type" VALUES(53,'event ref','grampsdb','eventref');
INSERT INTO "django_content_type" VALUES(54,'repository ref','grampsdb','repositoryref');
INSERT INTO "django_content_type" VALUES(55,'person ref','grampsdb','personref');
INSERT INTO "django_content_type" VALUES(56,'citation ref','grampsdb','citationref');
INSERT INTO "django_content_type" VALUES(57,'child ref','grampsdb','childref');
INSERT INTO "django_content_type" VALUES(58,'media ref','grampsdb','mediaref');
INSERT INTO "django_content_type" VALUES(59,'report','grampsdb','report');
INSERT INTO "django_content_type" VALUES(60,'result','grampsdb','result');
CREATE TABLE "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" datetime NOT NULL
);
INSERT INTO "django_session" VALUES('37aec6a13380b1a305f86c1265f832cf','YTJkY2YzOGM0MzQ0MzY4YjExZDZhODZjOTdhZjAxMDkxNWU5MTM0NjqAAn1xAS4=
','2012-07-02 21:46:10.607056');
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
INSERT INTO "django_admin_log" VALUES(1,'2012-06-18 21:43:45.466702',1,3,'2','admin1',2,'Changed is_staff and is_superuser.');
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
    "setting" varchar(25) NOT NULL,
    "description" text NOT NULL,
    "value_type" varchar(25) NOT NULL,
    "value" text NOT NULL
);
INSERT INTO "grampsdb_config" VALUES(1,'sitename','site name of family tree','str','Gramps-Connect');
INSERT INTO "grampsdb_config" VALUES(2,'db_version','database scheme version','str','0.6.1');
INSERT INTO "grampsdb_config" VALUES(3,'db_created','database creation date/time','str','2012-06-18 21:40');
INSERT INTO "grampsdb_config" VALUES(4,'htmlview.url-handler','','bool','False');
INSERT INTO "grampsdb_config" VALUES(5,'htmlview.start-url','','str','http://gramps-project.org');
INSERT INTO "grampsdb_config" VALUES(6,'paths.recent-export-dir','','str','');
INSERT INTO "grampsdb_config" VALUES(7,'paths.report-directory','','unicode','/home/dblank');
INSERT INTO "grampsdb_config" VALUES(8,'paths.quick-backup-filename','','str','%(filename)s_%(year)d-%(month)02d-%(day)02d.%(extension)s');
INSERT INTO "grampsdb_config" VALUES(9,'paths.recent-import-dir','','str','');
INSERT INTO "grampsdb_config" VALUES(10,'paths.quick-backup-directory','','unicode','/home/dblank');
INSERT INTO "grampsdb_config" VALUES(11,'paths.recent-file','','str','');
INSERT INTO "grampsdb_config" VALUES(12,'paths.website-directory','','unicode','/home/dblank');
INSERT INTO "grampsdb_config" VALUES(13,'preferences.family-warn','','bool','True');
INSERT INTO "grampsdb_config" VALUES(14,'preferences.no-surname-text','','unicode','[Missing Surname]');
INSERT INTO "grampsdb_config" VALUES(15,'preferences.family-relation-type','','int','3');
INSERT INTO "grampsdb_config" VALUES(16,'preferences.private-surname-text','','unicode','[Living]');
INSERT INTO "grampsdb_config" VALUES(17,'preferences.fprefix','','str','F%04d');
INSERT INTO "grampsdb_config" VALUES(18,'preferences.default-source','','bool','False');
INSERT INTO "grampsdb_config" VALUES(19,'preferences.calendar-format-report','','int','0');
INSERT INTO "grampsdb_config" VALUES(20,'preferences.oprefix','','str','O%04d');
INSERT INTO "grampsdb_config" VALUES(21,'preferences.nprefix','','str','N%04d');
INSERT INTO "grampsdb_config" VALUES(22,'preferences.use-last-view','','bool','True');
INSERT INTO "grampsdb_config" VALUES(23,'preferences.paper-preference','','str','Letter');
INSERT INTO "grampsdb_config" VALUES(24,'preferences.use-bsddb3','','bool','False');
INSERT INTO "grampsdb_config" VALUES(25,'preferences.hide-ep-msg','','bool','False');
INSERT INTO "grampsdb_config" VALUES(26,'preferences.iprefix','','str','I%04d');
INSERT INTO "grampsdb_config" VALUES(27,'preferences.rprefix','','str','R%04d');
INSERT INTO "grampsdb_config" VALUES(28,'preferences.sprefix','','str','S%04d');
INSERT INTO "grampsdb_config" VALUES(29,'preferences.no-given-text','','unicode','[Missing Given Name]');
INSERT INTO "grampsdb_config" VALUES(30,'preferences.paper-metric','','int','0');
INSERT INTO "grampsdb_config" VALUES(31,'preferences.age-display-precision','','int','1');
INSERT INTO "grampsdb_config" VALUES(32,'preferences.cprefix','','str','C%04d');
INSERT INTO "grampsdb_config" VALUES(33,'preferences.invalid-date-format','','str','<b>%s</b>');
INSERT INTO "grampsdb_config" VALUES(34,'preferences.last-views','','list','[]');
INSERT INTO "grampsdb_config" VALUES(35,'preferences.pprefix','','str','P%04d');
INSERT INTO "grampsdb_config" VALUES(36,'preferences.eprefix','','str','E%04d');
INSERT INTO "grampsdb_config" VALUES(37,'preferences.name-format','','int','1');
INSERT INTO "grampsdb_config" VALUES(38,'preferences.private-record-text','','unicode','[Private Record]');
INSERT INTO "grampsdb_config" VALUES(39,'preferences.online-maps','','bool','False');
INSERT INTO "grampsdb_config" VALUES(40,'preferences.no-record-text','','unicode','[Missing Record]');
INSERT INTO "grampsdb_config" VALUES(41,'preferences.date-format','','int','0');
INSERT INTO "grampsdb_config" VALUES(42,'preferences.last-view','','str','');
INSERT INTO "grampsdb_config" VALUES(43,'preferences.patronimic-surname','','bool','False');
INSERT INTO "grampsdb_config" VALUES(44,'preferences.private-given-text','','unicode','[Living]');
INSERT INTO "grampsdb_config" VALUES(45,'plugin.hiddenplugins','','list','[''htmlview'']');
INSERT INTO "grampsdb_config" VALUES(46,'plugin.addonplugins','','list','[]');
INSERT INTO "grampsdb_config" VALUES(47,'researcher.researcher-locality','','str','');
INSERT INTO "grampsdb_config" VALUES(48,'researcher.researcher-country','','str','');
INSERT INTO "grampsdb_config" VALUES(49,'researcher.researcher-name','','str','');
INSERT INTO "grampsdb_config" VALUES(50,'researcher.researcher-phone','','str','');
INSERT INTO "grampsdb_config" VALUES(51,'researcher.researcher-email','','str','');
INSERT INTO "grampsdb_config" VALUES(52,'researcher.researcher-state','','str','');
INSERT INTO "grampsdb_config" VALUES(53,'researcher.researcher-postal','','str','');
INSERT INTO "grampsdb_config" VALUES(54,'researcher.researcher-city','','str','');
INSERT INTO "grampsdb_config" VALUES(55,'researcher.researcher-addr','','str','');
INSERT INTO "grampsdb_config" VALUES(56,'export.proxy-order','','list','[[''privacy'', 0], [''living'', 0], [''person'', 0], [''note'', 0], [''reference'', 0]]');
INSERT INTO "grampsdb_config" VALUES(57,'behavior.use-tips','','bool','False');
INSERT INTO "grampsdb_config" VALUES(58,'behavior.generation-depth','','int','15');
INSERT INTO "grampsdb_config" VALUES(59,'behavior.last-check-for-updates','','str','1970/01/01');
INSERT INTO "grampsdb_config" VALUES(60,'behavior.startup','','int','0');
INSERT INTO "grampsdb_config" VALUES(61,'behavior.autoload','','bool','False');
INSERT INTO "grampsdb_config" VALUES(62,'behavior.pop-plugin-status','','bool','False');
INSERT INTO "grampsdb_config" VALUES(63,'behavior.do-not-show-previously-seen-updates','','bool','True');
INSERT INTO "grampsdb_config" VALUES(64,'behavior.check-for-updates','','int','0');
INSERT INTO "grampsdb_config" VALUES(65,'behavior.recent-export-type','','int','1');
INSERT INTO "grampsdb_config" VALUES(66,'behavior.addmedia-image-dir','','str','');
INSERT INTO "grampsdb_config" VALUES(67,'behavior.date-about-range','','int','50');
INSERT INTO "grampsdb_config" VALUES(68,'behavior.date-after-range','','int','50');
INSERT INTO "grampsdb_config" VALUES(69,'behavior.owner-warn','','bool','False');
INSERT INTO "grampsdb_config" VALUES(70,'behavior.date-before-range','','int','50');
INSERT INTO "grampsdb_config" VALUES(71,'behavior.min-generation-years','','int','13');
INSERT INTO "grampsdb_config" VALUES(72,'behavior.welcome','','int','100');
INSERT INTO "grampsdb_config" VALUES(73,'behavior.max-sib-age-diff','','int','20');
INSERT INTO "grampsdb_config" VALUES(74,'behavior.previously-seen-updates','','list','[]');
INSERT INTO "grampsdb_config" VALUES(75,'behavior.addmedia-relative-path','','bool','False');
INSERT INTO "grampsdb_config" VALUES(76,'behavior.spellcheck','','bool','False');
INSERT INTO "grampsdb_config" VALUES(77,'behavior.surname-guessing','','int','0');
INSERT INTO "grampsdb_config" VALUES(78,'behavior.check-for-update-types','','list','[''new'']');
INSERT INTO "grampsdb_config" VALUES(79,'behavior.avg-generation-gap','','int','20');
INSERT INTO "grampsdb_config" VALUES(80,'behavior.database-path','','unicode','/home/dblank/.gramps/grampsdb');
INSERT INTO "grampsdb_config" VALUES(81,'behavior.betawarn','','bool','False');
INSERT INTO "grampsdb_config" VALUES(82,'behavior.max-age-prob-alive','','int','110');
INSERT INTO "grampsdb_config" VALUES(83,'behavior.web-search-url','','str','http://google.com/#&q=%(text)s');
INSERT INTO "grampsdb_config" VALUES(84,'interface.family-height','','int','500');
INSERT INTO "grampsdb_config" VALUES(85,'interface.sidebar-text','','bool','True');
INSERT INTO "grampsdb_config" VALUES(86,'interface.source-ref-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(87,'interface.address-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(88,'interface.mapservice','','str','OpenStreetMap');
INSERT INTO "grampsdb_config" VALUES(89,'interface.pedview-layout','','int','0');
INSERT INTO "grampsdb_config" VALUES(90,'interface.family-width','','int','700');
INSERT INTO "grampsdb_config" VALUES(91,'interface.toolbar-on','','bool','True');
INSERT INTO "grampsdb_config" VALUES(92,'interface.citation-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(93,'interface.location-height','','int','250');
INSERT INTO "grampsdb_config" VALUES(94,'interface.person-ref-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(95,'interface.address-width','','int','650');
INSERT INTO "grampsdb_config" VALUES(96,'interface.edit-rule-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(97,'interface.filter-editor-width','','int','400');
INSERT INTO "grampsdb_config" VALUES(98,'interface.child-ref-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(99,'interface.person-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(100,'interface.repo-width','','int','650');
INSERT INTO "grampsdb_config" VALUES(101,'interface.pedview-tree-size','','int','5');
INSERT INTO "grampsdb_config" VALUES(102,'interface.citation-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(103,'interface.edit-rule-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(104,'interface.place-width','','int','650');
INSERT INTO "grampsdb_config" VALUES(105,'interface.place-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(106,'interface.source-ref-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(107,'interface.repo-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(108,'interface.source-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(109,'interface.clipboard-height','','int','300');
INSERT INTO "grampsdb_config" VALUES(110,'interface.fullscreen','','bool','False');
INSERT INTO "grampsdb_config" VALUES(111,'interface.attribute-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(112,'interface.lds-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(113,'interface.edit-filter-width','','int','500');
INSERT INTO "grampsdb_config" VALUES(114,'interface.clipboard-width','','int','300');
INSERT INTO "grampsdb_config" VALUES(115,'interface.media-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(116,'interface.person-ref-height','','int','350');
INSERT INTO "grampsdb_config" VALUES(117,'interface.citation-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(118,'interface.person-width','','int','750');
INSERT INTO "grampsdb_config" VALUES(119,'interface.lds-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(120,'interface.name-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(121,'interface.event-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(122,'interface.child-ref-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(123,'interface.filter','','bool','False');
INSERT INTO "grampsdb_config" VALUES(124,'interface.view','','bool','True');
INSERT INTO "grampsdb_config" VALUES(125,'interface.media-ref-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(126,'interface.family-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(127,'interface.pedview-show-marriage','','bool','False');
INSERT INTO "grampsdb_config" VALUES(128,'interface.height','','int','500');
INSERT INTO "grampsdb_config" VALUES(129,'interface.media-width','','int','650');
INSERT INTO "grampsdb_config" VALUES(130,'interface.event-ref-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(131,'interface.repo-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(132,'interface.media-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(133,'interface.width','','int','775');
INSERT INTO "grampsdb_config" VALUES(134,'interface.size-checked','','bool','False');
INSERT INTO "grampsdb_config" VALUES(135,'interface.media-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(136,'interface.source-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(137,'interface.surname-box-height','','int','150');
INSERT INTO "grampsdb_config" VALUES(138,'interface.repo-ref-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(139,'interface.name-height','','int','350');
INSERT INTO "grampsdb_config" VALUES(140,'interface.event-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(141,'interface.note-width','','int','700');
INSERT INTO "grampsdb_config" VALUES(142,'interface.statusbar','','int','1');
INSERT INTO "grampsdb_config" VALUES(143,'interface.person-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(144,'interface.note-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(145,'interface.view-categories','','list','[''Gramplets'', ''People'', ''Relationships'', ''Families'', ''Ancestry'', ''Events'', ''Places'', ''Geography'', ''Sources'', ''Citations'', ''Repositories'', ''Media'', ''Notes'']');
INSERT INTO "grampsdb_config" VALUES(146,'interface.repo-ref-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(147,'interface.event-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(148,'interface.note-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(149,'interface.person-height','','int','550');
INSERT INTO "grampsdb_config" VALUES(150,'interface.repo-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(151,'interface.attribute-height','','int','350');
INSERT INTO "grampsdb_config" VALUES(152,'interface.event-ref-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(153,'interface.source-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(154,'interface.edit-filter-height','','int','420');
INSERT INTO "grampsdb_config" VALUES(155,'interface.pedview-tree-direction','','int','2');
INSERT INTO "grampsdb_config" VALUES(156,'interface.family-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(157,'interface.source-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(158,'interface.url-height','','int','150');
INSERT INTO "grampsdb_config" VALUES(159,'interface.filter-editor-height','','int','350');
INSERT INTO "grampsdb_config" VALUES(160,'interface.media-ref-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(161,'interface.pedview-show-unknown-people','','bool','False');
INSERT INTO "grampsdb_config" VALUES(162,'interface.location-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(163,'interface.place-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(164,'interface.citation-sel-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(165,'interface.pedview-show-images','','bool','True');
INSERT INTO "grampsdb_config" VALUES(166,'interface.url-width','','int','600');
INSERT INTO "grampsdb_config" VALUES(167,'interface.event-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(168,'interface.note-height','','int','500');
INSERT INTO "grampsdb_config" VALUES(169,'interface.open-with-default-viewer','','bool','False');
INSERT INTO "grampsdb_config" VALUES(170,'interface.place-sel-height','','int','450');
INSERT INTO "grampsdb_config" VALUES(171,'interface.dont-ask','','bool','False');
INSERT INTO "grampsdb_config" VALUES(172,'geography.map','','str','person');
INSERT INTO "grampsdb_config" VALUES(173,'geography.zoom_when_center','','int','12');
INSERT INTO "grampsdb_config" VALUES(174,'geography.center-lon','','float','0.0');
INSERT INTO "grampsdb_config" VALUES(175,'geography.show_cross','','bool','False');
INSERT INTO "grampsdb_config" VALUES(176,'geography.zoom','','int','0');
INSERT INTO "grampsdb_config" VALUES(177,'geography.map_service','','int','1');
INSERT INTO "grampsdb_config" VALUES(178,'geography.lock','','bool','False');
INSERT INTO "grampsdb_config" VALUES(179,'geography.path','','str','');
INSERT INTO "grampsdb_config" VALUES(180,'geography.center-lat','','float','0.0');
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
INSERT INTO "grampsdb_person_families" VALUES(1,1,14);
INSERT INTO "grampsdb_person_families" VALUES(2,2,15);
INSERT INTO "grampsdb_person_families" VALUES(3,3,13);
INSERT INTO "grampsdb_person_families" VALUES(4,4,10);
INSERT INTO "grampsdb_person_families" VALUES(5,5,2);
INSERT INTO "grampsdb_person_families" VALUES(6,8,18);
INSERT INTO "grampsdb_person_families" VALUES(7,15,17);
INSERT INTO "grampsdb_person_families" VALUES(8,20,11);
INSERT INTO "grampsdb_person_families" VALUES(9,21,19);
INSERT INTO "grampsdb_person_families" VALUES(10,24,17);
INSERT INTO "grampsdb_person_families" VALUES(11,25,6);
INSERT INTO "grampsdb_person_families" VALUES(12,27,7);
INSERT INTO "grampsdb_person_families" VALUES(13,29,1);
INSERT INTO "grampsdb_person_families" VALUES(14,30,7);
INSERT INTO "grampsdb_person_families" VALUES(15,31,16);
INSERT INTO "grampsdb_person_families" VALUES(16,32,8);
INSERT INTO "grampsdb_person_families" VALUES(17,37,14);
INSERT INTO "grampsdb_person_families" VALUES(18,38,4);
INSERT INTO "grampsdb_person_families" VALUES(19,39,3);
INSERT INTO "grampsdb_person_families" VALUES(20,40,8);
INSERT INTO "grampsdb_person_families" VALUES(21,42,10);
INSERT INTO "grampsdb_person_families" VALUES(22,46,5);
INSERT INTO "grampsdb_person_families" VALUES(23,47,19);
INSERT INTO "grampsdb_person_families" VALUES(24,48,11);
INSERT INTO "grampsdb_person_families" VALUES(25,50,5);
INSERT INTO "grampsdb_person_families" VALUES(26,52,16);
INSERT INTO "grampsdb_person_families" VALUES(27,53,18);
INSERT INTO "grampsdb_person_families" VALUES(28,53,13);
INSERT INTO "grampsdb_person_families" VALUES(29,54,15);
INSERT INTO "grampsdb_person_families" VALUES(30,57,9);
INSERT INTO "grampsdb_person_families" VALUES(31,58,4);
INSERT INTO "grampsdb_person_families" VALUES(32,59,2);
INSERT INTO "grampsdb_person_families" VALUES(33,60,9);
INSERT INTO "grampsdb_person_families" VALUES(34,60,6);
INSERT INTO "grampsdb_person_families" VALUES(35,63,3);
INSERT INTO "grampsdb_person_families" VALUES(36,65,12);
INSERT INTO "grampsdb_person_families" VALUES(37,68,1);
INSERT INTO "grampsdb_person_families" VALUES(38,69,12);
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
INSERT INTO "grampsdb_person_parent_families" VALUES(1,2,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(2,3,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(3,4,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(4,6,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(5,7,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(6,9,17);
INSERT INTO "grampsdb_person_parent_families" VALUES(7,10,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(8,11,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(9,12,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(10,13,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(11,14,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(12,16,9);
INSERT INTO "grampsdb_person_parent_families" VALUES(13,17,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(14,18,17);
INSERT INTO "grampsdb_person_parent_families" VALUES(15,19,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(16,21,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(17,22,5);
INSERT INTO "grampsdb_person_parent_families" VALUES(18,23,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(19,24,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(20,26,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(21,27,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(22,28,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(23,30,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(24,31,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(25,33,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(26,34,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(27,35,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(28,36,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(29,38,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(30,39,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(31,41,5);
INSERT INTO "grampsdb_person_parent_families" VALUES(32,43,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(33,44,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(34,45,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(35,48,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(36,49,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(37,50,7);
INSERT INTO "grampsdb_person_parent_families" VALUES(38,51,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(39,53,9);
INSERT INTO "grampsdb_person_parent_families" VALUES(40,55,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(41,56,12);
INSERT INTO "grampsdb_person_parent_families" VALUES(42,59,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(43,61,19);
INSERT INTO "grampsdb_person_parent_families" VALUES(44,62,17);
INSERT INTO "grampsdb_person_parent_families" VALUES(45,64,5);
INSERT INTO "grampsdb_person_parent_families" VALUES(46,66,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(47,67,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(48,68,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(49,69,7);
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
INSERT INTO "grampsdb_person" VALUES(1,'c30181e535d5ebdb004','I0050','2012-06-18 21:44:27.007428','1994-11-03 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(2,'c30181e4ce741e3fa73','I0016','2012-06-18 21:44:27.144104','1969-12-31 19:00:00',NULL,0,NULL,3,1,119,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(3,'c30181e538e3a266f35','I0052','2012-06-18 21:44:27.287829','1995-04-29 00:00:00',NULL,0,NULL,2,0,118,19,0,1);
INSERT INTO "grampsdb_person" VALUES(4,'c30181e560b10fa403b','I0061','2012-06-18 21:44:27.419876','1994-05-27 00:00:00',NULL,0,NULL,3,1,68,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(5,'c30181e55a51f84bcdd','I0058','2012-06-18 21:44:27.545303','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(6,'c30181e4c66344d6b59','I0013','2012-06-18 21:44:27.679179','1969-12-31 19:00:00',NULL,0,NULL,2,1,67,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(7,'c30181e4a2c5bde9756','I0003','2012-06-18 21:44:27.956302','1994-05-29 00:00:00',NULL,0,NULL,2,0,123,63,1,2);
INSERT INTO "grampsdb_person" VALUES(8,'c30181e55bb4f5e7604','I0059','2012-06-18 21:44:28.088196','1994-05-29 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(9,'c30181e51582203951a','I0041','2012-06-18 21:44:28.221928','1969-12-31 19:00:00',NULL,0,NULL,3,1,24,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(10,'c30181e4f48333a0c57','I0030','2012-06-18 21:44:28.364165','1969-12-31 19:00:00',NULL,0,NULL,2,1,121,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(11,'c30181e4d8741e88bbb','I0020','2012-06-18 21:44:28.506923','1969-12-31 19:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(12,'c30181e563833367261','I0062','2012-06-18 21:44:28.642500','1994-05-27 00:00:00',NULL,0,NULL,2,0,21,64,0,1);
INSERT INTO "grampsdb_person" VALUES(13,'c30181e4d202bb7606a','I0017','2012-06-18 21:44:28.766293','1969-12-31 19:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(14,'c30181e4e7d52d85569','I0025','2012-06-18 21:44:28.900054','1969-12-31 19:00:00',NULL,0,NULL,2,1,73,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(15,'c30181e513f2620d344','I0040','2012-06-18 21:44:29.033576','1994-05-29 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(16,'c30181e57345dfeb38d','I0068','2012-06-18 21:44:29.167327','1994-05-27 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(17,'c30181e4a9200f276fc','I0004','2012-06-18 21:44:29.301255','1996-01-23 00:00:00',NULL,0,NULL,3,1,41,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(18,'c30181e517e1b2362a7','I0042','2012-06-18 21:44:29.434837','1969-12-31 19:00:00',NULL,0,NULL,2,1,113,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(19,'c30181e54a50cd16251','I0054','2012-06-18 21:44:29.576814','1994-05-29 00:00:00',NULL,0,NULL,3,1,95,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(20,'c30181e56ca410c2657','I0065','2012-06-18 21:44:29.711463','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(21,'c30181e4da97c2c0892','I0021','2012-06-18 21:44:29.847144','1994-05-29 00:00:00',NULL,0,NULL,2,0,124,125,0,1);
INSERT INTO "grampsdb_person" VALUES(22,'c30181e50d12404b391','I0038','2012-06-18 21:44:29.970892','1969-12-31 19:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(23,'c30181e4d6503fbab95','I0019','2012-06-18 21:44:30.112742','1969-12-31 19:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(24,'c30181e50f35512fd74','I0039','2012-06-18 21:44:30.246424','1994-05-29 00:00:00',NULL,0,NULL,2,1,70,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(25,'c30181e575d2a16862f','I0069','2012-06-18 21:44:30.380129','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(26,'c30181e4fb65b64e169','I0032','2012-06-18 21:44:30.513934','1969-12-31 19:00:00',NULL,0,NULL,2,1,128,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(27,'c30181e49a8263cfd55','I0002','2012-06-18 21:44:30.649349','1995-01-26 00:00:00',NULL,0,NULL,3,0,139,78,0,1);
INSERT INTO "grampsdb_person" VALUES(28,'c30181e4fee6bca5abf','I0033','2012-06-18 21:44:30.781420','1969-12-31 19:00:00',NULL,0,NULL,3,1,112,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(29,'c30181e56e25e112620','I0066','2012-06-18 21:44:30.907888','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(30,'c30181e48f33c0c82ae','I0001','2012-06-18 21:44:31.035144','1995-01-26 00:00:00',NULL,0,NULL,2,0,48,4,0,1);
INSERT INTO "grampsdb_person" VALUES(31,'c30181e4b04289ee499','I0006','2012-06-18 21:44:31.168652','1994-05-27 00:00:00',NULL,0,NULL,3,0,36,32,0,1);
INSERT INTO "grampsdb_person" VALUES(32,'c30181e524f2f0d0185','I0046','2012-06-18 21:44:31.302418','1994-10-16 00:00:00',NULL,0,NULL,2,0,140,44,0,1);
INSERT INTO "grampsdb_person" VALUES(33,'c30181e5535600afb6d','I0056','2012-06-18 21:44:31.436364','1969-12-31 19:00:00',NULL,0,NULL,2,0,27,138,0,1);
INSERT INTO "grampsdb_person" VALUES(34,'c30181e4f801f1cd999','I0031','2012-06-18 21:44:31.568239','1969-12-31 19:00:00',NULL,0,NULL,2,1,133,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(35,'c30181e4bda64b67fc2','I0009','2012-06-18 21:44:31.702026','1969-12-31 19:00:00',NULL,0,NULL,2,1,144,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(36,'c30181e4c434cf2456c','I0012','2012-06-18 21:44:31.844201','1969-12-31 19:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(37,'c30181e5378053b965e','I0051','2012-06-18 21:44:31.977889','1994-11-03 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(38,'c30181e4c1b677ed2b1','I0011','2012-06-18 21:44:32.111460','1994-06-30 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(39,'c30181e51d020c99a60','I0044','2012-06-18 21:44:32.248085','1994-05-29 00:00:00',NULL,0,NULL,2,0,103,94,0,1);
INSERT INTO "grampsdb_person" VALUES(40,'c30181e52a83c428ed5','I0047','2012-06-18 21:44:32.381797','1994-10-16 00:00:00',NULL,0,NULL,3,0,57,77,0,1);
INSERT INTO "grampsdb_person" VALUES(41,'c30181e507b0fa099ba','I0036','2012-06-18 21:44:32.513836','1969-12-31 19:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(42,'c30181e56b1191a3720','I0064','2012-06-18 21:44:32.647382','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(43,'c30181e4f1c1e2b4737','I0029','2012-06-18 21:44:32.781001','1969-12-31 19:00:00',NULL,0,NULL,3,1,81,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(44,'c30181e56fb11fbeea6','I0067','2012-06-18 21:44:32.914975','1994-05-27 00:00:00',NULL,0,NULL,3,1,91,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(45,'c30181e4e577ded1337','I0024','2012-06-18 21:44:33.048746','1969-12-31 19:00:00',NULL,0,NULL,2,1,135,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(46,'c30181e5028607ecc73','I0034','2012-06-18 21:44:33.174205','1969-12-31 19:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(47,'c30181e4e1b6981809d','I0022','2012-06-18 21:44:33.299587','1969-12-31 19:00:00',NULL,0,NULL,3,1,83,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(48,'c30181e56750f5540a3','I0063','2012-06-18 21:44:33.434032','1994-05-27 00:00:00',NULL,0,NULL,3,1,10,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(49,'c30181e4e3238a80483','I0023','2012-06-18 21:44:33.568012','1969-12-31 19:00:00',NULL,0,NULL,3,1,60,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(50,'c30181e503c2ca35ed9','I0035','2012-06-18 21:44:33.710869','1994-05-29 00:00:00',NULL,0,NULL,3,1,86,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(51,'c30181e4ecc53881846','I0027','2012-06-18 21:44:33.844085','1969-12-31 19:00:00',NULL,0,NULL,3,1,43,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(52,'c30181e4adc5c16c637','I0005','2012-06-18 21:44:34.005846','1969-12-31 19:00:00',NULL,0,NULL,2,0,23,29,0,1);
INSERT INTO "grampsdb_person" VALUES(53,'c30181e541b2e7cbb85','I0053','2012-06-18 21:44:34.172122','1994-05-29 00:00:00',NULL,0,NULL,3,0,37,42,0,1);
INSERT INTO "grampsdb_person" VALUES(54,'c30181e4cd050176a7c','I0015','2012-06-18 21:44:34.304042','1969-12-31 19:00:00',NULL,0,NULL,2,1,7,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(55,'c30181e4ea50fae3132','I0026','2012-06-18 21:44:34.437812','1969-12-31 19:00:00',NULL,0,NULL,2,1,96,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(56,'c30181e4c9a4de4acbb','I0014','2012-06-18 21:44:34.563242','1969-12-31 19:00:00',NULL,0,NULL,2,1,2,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(57,'c30181e52ee3b3e79a3','I0048','2012-06-18 21:44:34.699687','1994-06-30 00:00:00',NULL,0,NULL,2,0,NULL,101,-1,1);
INSERT INTO "grampsdb_person" VALUES(58,'c30181e4c0109979a61','I0010','2012-06-18 21:44:34.832135','1994-10-16 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(59,'c30181e557a52efa5da','I0057','2012-06-18 21:44:34.974194','1994-05-27 00:00:00',NULL,0,NULL,3,1,102,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(60,'c30181e534251f77dd2','I0049','2012-06-18 21:44:35.107405','1994-05-27 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(61,'c30181e4ef475b4a36d','I0028','2012-06-18 21:44:35.241237','1969-12-31 19:00:00',NULL,0,NULL,2,1,54,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(62,'c30181e51aa7c8661a3','I0043','2012-06-18 21:44:35.374936','1969-12-31 19:00:00',NULL,0,NULL,2,1,109,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(63,'c30181e523374ece98b','I0045','2012-06-18 21:44:35.751494','1994-05-29 00:00:00',NULL,0,NULL,3,0,NULL,99,-1,0);
INSERT INTO "grampsdb_person" VALUES(64,'c30181e509c100ee2b1','I0037','2012-06-18 21:44:35.883376','1969-12-31 19:00:00',NULL,0,NULL,2,1,1,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(65,'c30181e4b611ebce47a','I0007','2012-06-18 21:44:36.033738','1994-05-27 00:00:00',NULL,0,NULL,2,1,40,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(66,'c30181e54f47d176b2a','I0055','2012-06-18 21:44:36.168422','1995-04-29 00:00:00',NULL,0,NULL,2,1,38,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(67,'c30181e4d437b7664ed','I0018','2012-06-18 21:44:36.302050','1969-12-31 19:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(68,'c30181e55d23cb0928f','I0060','2012-06-18 21:44:36.435813','1994-05-27 00:00:00',NULL,0,NULL,3,1,17,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(69,'c30181e4b8e670156ec','I0008','2012-06-18 21:44:36.569528','1969-12-31 19:00:00',NULL,0,NULL,3,1,20,NULL,0,-1);
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
INSERT INTO "grampsdb_family" VALUES(1,'c30181e55e70c81bfe8','F0016','2012-06-18 21:44:21.776185','1969-12-31 19:00:00',NULL,0,NULL,29,68,5);
INSERT INTO "grampsdb_family" VALUES(2,'c30181e5582444c0bf3','F0014','2012-06-18 21:44:22.713264','1969-12-31 19:00:00',NULL,0,NULL,5,59,5);
INSERT INTO "grampsdb_family" VALUES(3,'c30181e49645bf7aa16','F0009','2012-06-18 21:44:22.964227','1969-12-31 19:00:00',NULL,0,NULL,39,63,5);
INSERT INTO "grampsdb_family" VALUES(4,'c30181e4c0709538bc4','F0004','2012-06-18 21:44:22.996128','1969-12-31 19:00:00',NULL,0,NULL,58,38,5);
INSERT INTO "grampsdb_family" VALUES(5,'c30181e502c5805c157','F0007','2012-06-18 21:44:23.223371','1969-12-31 19:00:00',NULL,0,NULL,46,50,5);
INSERT INTO "grampsdb_family" VALUES(6,'c30181e534921cadd07','F0019','2012-06-18 21:44:23.398452','1969-12-31 19:00:00',NULL,0,NULL,25,60,5);
INSERT INTO "grampsdb_family" VALUES(7,'c30181e496232b6add1','F0001','2012-06-18 21:44:23.417689','1969-12-31 19:00:00',NULL,0,NULL,30,27,5);
INSERT INTO "grampsdb_family" VALUES(8,'c30181e520a53997002','F0010','2012-06-18 21:44:23.563672','1969-12-31 19:00:00',NULL,0,NULL,32,40,5);
INSERT INTO "grampsdb_family" VALUES(9,'c30181e532552ac8f35','F0011','2012-06-18 21:44:23.897917','1969-12-31 19:00:00',NULL,0,NULL,57,60,5);
INSERT INTO "grampsdb_family" VALUES(10,'c30181e5614684141e2','F0017','2012-06-18 21:44:24.211262','1969-12-31 19:00:00',NULL,0,NULL,42,4,5);
INSERT INTO "grampsdb_family" VALUES(11,'c30181e568c79dfa768','F0018','2012-06-18 21:44:24.558084','1969-12-31 19:00:00',NULL,0,NULL,20,48,5);
INSERT INTO "grampsdb_family" VALUES(12,'c30181e4b7a0eb54cf3','F0003','2012-06-18 21:44:24.921302','1969-12-31 19:00:00',NULL,0,NULL,65,69,5);
INSERT INTO "grampsdb_family" VALUES(13,'c30181e53ec11f3aad3','F0013','2012-06-18 21:44:25.126956','1969-12-31 19:00:00',NULL,0,NULL,3,53,5);
INSERT INTO "grampsdb_family" VALUES(14,'c30181e4a0244bca5df','F0012','2012-06-18 21:44:25.269064','1969-12-31 19:00:00',NULL,0,NULL,1,37,5);
INSERT INTO "grampsdb_family" VALUES(15,'c30181e4cd86d1206ce','F0005','2012-06-18 21:44:25.503346','1969-12-31 19:00:00',NULL,0,NULL,54,2,5);
INSERT INTO "grampsdb_family" VALUES(16,'c30181e4af518af27e4','F0002','2012-06-18 21:44:25.980532','1969-12-31 19:00:00',NULL,0,NULL,52,31,5);
INSERT INTO "grampsdb_family" VALUES(17,'c30181e5112348535d9','F0008','2012-06-18 21:44:26.006860','1969-12-31 19:00:00',NULL,0,NULL,24,15,5);
INSERT INTO "grampsdb_family" VALUES(18,'c30181e54772c5ecfaf','F0015','2012-06-18 21:44:26.617589','1969-12-31 19:00:00',NULL,0,NULL,8,53,5);
INSERT INTO "grampsdb_family" VALUES(19,'c30181e4def38b64a89','F0006','2012-06-18 21:44:26.755563','1969-12-31 19:00:00',NULL,0,NULL,21,47,5);
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
INSERT INTO "grampsdb_source" VALUES(1,'c30181e586e58b05f95','S0010','2012-06-18 21:44:20.772518','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0010','','','');
INSERT INTO "grampsdb_source" VALUES(2,'c30181e579127c5333c','S0002','2012-06-18 21:44:20.906119','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0002','','','');
INSERT INTO "grampsdb_source" VALUES(3,'c30181e57c834b373fe','S0004','2012-06-18 21:44:21.081664','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0004','','','');
INSERT INTO "grampsdb_source" VALUES(4,'c30181e58526c2ca5a7','S0009','2012-06-18 21:44:21.187178','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0009','','','');
INSERT INTO "grampsdb_source" VALUES(5,'c30181e581a1a23df61','S0007','2012-06-18 21:44:21.210953','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0007','','','');
INSERT INTO "grampsdb_source" VALUES(6,'c30181e58006dae8fbf','S0006','2012-06-18 21:44:21.425740','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0006','','','');
INSERT INTO "grampsdb_source" VALUES(7,'c30181e58376f39240f','S0008','2012-06-18 21:44:21.451903','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0008','','','');
INSERT INTO "grampsdb_source" VALUES(8,'c30181e577553160493','S0001','2012-06-18 21:44:21.491063','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0001','','','');
INSERT INTO "grampsdb_source" VALUES(9,'c30181e57e33594def8','S0005','2012-06-18 21:44:21.578494','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0005','','','');
INSERT INTO "grampsdb_source" VALUES(10,'c30181e57ac72627de2','S0003','2012-06-18 21:44:21.584269','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0003','','','');
INSERT INTO "grampsdb_source" VALUES(11,'c30181e588935d3ec0c','S0011','2012-06-18 21:44:21.749153','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0011','','','');
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
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,9,1960,0,0,0,0,0,'SEP 1960',2437179,0,1,'c30181e50a064dd1f9f','E0061','2012-06-18 21:44:21.757653','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,7,1965,0,0,0,0,0,'20 JUL 1965',2438962,0,2,'c30181e4c9e3e855a25','E0038','2012-06-18 21:44:21.764377','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1882,0,0,0,0,0,'1882',2408447,0,3,'c30181e5e323afd0bfd','E0142','2012-06-18 21:44:21.789782','1969-12-31 19:00:00',NULL,0,NULL,37,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,11,1969,0,0,0,0,0,'18 NOV 1969',2440544,0,4,'c30181e490e63a65a2b','E0001','2012-06-18 21:44:21.796095','1969-12-31 19:00:00',NULL,0,NULL,5,'',24);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,5,'c30181e52d46c97b1a7','E0087','2012-06-18 21:44:20.762290','1969-12-31 19:00:00',NULL,0,NULL,47,'Her death was caused by a cerebral hemorrhage.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,6,'c30181e5201238e0923','E0072','2012-06-18 21:44:20.765538','1969-12-31 19:00:00',NULL,0,NULL,47,'Meridian St., East Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,9,1923,0,0,0,0,0,'7 SEP 1923',2423670,0,7,'c30181e4cd312bf0464','E0039','2012-06-18 21:44:20.775163','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,8,'c30181e53ca0183ef52','E0099','2012-06-18 21:44:20.786009','1969-12-31 19:00:00',NULL,0,NULL,29,'Senator',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,5,1953,0,0,0,0,0,'23 MAY 1953',2434521,0,9,'c30181e5a5642135eb7','E0131','2012-06-18 21:44:20.793225','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,7,1855,0,0,0,0,0,'18 JUL 1855',2398783,0,10,'c30181e56793471789e','E0124','2012-06-18 21:44:22.296367','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,11,'c30181e4a5907033f73','E0021','2012-06-18 21:44:20.814667','1969-12-31 19:00:00',NULL,0,NULL,47,'He suffered 2 cases of Jaundice during his beginning years a',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,12,'c30181e49e96cfc38b4','E0015','2012-06-18 21:44:20.820795','1969-12-31 19:00:00',NULL,0,NULL,47,'Died of complications due to pneumonia. ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,13,'c30181e4a572e8cf3d4','E0020','2012-06-18 21:44:20.823482','1969-12-31 19:00:00',NULL,0,NULL,18,'Harvard University, Harvard Law School',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,14,'c30181e54f90315f1d4','E0114','2012-06-18 21:44:20.826966','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,15,'c30181e495838a24851','E0008','2012-06-18 21:44:20.836996','1969-12-31 19:00:00',NULL,0,NULL,47,'Palm Beach, FL',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,16,'c30181e49357f186999','E0005','2012-06-18 21:44:20.851765','1969-12-31 19:00:00',NULL,0,NULL,47,'Joe Kennedy was a very hard worker, which often deteriorated',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,8,1851,0,0,0,0,0,'9 AUG 1851',2397344,0,17,'c30181e55d635228327','E0120','2012-06-18 21:44:22.473826','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,18,'c30181e49532f09b472','E0006','2012-06-18 21:44:20.872067','1969-12-31 19:00:00',NULL,0,NULL,47,'Bronxville, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1963,0,0,0,0,0,'22 NOV 1963',2438356,0,19,'c30181e53a658b4c1bf','E0097','2012-06-18 21:44:22.592511','1969-12-31 19:00:00',NULL,0,NULL,5,'',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1921,0,0,0,0,0,'JUL 1921',2422872,0,20,'c30181e4b920f747399','E0031','2012-06-18 21:44:22.598861','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,1,1854,0,0,0,0,0,'4 JAN 1854',2398223,0,21,'c30181e563c0d2c5580','E0122','2012-06-18 21:44:22.606809','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,22,'c30181e527b60dc98cb','E0079','2012-06-18 21:44:20.894569','1969-12-31 19:00:00',NULL,0,NULL,29,'Cooper, Ward Boss',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,12,1917,0,0,0,0,0,'10 DEC 1917',2421573,0,23,'c30181e4ae116d472bf','E0025','2012-06-18 21:44:20.899406','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,3,1960,0,0,0,0,0,'MAR 1960',2436995,0,24,'c30181e515c701f2a9a','E0065','2012-06-18 21:44:20.917350','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,5,1994,0,0,0,0,0,'23 MAY 1994',2449496,0,25,'c30181e544122208a82','E0105','2012-06-18 21:44:22.720724','1969-12-31 19:00:00',NULL,0,NULL,11,'',28);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,26,'c30181e54ce07185a6d','E0112','2012-06-18 21:44:20.927982','1969-12-31 19:00:00',NULL,0,NULL,18,'Brearly School',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,8,1963,0,0,0,0,0,'7 AUG 1963',2438249,0,27,'c30181e553a4c54640e','E0117','2012-06-18 21:44:22.818986','1969-12-31 19:00:00',NULL,0,NULL,4,'',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,28,'c30181e5144566a50dd','E0064','2012-06-18 21:44:20.943161','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,9,1944,0,0,0,0,0,'10 SEP 1944',2431344,0,29,'c30181e4ae46030da52','E0026','2012-06-18 21:44:22.881614','1969-12-31 19:00:00',NULL,0,NULL,5,'',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,30,'c30181e4c1f29b24811','E0036','2012-06-18 21:44:20.950628','1969-12-31 19:00:00',NULL,0,NULL,18,'Georgetown University',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,31,'c30181e4deb39027837','E0045','2012-06-18 21:44:20.953237','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,5,1948,0,0,0,0,0,'13 MAY 1948',2432685,0,32,'c30181e4b1c29fafe65','E0028','2012-06-18 21:44:23.038433','1969-12-31 19:00:00',NULL,0,NULL,5,'',9);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,9,1953,0,0,0,0,0,'12 SEP 1953',2434633,0,33,'c30181e5da829af2ca6','E0139','2012-06-18 21:44:23.153200','1969-12-31 19:00:00',NULL,0,NULL,37,'',26);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,34,'c30181e50523c42e733','E0060','2012-06-18 21:44:20.975209','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,35,'c30181e53e92c5dabfc','E0102','2012-06-18 21:44:20.977828','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1920,0,0,0,0,0,'1920',2422325,0,36,'c30181e4b09236f6b4f','E0027','2012-06-18 21:44:23.189914','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,7,1929,0,0,0,0,0,'28 JUL 1929',2425821,0,37,'c30181e54202bb27193','E0103','2012-06-18 21:44:23.252738','1969-12-31 19:00:00',NULL,0,NULL,4,'',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,11,1960,0,0,0,0,0,'25 NOV 1960',2437264,0,38,'c30181e54fa50dab2cb','E0115','2012-06-18 21:44:23.260499','1969-12-31 19:00:00',NULL,0,NULL,4,'',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,39,'c30181e4a684a1c97e6','E0022','2012-06-18 21:44:20.999798','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,11,1915,0,0,0,0,0,'9 NOV 1915',2420811,0,40,'c30181e4b677626cfaf','E0030','2012-06-18 21:44:23.268274','1969-12-31 19:00:00',NULL,0,NULL,4,'',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,9,1918,0,0,0,0,0,'SEP 1918',2421838,0,41,'c30181e4a981cd9203d','E0023','2012-06-18 21:44:23.276049','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,19,5,1994,0,0,0,0,0,'19 MAY 1994',2449492,0,42,'c30181e54312e09f62c','E0104','2012-06-18 21:44:23.282467','1969-12-31 19:00:00',NULL,0,NULL,5,'',15);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1955,0,0,0,0,0,'1955',2435109,0,43,'c30181e4ed0653b7724','E0052','2012-06-18 21:44:21.016759','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1858,0,0,0,0,0,'22 NOV 1858',2400006,0,44,'c30181e52652698fe9a','E0078','2012-06-18 21:44:23.290437','1969-12-31 19:00:00',NULL,0,NULL,5,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,45,'c30181e52d8430abe8c','E0088','2012-06-18 21:44:21.028203','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1956,0,0,0,0,0,'1956',2435474,0,46,'c30181e5be86d525dd1','E0134','2012-06-18 21:44:21.039482','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,47,'c30181e4e8253e73044','E0049','2012-06-18 21:44:21.050752','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,9,1888,0,0,0,0,0,'6 SEP 1888',2410887,0,48,'c30181e48fa5fe28ce0','E0000','2012-06-18 21:44:23.302739','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,49,'c30181e4b66345094be','E0029','2012-06-18 21:44:21.056014','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1883,0,0,0,0,0,'1883',2408812,0,50,'c30181e5deb6f4dfa25','E0140','2012-06-18 21:44:23.310694','1969-12-31 19:00:00',NULL,0,NULL,37,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,51,'c30181e4a302228cf9f','E0017','2012-06-18 21:44:21.061223','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,52,'c30181e53d124aa18ae','E0101','2012-06-18 21:44:21.064964','1969-12-31 19:00:00',NULL,0,NULL,47,'Later on in life he faced serious back surgery two times, on',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,53,'c30181e4920149cccea','E0002','2012-06-18 21:44:23.321373','1969-12-31 19:00:00',NULL,0,NULL,11,'',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1957,0,0,0,0,0,'1957',2435840,0,54,'c30181e4ef818f24294','E0053','2012-06-18 21:44:21.084181','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,55,'c30181e493079f99e2a','E0003','2012-06-18 21:44:21.095122','1969-12-31 19:00:00',NULL,0,NULL,29,'Bank President, Ambassador',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,56,'c30181e54d0497d16d4','E0113','2012-06-18 21:44:21.097888','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1821,0,0,0,0,0,'1821',2386167,0,57,'c30181e52ad6d99c52f','E0084','2012-06-18 21:44:21.108980','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,58,'c30181e53cc57040c7d','E0100','2012-06-18 21:44:21.114981','1969-12-31 19:00:00',NULL,0,NULL,18,'Choate, London Sch. Of Econ., Princeton, Harvard',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,59,'c30181e545566960e64','E0106','2012-06-18 21:44:21.118432','1969-12-31 19:00:00',NULL,0,NULL,47,'In 1955 Jackie suffered a miscarriage',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,7,1951,0,0,0,0,0,'4 JUL 1951',2433832,0,60,'c30181e4e363414c7c1','E0047','2012-06-18 21:44:21.125498','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,61,'c30181e4bde1ec9d6c8','E0033','2012-06-18 21:44:21.128784','1969-12-31 19:00:00',NULL,0,NULL,27,'III',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,62,'c30181e4de954e9bdfa','E0044','2012-06-18 21:44:21.139054','1969-12-31 19:00:00',NULL,0,NULL,47,'Hickory Hill',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,8,1944,0,0,0,0,0,'2 AUG 1944',2431305,0,63,'c30181e4a443edd4b23','E0019','2012-06-18 21:44:23.623938','1969-12-31 19:00:00',NULL,0,NULL,5,'',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,9,1855,0,0,0,0,0,'24 SEP 1855',2398851,0,64,'c30181e564f18b5ef65','E0123','2012-06-18 21:44:21.147210','1969-12-31 19:00:00',NULL,0,NULL,5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,65,'c30181e523b38d05f0d','E0076','2012-06-18 21:44:21.150402','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,66,'c30181e4955398370e1','E0007','2012-06-18 21:44:21.153770','1969-12-31 19:00:00',NULL,0,NULL,47,'Hyannis, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,2,1964,0,0,0,0,0,'FEB 1964',2438427,0,67,'c30181e4c6a044bb732','E0037','2012-06-18 21:44:23.639251','1969-12-31 19:00:00',NULL,0,NULL,4,'',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,12,1852,0,0,0,0,0,'4 DEC 1852',2397827,0,68,'c30181e561012d82b9a','E0121','2012-06-18 21:44:21.160301','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,69,'c30181e56cd4bc40ebb','E0126','2012-06-18 21:44:21.163623','1969-12-31 19:00:00',NULL,0,NULL,29,'Clerk',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,2,1932,0,0,0,0,0,'22 FEB 1932',2426760,0,70,'c30181e50f876ba04d0','E0062','2012-06-18 21:44:23.829599','1969-12-31 19:00:00',NULL,0,NULL,4,'',4);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,5,1944,0,0,0,0,0,'6 MAY 1944',2431217,0,71,'c30181e59de39a7ebd9','E0130','2012-06-18 21:44:23.835931','1969-12-31 19:00:00',NULL,0,NULL,37,'',6);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,72,'c30181e52877569cf7d','E0081','2012-06-18 21:44:21.209633','1969-12-31 19:00:00',NULL,0,NULL,47,'Duganstown, Ireland',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1953,0,0,0,0,0,'1953',2434379,0,73,'c30181e4e830d05a844','E0050','2012-06-18 21:44:21.213950','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,74,'c30181e4c063f49fa0e','E0035','2012-06-18 21:44:21.217284','1969-12-31 19:00:00',NULL,0,NULL,29,'Actor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,75,'c30181e56e74431e058','E0127','2012-06-18 21:44:21.224773','1969-12-31 19:00:00',NULL,0,NULL,29,'Teamster',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,10,1914,0,0,0,0,0,'7 OCT 1914',2420413,0,76,'c30181e59b8619ed053','E0129','2012-06-18 21:44:24.104399','1969-12-31 19:00:00',NULL,0,NULL,37,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,12,1888,0,0,0,0,0,'20 DEC 1888',2410992,0,77,'c30181e52b13a1f45ce','E0085','2012-06-18 21:44:24.110880','1969-12-31 19:00:00',NULL,0,NULL,5,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,1,1995,0,0,0,0,0,'22 JAN 1995',2449740,0,78,'c30181e49c02e640850','E0012','2012-06-18 21:44:24.117308','1969-12-31 19:00:00',NULL,0,NULL,5,'',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,79,'c30181e51eb44bbfa38','E0071','2012-06-18 21:44:21.254804','1969-12-31 19:00:00',NULL,0,NULL,29,'Dockhand, Saloonkeeper, Senator, Bank President',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,80,'c30181e52f363dad054','E0089','2012-06-18 21:44:21.258026','1969-12-31 19:00:00',NULL,0,NULL,27,'III',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1958,0,0,0,0,0,'1958',2436205,0,81,'c30181e4f2130ab6455','E0054','2012-06-18 21:44:21.264382','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,82,'c30181e53607e649aa7','E0095','2012-06-18 21:44:21.267919','1969-12-31 19:00:00',NULL,0,NULL,29,'Mayor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1928,0,0,0,0,0,'1928',2425247,0,83,'c30181e4e1e16f54c21','E0046','2012-06-18 21:44:21.271256','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1887,0,0,0,0,0,'1887',2410273,0,84,'c30181e5c8132d134d5','E0136','2012-06-18 21:44:21.274410','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,85,'c30181e4bb174a634aa','E0032','2012-06-18 21:44:21.297787','1969-12-31 19:00:00',NULL,0,NULL,47,'Timberlawn, MD',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,2,1928,0,0,0,0,0,'FEB 1928',2425278,0,86,'c30181e50405aafa5a6','E0059','2012-06-18 21:44:24.224140','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,87,'c30181e518340c98032','E0066','2012-06-18 21:44:21.309222','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,6,1942,0,0,0,0,0,'JUN 1942',2430512,0,88,'c30181e5e5600db124c','E0143','2012-06-18 21:44:21.312678','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,89,'c30181e5322450c2a87','E0093','2012-06-18 21:44:21.335956','1969-12-31 19:00:00',NULL,0,NULL,47,'East Hampton, NY',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,90,'c30181e4aa919d6530f','E0024','2012-06-18 21:44:21.363895','1969-12-31 19:00:00',NULL,0,NULL,47,'In 1941 she had a frontal lobotomy.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1892,0,0,0,0,0,'1892',2412099,0,91,'c30181e570004477f62','E0128','2012-06-18 21:44:24.513752','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,92,'c30181e5318307e4770','E0092','2012-06-18 21:44:21.382197','1969-12-31 19:00:00',NULL,0,NULL,47,'Died of cancer.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,93,'c30181e56b537b4e14e','E0125','2012-06-18 21:44:21.395710','1969-12-31 19:00:00',NULL,0,NULL,29,'Janitor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,5,1929,0,0,0,0,0,'MAY 1929',2425733,0,94,'c30181e51e8398aa506','E0070','2012-06-18 21:44:21.398389','1969-12-31 19:00:00',NULL,0,NULL,5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,11,1957,0,0,0,0,0,'27 NOV 1957',2436170,0,95,'c30181e54aa5b523b42','E0110','2012-06-18 21:44:24.524709','1969-12-31 19:00:00',NULL,0,NULL,4,'',11);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1954,0,0,0,0,0,'1954',2434744,0,96,'c30181e4eaa2aab1ef6','E0051','2012-06-18 21:44:21.416723','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,9,1872,0,0,0,0,0,'22 SEP 1872',2405059,0,97,'c30181e5e0f09d98977','E0141','2012-06-18 21:44:24.645252','1969-12-31 19:00:00',NULL,0,NULL,37,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,98,'c30181e547331deddc7','E0109','2012-06-18 21:44:21.433421','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1923,0,0,0,0,0,'1923',2423421,0,99,'c30181e52374c774380','E0075','2012-06-18 21:44:21.436065','1969-12-31 19:00:00',NULL,0,NULL,5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,100,'c30181e53082307d401','E0091','2012-06-18 21:44:24.907242','1969-12-31 19:00:00',NULL,0,NULL,11,'',27);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,8,1957,0,0,0,0,0,'AUG 1957',2436052,0,101,'c30181e52f4350e465c','E0090','2012-06-18 21:44:24.913590','1969-12-31 19:00:00',NULL,0,NULL,5,'',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1898,0,0,0,0,0,'1898',2414291,0,102,'c30181e557e06f2f3e5','E0119','2012-06-18 21:44:21.450826','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,1,1858,0,0,0,0,0,'14 JAN 1858',2399694,0,103,'c30181e51d50d162470','E0069','2012-06-18 21:44:25.031564','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,104,'c30181e511012f2d9e2','E0063','2012-06-18 21:44:21.464764','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,105,'c30181e495f0e2da01f','E0010','2012-06-18 21:44:21.471653','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,12,1957,0,0,0,0,0,'13 DEC 1957',2436186,0,106,'c30181e54bc0339f003','E0111','2012-06-18 21:44:25.197402','1969-12-31 19:00:00',NULL,0,NULL,14,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,1,1995,0,0,0,0,0,'25 JAN 1995',2449743,0,107,'c30181e49d04103d518','E0013','2012-06-18 21:44:25.210703','1969-12-31 19:00:00',NULL,0,NULL,11,'',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1965,0,0,0,0,0,'1965',2438762,0,108,'c30181e5ac154320785','E0132','2012-06-18 21:44:21.496979','1969-12-31 19:00:00',NULL,0,NULL,43,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,8,1963,0,0,0,0,0,'AUG 1963',2438243,0,109,'c30181e51ae4c78f74e','E0068','2012-06-18 21:44:21.499596','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,110,'c30181e52073247f681','E0074','2012-06-18 21:44:21.505616','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,17,6,1950,0,0,0,0,0,'17 JUN 1950',2433450,0,111,'c30181e5b9225ec68fa','E0133','2012-06-18 21:44:25.223047','1969-12-31 19:00:00',NULL,0,NULL,37,'',16);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,12,1968,0,0,0,0,0,'12 DEC 1968',2440203,0,112,'c30181e4ff33f7570e6','E0058','2012-06-18 21:44:25.229407','1969-12-31 19:00:00',NULL,0,NULL,4,'',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,9,1961,0,0,0,0,0,'26 SEP 1961',2437569,0,113,'c30181e518446c9b16a','E0067','2012-06-18 21:44:21.520042','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1940,0,0,0,0,0,'JUL 1940',2429812,0,114,'c30181e5d36233e4ced','E0138','2012-06-18 21:44:21.522690','1969-12-31 19:00:00',NULL,0,NULL,43,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,115,'c30181e528c44d39cf0','E0083','2012-06-18 21:44:21.525307','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,8,6,1968,0,0,0,0,0,'8 JUN 1968',2440016,0,116,'c30181e4dd20775aaf3','E0043','2012-06-18 21:44:25.326339','1969-12-31 19:00:00',NULL,0,NULL,11,'',28);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,117,'c30181e52897f795d4b','E0082','2012-06-18 21:44:21.548615','1969-12-31 19:00:00',NULL,0,NULL,47,'Liverpool St., East Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,5,1917,0,0,0,0,0,'29 MAY 1917',2421378,0,118,'c30181e53932ce5971d','E0096','2012-06-18 21:44:25.423310','1969-12-31 19:00:00',NULL,0,NULL,4,'',4);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,5,1924,0,0,0,0,0,'6 MAY 1924',2423912,0,119,'c30181e4cec197fdb51','E0040','2012-06-18 21:44:25.429673','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,120,'c30181e49e63995ac52','E0014','2012-06-18 21:44:21.558823','1969-12-31 19:00:00',NULL,0,NULL,18,'Dorchester High School, Sacred Heart Convent',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,6,1963,0,0,0,0,0,'4 JUN 1963',2438185,0,121,'c30181e4f4d5da3f0ad','E0055','2012-06-18 21:44:25.437702','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,122,'c30181e546d20ca6b5c','E0107','2012-06-18 21:44:21.569064','1969-12-31 19:00:00',NULL,0,NULL,47,'5th Avenue, NYC, NY',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1915,0,0,0,0,0,'JUL 1915',2420680,0,123,'c30181e4a327ea5b833','E0018','2012-06-18 21:44:25.580032','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,11,1925,0,0,0,0,0,'20 NOV 1925',2424475,0,124,'c30181e4dad7ad287cd','E0041','2012-06-18 21:44:25.650012','1969-12-31 19:00:00',NULL,0,NULL,4,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,6,1968,0,0,0,0,0,'6 JUN 1968',2440014,0,125,'c30181e4dc041fa6f0d','E0042','2012-06-18 21:44:25.835347','1969-12-31 19:00:00',NULL,0,NULL,5,'',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,9,1849,0,0,0,0,0,'28 SEP 1849',2396664,0,126,'c30181e5ced2f26274b','E0137','2012-06-18 21:44:25.931151','1969-12-31 19:00:00',NULL,0,NULL,37,'',5);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,127,'c30181e55116d5da680','E0116','2012-06-18 21:44:21.598530','1969-12-31 19:00:00',NULL,0,NULL,18,'Brown Univ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,3,1967,0,0,0,0,0,'24 MAR 1967',2439574,0,128,'c30181e4fba77152b03','E0057','2012-06-18 21:44:25.991495','1969-12-31 19:00:00',NULL,0,NULL,4,'',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,129,'c30181e52c37633e7f0','E0086','2012-06-18 21:44:25.997833','1969-12-31 19:00:00',NULL,0,NULL,11,'',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,130,'c30181e520403f6ea34','E0073','2012-06-18 21:44:21.637652','1969-12-31 19:00:00',NULL,0,NULL,47,'Webster St., Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,131,'c30181e495c6ea02d2c','E0009','2012-06-18 21:44:21.645016','1969-12-31 19:00:00',NULL,0,NULL,47,'Brookline, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,132,'c30181e49fe1b46b996','E0016','2012-06-18 21:44:21.655291','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,1,1965,0,0,0,0,0,'9 JAN 1965',2438770,0,133,'c30181e4f83206b566d','E0056','2012-06-18 21:44:26.217127','1969-12-31 19:00:00',NULL,0,NULL,4,'',11);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,11,1963,0,0,0,0,0,'25 NOV 1963',2438359,0,134,'c30181e53b77b934368','E0098','2012-06-18 21:44:26.346839','1969-12-31 19:00:00',NULL,0,NULL,11,'',28);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1952,0,0,0,0,0,'1952',2434013,0,135,'c30181e4e5b140b3d57','E0048','2012-06-18 21:44:21.693025','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,136,'c30181e49331ac90378','E0004','2012-06-18 21:44:21.697075','1969-12-31 19:00:00',NULL,0,NULL,18,'Harvard Graduate',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,137,'c30181e546f01cfb4bc','E0108','2012-06-18 21:44:21.702368','1969-12-31 19:00:00',NULL,0,NULL,47,'Martha''s Vineyard ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,8,1963,0,0,0,0,0,'9 AUG 1963',2438251,0,138,'c30181e554b7c4caa19','E0118','2012-06-18 21:44:26.570236','1969-12-31 19:00:00',NULL,0,NULL,5,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,7,1890,0,0,0,0,0,'22 JUL 1890',2411571,0,139,'c30181e49ad4f8c4c64','E0011','2012-06-18 21:44:26.576568','1969-12-31 19:00:00',NULL,0,NULL,4,'',14);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1823,0,0,0,0,0,'1823',2386897,0,140,'c30181e52544e118135','E0077','2012-06-18 21:44:26.608489','1969-12-31 19:00:00',NULL,0,NULL,4,'',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,141,'c30181e53451c401c12','E0094','2012-06-18 21:44:21.729485','1969-12-31 19:00:00',NULL,0,NULL,47,'Newport, RI',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,11,1958,0,0,0,0,0,'29 NOV 1958',2436537,0,142,'c30181e5c331bb7e885','E0135','2012-06-18 21:44:21.736598','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,143,'c30181e527d3745b60c','E0080','2012-06-18 21:44:21.745225','1969-12-31 19:00:00',NULL,0,NULL,47,'He died of an outbreak of Cholera.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1954,0,0,0,0,0,'1954',2434744,0,144,'c30181e4be1721dc6e8','E0034','2012-06-18 21:44:21.748072','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
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
INSERT INTO "grampsdb_place" VALUES(1,'c30181e5547507f1b95','P0045','2012-06-18 21:44:20.728523','1969-12-31 19:00:00',NULL,0,NULL,'Otis Air Force B, Mass','','');
INSERT INTO "grampsdb_place" VALUES(2,'c30181e542e38adc7bc','P0039','2012-06-18 21:44:20.733113','1969-12-31 19:00:00',NULL,0,NULL,'Southampton, Long Island, NY','','');
INSERT INTO "grampsdb_place" VALUES(3,'c30181e49ce5f2a3fda','P0009','2012-06-18 21:44:20.743906','1969-12-31 19:00:00',NULL,0,NULL,'Hyannis Port, MA ','','');
INSERT INTO "grampsdb_place" VALUES(4,'c30181e51060e653e6b','P0027','2012-06-18 21:44:20.756204','1969-12-31 19:00:00',NULL,0,NULL,'Brookline, MA','','');
INSERT INTO "grampsdb_place" VALUES(5,'c30181e5cfd64f937bc','P0053','2012-06-18 21:44:20.815759','1969-12-31 19:00:00',NULL,0,NULL,'Holy Cross Cathedral, Boston, MA','','');
INSERT INTO "grampsdb_place" VALUES(6,'c30181e59ec2b05a236','P0049','2012-06-18 21:44:20.824536','1969-12-31 19:00:00',NULL,0,NULL,'London','','');
INSERT INTO "grampsdb_place" VALUES(7,'c30181e4dcd1190d651','P0021','2012-06-18 21:44:20.889526','1969-12-31 19:00:00',NULL,0,NULL,'Los Angeles, CA','','');
INSERT INTO "grampsdb_place" VALUES(8,'c30181e4c78043db2d4','P0019','2012-06-18 21:44:20.978891','1969-12-31 19:00:00',NULL,0,NULL,'Washington, DC','','');
INSERT INTO "grampsdb_place" VALUES(9,'c30181e4b2d0157da9f','P0015','2012-06-18 21:44:20.994745','1969-12-31 19:00:00',NULL,0,NULL,'France','','');
INSERT INTO "grampsdb_place" VALUES(10,'c30181e5558424036a8','P0047','2012-06-18 21:44:21.003619','1969-12-31 19:00:00',NULL,0,NULL,'Boston, Mass','','');
INSERT INTO "grampsdb_place" VALUES(11,'c30181e4f9276a83b2a','P0025','2012-06-18 21:44:21.025802','1969-12-31 19:00:00',NULL,0,NULL,'New York','','');
INSERT INTO "grampsdb_place" VALUES(12,'c30181e4b767a1ebf72','P0017','2012-06-18 21:44:21.062260','1969-12-31 19:00:00',NULL,0,NULL,'Westminster, MD','','');
INSERT INTO "grampsdb_place" VALUES(13,'c30181e52d11a6229e5','P0031','2012-06-18 21:44:21.119693','1969-12-31 19:00:00',NULL,0,NULL,'Cathedral Of The Holy Cross, MA','','');
INSERT INTO "grampsdb_place" VALUES(14,'c30181e49bc50d87f78','P0007','2012-06-18 21:44:21.144111','1969-12-31 19:00:00',NULL,0,NULL,'North End, Boston, MA','','');
INSERT INTO "grampsdb_place" VALUES(15,'c30181e543f715bab9c','P0041','2012-06-18 21:44:21.176614','1969-12-31 19:00:00',NULL,0,NULL,'NYC, NY','','');
INSERT INTO "grampsdb_place" VALUES(16,'c30181e5ba0351f4872','P0051','2012-06-18 21:44:21.198929','1969-12-31 19:00:00',NULL,0,NULL,'Greenwich, Connecticut','','');
INSERT INTO "grampsdb_place" VALUES(17,'c30181e4af372d9e672','P0013','2012-06-18 21:44:21.241797','1969-12-31 19:00:00',NULL,0,NULL,'Belgium','','');
INSERT INTO "grampsdb_place" VALUES(18,'c30181e4a5438ffb3b6','P0011','2012-06-18 21:44:21.306063','1969-12-31 19:00:00',NULL,0,NULL,'Suffolk, England','','');
INSERT INTO "grampsdb_place" VALUES(19,'c30181e490b3eb730d1','P0001','2012-06-18 21:44:21.465837','1969-12-31 19:00:00',NULL,0,NULL,'Boston, MA','','');
INSERT INTO "grampsdb_place" VALUES(20,'c30181e53050d991edb','P0033','2012-06-18 21:44:21.469184','1969-12-31 19:00:00',NULL,0,NULL,'Lennox Hill Hosp., NY','','');
INSERT INTO "grampsdb_place" VALUES(21,'c30181e54cb0f1aa53b','P0043','2012-06-18 21:44:21.491905','1969-12-31 19:00:00',NULL,0,NULL,'St. Patricks Cathedral','','');
INSERT INTO "grampsdb_place" VALUES(22,'c30181e53b478406597','P0037','2012-06-18 21:44:21.506713','1969-12-31 19:00:00',NULL,0,NULL,'Dallas, TX','','');
INSERT INTO "grampsdb_place" VALUES(23,'c30181e52621c9d8854','P0029','2012-06-18 21:44:21.530190','1969-12-31 19:00:00',NULL,0,NULL,'Dunganstown, Ireland','','');
INSERT INTO "grampsdb_place" VALUES(24,'c30181e491c448a8afd','P0003','2012-06-18 21:44:21.533308','1969-12-31 19:00:00',NULL,0,NULL,'Hyannis Port, MA','','');
INSERT INTO "grampsdb_place" VALUES(25,'c30181e492e571baf78','P0005','2012-06-18 21:44:21.534167','1969-12-31 19:00:00',NULL,0,NULL,'Holyhood Cemetery, Brookline, MA ','','');
INSERT INTO "grampsdb_place" VALUES(26,'c30181e5db73e334da0','P0055','2012-06-18 21:44:21.535053','1969-12-31 19:00:00',NULL,0,NULL,'Newport, RI','','');
INSERT INTO "grampsdb_place" VALUES(27,'c30181e53140c06f148','P0035','2012-06-18 21:44:21.677969','1969-12-31 19:00:00',NULL,0,NULL,'St. Philomena''s Cemetery, NY','','');
INSERT INTO "grampsdb_place" VALUES(28,'c30181e4ddf39eda033','P0023','2012-06-18 21:44:21.750000','1969-12-31 19:00:00',NULL,0,NULL,'Arlington National, VA','','');
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
INSERT INTO "grampsdb_note" VALUES(1,'c30181e53d42b157837','N0047','2012-06-18 21:44:20.725124','1969-12-31 19:00:00',NULL,0,NULL,3,'In 1960 he became President of the United States.',0);
INSERT INTO "grampsdb_note" VALUES(2,'c30181e527f79384805','N0038','2012-06-18 21:44:20.730854','1969-12-31 19:00:00',NULL,0,NULL,3,'The potato famine of 1845-48, plagued the country of Ireland and pushed many Irishmen to flee to the land of promise, the USA. Patrick Kennedy was among those to leave his home in Wexford County, Ireland, in 1848, in hopes of finding a better
life in the US. Once he arrived in the US, he settled in East Boston, where he remained for the rest of his life.',0);
INSERT INTO "grampsdb_note" VALUES(3,'c30181e58a5668763f5','N0068','2012-06-18 21:44:20.736023','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   716: 0 C1 CSTA
Skipped subordinate line           Line   717: 1 NAME Twin
',0);
INSERT INTO "grampsdb_note" VALUES(4,'c30181e536300087061','N0045','2012-06-18 21:44:20.741655','1969-12-31 19:00:00',NULL,0,NULL,3,'He was known as "Honey Fitz".',0);
INSERT INTO "grampsdb_note" VALUES(5,'c30181e545b25b031d6','N0053','2012-06-18 21:44:20.745928','1969-12-31 19:00:00',NULL,0,NULL,3,'Before marrying JFK, Jackie worked as a photo journalist in Washington DC.',0);
INSERT INTO "grampsdb_note" VALUES(6,'c30181e4baa1f6209f3','N0023','2012-06-18 21:44:20.770272','1969-12-31 19:00:00',NULL,0,NULL,3,'She ran a summer home for retarded children.',0);
INSERT INTO "grampsdb_note" VALUES(7,'c30181e57ba3fde82f0','N0059','2012-06-18 21:44:20.777752','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0003:

Line ignored as not understood     Line   699: 1 NAME New York Times, March 4, 1946, pp. 1,3.
',0);
INSERT INTO "grampsdb_note" VALUES(8,'c30181e57f108e3c511','N0061','2012-06-18 21:44:20.803024','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0005:

Line ignored as not understood     Line   703: 1 NAME New York World Telegram and Sun, Oct 11, 1957, pg. 1.
',0);
INSERT INTO "grampsdb_note" VALUES(9,'c30181e52d678793d34','N0041','2012-06-18 21:44:20.808195','1969-12-31 19:00:00',NULL,0,NULL,3,'After her husband died, she opened up a "Notions Shop" to provide for her family.',0);
INSERT INTO "grampsdb_note" VALUES(10,'c30181e51fb7989d62e','N0035','2012-06-18 21:44:20.832841','1969-12-31 19:00:00',NULL,0,NULL,3,'Patrick later became a very successful businessman getting into wholesale liquor sales, owning a coal company and becoming the president of a bank.',0);
INSERT INTO "grampsdb_note" VALUES(11,'c30181e590474b2c67e','N0074','2012-06-18 21:44:20.839621','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   728: 0 C7 CSTA
Skipped subordinate line           Line   729: 1 NAME Adopted Twin
',0);
INSERT INTO "grampsdb_note" VALUES(12,'c30181e4b3565158156','N0019','2012-06-18 21:44:20.854076','1969-12-31 19:00:00',NULL,0,NULL,3,'Served with the Red Cross in England during the war.',0);
INSERT INTO "grampsdb_note" VALUES(13,'c30181e57824861d37c','N0057','2012-06-18 21:44:20.866193','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0001:

Line ignored as not understood     Line   695: 1 NAME Joseph P. Kennedy, A Life and Times, by David E. Koskoff.
',0);
INSERT INTO "grampsdb_note" VALUES(14,'c30181e4cfe5d5e04bd','N0026','2012-06-18 21:44:20.876582','1969-12-31 19:00:00',NULL,0,NULL,3,'Was a help to her brother John F. during his political campaigns.',0);
INSERT INTO "grampsdb_note" VALUES(15,'c30181e4a1c203223e4','N0010','2012-06-18 21:44:20.880266','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0002:

Empty note ignored                 Line    58: 1 NOTE 
Empty note ignored                 Line    60: 1 NOTE 
Empty note ignored                 Line    62: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(16,'c30181e493f3a822d42','N0001','2012-06-18 21:44:20.901622','1969-12-31 19:00:00',NULL,0,NULL,3,'He had an interesting hobby of tinkering with clocks.',0);
INSERT INTO "grampsdb_note" VALUES(17,'c30181e494a061baf89','N0003','2012-06-18 21:44:20.908149','1969-12-31 19:00:00',NULL,0,NULL,3,'Was one of the youngest Bank Presidents in US history. ',0);
INSERT INTO "grampsdb_note" VALUES(18,'c30181e4946576246e7','N0002','2012-06-18 21:44:20.913549','1969-12-31 19:00:00',NULL,0,NULL,3,'Joe was a poor student, but good at athletics and had an attractive personality. He was able to overcome many ethnic barriers during his school years at Boston Latin, a protestant and primarily Yankee school.',0);
INSERT INTO "grampsdb_note" VALUES(19,'c30181e58f44efe4539','N0073','2012-06-18 21:44:20.922513','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   726: 0 C6 CSTA
Skipped subordinate line           Line   727: 1 NAME Foster
',0);
INSERT INTO "grampsdb_note" VALUES(20,'c30181e53d36cc370d9','N0046','2012-06-18 21:44:20.939422','1969-12-31 19:00:00',NULL,0,NULL,3,'<img src="http://www.jacqueslowe.com/html/photographs/jfk/images/jfkp52bw.jpg" border=1>',0);
INSERT INTO "grampsdb_note" VALUES(21,'c30181e4b307c2eb2a0','N0018','2012-06-18 21:44:20.961754','1969-12-31 19:00:00',NULL,0,NULL,3,'Died in an airplane crash with her lover in France three years after her older brother Joseph''s death.',0);
INSERT INTO "grampsdb_note" VALUES(22,'c30181e4bcb3b5e1633','N0025','2012-06-18 21:44:20.981199','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0008:

Empty note ignored                 Line   146: 1 NOTE 
Empty note ignored                 Line   148: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(23,'c30181e58d50a3973cd','N0071','2012-06-18 21:44:21.011320','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   722: 0 C4 CSTA
Skipped subordinate line           Line   723: 1 NAME Duplicate
',0);
INSERT INTO "grampsdb_note" VALUES(24,'c30181e4acd32bde247','N0017','2012-06-18 21:44:21.019312','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0004:

Empty note ignored                 Line    98: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(25,'c30181e53db0178264b','N0048','2012-06-18 21:44:21.030426','1969-12-31 19:00:00',NULL,0,NULL,3,'He wrote 2 books, including "Profiles in Courage", which won him a Pulitzer Prize.',0);
INSERT INTO "grampsdb_note" VALUES(26,'c30181e4b517a24c01b','N0020','2012-06-18 21:44:21.034039','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0006:

Empty note ignored                 Line   122: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(27,'c30181e531b1962e79f','N0042','2012-06-18 21:44:21.041697','1969-12-31 19:00:00',NULL,0,NULL,3,'He was known as "Black Jack."',0);
INSERT INTO "grampsdb_note" VALUES(28,'c30181e54955cda4320','N0056','2012-06-18 21:44:21.045319','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0053:

Empty note ignored                 Line   544: 1 NOTE 
Empty note ignored                 Line   546: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(29,'c30181e499704167c0b','N0005','2012-06-18 21:44:21.074428','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0001:

Empty note ignored                 Line    26: 1 NOTE 
Empty note ignored                 Line    28: 1 NOTE 
Empty note ignored                 Line    30: 1 NOTE 
Empty note ignored                 Line    32: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(30,'c30181e4b792156d1dc','N0021','2012-06-18 21:44:21.079465','1969-12-31 19:00:00',NULL,0,NULL,3,'1972 was the vice presidential candidate.',0);
INSERT INTO "grampsdb_note" VALUES(31,'c30181e4de83804cdb2','N0028','2012-06-18 21:44:21.100167','1969-12-31 19:00:00',NULL,0,NULL,3,'He was very dedicated to his children and every evening had prayers with them, each of them saying the Rosary.',0);
INSERT INTO "grampsdb_note" VALUES(32,'c30181e4de1058fc8ef','N0027','2012-06-18 21:44:21.134078','1969-12-31 19:00:00',NULL,0,NULL,3,'Robert Francis was assassinated in California during his 1968 presidential campaign.',0);
INSERT INTO "grampsdb_note" VALUES(33,'c30181e51f513521e0b','N0034','2012-06-18 21:44:21.166711','1969-12-31 19:00:00',NULL,0,NULL,3,'Patrick was able to work his way from being a SaloonKeeper to becoming a Ward Boss, helping out other Irish immigrants. His popularity  rose and at the age of thirty he had become a power in Boston politics. In 1892 and 1893 he was elected to
the Massachusetts Senate.',0);
INSERT INTO "grampsdb_note" VALUES(34,'c30181e51f056e1b07f','N0033','2012-06-18 21:44:21.173860','1969-12-31 19:00:00',NULL,0,NULL,3,'As a young man, Patrick dropped out of school to work on the docks of Boston.',0);
INSERT INTO "grampsdb_note" VALUES(35,'c30181e49fc547b92a6','N0009','2012-06-18 21:44:21.189726','1969-12-31 19:00:00',NULL,0,NULL,3,'She was very dedicated to her family, which was evident by the strong support she gave her sons in their political campaigns.',0);
INSERT INTO "grampsdb_note" VALUES(36,'c30181e58c50c783cc5','N0070','2012-06-18 21:44:21.194085','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   720: 0 C3 CSTA
Skipped subordinate line           Line   721: 1 NAME Illegitimate
',0);
INSERT INTO "grampsdb_note" VALUES(37,'c30181e540a2e19ad0a','N0051','2012-06-18 21:44:21.202036','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0052:

Empty note ignored                 Line   518: 1 NOTE 
Empty note ignored                 Line   520: 1 NOTE 
Empty note ignored                 Line   522: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(38,'c30181e49f256308ece','N0007','2012-06-18 21:44:21.220096','1969-12-31 19:00:00',NULL,0,NULL,3,'She graduated from high school, one of the three highest in a class of 285. She was then sent to finish school in Europe for two years.',0);
INSERT INTO "grampsdb_note" VALUES(39,'c30181e580c172b9b4d','N0062','2012-06-18 21:44:21.233291','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0006:

Line ignored as not understood     Line   705: 1 NAME The Kennedys Dynasty and Disaster 1848-1983, by John H. Davis.
',0);
INSERT INTO "grampsdb_note" VALUES(40,'c30181e4aad15ee2787','N0015','2012-06-18 21:44:21.277133','1969-12-31 19:00:00',NULL,0,NULL,3,'She was born severely mentally retarded. For years her parents were ashamed of her and never told anyone about her problems.',0);
INSERT INTO "grampsdb_note" VALUES(41,'c30181e58e428977473','N0072','2012-06-18 21:44:21.284088','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   724: 0 C5 CSTA
Skipped subordinate line           Line   725: 1 NAME Stillborn
',0);
INSERT INTO "grampsdb_note" VALUES(42,'c30181e58286298635f','N0063','2012-06-18 21:44:21.290838','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0007:

Line ignored as not understood     Line   707: 1 NAME Growing Up Kennedy, Harrison Raine and John Quinn.
',0);
INSERT INTO "grampsdb_note" VALUES(43,'c30181e510d4acb1be4','N0031','2012-06-18 21:44:21.300683','1969-12-31 19:00:00',NULL,0,NULL,3,'Was known as "Teddy".',0);
INSERT INTO "grampsdb_note" VALUES(44,'c30181e58433ff4662b','N0064','2012-06-18 21:44:21.315767','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0008:

Line ignored as not understood     Line   709: 1 NAME New York Times, Nov. 22, 1963.
',0);
INSERT INTO "grampsdb_note" VALUES(45,'c30181e4ba561d35a3e','N0022','2012-06-18 21:44:21.322180','1969-12-31 19:00:00',NULL,0,NULL,3,'She helped in the many political campaigns of her brother, John Fitzgerald.',0);
INSERT INTO "grampsdb_note" VALUES(46,'c30181e52855e218b93','N0039','2012-06-18 21:44:21.338775','1969-12-31 19:00:00',NULL,0,NULL,3,'Upon Patrick''s arrival in Boston, he immediately became involved in politics. He was known as a Ward Boss in Boston, looking out for the other Irish immigrants and trying to improve the conditions in the community.',0);
INSERT INTO "grampsdb_note" VALUES(47,'c30181e4a5c1f1539ba','N0011','2012-06-18 21:44:21.343892','1969-12-31 19:00:00',NULL,0,NULL,3,'Joseph Patrick was well liked, quick to smile, and had a tremendous dose of Irish charm.',0);
INSERT INTO "grampsdb_note" VALUES(48,'c30181e4e0b597fafcc','N0029','2012-06-18 21:44:21.351143','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0021:

Empty note ignored                 Line   237: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(49,'c30181e587a25840546','N0066','2012-06-18 21:44:21.366664','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0010:

Line ignored as not understood     Line   713: 1 NAME CBS This Morning show.
',0);
INSERT INTO "grampsdb_note" VALUES(50,'c30181e58b55bdb0093','N0069','2012-06-18 21:44:21.384800','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   718: 0 C2 CSTA
Skipped subordinate line           Line   719: 1 NAME Adopted
',0);
INSERT INTO "grampsdb_note" VALUES(51,'c30181e5298757a23fe','N0040','2012-06-18 21:44:21.390216','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0046:

Empty note ignored                 Line   438: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(52,'c30181e57d46954be30','N0060','2012-06-18 21:44:21.403552','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0004:

Line ignored as not understood     Line   701: 1 NAME New York Times, March 6, 1946.
',0);
INSERT INTO "grampsdb_note" VALUES(53,'c30181e49f80ef08a92','N0008','2012-06-18 21:44:21.412937','1969-12-31 19:00:00',NULL,0,NULL,3,'She was courted by some of the finest young men, not only Boston''s Irish, but members of the English nobility as well.',0);
INSERT INTO "grampsdb_note" VALUES(54,'c30181e4a836d692953','N0014','2012-06-18 21:44:21.419299','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0003:

Empty note ignored                 Line    82: 1 NOTE 
Empty note ignored                 Line    84: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(55,'c30181e49ed00f988ea','N0006','2012-06-18 21:44:21.458329','1969-12-31 19:00:00',NULL,0,NULL,3,'She was considered the flower of Boston Irish society.',0);
INSERT INTO "grampsdb_note" VALUES(56,'c30181e52001a69e6d0','N0036','2012-06-18 21:44:21.476123','1969-12-31 19:00:00',NULL,0,NULL,3,'His personality was mild-mannered, quiet and reserved, and he was viewed as a man of moderate habits.',0);
INSERT INTO "grampsdb_note" VALUES(57,'c30181e589627577ffa','N0067','2012-06-18 21:44:21.479833','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0011:

Line ignored as not understood     Line   715: 1 NAME Harrisburg Patriot News, January 25, 1995.
',0);
INSERT INTO "grampsdb_note" VALUES(58,'c30181e49514eaec76c','N0004','2012-06-18 21:44:21.501828','1969-12-31 19:00:00',NULL,0,NULL,3,'He was fiercely proud of his family. He was quoted as having said his family was the finest thing in his life. ',0);
INSERT INTO "grampsdb_note" VALUES(59,'c30181e54652307dedf','N0054','2012-06-18 21:44:21.514027','1969-12-31 19:00:00',NULL,0,NULL,3,'While dating JFK, Jackie did not want him to know that she was not rich and think that she was only marrying him for his money. So, she went to great lengths to appear rich.',0);
INSERT INTO "grampsdb_note" VALUES(60,'c30181e4bb07a225ea5','N0024','2012-06-18 21:44:21.527816','1969-12-31 19:00:00',NULL,0,NULL,3,'After her mother, Eunice was considered the family''s model woman.',0);
INSERT INTO "grampsdb_note" VALUES(61,'c30181e510919967bbc','N0030','2012-06-18 21:44:21.539317','1969-12-31 19:00:00',NULL,0,NULL,3,'Enlisted in the Navy during World War II.',0);
INSERT INTO "grampsdb_note" VALUES(62,'c30181e53e80a60db4d','N0050','2012-06-18 21:44:21.576251','1969-12-31 19:00:00',NULL,0,NULL,3,'He was assassinated in Dallas, TX.',0);
INSERT INTO "grampsdb_note" VALUES(63,'c30181e545744f38427','N0052','2012-06-18 21:44:21.605113','1969-12-31 19:00:00',NULL,0,NULL,3,'<img src="http://www.jacqueslowe.com/html/photographs/jackie/images/Jacky01bw.jpg" border=1>',0);
INSERT INTO "grampsdb_note" VALUES(64,'c30181e546b4cf41c3c','N0055','2012-06-18 21:44:21.608600','1969-12-31 19:00:00',NULL,0,NULL,3,'She was said to be the only First Lady to resemble royalty. She shunned the media and never publicly discussed the assassination of JFK, how she felt about it, or the alleged affairs of her first husband.',0);
INSERT INTO "grampsdb_note" VALUES(65,'c30181e579d41d2d22b','N0058','2012-06-18 21:44:21.612327','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0002:

Line ignored as not understood     Line   697: 1 NAME Rose, by Gail Cameron.
',0);
INSERT INTO "grampsdb_note" VALUES(66,'c30181e4ab2407624c2','N0016','2012-06-18 21:44:21.619488','1969-12-31 19:00:00',NULL,0,NULL,3,'In 1946 her father gave $600,000 for the construction of the Joseph P. Kennedy Jr. Convalescent Home for disadvantaged children, because of Rosemary''s condition.',0);
INSERT INTO "grampsdb_note" VALUES(67,'c30181e52234f9a30bc','N0037','2012-06-18 21:44:21.625869','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0044:

Empty note ignored                 Line   402: 1 NOTE 
Empty note ignored                 Line   405: 1 NOTE 
Empty note ignored                 Line   407: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(68,'c30181e493a64d2db2e','N0000','2012-06-18 21:44:21.633597','1969-12-31 19:00:00',NULL,0,NULL,3,'From the time he was a school boy he was interested in making money.',0);
INSERT INTO "grampsdb_note" VALUES(69,'c30181e585f010c35cd','N0065','2012-06-18 21:44:21.647605','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0009:

Line ignored as not understood     Line   711: 1 NAME Harrisburg Patriot News, 23 May 1994.
',0);
INSERT INTO "grampsdb_note" VALUES(70,'c30181e4a610a2e3911','N0012','2012-06-18 21:44:21.667154','1969-12-31 19:00:00',NULL,0,NULL,3,'He enlisted in the Navy during World War II, and died during a naval flight.',0);
INSERT INTO "grampsdb_note" VALUES(71,'c30181e4a671cdf9e0b','N0013','2012-06-18 21:44:21.673098','1969-12-31 19:00:00',NULL,0,NULL,3,'He was known as Jack.',0);
INSERT INTO "grampsdb_note" VALUES(72,'c30181e532f12af9357','N0044','2012-06-18 21:44:21.684874','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0048:

Empty note ignored                 Line   473: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(73,'c30181e53205b8153b0','N0043','2012-06-18 21:44:21.709355','1969-12-31 19:00:00',NULL,0,NULL,3,'He was known to drink alcohol excessively.',0);
INSERT INTO "grampsdb_note" VALUES(74,'c30181e512f6668bc46','N0032','2012-06-18 21:44:21.715917','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0039:

Empty note ignored                 Line   359: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(75,'c30181e53df1a89fbf1','N0049','2012-06-18 21:44:21.738887','1969-12-31 19:00:00',NULL,0,NULL,3,'He had personal finances that were estimated to be around $10 million while in the Presidency.',0);
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
INSERT INTO "grampsdb_surname" VALUES(1,1,'FITZGERALD','',1,'',1,1);
INSERT INTO "grampsdb_surname" VALUES(2,1,'KENNEDY','',1,'',2,1);
INSERT INTO "grampsdb_surname" VALUES(3,1,'KENNEDY','',1,'',3,1);
INSERT INTO "grampsdb_surname" VALUES(4,1,'KENNEDY','',1,'',4,1);
INSERT INTO "grampsdb_surname" VALUES(5,1,'BURKE','',1,'',5,1);
INSERT INTO "grampsdb_surname" VALUES(6,1,'SHRIVER','',1,'',6,1);
INSERT INTO "grampsdb_surname" VALUES(7,1,'KENNEDY','',1,'',7,1);
INSERT INTO "grampsdb_surname" VALUES(8,1,'ONASSIS','',1,'',8,1);
INSERT INTO "grampsdb_surname" VALUES(9,1,'KENNEDY','',1,'',9,1);
INSERT INTO "grampsdb_surname" VALUES(10,1,'KENNEDY','',1,'',10,1);
INSERT INTO "grampsdb_surname" VALUES(11,1,'LAWFORD','',1,'',11,1);
INSERT INTO "grampsdb_surname" VALUES(12,1,'KENNEDY','',1,'',12,1);
INSERT INTO "grampsdb_surname" VALUES(13,1,'LAWFORD','',1,'',13,1);
INSERT INTO "grampsdb_surname" VALUES(14,1,'KENNEDY','',1,'',14,1);
INSERT INTO "grampsdb_surname" VALUES(15,1,'BENNETT','',1,'',15,1);
INSERT INTO "grampsdb_surname" VALUES(16,1,'BOUVIER','',1,'',16,1);
INSERT INTO "grampsdb_surname" VALUES(17,1,'KENNEDY','',1,'',17,1);
INSERT INTO "grampsdb_surname" VALUES(18,1,'KENNEDY','',1,'',18,1);
INSERT INTO "grampsdb_surname" VALUES(19,1,'KENNEDY','',1,'',19,1);
INSERT INTO "grampsdb_surname" VALUES(20,1,'CAULFIELD','',1,'',20,1);
INSERT INTO "grampsdb_surname" VALUES(21,1,'KENNEDY','',1,'',21,1);
INSERT INTO "grampsdb_surname" VALUES(22,1,'SMITH','',1,'',22,1);
INSERT INTO "grampsdb_surname" VALUES(23,1,'LAWFORD','',1,'',23,1);
INSERT INTO "grampsdb_surname" VALUES(24,1,'KENNEDY','',1,'',24,1);
INSERT INTO "grampsdb_surname" VALUES(25,1,'ACHINCLOSS','',1,'',25,1);
INSERT INTO "grampsdb_surname" VALUES(26,1,'KENNEDY','',1,'',26,1);
INSERT INTO "grampsdb_surname" VALUES(27,1,'FITZGERALD','',1,'',27,1);
INSERT INTO "grampsdb_surname" VALUES(28,1,'KENNEDY','',1,'',28,1);
INSERT INTO "grampsdb_surname" VALUES(29,1,'KANE','',1,'',29,1);
INSERT INTO "grampsdb_surname" VALUES(30,1,'KENNEDY','',1,'',30,1);
INSERT INTO "grampsdb_surname" VALUES(31,1,'KENNEDY','',1,'',31,1);
INSERT INTO "grampsdb_surname" VALUES(32,1,'KENNEDY','',1,'',32,1);
INSERT INTO "grampsdb_surname" VALUES(33,1,'KENNEDY','',1,'',33,1);
INSERT INTO "grampsdb_surname" VALUES(34,1,'KENNEDY','',1,'',34,1);
INSERT INTO "grampsdb_surname" VALUES(35,1,'SHRIVER','',1,'',35,1);
INSERT INTO "grampsdb_surname" VALUES(36,1,'SHRIVER','',1,'',36,1);
INSERT INTO "grampsdb_surname" VALUES(37,1,'HANNON','',1,'',37,1);
INSERT INTO "grampsdb_surname" VALUES(38,1,'SHRIVER','',1,'',38,1);
INSERT INTO "grampsdb_surname" VALUES(39,1,'KENNEDY','',1,'',39,1);
INSERT INTO "grampsdb_surname" VALUES(40,1,'MURPHY','',1,'',40,1);
INSERT INTO "grampsdb_surname" VALUES(41,1,'SMITH','',1,'',41,1);
INSERT INTO "grampsdb_surname" VALUES(42,1,'MAHONEY','',1,'',42,1);
INSERT INTO "grampsdb_surname" VALUES(43,1,'KENNEDY','',1,'',43,1);
INSERT INTO "grampsdb_surname" VALUES(44,1,'KENNEDY','',1,'',44,1);
INSERT INTO "grampsdb_surname" VALUES(45,1,'KENNEDY','',1,'',45,1);
INSERT INTO "grampsdb_surname" VALUES(46,1,'SMITH','',1,'',46,1);
INSERT INTO "grampsdb_surname" VALUES(47,1,'SKAKEL','',1,'',47,1);
INSERT INTO "grampsdb_surname" VALUES(48,1,'KENNEDY','',1,'',48,1);
INSERT INTO "grampsdb_surname" VALUES(49,1,'KENNEDY','',1,'',49,1);
INSERT INTO "grampsdb_surname" VALUES(50,1,'KENNEDY','',1,'',50,1);
INSERT INTO "grampsdb_surname" VALUES(51,1,'KENNEDY','',1,'',51,1);
INSERT INTO "grampsdb_surname" VALUES(52,1,'CAVENDISH','',1,'',52,1);
INSERT INTO "grampsdb_surname" VALUES(53,1,'BOUVIER','',1,'',53,1);
INSERT INTO "grampsdb_surname" VALUES(54,1,'LAWFORD','',1,'',54,1);
INSERT INTO "grampsdb_surname" VALUES(55,1,'KENNEDY','',1,'',55,1);
INSERT INTO "grampsdb_surname" VALUES(56,1,'SHRIVER','',1,'',56,1);
INSERT INTO "grampsdb_surname" VALUES(57,1,'BOUVIER','',1,'',57,1);
INSERT INTO "grampsdb_surname" VALUES(58,1,'SCHWARZENEGGER','',1,'',58,1);
INSERT INTO "grampsdb_surname" VALUES(59,1,'KENNEDY','',1,'',59,1);
INSERT INTO "grampsdb_surname" VALUES(60,1,'LEE','',1,'',60,1);
INSERT INTO "grampsdb_surname" VALUES(61,1,'KENNEDY','',1,'',61,1);
INSERT INTO "grampsdb_surname" VALUES(62,1,'KENNEDY','',1,'',62,1);
INSERT INTO "grampsdb_surname" VALUES(63,1,'HICKEY','',1,'',63,1);
INSERT INTO "grampsdb_surname" VALUES(64,1,'SMITH','',1,'',64,1);
INSERT INTO "grampsdb_surname" VALUES(65,1,'SHRIVER','',1,'',65,1);
INSERT INTO "grampsdb_surname" VALUES(66,1,'KENNEDY','',1,'',66,1);
INSERT INTO "grampsdb_surname" VALUES(67,1,'LAWFORD','',1,'',67,1);
INSERT INTO "grampsdb_surname" VALUES(68,1,'KENNEDY','',1,'',68,1);
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
INSERT INTO "grampsdb_name" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:21.807222',NULL,NULL,1,4,1,'John F.','','','','','','',1,1,1);
INSERT INTO "grampsdb_name" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:21.859574',NULL,NULL,1,4,1,'Patricia','','','','','','',1,1,2);
INSERT INTO "grampsdb_name" VALUES(3,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:21.921215',NULL,NULL,1,4,1,'John Fitzgerald','','','','','','',1,1,3);
INSERT INTO "grampsdb_name" VALUES(4,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.062340',NULL,NULL,1,4,1,'Johanna','','','','','','',1,1,4);
INSERT INTO "grampsdb_name" VALUES(5,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.110030',NULL,NULL,1,4,1,'Charles','','','','','','',1,1,5);
INSERT INTO "grampsdb_name" VALUES(6,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.137585',NULL,NULL,1,4,1,'Mark Kennedy','','','','','','',1,1,6);
INSERT INTO "grampsdb_name" VALUES(7,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.178340',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,7);
INSERT INTO "grampsdb_name" VALUES(8,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.305663',NULL,NULL,1,4,1,'Aristotle','','','','','','',1,1,8);
INSERT INTO "grampsdb_name" VALUES(9,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.334069',NULL,NULL,1,4,1,'Kara Ann','','','','','','',1,1,9);
INSERT INTO "grampsdb_name" VALUES(10,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.384535',NULL,NULL,1,4,1,'Christopher George','','','','','','',1,1,10);
INSERT INTO "grampsdb_name" VALUES(11,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.443888',NULL,NULL,1,4,1,'Robin','','','','','','',1,1,11);
INSERT INTO "grampsdb_name" VALUES(12,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.488577',NULL,NULL,1,4,1,'John','','','','','','',1,1,12);
INSERT INTO "grampsdb_name" VALUES(13,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.569315',NULL,NULL,1,4,1,'Christopher','','','','','','',1,1,13);
INSERT INTO "grampsdb_name" VALUES(14,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.617424',NULL,NULL,1,4,1,'Robert Francis','','','','','','',1,1,14);
INSERT INTO "grampsdb_name" VALUES(15,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.673135',NULL,NULL,1,4,1,'Virginia Joan','','','','','','',1,1,15);
INSERT INTO "grampsdb_name" VALUES(16,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.731517',NULL,NULL,1,4,1,'Lee','','','','','','',1,1,16);
INSERT INTO "grampsdb_name" VALUES(17,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.757190',NULL,NULL,1,4,1,'Rosemary','','','','','','',1,1,17);
INSERT INTO "grampsdb_name" VALUES(18,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.828143',NULL,NULL,1,4,1,'Edward More','','','','','','',1,1,18);
INSERT INTO "grampsdb_name" VALUES(19,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:22.890920',NULL,NULL,1,4,1,'Caroline Bouvier','','','','','','',1,1,19);
INSERT INTO "grampsdb_name" VALUES(20,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.004684',NULL,NULL,1,4,1,'John T.','','','','','','',1,1,20);
INSERT INTO "grampsdb_name" VALUES(21,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.047577',NULL,NULL,1,4,1,'Robert Francis','','','','','','',1,1,21);
INSERT INTO "grampsdb_name" VALUES(22,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.162394',NULL,NULL,1,4,1,'Amanda','','','','','','',1,1,22);
INSERT INTO "grampsdb_name" VALUES(23,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.199056',NULL,NULL,1,4,1,'Sydney','','','','','','',1,1,23);
INSERT INTO "grampsdb_name" VALUES(24,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.330323',NULL,NULL,1,4,1,'Edward Moore','','','','','','',1,1,24);
INSERT INTO "grampsdb_name" VALUES(25,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.490745',NULL,NULL,1,4,1,'Hugh','','','','','','',1,1,25);
INSERT INTO "grampsdb_name" VALUES(26,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.520967',NULL,NULL,1,4,1,'Douglas Harriman','','','','','','',1,1,26);
INSERT INTO "grampsdb_name" VALUES(27,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.652820',NULL,NULL,1,4,1,'Rose','','','','','','',1,1,27);
INSERT INTO "grampsdb_name" VALUES(28,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.788267',NULL,NULL,1,4,1,'Rory Elizabeth','','','','','','',1,1,28);
INSERT INTO "grampsdb_name" VALUES(29,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.863307',NULL,NULL,1,4,1,'Laurence','','','','','','',1,1,29);
INSERT INTO "grampsdb_name" VALUES(30,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:23.924212',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,30);
INSERT INTO "grampsdb_name" VALUES(31,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.129382',NULL,NULL,1,4,1,'Kathleen','','','','','','',1,1,31);
INSERT INTO "grampsdb_name" VALUES(32,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.237750',NULL,NULL,1,4,1,'Patrick','','','','','','',1,1,32);
INSERT INTO "grampsdb_name" VALUES(33,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.359687',NULL,NULL,1,4,1,'Patrick Bouvier','','','','','','',1,1,33);
INSERT INTO "grampsdb_name" VALUES(34,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.418340',NULL,NULL,1,4,1,'Matthew Maxwell Taylor','','','','','','',1,1,34);
INSERT INTO "grampsdb_name" VALUES(35,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.460757',NULL,NULL,1,4,1,'Robert Sargent','','','','','','',1,1,35);
INSERT INTO "grampsdb_name" VALUES(36,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.533834',NULL,NULL,1,4,1,'Timothy','','','','','','',1,1,36);
INSERT INTO "grampsdb_name" VALUES(37,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.573559',NULL,NULL,1,4,1,'Josephine Mary','','','','','','',1,1,37);
INSERT INTO "grampsdb_name" VALUES(38,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.604641',NULL,NULL,1,4,1,'Maria','','','','','','',1,1,38);
INSERT INTO "grampsdb_name" VALUES(39,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.657421',NULL,NULL,1,4,1,'Patrick Joseph','','','','','','',1,1,39);
INSERT INTO "grampsdb_name" VALUES(40,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.811402',NULL,NULL,1,4,1,'Bridget','','','','','','',1,1,40);
INSERT INTO "grampsdb_name" VALUES(41,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.972323',NULL,NULL,1,4,1,'Stephen','','','','','','',1,1,41);
INSERT INTO "grampsdb_name" VALUES(42,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:24.997985',NULL,NULL,1,4,1,'Humphrey','','','','','','',1,1,42);
INSERT INTO "grampsdb_name" VALUES(43,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.043601',NULL,NULL,1,4,1,'Mary Kerry','','','','','','',1,1,43);
INSERT INTO "grampsdb_name" VALUES(44,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.087298',NULL,NULL,1,4,1,'Loretta','','','','','','',1,1,44);
INSERT INTO "grampsdb_name" VALUES(45,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.159288',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,45);
INSERT INTO "grampsdb_name" VALUES(46,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.238561',NULL,NULL,1,4,1,'Stephen Edward','','','','','','',1,1,46);
INSERT INTO "grampsdb_name" VALUES(47,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.287980',NULL,NULL,1,4,1,'Ethel','','','','','','',1,1,47);
INSERT INTO "grampsdb_name" VALUES(48,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.335504',NULL,NULL,1,4,1,'Margaret','','','','','','',1,1,48);
INSERT INTO "grampsdb_name" VALUES(49,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.385018',NULL,NULL,1,4,1,'Kathleen Hartington','','','','','','',1,1,49);
INSERT INTO "grampsdb_name" VALUES(50,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.446880',NULL,NULL,1,4,1,'Jean Ann','','','','','','',1,1,50);
INSERT INTO "grampsdb_name" VALUES(51,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.542495',NULL,NULL,1,4,1,'Mary Courtney','','','','','','',1,1,51);
INSERT INTO "grampsdb_name" VALUES(52,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.594221',NULL,NULL,1,4,1,'William John Robert','','','','','','',1,1,52);
INSERT INTO "grampsdb_name" VALUES(53,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.664199',NULL,NULL,1,4,1,'Jacqueline','','','','','','',1,1,53);
INSERT INTO "grampsdb_name" VALUES(54,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.852773',NULL,NULL,1,4,1,'Peter','','','','','','',1,1,54);
INSERT INTO "grampsdb_name" VALUES(55,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.893336',NULL,NULL,1,4,1,'David Anthony','','','','','','',1,1,55);
INSERT INTO "grampsdb_name" VALUES(56,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:25.941667',NULL,NULL,1,4,1,'Anthony Paul','','','','','','',1,1,56);
INSERT INTO "grampsdb_name" VALUES(57,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.038707',NULL,NULL,1,4,1,'John Vernou','','','','','','',1,1,57);
INSERT INTO "grampsdb_name" VALUES(58,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.135464',NULL,NULL,1,4,1,'Arnold','','','','','','',1,1,58);
INSERT INTO "grampsdb_name" VALUES(59,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.172605',NULL,NULL,1,4,1,'Margaret','','','','','','',1,1,59);
INSERT INTO "grampsdb_name" VALUES(60,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.226073',NULL,NULL,1,4,1,'Janet','','','','','','',1,1,60);
INSERT INTO "grampsdb_name" VALUES(61,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.268668',NULL,NULL,1,4,1,'Michael L.','','','','','','',1,1,61);
INSERT INTO "grampsdb_name" VALUES(62,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.309198',NULL,NULL,1,4,1,'Patrick Joseph','','','','','','',1,1,62);
INSERT INTO "grampsdb_name" VALUES(63,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.357190',NULL,NULL,1,4,1,'Mary Augusta','','','','','','',1,1,63);
INSERT INTO "grampsdb_name" VALUES(64,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.410570',NULL,NULL,1,4,1,'William Kennedy','','','','','','',1,1,64);
INSERT INTO "grampsdb_name" VALUES(65,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.452235',NULL,NULL,1,4,1,'Robert Sargent','','','','','','',1,1,65);
INSERT INTO "grampsdb_name" VALUES(66,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.509354',NULL,NULL,1,4,1,'John Fitzgerald','','','','','','',1,1,66);
INSERT INTO "grampsdb_name" VALUES(67,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.585526',NULL,NULL,1,4,1,'Victoria','','','','','','',1,1,67);
INSERT INTO "grampsdb_name" VALUES(68,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.626109',NULL,NULL,1,4,1,'Mary','','','','','','',1,1,68);
INSERT INTO "grampsdb_name" VALUES(69,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-18 21:44:26.674859',NULL,NULL,1,4,1,'Eunice Mary','','','','','','',1,1,69);
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
INSERT INTO "grampsdb_markup" VALUES(1,3,4,1,'Monospace','[(0, 154)]');
INSERT INTO "grampsdb_markup" VALUES(2,7,4,1,'Monospace','[(0, 152)]');
INSERT INTO "grampsdb_markup" VALUES(3,8,4,1,'Monospace','[(0, 166)]');
INSERT INTO "grampsdb_markup" VALUES(4,11,4,1,'Monospace','[(0, 162)]');
INSERT INTO "grampsdb_markup" VALUES(5,13,4,1,'Monospace','[(0, 170)]');
INSERT INTO "grampsdb_markup" VALUES(6,15,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(7,19,4,1,'Monospace','[(0, 156)]');
INSERT INTO "grampsdb_markup" VALUES(8,22,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(9,23,4,1,'Monospace','[(0, 159)]');
INSERT INTO "grampsdb_markup" VALUES(10,24,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(11,26,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(12,28,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(13,29,4,1,'Monospace','[(0, 282)]');
INSERT INTO "grampsdb_markup" VALUES(14,36,4,1,'Monospace','[(0, 162)]');
INSERT INTO "grampsdb_markup" VALUES(15,37,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(16,39,4,1,'Monospace','[(0, 175)]');
INSERT INTO "grampsdb_markup" VALUES(17,41,4,1,'Monospace','[(0, 159)]');
INSERT INTO "grampsdb_markup" VALUES(18,42,4,1,'Monospace','[(0, 163)]');
INSERT INTO "grampsdb_markup" VALUES(19,44,4,1,'Monospace','[(0, 143)]');
INSERT INTO "grampsdb_markup" VALUES(20,48,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(21,49,4,1,'Monospace','[(0, 135)]');
INSERT INTO "grampsdb_markup" VALUES(22,50,4,1,'Monospace','[(0, 157)]');
INSERT INTO "grampsdb_markup" VALUES(23,51,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(24,52,4,1,'Monospace','[(0, 143)]');
INSERT INTO "grampsdb_markup" VALUES(25,54,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(26,57,4,1,'Monospace','[(0, 155)]');
INSERT INTO "grampsdb_markup" VALUES(27,65,4,1,'Monospace','[(0, 135)]');
INSERT INTO "grampsdb_markup" VALUES(28,67,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(29,69,4,1,'Monospace','[(0, 150)]');
INSERT INTO "grampsdb_markup" VALUES(30,72,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(31,74,4,1,'Monospace','[(0, 117)]');
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
INSERT INTO "grampsdb_noteref" VALUES(1,32,1,1,'2012-06-18 21:44:21.830825',NULL,NULL,0,4);
INSERT INTO "grampsdb_noteref" VALUES(2,32,2,1,'2012-06-18 21:44:21.885811',NULL,NULL,0,14);
INSERT INTO "grampsdb_noteref" VALUES(3,35,1,1,'2012-06-18 21:44:21.912155',NULL,NULL,0,49);
INSERT INTO "grampsdb_noteref" VALUES(4,32,3,1,'2012-06-18 21:44:21.976232',NULL,NULL,0,20);
INSERT INTO "grampsdb_noteref" VALUES(5,32,3,1,'2012-06-18 21:44:21.980105',NULL,NULL,0,1);
INSERT INTO "grampsdb_noteref" VALUES(6,32,3,1,'2012-06-18 21:44:21.983843',NULL,NULL,0,25);
INSERT INTO "grampsdb_noteref" VALUES(7,32,3,1,'2012-06-18 21:44:21.987563',NULL,NULL,0,75);
INSERT INTO "grampsdb_noteref" VALUES(8,32,3,1,'2012-06-18 21:44:21.991415',NULL,NULL,0,62);
INSERT INTO "grampsdb_noteref" VALUES(9,32,3,1,'2012-06-18 21:44:21.995166',NULL,NULL,0,37);
INSERT INTO "grampsdb_noteref" VALUES(10,32,7,1,'2012-06-18 21:44:22.221594',NULL,NULL,0,47);
INSERT INTO "grampsdb_noteref" VALUES(11,32,7,1,'2012-06-18 21:44:22.225494',NULL,NULL,0,70);
INSERT INTO "grampsdb_noteref" VALUES(12,32,7,1,'2012-06-18 21:44:22.229260',NULL,NULL,0,71);
INSERT INTO "grampsdb_noteref" VALUES(13,32,7,1,'2012-06-18 21:44:22.233004',NULL,NULL,0,54);
INSERT INTO "grampsdb_noteref" VALUES(14,35,2,1,'2012-06-18 21:44:22.707245',NULL,NULL,0,65);
INSERT INTO "grampsdb_noteref" VALUES(15,32,17,1,'2012-06-18 21:44:22.780492',NULL,NULL,0,40);
INSERT INTO "grampsdb_noteref" VALUES(16,32,17,1,'2012-06-18 21:44:22.784389',NULL,NULL,0,66);
INSERT INTO "grampsdb_noteref" VALUES(17,32,17,1,'2012-06-18 21:44:22.789462',NULL,NULL,0,24);
INSERT INTO "grampsdb_noteref" VALUES(18,32,21,1,'2012-06-18 21:44:23.092783',NULL,NULL,0,32);
INSERT INTO "grampsdb_noteref" VALUES(19,32,21,1,'2012-06-18 21:44:23.096555',NULL,NULL,0,31);
INSERT INTO "grampsdb_noteref" VALUES(20,32,21,1,'2012-06-18 21:44:23.100428',NULL,NULL,0,48);
INSERT INTO "grampsdb_noteref" VALUES(21,32,24,1,'2012-06-18 21:44:23.360614',NULL,NULL,0,61);
INSERT INTO "grampsdb_noteref" VALUES(22,32,24,1,'2012-06-18 21:44:23.364551',NULL,NULL,0,43);
INSERT INTO "grampsdb_noteref" VALUES(23,32,24,1,'2012-06-18 21:44:23.368274',NULL,NULL,0,74);
INSERT INTO "grampsdb_noteref" VALUES(24,35,3,1,'2012-06-18 21:44:23.410125',NULL,NULL,0,52);
INSERT INTO "grampsdb_noteref" VALUES(25,32,27,1,'2012-06-18 21:44:23.709955',NULL,NULL,0,55);
INSERT INTO "grampsdb_noteref" VALUES(26,32,27,1,'2012-06-18 21:44:23.713720',NULL,NULL,0,38);
INSERT INTO "grampsdb_noteref" VALUES(27,32,27,1,'2012-06-18 21:44:23.717481',NULL,NULL,0,53);
INSERT INTO "grampsdb_noteref" VALUES(28,32,27,1,'2012-06-18 21:44:23.721224',NULL,NULL,0,35);
INSERT INTO "grampsdb_noteref" VALUES(29,32,27,1,'2012-06-18 21:44:23.725230',NULL,NULL,0,15);
INSERT INTO "grampsdb_noteref" VALUES(30,35,4,1,'2012-06-18 21:44:23.842987',NULL,NULL,0,69);
INSERT INTO "grampsdb_noteref" VALUES(31,35,5,1,'2012-06-18 21:44:23.851287',NULL,NULL,0,42);
INSERT INTO "grampsdb_noteref" VALUES(32,32,30,1,'2012-06-18 21:44:23.999643',NULL,NULL,0,68);
INSERT INTO "grampsdb_noteref" VALUES(33,32,30,1,'2012-06-18 21:44:24.003657',NULL,NULL,0,16);
INSERT INTO "grampsdb_noteref" VALUES(34,32,30,1,'2012-06-18 21:44:24.007484',NULL,NULL,0,18);
INSERT INTO "grampsdb_noteref" VALUES(35,32,30,1,'2012-06-18 21:44:24.011393',NULL,NULL,0,17);
INSERT INTO "grampsdb_noteref" VALUES(36,32,30,1,'2012-06-18 21:44:24.015154',NULL,NULL,0,58);
INSERT INTO "grampsdb_noteref" VALUES(37,32,30,1,'2012-06-18 21:44:24.018893',NULL,NULL,0,29);
INSERT INTO "grampsdb_noteref" VALUES(38,32,31,1,'2012-06-18 21:44:24.159572',NULL,NULL,0,21);
INSERT INTO "grampsdb_noteref" VALUES(39,32,31,1,'2012-06-18 21:44:24.163490',NULL,NULL,0,12);
INSERT INTO "grampsdb_noteref" VALUES(40,32,31,1,'2012-06-18 21:44:24.167283',NULL,NULL,0,26);
INSERT INTO "grampsdb_noteref" VALUES(41,32,32,1,'2012-06-18 21:44:24.286031',NULL,NULL,0,2);
INSERT INTO "grampsdb_noteref" VALUES(42,32,32,1,'2012-06-18 21:44:24.289813',NULL,NULL,0,46);
INSERT INTO "grampsdb_noteref" VALUES(43,32,32,1,'2012-06-18 21:44:24.293581',NULL,NULL,0,51);
INSERT INTO "grampsdb_noteref" VALUES(44,35,6,1,'2012-06-18 21:44:24.597114',NULL,NULL,0,39);
INSERT INTO "grampsdb_noteref" VALUES(45,32,39,1,'2012-06-18 21:44:24.734661',NULL,NULL,0,34);
INSERT INTO "grampsdb_noteref" VALUES(46,32,39,1,'2012-06-18 21:44:24.739944',NULL,NULL,0,33);
INSERT INTO "grampsdb_noteref" VALUES(47,32,39,1,'2012-06-18 21:44:24.743777',NULL,NULL,0,10);
INSERT INTO "grampsdb_noteref" VALUES(48,32,39,1,'2012-06-18 21:44:24.747551',NULL,NULL,0,56);
INSERT INTO "grampsdb_noteref" VALUES(49,32,39,1,'2012-06-18 21:44:24.751312',NULL,NULL,0,67);
INSERT INTO "grampsdb_noteref" VALUES(50,32,40,1,'2012-06-18 21:44:24.852871',NULL,NULL,0,9);
INSERT INTO "grampsdb_noteref" VALUES(51,35,7,1,'2012-06-18 21:44:24.964817',NULL,NULL,0,44);
INSERT INTO "grampsdb_noteref" VALUES(52,35,8,1,'2012-06-18 21:44:25.204496',NULL,NULL,0,13);
INSERT INTO "grampsdb_noteref" VALUES(53,35,9,1,'2012-06-18 21:44:25.586906',NULL,NULL,0,8);
INSERT INTO "grampsdb_noteref" VALUES(54,35,10,1,'2012-06-18 21:44:25.656834',NULL,NULL,0,7);
INSERT INTO "grampsdb_noteref" VALUES(55,32,53,1,'2012-06-18 21:44:25.725447',NULL,NULL,0,63);
INSERT INTO "grampsdb_noteref" VALUES(56,32,53,1,'2012-06-18 21:44:25.729201',NULL,NULL,0,5);
INSERT INTO "grampsdb_noteref" VALUES(57,32,53,1,'2012-06-18 21:44:25.735546',NULL,NULL,0,59);
INSERT INTO "grampsdb_noteref" VALUES(58,32,53,1,'2012-06-18 21:44:25.750978',NULL,NULL,0,64);
INSERT INTO "grampsdb_noteref" VALUES(59,32,53,1,'2012-06-18 21:44:25.755975',NULL,NULL,0,28);
INSERT INTO "grampsdb_noteref" VALUES(60,32,57,1,'2012-06-18 21:44:26.076417',NULL,NULL,0,27);
INSERT INTO "grampsdb_noteref" VALUES(61,32,57,1,'2012-06-18 21:44:26.080167',NULL,NULL,0,73);
INSERT INTO "grampsdb_noteref" VALUES(62,32,57,1,'2012-06-18 21:44:26.083915',NULL,NULL,0,72);
INSERT INTO "grampsdb_noteref" VALUES(63,32,65,1,'2012-06-18 21:44:26.475213',NULL,NULL,0,30);
INSERT INTO "grampsdb_noteref" VALUES(64,32,69,1,'2012-06-18 21:44:26.704588',NULL,NULL,0,45);
INSERT INTO "grampsdb_noteref" VALUES(65,32,69,1,'2012-06-18 21:44:26.708426',NULL,NULL,0,6);
INSERT INTO "grampsdb_noteref" VALUES(66,32,69,1,'2012-06-18 21:44:26.712184',NULL,NULL,0,60);
INSERT INTO "grampsdb_noteref" VALUES(67,32,69,1,'2012-06-18 21:44:26.715923',NULL,NULL,0,22);
INSERT INTO "grampsdb_noteref" VALUES(68,35,11,1,'2012-06-18 21:44:26.748288',NULL,NULL,0,57);
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
INSERT INTO "grampsdb_eventref" VALUES(1,33,1,1,'2012-06-18 21:44:21.784611',NULL,NULL,0,50,10);
INSERT INTO "grampsdb_eventref" VALUES(2,32,1,1,'2012-06-18 21:44:21.816702',NULL,NULL,0,82,3);
INSERT INTO "grampsdb_eventref" VALUES(3,32,2,1,'2012-06-18 21:44:21.866844',NULL,NULL,0,119,3);
INSERT INTO "grampsdb_eventref" VALUES(4,32,3,1,'2012-06-18 21:44:21.928414',NULL,NULL,0,118,3);
INSERT INTO "grampsdb_eventref" VALUES(5,32,3,2,'2012-06-18 21:44:21.933447',NULL,NULL,0,19,3);
INSERT INTO "grampsdb_eventref" VALUES(6,32,3,3,'2012-06-18 21:44:21.938348',NULL,NULL,0,134,3);
INSERT INTO "grampsdb_eventref" VALUES(7,32,3,4,'2012-06-18 21:44:21.943410',NULL,NULL,0,8,3);
INSERT INTO "grampsdb_eventref" VALUES(8,32,3,5,'2012-06-18 21:44:21.948318',NULL,NULL,0,58,3);
INSERT INTO "grampsdb_eventref" VALUES(9,32,3,6,'2012-06-18 21:44:21.953455',NULL,NULL,0,52,3);
INSERT INTO "grampsdb_eventref" VALUES(10,32,3,7,'2012-06-18 21:44:21.958387',NULL,NULL,0,35,3);
INSERT INTO "grampsdb_eventref" VALUES(11,32,4,1,'2012-06-18 21:44:22.069557',NULL,NULL,0,68,3);
INSERT INTO "grampsdb_eventref" VALUES(12,32,6,1,'2012-06-18 21:44:22.144946',NULL,NULL,0,67,3);
INSERT INTO "grampsdb_eventref" VALUES(13,32,7,1,'2012-06-18 21:44:22.185718',NULL,NULL,0,51,3);
INSERT INTO "grampsdb_eventref" VALUES(14,32,7,2,'2012-06-18 21:44:22.190672',NULL,NULL,0,123,3);
INSERT INTO "grampsdb_eventref" VALUES(15,32,7,3,'2012-06-18 21:44:22.195744',NULL,NULL,0,63,3);
INSERT INTO "grampsdb_eventref" VALUES(16,32,7,4,'2012-06-18 21:44:22.200651',NULL,NULL,0,13,3);
INSERT INTO "grampsdb_eventref" VALUES(17,32,7,5,'2012-06-18 21:44:22.205812',NULL,NULL,0,11,3);
INSERT INTO "grampsdb_eventref" VALUES(18,32,7,6,'2012-06-18 21:44:22.210749',NULL,NULL,0,39,3);
INSERT INTO "grampsdb_eventref" VALUES(19,32,9,1,'2012-06-18 21:44:22.341515',NULL,NULL,0,24,3);
INSERT INTO "grampsdb_eventref" VALUES(20,32,10,1,'2012-06-18 21:44:22.394432',NULL,NULL,0,121,3);
INSERT INTO "grampsdb_eventref" VALUES(21,32,12,1,'2012-06-18 21:44:22.498707',NULL,NULL,0,21,3);
INSERT INTO "grampsdb_eventref" VALUES(22,32,12,2,'2012-06-18 21:44:22.505421',NULL,NULL,0,64,3);
INSERT INTO "grampsdb_eventref" VALUES(23,32,14,1,'2012-06-18 21:44:22.624809',NULL,NULL,0,47,3);
INSERT INTO "grampsdb_eventref" VALUES(24,32,14,2,'2012-06-18 21:44:22.629847',NULL,NULL,0,73,3);
INSERT INTO "grampsdb_eventref" VALUES(25,32,15,1,'2012-06-18 21:44:22.680414',NULL,NULL,0,28,3);
INSERT INTO "grampsdb_eventref" VALUES(26,32,17,1,'2012-06-18 21:44:22.764597',NULL,NULL,0,41,3);
INSERT INTO "grampsdb_eventref" VALUES(27,32,17,2,'2012-06-18 21:44:22.769524',NULL,NULL,0,90,3);
INSERT INTO "grampsdb_eventref" VALUES(28,32,18,1,'2012-06-18 21:44:22.835569',NULL,NULL,0,87,3);
INSERT INTO "grampsdb_eventref" VALUES(29,32,18,2,'2012-06-18 21:44:22.840507',NULL,NULL,0,113,3);
INSERT INTO "grampsdb_eventref" VALUES(30,32,19,1,'2012-06-18 21:44:22.898255',NULL,NULL,0,95,3);
INSERT INTO "grampsdb_eventref" VALUES(31,32,19,2,'2012-06-18 21:44:22.903190',NULL,NULL,0,106,3);
INSERT INTO "grampsdb_eventref" VALUES(32,32,19,3,'2012-06-18 21:44:22.908359',NULL,NULL,0,26,3);
INSERT INTO "grampsdb_eventref" VALUES(33,32,19,4,'2012-06-18 21:44:22.913267',NULL,NULL,0,56,3);
INSERT INTO "grampsdb_eventref" VALUES(34,33,3,1,'2012-06-18 21:44:22.990161',NULL,NULL,0,84,10);
INSERT INTO "grampsdb_eventref" VALUES(35,32,20,1,'2012-06-18 21:44:23.012184',NULL,NULL,0,69,3);
INSERT INTO "grampsdb_eventref" VALUES(36,32,21,1,'2012-06-18 21:44:23.054847',NULL,NULL,0,124,3);
INSERT INTO "grampsdb_eventref" VALUES(37,32,21,2,'2012-06-18 21:44:23.059945',NULL,NULL,0,125,3);
INSERT INTO "grampsdb_eventref" VALUES(38,32,21,3,'2012-06-18 21:44:23.064869',NULL,NULL,0,116,3);
INSERT INTO "grampsdb_eventref" VALUES(39,32,21,4,'2012-06-18 21:44:23.069967',NULL,NULL,0,62,3);
INSERT INTO "grampsdb_eventref" VALUES(40,32,21,5,'2012-06-18 21:44:23.074907',NULL,NULL,0,31,3);
INSERT INTO "grampsdb_eventref" VALUES(41,33,5,1,'2012-06-18 21:44:23.247868',NULL,NULL,0,46,10);
INSERT INTO "grampsdb_eventref" VALUES(42,32,24,1,'2012-06-18 21:44:23.337681',NULL,NULL,0,70,3);
INSERT INTO "grampsdb_eventref" VALUES(43,32,24,2,'2012-06-18 21:44:23.342796',NULL,NULL,0,104,3);
INSERT INTO "grampsdb_eventref" VALUES(44,33,6,1,'2012-06-18 21:44:23.404810',NULL,NULL,0,88,10);
INSERT INTO "grampsdb_eventref" VALUES(45,33,7,1,'2012-06-18 21:44:23.478609',NULL,NULL,0,76,10);
INSERT INTO "grampsdb_eventref" VALUES(46,32,26,1,'2012-06-18 21:44:23.528330',NULL,NULL,0,128,3);
INSERT INTO "grampsdb_eventref" VALUES(47,33,8,1,'2012-06-18 21:44:23.616135',NULL,NULL,0,126,10);
INSERT INTO "grampsdb_eventref" VALUES(48,32,27,1,'2012-06-18 21:44:23.667384',NULL,NULL,0,139,3);
INSERT INTO "grampsdb_eventref" VALUES(49,32,27,2,'2012-06-18 21:44:23.672332',NULL,NULL,0,78,3);
INSERT INTO "grampsdb_eventref" VALUES(50,32,27,3,'2012-06-18 21:44:23.677553',NULL,NULL,0,107,3);
INSERT INTO "grampsdb_eventref" VALUES(51,32,27,4,'2012-06-18 21:44:23.682541',NULL,NULL,0,120,3);
INSERT INTO "grampsdb_eventref" VALUES(52,32,27,5,'2012-06-18 21:44:23.687450',NULL,NULL,0,12,3);
INSERT INTO "grampsdb_eventref" VALUES(53,32,27,6,'2012-06-18 21:44:23.692375',NULL,NULL,0,132,3);
INSERT INTO "grampsdb_eventref" VALUES(54,32,28,1,'2012-06-18 21:44:23.795550',NULL,NULL,0,112,3);
INSERT INTO "grampsdb_eventref" VALUES(55,32,29,1,'2012-06-18 21:44:23.870739',NULL,NULL,0,75,3);
INSERT INTO "grampsdb_eventref" VALUES(56,33,9,1,'2012-06-18 21:44:23.916582',NULL,NULL,0,114,10);
INSERT INTO "grampsdb_eventref" VALUES(57,32,30,1,'2012-06-18 21:44:23.931600',NULL,NULL,0,48,3);
INSERT INTO "grampsdb_eventref" VALUES(58,32,30,2,'2012-06-18 21:44:23.936522',NULL,NULL,0,4,3);
INSERT INTO "grampsdb_eventref" VALUES(59,32,30,3,'2012-06-18 21:44:23.941595',NULL,NULL,0,53,3);
INSERT INTO "grampsdb_eventref" VALUES(60,32,30,4,'2012-06-18 21:44:23.946535',NULL,NULL,0,55,3);
INSERT INTO "grampsdb_eventref" VALUES(61,32,30,5,'2012-06-18 21:44:23.951595',NULL,NULL,0,136,3);
INSERT INTO "grampsdb_eventref" VALUES(62,32,30,6,'2012-06-18 21:44:23.956501',NULL,NULL,0,16,3);
INSERT INTO "grampsdb_eventref" VALUES(63,32,30,7,'2012-06-18 21:44:23.961529',NULL,NULL,0,18,3);
INSERT INTO "grampsdb_eventref" VALUES(64,32,30,8,'2012-06-18 21:44:23.966479',NULL,NULL,0,66,3);
INSERT INTO "grampsdb_eventref" VALUES(65,32,30,9,'2012-06-18 21:44:23.971546',NULL,NULL,0,15,3);
INSERT INTO "grampsdb_eventref" VALUES(66,32,30,10,'2012-06-18 21:44:23.976544',NULL,NULL,0,131,3);
INSERT INTO "grampsdb_eventref" VALUES(67,32,30,11,'2012-06-18 21:44:23.981586',NULL,NULL,0,105,3);
INSERT INTO "grampsdb_eventref" VALUES(68,32,31,1,'2012-06-18 21:44:24.136799',NULL,NULL,0,36,3);
INSERT INTO "grampsdb_eventref" VALUES(69,32,31,2,'2012-06-18 21:44:24.141710',NULL,NULL,0,32,3);
INSERT INTO "grampsdb_eventref" VALUES(70,33,10,1,'2012-06-18 21:44:24.217654',NULL,NULL,0,97,10);
INSERT INTO "grampsdb_eventref" VALUES(71,32,32,1,'2012-06-18 21:44:24.245110',NULL,NULL,0,140,3);
INSERT INTO "grampsdb_eventref" VALUES(72,32,32,2,'2012-06-18 21:44:24.250060',NULL,NULL,0,44,3);
INSERT INTO "grampsdb_eventref" VALUES(73,32,32,3,'2012-06-18 21:44:24.255128',NULL,NULL,0,22,3);
INSERT INTO "grampsdb_eventref" VALUES(74,32,32,4,'2012-06-18 21:44:24.260061',NULL,NULL,0,143,3);
INSERT INTO "grampsdb_eventref" VALUES(75,32,32,5,'2012-06-18 21:44:24.265101',NULL,NULL,0,72,3);
INSERT INTO "grampsdb_eventref" VALUES(76,32,32,6,'2012-06-18 21:44:24.270047',NULL,NULL,0,117,3);
INSERT INTO "grampsdb_eventref" VALUES(77,32,32,7,'2012-06-18 21:44:24.275090',NULL,NULL,0,115,3);
INSERT INTO "grampsdb_eventref" VALUES(78,32,33,1,'2012-06-18 21:44:24.367176',NULL,NULL,0,27,3);
INSERT INTO "grampsdb_eventref" VALUES(79,32,33,2,'2012-06-18 21:44:24.372174',NULL,NULL,0,138,3);
INSERT INTO "grampsdb_eventref" VALUES(80,32,34,1,'2012-06-18 21:44:24.425595',NULL,NULL,0,133,3);
INSERT INTO "grampsdb_eventref" VALUES(81,32,35,1,'2012-06-18 21:44:24.468202',NULL,NULL,0,61,3);
INSERT INTO "grampsdb_eventref" VALUES(82,32,35,2,'2012-06-18 21:44:24.473238',NULL,NULL,0,144,3);
INSERT INTO "grampsdb_eventref" VALUES(83,33,11,1,'2012-06-18 21:44:24.564451',NULL,NULL,0,3,10);
INSERT INTO "grampsdb_eventref" VALUES(84,32,38,1,'2012-06-18 21:44:24.612194',NULL,NULL,0,30,3);
INSERT INTO "grampsdb_eventref" VALUES(85,32,39,1,'2012-06-18 21:44:24.671502',NULL,NULL,0,103,3);
INSERT INTO "grampsdb_eventref" VALUES(86,32,39,2,'2012-06-18 21:44:24.678020',NULL,NULL,0,94,3);
INSERT INTO "grampsdb_eventref" VALUES(87,32,39,3,'2012-06-18 21:44:24.687831',NULL,NULL,0,79,3);
INSERT INTO "grampsdb_eventref" VALUES(88,32,39,4,'2012-06-18 21:44:24.700844',NULL,NULL,0,6,3);
INSERT INTO "grampsdb_eventref" VALUES(89,32,39,5,'2012-06-18 21:44:24.706244',NULL,NULL,0,130,3);
INSERT INTO "grampsdb_eventref" VALUES(90,32,39,6,'2012-06-18 21:44:24.712317',NULL,NULL,0,110,3);
INSERT INTO "grampsdb_eventref" VALUES(91,32,40,1,'2012-06-18 21:44:24.818661',NULL,NULL,0,57,3);
INSERT INTO "grampsdb_eventref" VALUES(92,32,40,2,'2012-06-18 21:44:24.823588',NULL,NULL,0,77,3);
INSERT INTO "grampsdb_eventref" VALUES(93,32,40,3,'2012-06-18 21:44:24.828490',NULL,NULL,0,129,3);
INSERT INTO "grampsdb_eventref" VALUES(94,32,40,4,'2012-06-18 21:44:24.833413',NULL,NULL,0,5,3);
INSERT INTO "grampsdb_eventref" VALUES(95,32,40,5,'2012-06-18 21:44:24.838318',NULL,NULL,0,45,3);
INSERT INTO "grampsdb_eventref" VALUES(96,33,12,1,'2012-06-18 21:44:24.958050',NULL,NULL,0,9,10);
INSERT INTO "grampsdb_eventref" VALUES(97,32,42,1,'2012-06-18 21:44:25.005241',NULL,NULL,0,93,3);
INSERT INTO "grampsdb_eventref" VALUES(98,32,43,1,'2012-06-18 21:44:25.051005',NULL,NULL,0,81,3);
INSERT INTO "grampsdb_eventref" VALUES(99,32,44,1,'2012-06-18 21:44:25.094668',NULL,NULL,0,91,3);
INSERT INTO "grampsdb_eventref" VALUES(100,33,13,1,'2012-06-18 21:44:25.151772',NULL,NULL,0,33,10);
INSERT INTO "grampsdb_eventref" VALUES(101,32,45,1,'2012-06-18 21:44:25.166572',NULL,NULL,0,135,3);
INSERT INTO "grampsdb_eventref" VALUES(102,32,47,1,'2012-06-18 21:44:25.295401',NULL,NULL,0,83,3);
INSERT INTO "grampsdb_eventref" VALUES(103,32,48,1,'2012-06-18 21:44:25.342899',NULL,NULL,0,10,3);
INSERT INTO "grampsdb_eventref" VALUES(104,32,49,1,'2012-06-18 21:44:25.392403',NULL,NULL,0,60,3);
INSERT INTO "grampsdb_eventref" VALUES(105,32,50,1,'2012-06-18 21:44:25.454292',NULL,NULL,0,86,3);
INSERT INTO "grampsdb_eventref" VALUES(106,32,50,2,'2012-06-18 21:44:25.459287',NULL,NULL,0,34,3);
INSERT INTO "grampsdb_eventref" VALUES(107,33,15,1,'2012-06-18 21:44:25.533584',NULL,NULL,0,108,10);
INSERT INTO "grampsdb_eventref" VALUES(108,32,51,1,'2012-06-18 21:44:25.549739',NULL,NULL,0,43,3);
INSERT INTO "grampsdb_eventref" VALUES(109,32,52,1,'2012-06-18 21:44:25.601486',NULL,NULL,0,23,3);
INSERT INTO "grampsdb_eventref" VALUES(110,32,52,2,'2012-06-18 21:44:25.606455',NULL,NULL,0,29,3);
INSERT INTO "grampsdb_eventref" VALUES(111,32,53,1,'2012-06-18 21:44:25.671464',NULL,NULL,0,37,3);
INSERT INTO "grampsdb_eventref" VALUES(112,32,53,2,'2012-06-18 21:44:25.676399',NULL,NULL,0,42,3);
INSERT INTO "grampsdb_eventref" VALUES(113,32,53,3,'2012-06-18 21:44:25.681313',NULL,NULL,0,25,3);
INSERT INTO "grampsdb_eventref" VALUES(114,32,53,4,'2012-06-18 21:44:25.686232',NULL,NULL,0,59,3);
INSERT INTO "grampsdb_eventref" VALUES(115,32,53,5,'2012-06-18 21:44:25.691163',NULL,NULL,0,122,3);
INSERT INTO "grampsdb_eventref" VALUES(116,32,53,6,'2012-06-18 21:44:25.696065',NULL,NULL,0,137,3);
INSERT INTO "grampsdb_eventref" VALUES(117,32,53,7,'2012-06-18 21:44:25.701005',NULL,NULL,0,98,3);
INSERT INTO "grampsdb_eventref" VALUES(118,32,54,1,'2012-06-18 21:44:25.860153',NULL,NULL,0,7,3);
INSERT INTO "grampsdb_eventref" VALUES(119,32,55,1,'2012-06-18 21:44:25.900690',NULL,NULL,0,96,3);
INSERT INTO "grampsdb_eventref" VALUES(120,32,56,1,'2012-06-18 21:44:25.948952',NULL,NULL,0,2,3);
INSERT INTO "grampsdb_eventref" VALUES(121,33,16,1,'2012-06-18 21:44:25.986720',NULL,NULL,0,71,10);
INSERT INTO "grampsdb_eventref" VALUES(122,33,17,1,'2012-06-18 21:44:26.031360',NULL,NULL,0,142,10);
INSERT INTO "grampsdb_eventref" VALUES(123,32,57,1,'2012-06-18 21:44:26.045945',NULL,NULL,0,80,3);
INSERT INTO "grampsdb_eventref" VALUES(124,32,57,2,'2012-06-18 21:44:26.050888',NULL,NULL,0,101,3);
INSERT INTO "grampsdb_eventref" VALUES(125,32,57,3,'2012-06-18 21:44:26.055824',NULL,NULL,0,100,3);
INSERT INTO "grampsdb_eventref" VALUES(126,32,57,4,'2012-06-18 21:44:26.060733',NULL,NULL,0,92,3);
INSERT INTO "grampsdb_eventref" VALUES(127,32,57,5,'2012-06-18 21:44:26.065683',NULL,NULL,0,89,3);
INSERT INTO "grampsdb_eventref" VALUES(128,32,58,1,'2012-06-18 21:44:26.142731',NULL,NULL,0,74,3);
INSERT INTO "grampsdb_eventref" VALUES(129,32,59,1,'2012-06-18 21:44:26.179838',NULL,NULL,0,102,3);
INSERT INTO "grampsdb_eventref" VALUES(130,32,60,1,'2012-06-18 21:44:26.233343',NULL,NULL,0,141,3);
INSERT INTO "grampsdb_eventref" VALUES(131,32,61,1,'2012-06-18 21:44:26.275896',NULL,NULL,0,54,3);
INSERT INTO "grampsdb_eventref" VALUES(132,32,62,1,'2012-06-18 21:44:26.316464',NULL,NULL,0,109,3);
INSERT INTO "grampsdb_eventref" VALUES(133,32,63,1,'2012-06-18 21:44:26.364404',NULL,NULL,0,99,3);
INSERT INTO "grampsdb_eventref" VALUES(134,32,63,2,'2012-06-18 21:44:26.369336',NULL,NULL,0,65,3);
INSERT INTO "grampsdb_eventref" VALUES(135,32,64,1,'2012-06-18 21:44:26.417815',NULL,NULL,0,1,3);
INSERT INTO "grampsdb_eventref" VALUES(136,32,65,1,'2012-06-18 21:44:26.459513',NULL,NULL,0,49,3);
INSERT INTO "grampsdb_eventref" VALUES(137,32,65,2,'2012-06-18 21:44:26.464464',NULL,NULL,0,40,3);
INSERT INTO "grampsdb_eventref" VALUES(138,32,66,1,'2012-06-18 21:44:26.516595',NULL,NULL,0,14,3);
INSERT INTO "grampsdb_eventref" VALUES(139,32,66,2,'2012-06-18 21:44:26.521508',NULL,NULL,0,38,3);
INSERT INTO "grampsdb_eventref" VALUES(140,32,66,3,'2012-06-18 21:44:26.526435',NULL,NULL,0,127,3);
INSERT INTO "grampsdb_eventref" VALUES(141,32,68,1,'2012-06-18 21:44:26.633349',NULL,NULL,0,17,3);
INSERT INTO "grampsdb_eventref" VALUES(142,32,69,1,'2012-06-18 21:44:26.682050',NULL,NULL,0,20,3);
INSERT INTO "grampsdb_eventref" VALUES(143,32,69,2,'2012-06-18 21:44:26.687011',NULL,NULL,0,85,3);
INSERT INTO "grampsdb_eventref" VALUES(144,33,19,1,'2012-06-18 21:44:26.827754',NULL,NULL,0,111,10);
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
INSERT INTO "grampsdb_childref" VALUES(1,33,3,1,'2012-06-18 21:44:22.972485',NULL,NULL,0,2,2,30);
INSERT INTO "grampsdb_childref" VALUES(2,33,3,2,'2012-06-18 21:44:22.978992',NULL,NULL,0,2,2,44);
INSERT INTO "grampsdb_childref" VALUES(3,33,3,3,'2012-06-18 21:44:22.984999',NULL,NULL,0,2,2,59);
INSERT INTO "grampsdb_childref" VALUES(4,33,5,1,'2012-06-18 21:44:23.230674',NULL,NULL,0,2,2,41);
INSERT INTO "grampsdb_childref" VALUES(5,33,5,2,'2012-06-18 21:44:23.236665',NULL,NULL,0,2,2,64);
INSERT INTO "grampsdb_childref" VALUES(6,33,5,3,'2012-06-18 21:44:23.242819',NULL,NULL,0,2,2,22);
INSERT INTO "grampsdb_childref" VALUES(7,33,7,1,'2012-06-18 21:44:23.425019',NULL,NULL,0,2,2,7);
INSERT INTO "grampsdb_childref" VALUES(8,33,7,2,'2012-06-18 21:44:23.431038',NULL,NULL,0,2,2,3);
INSERT INTO "grampsdb_childref" VALUES(9,33,7,3,'2012-06-18 21:44:23.437203',NULL,NULL,0,2,2,17);
INSERT INTO "grampsdb_childref" VALUES(10,33,7,4,'2012-06-18 21:44:23.443298',NULL,NULL,0,2,2,31);
INSERT INTO "grampsdb_childref" VALUES(11,33,7,5,'2012-06-18 21:44:23.449291',NULL,NULL,0,2,2,69);
INSERT INTO "grampsdb_childref" VALUES(12,33,7,6,'2012-06-18 21:44:23.455400',NULL,NULL,0,2,2,2);
INSERT INTO "grampsdb_childref" VALUES(13,33,7,7,'2012-06-18 21:44:23.461342',NULL,NULL,0,2,2,21);
INSERT INTO "grampsdb_childref" VALUES(14,33,7,8,'2012-06-18 21:44:23.467463',NULL,NULL,0,2,2,50);
INSERT INTO "grampsdb_childref" VALUES(15,33,7,9,'2012-06-18 21:44:23.473554',NULL,NULL,0,2,2,24);
INSERT INTO "grampsdb_childref" VALUES(16,33,8,1,'2012-06-18 21:44:23.574712',NULL,NULL,0,2,2,68);
INSERT INTO "grampsdb_childref" VALUES(17,33,8,2,'2012-06-18 21:44:23.581713',NULL,NULL,0,2,2,4);
INSERT INTO "grampsdb_childref" VALUES(18,33,8,3,'2012-06-18 21:44:23.589781',NULL,NULL,0,2,2,12);
INSERT INTO "grampsdb_childref" VALUES(19,33,8,4,'2012-06-18 21:44:23.597111',NULL,NULL,0,2,2,48);
INSERT INTO "grampsdb_childref" VALUES(20,33,8,5,'2012-06-18 21:44:23.604295',NULL,NULL,0,2,2,39);
INSERT INTO "grampsdb_childref" VALUES(21,33,9,1,'2012-06-18 21:44:23.905350',NULL,NULL,0,2,2,53);
INSERT INTO "grampsdb_childref" VALUES(22,33,9,2,'2012-06-18 21:44:23.911569',NULL,NULL,0,2,2,16);
INSERT INTO "grampsdb_childref" VALUES(23,33,12,1,'2012-06-18 21:44:24.928594',NULL,NULL,0,2,2,35);
INSERT INTO "grampsdb_childref" VALUES(24,33,12,2,'2012-06-18 21:44:24.934622',NULL,NULL,0,2,2,38);
INSERT INTO "grampsdb_childref" VALUES(25,33,12,3,'2012-06-18 21:44:24.940765',NULL,NULL,0,2,2,36);
INSERT INTO "grampsdb_childref" VALUES(26,33,12,4,'2012-06-18 21:44:24.946876',NULL,NULL,0,2,2,6);
INSERT INTO "grampsdb_childref" VALUES(27,33,12,5,'2012-06-18 21:44:24.952859',NULL,NULL,0,2,2,56);
INSERT INTO "grampsdb_childref" VALUES(28,33,13,1,'2012-06-18 21:44:25.134267',NULL,NULL,0,2,2,19);
INSERT INTO "grampsdb_childref" VALUES(29,33,13,2,'2012-06-18 21:44:25.140472',NULL,NULL,0,2,2,66);
INSERT INTO "grampsdb_childref" VALUES(30,33,13,3,'2012-06-18 21:44:25.146506',NULL,NULL,0,2,2,33);
INSERT INTO "grampsdb_childref" VALUES(31,33,14,1,'2012-06-18 21:44:25.276420',NULL,NULL,0,2,2,27);
INSERT INTO "grampsdb_childref" VALUES(32,33,15,1,'2012-06-18 21:44:25.510546',NULL,NULL,0,2,2,13);
INSERT INTO "grampsdb_childref" VALUES(33,33,15,2,'2012-06-18 21:44:25.516560',NULL,NULL,0,2,2,67);
INSERT INTO "grampsdb_childref" VALUES(34,33,15,3,'2012-06-18 21:44:25.522548',NULL,NULL,0,2,2,23);
INSERT INTO "grampsdb_childref" VALUES(35,33,15,4,'2012-06-18 21:44:25.528552',NULL,NULL,0,2,2,11);
INSERT INTO "grampsdb_childref" VALUES(36,33,17,1,'2012-06-18 21:44:26.014045',NULL,NULL,0,2,2,9);
INSERT INTO "grampsdb_childref" VALUES(37,33,17,2,'2012-06-18 21:44:26.020310',NULL,NULL,0,2,2,18);
INSERT INTO "grampsdb_childref" VALUES(38,33,17,3,'2012-06-18 21:44:26.026339',NULL,NULL,0,2,2,62);
INSERT INTO "grampsdb_childref" VALUES(39,33,19,1,'2012-06-18 21:44:26.762715',NULL,NULL,0,2,2,49);
INSERT INTO "grampsdb_childref" VALUES(40,33,19,2,'2012-06-18 21:44:26.768710',NULL,NULL,0,2,2,45);
INSERT INTO "grampsdb_childref" VALUES(41,33,19,3,'2012-06-18 21:44:26.774714',NULL,NULL,0,2,2,14);
INSERT INTO "grampsdb_childref" VALUES(42,33,19,4,'2012-06-18 21:44:26.780674',NULL,NULL,0,2,2,55);
INSERT INTO "grampsdb_childref" VALUES(43,33,19,5,'2012-06-18 21:44:26.786650',NULL,NULL,0,2,2,51);
INSERT INTO "grampsdb_childref" VALUES(44,33,19,6,'2012-06-18 21:44:26.792603',NULL,NULL,0,2,2,61);
INSERT INTO "grampsdb_childref" VALUES(45,33,19,7,'2012-06-18 21:44:26.798574',NULL,NULL,0,2,2,43);
INSERT INTO "grampsdb_childref" VALUES(46,33,19,8,'2012-06-18 21:44:26.804533',NULL,NULL,0,2,2,10);
INSERT INTO "grampsdb_childref" VALUES(47,33,19,9,'2012-06-18 21:44:26.810639',NULL,NULL,0,2,2,34);
INSERT INTO "grampsdb_childref" VALUES(48,33,19,10,'2012-06-18 21:44:26.816783',NULL,NULL,0,2,2,26);
INSERT INTO "grampsdb_childref" VALUES(49,33,19,11,'2012-06-18 21:44:26.822746',NULL,NULL,0,2,2,28);
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
CREATE INDEX "grampsdb_profile_71d2bf68" ON "grampsdb_profile" ("theme_type_id");
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
CREATE INDEX "grampsdb_log_518e5aa5" ON "grampsdb_log" ("object_type_id");
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
