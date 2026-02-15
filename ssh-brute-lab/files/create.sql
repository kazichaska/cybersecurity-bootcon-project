CREATE DATABASE bwapp;

USE bwapp;

CREATE TABLE IF NOT EXISTS users (id int(10) NOT NULL AUTO_INCREMENT,login varchar(100) DEFAULT NULL,password varchar(100) DEFAULT NULL, email varchar(100) DEFAULT NULL,secret varchar(100) DEFAULT NULL,activation_code varchar(100) DEFAULT NULL,activated tinyint(1) DEFAULT '0', reset_code varchar(100) DEFAULT NULL,admin tinyint(1) DEFAULT '0',PRIMARY KEY (id)) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

INSERT INTO users (login, password, email, secret, activation_code, activated, reset_code, admin) VALUES('A.I.M.', '6885858486f31043e5839c735d99457f045affd0', 'bwapp-aim@mailinator.com', 'A.I.M. or Authentication Is Missing', NULL, 1, NULL, 1),('bee', '6885858486f31043e5839c735d99457f045affd0', 'bwapp-bee@mailinator.com', 'Any bugs?', NULL, 1, NULL, 1);

CREATE TABLE IF NOT EXISTS blog (id int(10) NOT NULL AUTO_INCREMENT,owner varchar(100) DEFAULT NULL, entry varchar(500) DEFAULT NULL,date datetime DEFAULT NULL,PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS visitors (id int(10) NOT NULL AUTO_INCREMENT,ip_address varchar(50) DEFAULT NULL, user_agent varchar(500) DEFAULT NULL,date datetime DEFAULT NULL,PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS movies (id int(10) NOT NULL AUTO_INCREMENT,title varchar(100) DEFAULT NULL, release_year varchar(100) DEFAULT NULL,genre varchar(100) DEFAULT NULL,main_character varchar(100) DEFAULT NULL, imdb varchar(100) DEFAULT NULL,tickets_stock int(10) DEFAULT NULL,PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

INSERT INTO movies (title, release_year, genre, main_character, imdb, tickets_stock) VALUES ('G.I. Joe: Retaliation', '2013', 'action', 'Cobra Commander', 'tt1583421', 100),('Iron Man', '2008', 'action', 'Tony Stark', 'tt0371746', 53),('Man of Steel', '2013', 'action', 'Clark Kent', 'tt0770828', 78),('Terminator Salvation', '2009', 'sci-fi', 'John Connor', 'tt0438488', 100),('The Amazing Spider-Man', '2012', 'action', 'Peter Parker', 'tt0948470', 13),('The Cabin in the Woods', '2011', 'horror', 'Some zombies', 'tt1259521', 666),('The Dark Knight Rises', '2012', 'action', 'Bruce Wayne', 'tt1345836', 3),('The Fast and the Furious', '2001', 'action', 'Brian O\'Connor', 'tt0232500', 40),('The Incredible Hulk', '2008', 'action', 'Bruce Banner', 'tt0800080', 23),('World War Z', '2013', 'horror', 'Gerry Lane', 'tt0816711', 0);

CREATE TABLE IF NOT EXISTS heroes (id int(10) NOT NULL AUTO_INCREMENT,login varchar(100) DEFAULT NULL,password varchar(100) DEFAULT NULL,secret varchar(100) DEFAULT NULL, PRIMARY KEY (id)) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

INSERT INTO heroes (login, password, secret) VALUES('neo', 'trinity', 'Oh why didn\'t I took that BLACK pill?'),('alice', 'loveZombies', 'There\'s a cure!'),('thor', 'Asgard', 'Oh, no... this is Earth... isn\'t it?'),('wolverine', 'Log@N', 'What\'s a Magneto?'),('johnny', 'm3ph1st0ph3l3s', 'I\'m the Ghost Rider!'),('seline', 'm00n', 'It wasn\'t the Lycans. It was you.');