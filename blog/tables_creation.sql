CREATE TABLE user(
    id              INT unsigned NOT NULL AUTO_INCREMENT,
    login            VARCHAR(150) NOT NULL,
    password             VARCHAR(150) NOT NULL,
    PRIMARY KEY     (id)
    );

CREATE TABLE blog(
    id              INT unsigned NOT NULL AUTO_INCREMENT,
    name            VARCHAR(150) NOT NULL,
    user_token      CHAR(36),
    PRIMARY KEY     (id)
    );

CREATE TABLE post(
    id              INT unsigned NOT NULL AUTO_INCREMENT,
    title           VARCHAR(150) NOT NULL,
    text            Text NOT NULL,
    PRIMARY KEY     (id)
    );


CREATE TABLE blog_post(
    id              INT unsigned NOT NULL AUTO_INCREMENT,
    post_id         INT unsigned NOT NULL,
    blog_id         INT unsigned NOT NULL,
    PRIMARY KEY     (id)
    );

CREATE TABLE comment(
    id                INT unsigned NOT NULL AUTO_INCREMENT,
    text              Text NOT NULL,
    user_id           INT unsigned NOT NULL,
    post_id           INT unsigned NOT NULL,
    parent_comment_id INT unsigned,
    PRIMARY KEY     (id)
    );

CREATE TABLE session(
    id                INT unsigned NOT NULL AUTO_INCREMENT,
    user_id           INT unsigned NOT NULL,
    token             CHAR(36) NOT NULL,
    PRIMARY KEY     (id)
    );
