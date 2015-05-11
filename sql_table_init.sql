CREATE TABLE IF NOT EXISTS directory_stats
(
    datetime timestamp without time zone,
    searched_directory character varying(512),
    total_file_size integer,
    disk_use_percent float,
    disk_use_change float,
    last_access_average float,
    access_averaage_change float,

    PRIMARY KEY (datetime, searched_directory, total_file_size, disk_use_percent, disk_use_change, last_access_average, access_averaage_change)
)

WITH ( OIDS=FALSE );

CREATE TABLE IF NOT EXISTS user_stats
(
    datetime timestamp without time zone NULL,
    searched_directory character varying(512) NULL,
    user_name character varying(64) NULL,
    total_file_size integer NULL,
    disk_use_percent float NULL,
    disk_use_change float NULL,
    last_access_average float NULL,
    access_averaage_change float NULL,

    PRIMARY KEY (datetime, searched_directory, user_name, total_file_size, disk_use_percent, disk_use_change, last_access_average, access_averaage_change)
)

WITH ( OIDS=FALSE );
