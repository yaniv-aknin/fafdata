# BigQuery management commands

Starting from an empty GCP project, these are the commands I used to create the table.

```bash
bq mk --dataset faf

bq mk --table \
    --time_partitioning_field endTime \
    --time_partitioning_type MONTH \
    faf.games ./bigquery/games.schema.json

# Assume you transformed data with: faf_dump_to_bigquery_jsonl path_to_raw_api_dump.json transformed_dump.jsonl
bq load \
    --source_format=NEWLINE_DELIMITED_JSON \
    faf.games transformed_dump.jsonl
```

## Creating table schema

To create the table schema, I've used BigQuery autodetection feature, and then edited it manually (so the order of fields etc makes more sense).

```bash
# Assume you transformed data with: faf_dump_to_bigquery_jsonl path_to_raw_api_dump.json transformed_dump.jsonl
bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON faf.games transformed_dump.jsonl

# the output includes the schema in JSON format
bq show --format=prettyjson faf.games
```
