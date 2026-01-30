# Operational Excellence

## Definition

𝑂𝐸 𝑆𝑐𝑜𝑟𝑒 = sum from i=1 to |l| of (wi * si)

Wherein 𝐿 = {𝑚1, 𝑚2, … }is the list of metrics defined in Section 5.2, 𝑠i represents the score of the
entity for metric 𝑚i,and 𝑤i represents the weight of that metric. The rationale for introducing weights
in the calculation is to administer the role of the metrics 

## Weights
### How many metrics are targeted for the third round/year of the assessment, and what were their weights?
For the third round, 13 metrics are targeted which are listed below along with their weights:

Metric ID Metric Name Platform
Metric
Weight
DSI.OE.02 Systems integrated with NDL NDL 0.20
DO.OE.03 Responsiveness of the integration solution with NDL NDL 0.05
DQ.OE.02 Conformance to data standards in NDL NDL 0.05
DO.OE.02 Responsiveness of GSB API calls GSB 0.10
DSI.OE.01 Adherence to the Data Sharing Policy GSB 0.05
RMD.OE.01 Publishing reference entities RDP 0.10
OD.OE.01 Datasets published in ODP ODP 0.15
OD.OE.05 Response effectiveness to new open dataset requests ODP 0.05
MCM.OE.01 Systems cataloged in NDC NDC 0.05
MCM.OE.02 Business attributes defined and linked in NDC NDC 0.05
MCM.OE.03 Reporting assets defined in NDC NDC 0.05
DSI.OE.05 Attributes Availability for Correction in Tawakkalna Tawakkalna 0.05
DQ.OE.03 Attributes published in Tawakkalna Tawakkalna 0.05

### What does it signify when a metric is marked as “NA”(‘Not Applicable’)for an entity, and how is the overall result subsequently calculated? 
If a metric is marked as “NA,” it indicates that the entity is exempted from evaluation on that
particular metric for the current assessment round. Consequently, the overall weight distribution will
be recalibrated, reallocating the weights of the excluded metrics proportionally across the remaining
applicable ones, thereby increasing their individual weights. For example, given the original metrics
and their weightsshown in the previous table, assuming DO.OE.02and DSI.OE.01aremarked as “NA”,
the adjusted weights after redistribution will be:


Metric ID Metric Name Platform
Metric
Weight
DSI.OE.02 Systems integrated with NDL NDL 0.24
DO.OE.03 Responsiveness of the integration solution with NDL NDL 0.06
DQ.OE.02 Conformance to data standards in NDL NDL 0.06
RMD.OE.01 Publishing reference entities RDP 0.12
OD.OE.01 Datasets published in ODP ODP 0.18
OD.OE.05 Response effectiveness to new open dataset requests ODP 0.06
MCM.OE.01 Systems cataloged in NDC NDC 0.06
MCM.OE.02 Business attributes defined and linked in NDC NDC 0.06
MCM.OE.03 Reporting assets defined in NDC NDC 0.06
DSI.OE.05 Attributes availability for correction in Tawakkalna Tawakkalna 0.06
DQ.OE.03 Attributes published in Tawakkalna Tawakkalna 0.06

This adjustment ensures that the total weight of all metrics remains one and that the entity is only
evaluated on applicable metrics.

### What are the weights associated for the two evaluation criteria: Number of certified attributes and the API classification?
The weight of the first criteria is 0.8 whereas the weight of the second one is 0.2 respectively.

### Please show an example of how the metric is calculated.

Suppose an entity has published three APIs on the GSB and the details of these APIs, such as their
attribute count, the number of their certified attributes (i.e., attributes where the publisher is the
same as the source/authorized entity), and their classification status are as shown in the table below.
API Version
Number of API
Attributes
Number of Certified
Attributes
API Classification
Complete?
API 1 1 70 68 Yes
API 2 3 30 25 Yes
API 3 1 20 17 No
Based on the status above, the metric score is calculated as follows:
• Adherence of API 1= ((68 / 70 * 0.8) + (1 * 0.2)) * 100 = 97.7%
• Adherence of API 2= ((25 / 30 * 0.8) + (1 * 0.2)) * 100 = 86.6%
• Adherence of API 3 = ((17 / 20 * 0.8) + (0 * 0.2)) * 100 = 68.0%
Then, the adherence score for the entity is calculated as the average adherence score for the APIs as
follows = (97.7% + 86.6% + 68.0%) ÷ 3 = 84.1%
Scale Interval = Good


