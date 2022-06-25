# fafdata

![Build Status](https://github.com/yaniv-aknin/fafdata/actions/workflows/test.yml/badge.svg?branch=main)

A set of data engineering utilities to ETL or ELT data from `api.faforever.com` and associated replays into BigQuery or similar platforms. The intention is to reconstruct (part) of the [Forged Alliance Forver](http://faforver.com) database as a public BigQuery dataset.

The utilities are meant to run in one of two environments / mindsets:

* As CLI used interactively by a human (i.e., to establish a historic baseline dataset)
* As webapp invoked on schedule (i.e., to append daily diffs)

## The dataset

Using these tools, I've scraped the API and created a dataset of all `game` models and some associated models (`player`, `gamePlayerStats`, `mapVersion`, etc).

[![Dashboard of resulting data](https://user-images.githubusercontent.com/101657/175792157-8cdea1bf-a01e-4a42-afb7-13aeb0b54dbb.png)][Datastudio Dashboard]

At the time of this writing, there are two publicly accessible ways to use the resulting data:

* A simple [Datastudio Dashboard]
* Publicly accessible BigQuery dataset
  * Try [pinning][pinning a project] the `fafalytics` project in Cloud Console
  * Try the query ``SELECT COUNT(id) FROM `fafalytics.faf_eu.games` WHERE DATE(startTime) = "2022-01-01"`` \
    (you might [pay][public query pricing] a tiny amount for this)

[Datastudio Dashboard]: https://datastudio.google.com/reporting/ad26e447-e1fd-4856-b7d0-78447dfcfde7
[pinning a project]: https://cloud.google.com/bigquery/docs/bigquery-web-ui#pinning_adding_a_project
[public query pricing]: https://cloud.google.com/bigquery/public-data#share_a_dataset_with_the_public


## The utilities

* `faf.extract`: Scrapes models from `api.faforver.com`, storing them as JSONs on disk.
* `faf.transform`: Transform extracted JSON files into JSONL files ready for loading to a data lake.
* `faf.parse`: Parses a downloaded `.fafreplay` file into a `.pickle`; this speeds up subsequent use of the replay.
* `faf.dump`: Dumps the content of a replay (raw `.fafreplay` or pre-parsed `.pickle`) into a JSONL file to be loaded.

For example, here's a plausible session using `faf.extract` and `faf.transform` to create a BigQuery table:
```ShellSession
(fafdata) $ faf.extract /tmp/game.d game
Scraping API  [####################################]  100%          
(fafdata) $ head /tmp/game.d/game0001.json 
{
    "data": [
        {
            "type": "game",
            "id": "17348476",
            "attributes": {
                "endTime": "2022-06-23T00:11:37Z",
                "name": "1v1 take my rating",
                "replayAvailable": true,
                "replayTicks": 6490,
                "replayUrl": "https://content.faforever.com/replays/0/17/34/84/17348476.fafreplay",
(fafdata) $ faf.transform /tmp/game.jsonl.d /tmp/game.d/game0*.json
Transforming  [####################################]  100%
(fafdata) $ head /tmp/game.jsonl.d/xformed.jsonl 
{"id": "17348476", "endTime": "2022-06-23 00:11:37", "name": "1v1 take my rating", [...]
[...]
(fafdata) $ bq load --source_format=NEWLINE_DELIMITED_JSON faf.game \
> /tmp/game.jsonl.d/xformed.jsonl bigquery/games.schema.json
[...]
(fafdata) $ 
```
## The webapp

Is still a work in progress and isn't yet finished/deployed (i.e., nothing updates the webapp automatically).

## Epilogue

This is a bit of a fork/rewrite of [fafalytics](https://github.com/yaniv-aknin/fafalytics), another project of mine with much larger scope (not just scrape the API, but also download and analyse the binary replay files). I now think it's better to approach this with three smaller scoped projects - one for data engineering, one for dataviz and analytics, and one for ML.
