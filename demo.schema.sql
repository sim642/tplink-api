CREATE TABLE demo
(
	id integer not null
		constraint demo_pk
			primary key autoincrement,
	datetime TEXT not null,
	hostname text not null,
	bytes integer not null
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE VIEW demo_diff AS
SELECT *,
--     (CASE
--         WHEN (bytes - (lag(bytes) OVER host_win)) >= 0 THEN (bytes - (lag(bytes) OVER host_win))
--         ELSE ((4294967295 - (lag(bytes) OVER host_win)) + bytes)
--     END) AS bytes_diff,
    ((bytes - (lag(bytes) OVER host_win) + 4294967296) % 4294967296) AS bytes_diff,
    (julianday(datetime) - julianday(lag(datetime) OVER host_win)) * 24 * 60 * 60 AS datetime_diff
FROM demo
WINDOW host_win AS (PARTITION BY hostname ORDER BY datetime ASC)
ORDER BY hostname ASC, datetime ASC
/* demo_diff(id,datetime,hostname,bytes,bytes_diff,datetime_diff) */;