4.1.2.Metric (DSI.OE.02): Systems integrated with NDL
This metric reflects the share of systems fully integrated with the National Data Lake (NDL), based on
requests from the NDL team. Integration counts only if all requirements (e.g., currency of data and
adherence to the integration method)are met, ensuring the data is usableand reliable.


## Metric Structure
The metric structure consists of several elements discussed in the table below.
ID Element Name Description
1 Metric ID A unique identifier of the metric using the following format
[DomainID.OE.NUMBER] where NUMBER is an ordering number of the
metric within the NDMO domain and OE. For example, MCM.OE.01 is the
first OE metric within the Data Catalog and Metadata domain of NDMO
2 Metric Name The name of the metric, e.g., response time of GSB APIs
3 Metric Description A high-level description with a detailed explanation and rationale for the
metric
4 Domain Name The name of the NDMO domain, e.g., Data Catalog and Metadata (MCM)
5 Data Platforms The name of the national data platforms that will support the metric
calculation
6 Definitions The constituents of each metric required to calculate the output of the
metric
7 Calculation The process that transforms the metric’s constituents into one output value
using a predefined equation
8 Measurement Unit The definite magnitude of the metric output
9 Acceptable Threshold The acceptable value beyond which the metric output will not be
acceptable
10 Scale Intervals The intervals that correspond to the unified scale levels
11 Version History The version history allowing versioning control of changes following the
release of the document
12 Dependencies The prerequisites for calculating the metric output

## List of Metrics

### Data Sharing and Interoperability (DSI)

#### Adherence to the Data Sharing Policy - DSI.OE.01
Element Name Element Details
Metric ID DSI.OE.01
Metric Name Adherence to the Data Sharing Policy
Metric Description This metric assesses the adherence of the entity’s GSB APIs to the Data Sharing Policy
according to two main criterions. For each API, the first criterion measures the
percentage of the API attributes where the publisher is the source/authorized entity
(as defined in NDC) against the total number of the API attributes, whereas the
second criterion checks the existence of the API classification.We use the term certified attributes to refer to the attributes where the publisher is
the source/authorized entity.
This metric helps in achieving the required governance on data sharing and
interoperability and ensures that only source/authorized entity can share the data
on GSB, hence improving the quality of data in Saudi Arabia.
Domain Name Data Sharing and Interoperability (DSI)
Data Platforms Government Service Bus (GSB) and National Data Catalog (NDC)
Definitions • Number of API certified attributes
• Total number of API attributes
Calculation = Average adherence score for all entity’s APIs, where the adherence score of one API
is calculated as follows:
= (w1 * Number of the API certified attributes / Total number of API attributes + w2 *
c) * 100
where w1 is the weight assigned to first criterion, w2 is the weight assigned to second
criterion, and c is 1 if the API is classified or 0 otherwise.
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies

#### Systems integrated with NDL - DSI.OE.02
Element Name Element Details
Metric ID DSI.OE.02
Metric Name Systems integrated with NDL
Metric Description This metric measures the percentage of systems shared by the entity with the
National Data Lake (NDL) against the total number of the entity’s systems requested
by the NDL team. Note that a system will be considered integrated only if all required
dimensions of its data are fully sourced to NDL.
This metric aims to accelerate the efforts to enrich NDL with high-value and widespectrum data assets generated by various government entities. It also helps in achieving the goal of making NDL the unified single source of truth for analytical data assets. 
Domain Name Data Sharing and Interoperability (DSI)
Data Platforms National Data Lake (NDL)
Definitions • Number of systems integrated with NDL by the entity
• Total number of the entity’s systems requested by NDL
Calculation = Number of systems integrated with NDL by the entity / Total number of the
entity’s systems requested by NDL * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies

