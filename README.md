# fafscrape

A set of utilities to scrape api.faforever.com. The intention is to reconstruct (part) of the [Forged Alliance Forver](http://faforver.com) database as a public BigQuery dataset.

The utilities are meant to run in one of two environments / mindsets:

* Manual / as CLI: meant to be used interactively by a human (i.e., to establish a historic baseline dataset)
* Automated / as webapp: meant to be invoked on schedule (i.e., to append daily diffs)
