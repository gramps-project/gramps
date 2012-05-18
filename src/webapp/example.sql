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
INSERT INTO "auth_user" VALUES(2,'admin','Super','User','doug.blank@gmail.com','sha1$e2dde$a525775915da0b6229840916b01383b0c1dfab88',1,1,1,'2012-05-18 07:32:02.236336','2012-05-18 07:28:11');
INSERT INTO "auth_user" VALUES(3,'admin1','Regular','User','doug.blank@gmail.com','sha1$5522a$2e170386e66bf66418353694c41f3c3d84dd9588',0,1,0,'2012-05-18 07:31:24.829656','2012-05-18 07:29:35');
CREATE TABLE "auth_message" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "message" text NOT NULL
);
INSERT INTO "auth_message" VALUES(1,1,'Successfully deleted 1 user.');
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
INSERT INTO "django_session" VALUES('8125ee0b093b091383cb10e4a833a4c6','NDQ5ZWJmZjkxYjEzZDQ0YmI0MmU5ZGFiMGVkMDkzOGVmM2JiZGFiYjqAAn1xAShVEl9hdXRoX3Vz
ZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED
VQ1fYXV0aF91c2VyX2lkcQRLAnUu
','2012-06-01 07:32:02.467559');
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
INSERT INTO "grampsdb_profile" VALUES(2,2,'Web_Mainz.css');
INSERT INTO "grampsdb_profile" VALUES(3,3,'Web_Mainz.css');
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
INSERT INTO "grampsdb_nameorigintype" VALUES(1,'Unknown',-1);
INSERT INTO "grampsdb_nameorigintype" VALUES(2,'Custom',0);
INSERT INTO "grampsdb_nameorigintype" VALUES(3,'',1);
INSERT INTO "grampsdb_nameorigintype" VALUES(4,'Inherited',2);
INSERT INTO "grampsdb_nameorigintype" VALUES(5,'Given',3);
INSERT INTO "grampsdb_nameorigintype" VALUES(6,'Taken',4);
INSERT INTO "grampsdb_nameorigintype" VALUES(7,'Patronymic',5);
INSERT INTO "grampsdb_nameorigintype" VALUES(8,'Matronymic',6);
INSERT INTO "grampsdb_nameorigintype" VALUES(9,'Feudal',7);
INSERT INTO "grampsdb_nameorigintype" VALUES(10,'Pseudonym',8);
INSERT INTO "grampsdb_nameorigintype" VALUES(11,'Patrilineal',9);
INSERT INTO "grampsdb_nameorigintype" VALUES(12,'Matrilineal',10);
INSERT INTO "grampsdb_nameorigintype" VALUES(13,'Occupation',11);
INSERT INTO "grampsdb_nameorigintype" VALUES(14,'Location',12);
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
INSERT INTO "grampsdb_config" VALUES(1,'db_version','database scheme version','str','0.5.1');
INSERT INTO "grampsdb_config" VALUES(2,'db_created','database creation date/time','str','2012-05-16 21:15');
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
INSERT INTO "grampsdb_person_families" VALUES(1,7,2);
INSERT INTO "grampsdb_person_families" VALUES(2,9,12);
INSERT INTO "grampsdb_person_families" VALUES(3,14,7);
INSERT INTO "grampsdb_person_families" VALUES(4,21,9);
INSERT INTO "grampsdb_person_families" VALUES(5,23,9);
INSERT INTO "grampsdb_person_families" VALUES(6,30,1);
INSERT INTO "grampsdb_person_families" VALUES(7,31,1);
INSERT INTO "grampsdb_person_families" VALUES(8,32,2);
INSERT INTO "grampsdb_person_families" VALUES(9,39,12);
INSERT INTO "grampsdb_person_families" VALUES(10,41,7);
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
INSERT INTO "grampsdb_person_parent_families" VALUES(1,1,5);
INSERT INTO "grampsdb_person_parent_families" VALUES(2,5,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(3,6,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(4,7,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(5,8,15);
INSERT INTO "grampsdb_person_parent_families" VALUES(6,11,4);
INSERT INTO "grampsdb_person_parent_families" VALUES(7,12,6);
INSERT INTO "grampsdb_person_parent_families" VALUES(8,13,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(9,15,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(10,16,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(11,17,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(12,19,3);
INSERT INTO "grampsdb_person_parent_families" VALUES(13,21,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(14,22,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(15,26,6);
INSERT INTO "grampsdb_person_parent_families" VALUES(16,29,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(17,31,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(18,33,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(19,34,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(20,35,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(21,36,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(22,37,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(23,39,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(24,40,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(25,41,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(26,42,14);
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
INSERT INTO "grampsdb_person" VALUES(1,'c29bcaa7c0b4b90f98e4129c911','I0035','2012-05-18 07:20:34.730884','2007-12-21 01:35:26',NULL,0,NULL,2,1,49,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(2,'c29bcaa7baf1333ac1e121fbc14','I0032','2012-05-18 07:20:34.991034','2007-12-21 01:35:26',NULL,0,NULL,3,1,53,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(3,'c29bcaa7cb766f21e8edf574482','I0038','2012-05-18 07:20:35.248736','2007-12-21 01:35:26',NULL,0,NULL,3,0,45,26,0,1);
INSERT INTO "grampsdb_person" VALUES(4,'c29bcaa7bef8cb476cb33d76e6','I0034','2012-05-18 07:20:35.502692','2007-12-21 01:35:26',NULL,0,NULL,3,1,78,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(5,'c29bcaa792f1f8b4496f40500ff','I0002','2012-05-18 07:20:35.741620','2007-12-21 01:35:26',NULL,0,NULL,3,1,60,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(6,'c29bcaa7d0d4b447dfc1598dea0','I0004','2012-05-18 07:20:35.963078','2007-12-21 01:35:26',NULL,0,NULL,2,1,54,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(7,'c29bcaa7877357b9d660ca91e39','I0015','2012-05-18 07:20:36.210754','2007-12-21 01:35:26',NULL,0,NULL,2,0,17,2,0,1);
INSERT INTO "grampsdb_person" VALUES(8,'c29bcaa7d8c410f2e0fbfcb779f','I0005','2012-05-18 07:20:36.463082','2007-12-21 01:35:26',NULL,0,NULL,2,1,64,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(9,'c29bcaa7de370652b6ab57247c3','I0006','2012-05-18 07:20:36.752631','2007-12-21 01:35:26',NULL,0,NULL,2,1,46,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(10,'c29bcaa7b6999e55c40f12e426','I0030','2012-05-18 07:20:36.997377','2007-12-21 01:35:26',NULL,0,NULL,3,1,27,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(11,'c29bcaa7cde3e5fdb19a1fe20c1','I0039','2012-05-18 07:20:37.255074','2007-12-21 01:35:26',NULL,0,NULL,2,0,16,29,0,1);
INSERT INTO "grampsdb_person" VALUES(12,'c29bcaa78e214c39c33959397c7','I0018','2012-05-18 07:20:37.508853','2007-12-21 01:35:26',NULL,0,NULL,2,1,44,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(13,'c29bcaa7dfc5599daa2f4a411e','I0007','2012-05-18 07:20:37.752581','2007-12-21 01:35:26',NULL,0,NULL,3,1,85,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(14,'c29bcaa78a34aba0f2cf1d70f1a','I0016','2012-05-18 07:20:38.026048','2007-12-21 01:35:26',NULL,0,NULL,3,0,10,66,0,1);
INSERT INTO "grampsdb_person" VALUES(15,'c29bcaa6a2c56593890bab8a506','I0001','2012-05-18 07:20:38.274904','2007-12-21 01:35:26',NULL,0,NULL,2,1,75,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(16,'c29bcaa7d3b5ad7f711072b13d0','I0040','2012-05-18 07:20:38.513354','2007-12-21 01:35:26',NULL,0,NULL,3,1,62,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(17,'c29bcaa79c9185b51e72e2386d3','I0022','2012-05-18 07:20:38.755057','2007-12-21 01:35:26',NULL,0,NULL,2,0,83,7,0,1);
INSERT INTO "grampsdb_person" VALUES(18,'c29bcaa78c710ed0dba2bda4d5f','I0017','2012-05-18 07:20:39.026837','2007-12-21 01:35:26',NULL,0,NULL,3,0,81,77,0,1);
INSERT INTO "grampsdb_person" VALUES(19,'c29bcaa77d67c31f25d475bb274','I0011','2012-05-18 07:20:39.274976','2007-12-21 01:35:26',NULL,0,NULL,3,1,33,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(20,'c29bcaa7c3a3a31f63407fa71c1','I0036','2012-05-18 07:20:39.521747','2007-12-21 01:35:26',NULL,0,NULL,3,0,24,42,0,1);
INSERT INTO "grampsdb_person" VALUES(21,'c29bcaa7a0757906cf42733d695','I0023','2012-05-18 07:20:39.777326','2007-12-21 01:35:26',NULL,0,NULL,3,0,84,51,0,1);
INSERT INTO "grampsdb_person" VALUES(22,'c29bcaa7e986f8a44e4a37d7dcd','I0009','2012-05-18 07:20:40.119251','2007-12-21 01:35:26',NULL,0,NULL,2,1,13,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(23,'c29bcaa78107bd26570165c362','I0012','2012-05-18 07:20:40.572494','2007-12-21 01:35:26',NULL,0,NULL,2,0,19,59,0,1);
INSERT INTO "grampsdb_person" VALUES(24,'c29bcaa7a801de03c8be42ce462','I0025','2012-05-18 07:20:40.874113','2007-12-21 01:35:26',NULL,0,NULL,3,1,50,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(25,'c29bcaa7b884d7e8361db690bb7','I0031','2012-05-18 07:20:41.160056','2007-12-21 01:35:26',NULL,0,NULL,3,0,32,35,0,1);
INSERT INTO "grampsdb_person" VALUES(26,'c29bcaa78563bbf9a8d6de8d222','I0014','2012-05-18 07:20:41.456956','2007-12-21 01:35:26',NULL,0,NULL,3,1,88,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(27,'c29bcaa686028208d00421bf659','I0000','2012-05-18 07:20:41.873240','2007-12-21 01:35:26',NULL,0,NULL,3,0,20,3,0,1);
INSERT INTO "grampsdb_person" VALUES(28,'c29bcaa7acd24b02bfbd0782026','I0027','2012-05-18 07:20:42.274140','2007-12-21 01:35:26',NULL,0,NULL,2,1,68,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(29,'c29bcaa7e2cd1b3a6ad3d42419','I0008','2012-05-18 07:20:42.587506','2007-12-21 01:35:26',NULL,0,NULL,2,0,28,38,0,1);
INSERT INTO "grampsdb_person" VALUES(30,'c29bcaa7ae8461a2d56c310eced','I0028','2012-05-18 07:20:42.832055','2007-12-21 01:35:26',NULL,0,NULL,3,0,40,65,0,1);
INSERT INTO "grampsdb_person" VALUES(31,'c29bcaa7b39256ab6d9cb0c7494','I0003','2012-05-18 07:20:43.074742','2007-12-21 01:35:26',NULL,0,NULL,2,0,48,11,0,1);
INSERT INTO "grampsdb_person" VALUES(32,'c29bcaa78442f0a213317c9bb74','I0013','2012-05-18 07:20:43.318468','2007-12-21 01:35:26',NULL,0,NULL,3,1,6,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(33,'c29bcaa7a3850355aafe6701a3a','I0024','2012-05-18 07:20:43.620954','2007-12-21 01:35:26',NULL,0,NULL,2,0,47,57,0,1);
INSERT INTO "grampsdb_person" VALUES(34,'c29bcaa7b1271397d0afaa7d696','I0029','2012-05-18 07:20:43.868010','2007-12-21 01:35:26',NULL,0,NULL,2,1,72,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(35,'c29bcaa7c6d1765b8f083e920f','I0037','2012-05-18 07:20:44.107415','2007-12-21 01:35:26',NULL,0,NULL,2,1,73,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(36,'c29bcaa79985ca8a669e4a813da','I0021','2012-05-18 07:20:44.354333','2007-12-21 01:35:26',NULL,0,NULL,2,0,55,91,0,1);
INSERT INTO "grampsdb_person" VALUES(37,'c29bcaa7bcb5d53ddc3cd9589f1','I0033','2012-05-18 07:20:44.596191','2007-12-21 01:35:26',NULL,0,NULL,2,1,25,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(38,'c29bcaa7d6d427d5a90140d2eb5','I0041','2012-05-18 07:20:44.830376','2007-12-21 01:35:26',NULL,0,NULL,3,1,1,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(39,'c29bcaa7a9d5721610d66559929','I0026','2012-05-18 07:20:45.059270','2007-12-21 01:35:26',NULL,0,NULL,3,0,41,30,0,1);
INSERT INTO "grampsdb_person" VALUES(40,'c29bcaa790313b224e1e73b4fdd','I0019','2012-05-18 07:20:45.290085','2007-12-21 01:35:26',NULL,0,NULL,2,1,90,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(41,'c29bcaa7739e9e0dae86660fdc','I0010','2012-05-18 07:20:45.637077','2007-12-21 01:35:26',NULL,0,NULL,2,0,89,63,0,1);
INSERT INTO "grampsdb_person" VALUES(42,'c29bcaa795f432082445d6084ce','I0020','2012-05-18 07:20:46.009808','2007-12-21 01:35:26',NULL,0,NULL,2,0,80,69,0,1);
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
INSERT INTO "grampsdb_family" VALUES(1,'c29bcaa7b0435050e62e7941401','F0011','2012-05-18 07:18:53.313040','2007-12-21 01:35:26',NULL,0,NULL,31,30,5);
INSERT INTO "grampsdb_family" VALUES(2,'c29bcaa784a6e396ebca67360a9','F0007','2012-05-18 07:19:19.684274','2007-12-21 01:35:26',NULL,0,NULL,7,32,5);
INSERT INTO "grampsdb_family" VALUES(3,'c29bcaa77f76dae850e62d2c49f','F0000','2012-05-18 07:19:20.778257','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(4,'c29bcaa7a8f6883d4a0ad68d700','F0001','2012-05-18 07:19:23.417362','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(5,'c29bcaa79235cda0d8a4f2d33f7','F0010','2012-05-18 07:19:24.644955','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(6,'c29bcaa7863611ed3fd0bc5e032','F0006','2012-05-18 07:19:25.492305','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(7,'c29bcaa778561bcc1293b856146','F0014','2012-05-18 07:19:27.864763','2007-12-21 01:35:26',NULL,0,NULL,41,14,1);
INSERT INTO "grampsdb_family" VALUES(8,'c29bcaa79f939e04b7975228ee1','F0002','2012-05-18 07:20:00.234380','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(9,'c29bcaa782c73371e35c472335e','F0005','2012-05-18 07:20:01.272370','2007-12-21 01:35:26',NULL,0,NULL,23,21,5);
INSERT INTO "grampsdb_family" VALUES(10,'c29bcaa6a413b3fbc25826b6bc','F0008','2012-05-18 07:20:07.472684','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(11,'c29bcaa7784204abe03533e7d3c','F0009','2012-05-18 07:20:08.951043','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(12,'c29bcaa7ac1386a183e3f74b380','F0004','2012-05-18 07:20:12.999362','2007-12-21 01:35:26',NULL,0,NULL,9,39,5);
INSERT INTO "grampsdb_family" VALUES(13,'c29bcaa78f8429892c2369e85cb','F0012','2012-05-18 07:20:18.555179','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(14,'c29bcaa68bf5983f5c39fe88b01','F0003','2012-05-18 07:20:19.462475','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
INSERT INTO "grampsdb_family" VALUES(15,'c29bcaa7948596835bcddae984e','F0013','2012-05-18 07:20:27.585014','1969-12-31 19:00:00',NULL,0,NULL,NULL,NULL,1);
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
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,1,'c29bcaa7fcb73ce7f57af97c7a0','C0002','2012-05-18 07:18:43.777089','1969-12-31 19:00:00',NULL,0,NULL,2,'',2);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,2,'c29bcaa7c792d7fca6b4f14d742','C0000','2012-05-18 07:19:58.251639','1969-12-31 19:00:00',NULL,0,NULL,2,'',1);
INSERT INTO "grampsdb_citation" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,3,'c29bcaa7c8e24463b8981edf2c9','C0001','2012-05-18 07:20:17.109373','1969-12-31 19:00:00',NULL,0,NULL,2,'',3);
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
INSERT INTO "grampsdb_source" VALUES(1,'c29bcaa7c79454d725ecfaa9d47','S0001','2012-05-18 07:17:52.887168','1969-12-31 19:00:00',NULL,0,NULL,'@S1@','','','');
INSERT INTO "grampsdb_source" VALUES(2,'c29bcaa7fca79ffd014971d1212','S0000','2012-05-18 07:18:21.591651','1969-12-31 19:00:00',NULL,0,NULL,'@S0@','','','');
INSERT INTO "grampsdb_source" VALUES(3,'c29bcaa7c8d66fae826018c120','S0003','2012-05-18 07:18:26.442221','1969-12-31 19:00:00',NULL,0,NULL,'@S3@','','','');
INSERT INTO "grampsdb_source" VALUES(4,'c29bcaa82a23cb0d3b85100dfb','S0002','2012-05-18 07:18:32.215731','2007-12-21 01:35:26',NULL,0,NULL,'Birth Records','','','');
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
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,12,1935,0,0,0,0,0,'2 DEC 1935',2428139,0,1,'c29bcaa7d72d909dcb67acc1af','E0067','2012-05-18 07:17:28.857151','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Janis Elaine Green',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,10,1963,0,0,0,0,0,'21 OCT 1963',2438324,0,2,'c29bcaa7884113297aa8932c98c','E0011','2012-05-18 07:18:41.273230','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Gus Smith',9);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,9,1945,0,0,0,0,0,'29 SEP 1945',2431728,0,3,'c29bcaa68a2cb867a664655897','E0001','2012-05-18 07:18:41.525853','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Anna Hansdotter',30);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,10,1927,0,0,0,0,0,'31 OCT 1927',2425185,0,4,'c29bcaa8180669446f6603e0c39','E0088','2012-05-18 07:18:41.781162','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Hjalmar Smith and Marjorie Ohman',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,6,1954,0,0,0,0,0,'4 JUN 1954',2434898,0,5,'c29bcaa7fb024ea97ef3b189e75','E0081','2012-05-18 07:18:45.219909','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of John Hjalmar Smith and Alice Paula Perkins',28);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1897,0,0,0,0,0,'ABT 1897',2413926,0,6,'c29bcaa7847404d209571adbd19','E0008','2012-05-18 07:17:31.457212','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Evelyn Michaels',NULL);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1899,0,0,0,1905,0,'BET 1899 AND 1905',2414656,0,7,'c29bcaa79d977c17a551e97e5c7','E0026','2012-05-18 07:18:47.350771','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Martin Smith',62);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1816,0,0,0,0,0,'ABT 1816',2384340,0,8,'c29bcaa7ebb16379851233ee3d2','E0077','2012-05-18 07:18:48.697324','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Martin Smith and Elna Jefferson',64);
INSERT INTO "grampsdb_event" VALUES(0,0,0,16,9,1800,0,0,0,0,0,'16 SEP 1800',2378755,0,9,'c29bcaa7c5468032b9044ef0cc9','E0056','2012-05-18 07:18:48.947868','1969-12-31 19:00:00',NULL,0,NULL,14,'Christening of Elna Jefferson',32);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,11,1907,0,0,0,0,0,'5 NOV 1907',2417885,0,10,'c29bcaa78a62462158fe4d08674','E0012','2012-05-18 07:18:49.196339','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Jennifer Anderson',26);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,2,1910,0,0,0,0,0,'20 FEB 1910',2418723,0,11,'c29bcaa7b484bae466761866bde','E0043','2012-05-18 07:18:49.451483','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Magnes Smith',53);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,7,1986,0,0,0,0,0,'12 JUL 1986',2446624,0,12,'c29bcaa7f4e43abb126fc4fa5fc','E0079','2012-05-18 07:18:51.519579','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Eric Lloyd Smith and Darcy Horne',45);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,9,1860,0,0,0,0,0,'27 SEP 1860',2400681,0,13,'c29bcaa7e9b6dde3d869f4254fd','E0076','2012-05-18 07:18:53.936960','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Emil Smith',3);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1979,0,0,0,1984,0,'BET 1979 AND 1984',2443875,0,14,'c29bcaa7c925bda63f827c13741','E0059','2012-05-18 07:18:57.088866','1969-12-31 19:00:00',NULL,0,NULL,18,'Education of Edwin Michael Smith',66);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,15,'c29bcaa7b207c749e0aeda78790','E0041','2012-05-18 07:17:37.963725','1969-12-31 19:00:00',NULL,0,NULL,13,'Census of Craig Peter Smith',NULL);
INSERT INTO "grampsdb_event" VALUES(0,4,0,0,0,1794,0,0,0,1796,0,'BET 1794 AND 1796',2376306,0,16,'c29bcaa7ce13faa2bc72ff2f3bd','E0063','2012-05-18 07:19:08.620751','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Martin Smith',48);
INSERT INTO "grampsdb_event" VALUES(0,0,0,11,9,1897,0,0,0,0,0,'11 SEP 1897',2414179,0,17,'c29bcaa787a1631494ecbb0e5d1','E0010','2012-05-18 07:19:08.880130','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Gus Smith',43);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1984,0,0,0,0,0,'1984',2445701,0,18,'c29bcaa7c9d1c28b79b80fe2404','E0060','2012-05-18 07:17:42.839544','1969-12-31 19:00:00',NULL,0,NULL,17,'B.S.E.E.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,8,1889,0,0,0,0,0,'31 AUG 1889',2411246,0,19,'c29bcaa7814202c4b14264cbb0a','E0006','2012-05-18 07:19:09.228800','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Herman Julius Nielsen',73);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,10,1864,0,0,0,0,0,'2 OCT 1864',2402147,0,20,'c29bcaa6878794b45ac051ce377','E0000','2012-05-18 07:19:09.580931','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Anna Hansdotter',35);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,10,1994,0,0,0,0,0,'5 OCT 1994',2449631,0,21,'c29bcaa80186fa66883e28aa45','E0083','2012-05-18 07:19:09.825235','1969-12-31 19:00:00',NULL,0,NULL,42,'Engagement of Edwin Michael Smith and Janice Ann Adams',58);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1856,0,0,0,0,0,'ABT 1856',2398950,0,22,'c29bcaa806b1a352ec8c855f8b8','E0084','2012-05-18 07:17:45.828298','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Martin Smith and Kerstina Hansdotter',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,11,1885,0,0,0,0,0,'27 NOV 1885',2409873,0,23,'c29bcaa80a211cf4eaf3cefce6f','E0085','2012-05-18 07:19:18.025342','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Gustaf Smith, Sr. and Anna Hansdotter',6);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,9,1800,0,0,0,0,0,'14 SEP 1800',2378753,0,24,'c29bcaa7c3e33af3605a8974b43','E0054','2012-05-18 07:19:20.302825','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Elna Jefferson',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,3,1935,0,0,0,0,0,'13 MAR 1935',2427875,0,25,'c29bcaa7bce5a2f2e1d0ff9d140','E0050','2012-05-18 07:19:20.537180','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Lloyd Smith',57);
INSERT INTO "grampsdb_event" VALUES(0,1,0,0,0,1908,0,0,0,0,0,'BEF 1908',2417942,0,26,'c29bcaa7cc6182969207ba000e4','E0062','2012-05-18 07:19:23.149246','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Kerstina Hansdotter',63);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,8,1965,0,0,0,0,0,'26 AUG 1965',2438999,0,27,'c29bcaa7b6c3beeb10fc21ea4e2','E0044','2012-05-18 07:19:23.915393','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Janice Ann Adams',14);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,4,1895,0,0,0,0,0,'7 APR 1895',2413291,0,28,'c29bcaa7e3245ce107cdb37b3e6','E0072','2012-05-18 07:19:24.160658','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Hjalmar Smith',68);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,29,'c29bcaa7cedd30af09d361cee9','E0064','2012-05-18 07:19:25.168792','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Martin Smith',38);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,7,1966,0,0,0,0,0,'18 JUL 1966',2439325,0,30,'c29bcaa7aac436466ec357bc072','E0036','2012-05-18 07:19:26.008551','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Kirsti Marie Smith',44);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,8,1958,0,0,0,0,0,'10 AUG 1958',2436426,0,31,'c29bcaa81df56782366f2acf47','E0090','2012-05-18 07:19:26.373606','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Lloyd Smith and Janis Elaine Green',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,3,6,1903,0,0,0,0,0,'3 JUN 1903',2416269,0,32,'c29bcaa7b8c68bfbbca6fe25c7a','E0047','2012-05-18 07:19:26.624000','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Marjorie Ohman',74);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1821,0,0,0,0,0,'29 JAN 1821',2386195,0,33,'c29bcaa77df377e541f0556fca4','E0005','2012-05-18 07:19:26.873211','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Hanna Smith',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,4,1998,0,0,0,0,0,'26 APR 1998',2450930,0,34,'c29bcaa793e4645f6cc6441143d','E0020','2012-05-18 07:19:27.114299','1969-12-31 19:00:00',NULL,0,NULL,14,'Christening of Amber Marie Smith',16);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,6,1980,0,0,0,0,0,'22 JUN 1980',2444413,0,35,'c29bcaa7b98767cb368d384b2d7','E0048','2012-05-18 07:19:27.362473','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Marjorie Ohman',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,30,11,1912,0,0,0,0,0,'30 NOV 1912',2419737,0,36,'c29bcaa815417da228ee0d80765','E0087','2012-05-18 07:19:27.613808','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Herman Julius Nielsen and Astrid Shermanna Augusta Smith',61);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1910,0,0,0,0,0,'ABT 1910',2418673,0,37,'c29bcaa8135eb94c3e7a266af9','E0086','2012-05-18 07:17:56.845074','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Edwin Willard and Kirsti Marie Smith',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1975,0,0,0,0,0,'26 JUN 1975',2442590,0,38,'c29bcaa7e4021e418d9b0db8385','E0073','2012-05-18 07:19:28.119165','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Hjalmar Smith',25);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1920,0,0,0,0,0,'ABT 1920',2422325,0,39,'c29bcaa81c92444a4d1ea7efd96','E0089','2012-05-18 07:18:00.437910','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Gus Smith and Evelyn Michaels',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,9,1860,0,0,0,0,0,'23 SEP 1860',2400677,0,40,'c29bcaa7aec51193fc4576c4ff3','E0038','2012-05-18 07:19:38.884796','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Anna Streiffert',52);
INSERT INTO "grampsdb_event" VALUES(0,0,0,15,12,1886,0,0,0,0,0,'15 DEC 1886',2410256,0,41,'c29bcaa7aa015cf90b41aee35d','E0035','2012-05-18 07:19:39.132802','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Kirsti Marie Smith',39);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,42,'c29bcaa7c49564ae5c3c0f71e95','E0055','2012-05-18 07:19:40.898407','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Elna Jefferson',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,5,1995,0,0,0,0,0,'27 MAY 1995',2449865,0,43,'c29bcaa800549e06fb56199879f','E0082','2012-05-18 07:19:42.632124','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Edwin Michael Smith and Janice Ann Adams',41);
INSERT INTO "grampsdb_event" VALUES(0,0,0,30,1,1932,0,0,0,0,0,'30 JAN 1932',2426737,0,44,'c29bcaa78e51be432cb47a267fd','E0016','2012-05-18 07:19:44.185015','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of John Hjalmar Smith',40);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,11,1832,0,0,0,0,0,'29 NOV 1832',2390517,0,45,'c29bcaa7cbb2669842335f8efc','E0061','2012-05-18 07:19:44.561366','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Kerstina Hansdotter',13);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1886,0,0,0,0,0,'ABT 1886',2409908,0,46,'c29bcaa7de75fd353339c6d6983','E0070','2012-05-18 07:18:07.756488','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Edwin Willard',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,11,1862,0,0,0,0,0,'28 NOV 1862',2401473,0,47,'c29bcaa7a3b41cbf6be7ff4753e','E0030','2012-05-18 07:19:47.418099','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Gustaf Smith, Sr.',5);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,10,1858,0,0,0,0,0,'6 OCT 1858',2399959,0,48,'c29bcaa7b3c341faf3fc5d1ffc8','E0042','2012-05-18 07:19:53.079221','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Magnes Smith',29);
INSERT INTO "grampsdb_event" VALUES(0,0,0,16,9,1991,0,0,0,0,0,'16 SEP 1991',2448516,0,49,'c29bcaa7c0e1830ef34dae0c260','E0052','2012-05-18 07:19:53.379327','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Lars Peter Smith',71);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1775,0,0,0,0,0,'ABT 1775',2369366,0,50,'c29bcaa7a844a9736e92fdc2e4c','E0034','2012-05-18 07:19:53.737296','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Marta Ericsdotter',69);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,12,1963,0,0,0,0,0,'21 DEC 1963',2438385,0,51,'c29bcaa7a16752b909989790265','E0029','2012-05-18 07:19:54.041997','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Astrid Shermanna Augusta Smith',75);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,11,1830,0,0,0,0,0,'23 NOV 1830',2389780,0,52,'c29bcaa79e53a0d714a4e62073b','E0027','2012-05-18 07:19:54.341017','1969-12-31 19:00:00',NULL,0,NULL,7,'Baptism of Martin Smith',70);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,7,1966,0,0,0,0,0,'2 JUL 1966',2439309,0,53,'c29bcaa7bb34b24550ced938667','E0049','2012-05-18 07:19:54.639828','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Darcy Horne',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1826,0,0,0,0,0,'29 JAN 1826',2388021,0,54,'c29bcaa7d116fcc714cf8311504','E0065','2012-05-18 07:19:54.891093','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Ingeman Smith',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,1,1893,0,0,0,0,0,'31 JAN 1893',2412495,0,55,'c29bcaa799c69f8363aa6b49aea','E0023','2012-05-18 07:19:55.271838','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Hjalmar Smith',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,3,6,1895,0,0,0,0,0,'3 JUN 1895',2413348,0,56,'c29bcaa7e544a34f8543e7d0123','E0074','2012-05-18 07:19:55.568060','1969-12-31 19:00:00',NULL,0,NULL,7,'Baptism of Hjalmar Smith',4);
INSERT INTO "grampsdb_event" VALUES(0,1,0,23,7,1930,0,0,0,0,0,'BEF 23 JUL 1930',2426181,0,57,'c29bcaa7a47636ee97841ee179c','E0031','2012-05-18 07:19:55.876246','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Gustaf Smith, Sr.',72);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,12,1862,0,0,0,0,0,'7 DEC 1862',2401482,0,58,'c29bcaa7a5e6b73c273ffe59760','E0033','2012-05-18 07:19:57.240468','1969-12-31 19:00:00',NULL,0,NULL,14,'Christening of Gustaf Smith, Sr.',54);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1945,0,0,0,0,0,'1945',2431457,0,59,'c29bcaa78252080880478abda7b','E0007','2012-05-18 07:18:16.138861','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Herman Julius Nielsen',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,4,1998,0,0,0,0,0,'12 APR 1998',2450916,0,60,'c29bcaa793334529e4ebe34bc5f','E0019','2012-05-18 07:19:57.487849','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Amber Marie Smith',60);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,61,'c29bcaa791015aa50f613217253','E0018','2012-05-18 07:18:17.877408','1969-12-31 19:00:00',NULL,0,NULL,3,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,5,2,1960,0,0,0,0,0,'5 FEB 1960',2436970,0,62,'c29bcaa7d4019b4021bf4aafe0e','E0066','2012-05-18 07:19:57.726831','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Marjorie Alice Smith',34);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,1,1977,0,0,0,0,0,'29 JAN 1977',2443173,0,63,'c29bcaa775c1d1fff53ba16b993','E0004','2012-05-18 07:19:57.995975','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Hans Peter Smith',56);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1996,0,0,0,0,0,'26 JUN 1996',2450261,0,64,'c29bcaa7d936b8c9989df17eee9','E0068','2012-05-18 07:19:59.984977','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Mason Michael Smith',59);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,2,1927,0,0,0,0,0,'2 FEB 1927',2424914,0,65,'c29bcaa7af9324c1a68199e5f88','E0039','2012-05-18 07:20:00.735277','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Anna Streiffert',55);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,5,1985,0,0,0,0,0,'29 MAY 1985',2446215,0,66,'c29bcaa78b12b0ef03aad4358c8','E0013','2012-05-18 07:20:00.989372','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Jennifer Anderson',76);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,67,'c29bcaa7c1955130474c3aea77c','E0053','2012-05-18 07:18:20.677396','1969-12-31 19:00:00',NULL,0,NULL,3,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1770,0,0,0,0,0,'ABT 1770',2367540,0,68,'c29bcaa7ad141728cb89824e22c','E0037','2012-05-18 07:20:04.416039','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Ingeman Smith',46);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,1,1959,0,0,0,0,0,'28 JAN 1959',2436597,0,69,'c29bcaa796d79e823713474061f','E0022','2012-05-18 07:20:04.661639','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Carl Emil Smith',50);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,70,'c29bcaa7b783a4c502b3a4ffbe6','E0045','2012-05-18 07:18:24.060249','1969-12-31 19:00:00',NULL,0,NULL,29,'Retail Manager',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1988,0,0,0,0,0,'1988',2447162,0,71,'c29bcaa7b7a7eba8a6c282f96b9','E0046','2012-05-18 07:18:25.127623','1969-12-31 19:00:00',NULL,0,NULL,17,'Business Management',NULL);
INSERT INTO "grampsdb_event" VALUES(0,2,0,0,0,1966,0,0,0,0,0,'AFT 1966',2439127,0,72,'c29bcaa7b157cff8fa9362a14ee','E0040','2012-05-18 07:20:07.962308','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Craig Peter Smith',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,5,1961,0,0,0,0,0,'24 MAY 1961',2437444,0,73,'c29bcaa7c7b381a32a386570af2','E0057','2012-05-18 07:20:08.308622','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Edwin Michael Smith',42);
INSERT INTO "grampsdb_event" VALUES(0,3,0,0,0,1790,0,0,0,0,0,'ABT 1790',2374845,0,74,'c29bcaa7f123a1048053efae85d','E0078','2012-05-18 07:20:09.628422','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Ingeman Smith and Marta Ericsdotter',47);
INSERT INTO "grampsdb_event" VALUES(0,0,0,11,8,1966,0,0,0,0,0,'11 AUG 1966',2439349,0,75,'c29bcaa6a353e817665d7c695cb','E0002','2012-05-18 07:20:09.865615','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Keith Lloyd Smith',37);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,11,1912,0,0,0,0,0,'14 NOV 1912',2419721,0,76,'c29bcaa7e6855cf5167c08132ea','E0075','2012-05-18 07:20:13.506669','1969-12-31 19:00:00',NULL,0,NULL,47,'',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,6,1990,0,0,0,0,0,'26 JUN 1990',2448069,0,77,'c29bcaa78d459bfac8c51e13307','E0015','2012-05-18 07:18:29.244042','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Lillie Harriet Jones',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1933,0,0,0,0,0,'22 NOV 1933',2427399,0,78,'c29bcaa7bf33787f4422f2c9d10','E0051','2012-05-18 07:20:14.020522','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Alice Paula Perkins',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,7,1996,0,0,0,0,0,'10 JUL 1996',2450275,0,79,'c29bcaa7da84804cbc19cdeb775','E0069','2012-05-18 07:20:14.309265','1969-12-31 19:00:00',NULL,0,NULL,14,'Christening of Mason Michael Smith',24);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,12,1899,0,0,0,0,0,'20 DEC 1899',2415009,0,80,'c29bcaa7962aebe547aec653af','E0021','2012-05-18 07:20:14.628994','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Carl Emil Smith',51);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,5,1910,0,0,0,0,0,'2 MAY 1910',2418794,0,81,'c29bcaa78ca887e00af51e7a7f','E0014','2012-05-18 07:20:17.440182','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Lillie Harriet Jones',15);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,82,'c29bcaa7c8f66ced8f6d4b162a2','E0058','2012-05-18 07:18:31.988350','1969-12-31 19:00:00',NULL,0,NULL,29,'Software Engineer',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,19,11,1830,0,0,0,0,0,'19 NOV 1830',2389776,0,83,'c29bcaa79ce3273cb2754ded053','E0025','2012-05-18 07:20:18.097725','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Martin Smith',27);
INSERT INTO "grampsdb_event" VALUES(0,0,0,31,1,1889,0,0,0,0,0,'31 JAN 1889',2411034,0,84,'c29bcaa7a0a57cc28959b91510','E0028','2012-05-18 07:20:22.617512','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Astrid Shermanna Augusta Smith',31);
INSERT INTO "grampsdb_event" VALUES(0,2,0,0,0,1823,0,0,0,0,0,'AFT 1823',2386897,0,85,'c29bcaa7dff174e31e62cbbd00b','E0071','2012-05-18 07:20:22.874061','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Ingar Smith',33);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,8,1884,0,0,0,0,0,'24 AUG 1884',2409413,0,86,'c29bcaa7f8b60eebd7fec8b61c9','E0080','2012-05-18 07:20:27.329222','1969-12-31 19:00:00',NULL,0,NULL,37,'Marriage of Magnes Smith and Anna Streiffert',36);
INSERT INTO "grampsdb_event" VALUES(0,0,0,21,5,1908,0,0,0,0,0,'21 MAY 1908',2418083,0,87,'c29bcaa7a527178a4e8fa9fdf29','E0032','2012-05-18 07:20:31.639766','1969-12-31 19:00:00',NULL,0,NULL,47,'',67);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,11,1934,0,0,0,0,0,'4 NOV 1934',2427746,0,88,'c29bcaa785941a13e1860effcd8','E0009','2012-05-18 07:20:31.923390','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Marjorie Lee Smith',49);
INSERT INTO "grampsdb_event" VALUES(0,0,0,17,4,1904,0,0,0,0,0,'17 APR 1904',2416588,0,89,'c29bcaa774358c8cf9ad284beaf','E0003','2012-05-18 07:20:33.953701','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Hans Peter Smith',11);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,8,1963,0,0,0,0,0,'28 AUG 1963',2438270,0,90,'c29bcaa79065726a044c91640ba','E0017','2012-05-18 07:20:34.206128','1969-12-31 19:00:00',NULL,0,NULL,4,'Birth of Eric Lloyd Smith',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,9,1894,0,0,0,0,0,'25 SEP 1894',2413097,0,91,'c29bcaa79a78647c394e856178','E0024','2012-05-18 07:20:34.464239','1969-12-31 19:00:00',NULL,0,NULL,5,'Death of Hjalmar Smith',65);
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
INSERT INTO "grampsdb_repository" VALUES(1,'c29bcaa82f15b0f3ce4b469059a','R0003','2012-05-18 07:18:09.673078','1969-12-31 19:00:00',NULL,0,NULL,3,'Aunt Martha''s Attic');
INSERT INTO "grampsdb_repository" VALUES(2,'c29bcaa826c5cefc40e3728ae3f','R0002','2012-05-18 07:18:15.261912','1969-12-31 19:00:00',NULL,0,NULL,3,'New York Public Library');
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
INSERT INTO "grampsdb_place" VALUES(1,'c29bcaa81eb47e80f59249a756b','P0099','2012-05-18 07:17:28.472868','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(2,'c29bcaa7bbd6c57c63278a0c577','P0058','2012-05-18 07:17:29.828153','1969-12-31 19:00:00',NULL,0,NULL,'Sacramento, Sacramento Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(3,'c29bcaa7ea427b9a4f67d9ff29','P0086','2012-05-18 07:17:33.283453','1969-12-31 19:00:00',NULL,0,NULL,'Simrishamn, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(4,'c29bcaa7e64763e274b232fd7b8','P0084','2012-05-18 07:17:33.539083','1969-12-31 19:00:00',NULL,0,NULL,'Ronne Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(5,'c29bcaa7a4515213a12b8a7bdee','P0036','2012-05-18 07:17:34.839168','1969-12-31 19:00:00',NULL,0,NULL,'Grostorp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(6,'c29bcaa80b27eace2e509e44292','P0096','2012-05-18 07:17:35.909950','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(7,'c29bcaa7c512d04d3dd08c4d4d5','P0064','2012-05-18 07:17:36.143164','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(8,'c29bcaa7d1a4ba21e01caeb4f8c','P0076','2012-05-18 07:17:36.983503','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(9,'c29bcaa788d47cc82c7ae80e1dd','P0015','2012-05-18 07:17:37.227756','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(10,'c29bcaa79a643cedaf99fbe27da','P0027','2012-05-18 07:17:37.472364','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(11,'c29bcaa775861e3c2c9ab88e034','P0007','2012-05-18 07:17:38.432053','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(12,'c29bcaa7b1f79085ee56b00449','P0048','2012-05-18 07:17:40.194653','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(13,'c29bcaa7cc54f59469973267301','P0071','2012-05-18 07:17:40.437068','1969-12-31 19:00:00',NULL,0,NULL,'Smestorp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(14,'c29bcaa7b76589a053927a3b113','P0053','2012-05-18 07:17:41.550324','1969-12-31 19:00:00',NULL,0,NULL,'Fremont, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(15,'c29bcaa78d3694ab7ee708fbc77','P0018','2012-05-18 07:17:42.514968','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(16,'c29bcaa7946147e79213ca2bc86','P0024','2012-05-18 07:17:45.594412','1969-12-31 19:00:00',NULL,0,NULL,'Community Presbyterian Church, Danville, CA','','');
INSERT INTO "grampsdb_place" VALUES(17,'c29bcaa7e783bced1a85b8838c','P0085','2012-05-18 07:17:46.070146','1969-12-31 19:00:00',NULL,0,NULL,'Copenhagen, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(18,'c29bcaa7bfce2770d1f95d42ae','P0060','2012-05-18 07:17:46.948034','1969-12-31 19:00:00',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(19,'c29bcaa790f6e85543dc61caa07','P0020','2012-05-18 07:17:47.747936','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(20,'c29bcaa7ba1ee1414bb0c92a69','P0056','2012-05-18 07:17:48.836847','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(21,'c29bcaa7c4711bdba13a1bb95ef','P0063','2012-05-18 07:17:49.570257','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(22,'c29bcaa81916936d8a700926873','P0098','2012-05-18 07:17:52.209781','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(23,'c29bcaa77f35f83b66aec85e647','P0010','2012-05-18 07:17:53.181186','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(24,'c29bcaa7dba4991acc7f804f8f2','P0079','2012-05-18 07:17:53.458976','1969-12-31 19:00:00',NULL,0,NULL,'Community Presbyterian Church, Danville, CA','','');
INSERT INTO "grampsdb_place" VALUES(25,'c29bcaa7e4f28ab40719375d60f','P0082','2012-05-18 07:17:55.175015','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(26,'c29bcaa78af2fd875a6fe8e78a2','P0016','2012-05-18 07:17:55.564935','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(27,'c29bcaa79d751a7444d1ea4ef93','P0029','2012-05-18 07:17:57.131460','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(28,'c29bcaa7fbc1d5044b9bf9050d7','P0092','2012-05-18 07:17:57.442555','1969-12-31 19:00:00',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(29,'c29bcaa7b465131b38b4276bb68','P0050','2012-05-18 07:18:00.122356','1969-12-31 19:00:00',NULL,0,NULL,'Simrishamn, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(30,'c29bcaa68bc6665b070e61347f4','P0003','2012-05-18 07:18:00.781091','1969-12-31 19:00:00',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(31,'c29bcaa7a1410d10c9aafac9b68','P0033','2012-05-18 07:18:01.020328','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(32,'c29bcaa7c5d53ef9c33ebf16d88','P0065','2012-05-18 07:18:01.498021','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(33,'c29bcaa7e0c39b25e57a09fbcaa','P0080','2012-05-18 07:18:01.736578','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(34,'c29bcaa7d4d5571fd2a7279782c','P0077','2012-05-18 07:18:02.038418','1969-12-31 19:00:00',NULL,0,NULL,'San Jose, Santa Clara Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(35,'c29bcaa689f1114459942cbb3a0','P0001','2012-05-18 07:18:03.264808','1969-12-31 19:00:00',NULL,0,NULL,'Loderup, Malmous Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(36,'c29bcaa7f9c131c9a3f815ba618','P0091','2012-05-18 07:18:03.953568','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(37,'c29bcaa6a3f6e1cc12f1d1073c9','P0005','2012-05-18 07:18:04.431376','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(38,'c29bcaa7cf6bc6a487a6383b5','P0075','2012-05-18 07:18:05.045469','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(39,'c29bcaa7aaa2a1a830cad39f9b5','P0042','2012-05-18 07:18:07.009246','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(40,'c29bcaa78ed640a41d219da731f','P0019','2012-05-18 07:18:07.498190','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(41,'c29bcaa80155ad4f67ba7914c22','P0094','2012-05-18 07:18:08.409222','1969-12-31 19:00:00',NULL,0,NULL,'San Ramon, Conta Costa Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(42,'c29bcaa7c854a6235ce64542c31','P0067','2012-05-18 07:18:10.681113','1969-12-31 19:00:00',NULL,0,NULL,'San Jose, Santa Clara Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(43,'c29bcaa788249582fba76d1809c','P0014','2012-05-18 07:18:13.620103','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(44,'c29bcaa7ab559029b299e6d7911','P0043','2012-05-18 07:18:13.931305','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(45,'c29bcaa7f60789ed82181ea2e2','P0090','2012-05-18 07:18:15.010616','1969-12-31 19:00:00',NULL,0,NULL,'Woodland, Yolo Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(46,'c29bcaa7adb5728f0c9b8a5ad8f','P0044','2012-05-18 07:18:16.831445','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(47,'c29bcaa7f2340753851874030f8','P0088','2012-05-18 07:18:17.086647','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(48,'c29bcaa7ceb3665e94b6af6e939','P0074','2012-05-18 07:18:17.331138','1969-12-31 19:00:00',NULL,0,NULL,'Tommarp, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(49,'c29bcaa78626c2fa23e6fe7d92c','P0013','2012-05-18 07:18:21.331088','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(50,'c29bcaa797620c05667f592957e','P0026','2012-05-18 07:18:21.836205','1969-12-31 19:00:00',NULL,0,NULL,'Reno, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(51,'c29bcaa796b71e4c698bd1d4354','P0025','2012-05-18 07:18:22.319813','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(52,'c29bcaa7af724d79b053af499c5','P0046','2012-05-18 07:18:22.930992','1969-12-31 19:00:00',NULL,0,NULL,'Hoya/Jona/Hoia, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(53,'c29bcaa7b51d54b9aedefb5f','P0051','2012-05-18 07:18:23.242148','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(54,'c29bcaa7a68795cd548877aa122','P0040','2012-05-18 07:18:23.482587','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(55,'c29bcaa7b021eefb7cfe0e04264','P0047','2012-05-18 07:18:25.825159','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(56,'c29bcaa777062811119837c135e','P0008','2012-05-18 07:18:27.149228','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(57,'c29bcaa7bd85ce6471141b8cf56','P0059','2012-05-18 07:18:28.682386','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(58,'c29bcaa802a1211490d2d845e7c','P0095','2012-05-18 07:18:28.926839','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(59,'c29bcaa7da61d694cc3c2aef46c','P0078','2012-05-18 07:18:29.537402','1969-12-31 19:00:00',NULL,0,NULL,'Hayward, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(60,'c29bcaa793b87dba9e3240ae53','P0022','2012-05-18 07:18:30.004857','1969-12-31 19:00:00',NULL,0,NULL,'Hayward, Alameda Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(61,'c29bcaa81653db200dfb4299256','P0097','2012-05-18 07:18:30.238078','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(62,'c29bcaa79e224cc29235fa750f6','P0031','2012-05-18 07:18:31.160239','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(63,'c29bcaa7cd01f963d5ae03401d4','P0072','2012-05-18 07:18:33.035090','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(64,'c29bcaa7ec473bc0abb7a8b1366','P0087','2012-05-18 07:18:33.886377','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(65,'c29bcaa79b255a8abbd85cea4f1','P0028','2012-05-18 07:18:35.037932','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(66,'c29bcaa7c9c4a88475fb9c522e7','P0069','2012-05-18 07:18:35.869276','1969-12-31 19:00:00',NULL,0,NULL,'UC Berkeley','','');
INSERT INTO "grampsdb_place" VALUES(67,'c29bcaa7a5c48a4e235d0b1dc9d','P0039','2012-05-18 07:18:37.253007','1969-12-31 19:00:00',NULL,0,NULL,'Copenhagen, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(68,'c29bcaa7e3e13eaf1ebe8d6b26f','P0081','2012-05-18 07:18:37.502639','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(69,'c29bcaa7a8d3bf78ead4b56d060','P0041','2012-05-18 07:18:37.808472','1969-12-31 19:00:00',NULL,0,NULL,'Sweden','','');
INSERT INTO "grampsdb_place" VALUES(70,'c29bcaa79ed5a48455d5794c8ca','P0032','2012-05-18 07:18:38.480448','1969-12-31 19:00:00',NULL,0,NULL,'Gladsax, Kristianstad Lan, Sweden','','');
INSERT INTO "grampsdb_place" VALUES(71,'c29bcaa7c18230dacfbd6a0cf19','P0062','2012-05-18 07:18:38.825032','1969-12-31 19:00:00',NULL,0,NULL,'Santa Rosa, Sonoma Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(72,'c29bcaa7a5188866ee68d61ab6','P0037','2012-05-18 07:18:39.078278','1969-12-31 19:00:00',NULL,0,NULL,'Sparks, Washoe Co., NV','','');
INSERT INTO "grampsdb_place" VALUES(73,'c29bcaa78225303a057e38836cc','P0011','2012-05-18 07:18:39.575097','1969-12-31 19:00:00',NULL,0,NULL,'Ronne, Bornholm, Denmark','','');
INSERT INTO "grampsdb_place" VALUES(74,'c29bcaa7b95aef5d98fd361156','P0055','2012-05-18 07:18:39.813612','1969-12-31 19:00:00',NULL,0,NULL,'Denver, Denver Co., CO','','');
INSERT INTO "grampsdb_place" VALUES(75,'c29bcaa7a1f535131b55993d85f','P0034','2012-05-18 07:18:40.286290','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
INSERT INTO "grampsdb_place" VALUES(76,'c29bcaa78b9290ebbebeb7e75b2','P0017','2012-05-18 07:18:40.775180','1969-12-31 19:00:00',NULL,0,NULL,'San Francisco, San Francisco Co., CA','','');
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
INSERT INTO "grampsdb_note" VALUES(1,'c29bcaa7b2174c50456b9ca864c','N0000','2012-05-18 07:17:31.719213','1969-12-31 19:00:00',NULL,0,NULL,3,'Witness name: John Doe
Witness comment: This is a simple test.',0);
INSERT INTO "grampsdb_note" VALUES(2,'c29bcaa82703a77064e960b8597','N0004','2012-05-18 07:17:35.089796','1969-12-31 19:00:00',NULL,0,NULL,3,'But Aunt Martha still keeps the original!',0);
INSERT INTO "grampsdb_note" VALUES(3,'c29bcaa7e8c1771ab0c5efa03a5','N0003','2012-05-18 07:17:44.194537','1969-12-31 19:00:00',NULL,0,NULL,3,'BIOGRAPHY

Hjalmar sailed from Copenhagen, Denmark on the OSCAR II, 14 November 1912 arriving in New York 27 November 1912. He was seventeen years old. On the ship passenger list his trade was listed as a Blacksmith.  He came to Reno, Nevada and lived with his sister Marie for a time before settling in Sparks. He worked for Southern Pacific Railroad as a car inspector for a time, then went to work for Standard Oil
Company. He enlisted in the army at Sparks 7 December 1917 and served as a Corporal in the Medical Corp until his discharge 12 August 1919 at the Presidio in San Francisco, California. Both he and Marjorie are buried in the Masonic Memorial Gardens Mausoleum in Reno, he the 30th June 1975, and she the 25th of June 1980.',0);
INSERT INTO "grampsdb_note" VALUES(4,'c29bcaa82c83945672eb263a65c','N0005','2012-05-18 07:17:49.338336','1969-12-31 19:00:00',NULL,0,NULL,3,'The repository reference from the source is important',0);
INSERT INTO "grampsdb_note" VALUES(5,'c29bcaa7c91376659a182b733bf','N0001','2012-05-18 07:17:51.000304','1969-12-31 19:00:00',NULL,0,NULL,3,'Witness name: No Name',0);
INSERT INTO "grampsdb_note" VALUES(6,'c29bcaa68491d1dfd4d6b565d22','N0000','2012-05-18 07:17:58.031720','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SUBM (Submitter): @SUBM@:

Warn: ADDR overwritten             Line    19: 2 ADR1 Not Provided
',0);
INSERT INTO "grampsdb_note" VALUES(7,'c29bcaa832520d40f03ae83e631','N0003','2012-05-18 07:18:01.260908','1969-12-31 19:00:00',NULL,0,NULL,3,'Objects referenced by this note were missing in a file imported on 05/18/2012 07:17:28 AM.',0);
INSERT INTO "grampsdb_note" VALUES(8,'c29bcaa79fa4bfe6f9f9ee3e361','N0002','2012-05-18 07:18:04.199433','1969-12-31 19:00:00',NULL,0,NULL,3,'BIOGRAPHY
Martin was listed as being a Husman, (owning a house as opposed to a farm) in the house records of Gladsax.',0);
INSERT INTO "grampsdb_note" VALUES(9,'c29bcaa82fa2f0fdb0eaf79f6cb','N0006','2012-05-18 07:18:05.759984','1969-12-31 19:00:00',NULL,0,NULL,3,'Some note on the repo',0);
INSERT INTO "grampsdb_note" VALUES(10,'c29bcaa82ff2d5a920be629ab62','N0002','2012-05-18 07:18:12.167132','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into REPO (repository) Gramps ID R0003:

Warn: ADDR overwritten             Line   918: 2 ADR1 123 Main St
',0);
INSERT INTO "grampsdb_note" VALUES(11,'c29bcaa82e567863d5ec7367566','N0001','2012-05-18 07:18:19.093462','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into REPO (repository) Gramps ID R0002:

Warn: ADDR overwritten             Line   910: 2 ADR1 5th Ave at 42 street
',0);
CREATE TABLE "grampsdb_surname" (
    "id" integer NOT NULL PRIMARY KEY,
    "name_origin_type_id" integer NOT NULL REFERENCES "grampsdb_nameorigintype" ("id"),
    "surname" text NOT NULL,
    "prefix" text NOT NULL,
    "primary" bool NOT NULL,
    "connector" text NOT NULL,
    "name_id" integer NOT NULL
);
INSERT INTO "grampsdb_surname" VALUES(1,3,'Smith','',1,'',1);
INSERT INTO "grampsdb_surname" VALUES(2,3,'Horne','',1,'',2);
INSERT INTO "grampsdb_surname" VALUES(3,3,'Hansdotter','',1,'',3);
INSERT INTO "grampsdb_surname" VALUES(4,3,'Perkins','',1,'',4);
INSERT INTO "grampsdb_surname" VALUES(5,3,'Smith','',1,'',5);
INSERT INTO "grampsdb_surname" VALUES(6,3,'Smith','',1,'',6);
INSERT INTO "grampsdb_surname" VALUES(7,3,'Smith','',1,'',7);
INSERT INTO "grampsdb_surname" VALUES(8,3,'Smith','',1,'',8);
INSERT INTO "grampsdb_surname" VALUES(9,3,'Willard','',1,'',9);
INSERT INTO "grampsdb_surname" VALUES(10,3,'Adams','',1,'',10);
INSERT INTO "grampsdb_surname" VALUES(11,3,'Smith','',1,'',11);
INSERT INTO "grampsdb_surname" VALUES(12,3,'Smith','',1,'',12);
INSERT INTO "grampsdb_surname" VALUES(13,3,'Smith','',1,'',13);
INSERT INTO "grampsdb_surname" VALUES(14,3,'Anderson','',1,'',14);
INSERT INTO "grampsdb_surname" VALUES(15,3,'Smith','',1,'',15);
INSERT INTO "grampsdb_surname" VALUES(16,3,'Smith','',1,'',16);
INSERT INTO "grampsdb_surname" VALUES(17,3,'Smith','',1,'',17);
INSERT INTO "grampsdb_surname" VALUES(18,3,'Jones','',1,'',18);
INSERT INTO "grampsdb_surname" VALUES(19,3,'Smith','',1,'',19);
INSERT INTO "grampsdb_surname" VALUES(20,3,'Jefferson','',1,'',20);
INSERT INTO "grampsdb_surname" VALUES(21,3,'Smith','',1,'',21);
INSERT INTO "grampsdb_surname" VALUES(22,3,'Smith','',1,'',22);
INSERT INTO "grampsdb_surname" VALUES(23,3,'Nielsen','',1,'',23);
INSERT INTO "grampsdb_surname" VALUES(24,3,'Ericsdotter','',1,'',24);
INSERT INTO "grampsdb_surname" VALUES(25,3,'Ohman','',1,'',25);
INSERT INTO "grampsdb_surname" VALUES(26,3,'Smith','',1,'',26);
INSERT INTO "grampsdb_surname" VALUES(27,3,'Hansdotter','',1,'',27);
INSERT INTO "grampsdb_surname" VALUES(28,3,'Smith','',1,'',28);
INSERT INTO "grampsdb_surname" VALUES(29,3,'Smith','',1,'',29);
INSERT INTO "grampsdb_surname" VALUES(30,3,'Streiffert','',1,'',30);
INSERT INTO "grampsdb_surname" VALUES(31,3,'Smith','',1,'',31);
INSERT INTO "grampsdb_surname" VALUES(32,3,'Michaels','',1,'',32);
INSERT INTO "grampsdb_surname" VALUES(33,3,'Smith','',1,'',33);
INSERT INTO "grampsdb_surname" VALUES(34,3,'Smith','',1,'',34);
INSERT INTO "grampsdb_surname" VALUES(35,3,'Smith','',1,'',35);
INSERT INTO "grampsdb_surname" VALUES(36,3,'Smith','',1,'',36);
INSERT INTO "grampsdb_surname" VALUES(37,3,'Smith','',1,'',37);
INSERT INTO "grampsdb_surname" VALUES(38,3,'Green','',1,'',38);
INSERT INTO "grampsdb_surname" VALUES(39,3,'Smith','',1,'',39);
INSERT INTO "grampsdb_surname" VALUES(40,3,'Smith','',1,'',40);
INSERT INTO "grampsdb_surname" VALUES(41,3,'Smith','',1,'',41);
INSERT INTO "grampsdb_surname" VALUES(42,3,'Smith','',1,'',42);
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
INSERT INTO "grampsdb_name" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:42.029903',NULL,NULL,1,4,1,'Lars Peter','','','','','','',1,1,1);
INSERT INTO "grampsdb_name" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:44.040145',NULL,NULL,1,4,1,'Darcy','','','','','','',1,1,2);
INSERT INTO "grampsdb_name" VALUES(3,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:45.796407',NULL,NULL,1,4,1,'Kerstina','','','','','','',1,1,3);
INSERT INTO "grampsdb_name" VALUES(4,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:47.668777',NULL,NULL,1,4,1,'Alice Paula','','','','','','',1,1,4);
INSERT INTO "grampsdb_name" VALUES(5,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:49.707218',NULL,NULL,1,4,1,'Amber Marie','','','','','','',1,1,5);
INSERT INTO "grampsdb_name" VALUES(6,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:51.807424',NULL,NULL,1,4,1,'Ingeman','','','','','','',1,1,6);
INSERT INTO "grampsdb_name" VALUES(7,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:54.198306',NULL,NULL,1,4,1,'Gus','','','','','','',1,1,7);
INSERT INTO "grampsdb_name" VALUES(8,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:57.588446',NULL,NULL,1,4,1,'Mason Michael','','','','','','',1,1,8);
INSERT INTO "grampsdb_name" VALUES(9,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:18:59.784652',NULL,NULL,1,4,1,'Edwin','','','','','','',1,1,9);
INSERT INTO "grampsdb_name" VALUES(10,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:01.322448',NULL,NULL,1,4,1,'Janice Ann','','','','','','',1,1,10);
INSERT INTO "grampsdb_name" VALUES(11,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:02.839366',NULL,NULL,1,4,1,'Martin','','','','','','',1,1,11);
INSERT INTO "grampsdb_name" VALUES(12,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:05.291525',NULL,NULL,1,4,1,'John Hjalmar','','','','','','',1,1,12);
INSERT INTO "grampsdb_name" VALUES(13,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:06.832988',NULL,NULL,1,4,1,'Ingar','','','','','','',1,1,13);
INSERT INTO "grampsdb_name" VALUES(14,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:10.110761',NULL,NULL,1,4,1,'Jennifer','','','','','','',1,1,14);
INSERT INTO "grampsdb_name" VALUES(15,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:11.893240',NULL,NULL,1,4,1,'Keith Lloyd','','','','','','',1,1,15);
INSERT INTO "grampsdb_name" VALUES(16,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:13.589810',NULL,NULL,1,4,1,'Marjorie Alice','','','','','','',1,1,16);
INSERT INTO "grampsdb_name" VALUES(17,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:15.485872',NULL,NULL,1,4,1,'Martin','','','','','','',1,1,17);
INSERT INTO "grampsdb_name" VALUES(18,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:18.275403',NULL,NULL,1,4,1,'Lillie Harriet','','','','','','',1,1,18);
INSERT INTO "grampsdb_name" VALUES(19,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:21.521533',NULL,NULL,1,4,1,'Hanna','','','','','','',1,1,19);
INSERT INTO "grampsdb_name" VALUES(20,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:28.472433',NULL,NULL,1,4,1,'Elna','','','','','','',1,1,20);
INSERT INTO "grampsdb_name" VALUES(21,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:30.061199',NULL,NULL,1,4,1,'Astrid Shermanna Augusta','','','','','','',1,1,21);
INSERT INTO "grampsdb_name" VALUES(22,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:32.953007',NULL,NULL,1,4,1,'Emil','','','','','','',1,1,22);
INSERT INTO "grampsdb_name" VALUES(23,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:34.709306',NULL,NULL,1,4,1,'Herman Julius','','','','','','',1,1,23);
INSERT INTO "grampsdb_name" VALUES(24,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:36.455676',NULL,NULL,1,4,1,'Marta','','','','','','',1,1,24);
INSERT INTO "grampsdb_name" VALUES(25,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:37.563743',NULL,NULL,1,4,1,'Marjorie','','','','','','',1,1,25);
INSERT INTO "grampsdb_name" VALUES(26,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:39.384094',NULL,NULL,1,4,1,'Marjorie Lee','','','','','','',1,1,26);
INSERT INTO "grampsdb_name" VALUES(27,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:41.154580',NULL,NULL,1,4,1,'Anna','','','','','','',1,1,27);
INSERT INTO "grampsdb_name" VALUES(28,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:42.954289',NULL,NULL,1,4,1,'Ingeman','','','','','','',1,1,28);
INSERT INTO "grampsdb_name" VALUES(29,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:44.837965',NULL,NULL,1,4,1,'Hjalmar','','','','','','',1,1,29);
INSERT INTO "grampsdb_name" VALUES(30,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:47.688846',NULL,NULL,1,4,1,'Anna','','','','','','',1,1,30);
INSERT INTO "grampsdb_name" VALUES(31,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:49.379670',NULL,NULL,1,4,1,'Magnes','','','','','','',1,1,31);
INSERT INTO "grampsdb_name" VALUES(32,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:58.510910',NULL,NULL,1,4,1,'Evelyn','','','','','','',1,1,32);
INSERT INTO "grampsdb_name" VALUES(33,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:02.023542',NULL,NULL,1,4,1,'Gustaf','Sr.','','','','','',1,1,33);
INSERT INTO "grampsdb_name" VALUES(34,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:05.419591',NULL,NULL,1,4,1,'Craig Peter','','','','','','',1,1,34);
INSERT INTO "grampsdb_name" VALUES(35,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:10.121632',NULL,NULL,1,4,1,'Edwin Michael','','','','','','',1,1,35);
INSERT INTO "grampsdb_name" VALUES(36,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:15.001641',NULL,NULL,1,4,1,'Hjalmar','','','','','','',1,1,36);
INSERT INTO "grampsdb_name" VALUES(37,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:20.095238',NULL,NULL,1,4,1,'Lloyd','','','','','','',1,1,37);
INSERT INTO "grampsdb_name" VALUES(38,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:21.665690',NULL,NULL,1,4,1,'Janis Elaine','','','','','','',1,1,38);
INSERT INTO "grampsdb_name" VALUES(39,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:23.138155',NULL,NULL,1,4,1,'Kirsti Marie','','','','','','',1,1,39);
INSERT INTO "grampsdb_name" VALUES(40,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:25.467426',NULL,NULL,1,4,1,'Eric Lloyd','','','','','','',1,1,40);
INSERT INTO "grampsdb_name" VALUES(41,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:28.264407',NULL,NULL,1,4,1,'Hans Peter','','','','','','',1,1,41);
INSERT INTO "grampsdb_name" VALUES(42,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:20:32.179898',NULL,NULL,1,4,1,'Carl Emil','','','','','','',1,1,42);
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
INSERT INTO "grampsdb_markup" VALUES(1,6,1,1,'Monospace','[(0, 120)]');
INSERT INTO "grampsdb_markup" VALUES(2,10,1,1,'Monospace','[(0, 128)]');
INSERT INTO "grampsdb_markup" VALUES(3,11,1,1,'Monospace','[(0, 137)]');
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
INSERT INTO "grampsdb_address" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:52.830710',NULL,NULL,1,NULL,1);
INSERT INTO "grampsdb_address" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-05-18 07:19:56.997185',NULL,NULL,1,NULL,2);
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
INSERT INTO "grampsdb_attribute" VALUES(1,0,10,'Bad breath',36,69);
INSERT INTO "grampsdb_attribute" VALUES(2,0,12,'23',52,66);
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
INSERT INTO "grampsdb_noteref" VALUES(1,36,15,1,'2012-05-18 07:18:57.331862',NULL,NULL,0,1);
INSERT INTO "grampsdb_noteref" VALUES(2,32,17,1,'2012-05-18 07:19:17.317096',NULL,NULL,0,8);
INSERT INTO "grampsdb_noteref" VALUES(3,32,29,1,'2012-05-18 07:19:46.884049',NULL,NULL,0,3);
INSERT INTO "grampsdb_noteref" VALUES(4,37,1,1,'2012-05-18 07:19:51.604463',NULL,NULL,0,9);
INSERT INTO "grampsdb_noteref" VALUES(5,37,1,1,'2012-05-18 07:19:51.849664',NULL,NULL,0,10);
INSERT INTO "grampsdb_noteref" VALUES(6,37,2,1,'2012-05-18 07:19:56.118056',NULL,NULL,0,11);
INSERT INTO "grampsdb_noteref" VALUES(7,36,82,1,'2012-05-18 07:20:17.762672',NULL,NULL,0,5);
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
INSERT INTO "grampsdb_eventref" VALUES(1,32,1,1,'2012-05-18 07:18:42.529304',NULL,NULL,0,49,3);
INSERT INTO "grampsdb_eventref" VALUES(2,32,1,1,'2012-05-18 07:18:42.775551',NULL,NULL,0,67,3);
INSERT INTO "grampsdb_eventref" VALUES(3,32,2,1,'2012-05-18 07:18:44.553556',NULL,NULL,0,53,3);
INSERT INTO "grampsdb_eventref" VALUES(4,32,3,1,'2012-05-18 07:18:46.438243',NULL,NULL,0,45,3);
INSERT INTO "grampsdb_eventref" VALUES(5,32,3,1,'2012-05-18 07:18:46.764551',NULL,NULL,0,26,3);
INSERT INTO "grampsdb_eventref" VALUES(6,32,4,1,'2012-05-18 07:18:48.196953',NULL,NULL,0,78,3);
INSERT INTO "grampsdb_eventref" VALUES(7,32,5,1,'2012-05-18 07:18:50.197908',NULL,NULL,0,60,3);
INSERT INTO "grampsdb_eventref" VALUES(8,32,5,1,'2012-05-18 07:18:50.430110',NULL,NULL,0,34,3);
INSERT INTO "grampsdb_eventref" VALUES(9,32,6,1,'2012-05-18 07:18:52.303791',NULL,NULL,0,54,3);
INSERT INTO "grampsdb_eventref" VALUES(10,33,1,1,'2012-05-18 07:18:53.624203',NULL,NULL,0,86,10);
INSERT INTO "grampsdb_eventref" VALUES(11,32,7,1,'2012-05-18 07:18:54.709352',NULL,NULL,0,17,3);
INSERT INTO "grampsdb_eventref" VALUES(12,32,7,1,'2012-05-18 07:18:55.040283',NULL,NULL,0,2,3);
INSERT INTO "grampsdb_eventref" VALUES(13,32,8,1,'2012-05-18 07:18:58.162834',NULL,NULL,0,64,3);
INSERT INTO "grampsdb_eventref" VALUES(14,32,8,1,'2012-05-18 07:18:58.503814',NULL,NULL,0,79,3);
INSERT INTO "grampsdb_eventref" VALUES(15,32,9,1,'2012-05-18 07:19:00.252465',NULL,NULL,0,46,3);
INSERT INTO "grampsdb_eventref" VALUES(16,32,10,1,'2012-05-18 07:19:01.814529',NULL,NULL,0,27,3);
INSERT INTO "grampsdb_eventref" VALUES(17,32,10,1,'2012-05-18 07:19:02.060252',NULL,NULL,0,70,3);
INSERT INTO "grampsdb_eventref" VALUES(18,32,10,1,'2012-05-18 07:19:02.315266',NULL,NULL,0,71,3);
INSERT INTO "grampsdb_eventref" VALUES(19,32,11,1,'2012-05-18 07:19:03.343086',NULL,NULL,0,16,3);
INSERT INTO "grampsdb_eventref" VALUES(20,32,11,1,'2012-05-18 07:19:03.826274',NULL,NULL,0,29,3);
INSERT INTO "grampsdb_eventref" VALUES(21,32,12,1,'2012-05-18 07:19:05.836542',NULL,NULL,0,44,3);
INSERT INTO "grampsdb_eventref" VALUES(22,32,13,1,'2012-05-18 07:19:07.318802',NULL,NULL,0,85,3);
INSERT INTO "grampsdb_eventref" VALUES(23,32,14,1,'2012-05-18 07:19:10.625002',NULL,NULL,0,10,3);
INSERT INTO "grampsdb_eventref" VALUES(24,32,14,1,'2012-05-18 07:19:10.864009',NULL,NULL,0,66,3);
INSERT INTO "grampsdb_eventref" VALUES(25,32,15,1,'2012-05-18 07:19:12.508936',NULL,NULL,0,75,3);
INSERT INTO "grampsdb_eventref" VALUES(26,32,16,1,'2012-05-18 07:19:14.241057',NULL,NULL,0,62,3);
INSERT INTO "grampsdb_eventref" VALUES(27,32,17,1,'2012-05-18 07:19:15.976511',NULL,NULL,0,83,3);
INSERT INTO "grampsdb_eventref" VALUES(28,32,17,1,'2012-05-18 07:19:16.232300',NULL,NULL,0,7,3);
INSERT INTO "grampsdb_eventref" VALUES(29,32,17,1,'2012-05-18 07:19:16.553479',NULL,NULL,0,52,3);
INSERT INTO "grampsdb_eventref" VALUES(30,32,18,1,'2012-05-18 07:19:18.785233',NULL,NULL,0,81,3);
INSERT INTO "grampsdb_eventref" VALUES(31,32,18,1,'2012-05-18 07:19:19.041576',NULL,NULL,0,77,3);
INSERT INTO "grampsdb_eventref" VALUES(32,33,2,1,'2012-05-18 07:19:20.002442',NULL,NULL,0,39,10);
INSERT INTO "grampsdb_eventref" VALUES(33,32,19,1,'2012-05-18 07:19:22.169018',NULL,NULL,0,33,3);
INSERT INTO "grampsdb_eventref" VALUES(34,32,20,1,'2012-05-18 07:19:28.991800',NULL,NULL,0,24,3);
INSERT INTO "grampsdb_eventref" VALUES(35,32,20,1,'2012-05-18 07:19:29.246444',NULL,NULL,0,42,3);
INSERT INTO "grampsdb_eventref" VALUES(36,32,20,1,'2012-05-18 07:19:29.513064',NULL,NULL,0,9,3);
INSERT INTO "grampsdb_eventref" VALUES(37,32,21,1,'2012-05-18 07:19:30.558187',NULL,NULL,0,84,3);
INSERT INTO "grampsdb_eventref" VALUES(38,32,21,1,'2012-05-18 07:19:30.836744',NULL,NULL,0,51,3);
INSERT INTO "grampsdb_eventref" VALUES(39,32,22,1,'2012-05-18 07:19:33.646659',NULL,NULL,0,13,3);
INSERT INTO "grampsdb_eventref" VALUES(40,32,23,1,'2012-05-18 07:19:35.212812',NULL,NULL,0,19,3);
INSERT INTO "grampsdb_eventref" VALUES(41,32,23,1,'2012-05-18 07:19:35.454670',NULL,NULL,0,59,3);
INSERT INTO "grampsdb_eventref" VALUES(42,32,24,1,'2012-05-18 07:19:36.962708',NULL,NULL,0,50,3);
INSERT INTO "grampsdb_eventref" VALUES(43,32,25,1,'2012-05-18 07:19:38.129038',NULL,NULL,0,32,3);
INSERT INTO "grampsdb_eventref" VALUES(44,32,25,1,'2012-05-18 07:19:38.383748',NULL,NULL,0,35,3);
INSERT INTO "grampsdb_eventref" VALUES(45,32,26,1,'2012-05-18 07:19:39.875904',NULL,NULL,0,88,3);
INSERT INTO "grampsdb_eventref" VALUES(46,32,27,1,'2012-05-18 07:19:41.686797',NULL,NULL,0,20,3);
INSERT INTO "grampsdb_eventref" VALUES(47,32,27,1,'2012-05-18 07:19:41.954174',NULL,NULL,0,3,3);
INSERT INTO "grampsdb_eventref" VALUES(48,32,28,1,'2012-05-18 07:19:43.511912',NULL,NULL,0,68,3);
INSERT INTO "grampsdb_eventref" VALUES(49,32,29,1,'2012-05-18 07:19:45.317560',NULL,NULL,0,28,3);
INSERT INTO "grampsdb_eventref" VALUES(50,32,29,1,'2012-05-18 07:19:45.563510',NULL,NULL,0,38,3);
INSERT INTO "grampsdb_eventref" VALUES(51,32,29,1,'2012-05-18 07:19:45.825194',NULL,NULL,0,56,3);
INSERT INTO "grampsdb_eventref" VALUES(52,32,29,1,'2012-05-18 07:19:46.073078',NULL,NULL,0,76,3);
INSERT INTO "grampsdb_eventref" VALUES(53,32,30,1,'2012-05-18 07:19:48.146449',NULL,NULL,0,40,3);
INSERT INTO "grampsdb_eventref" VALUES(54,32,30,1,'2012-05-18 07:19:48.379269',NULL,NULL,0,65,3);
INSERT INTO "grampsdb_eventref" VALUES(55,32,31,1,'2012-05-18 07:19:49.851409',NULL,NULL,0,48,3);
INSERT INTO "grampsdb_eventref" VALUES(56,32,31,1,'2012-05-18 07:19:50.101734',NULL,NULL,0,11,3);
INSERT INTO "grampsdb_eventref" VALUES(57,32,32,1,'2012-05-18 07:19:59.006731',NULL,NULL,0,6,3);
INSERT INTO "grampsdb_eventref" VALUES(58,33,9,1,'2012-05-18 07:20:01.574135',NULL,NULL,0,36,10);
INSERT INTO "grampsdb_eventref" VALUES(59,32,33,1,'2012-05-18 07:20:02.645174',NULL,NULL,0,47,3);
INSERT INTO "grampsdb_eventref" VALUES(60,32,33,1,'2012-05-18 07:20:02.884704',NULL,NULL,0,57,3);
INSERT INTO "grampsdb_eventref" VALUES(61,32,33,1,'2012-05-18 07:20:03.129701',NULL,NULL,0,87,3);
INSERT INTO "grampsdb_eventref" VALUES(62,32,33,1,'2012-05-18 07:20:03.384449',NULL,NULL,0,58,3);
INSERT INTO "grampsdb_eventref" VALUES(63,32,34,1,'2012-05-18 07:20:06.108856',NULL,NULL,0,72,3);
INSERT INTO "grampsdb_eventref" VALUES(64,32,34,1,'2012-05-18 07:20:06.352669',NULL,NULL,0,15,3);
INSERT INTO "grampsdb_eventref" VALUES(65,32,35,1,'2012-05-18 07:20:10.884967',NULL,NULL,0,73,3);
INSERT INTO "grampsdb_eventref" VALUES(66,32,35,1,'2012-05-18 07:20:11.151490',NULL,NULL,0,82,3);
INSERT INTO "grampsdb_eventref" VALUES(67,32,35,1,'2012-05-18 07:20:11.713317',NULL,NULL,0,14,3);
INSERT INTO "grampsdb_eventref" VALUES(68,32,35,1,'2012-05-18 07:20:11.962586',NULL,NULL,0,18,3);
INSERT INTO "grampsdb_eventref" VALUES(69,33,12,1,'2012-05-18 07:20:13.250836',NULL,NULL,0,37,10);
INSERT INTO "grampsdb_eventref" VALUES(70,32,36,1,'2012-05-18 07:20:15.657032',NULL,NULL,0,55,3);
INSERT INTO "grampsdb_eventref" VALUES(71,32,36,1,'2012-05-18 07:20:15.924833',NULL,NULL,0,91,3);
INSERT INTO "grampsdb_eventref" VALUES(72,32,37,1,'2012-05-18 07:20:20.651924',NULL,NULL,0,25,3);
INSERT INTO "grampsdb_eventref" VALUES(73,32,38,1,'2012-05-18 07:20:22.129746',NULL,NULL,0,1,3);
INSERT INTO "grampsdb_eventref" VALUES(74,32,39,1,'2012-05-18 07:20:23.641066',NULL,NULL,0,41,3);
INSERT INTO "grampsdb_eventref" VALUES(75,32,39,1,'2012-05-18 07:20:23.891522',NULL,NULL,0,30,3);
INSERT INTO "grampsdb_eventref" VALUES(76,32,40,1,'2012-05-18 07:20:25.946474',NULL,NULL,0,90,3);
INSERT INTO "grampsdb_eventref" VALUES(77,32,40,1,'2012-05-18 07:20:26.185208',NULL,NULL,0,61,3);
INSERT INTO "grampsdb_eventref" VALUES(78,32,41,1,'2012-05-18 07:20:28.964110',NULL,NULL,0,89,3);
INSERT INTO "grampsdb_eventref" VALUES(79,32,41,1,'2012-05-18 07:20:29.329455',NULL,NULL,0,63,3);
INSERT INTO "grampsdb_eventref" VALUES(80,32,42,1,'2012-05-18 07:20:32.673639',NULL,NULL,0,80,3);
INSERT INTO "grampsdb_eventref" VALUES(81,32,42,1,'2012-05-18 07:20:32.929705',NULL,NULL,0,69,3);
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
INSERT INTO "grampsdb_citationref" VALUES(1,36,5,1,'2012-05-18 07:18:45.470878',NULL,NULL,0,1);
INSERT INTO "grampsdb_citationref" VALUES(2,36,73,1,'2012-05-18 07:20:08.622067',NULL,NULL,0,3);
INSERT INTO "grampsdb_citationref" VALUES(3,42,35,1,'2012-05-18 07:20:10.618177',NULL,NULL,0,2);
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
INSERT INTO "grampsdb_childref" VALUES(1,33,3,1,'2012-05-18 07:19:21.083520',NULL,NULL,0,2,2,19);
INSERT INTO "grampsdb_childref" VALUES(2,33,4,1,'2012-05-18 07:19:23.669636',NULL,NULL,0,2,2,11);
INSERT INTO "grampsdb_childref" VALUES(3,33,5,1,'2012-05-18 07:19:24.915565',NULL,NULL,0,3,3,1);
INSERT INTO "grampsdb_childref" VALUES(4,33,6,1,'2012-05-18 07:19:25.749009',NULL,NULL,0,2,2,26);
INSERT INTO "grampsdb_childref" VALUES(5,33,8,1,'2012-05-18 07:20:00.485418',NULL,NULL,0,2,2,33);
INSERT INTO "grampsdb_childref" VALUES(6,33,10,1,'2012-05-18 07:20:07.714614',NULL,NULL,0,2,2,15);
INSERT INTO "grampsdb_childref" VALUES(7,33,11,1,'2012-05-18 07:20:09.285915',NULL,NULL,0,2,2,37);
INSERT INTO "grampsdb_childref" VALUES(8,33,13,1,'2012-05-18 07:20:18.897593',NULL,NULL,0,2,2,35);
INSERT INTO "grampsdb_childref" VALUES(9,33,14,1,'2012-05-18 07:20:19.832078',NULL,NULL,0,2,2,41);
INSERT INTO "grampsdb_childref" VALUES(10,33,15,1,'2012-05-18 07:20:27.932907',NULL,NULL,0,2,2,5);
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