#### Data sharing agreement processing - DSI.OE.03
Element Name Element Details
Metric ID DSI.OE.03
Metric Name Data sharing agreement processing
Metric Description This metric measures the amount of time taken by the data producer to process the
data sharing requests raised by the consumer entities. This metric considers the time
taken for either approving or rejecting the requests as part of the processing time.
This metric aims to improve data sharing and accessibility by optimizing the overall
data sharing agreement approval lifecycle. It also helps accelerate data consumption
by lowering the barriers to accessing the data required for decision-making and
insight generation.
Domain Name Data Sharing and Interoperability (DSI)
Data Platforms Data Marketplace (DMP)
Definitions • Time taken by the data producer entity to approve or reject all received data
sharing agreements (in days)
• Total number of data sharing agreements received by the producer entity
Calculation = Time taken by the data producer entity to approve or reject all received data
sharing agreements (in days) / Total number of data sharing agreements received by
the producer entity
Measurement Unit Days
Acceptable Threshold 10 Days
Scale Intervals Unacceptable: > 10 days
Low: (8 days, 10 days]
Fair: (6 days, 8 days]
Good: (4 days, 6 days]
Excellent: (2 days, 4 days]
Leader: <= 2 days
Version History
Dependencies

#### Published APIs on GSB - DSI.OE.04
Element Name Element Details
Metric ID DSI.OE.04
Metric Name Published APIs on GSB
Metric Description This metric measures the percentage of APIs published by the entity on GSB against
the total number of APIs required to be published by the entity. Note that an API will
be considered published only if all required requirements are fully implemented in
GSB.
This metric aims to accelerate the efforts to enrich GSB and achieve the goal of
making GSB the unified single source of truth for operational data assets.
Domain Name Data Sharing and Interoperability (DSI)
Data Platforms Government Service Bus (GSB)
Definitions • Number of APIs published on GSB by the entity
• Total number of APIs required to be published on GSB by the entity
Calculation = Number of APIs published on GSB by the entity / Total number of APIs required to
be published on GSB by the entity * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies The total number of APIs to be published by each entity will be determined based on
the size and nature of the business of that entity

#### Attributes published in Tawakkalna - DSI.OE.05
Element Name Element Details
Metric ID DSI.OE.05
Metric Name Attributes published in Tawakkalna
Metric Description This metric measures the percentage of attributes published by the entity on the
‘Personal’ page in Tawakkalna, under the relevant sections (Info, Cards, or Docs)
depending on the attribute typeagainst the total number of attributes required to be
published by the entity on the ‘Personal’ page in Tawakkalna.
This metric aims to accelerate the efforts in enriching Tawakkalna with
comprehensive and diverse user attributes published by various government
entities, and also seeks to strengthen the platform’s role as the unified reference for
government services and data.
Domain Name Data Sharing and Interoperability (DSI)
Data Platforms National Super App (Tawakkalna)
Definitions • Number of attributes published by the entity on the ‘Personal’ page in
Tawakkalna, under the relevant sections
• Total number of attributes required to be published by the entity on the
‘Personal’ page in Tawakkalna, under the relevant sections
Calculation = Number of attributes published by the entity on the ‘Personal’ page in
Tawakkalna, under the relevant sections / Total number of attributes required to be
published by the entity on the ‘Personal’ page in Tawakkalna, under the relevant
sections * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies The total number of attributes to be published by each entity will be determined
based on the size and nature of the business of that entity.

### Open Data (OD)

#### Datasets published in ODP - OD.OE.01

Element Name Element Details
Metric ID OD.OE.01
Metric Name Datasets published in ODP
Metric Description This metric measures the percentage of datasets published by the entity in ODP
against the total number of datasets required to be published in ODP by the entity.
This metric aims to expedite the efforts in enriching ODP with high-impact and
wide-spectrum open datasets generated by various government entities. It also aims
to increase the contribution of the platform towards the development of innovative
services, applications, and new business ideas.
Domain Name Open Data (OD)
Data Platforms Open Data Platform (ODP)
Definitions • Number of datasets published in ODP by the entity
• Total number of datasets required to be published in ODP by the entity
Calculation = Number of datasets published in ODP by the entity / Total number of datasets
required to be published in ODP by the entity * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies The total number of open datasets to be published by each entity will be
determined based on the size and nature of the business of that entity.

####  Delay/Lag in refreshing open datasets - OD.OE.02

