## Please run the following statements in the RDS database instance mysqlinstp:

CREATE TABLE mysqldbp.books (id INTEGER, title VARCHAR(50), author VARCHAR(20), year INTEGER);

INSERT INTO mysqldbp.books VALUES (1, '1984', 'Orwell', 1949);
INSERT INTO mysqldbp.books VALUES (2, 'The book of the jungle', 'Kipling', 1894);
INSERT INTO mysqldbp.books VALUES (3, 'Neuromancer', 'Gibson', 1984);
INSERT INTO mysqldbp.books VALUES (4, 'Jurassic Park', 'Crichton', 1990);
INSERT INTO mysqldbp.books VALUES (5, 'The little prince', 'de Saint-Exupery', 1943);
COMMIT;


CREATE TABLE mysqldbp.logs (recordingdate TIMESTAMP, message VARCHAR(100));

INSERT INTO mysqldbp.logs VALUES (CURRENT_TIMESTAMP, 'new book inserted');
INSERT INTO mysqldbp.logs VALUES (CURRENT_TIMESTAMP, 'new book inserted');
INSERT INTO mysqldbp.logs VALUES (CURRENT_TIMESTAMP, 'book updated');
INSERT INTO mysqldbp.logs VALUES (CURRENT_TIMESTAMP, 'book delete');
INSERT INTO mysqldbp.logs VALUES (CURRENT_TIMESTAMP, 'new book inserted');
COMMIT;


CREATE TABLE mysqldbp.customers (id INTEGER, surname VARCHAR(50), email VARCHAR(30), address VARCHAR(50));

INSERT INTO mysqldbp.customers VALUES (1, 'John Doe', 'john.doe@email123.com', 'Rout 66');
INSERT INTO mysqldbp.customers VALUES (2, 'Jason Burns', 'jason.burns@email123.com', 'Route 53');
INSERT INTO mysqldbp.customers VALUES (3, 'Mike Santos', 'mike.santos@email123.com', 'Main street');
INSERT INTO mysqldbp.customers VALUES (4, 'Mario Rossi', 'mario.rossi@email123.com', 'High street');
INSERT INTO mysqldbp.customers VALUES (5, 'Jack Fried', 'jack.fried@email123.com', 'Lower street');
COMMIT;

SELECT * FROM mysqldbp.books ORDER BY id;

SELECT * FROM mysqldbp.logs ORDER BY recordingdate;

SELECT * FROM mysqldbp.customers ORDER BY id;