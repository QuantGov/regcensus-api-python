_The current version of RegCensusAPI is only compatible with Python 3.6 and newer._

# RegCensus API

## Introduction
RegCensusAPI is an API client that connects to the RegData regulatory restrictions data by the Mercatus Center at George Mason University. RegData uses machine learning algorithms to quantify the number of regulatory restrictions in a jurisdiction. Currently, RegData is available for three countries - Australia, Canada, and the United States. In addition, there are regulatory restrictions data for jurisdictions (provinces in Canada and states in Australia and US) within these countries. You can find out more about RegData from http://www.quantgov.org. 

This Python API client connects to the api located at at the [QuantGov website][1]. More advanced users who want to interact with the API directly can use the link above to pull data from the RegData API. R users can access the same features provided in this package in the R package __regcensusAPI__.

We put together a short video tutorial, showing some of the basics of the API library. You can view that [here][4].

## Installing and Importing __RegCensus__

The RegCensus Python library is pip installable:

```
$ pip install regcensus
```

Once installed, import the library, using the following (use the `rc` alias to more easily use the library):

```
import regcensus as rc
```

## Structure of the API

The API organizes data around __document types__, which are then divided into __series__. Within each series are __values__, which are the ultimate values of interest. Values are available by three sub-groups: agency, industry, and occupation. Presently, there are no series with occupation subgroup. However, these are available for future use. Document types broadly define the data available. For example, RegData for regulatory restrictions is falls under the broad document type "Regulatory Restrictions." Within Regulatory Restrictions document type, there are a number of series available. These include Total Restrictions, Total Wordcount, Total "Shall," etc.

A fundamental concept in RegData is the "document." In RegData, a set of documents represents a body of regulations for which we have produced regulatory restriction counts. For example, to produce data on regulatory restrictions imposed by the US Federal government, RegData uses the Code of Federal Regulations (CFR) as the source documents. Within the CFR, RegData identifies a unit of regulation as the title-part combination. The CFR is organized into 50 titles, and within each title are parts, which could have subparts, but not always. Under the parts are sections. Determining this unit of analyses is critical for the context of the data produced by RegData. Producing regulatory restriction data for US states follows the same strategy but uses the state-specific regulatory code.

In requesting data through the API, you must specify the document type and the indicate a preference for *summary* or *document-level*. By default, RegCensus API returns summarized data for the date of interest. This means that if you do not specify the *summary* preference, you will receive the summarized data for a date. The __get_series__ helper function (described below) returns the dates available for each series.

RegCensus API defines a number of dates depending on the series. For example, the total restrictions series of Federal regulations uses two main dates: daily and annual. The daily data produces the number of regulatory restrictions issued on a particular date by the US Federal government. The same data are available on an annual basis.

There are five helper functions to retrieve information about these key components of regdata. These functions provider the following information: document types, jurisdictions, series, agencies, and dates with data. The list functions begin with __list__.

Each document type comprises one or more *series*. The __list_series__ function returns the list of all series when no series id is provided. 

```
rc.list_series(jurisdictionID = 38)
```

Listing the jurisdictions is another great place to start. If you are looking for data for a specifc jurisdiction(s), this function
will return the jurisdiction_id for all jurisdiction, which is key for retrieving data on any individual jurisdiction.

The __get_series__ function returns a list of all series and the years with data available for each jurisdiction. 

The output from this function can serve as a reference for the valid values that can be passed to parameters in the __get_values__ function. The number of records returned is the unique combination of series and jurisdictions that are available in RegData. The function takes the optional argument jurisdiction id.

## Metadata
The __get_*__ functions return the details about RegData metadata. These metadata are not included in the __get_values__ functions that will be described later. 

### Jurisdictions 

Use the __get_jurisdiction__ function to return a data frame with all the jurisdictions. When you supply the jurisdiction ID parameter, the function returns the details of just that jurisdiction. Use the output from the __get_jurisdiction__ function to merge with data from the __get_values__ function.

```
rc.get_jurisdictions()
```

### Agencies

The __get_agencies__ function returns a data frame of agencies with data in RegData. Either the `jurisdictionID` or `keyword` arguments must be supplied. If `jurisdictionID` is passed, the data frame will include information for all agencies in that jurisdiction. If `keyword` is supplied, the data frame will include information for all agencies whose name contains the keyword.

The following code snippet will return data for all agencies in the Federal United States:

```
rc.get_agencies(jurisdiction = 38)
```

Likewise, this code snippet will return data for all agencies (in any jurisdiction) containing the word "education" (not case sensitive):

```
rc.get_agencies(keyword = 'education')
```

Use the value of the agency_id field when pulling values with the __get_values__ function.

### Industries

The __get_industries__ function returns a data frame of industries with data in the API. The available standards include the North American Industry Classification System (NAICS), the Bereau of Economic Analysis system (BEA), and the Standard Occupational Classification System (SOC). By default, the function only returns a data frame with 3-digit NAICS industries. The `codeLevel` and `standard` arguments can be used to select from other classifications.

The following line will get you industry information for all 4-digit NAICS industries:

```
rc.get_industries(codeLevel = 4)
```

This line will get you information for the BEA industries:

```
rc.get_industries(standard = 'BEA')
```

Like the __get_agencies__ function, the `keyword` argument may also be used. The following code snippet will return information for all 6-digit NAICS industries with the word "fishing" in the name:

```
rc.get_industries(keyword = 'fishing', codeLevel = 6)
```

### Documents

The __get_documents__ function returns a data frame with metadata for document-level data. The fucntion takes two parameters, jurisdictionID (required) and documentType (default value of 1, which is "all regulations").

The following line will get metadata for documents associated with U.S. Federal healthcare regulations.