Element Name Element Details
Metric ID OD.OE.02
Metric Name Delay/Lag in refreshing open datasets
Metric Description This metric measures the delay in refreshing the published datasets in ODP by the
entity. It helps entities adhere to the refresh schedule (update frequency) for the
published datasets.
The prime focus of this metric is to improve data freshness by ensuring that datasets
are updated according to the expected update frequency. This helps in providing data
consumers with the most up-to-date data for various forms of consumption.
Domain Name Open Data (OD)
Data Platforms Open Data Platform (ODP)
Definitions • Delay in refreshing a dataset (in days) by the entity according to the update
frequency of the dataset
• Update frequency of the dataset (in days)
• Total number of datasets that have been published in ODP by the entity
Calculation = Average delay percentage for all the entity’s datasets, where the delay percentage
of one dataset is calculated as:
= Sum of the delay in refreshing the dataset (in days) by the entity according to its
update frequency / (number of expected refreshes * update frequency of the
dataset) * 100
Measurement Unit Percentage
Acceptable Threshold 10%
Scale Intervals Unacceptable: > 10%
Low: (8%, 10%]
Fair: (6%, 8%]
Good: (4%, 6%]
Excellent: (2%, 4%]
Leader: <= 2%
Version History
Dependencies

#### Reported issues for the published datasets - OD.OE.03
Element Name Element Details
Metric ID OD.OE.03
Metric Name Reported issues for the published datasets
Metric Description This metric measures the average number of issues reported by the end users on the
entity’s published datasets in ODP.
This metric aims to improve the overall quality of published datasets,given theirfarreaching impact on the services, research, applications, and business models
developed on top of them.
Domain Name Open Data (OD)
Data Platforms Open Data Platform (ODP)
Definitions • Number of issues reported on the entity’s published datasets in ODP
• Total number of datasets published in ODP by the entity
Calculation = Number of issues reported on the entity’s published datasets in ODP / Total
number of datasets published in ODP by the entity
Measurement Unit Number of issues
Acceptable Threshold 5
Scale Intervals Unacceptable: > 5
Low: (4, 5]
Fair: (3, 4]
Good: (2, 3]
Excellent: (1, 2]
Leader: <= 1
Version History
Dependencies

#### Delay in resolving reported issues on published datasets - OD.OE.04
Element Name Element Details
Metric ID OD.OE.04
Metric Name Delay in resolving reported issues on published datasets
Metric Description This metric measures the delay in resolving the issues reported on the entity’s
published datasets in ODP.
This metric aims to optimize the time for remediating the reported issues as the
affected datasets have a far-reaching impact on the services, research, applications,
and business models developed on top of them.
Domain Name Open Data (OD)
Data Platforms Open Data Platform (ODP)
Definitions • Time taken by the entity to resolve an issue reported on a dataset (in days)
• Expected resolution time (in days)
Calculation = Average delay percentage for fixing all the issues reported on the entity’s
datasets, where the delay percentage associated with one issue is calculated as:
= (Time taken by the entity to resolve an issue reported on a dataset – Expected
resolution time of that issue) / Expected resolution time of that issue * 100
Measurement Unit Percentage
Acceptable Threshold 10%
Scale Intervals Unacceptable: > 10%
Low: (8%, 10%]
Fair: (6%, 8%]
Good: (4%, 6%]
Excellent: (2%, 4%]
Leader: <= 2%
Version History
Dependencies Issues on ODP will be categorized based on their expected resolution time.

#### Response effectiveness to new open dataset requests - OD.OE.05
Element Name Element Details
Metric Name Response effectiveness to new open dataset requests
Metric Description This metric measures the time taken to process the new open dataset requests raised
to the entity on ODP. Note that a request process should result in either publishing
the requested dataset on ODP or rejecting it in case of the unavailability of data at
the entity, with the reasoning and justification.
This metric measures the entity’s responsiveness and efficiency in addressing user
data requests, aiming to improve the overall user satisfaction and enrich the
platform with high-impact and wide-spectrum open datasets.
Domain Name Open Data (OD)
Data Platforms Open Data Platform (ODP)
Definitions • Time taken by the entity to process the request (in days)
• Expected processing time (in days)
Calculation = Average effectiveness for all the entity’s requests, where the effectiveness of one
request is calculated as:
= (1 – ((Time taken by the entity to process the request – Expected processing time) /
Expected processing time)) * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies Expected processing time for different levels of request complexity will be
determined by NDMO. 

### Data Catalog and Metadata (MCM)

#### Systems cataloged in NDC - MCM.OE.01

