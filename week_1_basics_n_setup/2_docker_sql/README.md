## Docker and SQL

Notes I used for preparing the videos: [link](https://docs.google.com/document/d/e/2PACX-1vRJUuGfzgIdbkalPgg2nQ884CnZkCg314T_OBq-_hfcowPxNIA0-z5OtMTDzuzute9VBHMjNYZFTCc1/pub)


## Commands 

All the commands from the video

Downloading the data with Curl (-LO required when downloading from GitHub)

```bash
curl -LO https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz 
```

> Note: now the CSV data is stored in the `csv_backup` folder, not `trip+date` like previously

### Running Postgres with Docker

#### Windows

Running Postgres on Windows (note the full path)

```bash
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v c:/Users/alexe/git/data-engineering-zoomcamp/week_1_basics_n_setup/2_docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13
```

If you have the following error:

```
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v e:/zoomcamp/data_engineer/week_1_fundamentals/2_docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data  \
  -p 5432:5432 \
  postgres:13

docker: Error response from daemon: invalid mode: \Program Files\Git\var\lib\postgresql\data.
See 'docker run --help'.
```

Change the mounting path. Replace it with the following:

```
-v /e/zoomcamp/...:/var/lib/postgresql/data
```

#### Linux and MacOS

Spoiler: create network first
```bash
docker network create pg-network
```

```bash
docker run --rm -d \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p [CHANGE PORT APPROPRIATELY]:5432 \
  --network=pg-network \
  --name=pg-database \
  postgres:13
```

If you see that `ny_taxi_postgres_data` is empty after running
the container, try these:

* Deleting the folder and running Docker again (Docker will re-create the folder)
* Adjust the permissions of the folder by running `sudo chmod a+rwx ny_taxi_postgres_data`


### CLI for Postgres

Installing `pgcli`

```bash
pip install pgcli
```

If you have problems installing `pgcli` with the command above, try this:

```bash
conda install -c conda-forge pgcli
pip install -U mycli
```

Using `pgcli` to connect to Postgres

```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi
```


### NY Trips Dataset

Dataset:

* https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
* https://www1.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf

> According to the [TLC data website](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page),
> from 05/13/2022, the data will be in ```.parquet``` format instead of ```.csv```
> The website has provided a useful [link](https://www1.nyc.gov/assets/tlc/downloads/pdf/working_parquet_format.pdf) with sample steps to read ```.parquet``` file and convert it to Pandas data frame.
>
> You can use the csv backup located here, https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz, to follow along with the video.
```
$ aws s3 ls s3://nyc-tlc
                           PRE csv_backup/
                           PRE misc/
                           PRE trip data/
```

### pgAdmin

Running pgAdmin

```bash
docker run --rm -d \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  --network=pg-network \
  --name=pgadmin \
  dpage/pgadmin4
```

### Running Postgres and pgAdmin together

REMOVED: did this already above


### Data ingestion

Running locally

```bash
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

python ingest_data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=yellow_taxi_trips \
  --datecols=tpep_pickup_datetime,tpep_dropoff_datetime
  --url=${URL}
```

Build the image

```bash
docker build -t taxi_ingest:v001 .
```

On Linux you may have a problem building it:

```
error checking context: 'can't stat '/home/name/data_engineering/ny_taxi_postgres_data''.
```

You can solve it with `.dockerignore`:

* Create a folder `data`
* Move `ny_taxi_postgres_data` to `data` (you might need to use `sudo` for that)
* Map `-v $(pwd)/data/ny_taxi_postgres_data:/var/lib/postgresql/data`
* Create a file `.dockerignore` and add `data` there
* Check [this video](https://www.youtube.com/watch?v=tOr4hTsHOzU&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) (the middle) for more details 

Run the script with Docker

**Don't forget to change port as appropriate!**

```bash

docker run -d --rm \
  --network=pg-network \
  taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5433 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips \
    --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
```

### Docker-Compose

The options for ingesting data can be passed as environment variables. You can just include them before running the docker compose up command, on the the same line, e.g.:

```bash
PG_TABLE_NAME=green_taxi_trips DATA_URL=https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv docker compose up```

... will ingest the data into the table `green_taxi_trips` and take the data from the specified URL.

Run it:

```bash
docker-compose up
```

Run in detached mode:

```bash
docker compose up -d
```

Shutting it down:

```bash
docker compose down
```

A Docker volume is specified in `docker-compose.yml` to ensure the storage is persistent (so you don't have to re-ingest data every time, or re-enter connection settings in pgadmin every time you restart the containers).

## SQL -> Homework for week 1

#### Question 1: docker help

```
docker help build
```

#### Question 2. Understanding Docker first run

Build the image:

```bash
docker build . --tag data-ingester
```

I changed my Dockerfile a little, so the following works for me:

```bash
docker run --rm data-ingester -m pip list --not-required
```

#### Question 3. Count records

```SQL
SELECT
COUNT(*)
FROM green_taxi_trips
WHERE
	lpep_pickup_datetime::timestamp >= '2019-01-15'::timestamp
	AND
	lpep_dropoff_datetime::timestamp < '2019-01-16'::timestamp
```

#### Question 4. Largest trip for each day

```SELECT
	lpep_pickup_datetime::date as pickup_date,
	MAX(trip_distance)
FROM
	green_taxi_trips
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1
```

#### Question 5. Number of passengers

```SQL
SELECT COUNT(*) FROM
	(SELECT
		lpep_pickup_datetime::timestamp AS pickup,
	 	passenger_count
	FROM
		green_taxi_trips) sub
WHERE
	pickup >= '2019-01-01'::timestamp
	AND 
	pickup < '2019-01-02'::timestamp
	AND
	passenger_count = 3

```
#### Question 6. Largest tip

```SQL
SELECT
	green_zone_lookup."Zone" AS do_zone,
	MAX(tip_amount) AS highest_tip
FROM
(SELECT * FROM green_taxi_trips
JOIN
	green_zone_lookup
	ON
	"PULocationID" = green_zone_lookup."LocationID"
WHERE
 	green_zone_lookup."Zone" = 'Astoria'
) sub
JOIN
	green_zone_lookup
	ON
	"DOLocationID" = green_zone_lookup."LocationID"
GROUP BY
	do_zone
ORDER BY highest_tip DESC
```
