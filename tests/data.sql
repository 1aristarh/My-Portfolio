INSERT INTO user (username, password, role)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', 'read_only'),
  ('admin', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79', 'admin');

INSERT INTO post (title, body, author_id, created, youtube_id)
VALUES
  ('test title', 'test body', 2, '2018-01-01 00:00:00', 'dQw4w9WgXcQ'),
  ('another post', 'body text', 2, '2018-01-02 00:00:00', null);