Element Name Element Details
Metric ID MCM.OE.01
Metric Name Systems cataloged in NDC
Metric Description This metric measures the percentage of systems cataloged by the entity in NDC
against the total number of the entity’s critical systems. Note that a system is
considered cataloged if its technical metadata is fully scanned and uploaded to NDC.
This metric aims to accelerate the documentation of national data assets, allowing
consumers to explore the business context of those assets with appropriate technical
details, and improving data accessibility and discovery.
Domain Name Data Catalog and Metadata (MCM)
Data Platforms National Data Catalog (NDC)
Definitions • Number of critical systems that have been cataloged in NDC by the entity
• Total number of the entity’s critical systems
Calculation = Number of critical systems that have been cataloged in NDC by the entity / Total
number of the entity’s critical systems * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies The number of critical systems that need to be cataloged by the entity will be
determined based on the size and nature of the business of that entity

#### Business attributes defined and linked in NDC - MCM.OE.02
Element Name Element Details
Metric ID MCM.OE.02
Metric Name Business attributes defined and linked in NDC
Metric Description This metric measures the percentage of business attributes that are defined and
linked by the entity to technical columns in NDC against the total number of business
attributes that the entity is required to define in NDC.
This metric aims to accelerate the documentation of national data assets, allowing
consumers to explore the business context of those assets with appropriate technical
details, improving data accessibility and discovery.
Domain Name Data Catalog and Metadata (MCM)
Data Platforms National Data Catalog (NDC)
Definitions • Number of system business attributes defined and linked by the entity to
technical columns in NDC
• Total number of system business attributes required to be defined by the entity
Calculation = Average scorefor all the entity’s systems, where the score of one system is
calculated as:
= Number of system business attributes defined and linked by the entity to
technical columns in NDC / Total number of system business attributes required to
be defined by the entity * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies The total count of required business attributes for a system is determined based on
the quantity and complexity of the business functions implemented in that system.

#### Reporting assets defined in NDC - MCM.OE.03
Element Name Element Details
Metric ID MCM.OE.03
Metric Name Reporting assets defined in NDC
Metric Description This metric measures the percentage of reporting assets (KPIs/metrics) that are
defined in NDC by the entity against the total number of reporting assets that the
entity is required to document in NDC.
This metric helps in documenting the important analytics assets that will be made
discoverable for other consumers to leverage for their analysis and decision-making.
This, in turn, promotes the reusability of those authentic and verified assets to
reduce the time to market for consumers.
Domain Name Data Catalog and Metadata (MCM)
Data Platforms National Data Catalog (NDC)
Definitions • Number of reporting assets defined in NDC by entity
• Total number of required reporting assets to be defined in NDC by entity
Calculation = Number of reporting assets defined in NDC by the entity / Total number of
required reporting assets to be defined in NDC by the entity * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies The total number of required reporting assets to be defined is determined upon
onboarding the entity to NDC based on its size and the number of its critical systems.


#### Business attributes linked to attribute class standards in NDC - MCM.OE.04
Element Name Element Details
Metric ID MCM.OE.04
Metric Name Business attributes linked to attribute class standards in NDC
Metric Description This metric measures the percentage of business attributes linked to attribute class
standards in NDC by the entity against the total number of business attributes that
are defined by that entity.
This metric aims to accelerate the efforts for standardizing national data assets,
improving the overall quality of data. It will ultimately help in achieving seamless
data sharing and interoperability with full trust across business processes,
applications, and systems.
Domain Name Data Catalog and Metadata (MCM)
Data Platforms National Data Catalog (NDC)
Definitions • Number of business attributes linked to attribute class standards in NDC by the
entity
• Total number of business attributes defined in NDC by the entity
Calculation = Number of business attributes linked to attribute class standards in NDC by the
entity / Total number of business attributes defined in NDC by the entity * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies

#### Accuracy of business attribute relationships in NDC - MCM.OE.05
Element Name Element Details
Metric ID MCM.OE.05
Metric Name Accuracy of business attribute relationships in NDC
Metric Description This metric measures the percentage of issues reported on the business attributes
that are incorrectly linked to other metadata objects in NDC (e.g., business attributes
linked to incorrect attribute class standards, incorrect technical columns, or
incorrect measures).
This metric aims to enhance the accuracy of the metadata, which in turn increases
the quality and reliability of consumer analyses and decision-making.
Domain Name Data Catalog and Metadata (MCM)
Data Platforms National Data Catalog (NDC)
Definitions • Number of incorrectly linked business attributes defined in NDC by the entity
• Total number of business attributes defined in NDC by the entity
Calculation = Number of business attributes incorrectly linked by the entity in NDC / Total
number of business attributes defined in NDC by the entity * 100
Measurement Unit Percentage
Acceptable Threshold 10%
Scale Intervals Unacceptable: > 10%
Low: (8%, 10%]
Fair: (6%, 8%]
Good: (4%,6%]
Excellent: (2%, 4%]
Leader: <= 4%
Version History
Dependencies

