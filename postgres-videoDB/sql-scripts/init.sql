CREATE DATABASE video_db;
CREATE TABLE IF NOT EXISTS videos
(
	video_id serial PRIMARY KEY,
	user_id serial,
	title VARCHAR ( 100 ) UNIQUE NOT NULL,
	description VARCHAR ( 1000 ) NOT NULL,
	width INT NOT NULL,
	height INT NOT NULL,
	created_on TIMESTAMP NOT NULL,
	path VARCHAR ( 1000 ) UNIQUE NOT NULL
);
INSERT INTO videos (video_id, user_id, title, description, width, height, created_on, path) VALUES (1,1,'Video title 1', 'Video description 1', 1920, 1080, '2006-01-01 15:36:38', 'path/to/video/video1.mp4');
INSERT INTO videos (video_id, user_id, title, description, width, height, created_on, path) VALUES (2,2,'Video title 2', 'Video description 2', 1920, 1080, '2006-01-02 15:36:38', 'path/to/video/video2.mp4');
INSERT INTO videos (video_id, user_id, title, description, width, height, created_on, path) VALUES (3,1,'Video title 3', 'Video description 3', 1920, 1080, '2006-01-03 15:36:38', 'path/to/video/video3.mp4');
INSERT INTO videos (video_id, user_id, title, description, width, height, created_on, path) VALUES (4,2,'Video title 4', 'Video description 4', 1920, 1080, '2006-01-04 15:36:38', 'path/to/video/video4.mp4');
