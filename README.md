# fafscrape

A set of utilities to scrape api.faforever.com. The intention is to reconstruct (part) of the [Forged Alliance Forver](http://faforver.com) database as a public BigQuery dataset.

The utilities are meant to run in one of two environments / mindsets:

* Manual / as CLI: meant to be used interactively by a human (i.e., to establish a historic baseline dataset)
* Automated / as webapp: meant to be invoked on schedule (i.e., to append daily diffs)

These utilities are a bit of a fork/complementary project to [fafalytics](https://github.com/yaniv-aknin/fafalytics), another project of mine with much larger scope (not just scrape the API, but also download and analyse the binary replay files). Hopefully I can make faster progress on _fafscrape_ and then decide how to reconcile the common functionality in the two projects.