### Reference and Master Data Management (RMD)

#### Publishing reference entities - RMD.OE.01

Element Name Element Details
Metric ID RMD.OE.01
Metric Name Publishing reference entities
Metric Description This metric measures the percentage of standardized reference entities (tables) that
are published by the entity on the GSB against the number of reference entities
(produced by that entity) that are required by government entitiesto perform their
business functions.
This metric aims to accelerate the standardization of reference values, which is
required by different business processes for trusted reference data interoperability.
Domain Name Reference and Master Data Management (RMD)
Data Platforms Government Service Bus (GSB) and Reference Data Management Platform (RDP)
Definitions • Number of published reference entities by the entity on GSB
• Total number of reference entities that are expected to be published by the
entity
Calculation = Number of published reference entities by the entity on GSB / Total number of
reference entities that are expected to be published by the entity * 100
Measurement Unit Percentage
Acceptable Threshold 90%
Scale Intervals Unacceptable: <= 90%
Low: (90%, 92%]
Fair: (92%, 94%]
Good: (94%, 96%]
Excellent: (96%, 98%]
Leader: > 98%
Version History
Dependencies

#### Time taken to publish new reference entities - RMD.OE.02
Element Name Element Details
Metric ID RMD.OE.02
Metric Name Time taken to publish new reference entities
Metric Description This metric measures the average time it takes for the entity to publish new
reference entities requested by other entities on GSB.
This metric aims to improve the overall availability of reference values, fostering
agility for building accurate business services, analysis, and reference data
interoperability.
Domain Name Reference and Master Data Management (RMD)
Data Platforms Government Service Bus (GSB) and Reference Data Management Platform (RDP)
Definitions • Total time taken by the entity to publish a reference entity on GSB (in days)
• Total number of reference entities that are published by the entity
Calculation = Sum of total time taken by the entity to publish its reference entities on GSB (in
days) / Total number of reference entities that are published by the entity
Measurement Unit Days
Acceptable Threshold 30 Days
Scale Intervals Unacceptable: > 30 days
Low: (25 days, 30 days]
Fair: (20 days, 25 days]
Good: (15 days, 20 days]
Excellent: (10 days, 15 days]
Leader: <= 10 days
Version History
Dependencies

#### Time taken to fix reported issues in reference entities - RMD.OE.03
Element Name Element Details
Metric ID RMD.OE.03
Metric Name Time taken to fix reported issues in reference entities
Metric Description This metric measures the average time it takes for the entity to resolve an issue
reported on its reference entities that are published on GSB.
This metric aims to minimize and contain data quality issues across government
systems and applications. It also helps maintain the quality of the outcomes
pertaining to analyses, business processes, and data interoperability,as incorrect or
missing reference values will negatively impact consumer experience and trust.
Domain Name Reference and Master Data Management (RMD)
Data Platforms Government Service Bus (GSB) and Reference Data Management Platform (RDP)
Definitions • Time taken by the entity to resolve a reported issue related to its reference
entities (in days)
• Total number of reported issues related to the entity’s reference entities
published on GSB
Calculation = Sum of time taken by the entity to resolve a reported issue related to its reference
entities (in days) / Total number of reported issues related to the entity’s reference
entities published on GSB
Measurement Unit Days
Acceptable Threshold 5 Days
Scale Intervals Unacceptable: > 5 days
Low: (4 days, 5 days]
Fair: (3 days, 4 days]
Good: (2 days, 3 days]
Excellent: (1 days, 2 days]
Leader: <= 1 day
Version History
Dependencies

### Data Quality (DQ)

