# fafdata

![Build Status](https://github.com/yaniv-aknin/fafdata/actions/workflows/test.yml/badge.svg?branch=main)

A data engineering toolkit to extract metadata and replays from `api.faforever.com` and load it into a data lake like BigQuery. The intention is to reconstruct (part) of the [Forged Alliance Forver](http://faforver.com) database as a public BigQuery dataset.

The utilities are meant to run in one of two environments / mindsets:

* As CLI used interactively by a human (i.e., to establish a historic baseline dataset)
* As webapp invoked on schedule (i.e., to append daily diffs)

## The dataset

Using this toolkit, I've scraped the API and created a dataset of all `game` models and some associated models (`player`, `gamePlayerStats`, `mapVersion`, etc).

It lets you make stuff like this:
![Scatter plot panels](https://user-images.githubusercontent.com/101657/177016397-5a47fe4d-862a-489b-8610-3e28487ea06c.png)

At the time of this writing, there are three public ways to use this dataset:

* A simple [Datastudio Dashboard] for quick browsing
* A [Kaggle dataset] where I've flattened, filtered and documented two CSVs
* A publicly accessible BigQuery dataset for your own queries (← the good stuff is here)
  * Try the query ``SELECT COUNT(id) FROM `fafalytics.faf.games` WHERE DATE(startTime) = "2022-01-01"`` \
    (you might [pay][public query pricing] a tiny amount for this)
  * Try [pinning][pinning a project] the `fafalytics` project in Cloud Console

[Datastudio Dashboard]: https://datastudio.google.com/reporting/ad26e447-e1fd-4856-b7d0-78447dfcfde7
[Kaggle dataset]: https://www.kaggle.com/datasets/yanivaknin/fafdata
[pinning a project]: https://cloud.google.com/bigquery/docs/bigquery-web-ui#pinning_adding_a_project
[public query pricing]: https://cloud.google.com/bigquery/public-data#share_a_dataset_with_the_public


## The utilities

The tools includes utilities to extract, transform and load FAF metadata and replay data. Here's a demo session using `faf.extract` and `faf.transform` to create a BigQuery table:

[![from faforever to bigquery in 30s](https://asciinema.org/a/MYghLXpGbNIKwsnVDtCQOXoEO.svg)](https://asciinema.org/a/MYghLXpGbNIKwsnVDtCQOXoEO)

An overview of all utilities:

* `faf.extract`: Scrapes models from `api.faforver.com`, storing them as JSONs on disk.
* `faf.transform`: Transform extracted JSON files into JSONL files ready for loading to a data lake.
* `faf.parse`: Parses a downloaded `.fafreplay` file into a `.pickle`; this speeds up subsequent dumps of the replay.
* `faf.dump`: Dumps the content of a replay (raw `.fafreplay` or pre-parsed `.pickle`) into a JSONL file to be loaded to the lake.

## The webapp

The webapp is still a work in progress and isn't yet finished/deployed (i.e., nothing updates the dataset automatically).

## Epilogue

This is a bit of a fork/rewrite of [fafalytics](https://github.com/yaniv-aknin/fafalytics), another project of mine with much larger scope (not just scrape the API, but also download and analyse the binary replay files). I now think it's better to approach this with three smaller scoped projects - one for data engineering, one for dataviz and analytics, and one for ML.
