-- SQLite
UPDATE users set user_type = 'admin' where id = 1;

BEGIN TRANSACTION;
UPDATE product_deals set date = '2024-05-18';
COMMIT;

BEGIN TRANSACTION;
UPDATE product_deals set active = 1;
COMMIT;

BEGIN TRANSACTION;
DELETE FROM product_deals;
COMMIT;