CREATE TABLE IF NOT EXISTS directory_stats
(
    datetime timestamp without time zone,
    searched_directory character varying(512),
    system character varying(64),
    total_file_size bigint,
    disk_use_percent float,
    disk_use_change float,
    last_access_average float,
    access_average_change float,

    PRIMARY KEY (datetime, searched_directory, system, total_file_size, disk_use_percent, disk_use_change, last_access_average, access_average_change)
)

WITH ( OIDS=FALSE );

CREATE TABLE IF NOT EXISTS user_stats
(
    datetime timestamp without time zone NULL,
    searched_directory character varying(512) NULL,
    system character varying(64),
    user_name character varying(64) NULL,
    total_file_size bigint NULL,
    disk_use_percent float NULL,
    disk_use_change float NULL,
    last_access_average float NULL,
    access_average_change float NULL,

    PRIMARY KEY (datetime, searched_directory, system, user_name, total_file_size, disk_use_percent, disk_use_change, last_access_average, access_average_change)
)

WITH ( OIDS=FALSE );
