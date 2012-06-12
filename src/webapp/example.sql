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
INSERT INTO "auth_group_permissions" VALUES(1,1,128);
INSERT INTO "auth_group_permissions" VALUES(2,1,2);
INSERT INTO "auth_group_permissions" VALUES(3,1,131);
INSERT INTO "auth_group_permissions" VALUES(4,1,5);
INSERT INTO "auth_group_permissions" VALUES(5,1,134);
INSERT INTO "auth_group_permissions" VALUES(6,1,8);
INSERT INTO "auth_group_permissions" VALUES(7,1,137);
INSERT INTO "auth_group_permissions" VALUES(8,1,11);
INSERT INTO "auth_group_permissions" VALUES(9,1,140);
INSERT INTO "auth_group_permissions" VALUES(10,1,14);
INSERT INTO "auth_group_permissions" VALUES(11,1,143);
INSERT INTO "auth_group_permissions" VALUES(12,1,17);
INSERT INTO "auth_group_permissions" VALUES(13,1,146);
INSERT INTO "auth_group_permissions" VALUES(14,1,20);
INSERT INTO "auth_group_permissions" VALUES(15,1,149);
INSERT INTO "auth_group_permissions" VALUES(16,1,23);
INSERT INTO "auth_group_permissions" VALUES(17,1,152);
INSERT INTO "auth_group_permissions" VALUES(18,1,26);
INSERT INTO "auth_group_permissions" VALUES(19,1,155);
INSERT INTO "auth_group_permissions" VALUES(20,1,29);
INSERT INTO "auth_group_permissions" VALUES(21,1,158);
INSERT INTO "auth_group_permissions" VALUES(22,1,32);
INSERT INTO "auth_group_permissions" VALUES(23,1,161);
INSERT INTO "auth_group_permissions" VALUES(24,1,35);
INSERT INTO "auth_group_permissions" VALUES(25,1,164);
INSERT INTO "auth_group_permissions" VALUES(26,1,38);
INSERT INTO "auth_group_permissions" VALUES(27,1,167);
INSERT INTO "auth_group_permissions" VALUES(28,1,41);
INSERT INTO "auth_group_permissions" VALUES(29,1,170);
INSERT INTO "auth_group_permissions" VALUES(30,1,44);
INSERT INTO "auth_group_permissions" VALUES(31,1,173);
INSERT INTO "auth_group_permissions" VALUES(32,1,47);
INSERT INTO "auth_group_permissions" VALUES(33,1,176);
INSERT INTO "auth_group_permissions" VALUES(34,1,50);
INSERT INTO "auth_group_permissions" VALUES(35,1,53);
INSERT INTO "auth_group_permissions" VALUES(36,1,56);
INSERT INTO "auth_group_permissions" VALUES(37,1,59);
INSERT INTO "auth_group_permissions" VALUES(38,1,62);
INSERT INTO "auth_group_permissions" VALUES(39,1,65);
INSERT INTO "auth_group_permissions" VALUES(40,1,68);
INSERT INTO "auth_group_permissions" VALUES(41,1,71);
INSERT INTO "auth_group_permissions" VALUES(42,1,74);
INSERT INTO "auth_group_permissions" VALUES(43,1,77);
INSERT INTO "auth_group_permissions" VALUES(44,1,80);
INSERT INTO "auth_group_permissions" VALUES(45,1,83);
INSERT INTO "auth_group_permissions" VALUES(46,1,86);
INSERT INTO "auth_group_permissions" VALUES(47,1,89);
INSERT INTO "auth_group_permissions" VALUES(48,1,92);
INSERT INTO "auth_group_permissions" VALUES(49,1,95);
INSERT INTO "auth_group_permissions" VALUES(50,1,98);
INSERT INTO "auth_group_permissions" VALUES(51,1,101);
INSERT INTO "auth_group_permissions" VALUES(52,1,104);
INSERT INTO "auth_group_permissions" VALUES(53,1,107);
INSERT INTO "auth_group_permissions" VALUES(54,1,110);
INSERT INTO "auth_group_permissions" VALUES(55,1,113);
INSERT INTO "auth_group_permissions" VALUES(56,1,116);
INSERT INTO "auth_group_permissions" VALUES(57,1,119);
INSERT INTO "auth_group_permissions" VALUES(58,1,122);
INSERT INTO "auth_group_permissions" VALUES(59,1,125);
CREATE TABLE "auth_group" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL UNIQUE
);
INSERT INTO "auth_group" VALUES(1,'Editor');
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
INSERT INTO "auth_user_groups" VALUES(1,1,1);
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
INSERT INTO "auth_user" VALUES(1,'admin','','','bugs@gramps-project.org','sha1$a4c03$de6d2ce8c551e0b682f11ab92170f6afb4bede0b',1,1,1,'2012-06-10 22:23:53','2012-06-10 22:23:34');
INSERT INTO "auth_user" VALUES(2,'admin1','','','bugs@gramps-project.org','sha1$b3283$5306be6909a7ff60692513e406b40de8c84007ee',1,1,1,'2012-06-10 22:23:40.249002','2012-06-10 22:23:40.249002');
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
INSERT INTO "django_session" VALUES('3c99ce6c280d2f7957446d227beb3365','MmU1MjliMDM2NzcyODdjNmJlOTgzMGFiYzc2MjFkMmViYWFiOTIzMjqAAn1xAShVEl9hdXRoX3Vz
ZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED
VQ1fYXV0aF91c2VyX2lkcQRLAXUu
','2012-06-24 22:23:53.981505');
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
INSERT INTO "django_admin_log" VALUES(1,'2012-06-10 22:24:32.318268',1,9,'1','admin',2,'Changed theme_type.');
INSERT INTO "django_admin_log" VALUES(2,'2012-06-10 22:24:45.300529',1,9,'1','admin',2,'Changed theme_type.');
INSERT INTO "django_admin_log" VALUES(3,'2012-06-11 06:55:51.555028',1,9,'1','admin',2,'Changed theme_type.');
INSERT INTO "django_admin_log" VALUES(4,'2012-06-11 07:01:37.331748',1,2,'1','Editor',1,'');
INSERT INTO "django_admin_log" VALUES(5,'2012-06-11 07:01:50.823018',1,3,'1','admin',2,'Changed groups.');
INSERT INTO "django_admin_log" VALUES(6,'2012-06-11 21:25:15.748466',1,9,'1','admin',2,'No fields changed.');
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
INSERT INTO "grampsdb_config" VALUES(3,'db_created','database creation date/time','str','2012-06-10 22:21');
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
INSERT INTO "grampsdb_person_families" VALUES(1,1,18);
INSERT INTO "grampsdb_person_families" VALUES(2,3,12);
INSERT INTO "grampsdb_person_families" VALUES(3,4,14);
INSERT INTO "grampsdb_person_families" VALUES(4,6,12);
INSERT INTO "grampsdb_person_families" VALUES(5,7,8);
INSERT INTO "grampsdb_person_families" VALUES(6,11,19);
INSERT INTO "grampsdb_person_families" VALUES(7,12,13);
INSERT INTO "grampsdb_person_families" VALUES(8,14,15);
INSERT INTO "grampsdb_person_families" VALUES(9,16,16);
INSERT INTO "grampsdb_person_families" VALUES(10,18,6);
INSERT INTO "grampsdb_person_families" VALUES(11,19,3);
INSERT INTO "grampsdb_person_families" VALUES(12,20,6);
INSERT INTO "grampsdb_person_families" VALUES(13,21,16);
INSERT INTO "grampsdb_person_families" VALUES(14,23,10);
INSERT INTO "grampsdb_person_families" VALUES(15,25,18);
INSERT INTO "grampsdb_person_families" VALUES(16,25,5);
INSERT INTO "grampsdb_person_families" VALUES(17,27,14);
INSERT INTO "grampsdb_person_families" VALUES(18,28,2);
INSERT INTO "grampsdb_person_families" VALUES(19,29,5);
INSERT INTO "grampsdb_person_families" VALUES(20,31,3);
INSERT INTO "grampsdb_person_families" VALUES(21,33,10);
INSERT INTO "grampsdb_person_families" VALUES(22,34,8);
INSERT INTO "grampsdb_person_families" VALUES(23,40,9);
INSERT INTO "grampsdb_person_families" VALUES(24,42,4);
INSERT INTO "grampsdb_person_families" VALUES(25,43,1);
INSERT INTO "grampsdb_person_families" VALUES(26,46,4);
INSERT INTO "grampsdb_person_families" VALUES(27,48,1);
INSERT INTO "grampsdb_person_families" VALUES(28,49,2);
INSERT INTO "grampsdb_person_families" VALUES(29,50,9);
INSERT INTO "grampsdb_person_families" VALUES(30,51,17);
INSERT INTO "grampsdb_person_families" VALUES(31,56,13);
INSERT INTO "grampsdb_person_families" VALUES(32,57,11);
INSERT INTO "grampsdb_person_families" VALUES(33,58,19);
INSERT INTO "grampsdb_person_families" VALUES(34,63,7);
INSERT INTO "grampsdb_person_families" VALUES(35,64,11);
INSERT INTO "grampsdb_person_families" VALUES(36,67,15);
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
INSERT INTO "grampsdb_person_parent_families" VALUES(1,2,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(2,5,18);
INSERT INTO "grampsdb_person_parent_families" VALUES(3,6,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(4,8,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(5,9,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(6,10,4);
INSERT INTO "grampsdb_person_parent_families" VALUES(7,13,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(8,15,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(9,17,4);
INSERT INTO "grampsdb_person_parent_families" VALUES(10,18,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(11,19,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(12,21,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(13,22,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(14,23,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(15,24,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(16,26,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(17,27,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(18,30,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(19,32,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(20,33,2);
INSERT INTO "grampsdb_person_parent_families" VALUES(21,35,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(22,36,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(23,37,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(24,38,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(25,39,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(26,41,4);
INSERT INTO "grampsdb_person_parent_families" VALUES(27,42,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(28,44,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(29,45,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(30,47,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(31,48,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(32,50,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(33,51,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(34,52,1);
INSERT INTO "grampsdb_person_parent_families" VALUES(35,53,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(36,54,16);
INSERT INTO "grampsdb_person_parent_families" VALUES(37,55,14);
INSERT INTO "grampsdb_person_parent_families" VALUES(38,56,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(39,58,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(40,59,17);
INSERT INTO "grampsdb_person_parent_families" VALUES(41,60,8);
INSERT INTO "grampsdb_person_parent_families" VALUES(42,61,17);
INSERT INTO "grampsdb_person_parent_families" VALUES(43,62,17);
INSERT INTO "grampsdb_person_parent_families" VALUES(44,64,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(45,65,13);
INSERT INTO "grampsdb_person_parent_families" VALUES(46,66,11);
INSERT INTO "grampsdb_person_parent_families" VALUES(47,67,10);
INSERT INTO "grampsdb_person_parent_families" VALUES(48,68,10);
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
INSERT INTO "grampsdb_person" VALUES(1,'c2e7d98180317b0250c3e61c833','I0048','2012-06-10 22:25:19.088130','1994-06-30 00:00:00',NULL,0,NULL,2,0,NULL,48,-1,1);
INSERT INTO "grampsdb_person" VALUES(2,'c2e7d98160c371b9f5dc06bb5ac','I0032','2012-06-10 22:25:19.347376','1969-12-31 19:00:00',NULL,0,NULL,2,1,15,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(3,'c2e7d981a291a4ef72ad67ebc95','I0065','2012-06-10 22:25:19.599091','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(4,'c2e7d9816f0250098c8802aa12','I0040','2012-06-10 22:25:19.859161','1994-05-29 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(5,'c2e7d981a6b3c11a2714001973d','I0068','2012-06-10 22:25:20.102957','1994-05-27 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(6,'c2e7d9819f9615264e6af2f3847','I0063','2012-06-10 22:25:20.347375','1994-05-27 00:00:00',NULL,0,NULL,3,1,133,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(7,'c2e7d9817aa3b4eb6d9dcf39715','I0046','2012-06-10 22:25:20.594972','1994-10-16 00:00:00',NULL,0,NULL,2,0,91,23,0,1);
INSERT INTO "grampsdb_person" VALUES(8,'c2e7d9814435c2765fa451583b7','I0014','2012-06-10 22:25:20.869616','1969-12-31 19:00:00',NULL,0,NULL,2,1,78,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(9,'c2e7d9815a2123b668d30ce53b4','I0028','2012-06-10 22:25:21.270993','1969-12-31 19:00:00',NULL,0,NULL,2,1,37,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(10,'c2e7d98168076135eccccb2259e','I0036','2012-06-10 22:25:21.653877','1969-12-31 19:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(11,'c2e7d9813e88a9520c9f3a51b2','I0010','2012-06-10 22:25:21.914043','1994-10-16 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(12,'c2e7d98131a63ca16d54254bab4','I0007','2012-06-10 22:25:22.171445','1994-05-27 00:00:00',NULL,0,NULL,2,1,60,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(13,'c2e7d9815ce36a8dddad364b594','I0030','2012-06-10 22:25:22.436897','1969-12-31 19:00:00',NULL,0,NULL,2,1,144,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(14,'c2e7d9812811cfb50d360f25799','I0005','2012-06-11 16:36:17.800423','2012-06-11 16:36:16.709320','admin',0,'KFMnYzJlN2Q5ODEyODExY2ZiNTBkMzYwZjI1Nzk5JwpWSTAwMDUKcDEKSTEKKEkwMAoobChsKEkw
CkkwCkkwCihJMApJMApJMApJMDAKTk5OTnRWCkkwCkkwCnRWV2lsbGlhbSBKb2huIFJvYmVydApw
MgoobHAzCihWQ0FWRU5ESVNIClYKSTAxCihJMQpWCnRWCnRwNAphVgpWCihJMgpWQmlydGggTmFt
ZQpwNQp0VgpJMApJMApWClYKVgp0KGxJMQpJMAoobHA2CihJMDAKKGwobFZjMmU3ZDk4MTI4NzQ0
YjIzN2JiMDAxMWFlZTIKKEkxClZQcmltYXJ5CnR0cDcKYShJMDAKKGwobFZjMmU3ZDk4MTI4YTEx
NjRiMzk1NzY3N2UwMzkKKEkxClZQcmltYXJ5CnR0cDgKYShscDkKVmMyZTdkOTgxMjljNTdhNzg2
OTFiN2ZlM2Y1MgpwMTAKYShsKGwobChsKGwobChsKGxJMTMzOTQ0Njk3NgoodEkwMAoobHRwMTEK
Lg==
',2,0,137,66,0,1);
INSERT INTO "grampsdb_person" VALUES(15,'c2e7d98148f3cc9f5495499075f','I0017','2012-06-10 22:25:22.965484','1969-12-31 19:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(16,'c2e7d9815204a968fbbd966d878','I0022','2012-06-10 22:25:23.220475','1969-12-31 19:00:00',NULL,0,NULL,3,1,104,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(17,'c2e7d9816931a1a78dc081ca7d3','I0037','2012-06-10 22:25:23.459173','1969-12-31 19:00:00',NULL,0,NULL,2,1,20,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(18,'c2e7d9819bd10fda2e87a1eeb82','I0061','2012-06-10 22:25:23.703662','1994-05-27 00:00:00',NULL,0,NULL,3,1,100,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(19,'c2e7d98199a346e54bb715456e1','I0060','2012-06-10 22:25:23.948082','1994-05-27 00:00:00',NULL,0,NULL,3,1,19,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(20,'c2e7d981a1b4fd787a11d506143','I0064','2012-06-10 22:25:24.191812','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(21,'c2e7d9814dd2cb9db418b837d0b','I0021','2012-06-10 22:25:24.460785','1994-05-29 00:00:00',NULL,0,NULL,2,0,58,132,0,1);
INSERT INTO "grampsdb_person" VALUES(22,'c2e7d98155758bf50da8af7beb8','I0025','2012-06-10 22:25:24.716021','1969-12-31 19:00:00',NULL,0,NULL,2,1,129,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(23,'c2e7d98022f25f84cb69b6d417d','I0001','2012-06-10 22:25:25.206198','1995-01-26 00:00:00',NULL,0,NULL,2,0,108,30,0,1);
INSERT INTO "grampsdb_person" VALUES(24,'c2e7d98156f44a942c2f37585b8','I0026','2012-06-10 22:25:25.587151','1969-12-31 19:00:00',NULL,0,NULL,2,1,80,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(25,'c2e7d98182f16ac9317fa4b42a4','I0049','2012-06-10 22:25:25.847953','1994-05-27 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(26,'c2e7d98152d38ca4245cae17c1b','I0023','2012-06-10 22:25:26.094513','1969-12-31 19:00:00',NULL,0,NULL,3,1,70,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(27,'c2e7d9816c563e0ba1a332b0114','I0039','2012-06-10 22:25:26.481398','1994-05-29 00:00:00',NULL,0,NULL,2,1,92,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(28,'c2e7d98183e381a938aa86c59de','I0050','2012-06-10 22:25:26.736870','1994-11-03 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(29,'c2e7d981a814d1879ec29f6f976','I0069','2012-06-10 22:25:27.002862','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(30,'c2e7d9815b8276f274e3eb48c57','I0029','2012-06-10 22:25:27.347269','1969-12-31 19:00:00',NULL,0,NULL,3,1,69,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(31,'c2e7d981a364e8edd733f02f711','I0066','2012-06-10 22:25:27.692434','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(32,'c2e7d98172a102e57e7d5159dda','I0043','2012-06-10 22:25:28.069623','1969-12-31 19:00:00',NULL,0,NULL,2,1,9,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(33,'c2e7d981154140d4c615c7b9c98','I0002','2012-06-10 22:25:28.338493','1995-01-26 00:00:00',NULL,0,NULL,3,0,63,26,0,1);
INSERT INTO "grampsdb_person" VALUES(34,'c2e7d9817db41b1782aa044dcb1','I0047','2012-06-10 22:25:28.617216','1994-10-16 00:00:00',NULL,0,NULL,3,0,50,77,0,1);
INSERT INTO "grampsdb_person" VALUES(35,'c2e7d9812295a70338a45cd5060','I0004','2012-06-10 22:25:28.876963','1996-01-23 00:00:00',NULL,0,NULL,3,1,6,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(36,'c2e7d9814c93ceffc927c2b3c2d','I0020','2012-06-10 22:25:29.225217','1969-12-31 19:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(37,'c2e7d981542146add10822a195c','I0024','2012-06-10 22:25:29.515121','1969-12-31 19:00:00',NULL,0,NULL,2,1,122,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(38,'c2e7d981425170dc6f7377c7537','I0013','2012-06-10 22:25:29.758385','1969-12-31 19:00:00',NULL,0,NULL,2,1,124,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(39,'c2e7d9815ef67df7d7786764a4b','I0031','2012-06-10 22:25:30.014780','1969-12-31 19:00:00',NULL,0,NULL,2,1,7,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(40,'c2e7d98198178226ed00178db13','I0058','2012-06-10 22:25:30.270412','1994-05-27 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(41,'c2e7d9816b111bf3082b0a5df1','I0038','2012-06-10 22:25:30.521706','1969-12-31 19:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(42,'c2e7d98165b64ab43c434930cf8','I0035','2012-06-10 22:25:30.780611','1994-05-29 00:00:00',NULL,0,NULL,3,1,117,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(43,'c2e7d9817995a79fbbe291b5ec7','I0045','2012-06-10 22:25:31.038554','1994-05-29 00:00:00',NULL,0,NULL,3,0,NULL,64,-1,0);
INSERT INTO "grampsdb_person" VALUES(44,'c2e7d9814a2641bd3a551b14705','I0018','2012-06-10 22:25:31.336812','1969-12-31 19:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(45,'c2e7d981713143381e3cfc8fc19','I0042','2012-06-10 22:25:31.591717','1969-12-31 19:00:00',NULL,0,NULL,2,1,83,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(46,'c2e7d9816503462e1fbeb0e3b74','I0034','2012-06-10 22:25:31.847928','1969-12-31 19:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(47,'c2e7d98162e48c13e8fdc9e25a2','I0033','2012-06-10 22:25:32.102831','1969-12-31 19:00:00',NULL,0,NULL,3,1,68,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(48,'c2e7d9817405bf8f1ef84cd3cf4','I0044','2012-06-10 22:25:32.361431','1994-05-29 00:00:00',NULL,0,NULL,2,0,32,17,0,1);
INSERT INTO "grampsdb_person" VALUES(49,'c2e7d98184dad8966949a485df','I0051','2012-06-10 22:25:32.625765','1994-11-03 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(50,'c2e7d9819693b1c54e2031118b9','I0057','2012-06-10 22:25:32.888126','1994-05-27 00:00:00',NULL,0,NULL,3,1,119,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(51,'c2e7d9818599fc62ec468702a8','I0052','2012-06-10 22:25:33.205296','1995-04-29 00:00:00',NULL,0,NULL,2,0,95,115,0,1);
INSERT INTO "grampsdb_person" VALUES(52,'c2e7d981a442eaedd90f4e58dda','I0067','2012-06-10 22:25:33.632710','1994-05-27 00:00:00',NULL,0,NULL,3,1,143,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(53,'c2e7d9813d125c1e6199744bde','I0009','2012-06-10 22:25:33.980609','1969-12-31 19:00:00',NULL,0,NULL,2,1,98,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(54,'c2e7d98158c3d15b37a444f99f','I0027','2012-06-10 22:25:34.359596','1969-12-31 19:00:00',NULL,0,NULL,3,1,127,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(55,'c2e7d9816fe126a1a7eba6d4202','I0041','2012-06-10 22:25:34.758411','1969-12-31 19:00:00',NULL,0,NULL,3,1,4,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(56,'c2e7d98137021aff46e5c5342c2','I0008','2012-06-10 22:25:35.088777','1969-12-31 19:00:00',NULL,0,NULL,3,1,101,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(57,'c2e7d9814625f49502b651ad6f3','I0015','2012-06-10 22:25:35.436775','1969-12-31 19:00:00',NULL,0,NULL,2,1,52,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(58,'c2e7d9813f753bab218cbfd05b6','I0011','2012-06-10 22:25:35.702911','1994-06-30 00:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(59,'c2e7d98191e2d4f6392700d1cad','I0055','2012-06-10 22:25:35.954732','1995-04-29 00:00:00',NULL,0,NULL,2,1,85,NULL,1,-1);
INSERT INTO "grampsdb_person" VALUES(60,'c2e7d9819d75845aa4770e1f524','I0062','2012-06-10 22:25:36.201638','1994-05-27 00:00:00',NULL,0,NULL,2,0,29,2,0,1);
INSERT INTO "grampsdb_person" VALUES(61,'c2e7d9818f26014a57c7e22944e','I0054','2012-06-10 22:25:36.454092','1994-05-29 00:00:00',NULL,0,NULL,3,1,5,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(62,'c2e7d9819414413814b85203f82','I0056','2012-06-10 22:25:36.702088','1969-12-31 19:00:00',NULL,0,NULL,2,0,59,125,0,1);
INSERT INTO "grampsdb_person" VALUES(63,'c2e7d98198ef1fcc9df292b14e','I0059','2012-06-10 22:25:37.013869','1994-05-29 00:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(64,'c2e7d98146f42fc43a22aa1088b','I0016','2012-06-10 22:25:37.358201','1969-12-31 19:00:00',NULL,0,NULL,3,1,82,NULL,0,-1);
INSERT INTO "grampsdb_person" VALUES(65,'c2e7d98140f20eaac50b036e055','I0012','2012-06-10 22:25:37.668915','1969-12-31 19:00:00',NULL,0,NULL,2,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(66,'c2e7d9814b655fa6bddb726fdc3','I0019','2012-06-10 22:25:37.925792','1969-12-31 19:00:00',NULL,0,NULL,3,1,NULL,NULL,-1,-1);
INSERT INTO "grampsdb_person" VALUES(67,'c2e7d9812b1385fdc2212104437','I0006','2012-06-10 22:25:38.184101','1994-05-27 00:00:00',NULL,0,NULL,3,0,39,74,0,1);
INSERT INTO "grampsdb_person" VALUES(68,'c2e7d9811de3b4a1e51cfc4e442','I0003','2012-06-10 22:25:38.460689','1994-05-29 00:00:00',NULL,0,NULL,2,0,79,105,1,2);
INSERT INTO "grampsdb_person" VALUES(69,'c2e7d9818a84a3f6dcddec6788f','I0053','2012-06-11 16:33:07.943070','2012-06-11 16:32:48.282165','admin',0,'KFMnYzJlN2Q5ODE4YTg0YTNmNmRjZGRlYzY3ODhmJwpWSTAwNTMKcDEKSTAKKEkwMAoobChsKEkw
CkkwCkkwCihJMApJMApJMApJMDAKTk5OTnRWCkkwCkkwCnRWSmFjcXVlbGluZQpwMgoobHAzCihW
Qk9VVklFUgpWCkkwMQooSTEKVgp0Vgp0cDQKYVYKVgooSTIKVkJpcnRoIE5hbWUKcDUKdFYKSTAK
STAKVgpWClYKdChsSTEKSTAKKGxwNgooSTAwCihsKGxWYzJlN2Q5ODE4YWI2MTI5M2Q5NjE3MzAz
NzY2CihJMQpWUHJpbWFyeQp0dHA3CmEoSTAwCihsKGxWYzJlN2Q5ODE4YjUxNWIzMjgyOTg5NmJj
OTI3CihJMQpWUHJpbWFyeQp0dHA4CmEoSTAwCihsKGxWYzJlN2Q5ODE4YmYxYWMxZjVlNDIxOGNj
NjIwCihJMQpWUHJpbWFyeQp0dHA5CmEoSTAwCihsKGxWYzJlN2Q5ODE4Y2I2N2VjYWI1ZDk5ZTU3
YjZhCihJMQpWUHJpbWFyeQp0dHAxMAphKEkwMAoobChsVmMyZTdkOTgxOGQ1N2JlMDI1YTUxYmFk
ZmVmMQooSTEKVlByaW1hcnkKdHRwMTEKYShJMDAKKGwobFZjMmU3ZDk4MThkNjdmZjliMjFjNzZl
YmU3YTcKKEkxClZQcmltYXJ5CnR0cDEyCmEoSTAwCihsKGxWYzJlN2Q5ODE4ZDc1MmJiMzJiNTU4
ODQwMDFkCihJMQpWUHJpbWFyeQp0dHAxMwphKGwobChsKGwobChsKGwobChscDE0ClZjMmU3ZDk4
MThjYzQ5OGRiOGVlM2RlYTQxMzgKcDE1CmFWYzJlN2Q5ODE4Y2U2N2I5ZDE2OTkzZjUwMmQKcDE2
CmFWYzJlN2Q5ODE4ZDE0N2MzZmJlMzllZjU3OGMyCnAxNwphVmMyZTdkOTgxOGQ0OTBjYzA5ZWE3
Zjc4Njg0CnAxOAphVmMyZTdkOTgxOGU5Njg3YTY2OTBkMTJkNTEwMgpwMTkKYUkxMzM5NDQ2NzY4
Cih0STAwCihsdHAyMAou
',3,0,14,130,0,1);
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
INSERT INTO "grampsdb_family" VALUES(1,'c2e7d9803943fb9762fa08aed46','F0009','2012-06-10 22:25:15.833810','1969-12-31 19:00:00',NULL,0,NULL,48,43,5);
INSERT INTO "grampsdb_family" VALUES(2,'c2e7d9811be42ee8096a2072b04','F0012','2012-06-10 22:25:16.082209','1969-12-31 19:00:00',NULL,0,NULL,28,49,1);
INSERT INTO "grampsdb_family" VALUES(3,'c2e7d9819a945a96ff1513a0081','F0016','2012-06-10 22:25:16.401086','1969-12-31 19:00:00',NULL,0,NULL,31,19,5);
INSERT INTO "grampsdb_family" VALUES(4,'c2e7d98165233b3d1514fa732','F0007','2012-06-10 22:25:16.621307','1969-12-31 19:00:00',NULL,0,NULL,46,42,5);
INSERT INTO "grampsdb_family" VALUES(5,'c2e7d9818334185f428ecb1719d','F0019','2012-06-10 22:25:16.644076','1969-12-31 19:00:00',NULL,0,NULL,29,25,5);
INSERT INTO "grampsdb_family" VALUES(6,'c2e7d9819c2551eb6aa8c0c333c','F0017','2012-06-10 22:25:16.743425','1969-12-31 19:00:00',NULL,0,NULL,20,18,5);
INSERT INTO "grampsdb_family" VALUES(7,'c2e7d9818d9d0592e7e396f61d','F0015','2012-06-10 22:25:16.801625','1969-12-31 19:00:00',NULL,0,NULL,63,69,1);
INSERT INTO "grampsdb_family" VALUES(8,'c2e7d9817621bdae63027934dde','F0010','2012-06-10 22:25:16.921089','1969-12-31 19:00:00',NULL,0,NULL,7,34,5);
INSERT INTO "grampsdb_family" VALUES(9,'c2e7d98196d592bec68644108d8','F0014','2012-06-10 22:25:16.973993','1969-12-31 19:00:00',NULL,0,NULL,40,50,1);
INSERT INTO "grampsdb_family" VALUES(10,'c2e7d9803923bfdb91518ebca47','F0001','2012-06-10 22:25:17.125106','1969-12-31 19:00:00',NULL,0,NULL,23,33,5);
INSERT INTO "grampsdb_family" VALUES(11,'c2e7d981466658770dc43b7586e','F0005','2012-06-10 22:25:17.165687','1969-12-31 19:00:00',NULL,0,NULL,57,64,1);
INSERT INTO "grampsdb_family" VALUES(12,'c2e7d981a0633a6e8883fb7ac71','F0018','2012-06-10 22:25:17.194612','1969-12-31 19:00:00',NULL,0,NULL,3,6,5);
INSERT INTO "grampsdb_family" VALUES(13,'c2e7d981335351ada2dae0b88d5','F0003','2012-06-10 22:25:17.371427','1969-12-31 19:00:00',NULL,0,NULL,12,56,5);
INSERT INTO "grampsdb_family" VALUES(14,'c2e7d9816d752e58ba42e9fcb6e','F0008','2012-06-10 22:25:17.655605','1969-12-31 19:00:00',NULL,0,NULL,27,4,5);
INSERT INTO "grampsdb_family" VALUES(15,'c2e7d98129c57a78691b7fe3f52','F0002','2012-06-10 22:25:17.935227','1969-12-31 19:00:00',NULL,0,NULL,14,67,5);
INSERT INTO "grampsdb_family" VALUES(16,'c2e7d98150873e2dbb44ecbcf65','F0006','2012-06-10 22:25:18.146829','1969-12-31 19:00:00',NULL,0,NULL,21,16,5);
INSERT INTO "grampsdb_family" VALUES(17,'c2e7d98188b3af23c99c4f4ef8d','F0013','2012-06-10 22:25:18.372841','1969-12-31 19:00:00',NULL,0,NULL,51,69,5);
INSERT INTO "grampsdb_family" VALUES(18,'c2e7d98182140ba9f409ba160e7','F0011','2012-06-10 22:25:18.404341','1969-12-31 19:00:00',NULL,0,NULL,1,25,1);
INSERT INTO "grampsdb_family" VALUES(19,'c2e7d9813ec1c8a83cb49be562a','F0004','2012-06-10 22:25:18.447402','1969-12-31 19:00:00',NULL,0,NULL,11,58,1);
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
INSERT INTO "grampsdb_source" VALUES(1,'c2e7d981acd5fe9a782e4371147','S0005','2012-06-10 22:25:15.061383','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0005','','','');
INSERT INTO "grampsdb_source" VALUES(2,'c2e7d981b0f594cdb18c1652cd0','S0008','2012-06-10 22:25:15.091490','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0008','','','');
INSERT INTO "grampsdb_source" VALUES(3,'c2e7d981ae557e383f5325d7d6b','S0006','2012-06-10 22:25:15.181379','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0006','','','');
INSERT INTO "grampsdb_source" VALUES(4,'c2e7d981afa70e7f3805ff9cf97','S0007','2012-06-10 22:25:15.220948','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0007','','','');
INSERT INTO "grampsdb_source" VALUES(5,'c2e7d981b3299e0188b1ec76fe','S0010','2012-06-10 22:25:15.260624','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0010','','','');
INSERT INTO "grampsdb_source" VALUES(6,'c2e7d981aa05d3f3af9fd1aa55','S0002','2012-06-10 22:25:15.301377','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0002','','','');
INSERT INTO "grampsdb_source" VALUES(7,'c2e7d981a905f36ea6f8651e849','S0001','2012-06-10 22:25:15.391493','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0001','','','');
INSERT INTO "grampsdb_source" VALUES(8,'c2e7d981aaf4f0a6b6b287487ff','S0003','2012-06-10 22:25:15.500731','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0003','','','');
INSERT INTO "grampsdb_source" VALUES(9,'c2e7d981abe6309eb27d4b07c38','S0004','2012-06-10 22:25:15.520413','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0004','','','');
INSERT INTO "grampsdb_source" VALUES(10,'c2e7d981b415a3eb43cd1b9aec4','S0011','2012-06-10 22:25:15.597182','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0011','','','');
INSERT INTO "grampsdb_source" VALUES(11,'c2e7d981b236742e45ef146d831','S0009','2012-06-10 22:25:15.692047','1969-12-31 19:00:00',NULL,0,NULL,'No title - ID S0009','','','');
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
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,11,1963,0,0,0,0,0,'25 NOV 1963',2438359,0,1,'c2e7d9818705d2a9d0a54ceefb','E0098','2012-06-10 22:25:15.699897','1969-12-31 19:00:00',NULL,0,NULL,11,'',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,9,1855,0,0,0,0,0,'24 SEP 1855',2398851,0,2,'c2e7d9819e44dd8badd21fd8b51','E0123','2012-06-10 22:25:15.042811','1969-12-31 19:00:00',NULL,0,NULL,5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,6,1942,0,0,0,0,0,'JUN 1942',2430512,0,3,'c2e7d981ea15d2ccb5bf1dadc4b','E0143','2012-06-10 22:25:15.046067','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,3,1960,0,0,0,0,0,'MAR 1960',2436995,0,4,'c2e7d9817004199dbf5ca26f835','E0065','2012-06-10 22:25:15.066666','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,27,11,1957,0,0,0,0,0,'27 NOV 1957',2436170,0,5,'c2e7d9818f4674427bce0e28718','E0110','2012-06-10 22:25:15.968256','1969-12-31 19:00:00',NULL,0,NULL,4,'',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,9,1918,0,0,0,0,0,'SEP 1918',2421838,0,6,'c2e7d98122d4bd9271626b89b89','E0023','2012-06-10 22:25:15.995166','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,1,1965,0,0,0,0,0,'9 JAN 1965',2438770,0,7,'c2e7d9815f1681bc649fdece90b','E0056','2012-06-10 22:25:15.998660','1969-12-31 19:00:00',NULL,0,NULL,4,'',23);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,8,'c2e7d98155a401feaa0998798b5','E0049','2012-06-10 22:25:15.082914','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,8,1963,0,0,0,0,0,'AUG 1963',2438243,0,9,'c2e7d98172d174277e6e0abdfe1','E0068','2012-06-10 22:25:15.084355','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,10,'c2e7d9813fa109ddf53df7f5a2b','E0036','2012-06-10 22:25:15.085780','1969-12-31 19:00:00',NULL,0,NULL,18,'Georgetown University',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,11,'c2e7d9817c2777d87ddc0a3dc58','E0079','2012-06-10 22:25:15.092834','1969-12-31 19:00:00',NULL,0,NULL,29,'Cooper, Ward Boss',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,12,'c2e7d9811e173cfa644747596f5','E0017','2012-06-10 22:25:15.095616','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,13,'c2e7d98037f718f0a794e2d3f81','E0006','2012-06-10 22:25:15.097655','1969-12-31 19:00:00',NULL,0,NULL,47,'Bronxville, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,7,1929,0,0,0,0,0,'28 JUL 1929',2425821,0,14,'c2e7d9818ab61293d9617303766','E0103','2012-06-10 22:25:16.034200','1969-12-31 19:00:00',NULL,0,NULL,4,'',14);
INSERT INTO "grampsdb_event" VALUES(0,0,0,24,3,1967,0,0,0,0,0,'24 MAR 1967',2439574,0,15,'c2e7d98160f5242991055c5f9f7','E0057','2012-06-10 22:25:16.037709','1969-12-31 19:00:00',NULL,0,NULL,4,'',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,5,1953,0,0,0,0,0,'23 MAY 1953',2434521,0,16,'c2e7d981c496ff536cd3d1fa3eb','E0131','2012-06-10 22:25:15.103209','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,5,1929,0,0,0,0,0,'MAY 1929',2425733,0,17,'c2e7d98174e7dffa88367ceb7e','E0070','2012-06-10 22:25:15.106367','1969-12-31 19:00:00',NULL,0,NULL,5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,18,'c2e7d980278619a308590dc04ce','E0002','2012-06-10 22:25:16.122546','1969-12-31 19:00:00',NULL,0,NULL,11,'',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,8,1851,0,0,0,0,0,'9 AUG 1851',2397344,0,19,'c2e7d98199d1a7377260caa9956','E0120','2012-06-10 22:25:16.126052','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,9,1960,0,0,0,0,0,'SEP 1960',2437179,0,20,'c2e7d98169540efbd6293605cc5','E0061','2012-06-10 22:25:16.129524','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,21,'c2e7d9818311149395470de3fd1','E0094','2012-06-10 22:25:15.128242','1969-12-31 19:00:00',NULL,0,NULL,47,'Newport, RI',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,12,1957,0,0,0,0,0,'13 DEC 1957',2436186,0,22,'c2e7d9818ff4701d1867e58899f','E0111','2012-06-10 22:25:16.204265','1969-12-31 19:00:00',NULL,0,NULL,14,'',9);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1858,0,0,0,0,0,'22 NOV 1858',2400006,0,23,'c2e7d9817b679fae1ce4aaf400a','E0078','2012-06-10 22:25:16.208524','1969-12-31 19:00:00',NULL,0,NULL,5,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,24,'c2e7d98184048836fa7a48b58d0','E0095','2012-06-10 22:25:15.133154','1969-12-31 19:00:00',NULL,0,NULL,29,'Mayor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,25,'c2e7d981a1d608dac5dbac83934','E0125','2012-06-10 22:25:15.140333','1969-12-31 19:00:00',NULL,0,NULL,29,'Janitor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,1,1995,0,0,0,0,0,'22 JAN 1995',2449740,0,26,'c2e7d981176281ac3fbce52dea4','E0012','2012-06-10 22:25:16.314997','1969-12-31 19:00:00',NULL,0,NULL,5,'',16);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,27,'c2e7d98166957975cf5d3cea108','E0060','2012-06-10 22:25:15.152753','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1940,0,0,0,0,0,'JUL 1940',2429812,0,28,'c2e7d981dfa26a5eb250321b5c1','E0138','2012-06-10 22:25:15.162943','1969-12-31 19:00:00',NULL,0,NULL,43,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,1,1854,0,0,0,0,0,'4 JAN 1854',2398223,0,29,'c2e7d9819d9626a30dec45fc464','E0122','2012-06-10 22:25:16.438776','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,11,1969,0,0,0,0,0,'18 NOV 1969',2440544,0,30,'c2e7d9802605aa5ee22f4c7cb73','E0001','2012-06-10 22:25:16.442304','1969-12-31 19:00:00',NULL,0,NULL,5,'',10);
INSERT INTO "grampsdb_event" VALUES(0,0,0,8,6,1968,0,0,0,0,0,'8 JUN 1968',2440016,0,31,'c2e7d9814f46ed91954c713b2a8','E0043','2012-06-10 22:25:16.571776','1969-12-31 19:00:00',NULL,0,NULL,11,'',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,14,1,1858,0,0,0,0,0,'14 JAN 1858',2399694,0,32,'c2e7d981742633f389097e0c3d6','E0069','2012-06-10 22:25:16.615069','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,33,'c2e7d9816f325d38ff5c94e5b51','E0064','2012-06-10 22:25:15.202976','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1956,0,0,0,0,0,'1956',2435474,0,34,'c2e7d981d3a158ebcb5bb955305','E0134','2012-06-10 22:25:15.205849','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,35,'c2e7d98190a447c044ac2328646','E0113','2012-06-10 22:25:15.217493','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,36,'c2e7d980296774a35c789f442a5','E0004','2012-06-10 22:25:15.220006','1969-12-31 19:00:00',NULL,0,NULL,18,'Harvard Graduate',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1957,0,0,0,0,0,'1957',2435840,0,37,'c2e7d9815a44f203265dfa5b264','E0053','2012-06-10 22:25:15.225572','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,38,'c2e7d9817ca34182beec6b4d1c5','E0082','2012-06-10 22:25:15.228418','1969-12-31 19:00:00',NULL,0,NULL,47,'Liverpool St., East Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1920,0,0,0,0,0,'1920',2422325,0,39,'c2e7d9812b512a0820f7dea3000','E0027','2012-06-10 22:25:16.738158','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,40,'c2e7d9818d752bb32b55884001d','E0109','2012-06-10 22:25:15.232860','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,41,'c2e7d98175f277e780cb869f496','E0073','2012-06-10 22:25:15.237562','1969-12-31 19:00:00',NULL,0,NULL,47,'Webster St., Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,42,'c2e7d98187b2947786b7ccb8bb4','E0099','2012-06-10 22:25:15.243770','1969-12-31 19:00:00',NULL,0,NULL,29,'Senator',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,1,1995,0,0,0,0,0,'25 JAN 1995',2449743,0,43,'c2e7d98118910cf534391ddf973','E0013','2012-06-10 22:25:16.805821','1969-12-31 19:00:00',NULL,0,NULL,11,'',13);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,44,'c2e7d98120b5a7cb2467f7a0b23','E0022','2012-06-10 22:25:15.251741','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,45,'c2e7d9815043a7f6ef556134f73','E0044','2012-06-10 22:25:15.255866','1969-12-31 19:00:00',NULL,0,NULL,47,'Hickory Hill',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,46,'c2e7d9817ccd47f96fb1d0f2e0','E0083','2012-06-10 22:25:15.257916','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,47,'c2e7d98038e7757d98ef03c8c11','E0010','2012-06-10 22:25:15.259968','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,8,1957,0,0,0,0,0,'AUG 1957',2436052,0,48,'c2e7d98180752fe1e5496b64586','E0090','2012-06-10 22:25:16.852724','1969-12-31 19:00:00',NULL,0,NULL,5,'',17);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,49,'c2e7d9811a4aff7cb9890c91fe','E0015','2012-06-10 22:25:15.274021','1969-12-31 19:00:00',NULL,0,NULL,47,'Died of complications due to pneumonia. ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1821,0,0,0,0,0,'1821',2386167,0,50,'c2e7d9817de4e50451349e3f818','E0084','2012-06-10 22:25:15.297379','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,51,'c2e7d981a391c45fbebdff8aee0','E0127','2012-06-10 22:25:15.299014','1969-12-31 19:00:00',NULL,0,NULL,29,'Teamster',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,9,1923,0,0,0,0,0,'7 SEP 1923',2423670,0,52,'c2e7d9814642b4a30a7abc27ced','E0039','2012-06-10 22:25:15.300551','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,53,'c2e7d98192d187fef93b2763ed3','E0116','2012-06-10 22:25:15.307560','1969-12-31 19:00:00',NULL,0,NULL,18,'Brown Univ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,54,'c2e7d98175d18d1df57b85880c4','E0072','2012-06-10 22:25:15.309849','1969-12-31 19:00:00',NULL,0,NULL,47,'Meridian St., East Boston, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,55,'c2e7d9818116231e029ac97fc6c','E0091','2012-06-10 22:25:16.908226','1969-12-31 19:00:00',NULL,0,NULL,11,'',26);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,56,'c2e7d98029940bad318b6258380','E0005','2012-06-10 22:25:15.314258','1969-12-31 19:00:00',NULL,0,NULL,47,'Joe Kennedy was a very hard worker, which often deteriorated',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,57,'c2e7d9819092271e43f7bf9012f','E0112','2012-06-10 22:25:15.316301','1969-12-31 19:00:00',NULL,0,NULL,18,'Brearly School',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,11,1925,0,0,0,0,0,'20 NOV 1925',2424475,0,58,'c2e7d9814df10a016dc3d0e5462','E0041','2012-06-10 22:25:16.913419','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,8,1963,0,0,0,0,0,'7 AUG 1963',2438249,0,59,'c2e7d981944134e9155f1b7cfb8','E0117','2012-06-10 22:25:16.916890','1969-12-31 19:00:00',NULL,0,NULL,4,'',24);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,11,1915,0,0,0,0,0,'9 NOV 1915',2420811,0,60,'c2e7d981321708e6de44e1e0f96','E0030','2012-06-10 22:25:16.969782','1969-12-31 19:00:00',NULL,0,NULL,4,'',5);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,61,'c2e7d9813b435b4a9ec53e2a5c','E0032','2012-06-10 22:25:15.347911','1969-12-31 19:00:00',NULL,0,NULL,47,'Timberlawn, MD',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,62,'c2e7d9817506191fc07a6afa454','E0071','2012-06-10 22:25:15.350935','1969-12-31 19:00:00',NULL,0,NULL,29,'Dockhand, Saloonkeeper, Senator, Bank President',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,7,1890,0,0,0,0,0,'22 JUL 1890',2411571,0,63,'c2e7d98115e17cf95dcc84e1dbb','E0011','2012-06-10 22:25:16.980764','1969-12-31 19:00:00',NULL,0,NULL,4,'',6);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1923,0,0,0,0,0,'1923',2423421,0,64,'c2e7d98179c623d0415bf903305','E0075','2012-06-10 22:25:15.356329','1969-12-31 19:00:00',NULL,0,NULL,5,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1882,0,0,0,0,0,'1882',2408447,0,65,'c2e7d981e8d3e28ecd8cb514b2b','E0142','2012-06-10 22:25:16.985190','1969-12-31 19:00:00',NULL,0,NULL,37,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,9,1944,0,0,0,0,0,'10 SEP 1944',2431344,0,66,'c2e7d98128a1164b3957677e039','E0026','2012-06-10 22:25:16.988801','1969-12-31 19:00:00',NULL,0,NULL,5,'',27);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1883,0,0,0,0,0,'1883',2408812,0,67,'c2e7d981e623fb7c8ea8b0a5b03','E0140','2012-06-10 22:25:16.993094','1969-12-31 19:00:00',NULL,0,NULL,37,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,12,1968,0,0,0,0,0,'12 DEC 1968',2440203,0,68,'c2e7d9816302b35cb69c5ff5cf','E0058','2012-06-10 22:25:16.996568','1969-12-31 19:00:00',NULL,0,NULL,4,'',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1958,0,0,0,0,0,'1958',2436205,0,69,'c2e7d9815ba64ca1a0870e97e64','E0054','2012-06-10 22:25:15.384793','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,7,1951,0,0,0,0,0,'4 JUL 1951',2433832,0,70,'c2e7d98152f6d62763056d39b98','E0047','2012-06-10 22:25:15.387815','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,71,'c2e7d98150617043edb79cdfdc5','E0045','2012-06-10 22:25:15.393804','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,72,'c2e7d9818d67ff9b21c76ebe7a7','E0108','2012-06-10 22:25:15.397485','1969-12-31 19:00:00',NULL,0,NULL,47,'Martha''s Vineyard ',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,73,'c2e7d9813eb3da305a5107fc3b3','E0035','2012-06-10 22:25:15.399611','1969-12-31 19:00:00',NULL,0,NULL,29,'Actor',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,13,5,1948,0,0,0,0,0,'13 MAY 1948',2432685,0,74,'c2e7d9812ca56268037cd0295e','E0028','2012-06-10 22:25:17.200805','1969-12-31 19:00:00',NULL,0,NULL,5,'',25);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,75,'c2e7d9817c310c915a0cb7070f6','E0080','2012-06-10 22:25:15.432087','1969-12-31 19:00:00',NULL,0,NULL,47,'He died of an outbreak of Cholera.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,76,'c2e7d9817f4746171245236274c','E0087','2012-06-10 22:25:15.440429','1969-12-31 19:00:00',NULL,0,NULL,47,'Her death was caused by a cerebral hemorrhage.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,12,1888,0,0,0,0,0,'20 DEC 1888',2410992,0,77,'c2e7d9817e1690352c6bf2da24','E0085','2012-06-10 22:25:17.344805','1969-12-31 19:00:00',NULL,0,NULL,5,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,20,7,1965,0,0,0,0,0,'20 JUL 1965',2438962,0,78,'c2e7d98144637538c4bc54b5853','E0038','2012-06-10 22:25:17.349244','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1915,0,0,0,0,0,'JUL 1915',2420680,0,79,'c2e7d9811e3a2a2c4e47e5c1a7','E0018','2012-06-10 22:25:17.367202','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1954,0,0,0,0,0,'1954',2434744,0,80,'c2e7d98157245ed5085594588c9','E0051','2012-06-10 22:25:15.455248','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,81,'c2e7d9803823a3b1415bfb65293','E0007','2012-06-10 22:25:15.473450','1969-12-31 19:00:00',NULL,0,NULL,47,'Hyannis, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,5,1924,0,0,0,0,0,'6 MAY 1924',2423912,0,82,'c2e7d98147223b844cac979c110','E0040','2012-06-10 22:25:17.503107','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,26,9,1961,0,0,0,0,0,'26 SEP 1961',2437569,0,83,'c2e7d9817176ac23cc6bbd8dde8','E0067','2012-06-10 22:25:15.487686','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,84,'c2e7d9817c96bd4f7fed7582b73','E0081','2012-06-10 22:25:15.490701','1969-12-31 19:00:00',NULL,0,NULL,47,'Duganstown, Ireland',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,25,11,1960,0,0,0,0,0,'25 NOV 1960',2437264,0,85,'c2e7d9819222c125c85eccd24cd','E0115','2012-06-10 22:25:17.522650','1969-12-31 19:00:00',NULL,0,NULL,4,'',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,86,'c2e7d9813d47532ba58297c4cb5','E0033','2012-06-10 22:25:15.499524','1969-12-31 19:00:00',NULL,0,NULL,27,'III',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,9,1872,0,0,0,0,0,'22 SEP 1872',2405059,0,87,'c2e7d981e7871b0349b4d8fd87a','E0141','2012-06-10 22:25:17.530109','1969-12-31 19:00:00',NULL,0,NULL,37,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,88,'c2e7d98180662a977b687755898','E0089','2012-06-10 22:25:15.513017','1969-12-31 19:00:00',NULL,0,NULL,27,'III',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,89,'c2e7d9817f744fd720533203ceb','E0088','2012-06-10 22:25:15.515900','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,90,'c2e7d9818cb67ecab5d99e57b6a','E0106','2012-06-10 22:25:15.519250','1969-12-31 19:00:00',NULL,0,NULL,47,'In 1955 Jackie suffered a miscarriage',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1823,0,0,0,0,0,'1823',2386897,0,91,'c2e7d9817ac52515d08d04c374f','E0077','2012-06-10 22:25:17.562671','1969-12-31 19:00:00',NULL,0,NULL,4,'',4);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,2,1932,0,0,0,0,0,'22 FEB 1932',2426760,0,92,'c2e7d9816c73db8348b0c6b01fb','E0062','2012-06-10 22:25:17.566198','1969-12-31 19:00:00',NULL,0,NULL,4,'',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,28,9,1849,0,0,0,0,0,'28 SEP 1849',2396664,0,93,'c2e7d981dd14afab07b5fd2a825','E0137','2012-06-10 22:25:17.641756','1969-12-31 19:00:00',NULL,0,NULL,37,'',2);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,94,'c2e7d9811a1f15c8ca34e502e0','E0014','2012-06-10 22:25:15.540790','1969-12-31 19:00:00',NULL,0,NULL,18,'Dorchester High School, Sacred Heart Convent',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,5,1917,0,0,0,0,0,'29 MAY 1917',2421378,0,95,'c2e7d98185c6a8d02b66ba6720e','E0096','2012-06-10 22:25:17.646135','1969-12-31 19:00:00',NULL,0,NULL,4,'',12);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,96,'c2e7d98038670eda1681bfcb8ad','E0008','2012-06-10 22:25:15.543844','1969-12-31 19:00:00',NULL,0,NULL,47,'Palm Beach, FL',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,97,'c2e7d9817eb6481cbdcc5dd24f8','E0086','2012-06-10 22:25:17.650548','1969-12-31 19:00:00',NULL,0,NULL,11,'',18);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1954,0,0,0,0,0,'1954',2434744,0,98,'c2e7d9813d52bee4e492ba2245d','E0034','2012-06-10 22:25:15.548693','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,99,'c2e7d98124158abcb87753d2fe7','E0024','2012-06-10 22:25:15.551506','1969-12-31 19:00:00',NULL,0,NULL,47,'In 1941 she had a frontal lobotomy.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,12,1852,0,0,0,0,0,'4 DEC 1852',2397827,0,100,'c2e7d9819c06483737f3aa7ec2b','E0121','2012-06-10 22:25:15.560545','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,7,1921,0,0,0,0,0,'JUL 1921',2422872,0,101,'c2e7d9813796e3316d81dfcdd9e','E0031','2012-06-10 22:25:17.715124','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,102,'c2e7d9818207e3cb8b4d457442f','E0093','2012-06-10 22:25:15.563568','1969-12-31 19:00:00',NULL,0,NULL,47,'East Hampton, NY',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,23,5,1994,0,0,0,0,0,'23 MAY 1994',2449496,0,103,'c2e7d9818bf1ac1f5e4218cc620','E0105','2012-06-10 22:25:17.719491','1969-12-31 19:00:00',NULL,0,NULL,11,'',3);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1928,0,0,0,0,0,'1928',2425247,0,104,'c2e7d9815222289d4718eaba123','E0046','2012-06-10 22:25:15.570853','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,2,8,1944,0,0,0,0,0,'2 AUG 1944',2431305,0,105,'c2e7d9811f13b0c22ee70ef397c','E0019','2012-06-10 22:25:17.858562','1969-12-31 19:00:00',NULL,0,NULL,5,'',28);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,5,1944,0,0,0,0,0,'6 MAY 1944',2431217,0,106,'c2e7d981c041fbc32870fde9054','E0130','2012-06-10 22:25:17.862619','1969-12-31 19:00:00',NULL,0,NULL,37,'',15);
INSERT INTO "grampsdb_event" VALUES(0,0,0,7,10,1914,0,0,0,0,0,'7 OCT 1914',2420413,0,107,'c2e7d981bed7518f36fe418885','E0129','2012-06-10 22:25:17.866555','1969-12-31 19:00:00',NULL,0,NULL,37,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,9,1888,0,0,0,0,0,'6 SEP 1888',2410887,0,108,'c2e7d98023657b23677fbf8708b','E0000','2012-06-10 22:25:17.871831','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,109,'c2e7d98171643772096e4ec7e6b','E0066','2012-06-10 22:25:15.589619','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,110,'c2e7d98181a1af703aae68bfc02','E0092','2012-06-10 22:25:15.591208','1969-12-31 19:00:00',NULL,0,NULL,47,'Died of cancer.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,111,'c2e7d9819212028f5946ff0297a','E0114','2012-06-10 22:25:15.595116','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1887,0,0,0,0,0,'1887',2410273,0,112,'c2e7d981d927e174bbf58be9ef9','E0136','2012-06-10 22:25:15.596560','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,113,'c2e7d9818d57be025a51badfef1','E0107','2012-06-10 22:25:15.598681','1969-12-31 19:00:00',NULL,0,NULL,47,'5th Avenue, NYC, NY',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,114,'c2e7d98038b786aea1f239427ad','E0009','2012-06-10 22:25:15.603978','1969-12-31 19:00:00',NULL,0,NULL,47,'Brookline, MA',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,22,11,1963,0,0,0,0,0,'22 NOV 1963',2438356,0,115,'c2e7d981866566a4046a200fbd6','E0097','2012-06-10 22:25:18.010725','1969-12-31 19:00:00',NULL,0,NULL,5,'',20);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,116,'c2e7d98188a772317c9793d7e06','E0102','2012-06-10 22:25:15.606867','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,2,1928,0,0,0,0,0,'FEB 1928',2425278,0,117,'c2e7d98165d4b33177f0bd1d90a','E0059','2012-06-10 22:25:18.076256','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,118,'c2e7d98029370e7f1d074cba5d8','E0003','2012-06-10 22:25:15.614676','1969-12-31 19:00:00',NULL,0,NULL,29,'Bank President, Ambassador',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1898,0,0,0,0,0,'1898',2414291,0,119,'c2e7d98196b2fcfe46d41cf065d','E0119','2012-06-10 22:25:15.618069','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,120,'c2e7d9812013868484116e993c3','E0021','2012-06-10 22:25:15.627524','1969-12-31 19:00:00',NULL,0,NULL,47,'He suffered 2 cases of Jaundice during his beginning years a',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,121,'c2e7d981a2b4b631e24f5b4dbd2','E0126','2012-06-10 22:25:15.633346','1969-12-31 19:00:00',NULL,0,NULL,29,'Clerk',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1952,0,0,0,0,0,'1952',2434013,0,122,'c2e7d98154417d3a553ba91a60d','E0048','2012-06-10 22:25:15.636053','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,123,'c2e7d9817602255a08a6ea423b0','E0074','2012-06-10 22:25:15.637655','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,2,1964,0,0,0,0,0,'FEB 1964',2438427,0,124,'c2e7d9814273d42ca42f86ef577','E0037','2012-06-10 22:25:18.229677','1969-12-31 19:00:00',NULL,0,NULL,4,'',7);
INSERT INTO "grampsdb_event" VALUES(0,0,0,9,8,1963,0,0,0,0,0,'9 AUG 1963',2438251,0,125,'c2e7d98194d1eccf69327f26868','E0118','2012-06-10 22:25:18.233207','1969-12-31 19:00:00',NULL,0,NULL,5,'',19);
INSERT INTO "grampsdb_event" VALUES(0,0,0,17,6,1950,0,0,0,0,0,'17 JUN 1950',2433450,0,126,'c2e7d981d054ac642daaf37186b','E0133','2012-06-10 22:25:18.236703','1969-12-31 19:00:00',NULL,0,NULL,37,'',1);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1955,0,0,0,0,0,'1955',2435109,0,127,'c2e7d98158e6819eaaca236503f','E0052','2012-06-10 22:25:15.643984','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,128,'c2e7d98187e764e03d39c6d1b8a','E0101','2012-06-10 22:25:15.645584','1969-12-31 19:00:00',NULL,0,NULL,47,'Later on in life he faced serious back surgery two times, on',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1953,0,0,0,0,0,'1953',2434379,0,129,'c2e7d98155a3067712c37754513','E0050','2012-06-10 22:25:15.647038','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,19,5,1994,0,0,0,0,0,'19 MAY 1994',2449492,0,130,'c2e7d9818b515b32829896bc927','E0104','2012-06-10 22:25:18.317389','1969-12-31 19:00:00',NULL,0,NULL,5,'',22);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,131,'c2e7d98179e21030dafd57451c8','E0076','2012-06-10 22:25:15.652485','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,6,6,1968,0,0,0,0,0,'6 JUN 1968',2440014,0,132,'c2e7d9814ea2a4dee17e4251acb','E0042','2012-06-10 22:25:18.321810','1969-12-31 19:00:00',NULL,0,NULL,5,'',8);
INSERT INTO "grampsdb_event" VALUES(0,0,0,18,7,1855,0,0,0,0,0,'18 JUL 1855',2398783,0,133,'c2e7d9819fc89cf81d325feca7','E0124','2012-06-10 22:25:18.325510','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,134,'c2e7d9816d64bd454c10afc290d','E0063','2012-06-10 22:25:15.661956','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,29,11,1958,0,0,0,0,0,'29 NOV 1958',2436537,0,135,'c2e7d981d6574ccc32392b62310','E0135','2012-06-10 22:25:15.663393','1969-12-31 19:00:00',NULL,0,NULL,37,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,136,'c2e7d98187c5f05a35bf4ae88bd','E0100','2012-06-10 22:25:15.664816','1969-12-31 19:00:00',NULL,0,NULL,18,'Choate, London Sch. Of Econ., Princeton, Harvard',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,10,12,1917,0,0,0,0,0,'10 DEC 1917',2421573,0,137,'c2e7d98128744b237bb0011aee2','E0025','2012-06-10 22:25:15.666260','1969-12-31 19:00:00',NULL,0,NULL,4,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,12,9,1953,0,0,0,0,0,'12 SEP 1953',2434633,0,138,'c2e7d981e3b34419998c9467446','E0139','2012-06-10 22:25:18.366007','1969-12-31 19:00:00',NULL,0,NULL,37,'',11);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,139,'c2e7d98131f2561c50729351265','E0029','2012-06-10 22:25:15.674010','1969-12-31 19:00:00',NULL,0,NULL,27,'Jr.',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,140,'c2e7d9811ba63df6d641e1d6a43','E0016','2012-06-10 22:25:15.675445','1969-12-31 19:00:00',NULL,0,NULL,33,'Roman Catholic',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1965,0,0,0,0,0,'1965',2438762,0,141,'c2e7d981c864a7296a834610378','E0132','2012-06-10 22:25:15.685488','1969-12-31 19:00:00',NULL,0,NULL,43,'',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,0,0,0,0,0,0,'',0,0,142,'c2e7d9811ff7b8590e73e209d67','E0020','2012-06-10 22:25:15.690178','1969-12-31 19:00:00',NULL,0,NULL,18,'Harvard University, Harvard Law School',NULL);
INSERT INTO "grampsdb_event" VALUES(0,0,0,0,0,1892,0,0,0,0,0,'1892',2412099,0,143,'c2e7d981a475bfe1cf7484fe831','E0128','2012-06-10 22:25:18.596689','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
INSERT INTO "grampsdb_event" VALUES(0,0,0,4,6,1963,0,0,0,0,0,'4 JUN 1963',2438185,0,144,'c2e7d9815d1591c860096c3a0ff','E0055','2012-06-10 22:25:18.600956','1969-12-31 19:00:00',NULL,0,NULL,4,'',21);
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
INSERT INTO "grampsdb_place" VALUES(1,'c2e7d981d0e488927236c973387','P0051','2012-06-10 22:25:15.056948','1969-12-31 19:00:00',NULL,0,NULL,'Greenwich, Connecticut','','');
INSERT INTO "grampsdb_place" VALUES(2,'c2e7d981dd9253baf6f159c49f2','P0053','2012-06-10 22:25:15.067267','1969-12-31 19:00:00',NULL,0,NULL,'Holy Cross Cathedral, Boston, MA','','');
INSERT INTO "grampsdb_place" VALUES(3,'c2e7d9814fe390d1a70b2005d49','P0023','2012-06-10 22:25:15.078304','1969-12-31 19:00:00',NULL,0,NULL,'Arlington National, VA','','');
INSERT INTO "grampsdb_place" VALUES(4,'c2e7d9817b56533ae4b9d6d11eb','P0029','2012-06-10 22:25:15.105033','1969-12-31 19:00:00',NULL,0,NULL,'Dunganstown, Ireland','','');
INSERT INTO "grampsdb_place" VALUES(5,'c2e7d9813316b941b6b0610ad09','P0017','2012-06-10 22:25:15.111985','1969-12-31 19:00:00',NULL,0,NULL,'Westminster, MD','','');
INSERT INTO "grampsdb_place" VALUES(6,'c2e7d9811713280dcadd2246581','P0007','2012-06-10 22:25:15.130305','1969-12-31 19:00:00',NULL,0,NULL,'North End, Boston, MA','','');
INSERT INTO "grampsdb_place" VALUES(7,'c2e7d98142f1ddd5ced580b8239','P0019','2012-06-10 22:25:15.238392','1969-12-31 19:00:00',NULL,0,NULL,'Washington, DC','','');
INSERT INTO "grampsdb_place" VALUES(8,'c2e7d9814f277250b3d906813e7','P0021','2012-06-10 22:25:15.278217','1969-12-31 19:00:00',NULL,0,NULL,'Los Angeles, CA','','');
INSERT INTO "grampsdb_place" VALUES(9,'c2e7d98190713f6bfce46bf4ec0','P0043','2012-06-10 22:25:15.328884','1969-12-31 19:00:00',NULL,0,NULL,'St. Patricks Cathedral','','');
INSERT INTO "grampsdb_place" VALUES(10,'c2e7d98027539da81413f86db4b','P0003','2012-06-10 22:25:15.329601','1969-12-31 19:00:00',NULL,0,NULL,'Hyannis Port, MA','','');
INSERT INTO "grampsdb_place" VALUES(11,'c2e7d981e443fc750f3a5523ae9','P0055','2012-06-10 22:25:15.330239','1969-12-31 19:00:00',NULL,0,NULL,'Newport, RI','','');
INSERT INTO "grampsdb_place" VALUES(12,'c2e7d9816d024c64a018da9c8cb','P0027','2012-06-10 22:25:15.352136','1969-12-31 19:00:00',NULL,0,NULL,'Brookline, MA','','');
INSERT INTO "grampsdb_place" VALUES(13,'c2e7d980290dfba8c6111d8681','P0005','2012-06-10 22:25:15.365059','1969-12-31 19:00:00',NULL,0,NULL,'Holyhood Cemetery, Brookline, MA ','','');
INSERT INTO "grampsdb_place" VALUES(14,'c2e7d9818b348154106ceeca5d1','P0039','2012-06-10 22:25:15.382084','1969-12-31 19:00:00',NULL,0,NULL,'Southampton, Long Island, NY','','');
INSERT INTO "grampsdb_place" VALUES(15,'c2e7d981c0c5c3a9a99860f9a42','P0049','2012-06-10 22:25:15.394642','1969-12-31 19:00:00',NULL,0,NULL,'London','','');
INSERT INTO "grampsdb_place" VALUES(16,'c2e7d9811862333e940d3d36f6f','P0009','2012-06-10 22:25:15.395316','1969-12-31 19:00:00',NULL,0,NULL,'Hyannis Port, MA ','','');
INSERT INTO "grampsdb_place" VALUES(17,'c2e7d98180f64cd92fbc10fe3ce','P0033','2012-06-10 22:25:15.421588','1969-12-31 19:00:00',NULL,0,NULL,'Lennox Hill Hosp., NY','','');
INSERT INTO "grampsdb_place" VALUES(18,'c2e7d9817f378c2dec0ce4c8285','P0031','2012-06-10 22:25:15.422088','1969-12-31 19:00:00',NULL,0,NULL,'Cathedral Of The Holy Cross, MA','','');
INSERT INTO "grampsdb_place" VALUES(19,'c2e7d9819556ab75cb9f638bd53','P0047','2012-06-10 22:25:15.434601','1969-12-31 19:00:00',NULL,0,NULL,'Boston, Mass','','');
INSERT INTO "grampsdb_place" VALUES(20,'c2e7d98186e4f9c701b41a36a5f','P0037','2012-06-10 22:25:15.435265','1969-12-31 19:00:00',NULL,0,NULL,'Dallas, TX','','');
INSERT INTO "grampsdb_place" VALUES(21,'c2e7d98025b73928981abcd464','P0001','2012-06-10 22:25:15.445343','1969-12-31 19:00:00',NULL,0,NULL,'Boston, MA','','');
INSERT INTO "grampsdb_place" VALUES(22,'c2e7d9818be1696aedef5079ccc','P0041','2012-06-10 22:25:15.528339','1969-12-31 19:00:00',NULL,0,NULL,'NYC, NY','','');
INSERT INTO "grampsdb_place" VALUES(23,'c2e7d9815f97082df4d525d64d5','P0025','2012-06-10 22:25:15.591831','1969-12-31 19:00:00',NULL,0,NULL,'New York','','');
INSERT INTO "grampsdb_place" VALUES(24,'c2e7d98194b2b5bf5c886dd0f90','P0045','2012-06-10 22:25:15.607471','1969-12-31 19:00:00',NULL,0,NULL,'Otis Air Force B, Mass','','');
INSERT INTO "grampsdb_place" VALUES(25,'c2e7d9812db79e50b2f4ba193b2','P0015','2012-06-10 22:25:15.609286','1969-12-31 19:00:00',NULL,0,NULL,'France','','');
INSERT INTO "grampsdb_place" VALUES(26,'c2e7d981818e31aa2beb6bd794','P0035','2012-06-10 22:25:15.642658','1969-12-31 19:00:00',NULL,0,NULL,'St. Philomena''s Cemetery, NY','','');
INSERT INTO "grampsdb_place" VALUES(27,'c2e7d9812997b0ded88d5487e0d','P0013','2012-06-10 22:25:15.672673','1969-12-31 19:00:00',NULL,0,NULL,'Belgium','','');
INSERT INTO "grampsdb_place" VALUES(28,'c2e7d9811fd1330bccebd96b28e','P0011','2012-06-10 22:25:15.694017','1969-12-31 19:00:00',NULL,0,NULL,'Suffolk, England','','');
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
INSERT INTO "grampsdb_note" VALUES(1,'c2e7d9817c55526722b5897e12a','N0038','2012-06-10 22:25:15.035821','1969-12-31 19:00:00',NULL,0,NULL,3,'The potato famine of 1845-48, plagued the country of Ireland and pushed many Irishmen to flee to the land of promise, the USA. Patrick Kennedy was among those to leave his home in Wexford County, Ireland, in 1848, in hopes of finding a better
life in the US. Once he arrived in the US, he settled in East Boston, where he remained for the rest of his life.',0);
INSERT INTO "grampsdb_note" VALUES(2,'c2e7d981ac571aa49322c4b6412','N0060','2012-06-10 22:25:15.038979','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0004:

Line ignored as not understood     Line   701: 1 NAME New York Times, March 6, 1946.
',0);
INSERT INTO "grampsdb_note" VALUES(3,'c2e7d981ab63c4bfc6b1ad335b2','N0059','2012-06-10 22:25:15.047504','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0003:

Line ignored as not understood     Line   699: 1 NAME New York Times, March 4, 1946, pp. 1,3.
',0);
INSERT INTO "grampsdb_note" VALUES(4,'c2e7d98175285db77279797c28','N0033','2012-06-10 22:25:15.055643','1969-12-31 19:00:00',NULL,0,NULL,3,'As a young man, Patrick dropped out of school to work on the docks of Boston.',0);
INSERT INTO "grampsdb_note" VALUES(5,'c2e7d9818802e5e500e76024dbf','N0046','2012-06-10 22:25:15.062605','1969-12-31 19:00:00',NULL,0,NULL,3,'<img src="http://www.jacqueslowe.com/html/photographs/jfk/images/jfkp52bw.jpg" border=1>',0);
INSERT INTO "grampsdb_note" VALUES(6,'c2e7d9812465f7984cb185da276','N0015','2012-06-10 22:25:15.064514','1969-12-31 19:00:00',NULL,0,NULL,3,'She was born severely mentally retarded. For years her parents were ashamed of her and never told anyone about her problems.',0);
INSERT INTO "grampsdb_note" VALUES(7,'c2e7d981b7f533a7d7145101942','N0074','2012-06-10 22:25:15.070007','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   728: 0 C7 CSTA
Skipped subordinate line           Line   729: 1 NAME Adopted Twin
',0);
INSERT INTO "grampsdb_note" VALUES(8,'c2e7d98188924cabda321db84ba','N0050','2012-06-10 22:25:15.075601','1969-12-31 19:00:00',NULL,0,NULL,3,'He was assassinated in Dallas, TX.',0);
INSERT INTO "grampsdb_note" VALUES(9,'c2e7d981a9742ee5f69a83ea6d6','N0057','2012-06-10 22:25:15.079606','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0001:

Line ignored as not understood     Line   695: 1 NAME Joseph P. Kennedy, A Life and Times, by David E. Koskoff.
',0);
INSERT INTO "grampsdb_note" VALUES(10,'c2e7d9816d43190e4a6c955092a','N0031','2012-06-10 22:25:15.087070','1969-12-31 19:00:00',NULL,0,NULL,3,'Was known as "Teddy".',0);
INSERT INTO "grampsdb_note" VALUES(11,'c2e7d981b2a15db832f02051586','N0065','2012-06-10 22:25:15.089231','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0009:

Line ignored as not understood     Line   711: 1 NAME Harrisburg Patriot News, 23 May 1994.
',0);
INSERT INTO "grampsdb_note" VALUES(12,'c2e7d9815004746bfffc2650c9e','N0027','2012-06-10 22:25:15.109386','1969-12-31 19:00:00',NULL,0,NULL,3,'Robert Francis was assassinated in California during his 1968 presidential campaign.',0);
INSERT INTO "grampsdb_note" VALUES(13,'c2e7d98037c6f173e34ba8aa0a9','N0004','2012-06-10 22:25:15.113129','1969-12-31 19:00:00',NULL,0,NULL,3,'He was fiercely proud of his family. He was quoted as having said his family was the finest thing in his life. ',0);
INSERT INTO "grampsdb_note" VALUES(14,'c2e7d98120a158f5708f62efcdb','N0013','2012-06-10 22:25:15.117175','1969-12-31 19:00:00',NULL,0,NULL,3,'He was known as Jack.',0);
INSERT INTO "grampsdb_note" VALUES(15,'c2e7d9817f64aed876e0b99404c','N0041','2012-06-10 22:25:15.122154','1969-12-31 19:00:00',NULL,0,NULL,3,'After her husband died, she opened up a "Notions Shop" to provide for her family.',0);
INSERT INTO "grampsdb_note" VALUES(16,'c2e7d981271720f4434c6db3d26','N0017','2012-06-10 22:25:15.135835','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0004:

Empty note ignored                 Line    98: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(17,'c2e7d9815033c3f2d05c7f1a982','N0028','2012-06-10 22:25:15.141609','1969-12-31 19:00:00',NULL,0,NULL,3,'He was very dedicated to his children and every evening had prayers with them, each of them saying the Rosary.',0);
INSERT INTO "grampsdb_note" VALUES(18,'c2e7d981b6f63b0a54f02886c0f','N0072','2012-06-10 22:25:15.146264','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   724: 0 C5 CSTA
Skipped subordinate line           Line   725: 1 NAME Stillborn
',0);
INSERT INTO "grampsdb_note" VALUES(19,'c2e7d9811ad13d32faabb0ab30f','N0007','2012-06-10 22:25:15.149201','1969-12-31 19:00:00',NULL,0,NULL,3,'She graduated from high school, one of the three highest in a class of 285. She was then sent to finish school in Europe for two years.',0);
INSERT INTO "grampsdb_note" VALUES(20,'c2e7d9813349b015f3db31de2b','N0021','2012-06-10 22:25:15.156518','1969-12-31 19:00:00',NULL,0,NULL,3,'1972 was the vice presidential candidate.',0);
INSERT INTO "grampsdb_note" VALUES(21,'c2e7d9811d2773e6ea5cccef41d','N0010','2012-06-10 22:25:15.159813','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0002:

Empty note ignored                 Line    58: 1 NOTE 
Empty note ignored                 Line    60: 1 NOTE 
Empty note ignored                 Line    62: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(22,'c2e7d9817c87e57a02eb5330d17','N0039','2012-06-10 22:25:15.164200','1969-12-31 19:00:00',NULL,0,NULL,3,'Upon Patrick''s arrival in Boston, he immediately became involved in politics. He was known as a Ward Boss in Boston, looking out for the other Irish immigrants and trying to improve the conditions in the community.',0);
INSERT INTO "grampsdb_note" VALUES(23,'c2e7d98147c625cf389af2f2e41','N0026','2012-06-10 22:25:15.166122','1969-12-31 19:00:00',NULL,0,NULL,3,'Was a help to her brother John F. during his political campaigns.',0);
INSERT INTO "grampsdb_note" VALUES(24,'c2e7d9817556015ad3b0c4eb845','N0034','2012-06-10 22:25:15.170746','1969-12-31 19:00:00',NULL,0,NULL,3,'Patrick was able to work his way from being a SaloonKeeper to becoming a Ward Boss, helping out other Irish immigrants. His popularity  rose and at the age of thirty he had become a power in Boston politics. In 1892 and 1893 he was elected to
the Massachusetts Senate.',0);
INSERT INTO "grampsdb_note" VALUES(25,'c2e7d9802d7350857b331d1200f','N0001','2012-06-10 22:25:15.172668','1969-12-31 19:00:00',NULL,0,NULL,3,'He had an interesting hobby of tinkering with clocks.',0);
INSERT INTO "grampsdb_note" VALUES(26,'c2e7d9812e5666554debe8b2223','N0019','2012-06-10 22:25:15.195832','1969-12-31 19:00:00',NULL,0,NULL,3,'Served with the Red Cross in England during the war.',0);
INSERT INTO "grampsdb_note" VALUES(27,'c2e7d981b5878726b21eaed3d03','N0069','2012-06-10 22:25:15.211213','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   718: 0 C2 CSTA
Skipped subordinate line           Line   719: 1 NAME Adopted
',0);
INSERT INTO "grampsdb_note" VALUES(28,'c2e7d9817d215fd0cc5541d6f7f','N0040','2012-06-10 22:25:15.269708','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0046:

Empty note ignored                 Line   438: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(29,'c2e7d981826c13718a9723ff14','N0044','2012-06-10 22:25:15.275731','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0048:

Empty note ignored                 Line   473: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(30,'c2e7d981b78d0d8b89584c4aff','N0073','2012-06-10 22:25:15.279720','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   726: 0 C6 CSTA
Skipped subordinate line           Line   727: 1 NAME Foster
',0);
INSERT INTO "grampsdb_note" VALUES(31,'c2e7d981aec7b102455b8bf26fc','N0062','2012-06-10 22:25:15.283857','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0006:

Line ignored as not understood     Line   705: 1 NAME The Kennedys Dynasty and Disaster 1848-1983, by John H. Davis.
',0);
INSERT INTO "grampsdb_note" VALUES(32,'c2e7d98188672ce8dcff5bc755b','N0049','2012-06-10 22:25:15.287990','1969-12-31 19:00:00',NULL,0,NULL,3,'He had personal finances that were estimated to be around $10 million while in the Presidency.',0);
INSERT INTO "grampsdb_note" VALUES(33,'c2e7d981517482dd27c7dcf26e4','N0029','2012-06-10 22:25:15.290292','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0021:

Empty note ignored                 Line   237: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(34,'c2e7d9812e060ddd2f5cfa8aa21','N0018','2012-06-10 22:25:15.293558','1969-12-31 19:00:00',NULL,0,NULL,3,'Died in an airplane crash with her lover in France three years after her older brother Joseph''s death.',0);
INSERT INTO "grampsdb_note" VALUES(35,'c2e7d98178f6b15a96bfcb1a419','N0037','2012-06-10 22:25:15.303231','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0044:

Empty note ignored                 Line   402: 1 NOTE 
Empty note ignored                 Line   405: 1 NOTE 
Empty note ignored                 Line   407: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(36,'c2e7d981884475a9a5f06186e07','N0048','2012-06-10 22:25:15.320181','1969-12-31 19:00:00',NULL,0,NULL,3,'He wrote 2 books, including "Profiles in Courage", which won him a Pulitzer Prize.',0);
INSERT INTO "grampsdb_note" VALUES(37,'c2e7d9811b37a0458124a2bffe6','N0008','2012-06-10 22:25:15.323051','1969-12-31 19:00:00',NULL,0,NULL,3,'She was courted by some of the finest young men, not only Boston''s Irish, but members of the English nobility as well.',0);
INSERT INTO "grampsdb_note" VALUES(38,'c2e7d98120319928652348bfd55','N0011','2012-06-10 22:25:15.332216','1969-12-31 19:00:00',NULL,0,NULL,3,'Joseph Patrick was well liked, quick to smile, and had a tremendous dose of Irish charm.',0);
INSERT INTO "grampsdb_note" VALUES(39,'c2e7d9818e9687a6690d12d5102','N0056','2012-06-10 22:25:15.339378','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0053:

Empty note ignored                 Line   544: 1 NOTE 
Empty note ignored                 Line   546: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(40,'c2e7d981b487143f65969df856f','N0067','2012-06-10 22:25:15.362607','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0011:

Line ignored as not understood     Line   715: 1 NAME Harrisburg Patriot News, January 25, 1995.
',0);
INSERT INTO "grampsdb_note" VALUES(41,'c2e7d98121e651fcc66a36c7eac','N0014','2012-06-10 22:25:15.371233','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0003:

Empty note ignored                 Line    82: 1 NOTE 
Empty note ignored                 Line    84: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(42,'c2e7d9818415869921ce53964d8','N0045','2012-06-10 22:25:15.409050','1969-12-31 19:00:00',NULL,0,NULL,3,'He was known as "Honey Fitz".',0);
INSERT INTO "grampsdb_note" VALUES(43,'c2e7d98181b5e340b797bb66b10','N0042','2012-06-10 22:25:15.412003','1969-12-31 19:00:00',NULL,0,NULL,3,'He was known as "Black Jack."',0);
INSERT INTO "grampsdb_note" VALUES(44,'c2e7d9816e81f3c1665f8818109','N0032','2012-06-10 22:25:15.418374','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0039:

Empty note ignored                 Line   359: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(45,'c2e7d98181e1f6c8392b19b48f9','N0043','2012-06-10 22:25:15.424726','1969-12-31 19:00:00',NULL,0,NULL,3,'He was known to drink alcohol excessively.',0);
INSERT INTO "grampsdb_note" VALUES(46,'c2e7d981aa614c3705f03cf00e','N0058','2012-06-10 22:25:15.428464','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0002:

Line ignored as not understood     Line   697: 1 NAME Rose, by Gail Cameron.
',0);
INSERT INTO "grampsdb_note" VALUES(47,'c2e7d98029e5777d56d7f5eac0c','N0000','2012-06-10 22:25:15.437050','1969-12-31 19:00:00',NULL,0,NULL,3,'From the time he was a school boy he was interested in making money.',0);
INSERT INTO "grampsdb_note" VALUES(48,'c2e7d9818d490cc09ea7f78684','N0055','2012-06-10 22:25:15.464516','1969-12-31 19:00:00',NULL,0,NULL,3,'She was said to be the only First Lady to resemble royalty. She shunned the media and never publicly discussed the assassination of JFK, how she felt about it, or the alleged affairs of her first husband.',0);
INSERT INTO "grampsdb_note" VALUES(49,'c2e7d9802fc6e2af2921c578d49','N0002','2012-06-10 22:25:15.467360','1969-12-31 19:00:00',NULL,0,NULL,3,'Joe was a poor student, but good at athletics and had an attractive personality. He was able to overcome many ethnic barriers during his school years at Boston Latin, a protestant and primarily Yankee school.',0);
INSERT INTO "grampsdb_note" VALUES(50,'c2e7d9813af6156bde2a80a5c56','N0023','2012-06-10 22:25:15.470149','1969-12-31 19:00:00',NULL,0,NULL,3,'She ran a summer home for retarded children.',0);
INSERT INTO "grampsdb_note" VALUES(51,'c2e7d9818805687906797423a9f','N0047','2012-06-10 22:25:15.475601','1969-12-31 19:00:00',NULL,0,NULL,3,'In 1960 he became President of the United States.',0);
INSERT INTO "grampsdb_note" VALUES(52,'c2e7d981ad51ba7e8c4708c3f7e','N0061','2012-06-10 22:25:15.479874','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0005:

Line ignored as not understood     Line   703: 1 NAME New York World Telegram and Sun, Oct 11, 1957, pg. 1.
',0);
INSERT INTO "grampsdb_note" VALUES(53,'c2e7d9818d147c3fbe39ef578c2','N0054','2012-06-10 22:25:15.508526','1969-12-31 19:00:00',NULL,0,NULL,3,'While dating JFK, Jackie did not want him to know that she was not rich and think that she was only marrying him for his money. So, she went to great lengths to appear rich.',0);
INSERT INTO "grampsdb_note" VALUES(54,'c2e7d981b4f62f77d122612b547','N0068','2012-06-10 22:25:15.524550','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   716: 0 C1 CSTA
Skipped subordinate line           Line   717: 1 NAME Twin
',0);
INSERT INTO "grampsdb_note" VALUES(55,'c2e7d981b5f7199bcd53f2ab08f','N0070','2012-06-10 22:25:15.530971','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   720: 0 C3 CSTA
Skipped subordinate line           Line   721: 1 NAME Illegitimate
',0);
INSERT INTO "grampsdb_note" VALUES(56,'c2e7d981b387f5f1bbff1ad45ab','N0066','2012-06-10 22:25:15.534055','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0010:

Line ignored as not understood     Line   713: 1 NAME CBS This Morning show.
',0);
INSERT INTO "grampsdb_note" VALUES(57,'c2e7d98124c346fe9febd7a80f1','N0016','2012-06-10 22:25:15.536959','1969-12-31 19:00:00',NULL,0,NULL,3,'In 1946 her father gave $600,000 for the construction of the Joseph P. Kennedy Jr. Convalescent Home for disadvantaged children, because of Rosemary''s condition.',0);
INSERT INTO "grampsdb_note" VALUES(58,'c2e7d9811b85bc82b85514f7706','N0009','2012-06-10 22:25:15.545099','1969-12-31 19:00:00',NULL,0,NULL,3,'She was very dedicated to her family, which was evident by the strong support she gave her sons in their political campaigns.',0);
INSERT INTO "grampsdb_note" VALUES(59,'c2e7d9818ce67b9d16993f502d','N0053','2012-06-10 22:25:15.552791','1969-12-31 19:00:00',NULL,0,NULL,3,'Before marrying JFK, Jackie worked as a photo journalist in Washington DC.',0);
INSERT INTO "grampsdb_note" VALUES(60,'c2e7d98189f70f172e912ff3957','N0051','2012-06-10 22:25:15.557431','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0052:

Empty note ignored                 Line   518: 1 NOTE 
Empty note ignored                 Line   520: 1 NOTE 
Empty note ignored                 Line   522: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(61,'c2e7d981b68425932471c84c258','N0071','2012-06-10 22:25:15.567707','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into Top Level:

Line ignored as not understood     Line   722: 0 C4 CSTA
Skipped subordinate line           Line   723: 1 NAME Duplicate
',0);
INSERT INTO "grampsdb_note" VALUES(62,'c2e7d9818cc498db8ee3dea4138','N0052','2012-06-10 22:25:15.573371','1969-12-31 19:00:00',NULL,0,NULL,3,'<img src="http://www.jacqueslowe.com/html/photographs/jackie/images/Jacky01bw.jpg" border=1>',0);
INSERT INTO "grampsdb_note" VALUES(63,'c2e7d980468170d31685e92235c','N0005','2012-06-10 22:25:15.575432','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0001:

Empty note ignored                 Line    26: 1 NOTE 
Empty note ignored                 Line    28: 1 NOTE 
Empty note ignored                 Line    30: 1 NOTE 
Empty note ignored                 Line    32: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(64,'c2e7d9817594a0d00a51f363437','N0035','2012-06-10 22:25:15.579794','1969-12-31 19:00:00',NULL,0,NULL,3,'Patrick later became a very successful businessman getting into wholesale liquor sales, owning a coal company and becoming the president of a bank.',0);
INSERT INTO "grampsdb_note" VALUES(65,'c2e7d98120727d077fef968bbd9','N0012','2012-06-10 22:25:15.583359','1969-12-31 19:00:00',NULL,0,NULL,3,'He enlisted in the Navy during World War II, and died during a naval flight.',0);
INSERT INTO "grampsdb_note" VALUES(66,'c2e7d98036c6ae8226513082ccf','N0003','2012-06-10 22:25:15.592987','1969-12-31 19:00:00',NULL,0,NULL,3,'Was one of the youngest Bank Presidents in US history. ',0);
INSERT INTO "grampsdb_note" VALUES(67,'c2e7d98175c2d61569f78381d82','N0036','2012-06-10 22:25:15.611030','1969-12-31 19:00:00',NULL,0,NULL,3,'His personality was mild-mannered, quiet and reserved, and he was viewed as a man of moderate habits.',0);
INSERT INTO "grampsdb_note" VALUES(68,'c2e7d9813937f3aa990fe421c3b','N0022','2012-06-10 22:25:15.615958','1969-12-31 19:00:00',NULL,0,NULL,3,'She helped in the many political campaigns of her brother, John Fitzgerald.',0);
INSERT INTO "grampsdb_note" VALUES(69,'c2e7d9813c8242eeee978eadc2c','N0025','2012-06-10 22:25:15.620937','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0008:

Empty note ignored                 Line   146: 1 NOTE 
Empty note ignored                 Line   148: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(70,'c2e7d9816d241b53f482b98497b','N0030','2012-06-10 22:25:15.623957','1969-12-31 19:00:00',NULL,0,NULL,3,'Enlisted in the Navy during World War II.',0);
INSERT INTO "grampsdb_note" VALUES(71,'c2e7d981b191a44abef9463baad','N0064','2012-06-10 22:25:15.630233','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0008:

Line ignored as not understood     Line   709: 1 NAME New York Times, Nov. 22, 1963.
',0);
INSERT INTO "grampsdb_note" VALUES(72,'c2e7d9813b22ce4d81879099d8e','N0024','2012-06-10 22:25:15.655227','1969-12-31 19:00:00',NULL,0,NULL,3,'After her mother, Eunice was considered the family''s model woman.',0);
INSERT INTO "grampsdb_note" VALUES(73,'c2e7d9813067e03c20efb9e575c','N0020','2012-06-10 22:25:15.658798','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into INDI (individual) Gramps ID I0006:

Empty note ignored                 Line   122: 1 NOTE 
',0);
INSERT INTO "grampsdb_note" VALUES(74,'c2e7d981b0262dd756d26ae93c4','N0063','2012-06-10 22:25:15.668950','1969-12-31 19:00:00',NULL,0,NULL,27,'Records not imported into SOUR (source) Gramps ID S0007:

Line ignored as not understood     Line   707: 1 NAME Growing Up Kennedy, Harrison Raine and John Quinn.
',0);
INSERT INTO "grampsdb_note" VALUES(75,'c2e7d9811a83528a052fc9ccffb','N0006','2012-06-10 22:25:15.686765','1969-12-31 19:00:00',NULL,0,NULL,3,'She was considered the flower of Boston Irish society.',0);
INSERT INTO "grampsdb_note" VALUES(76,'c2ea2e7680b58d99355e521b943','N0075','2012-06-11 16:08:37.769654','2012-06-11 16:08:36.006871','admin',0,'KFMnYzJlYTJlNzY4MGI1OGQ5OTM1NWU1MjFiOTQzJwpWTjAwNzUKcDEKKGxwMgpWIkJyaWRnZXBv
cnQgTG9kZ2UsIE5vLiAxNjIsIEYuIGFuZCBBLiBNLiwgd2FzIGNoYXJ0ZXJlZCBNYXkgMjQsIDE4
NTQsIEpvc2VwaCBILiBCYWxsYXJkLCBXLiBNLjsgTm9haCBSZWFnYW4sIFMuIFcuOyBTYW11ZWwg
Ry4gT3dlbiwgSi4gVy4gVGhlIHByZXNlbnQgb2ZmaWNlcnMgb2YgdGhlIGxvZGdlIGFyZSBIdW1w
aHJleSBGb3JzaGEsIFcuIE0uOyBQZXRlciBQLiBCbGFuaywgUy4gVy47IFdvb2Rmb3JkIFRob21w
c29uLCBKLiBXLjsgRGFuaWVsIEJyb2Fkd2F5LCBUcmVhcy47IFIuIFcuIFRob21wc29uLCBTZWMu
IFRoZSBsb2RnZSBoYXMgbm93IHRoaXJ0eS1maXZlIG1lbWJlcnMuIlx1MDAwYVx1MDAwYUZyb206
XHUwMDBhXHUwMDBhaHR0cHM6Ly9zaXRlcy5nb29nbGUuY29tL3NpdGUvbWFyaW9uY291bnR5aW5n
ZW53ZWIvaG9tZS90b3duc2hpcC1oaXN0b3JpZXMvd2F5bmUtdG93bnNoaXBcdTAwMGFcdTAwMGFc
dTAwMGFcdTAwMGFTLlcuIHdhcyBwcm9iYWJseSAiU2VuaW9yIFdhcmRlbiIuXHUwMDBhXHUwMDBh
IlRoZSBTZW5pb3IgV2FyZGVuIChzb21ldGltZXMga25vd24gYXMgRmlyc3QgV2FyZGVuKSBpcyB0
aGUgc2Vjb25kIG9mIHRoZSB0aHJlZSBwcmluY2lwYWwgb2ZmaWNlcnMgb2YgYSBsb2RnZSwgYW5k
IGlzIHRoZSBNYXN0ZXIncyBwcmluY2lwYWwgZGVwdXR5LiBVbmRlciBzb21lIGNvbnN0aXR1dGlv
bnMsIGlmIHRoZSBXb3JzaGlwZnVsIE1hc3RlciBpcyBhYnNlbnQgdGhlbiB0aGUgU2VuaW9yIFdh
cmRlbiBwcmVzaWRlcyBhdCBtZWV0aW5ncyBhcyAiYWN0aW5nIE1hc3RlciIsIGFuZCBtYXkgYWN0
IGZvciB0aGUgTWFzdGVyIGluIGFsbCBtYXR0ZXJzIG9mIGxvZGdlIGJ1c2luZXNzLiBVbmRlciBv
dGhlciBjb25zdGl0dXRpb25zLCBpbmNsdWRpbmcgR3JhbmQgTG9kZ2Ugb2YgRW5nbGFuZCBhbmQg
R3JhbmQgTG9kZ2Ugb2YgSXJlbGFuZCwgb25seSBzaXR0aW5nIE1hc3RlcnMgb3IgUGFzdCBNYXN0
ZXJzIG1heSBwcmVzaWRlIGFzICJhY3RpbmcgTWFzdGVyIiwgYW5kIHNvIHRoZSBTZW5pb3IgV2Fy
ZGVuIGNhbm5vdCBmdWxmaWxsIHRoaXMgcm9sZSB1bmxlc3MgaGUgaXMgYWxzbyBhIFBhc3QgTWFz
dGVyLiBJbiBtYW55IGxvZGdlcyBpdCBpcyBwcmVzdW1lZCB0aGF0IHRoZSBTZW5pb3IgV2FyZGVu
IHdpbGwgYmVjb21lIHRoZSBuZXh0IFdvcnNoaXBmdWwgTWFzdGVyLiJcdTAwMGFcdTAwMGFodHRw
Oi8vZW4ud2lraXBlZGlhLm9yZy93aWtpL01hc29uaWNfTG9kZ2VfT2ZmaWNlcnNcdTAwMGFcdTAw
MGFGLiBhbmQgQS5NLiBiZWluZyBGcmVlIGFuZCBBY2NlcHRlZCBNYXNvbnNcdTAwMGFcdTAwMGFc
dTAwMGFcdTAwMGEKcDMKYShscDQKKChJMwpWZm9udGZhY2UKdFYKKGxwNQooSTQ3MgpJMTE0MAp0
cDYKYXRwNwphKChJMQpWaXRhbGljCnROKGxwOAooSTEyMTMKSTEyMzcKdHA5CmF0cDEwCmEoKEk4
ClZsaW5rCnRWaHR0cDovL2VuLndpa2lwZWRpYS5vcmcvd2lraS9NYXNvbmljX0xvZGdlX09mZmlj
ZXJzCihscDExCihJMTE0MgpJMTE5Mwp0cDEyCmF0cDEzCmEoKEk4ClZsaW5rCnRWaHR0cHM6Ly9z
aXRlcy5nb29nbGUuY29tL3NpdGUvbWFyaW9uY291bnR5aW5nZW53ZWIvaG9tZS90b3duc2hpcC1o
aXN0b3JpZXMvd2F5bmUtdG93bnNoaXAKKGxwMTQKKEkzNDMKSTQzMgp0cDE1CmF0cDE2CmFhSTAw
CihJMQpWR2VuZXJhbApwMTcKdEkxMzM5NDQ1MzE2Cih0STAwCnRwMTgKLg==
',3,'"Bridgeport Lodge, No. 162, F. and A. M., was chartered May 24, 1854, Joseph H. Ballard, W. M.; Noah Reagan, S. W.; Samuel G. Owen, J. W. The present officers of the lodge are Humphrey Forsha, W. M.; Peter P. Blank, S. W.; Woodford Thompson, J. W.; Daniel Broadway, Treas.; R. W. Thompson, Sec. The lodge has now thirty-five members."

From:

https://sites.google.com/site/marioncountyingenweb/home/township-histories/wayne-township



S.W. was probably "Senior Warden".

"The Senior Warden (sometimes known as First Warden) is the second of the three principal officers of a lodge, and is the Master''s principal deputy. Under some constitutions, if the Worshipful Master is absent then the Senior Warden presides at meetings as "acting Master", and may act for the Master in all matters of lodge business. Under other constitutions, including Grand Lodge of England and Grand Lodge of Ireland, only sitting Masters or Past Masters may preside as "acting Master", and so the Senior Warden cannot fulfill this role unless he is also a Past Master. In many lodges it is presumed that the Senior Warden will become the next Worshipful Master."

http://en.wikipedia.org/wiki/Masonic_Lodge_Officers

F. and A.M. being Free and Accepted Masons



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
INSERT INTO "grampsdb_surname" VALUES(1,1,'BOUVIER','',1,'',1,1);
INSERT INTO "grampsdb_surname" VALUES(2,1,'KENNEDY','',1,'',2,1);
INSERT INTO "grampsdb_surname" VALUES(3,1,'CAULFIELD','',1,'',3,1);
INSERT INTO "grampsdb_surname" VALUES(4,1,'BENNETT','',1,'',4,1);
INSERT INTO "grampsdb_surname" VALUES(5,1,'BOUVIER','',1,'',5,1);
INSERT INTO "grampsdb_surname" VALUES(6,1,'KENNEDY','',1,'',6,1);
INSERT INTO "grampsdb_surname" VALUES(7,1,'KENNEDY','',1,'',7,1);
INSERT INTO "grampsdb_surname" VALUES(8,1,'SHRIVER','',1,'',8,1);
INSERT INTO "grampsdb_surname" VALUES(9,1,'KENNEDY','',1,'',9,1);
INSERT INTO "grampsdb_surname" VALUES(10,1,'SMITH','',1,'',10,1);
INSERT INTO "grampsdb_surname" VALUES(11,1,'SCHWARZENEGGER','',1,'',11,1);
INSERT INTO "grampsdb_surname" VALUES(12,1,'SHRIVER','',1,'',12,1);
INSERT INTO "grampsdb_surname" VALUES(13,1,'KENNEDY','',1,'',13,1);
INSERT INTO "grampsdb_surname" VALUES(14,1,'CAVENDISH','',1,'',14,1);
INSERT INTO "grampsdb_surname" VALUES(15,1,'LAWFORD','',1,'',15,1);
INSERT INTO "grampsdb_surname" VALUES(16,1,'SKAKEL','',1,'',16,1);
INSERT INTO "grampsdb_surname" VALUES(17,1,'SMITH','',1,'',17,1);
INSERT INTO "grampsdb_surname" VALUES(18,1,'KENNEDY','',1,'',18,1);
INSERT INTO "grampsdb_surname" VALUES(19,1,'KENNEDY','',1,'',19,1);
INSERT INTO "grampsdb_surname" VALUES(20,1,'MAHONEY','',1,'',20,1);
INSERT INTO "grampsdb_surname" VALUES(21,1,'KENNEDY','',1,'',21,1);
INSERT INTO "grampsdb_surname" VALUES(22,1,'KENNEDY','',1,'',22,1);
INSERT INTO "grampsdb_surname" VALUES(23,1,'KENNEDY','',1,'',23,1);
INSERT INTO "grampsdb_surname" VALUES(24,1,'KENNEDY','',1,'',24,1);
INSERT INTO "grampsdb_surname" VALUES(25,1,'LEE','',1,'',25,1);
INSERT INTO "grampsdb_surname" VALUES(26,1,'KENNEDY','',1,'',26,1);
INSERT INTO "grampsdb_surname" VALUES(27,1,'KENNEDY','',1,'',27,1);
INSERT INTO "grampsdb_surname" VALUES(28,1,'FITZGERALD','',1,'',28,1);
INSERT INTO "grampsdb_surname" VALUES(29,1,'ACHINCLOSS','',1,'',29,1);
INSERT INTO "grampsdb_surname" VALUES(30,1,'KENNEDY','',1,'',30,1);
INSERT INTO "grampsdb_surname" VALUES(31,1,'KANE','',1,'',31,1);
INSERT INTO "grampsdb_surname" VALUES(32,1,'KENNEDY','',1,'',32,1);
INSERT INTO "grampsdb_surname" VALUES(33,1,'FITZGERALD','',1,'',33,1);
INSERT INTO "grampsdb_surname" VALUES(34,1,'MURPHY','',1,'',34,1);
INSERT INTO "grampsdb_surname" VALUES(35,1,'KENNEDY','',1,'',35,1);
INSERT INTO "grampsdb_surname" VALUES(36,1,'LAWFORD','',1,'',36,1);
INSERT INTO "grampsdb_surname" VALUES(37,1,'KENNEDY','',1,'',37,1);
INSERT INTO "grampsdb_surname" VALUES(38,1,'SHRIVER','',1,'',38,1);
INSERT INTO "grampsdb_surname" VALUES(39,1,'KENNEDY','',1,'',39,1);
INSERT INTO "grampsdb_surname" VALUES(40,1,'BURKE','',1,'',40,1);
INSERT INTO "grampsdb_surname" VALUES(41,1,'SMITH','',1,'',41,1);
INSERT INTO "grampsdb_surname" VALUES(42,1,'KENNEDY','',1,'',42,1);
INSERT INTO "grampsdb_surname" VALUES(43,1,'HICKEY','',1,'',43,1);
INSERT INTO "grampsdb_surname" VALUES(44,1,'LAWFORD','',1,'',44,1);
INSERT INTO "grampsdb_surname" VALUES(45,1,'KENNEDY','',1,'',45,1);
INSERT INTO "grampsdb_surname" VALUES(46,1,'SMITH','',1,'',46,1);
INSERT INTO "grampsdb_surname" VALUES(47,1,'KENNEDY','',1,'',47,1);
INSERT INTO "grampsdb_surname" VALUES(48,1,'KENNEDY','',1,'',48,1);
INSERT INTO "grampsdb_surname" VALUES(49,1,'HANNON','',1,'',49,1);
INSERT INTO "grampsdb_surname" VALUES(50,1,'KENNEDY','',1,'',50,1);
INSERT INTO "grampsdb_surname" VALUES(51,1,'KENNEDY','',1,'',51,1);
INSERT INTO "grampsdb_surname" VALUES(52,1,'KENNEDY','',1,'',52,1);
INSERT INTO "grampsdb_surname" VALUES(53,1,'SHRIVER','',1,'',53,1);
INSERT INTO "grampsdb_surname" VALUES(54,1,'KENNEDY','',1,'',54,1);
INSERT INTO "grampsdb_surname" VALUES(55,1,'KENNEDY','',1,'',55,1);
INSERT INTO "grampsdb_surname" VALUES(56,1,'KENNEDY','',1,'',56,1);
INSERT INTO "grampsdb_surname" VALUES(57,1,'LAWFORD','',1,'',57,1);
INSERT INTO "grampsdb_surname" VALUES(58,1,'SHRIVER','',1,'',58,1);
INSERT INTO "grampsdb_surname" VALUES(59,1,'KENNEDY','',1,'',59,1);
INSERT INTO "grampsdb_surname" VALUES(60,1,'KENNEDY','',1,'',60,1);
INSERT INTO "grampsdb_surname" VALUES(61,1,'KENNEDY','',1,'',61,1);
INSERT INTO "grampsdb_surname" VALUES(62,1,'KENNEDY','',1,'',62,1);
INSERT INTO "grampsdb_surname" VALUES(63,1,'ONASSIS','',1,'',63,1);
INSERT INTO "grampsdb_surname" VALUES(64,1,'KENNEDY','',1,'',64,1);
INSERT INTO "grampsdb_surname" VALUES(65,1,'SHRIVER','',1,'',65,1);
INSERT INTO "grampsdb_surname" VALUES(66,1,'LAWFORD','',1,'',66,1);
INSERT INTO "grampsdb_surname" VALUES(67,1,'KENNEDY','',1,'',67,1);
INSERT INTO "grampsdb_surname" VALUES(68,1,'KENNEDY','',1,'',68,1);
INSERT INTO "grampsdb_surname" VALUES(69,1,'BOUVIER','',1,'',69,1);
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
INSERT INTO "grampsdb_name" VALUES(1,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:15.706415',NULL,NULL,1,4,1,'John Vernou','','','','','','',1,1,1);
INSERT INTO "grampsdb_name" VALUES(2,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:15.768043',NULL,NULL,1,4,1,'Douglas Harriman','','','','','','',1,1,2);
INSERT INTO "grampsdb_name" VALUES(3,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:15.791663',NULL,NULL,1,4,1,'John T.','','','','','','',1,1,3);
INSERT INTO "grampsdb_name" VALUES(4,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:15.814243',NULL,NULL,1,4,1,'Virginia Joan','','','','','','',1,1,4);
INSERT INTO "grampsdb_name" VALUES(5,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:15.854161',NULL,NULL,1,4,1,'Lee','','','','','','',1,1,5);
INSERT INTO "grampsdb_name" VALUES(6,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:15.868407',NULL,NULL,1,4,1,'Margaret','','','','','','',1,1,6);
INSERT INTO "grampsdb_name" VALUES(7,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:15.894945',NULL,NULL,1,4,1,'Patrick','','','','','','',1,1,7);
INSERT INTO "grampsdb_name" VALUES(8,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:15.973452',NULL,NULL,1,4,1,'Anthony Paul','','','','','','',1,1,8);
INSERT INTO "grampsdb_name" VALUES(9,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.010894',NULL,NULL,1,4,1,'Michael L.','','','','','','',1,1,9);
INSERT INTO "grampsdb_name" VALUES(10,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.042774',NULL,NULL,1,4,1,'Stephen','','','','','','',1,1,10);
INSERT INTO "grampsdb_name" VALUES(11,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.059691',NULL,NULL,1,4,1,'Arnold','','','','','','',1,1,11);
INSERT INTO "grampsdb_name" VALUES(12,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.090555',NULL,NULL,1,4,1,'Robert Sargent','','','','','','',1,1,12);
INSERT INTO "grampsdb_name" VALUES(13,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.134784',NULL,NULL,1,4,1,'Christopher George','','','','','','',1,1,13);
INSERT INTO "grampsdb_name" VALUES(14,0,0,0,0,0,0,0,NULL,NULL,NULL,NULL,'',0,0,0,'2012-06-11 16:36:17.222852','2012-06-11 16:36:17.220356','admin',1,4,1,'William John Robert','','','','','','',1,1,14);
INSERT INTO "grampsdb_name" VALUES(15,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.190702',NULL,NULL,1,4,1,'Christopher','','','','','','',1,1,15);
INSERT INTO "grampsdb_name" VALUES(16,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.214403',NULL,NULL,1,4,1,'Ethel','','','','','','',1,1,16);
INSERT INTO "grampsdb_name" VALUES(17,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.237610',NULL,NULL,1,4,1,'William Kennedy','','','','','','',1,1,17);
INSERT INTO "grampsdb_name" VALUES(18,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.263117',NULL,NULL,1,4,1,'Johanna','','','','','','',1,1,18);
INSERT INTO "grampsdb_name" VALUES(19,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.289812',NULL,NULL,1,4,1,'Mary','','','','','','',1,1,19);
INSERT INTO "grampsdb_name" VALUES(20,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.320848',NULL,NULL,1,4,1,'Humphrey','','','','','','',1,1,20);
INSERT INTO "grampsdb_name" VALUES(21,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.341306',NULL,NULL,1,4,1,'Robert Francis','','','','','','',1,1,21);
INSERT INTO "grampsdb_name" VALUES(22,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.409696',NULL,NULL,1,4,1,'Robert Francis','','','','','','',1,1,22);
INSERT INTO "grampsdb_name" VALUES(23,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.447369',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,23);
INSERT INTO "grampsdb_name" VALUES(24,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.580991',NULL,NULL,1,4,1,'David Anthony','','','','','','',1,1,24);
INSERT INTO "grampsdb_name" VALUES(25,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.658227',NULL,NULL,1,4,1,'Janet','','','','','','',1,1,25);
INSERT INTO "grampsdb_name" VALUES(26,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.703581',NULL,NULL,1,4,1,'Kathleen Hartington','','','','','','',1,1,26);
INSERT INTO "grampsdb_name" VALUES(27,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.754974',NULL,NULL,1,4,1,'Edward Moore','','','','','','',1,1,27);
INSERT INTO "grampsdb_name" VALUES(28,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.810884',NULL,NULL,1,4,1,'John F.','','','','','','',1,1,28);
INSERT INTO "grampsdb_name" VALUES(29,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.834303',NULL,NULL,1,4,1,'Hugh','','','','','','',1,1,29);
INSERT INTO "grampsdb_name" VALUES(30,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.857778',NULL,NULL,1,4,1,'Mary Kerry','','','','','','',1,1,30);
INSERT INTO "grampsdb_name" VALUES(31,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.882283',NULL,NULL,1,4,1,'Laurence','','','','','','',1,1,31);
INSERT INTO "grampsdb_name" VALUES(32,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:16.948261',NULL,NULL,1,4,1,'Patrick Joseph','','','','','','',1,1,32);
INSERT INTO "grampsdb_name" VALUES(33,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.001740',NULL,NULL,1,4,1,'Rose','','','','','','',1,1,33);
INSERT INTO "grampsdb_name" VALUES(34,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.073183',NULL,NULL,1,4,1,'Bridget','','','','','','',1,1,34);
INSERT INTO "grampsdb_name" VALUES(35,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.205911',NULL,NULL,1,4,1,'Rosemary','','','','','','',1,1,35);
INSERT INTO "grampsdb_name" VALUES(36,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.242658',NULL,NULL,1,4,1,'Robin','','','','','','',1,1,36);
INSERT INTO "grampsdb_name" VALUES(37,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.259040',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,37);
INSERT INTO "grampsdb_name" VALUES(38,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.282391',NULL,NULL,1,4,1,'Mark Kennedy','','','','','','',1,1,38);
INSERT INTO "grampsdb_name" VALUES(39,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.306163',NULL,NULL,1,4,1,'Matthew Maxwell Taylor','','','','','','',1,1,39);
INSERT INTO "grampsdb_name" VALUES(40,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.331975',NULL,NULL,1,4,1,'Charles','','','','','','',1,1,40);
INSERT INTO "grampsdb_name" VALUES(41,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.354257',NULL,NULL,1,4,1,'Amanda','','','','','','',1,1,41);
INSERT INTO "grampsdb_name" VALUES(42,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.397072',NULL,NULL,1,4,1,'Jean Ann','','','','','','',1,1,42);
INSERT INTO "grampsdb_name" VALUES(43,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.429764',NULL,NULL,1,4,1,'Mary Augusta','','','','','','',1,1,43);
INSERT INTO "grampsdb_name" VALUES(44,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.459013',NULL,NULL,1,4,1,'Victoria','','','','','','',1,1,44);
INSERT INTO "grampsdb_name" VALUES(45,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.473221',NULL,NULL,1,4,1,'Edward More','','','','','','',1,1,45);
INSERT INTO "grampsdb_name" VALUES(46,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.509848',NULL,NULL,1,4,1,'Stephen Edward','','','','','','',1,1,46);
INSERT INTO "grampsdb_name" VALUES(47,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.535139',NULL,NULL,1,4,1,'Rory Elizabeth','','','','','','',1,1,47);
INSERT INTO "grampsdb_name" VALUES(48,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.571996',NULL,NULL,1,4,1,'Patrick Joseph','','','','','','',1,1,48);
INSERT INTO "grampsdb_name" VALUES(49,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.674620',NULL,NULL,1,4,1,'Josephine Mary','','','','','','',1,1,49);
INSERT INTO "grampsdb_name" VALUES(50,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.688988',NULL,NULL,1,4,1,'Margaret','','','','','','',1,1,50);
INSERT INTO "grampsdb_name" VALUES(51,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.724747',NULL,NULL,1,4,1,'John Fitzgerald','','','','','','',1,1,51);
INSERT INTO "grampsdb_name" VALUES(52,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.825063',NULL,NULL,1,4,1,'Loretta','','','','','','',1,1,52);
INSERT INTO "grampsdb_name" VALUES(53,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.879357',NULL,NULL,1,4,1,'Robert Sargent','','','','','','',1,1,53);
INSERT INTO "grampsdb_name" VALUES(54,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.946749',NULL,NULL,1,4,1,'Mary Courtney','','','','','','',1,1,54);
INSERT INTO "grampsdb_name" VALUES(55,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:17.978712',NULL,NULL,1,4,1,'Kara Ann','','','','','','',1,1,55);
INSERT INTO "grampsdb_name" VALUES(56,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.021259',NULL,NULL,1,4,1,'Eunice Mary','','','','','','',1,1,56);
INSERT INTO "grampsdb_name" VALUES(57,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.086384',NULL,NULL,1,4,1,'Peter','','','','','','',1,1,57);
INSERT INTO "grampsdb_name" VALUES(58,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.119533',NULL,NULL,1,4,1,'Maria','','','','','','',1,1,58);
INSERT INTO "grampsdb_name" VALUES(59,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.193174',NULL,NULL,1,4,1,'John Fitzgerald','','','','','','',1,1,59);
INSERT INTO "grampsdb_name" VALUES(60,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.245209',NULL,NULL,1,4,1,'John','','','','','','',1,1,60);
INSERT INTO "grampsdb_name" VALUES(61,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.278605',NULL,NULL,1,4,1,'Caroline Bouvier','','','','','','',1,1,61);
INSERT INTO "grampsdb_name" VALUES(62,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.334116',NULL,NULL,1,4,1,'Patrick Bouvier','','','','','','',1,1,62);
INSERT INTO "grampsdb_name" VALUES(63,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.390866',NULL,NULL,1,4,1,'Aristotle','','','','','','',1,1,63);
INSERT INTO "grampsdb_name" VALUES(64,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.418868',NULL,NULL,1,4,1,'Patricia','','','','','','',1,1,64);
INSERT INTO "grampsdb_name" VALUES(65,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.452264',NULL,NULL,1,4,1,'Timothy','','','','','','',1,1,65);
INSERT INTO "grampsdb_name" VALUES(66,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.466609',NULL,NULL,1,4,1,'Sydney','','','','','','',1,1,66);
INSERT INTO "grampsdb_name" VALUES(67,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.482156',NULL,NULL,1,4,1,'Kathleen','','','','','','',1,1,67);
INSERT INTO "grampsdb_name" VALUES(68,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0,'2012-06-10 22:25:18.526609',NULL,NULL,1,4,1,'Joseph Patrick','','','','','','',1,1,68);
INSERT INTO "grampsdb_name" VALUES(69,0,0,0,0,0,0,0,NULL,NULL,NULL,NULL,'',0,0,0,'2012-06-11 16:33:07.312620','2012-06-11 16:33:07.310642','admin',1,4,1,'Jacqueline','','','','','','',1,1,69);
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
INSERT INTO "grampsdb_markup" VALUES(1,2,4,1,'Monospace','[(0, 143)]');
INSERT INTO "grampsdb_markup" VALUES(2,3,4,1,'Monospace','[(0, 152)]');
INSERT INTO "grampsdb_markup" VALUES(3,7,4,1,'Monospace','[(0, 162)]');
INSERT INTO "grampsdb_markup" VALUES(4,9,4,1,'Monospace','[(0, 170)]');
INSERT INTO "grampsdb_markup" VALUES(5,11,4,1,'Monospace','[(0, 150)]');
INSERT INTO "grampsdb_markup" VALUES(6,16,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(7,18,4,1,'Monospace','[(0, 159)]');
INSERT INTO "grampsdb_markup" VALUES(8,21,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(9,27,4,1,'Monospace','[(0, 157)]');
INSERT INTO "grampsdb_markup" VALUES(10,28,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(11,29,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(12,30,4,1,'Monospace','[(0, 156)]');
INSERT INTO "grampsdb_markup" VALUES(13,31,4,1,'Monospace','[(0, 175)]');
INSERT INTO "grampsdb_markup" VALUES(14,33,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(15,35,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(16,39,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(17,40,4,1,'Monospace','[(0, 155)]');
INSERT INTO "grampsdb_markup" VALUES(18,41,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(19,44,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(20,46,4,1,'Monospace','[(0, 135)]');
INSERT INTO "grampsdb_markup" VALUES(21,52,4,1,'Monospace','[(0, 166)]');
INSERT INTO "grampsdb_markup" VALUES(22,54,4,1,'Monospace','[(0, 154)]');
INSERT INTO "grampsdb_markup" VALUES(23,55,4,1,'Monospace','[(0, 162)]');
INSERT INTO "grampsdb_markup" VALUES(24,56,4,1,'Monospace','[(0, 135)]');
INSERT INTO "grampsdb_markup" VALUES(25,60,4,1,'Monospace','[(0, 227)]');
INSERT INTO "grampsdb_markup" VALUES(26,61,4,1,'Monospace','[(0, 159)]');
INSERT INTO "grampsdb_markup" VALUES(27,63,4,1,'Monospace','[(0, 282)]');
INSERT INTO "grampsdb_markup" VALUES(28,69,4,1,'Monospace','[(0, 172)]');
INSERT INTO "grampsdb_markup" VALUES(29,71,4,1,'Monospace','[(0, 143)]');
INSERT INTO "grampsdb_markup" VALUES(30,73,4,1,'Monospace','[(0, 117)]');
INSERT INTO "grampsdb_markup" VALUES(31,74,4,1,'Monospace','[(0, 163)]');
INSERT INTO "grampsdb_markup" VALUES(32,76,4,1,'','[(472, 1140)]');
INSERT INTO "grampsdb_markup" VALUES(33,76,2,1,NULL,'[(1213, 1237)]');
INSERT INTO "grampsdb_markup" VALUES(34,76,9,1,'http://en.wikipedia.org/wiki/Masonic_Lodge_Officers','[(1142, 1193)]');
INSERT INTO "grampsdb_markup" VALUES(35,76,9,1,'https://sites.google.com/site/marioncountyingenweb/home/township-histories/wayne-township','[(343, 432)]');
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
INSERT INTO "grampsdb_noteref" VALUES(1,32,1,1,'2012-06-10 22:25:15.731661',NULL,NULL,0,43);
INSERT INTO "grampsdb_noteref" VALUES(2,32,1,1,'2012-06-10 22:25:15.733930',NULL,NULL,0,45);
INSERT INTO "grampsdb_noteref" VALUES(3,32,1,1,'2012-06-10 22:25:15.736070',NULL,NULL,0,29);
INSERT INTO "grampsdb_noteref" VALUES(4,32,7,1,'2012-06-10 22:25:15.921748',NULL,NULL,0,1);
INSERT INTO "grampsdb_noteref" VALUES(5,32,7,1,'2012-06-10 22:25:15.923953',NULL,NULL,0,22);
INSERT INTO "grampsdb_noteref" VALUES(6,32,7,1,'2012-06-10 22:25:15.926082',NULL,NULL,0,28);
INSERT INTO "grampsdb_noteref" VALUES(7,35,1,1,'2012-06-10 22:25:15.963920',NULL,NULL,0,52);
INSERT INTO "grampsdb_noteref" VALUES(8,35,2,1,'2012-06-10 22:25:16.005826',NULL,NULL,0,71);
INSERT INTO "grampsdb_noteref" VALUES(9,32,12,1,'2012-06-10 22:25:16.103603',NULL,NULL,0,20);
INSERT INTO "grampsdb_noteref" VALUES(10,32,21,1,'2012-06-10 22:25:16.366491',NULL,NULL,0,12);
INSERT INTO "grampsdb_noteref" VALUES(11,32,21,1,'2012-06-10 22:25:16.368605',NULL,NULL,0,17);
INSERT INTO "grampsdb_noteref" VALUES(12,32,21,1,'2012-06-10 22:25:16.370717',NULL,NULL,0,33);
INSERT INTO "grampsdb_noteref" VALUES(13,32,23,1,'2012-06-10 22:25:16.489313',NULL,NULL,0,47);
INSERT INTO "grampsdb_noteref" VALUES(14,32,23,1,'2012-06-10 22:25:16.491450',NULL,NULL,0,25);
INSERT INTO "grampsdb_noteref" VALUES(15,32,23,1,'2012-06-10 22:25:16.493602',NULL,NULL,0,49);
INSERT INTO "grampsdb_noteref" VALUES(16,32,23,1,'2012-06-10 22:25:16.495713',NULL,NULL,0,66);
INSERT INTO "grampsdb_noteref" VALUES(17,32,23,1,'2012-06-10 22:25:16.497822',NULL,NULL,0,13);
INSERT INTO "grampsdb_noteref" VALUES(18,32,23,1,'2012-06-10 22:25:16.499952',NULL,NULL,0,63);
INSERT INTO "grampsdb_noteref" VALUES(19,35,3,1,'2012-06-10 22:25:16.566132',NULL,NULL,0,31);
INSERT INTO "grampsdb_noteref" VALUES(20,35,4,1,'2012-06-10 22:25:16.695037',NULL,NULL,0,74);
INSERT INTO "grampsdb_noteref" VALUES(21,32,27,1,'2012-06-10 22:25:16.779231',NULL,NULL,0,70);
INSERT INTO "grampsdb_noteref" VALUES(22,32,27,1,'2012-06-10 22:25:16.782477',NULL,NULL,0,10);
INSERT INTO "grampsdb_noteref" VALUES(23,32,27,1,'2012-06-10 22:25:16.784618',NULL,NULL,0,44);
INSERT INTO "grampsdb_noteref" VALUES(24,32,28,1,'2012-06-10 22:25:16.821076',NULL,NULL,0,42);
INSERT INTO "grampsdb_noteref" VALUES(25,35,5,1,'2012-06-10 22:25:16.850061',NULL,NULL,0,56);
INSERT INTO "grampsdb_noteref" VALUES(26,35,6,1,'2012-06-10 22:25:16.903843',NULL,NULL,0,46);
INSERT INTO "grampsdb_noteref" VALUES(27,32,33,1,'2012-06-10 22:25:17.030148',NULL,NULL,0,75);
INSERT INTO "grampsdb_noteref" VALUES(28,32,33,1,'2012-06-10 22:25:17.032269',NULL,NULL,0,19);
INSERT INTO "grampsdb_noteref" VALUES(29,32,33,1,'2012-06-10 22:25:17.034424',NULL,NULL,0,37);
INSERT INTO "grampsdb_noteref" VALUES(30,32,33,1,'2012-06-10 22:25:17.036551',NULL,NULL,0,58);
INSERT INTO "grampsdb_noteref" VALUES(31,32,33,1,'2012-06-10 22:25:17.038700',NULL,NULL,0,21);
INSERT INTO "grampsdb_noteref" VALUES(32,32,34,1,'2012-06-10 22:25:17.094787',NULL,NULL,0,15);
INSERT INTO "grampsdb_noteref" VALUES(33,35,7,1,'2012-06-10 22:25:17.186475',NULL,NULL,0,9);
INSERT INTO "grampsdb_noteref" VALUES(34,32,35,1,'2012-06-10 22:25:17.218894',NULL,NULL,0,6);
INSERT INTO "grampsdb_noteref" VALUES(35,32,35,1,'2012-06-10 22:25:17.221015',NULL,NULL,0,57);
INSERT INTO "grampsdb_noteref" VALUES(36,32,35,1,'2012-06-10 22:25:17.223219',NULL,NULL,0,16);
INSERT INTO "grampsdb_noteref" VALUES(37,35,8,1,'2012-06-10 22:25:17.527438',NULL,NULL,0,3);
INSERT INTO "grampsdb_noteref" VALUES(38,35,9,1,'2012-06-10 22:25:17.559959',NULL,NULL,0,2);
INSERT INTO "grampsdb_noteref" VALUES(39,32,48,1,'2012-06-10 22:25:17.600199',NULL,NULL,0,4);
INSERT INTO "grampsdb_noteref" VALUES(40,32,48,1,'2012-06-10 22:25:17.602353',NULL,NULL,0,24);
INSERT INTO "grampsdb_noteref" VALUES(41,32,48,1,'2012-06-10 22:25:17.604472',NULL,NULL,0,64);
INSERT INTO "grampsdb_noteref" VALUES(42,32,48,1,'2012-06-10 22:25:17.606604',NULL,NULL,0,67);
INSERT INTO "grampsdb_noteref" VALUES(43,32,48,1,'2012-06-10 22:25:17.608739',NULL,NULL,0,35);
INSERT INTO "grampsdb_noteref" VALUES(44,32,51,1,'2012-06-10 22:25:17.756182',NULL,NULL,0,5);
INSERT INTO "grampsdb_noteref" VALUES(45,32,51,1,'2012-06-10 22:25:17.758490',NULL,NULL,0,51);
INSERT INTO "grampsdb_noteref" VALUES(46,32,51,1,'2012-06-10 22:25:17.760624',NULL,NULL,0,36);
INSERT INTO "grampsdb_noteref" VALUES(47,32,51,1,'2012-06-10 22:25:17.762760',NULL,NULL,0,32);
INSERT INTO "grampsdb_noteref" VALUES(48,32,51,1,'2012-06-10 22:25:17.764871',NULL,NULL,0,8);
INSERT INTO "grampsdb_noteref" VALUES(49,32,51,1,'2012-06-10 22:25:17.767039',NULL,NULL,0,60);
INSERT INTO "grampsdb_noteref" VALUES(50,35,10,1,'2012-06-10 22:25:17.928888',NULL,NULL,0,40);
INSERT INTO "grampsdb_noteref" VALUES(51,32,56,1,'2012-06-10 22:25:18.041188',NULL,NULL,0,68);
INSERT INTO "grampsdb_noteref" VALUES(52,32,56,1,'2012-06-10 22:25:18.044000',NULL,NULL,0,50);
INSERT INTO "grampsdb_noteref" VALUES(53,32,56,1,'2012-06-10 22:25:18.047212',NULL,NULL,0,72);
INSERT INTO "grampsdb_noteref" VALUES(54,32,56,1,'2012-06-10 22:25:18.050306',NULL,NULL,0,69);
INSERT INTO "grampsdb_noteref" VALUES(55,32,64,1,'2012-06-10 22:25:18.433226',NULL,NULL,0,23);
INSERT INTO "grampsdb_noteref" VALUES(56,32,67,1,'2012-06-10 22:25:18.499113',NULL,NULL,0,34);
INSERT INTO "grampsdb_noteref" VALUES(57,32,67,1,'2012-06-10 22:25:18.501261',NULL,NULL,0,26);
INSERT INTO "grampsdb_noteref" VALUES(58,32,67,1,'2012-06-10 22:25:18.503403',NULL,NULL,0,73);
INSERT INTO "grampsdb_noteref" VALUES(59,32,68,1,'2012-06-10 22:25:18.551204',NULL,NULL,0,38);
INSERT INTO "grampsdb_noteref" VALUES(60,32,68,1,'2012-06-10 22:25:18.553342',NULL,NULL,0,65);
INSERT INTO "grampsdb_noteref" VALUES(61,32,68,1,'2012-06-10 22:25:18.555469',NULL,NULL,0,14);
INSERT INTO "grampsdb_noteref" VALUES(62,32,68,1,'2012-06-10 22:25:18.557612',NULL,NULL,0,41);
INSERT INTO "grampsdb_noteref" VALUES(63,35,11,1,'2012-06-10 22:25:18.593992',NULL,NULL,0,11);
INSERT INTO "grampsdb_noteref" VALUES(64,32,69,1,'2012-06-10 22:25:18.641021',NULL,NULL,0,62);
INSERT INTO "grampsdb_noteref" VALUES(65,32,69,1,'2012-06-10 22:25:18.643167',NULL,NULL,0,59);
INSERT INTO "grampsdb_noteref" VALUES(66,32,69,1,'2012-06-10 22:25:18.645325',NULL,NULL,0,53);
INSERT INTO "grampsdb_noteref" VALUES(67,32,69,1,'2012-06-10 22:25:18.647443',NULL,NULL,0,48);
INSERT INTO "grampsdb_noteref" VALUES(68,32,69,1,'2012-06-10 22:25:18.649593',NULL,NULL,0,39);
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
INSERT INTO "grampsdb_eventref" VALUES(1,32,1,1,'2012-06-10 22:25:15.712242',NULL,NULL,0,88,3);
INSERT INTO "grampsdb_eventref" VALUES(2,32,1,2,'2012-06-10 22:25:15.715165',NULL,NULL,0,48,3);
INSERT INTO "grampsdb_eventref" VALUES(3,32,1,3,'2012-06-10 22:25:15.717936',NULL,NULL,0,55,3);
INSERT INTO "grampsdb_eventref" VALUES(4,32,1,4,'2012-06-10 22:25:15.720698',NULL,NULL,0,110,3);
INSERT INTO "grampsdb_eventref" VALUES(5,32,1,5,'2012-06-10 22:25:15.723524',NULL,NULL,0,102,3);
INSERT INTO "grampsdb_eventref" VALUES(6,32,2,1,'2012-06-10 22:25:15.772134',NULL,NULL,0,15,3);
INSERT INTO "grampsdb_eventref" VALUES(7,32,3,1,'2012-06-10 22:25:15.795762',NULL,NULL,0,121,3);
INSERT INTO "grampsdb_eventref" VALUES(8,32,4,1,'2012-06-10 22:25:15.818350',NULL,NULL,0,33,3);
INSERT INTO "grampsdb_eventref" VALUES(9,33,1,1,'2012-06-10 22:25:15.849184',NULL,NULL,0,112,10);
INSERT INTO "grampsdb_eventref" VALUES(10,32,6,1,'2012-06-10 22:25:15.872480',NULL,NULL,0,133,3);
INSERT INTO "grampsdb_eventref" VALUES(11,32,7,1,'2012-06-10 22:25:15.899010',NULL,NULL,0,91,3);
INSERT INTO "grampsdb_eventref" VALUES(12,32,7,2,'2012-06-10 22:25:15.901784',NULL,NULL,0,23,3);
INSERT INTO "grampsdb_eventref" VALUES(13,32,7,3,'2012-06-10 22:25:15.904526',NULL,NULL,0,11,3);
INSERT INTO "grampsdb_eventref" VALUES(14,32,7,4,'2012-06-10 22:25:15.907305',NULL,NULL,0,75,3);
INSERT INTO "grampsdb_eventref" VALUES(15,32,7,5,'2012-06-10 22:25:15.910070',NULL,NULL,0,84,3);
INSERT INTO "grampsdb_eventref" VALUES(16,32,7,6,'2012-06-10 22:25:15.912825',NULL,NULL,0,38,3);
INSERT INTO "grampsdb_eventref" VALUES(17,32,7,7,'2012-06-10 22:25:15.915585',NULL,NULL,0,46,3);
INSERT INTO "grampsdb_eventref" VALUES(18,32,8,1,'2012-06-10 22:25:15.977646',NULL,NULL,0,78,3);
INSERT INTO "grampsdb_eventref" VALUES(19,32,9,1,'2012-06-10 22:25:16.015003',NULL,NULL,0,37,3);
INSERT INTO "grampsdb_eventref" VALUES(20,32,11,1,'2012-06-10 22:25:16.064964',NULL,NULL,0,73,3);
INSERT INTO "grampsdb_eventref" VALUES(21,32,12,1,'2012-06-10 22:25:16.094691',NULL,NULL,0,139,3);
INSERT INTO "grampsdb_eventref" VALUES(22,32,12,2,'2012-06-10 22:25:16.097475',NULL,NULL,0,60,3);
INSERT INTO "grampsdb_eventref" VALUES(23,32,13,1,'2012-06-10 22:25:16.138918',NULL,NULL,0,144,3);
INSERT INTO "grampsdb_eventref" VALUES(24,32,14,1,'2012-06-10 22:25:16.161737',NULL,NULL,0,137,3);
INSERT INTO "grampsdb_eventref" VALUES(25,32,14,2,'2012-06-10 22:25:16.164520',NULL,NULL,0,66,3);
INSERT INTO "grampsdb_eventref" VALUES(26,32,16,1,'2012-06-10 22:25:16.218494',NULL,NULL,0,104,3);
INSERT INTO "grampsdb_eventref" VALUES(27,32,17,1,'2012-06-10 22:25:16.241725',NULL,NULL,0,20,3);
INSERT INTO "grampsdb_eventref" VALUES(28,32,18,1,'2012-06-10 22:25:16.267239',NULL,NULL,0,100,3);
INSERT INTO "grampsdb_eventref" VALUES(29,32,19,1,'2012-06-10 22:25:16.293892',NULL,NULL,0,19,3);
INSERT INTO "grampsdb_eventref" VALUES(30,32,20,1,'2012-06-10 22:25:16.325072',NULL,NULL,0,25,3);
INSERT INTO "grampsdb_eventref" VALUES(31,32,21,1,'2012-06-10 22:25:16.345376',NULL,NULL,0,58,3);
INSERT INTO "grampsdb_eventref" VALUES(32,32,21,2,'2012-06-10 22:25:16.348157',NULL,NULL,0,132,3);
INSERT INTO "grampsdb_eventref" VALUES(33,32,21,3,'2012-06-10 22:25:16.350958',NULL,NULL,0,31,3);
INSERT INTO "grampsdb_eventref" VALUES(34,32,21,4,'2012-06-10 22:25:16.353746',NULL,NULL,0,45,3);
INSERT INTO "grampsdb_eventref" VALUES(35,32,21,5,'2012-06-10 22:25:16.356522',NULL,NULL,0,71,3);
INSERT INTO "grampsdb_eventref" VALUES(36,33,3,1,'2012-06-10 22:25:16.404544',NULL,NULL,0,67,10);
INSERT INTO "grampsdb_eventref" VALUES(37,32,22,1,'2012-06-10 22:25:16.413793',NULL,NULL,0,8,3);
INSERT INTO "grampsdb_eventref" VALUES(38,32,22,2,'2012-06-10 22:25:16.416566',NULL,NULL,0,129,3);
INSERT INTO "grampsdb_eventref" VALUES(39,32,23,1,'2012-06-10 22:25:16.451434',NULL,NULL,0,108,3);
INSERT INTO "grampsdb_eventref" VALUES(40,32,23,2,'2012-06-10 22:25:16.454234',NULL,NULL,0,30,3);
INSERT INTO "grampsdb_eventref" VALUES(41,32,23,3,'2012-06-10 22:25:16.456994',NULL,NULL,0,18,3);
INSERT INTO "grampsdb_eventref" VALUES(42,32,23,4,'2012-06-10 22:25:16.459781',NULL,NULL,0,118,3);
INSERT INTO "grampsdb_eventref" VALUES(43,32,23,5,'2012-06-10 22:25:16.462548',NULL,NULL,0,36,3);
INSERT INTO "grampsdb_eventref" VALUES(44,32,23,6,'2012-06-10 22:25:16.465312',NULL,NULL,0,56,3);
INSERT INTO "grampsdb_eventref" VALUES(45,32,23,7,'2012-06-10 22:25:16.468091',NULL,NULL,0,13,3);
INSERT INTO "grampsdb_eventref" VALUES(46,32,23,8,'2012-06-10 22:25:16.470898',NULL,NULL,0,81,3);
INSERT INTO "grampsdb_eventref" VALUES(47,32,23,9,'2012-06-10 22:25:16.473693',NULL,NULL,0,96,3);
INSERT INTO "grampsdb_eventref" VALUES(48,32,23,10,'2012-06-10 22:25:16.476511',NULL,NULL,0,114,3);
INSERT INTO "grampsdb_eventref" VALUES(49,32,23,11,'2012-06-10 22:25:16.479346',NULL,NULL,0,47,3);
INSERT INTO "grampsdb_eventref" VALUES(50,32,24,1,'2012-06-10 22:25:16.589410',NULL,NULL,0,80,3);
INSERT INTO "grampsdb_eventref" VALUES(51,33,4,1,'2012-06-10 22:25:16.638928',NULL,NULL,0,34,10);
INSERT INTO "grampsdb_eventref" VALUES(52,33,5,1,'2012-06-10 22:25:16.649296',NULL,NULL,0,3,10);
INSERT INTO "grampsdb_eventref" VALUES(53,32,25,1,'2012-06-10 22:25:16.664310',NULL,NULL,0,21,3);
INSERT INTO "grampsdb_eventref" VALUES(54,32,26,1,'2012-06-10 22:25:16.707824',NULL,NULL,0,70,3);
INSERT INTO "grampsdb_eventref" VALUES(55,33,6,1,'2012-06-10 22:25:16.747476',NULL,NULL,0,87,10);
INSERT INTO "grampsdb_eventref" VALUES(56,32,27,1,'2012-06-10 22:25:16.761138',NULL,NULL,0,92,3);
INSERT INTO "grampsdb_eventref" VALUES(57,32,27,2,'2012-06-10 22:25:16.765551',NULL,NULL,0,134,3);
INSERT INTO "grampsdb_eventref" VALUES(58,32,28,1,'2012-06-10 22:25:16.814989',NULL,NULL,0,24,3);
INSERT INTO "grampsdb_eventref" VALUES(59,32,30,1,'2012-06-10 22:25:16.861856',NULL,NULL,0,69,3);
INSERT INTO "grampsdb_eventref" VALUES(60,32,31,1,'2012-06-10 22:25:16.886373',NULL,NULL,0,51,3);
INSERT INTO "grampsdb_eventref" VALUES(61,33,8,1,'2012-06-10 22:25:16.941773',NULL,NULL,0,93,10);
INSERT INTO "grampsdb_eventref" VALUES(62,32,32,1,'2012-06-10 22:25:16.952363',NULL,NULL,0,9,3);
INSERT INTO "grampsdb_eventref" VALUES(63,32,33,1,'2012-06-10 22:25:17.005884',NULL,NULL,0,63,3);
INSERT INTO "grampsdb_eventref" VALUES(64,32,33,2,'2012-06-10 22:25:17.008684',NULL,NULL,0,26,3);
INSERT INTO "grampsdb_eventref" VALUES(65,32,33,3,'2012-06-10 22:25:17.011537',NULL,NULL,0,43,3);
INSERT INTO "grampsdb_eventref" VALUES(66,32,33,4,'2012-06-10 22:25:17.014323',NULL,NULL,0,94,3);
INSERT INTO "grampsdb_eventref" VALUES(67,32,33,5,'2012-06-10 22:25:17.017095',NULL,NULL,0,49,3);
INSERT INTO "grampsdb_eventref" VALUES(68,32,33,6,'2012-06-10 22:25:17.019924',NULL,NULL,0,140,3);
INSERT INTO "grampsdb_eventref" VALUES(69,32,34,1,'2012-06-10 22:25:17.077294',NULL,NULL,0,50,3);
INSERT INTO "grampsdb_eventref" VALUES(70,32,34,2,'2012-06-10 22:25:17.080081',NULL,NULL,0,77,3);
INSERT INTO "grampsdb_eventref" VALUES(71,32,34,3,'2012-06-10 22:25:17.083031',NULL,NULL,0,97,3);
INSERT INTO "grampsdb_eventref" VALUES(72,32,34,4,'2012-06-10 22:25:17.085849',NULL,NULL,0,76,3);
INSERT INTO "grampsdb_eventref" VALUES(73,32,34,5,'2012-06-10 22:25:17.088620',NULL,NULL,0,89,3);
INSERT INTO "grampsdb_eventref" VALUES(74,33,10,1,'2012-06-10 22:25:17.159782',NULL,NULL,0,107,10);
INSERT INTO "grampsdb_eventref" VALUES(75,33,11,1,'2012-06-10 22:25:17.182811',NULL,NULL,0,141,10);
INSERT INTO "grampsdb_eventref" VALUES(76,33,12,1,'2012-06-10 22:25:17.198138',NULL,NULL,0,65,10);
INSERT INTO "grampsdb_eventref" VALUES(77,32,35,1,'2012-06-10 22:25:17.209996',NULL,NULL,0,6,3);
INSERT INTO "grampsdb_eventref" VALUES(78,32,35,2,'2012-06-10 22:25:17.212770',NULL,NULL,0,99,3);
INSERT INTO "grampsdb_eventref" VALUES(79,32,37,1,'2012-06-10 22:25:17.263205',NULL,NULL,0,122,3);
INSERT INTO "grampsdb_eventref" VALUES(80,32,38,1,'2012-06-10 22:25:17.286527',NULL,NULL,0,124,3);
INSERT INTO "grampsdb_eventref" VALUES(81,32,39,1,'2012-06-10 22:25:17.310281',NULL,NULL,0,7,3);
INSERT INTO "grampsdb_eventref" VALUES(82,33,13,1,'2012-06-10 22:25:17.392011',NULL,NULL,0,16,10);
INSERT INTO "grampsdb_eventref" VALUES(83,32,42,1,'2012-06-10 22:25:17.401171',NULL,NULL,0,117,3);
INSERT INTO "grampsdb_eventref" VALUES(84,32,42,2,'2012-06-10 22:25:17.403955',NULL,NULL,0,27,3);
INSERT INTO "grampsdb_eventref" VALUES(85,32,43,1,'2012-06-10 22:25:17.434026',NULL,NULL,0,64,3);
INSERT INTO "grampsdb_eventref" VALUES(86,32,43,2,'2012-06-10 22:25:17.436808',NULL,NULL,0,131,3);
INSERT INTO "grampsdb_eventref" VALUES(87,32,45,1,'2012-06-10 22:25:17.477477',NULL,NULL,0,109,3);
INSERT INTO "grampsdb_eventref" VALUES(88,32,45,2,'2012-06-10 22:25:17.480326',NULL,NULL,0,83,3);
INSERT INTO "grampsdb_eventref" VALUES(89,32,47,1,'2012-06-10 22:25:17.539245',NULL,NULL,0,68,3);
INSERT INTO "grampsdb_eventref" VALUES(90,32,48,1,'2012-06-10 22:25:17.576152',NULL,NULL,0,32,3);
INSERT INTO "grampsdb_eventref" VALUES(91,32,48,2,'2012-06-10 22:25:17.578944',NULL,NULL,0,17,3);
INSERT INTO "grampsdb_eventref" VALUES(92,32,48,3,'2012-06-10 22:25:17.581788',NULL,NULL,0,62,3);
INSERT INTO "grampsdb_eventref" VALUES(93,32,48,4,'2012-06-10 22:25:17.584657',NULL,NULL,0,54,3);
INSERT INTO "grampsdb_eventref" VALUES(94,32,48,5,'2012-06-10 22:25:17.587426',NULL,NULL,0,41,3);
INSERT INTO "grampsdb_eventref" VALUES(95,32,48,6,'2012-06-10 22:25:17.590194',NULL,NULL,0,123,3);
INSERT INTO "grampsdb_eventref" VALUES(96,33,14,1,'2012-06-10 22:25:17.669505',NULL,NULL,0,135,10);
INSERT INTO "grampsdb_eventref" VALUES(97,32,50,1,'2012-06-10 22:25:17.693098',NULL,NULL,0,119,3);
INSERT INTO "grampsdb_eventref" VALUES(98,32,51,1,'2012-06-10 22:25:17.729016',NULL,NULL,0,95,3);
INSERT INTO "grampsdb_eventref" VALUES(99,32,51,2,'2012-06-10 22:25:17.731835',NULL,NULL,0,115,3);
INSERT INTO "grampsdb_eventref" VALUES(100,32,51,3,'2012-06-10 22:25:17.734657',NULL,NULL,0,1,3);
INSERT INTO "grampsdb_eventref" VALUES(101,32,51,4,'2012-06-10 22:25:17.737466',NULL,NULL,0,42,3);
INSERT INTO "grampsdb_eventref" VALUES(102,32,51,5,'2012-06-10 22:25:17.740261',NULL,NULL,0,136,3);
INSERT INTO "grampsdb_eventref" VALUES(103,32,51,6,'2012-06-10 22:25:17.743088',NULL,NULL,0,128,3);
INSERT INTO "grampsdb_eventref" VALUES(104,32,51,7,'2012-06-10 22:25:17.745895',NULL,NULL,0,116,3);
INSERT INTO "grampsdb_eventref" VALUES(105,32,52,1,'2012-06-10 22:25:17.832030',NULL,NULL,0,143,3);
INSERT INTO "grampsdb_eventref" VALUES(106,32,53,1,'2012-06-10 22:25:17.885559',NULL,NULL,0,86,3);
INSERT INTO "grampsdb_eventref" VALUES(107,32,53,2,'2012-06-10 22:25:17.889699',NULL,NULL,0,98,3);
INSERT INTO "grampsdb_eventref" VALUES(108,33,15,1,'2012-06-10 22:25:17.940452',NULL,NULL,0,106,10);
INSERT INTO "grampsdb_eventref" VALUES(109,32,54,1,'2012-06-10 22:25:17.955220',NULL,NULL,0,127,3);
INSERT INTO "grampsdb_eventref" VALUES(110,32,55,1,'2012-06-10 22:25:17.983865',NULL,NULL,0,4,3);
INSERT INTO "grampsdb_eventref" VALUES(111,32,56,1,'2012-06-10 22:25:18.026514',NULL,NULL,0,101,3);
INSERT INTO "grampsdb_eventref" VALUES(112,32,56,2,'2012-06-10 22:25:18.029780',NULL,NULL,0,61,3);
INSERT INTO "grampsdb_eventref" VALUES(113,32,57,1,'2012-06-10 22:25:18.092434',NULL,NULL,0,52,3);
INSERT INTO "grampsdb_eventref" VALUES(114,32,58,1,'2012-06-10 22:25:18.126397',NULL,NULL,0,10,3);
INSERT INTO "grampsdb_eventref" VALUES(115,33,16,1,'2012-06-10 22:25:18.188038',NULL,NULL,0,126,10);
INSERT INTO "grampsdb_eventref" VALUES(116,32,59,1,'2012-06-10 22:25:18.197291',NULL,NULL,0,111,3);
INSERT INTO "grampsdb_eventref" VALUES(117,32,59,2,'2012-06-10 22:25:18.200069',NULL,NULL,0,85,3);
INSERT INTO "grampsdb_eventref" VALUES(118,32,59,3,'2012-06-10 22:25:18.202839',NULL,NULL,0,53,3);
INSERT INTO "grampsdb_eventref" VALUES(119,32,60,1,'2012-06-10 22:25:18.249345',NULL,NULL,0,29,3);
INSERT INTO "grampsdb_eventref" VALUES(120,32,60,2,'2012-06-10 22:25:18.252143',NULL,NULL,0,2,3);
INSERT INTO "grampsdb_eventref" VALUES(121,32,61,1,'2012-06-10 22:25:18.282727',NULL,NULL,0,5,3);
INSERT INTO "grampsdb_eventref" VALUES(122,32,61,2,'2012-06-10 22:25:18.285518',NULL,NULL,0,22,3);
INSERT INTO "grampsdb_eventref" VALUES(123,32,61,3,'2012-06-10 22:25:18.288303',NULL,NULL,0,57,3);
INSERT INTO "grampsdb_eventref" VALUES(124,32,61,4,'2012-06-10 22:25:18.291116',NULL,NULL,0,35,3);
INSERT INTO "grampsdb_eventref" VALUES(125,32,62,1,'2012-06-10 22:25:18.338282',NULL,NULL,0,59,3);
INSERT INTO "grampsdb_eventref" VALUES(126,32,62,2,'2012-06-10 22:25:18.341079',NULL,NULL,0,125,3);
INSERT INTO "grampsdb_eventref" VALUES(127,33,17,1,'2012-06-10 22:25:18.386582',NULL,NULL,0,138,10);
INSERT INTO "grampsdb_eventref" VALUES(128,33,18,1,'2012-06-10 22:25:18.414629',NULL,NULL,0,28,10);
INSERT INTO "grampsdb_eventref" VALUES(129,32,64,1,'2012-06-10 22:25:18.422974',NULL,NULL,0,82,3);
INSERT INTO "grampsdb_eventref" VALUES(130,32,67,1,'2012-06-10 22:25:18.486304',NULL,NULL,0,39,3);
INSERT INTO "grampsdb_eventref" VALUES(131,32,67,2,'2012-06-10 22:25:18.489093',NULL,NULL,0,74,3);
INSERT INTO "grampsdb_eventref" VALUES(132,32,68,1,'2012-06-10 22:25:18.530791',NULL,NULL,0,12,3);
INSERT INTO "grampsdb_eventref" VALUES(133,32,68,2,'2012-06-10 22:25:18.533633',NULL,NULL,0,79,3);
INSERT INTO "grampsdb_eventref" VALUES(134,32,68,3,'2012-06-10 22:25:18.536433',NULL,NULL,0,105,3);
INSERT INTO "grampsdb_eventref" VALUES(135,32,68,4,'2012-06-10 22:25:18.539216',NULL,NULL,0,142,3);
INSERT INTO "grampsdb_eventref" VALUES(136,32,68,5,'2012-06-10 22:25:18.542218',NULL,NULL,0,120,3);
INSERT INTO "grampsdb_eventref" VALUES(137,32,68,6,'2012-06-10 22:25:18.545062',NULL,NULL,0,44,3);
INSERT INTO "grampsdb_eventref" VALUES(138,32,69,1,'2012-06-10 22:25:18.610179',NULL,NULL,0,14,3);
INSERT INTO "grampsdb_eventref" VALUES(139,32,69,2,'2012-06-10 22:25:18.612972',NULL,NULL,0,130,3);
INSERT INTO "grampsdb_eventref" VALUES(140,32,69,3,'2012-06-10 22:25:18.615753',NULL,NULL,0,103,3);
INSERT INTO "grampsdb_eventref" VALUES(141,32,69,4,'2012-06-10 22:25:18.618562',NULL,NULL,0,90,3);
INSERT INTO "grampsdb_eventref" VALUES(142,32,69,5,'2012-06-10 22:25:18.621356',NULL,NULL,0,113,3);
INSERT INTO "grampsdb_eventref" VALUES(143,32,69,6,'2012-06-10 22:25:18.624237',NULL,NULL,0,72,3);
INSERT INTO "grampsdb_eventref" VALUES(144,32,69,7,'2012-06-10 22:25:18.627048',NULL,NULL,0,40,3);
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
INSERT INTO "grampsdb_childref" VALUES(1,33,1,1,'2012-06-10 22:25:15.839374',NULL,NULL,0,2,2,23);
INSERT INTO "grampsdb_childref" VALUES(2,33,1,2,'2012-06-10 22:25:15.842935',NULL,NULL,0,2,2,52);
INSERT INTO "grampsdb_childref" VALUES(3,33,1,3,'2012-06-10 22:25:15.846336',NULL,NULL,0,2,2,50);
INSERT INTO "grampsdb_childref" VALUES(4,33,2,1,'2012-06-10 22:25:16.086297',NULL,NULL,0,2,2,33);
INSERT INTO "grampsdb_childref" VALUES(5,33,4,1,'2012-06-10 22:25:16.625752',NULL,NULL,0,2,2,10);
INSERT INTO "grampsdb_childref" VALUES(6,33,4,2,'2012-06-10 22:25:16.630650',NULL,NULL,0,2,2,17);
INSERT INTO "grampsdb_childref" VALUES(7,33,4,3,'2012-06-10 22:25:16.634556',NULL,NULL,0,2,2,41);
INSERT INTO "grampsdb_childref" VALUES(8,33,8,1,'2012-06-10 22:25:16.925139',NULL,NULL,0,2,2,19);
INSERT INTO "grampsdb_childref" VALUES(9,33,8,2,'2012-06-10 22:25:16.928638',NULL,NULL,0,2,2,18);
INSERT INTO "grampsdb_childref" VALUES(10,33,8,3,'2012-06-10 22:25:16.932004',NULL,NULL,0,2,2,60);
INSERT INTO "grampsdb_childref" VALUES(11,33,8,4,'2012-06-10 22:25:16.935377',NULL,NULL,0,2,2,6);
INSERT INTO "grampsdb_childref" VALUES(12,33,8,5,'2012-06-10 22:25:16.938854',NULL,NULL,0,2,2,48);
INSERT INTO "grampsdb_childref" VALUES(13,33,10,1,'2012-06-10 22:25:17.129303',NULL,NULL,0,2,2,68);
INSERT INTO "grampsdb_childref" VALUES(14,33,10,2,'2012-06-10 22:25:17.132828',NULL,NULL,0,2,2,51);
INSERT INTO "grampsdb_childref" VALUES(15,33,10,3,'2012-06-10 22:25:17.136222',NULL,NULL,0,2,2,35);
INSERT INTO "grampsdb_childref" VALUES(16,33,10,4,'2012-06-10 22:25:17.139621',NULL,NULL,0,2,2,67);
INSERT INTO "grampsdb_childref" VALUES(17,33,10,5,'2012-06-10 22:25:17.143241',NULL,NULL,0,2,2,56);
INSERT INTO "grampsdb_childref" VALUES(18,33,10,6,'2012-06-10 22:25:17.146710',NULL,NULL,0,2,2,64);
INSERT INTO "grampsdb_childref" VALUES(19,33,10,7,'2012-06-10 22:25:17.150085',NULL,NULL,0,2,2,21);
INSERT INTO "grampsdb_childref" VALUES(20,33,10,8,'2012-06-10 22:25:17.153507',NULL,NULL,0,2,2,42);
INSERT INTO "grampsdb_childref" VALUES(21,33,10,9,'2012-06-10 22:25:17.156893',NULL,NULL,0,2,2,27);
INSERT INTO "grampsdb_childref" VALUES(22,33,11,1,'2012-06-10 22:25:17.169712',NULL,NULL,0,2,2,15);
INSERT INTO "grampsdb_childref" VALUES(23,33,11,2,'2012-06-10 22:25:17.173136',NULL,NULL,0,2,2,44);
INSERT INTO "grampsdb_childref" VALUES(24,33,11,3,'2012-06-10 22:25:17.176534',NULL,NULL,0,2,2,66);
INSERT INTO "grampsdb_childref" VALUES(25,33,11,4,'2012-06-10 22:25:17.179960',NULL,NULL,0,2,2,36);
INSERT INTO "grampsdb_childref" VALUES(26,33,13,1,'2012-06-10 22:25:17.375519',NULL,NULL,0,2,2,53);
INSERT INTO "grampsdb_childref" VALUES(27,33,13,2,'2012-06-10 22:25:17.378977',NULL,NULL,0,2,2,58);
INSERT INTO "grampsdb_childref" VALUES(28,33,13,3,'2012-06-10 22:25:17.382361',NULL,NULL,0,2,2,65);
INSERT INTO "grampsdb_childref" VALUES(29,33,13,4,'2012-06-10 22:25:17.385746',NULL,NULL,0,2,2,38);
INSERT INTO "grampsdb_childref" VALUES(30,33,13,5,'2012-06-10 22:25:17.389155',NULL,NULL,0,2,2,8);
INSERT INTO "grampsdb_childref" VALUES(31,33,14,1,'2012-06-10 22:25:17.659858',NULL,NULL,0,2,2,55);
INSERT INTO "grampsdb_childref" VALUES(32,33,14,2,'2012-06-10 22:25:17.663259',NULL,NULL,0,2,2,45);
INSERT INTO "grampsdb_childref" VALUES(33,33,14,3,'2012-06-10 22:25:17.666647',NULL,NULL,0,2,2,32);
INSERT INTO "grampsdb_childref" VALUES(34,33,16,1,'2012-06-10 22:25:18.150892',NULL,NULL,0,2,2,26);
INSERT INTO "grampsdb_childref" VALUES(35,33,16,2,'2012-06-10 22:25:18.154370',NULL,NULL,0,2,2,37);
INSERT INTO "grampsdb_childref" VALUES(36,33,16,3,'2012-06-10 22:25:18.157758',NULL,NULL,0,2,2,22);
INSERT INTO "grampsdb_childref" VALUES(37,33,16,4,'2012-06-10 22:25:18.161143',NULL,NULL,0,2,2,24);
INSERT INTO "grampsdb_childref" VALUES(38,33,16,5,'2012-06-10 22:25:18.164538',NULL,NULL,0,2,2,54);
INSERT INTO "grampsdb_childref" VALUES(39,33,16,6,'2012-06-10 22:25:18.168093',NULL,NULL,0,2,2,9);
INSERT INTO "grampsdb_childref" VALUES(40,33,16,7,'2012-06-10 22:25:18.171490',NULL,NULL,0,2,2,30);
INSERT INTO "grampsdb_childref" VALUES(41,33,16,8,'2012-06-10 22:25:18.174926',NULL,NULL,0,2,2,13);
INSERT INTO "grampsdb_childref" VALUES(42,33,16,9,'2012-06-10 22:25:18.178372',NULL,NULL,0,2,2,39);
INSERT INTO "grampsdb_childref" VALUES(43,33,16,10,'2012-06-10 22:25:18.181785',NULL,NULL,0,2,2,2);
INSERT INTO "grampsdb_childref" VALUES(44,33,16,11,'2012-06-10 22:25:18.185189',NULL,NULL,0,2,2,47);
INSERT INTO "grampsdb_childref" VALUES(45,33,17,1,'2012-06-10 22:25:18.376911',NULL,NULL,0,2,2,61);
INSERT INTO "grampsdb_childref" VALUES(46,33,17,2,'2012-06-10 22:25:18.380358',NULL,NULL,0,2,2,59);
INSERT INTO "grampsdb_childref" VALUES(47,33,17,3,'2012-06-10 22:25:18.383734',NULL,NULL,0,2,2,62);
INSERT INTO "grampsdb_childref" VALUES(48,33,18,1,'2012-06-10 22:25:18.408362',NULL,NULL,0,2,2,69);
INSERT INTO "grampsdb_childref" VALUES(49,33,18,2,'2012-06-10 22:25:18.411746',NULL,NULL,0,2,2,5);
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
