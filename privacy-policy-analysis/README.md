# Privacy Policy Analysis (Crawler + Modified PoliCheck)

This directory has the code for privacy policy analysis.

We modified [PoliCheck](https://github.com/benandow/PrivacyPolicyAnalysis) to analyze privacy policies of Alexa skills.

## Dependency

Most of the code is in Python. We use conda to manage dependencies. To create a conda environment with dependencies installed, run:

```
$ conda create -c main -c conda-forge -n policheck 'spacy==2.0.16' networkx lxml pandas beautifulsoup4 html2text roman langdetect pdfminer pdfminer.six pyyaml selenium
```

Then activate the Python environment:

```
$ conda activate policheck
```

Some of the crawler code is in NodeJS. To use them, you need to setup NodeJS and `npm` command.

## Download Privacy Policies

Scripts used to download privacy policies are located in the `crawler` subdirectory. We developed them in around spring 2022. Please be note that, due to constantly evolving webpages, these scripts are likely needed to be updated to work now.

Change to the `crawler` subdirectory:

```
$ cd crawler/
```

Run `crawl-subgroup-top20.mjs` to download the Amazon pages of top 20 skills in each category:

```
$ npm install
$ ln -s ../../skill-interaction/subgrouped_skills.json .
$ node crawl-subgroup-top20.mjs
```

Run `extract_policy_urls.py` to extract Skill names and privacy policy URLs from downloaded Amazon pages:

```
$ python extract_policy_urls.py top50-skill-pages/
```

It will write the information of Skills that provide privacy policy URLs into `privacy_policy_urls.csv`. We provide the file that we generated in this repo.

Run `download_policies.py` to download privacy policy URLs:

```
$ python download_policies.py
```

It will download privacy policies as HTML files in the `policies` subdirectory, which will be input to PoliCheck.

## Extract Data Flows

Another input to PoliCheck is the list of data flows. To generate it, make sure you have `privacy_policy_urls.csv` from the previous step and `report.csv` from the network traffic analysis, then run `convert_avs_sdk_result_csv_to_policheck_flows.py`:

```
python3 convert_avs_sdk_result_csv_to_policheck_flows.py report.csv privacy_policy_urls.csv policheck_flows.csv
```

The output `policheck_flows.csv` will be read by PoliCheck.

## Run PoliCheck to Analyze Endpoints

We modified PoliCheck from both the [original version](https://github.com/benandow/PrivacyPolicyAnalysis) and [OVRseen version](https://github.com/UCI-Networking-Group/OVRseen/tree/main/privacy_policy) for endpoint analysis.

Create `ext/` folder and copy input files:

```
$ mkdir -p ext/data
$ cp -r ontology/alexa/*.{gml,xml,yml} ext/data/
$ cp policheck_flows.csv ext/data/
$ cp -r crawler/policies/ ext/html_policies/
```

Download the [NLP model](https://drive.google.com/file/d/1yMB3TJt8oZX3-GHm9oB_eKU7oeJXfLbA/view?usp=sharing) provided by PoliCheck authors and extract it:

```
$ tar xvf NlpFinalModel.tar.gz -C ext/
```

Run PoliCheck Preprocessor:

```
$ python code/Preprocessor.py -i ext/html_policies -o ext/plaintext_policies
```

Run PoliCheck:

```
$ python code/PatternExtractionNotebook.py ext/
$ python code/CollectFirstPartyNames.py ext/
$ python code/ConsistencyAnalysis-AlexaEndpoints.py ext/
$ python code/RemoveSameSentenceContradictions.py ext/
$ python code/DisclosureClassification.py ext/
```

The endpoint analysis result is in `policheck_results.csv`. Table 10 in our paper was based on it.