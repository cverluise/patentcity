<h1 align="center">patentCity
</h1>

<p align="center">
<img src="https://img.shields.io/badge/release-1.0.0rc5-yellow">
<a href="https://cverluise.github.io/patentcity/">
    <img src="https://img.shields.io/badge/website-online-brightgreen">
</a>
<img src="https://img.shields.io/badge/code-MIT-green">
<img src="https://img.shields.io/badge/data-CC%20BY%204.0-blue">
<img src="https://img.shields.io/badge/models-dvc-purple">
</p>

<p align="center">
<img src="https://img.shields.io/github/watchers/cverluise/patentcity?style=social">
<img src="https://img.shields.io/github/stars/cverluise/patentcity?style=social">
<img src="https://img.shields.io/github/forks/cverluise/patentcity?style=social">
</p>


***

🗃️ This repository is the codebase of the patentCity database.

📚 The patentCity database is a comprehensive database reporting patentees' data extracted from patent texts as well as enriched data since the 19th century in Germany (including East Germany), France, Great Britain and the USA.

💥 The goal of the database is to spur research on the history of innovation and to deepen the set of natural experiments from which historians, economists and scientists in general can learn to improve our understanding of innovation dynamics.

🌎 Explore and visualize the patentCity database online at [patentcity.xyz](http://patentcity.xyz) (click on the map under the "Explore" section).

📥 Download the patentCity database at [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi%3A10.7910%2FDVN%2FPG6THV&version=DRAFT) ([CC-BY-4](docs/LICENSE_DATA.md)).

📝 The patentCity codebase and database are documented at [doc.patentcity.xyz](http://doc.patentcity.xyz).

🤗 We open source our code ([MIT](docs/LICENSE_CODE.md)) to support future extensions, and a collaborative way to create and continuously improve research databases.

💌 patentCity is due to expand and improve continuously in the coming years. Make sure to receive updates, [join our newsletter](http://www.patentcity.xyz) and star the GitHub repository!

©️ patentCity is the backbone of [Bergeaud and Verluise (2021, work in progress)](./CITATION.bib). If you use the data or the codebase, make sure to cite the paper.


## Developer guide

### Installation and set-up

```shell script
# Clone repo
git clone https://github.com/cverluise/patentcity.git

# set up env/ install dependencies and CLI
cd patentcity/
poetry install
```

Install [poetry](https://python-poetry.org/) if needed.

```shell script
# get data & models (dev-only, access to gcp bucket needed)
dvc pull
```

Install [dvc](https://dvc.org/) if needed.

### API doc

The API doc is available at the [documentation website](https://cverluise.github.io/patentcity/) under the API section.

Overall, the API is thought to be versatile and to adapt to new documents seamlessly. The main functions are covered by the `patencity` CLI
