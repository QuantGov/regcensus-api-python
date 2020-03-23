# RegCensus API

## Introduction
RegCensusAPI is an API client that connects to the RegData regulatory restrictions data by the Mercatus Center at George Mason University. RegData uses machine learning algorithms to quantify the number of regulatory restrictions in a jurisdiction. Currently, RegData is available for three countries - Australia, Canada, and the United States. In addition, there are regulatory restrictions data for jurisdictions (provinces in Canada and states in Australia and US) within these countries. You can find out more about RegData from http://www.quantgov.org. 

This Python API client connects to the api located at at the [QuantGov website][1]. More advanced users who want to interact with the API directly can use the link above to pull data from the RegData API. R users can access the same features provided in this package in the R package __regcensusAPI__.

## Installing and Importing __RegCensus__

The RegCensus Python library is pip installable:

```
$ pip install regcensus
```

Once installed, import the library, using the following (using the `rc` alias to more easily use the library):

```
import regcensus as rc
```

## Structure of the API

The API organizes data around __topics__, which are then divided into __series__. Within each series are __values__, which are the ultimate values of interest. Values are available by three sub-groups: agency, industry, and occupation. Presently, there are no series with occupation subgroup. However, these are available for future use. Topics broadly define the data available. For example, RegData for regulatory restrictions is falls under the broad topic "Regulatory Restrictions." Within Regulatory Restrictions topic, there are a number of series available. These include Total Restrictions, Total Wordcount, Total "Shall," etc.

A fundamental concept in RegData is the "document." In RegData, a set of documents represents a body of regulations for which we have produced regulatory restriction counts. For example, to produce data on regulatory restrictions imposed by the US Federal government, RegData uses the Code of Federal Regulations (CFR) as the source documents. Within the CFR, RegData identifies a unit of regulation as the title-part combination. The CFR is organized into 50 titles, and within each title are parts, which could have subparts, but not always. Under the parts are sections. Determining this unit of analyses is critical for the context of the data produced by RegData. Producing regulatory restriction data for US states follows the same strategy but uses the state-specific regulatory code.

In requesting data through the API, you must specify the document type and the indicate a preference for *summary* or *document-level*. By default, RegCensus API returns summarized data for the period of interest. This means that if you do not specify the *summary* preference, you will receive the summarized data for a period. The __list_series_period__ helper function (described below) returns the periods available for each series.

RegCensus API defines a number of periods depending on the series. For example, the total restrictions series of Federal regulations uses two main periods: daily and annual. The daily data produces the number of regulatory restrictions issued on a particular date by the US Federal government. The same data are available on an annual basis.

There are six helper functions to retrieve information about these key components of regdata. These functions provider the following information: topics, documents, jurisdictions, series, agencies, and years with data. The list functions begin with __list__. For example, to view the list of topics call __list_topics__. When an topic id parameter is supplied, the function returns the details about a specific topic.

```
rc.list_document_subtype()
```

Each subtype comprises one or more *series*. The __list_series__ function returns the list of all series when no series id is provided. This call is a great place to start if you are looking for data based on a **topic** first. 


```
rc.list_jurisdictions(jurisdictionID = 38)
```
Just like the above function call, listing the jurisdictions is another great place to start. If you are looking for data for a specifc jurisdiction(s), this function
will return the jurisdiction_id for all jurisdiction, which is key for retrieving data on any individual jurisdiction.

The __get_periods__ function returns a list of all seriesa and the years with data available. 

The output from this function can serve as a reference for the valid values that can be passed to parameters in the __get_values__ function. The number of records returned is the unique combination of series and jurisdictions that are available in RegData. The function takes the optional argument jurisdiction id.

```
rc.get_periods(jurisdictionID = 38)
```

## Metadata
The __get_*__ functions return the details about RegData metadata. These metadata are not included in the __get_values__ functions that will be described later. 

### Jurisdictions 