#### Data Quality (DQ) index in GSB - DQ.OE.01
Element Name Element Details
Metric ID DQ.OE.01
Metric Name Data Quality (DQ) index in GSB
Metric Description This metric calculatesthe average DQ index of the entity’s data that is shared on GSB
by applying DQ rules that span across the various DQ dimensions on all of the entity’s
GSB attributes.
Note that DQ rules and attributes have a many-to-many relationship. That is, a DQ
rule can be applied to more than one attribute and there can be more than one rule
associated with the same attribute. The notation “Rule, Attribute” will be used to
refer to a pair of DQ rulesapplied to an attribute.
A record is considered clean with regards to a DQ rule only if the attribute on which
the DQ rule is applied passes the logic implemented within that rule.
This metric aims to improve the quality of the data required for business process
integration and ensure trust and seamless interoperability of data in Saudi Arabia.
Domain Name Data Quality (DQ)
Data Platforms Government Service Bus (GSB)
Definitions • Total number of clean records for an attribute checked by a DQ rule
• Total number of records checked by the DQ rule
Calculation “Attribute, Rule” index = (Total number of clean records for the attribute checked by
the DQ rule / Total number of records checked by the DQ rule) * 100
The “Attribute, Rule” index is subsequently rolled up using weightages applied to
both attributes and DQ rules to calculate the DQ index of the entity.
Measurement Unit Percentage
Acceptable Threshold 90%
Scale Intervals Unacceptable: <= 90%
Low: (90%, 92%]
Fair: (92%, 94%]
Good: (94%, 96%]
Excellent: (96%, 98%]
Leader: > 98%
Version History
Dependencies

#### Conformance to data standards in NDL - DQ.OE.02
Element Name Element Details
Metric ID DQ.OE.02
Metric Name Conformance to data standards in NDL
Metric Description This metric calculates the conformance value of the entity’s data that is integrated in
NDL by applying DQ rules that measure the degree of conformity of that data against
the data standards published in the National Data Catalog (NDC). Entities have a large
number of attributes integrated in NDL. However, only a sample of these attributes
will be considered in the calculation of this index.
Note that a DQ rule can be applied to more than one attribute. The notation “Rule,
Attribute” will be used to refer to a pair of DQ rulesapplied to an attribute.
A record is considered clean with regards to a DQ rule if the attribute on which the
DQ rule is applied passes the logic implemented within that rule.
This metric aims to improve the quality of the data within NDL, providingconsumers
with high-fidelity data for their decision-making needs. It also supports identifying
and prioritizing the key areas of focus for improving the overall quality of national
data assets.
Domain Name Data Quality (DQ)
Data Platforms National Data Lake (NDL)
Definitions • Total number of clean records for an attribute checked by a DQ rule
• Total number of records checked by the DQ rule
Calculation “Attribute, Rule” index = (Total number of clean records for the attribute checked by
the DQ rule / Total number of records checked by the DQ rule) * 100
The score for one system is calculated by rolling up the “Attribute, Rule” index scores
for all the system’s attributes using weightages applied to both attributes and DQ
rules.
The final score for the entity is the average score of all the entity’s systems.
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies

#### Attributes Availability for Correction in Tawakkalna - DQ.OE.03
Element Name Element Details
Metric ID DQ.OE.03
Metric Name Attributes Availability for Correction in Tawakkalna
Metric Description This metric measures the percentage of user attributes published by the entity on the
‘Personal’ page in Tawakkalna under the respective sections that can be corrected
through the platform, relative to the total number of attributes eligible for
correction.
The objective of this metric is to enhance data accuracy and user control by
enabling individuals to correct their personal information through a unified,
secure, and user-friendly interface. It supports the broader goal of improving
service quality and advancing the digital transformation by promoting transparent
and user-centric data management.
Domain Name Data Quality (DQ)
Data Platforms National Super App (Tawakkalna)
Definitions • Number of attributes made available by the entity for correction on the
‘Personal’ page in Tawakkalna, under the relevant sections
• Total number of the entity’s attributes eligible forcorrection on the ‘Personal’
page in Tawakkalna, under the relevant sections
Calculation = Number of attributes made available by the entity for correction on the ‘Personal’
page in Tawakkalna, under the relevant sections / Total number of the entity’s
attributes eligible for correction on the ‘Personal’ page in Tawakkalna, under the
relevant sections * 100
Measurement Unit Percentage
Acceptable Threshold 70%
Scale Intervals Unacceptable: ≤ 70%
Low: (70%, 75%]
Fair: (75%, 80%]
Good: (80%, 85%]
Excellent: (85%, 90%]
Leader: > 90%
Version History
Dependencies The total number of attributes eligible forcorrection by each entity will be
determined based on the size and nature of the business of that entity

