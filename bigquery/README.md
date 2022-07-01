# BigQuery management commands

Starting from an empty GCP project, these are the commands I used to load the games table.

```bash
bq mk --dataset faf

bq mk --table \
    --time_partitioning_field endTime \
    --time_partitioning_type MONTH \
    faf.games ./bigquery/games.schema.json

# Assume you transformed data with: transform_api_dump_to_jsonl path_to_raw_api_dump.json transformed_dump.jsonl
bq load \
    --source_format=NEWLINE_DELIMITED_JSON \
    faf.games transformed_dump.jsonl
```

## Creating other tables

As I add support for more tables, I'll create more schema files under the `./bigquery` directory. They can be loaded the same way.

## Creating table schema

To create the table schema, I've used BigQuery autodetection feature, and then edited it manually (so the order of fields etc makes more sense).

```bash
# Assume you transformed data with: transform_api_dump_to_jsonl path_to_raw_api_dump.json transformed_dump.jsonl
bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON faf.games transformed_dump.jsonl

# the output includes the schema in JSON format
bq show --format=prettyjson faf.games
```

## Constants

There are a few files to help resolve constant values into their in-game meaning (like that faction `1` is `UEF`, or that blueprint `ual0303` is a T3 [Harbinger](https://supcom.fandom.com/wiki/Aeon_T3_Heavy_Assault_Bot)). I've stored them in `functions.sql` which defines translation functions fixed views and a `.jsonl` file which can be loaded into a small `units` table.