```
rc.get_documents(jurisdictionID = 38, documentType = 3)
```

## Values

The __get_values__ function is the primary function for obtaining RegData from the RegCensus API. The function takes the following parameters:

* jurisdiction (required) - value or list of jurisdiction IDs
* series (required) - value or list of series IDs
* date (required) - value or list of years
* agency (optional) - value or list of agencies
* industry (optional) - value of list of agencies
* dateIsRange (optional) - specify if the list of years provided for the parameter years is a range. Default is True.
* filtered (optional) - specify if poorly-performing industry results should be excluded. Default is True.
* summary (optional) - specify if summary results should be returned, instead of document-level results. Default is True.
* country (optional) - specify if all values for a country's jurisdiction ID should be returned. Default is False.
* industryLevel (optional): level of NAICS industries to include. Default is 3.
* version (optional): Version ID for datasets with multiple versions, if no ID is given, API returns most recent version
* download (optional): if not False, a path location for a downloaded csv of the results.
* verbose (optional) - value specifying how much debugging information should be printed for each function call. Higher number specifies more information, default is 0.

In the example below, we are interested in the total number of restrictions and total number of words for the US (get_jurisdictions(38)) for the dates 2010 to 2019.

```
rc.get_values(series = [1,2], jurisdiction = 38, date = [2010, 2019])
```

### Get all Values for a Country

The `country` argument can be used to get all values for one or multiple series for a specific national jurisdiction. The following line will get you a summary of the national and state-level restriction counts for the United States from 2016 to 2019:

```
rc.get_values(series = 1, jurisdiction = 38, date = [2016, 2019], country=True)
```

### Values by Subgroup

You can obtain data for any of the three subgroups for each series - agencies, industries, and occupations (when they become available).

#### Values by Agencies

To obtain the restrictions for a specific agency (or agencies), the series id supplied must be in the list of available series by agency. To recap, the list of available series for an agency is available via the __list_series__ function, and the list of agencies with data is available via __get_agencies__ function.

```
# Identify all agencies
rc.list_agencies(jurisdictionID)

# Call the get_values() for this agency and series 91
rc.get_values(series = 91, jurisdiction = 38, date = [1990, 2018], agency = [81, 84])
```

#### Values by Agency and Industry

Some agency series may also have data by industry. For example, under the Total Restrictions topic, RegData includes the industry-relevant restrictions, which estimates the number of restrictions that apply to a given industry. These are available in both the main series - Total Restrictions, and the sub-group Restrictions by Agency. 

Valid values for industries include the industry codes specified in the classification system obtained by calling the __get_industries(jurisdiction)__ function.

In the example below, the series 92 (Restrictions by Agency and Industry), we can request data for the two industries 111 and 33 by the following code snippet.

```
rc.get_values(series = 92, jurisdiction = 38, time = [1990, 2000], industry = [111, 33], agency = 66)
```

### Document-Level Values

For most use-cases, our summary-level data will be enough. However, document-level data is also available, though most of these queries take much longer to return results. Multi-year and industry results for jurisdiction 38 will especially take a long time. If you want the full dataset for United States Federal, consider using our bulk downloads, available at the [QuantGov website][2].

We can request the same data from above, but at the document level, using the following code snippet.

```
rc.get_values(series = [1,2], jurisdiction = 38, date = ['2010-01-01', '2019-01-01'], summary=False)
```

Alternatively, we can use the  __get_document_values__ function as in the following code snippet.

```
rc.get_document_values(series = [1,2], jurisdiction = 38, date = ['2010-01-01', '2019-01-01'])
```

Note that for document-level queries, a full date (not just the year) is often required. See the __get_series__ function for specifics by jurisdiction.

### Version

_This currently applies to the RegData U.S. Annual project only._

As of version 0.2.4, a version parameter can be passed to the __get_values__ function to obtained data from past versions of data (currently only for the RegData U.S. Annual project). Available versions and their associated versionIDs can be obtained by using the __get_version__ function. If no version parameter is given, the most recent version will be returned. The following code snippet will return restrictions data for the 3.2 version of RegData U.S. Annual for the years 2010 to 2019.

```
rc.get_values(series = 1, jurisdiction = 38, date = [2010, 2019], version = 1)
```

### Merging with Metadata

To minimize the network bandwidth requirements to use RegCensusAPI, the data returned by __get_values__ function contain very minimal metadata. Once you pull the values by __get_values__, you can use the Pandas library to include the metadata.

Suppose we want to attach the agency names and other agency characteristics to the data from the last code snippet. First be sure to pull the list of agencies into a separate data frame. Then merge with the values data frame. The key for matching the data will be the *agency_id* column.

We can merge the agency data with the values data as in the code snippet below.

```
agencies = rc.get_agencies(jurisdictionID = 38)
agency_by_industry = rc.get_values(
    series = 92,
    jurisdiction = 38,
    time = [1990, 2000],
    industry = [111, 33],
    agency = [66, 111])
agency_restrictions_ind = agency_by_industry.merge(
    agencies, by='agency_id')
```

## Downloading Data

There are two different ways to download data retrieved from RegCensusAPI:

1. Use the pandas `df.to_csv(outpath)` function, which allows the user to download a csv of the data, with the given outpath. See the pandas [documentation][3] for more features.

2. As of version 0.2.0, the __get_values__ function includes a `download` argument, which allows the user to simply download a csv of the data in the same line as the API call. See below for an example of this call.

```
rc.get_values(series = [1,2], jurisdiction = 38, date = [2010, 2019], download='regdata2010to2019.csv')
```

[1]:https://api.quantgov.org/swagger-ui.html
[2]:https://www.quantgov.org/download-interactively
[3]:https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html
[4]:https://mercatus.wistia.com/medias/1hxnkfjnxa