### Data Operations (DO) 

#### Delay in response time of GSB APIs - DO.OE.01
Element Name Element Details
Metric ID DO.OE.01
Metric Name Delay in response time of GSB APIs
Metric Description This metric measures the delay in the response time of the entity’s GSB APIs after
subtracting the time taken by the GSB platform. This metric only considers the actual
processing time incurred by the entity after receiving a request from the consumer.
This metric aims to improve business process integration and interoperability, and
hence enhance the consumer experience and application resilience.
Domain Name Data Operations (DO)
Data Platforms Government Service Bus (GSB)
Definitions • Response time of an API, which is the amount of time (in milliseconds) taken
by the API to process a request and generate a response
• Expected response time of the API (in milliseconds)
• Number of calls for an API
Calculation = Average delay percentage for all the entity’s APIs, where the delay percentage of
one API is calculated as:
= Sum of delay in response time of all API’s calls / (Number of calls for an API *
expected response time of the API) * 100
where the delay in response time of an API call is calculated as follows:
= Response time of the API – GSB latency – expected response time of the API
Measurement Unit Percentage
Acceptable Threshold 10%
Scale Intervals Unacceptable: > 10%
Low: (8%, 10%]
Fair: (6%, 8%]
Good: (4%, 6%]
Excellent: (2%, 4%]
Leader: <= 2%
Version History
Dependencies The expected response time of an API will be determined based on its processing
complexity and payload size. Prior to measuring this metric, all APIs of each entity
will need to be categorized into a defined set of categories in order to determine their
expected response time. 

#### Responsiveness of GSB API calls - DO.OE.02
Element Name Element Details
Metric ID DO.OE.02
Metric Name Responsiveness of GSB API calls
Metric Description This metric measuresthe responsiveness of the entity APIs that are published on GSB
by calculating the percentage of failed API calls invoked by the consumer
applications on the APIsagainst the total number of API calls. Note that a failed API
call refers to the scenario where the consumer application receives an error of any
type from the called API.
This metric aims to improve the resilience of GSB APIs, hence increasing the
efficiency of business functions and processes, and enhancing the consumer
experience.
Domain Name Data Operations (DO)
Data Platforms Government Service Bus (GSB)
Definitions • Total number of API calls
• Number of API calls failed due to operational issues from the entity
Calculation = Average responsiveness score for all entity’s APIs, where the responsiveness of one
API is calculated as follows:
= (Total number of the API calls – Number of the API calls failed due to operational
issues from the entity) / Total number of the API calls * 100
Measurement Unit Percentage
Acceptable Threshold 94%
Scale Intervals Unacceptable: <= 94%
Low: (94%, 95%]
Fair: (95%, 96%]
Good: (96%, 97%]
Excellent: (97%, 98%]
Leader: > 98%
Version History
Dependencies

#### Responsiveness of the integration solution with NDL - DO.OE.03
Element Name Element Details
Metric ID DO.OE.03
Metric Name Responsiveness of the integration solution with NDL
Metric Description This metric measures the responsiveness of the integration solution implemented
by the entity by calculating the percentage of operational issues encountered by NDL
against the number of data pipeline executions with the respective entity. Note that
an execution is considered failed only if it is caused by an operational issue from the
entity. This metric will be measured by NDL for each source entity with which NDL
has operated data pipelines.The prime focus of this metric is to improve data currency by reducing recurring
errors and issues. This will help in providing consumers with the most up-to-date
data for various forms of consumption.
Domain Name Data Operations (DO)
Data Platforms National Data Lake (NDL)
Definitions • Number of failed pipeline executions caused by operational issues from the
entity
• Total number of data pipeline executions with the entity
Calculation = Average responsiveness score for all entity’s systems, where the responsiveness
score of one system is calculated as follows:
= (Total number of the system’s data pipeline executions - Number of failed pipeline
executions caused by operational issues from the entity) / Total number of the
system’s data pipeline executions * 100
Measurement Unit Percentage
Acceptable Threshold 94%
Scale Intervals Unacceptable: <= 94%
Low: (94%, 95%]
Fair: (95%, 96%]
Good: (96%, 97%]
Excellent: (97%, 98%]
Leader: > 98%
Version History
Dependencies