Use the __get_jurisdiction__ function to return a data frame with all the jurisdictions. When you supply the jurisdiction ID parameter, the function returns the details of just that jurisdiction. Use the output from the __get_jurisdiction__ function to merge with data from the __get_values__ function.

```
rc.get_jurisdictions()
```

### Agencies

The __get_agencies__ function returns a data frame of all agencies with data in RegData. If an ID is supplied, the data frame returns the details about a single agency specified by the id. The data frame includes characteristics of the agencies. Currently, agency data are only available for federal RegData.

```
rc.get_agencies()
```

Use the value of the agency_id field when pulling values with the __get_values__ function.

### Industries

The __get_industries__ function returns a data frame of industries with data in the API. Presently the only classification system available is the North American Industry Classification System (NAICS). NAICS is used for both countries in North America and Australia, even the latter uses the Australia and New Zealand Standard Industrial Classification (ANZSIC) system. Presently, industry regulations for Australia are based on the NAICS. RegData expands to other countries, the industry codes will be country specific as well as contain mapping to the Standard Industry Codes (SIC) system.

```
rc.get_industries(38)
```

### Documents

The __get_documents__ function returns a data frame with metadata for document-level data. The fucntion takes two parameters, jurisdictionID (required) and documentType (default value of 3, which is "all regulations").

The following line will get metadata for documents associated with U.S. Federal healthcare regulations.

```
rc.get_documents(jurisdictionID = 38, documentType = 1)
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
* verbose (optional) - value specifying how much debugging information should be printed for each function call. Higher number specifies more information, default is 0.

In the example below, we are interested in the total number of restrictions and total numbe rof words (get_topics(1)) for the US (get_jurisdictions(38)) for the period 2010 to 2018.

```
rc.get_values(series = [1,2], jurisdiction = 38, date = [2010, 2018])
```

### Values by Subgroup

You can obtain data for any of the three subgroups for each series - agencies, industries, and occupations (when they become available).

#### Values by Agencies

To obtain the restrictions for a specific agency (or agencies), the series id supplied must be in the list of available series by agency. To recap, the list of available series for an agency is available via the __list_series(id,by='agency')__ function, and the list of agencies with data is available via __get_agencies__ function.

```
# Identify all agencies
rc.list_agencies()

# Call the get_values() for this agency and series 91
rc.get_values(series = 91, jurisdiction = 38, date = [1990, 2018], agency = [81, 84])
```

#### Values by Agency and Industry

Some agency series may also have data by industry. For example, under the Total Restrictions topic, RegData includes the industry-relevant restrictions, which estimates the number of restrictions that apply to a given industry. These are available in both the main series - Total Restrictions, and the sub-group Restrictions by Agency. 

To pull industry-relevant restrictions for an agency, call __get_agencies__ with the *industry* variable. The industry variable is of type string, and valid values include the industry codes specified in the classification system obtained by calling the __get_industries(jurisdiction)__ function.

In the example below, the series 92 (Restrictions by Agency and Industry), we can request data for the two industries 111 and 33 by the following code snippet.

```
rc.get_values(series = 92, jurisdiction = 38, , time = c(1990,2000), industry = c('111','33'), agency = 66)
```

### Merging with Metadata

To minimize the network bandwidth requirements to use RegCensusAPI, the data returned by __get_values__ functions contain very minimal metadata. Once you pull the values by __get_values__, you can use the Pandas library to include the metadata.

Suppose we want to attach the agency names and other agency characteristics to the data from the last code snippet. First be sure to pull the list of agencies into a separate data frame. Then merge with the values data frame. The key for matching the data will be the *agency_id* column.

We can merge the agency data with the values data as in the code snippet below.

```
agencies = rc.get_agencies()
agency_by_industry = rc.get_values(
    series = 92,
    jurisdiction = 38,
    time = [1990, 2000], 
    industry = [111, 33], 
    agency = [66, 111])
agency_restrictions_ind = agency_by_industry.merge(
    agencies, by='agency_id')
```

[1]:http://ec2-3-89-6-158.compute-1.amazonaws.com:8080/regdata/swagger-ui.html
