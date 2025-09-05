# DQ Model: Preset Template

## DQ Dimension: Accuracy
**Semantic:** Indicates the degree to which data is accurate. Refers to how well data correctly represents real-world objects or events.

### DQ Factor: Semantic Accuracy  
**Semantic:** Indicates the degree to which data correctly represents real-world entities or states.
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Real-world Matching Ratio
**Purpose:** Proportion of data matching real-world entities or states.  
**Granularity:** Tuple  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Semantic Accuracy


### DQ Factor: Syntactic Accuracy  
**Semantic:** Indicates the degree to which data conforms to expected structural formats, patterns, or data types.
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Format Compliance Ratio  
**Purpose:** Proportion of values conforming to the expected structural format, pattern, or type.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Syntactic Accuracy


### DQ Factor: Precision
**Semantic:** Refers to the level of detail in which data is captured or expressed.
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Detail Level Ratio  
**Purpose:** Proportion of data values captured with the required level of granularity or precision.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Precision


## DQ Dimension: Completeness
**Semantic:** Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.

### DQ Factor: Density  
**Semantic:** Describes the proportion of actual data entries compared to the total number of expected entries.
**Facet of (DQ Dimension):** Completeness

#### DQ Metric: Value Density Ratio  
**Purpose:** Proportion of non-null values relative to the total number of expected values.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

#### DQ Metric: Non-Null Values Ratio  
**Purpose:** Proportion of non-null values in a column relative to its total number of expected values.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density


### DQ Factor: Coverage  
**Semantic:** Indicates the extent to which the data covers the required scope, domain, or entities.
**Facet of (DQ Dimension):** Completeness

#### DQ Metric: Domain Coverage Ratio  
**Purpose:** Proportion of required domain elements represented in the data.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Coverage

#### DQ Metric: Valid Values Ratio
**Purpose:** Proportion of values in a column that are valid according to a predefined domain.
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Coverage



## DQ Dimension: Consistency
**Semantic:** Indicates the satisfaction of semantic rules defined on the data.
**Facet of (DQ Dimension):** Consistency

### DQ Factor: Domain Integrity
**Semantic:** Indicates whether individual attribute values comply with defined constraints, rules, or value domains.
**Facet of (DQ Dimension):** Consistency

#### DQ Metric: Domain Constraint Compliance Ratio 
**Purpose:** Proportion of values that comply with domain rules or constraints.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Domain Integrity

#### DQ Metric: Domain Constraint Compliance Ratio 
**Purpose:** Proportion of values that comply with domain rules or constraints.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Domain Integrity


### DQ Factor: Intra-relationship Integrity
**Semantic:** Indicates whether values across multiple attributes within the same record or table satisfy logical rules or dependencies.
**Facet of (DQ Dimension):** Consistency

#### DQ Metric: Intra-record Rule Compliance Ratio  
**Purpose:** Proportion of records that satisfy intra-attribute logical rules or dependencies.  
**Granularity:** Tuple  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Intra-relationship Integrity

#### DQ Metric: Intra-relational Rule Compliance Ratio  
**Purpose:** Proportion of records that satisfy intra-attribute logical rules or dependencies.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Intra-relationship Integrity

### DQ Factor: Inter-relationship Integrity
**Semantic:** Indicates whether data relationships across different tables or entities satisfy expected referential and semantic rules.
**Facet of (DQ Dimension):** Consistency

#### DQ Metric: Referential Integrity Compliance Ratio  
**Purpose:** Proportion of valid inter-table references according to defined relationships.  
**Granularity:** Tuple  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Inter-relationship Integrity



## DQ Dimension: Uniqueness
**Semantic:** Indicates the degree to which a real-world entity is represented only once in the information system, without duplication or contradiction.

### DQ Factor: No-duplication
**Semantic:** Indicates the absence of duplicate records within the dataset.
**Facet of (DQ Dimension):** Uniqueness

#### DQ Metric: Non-Duplicate Entry Ratio  
**Purpose:** Measures the proportion of entries in the dataset that are not exact duplicates.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** No-duplication


### DQ Factor: No-contradiction
**Semantic:** Ensures that logically related records do not contain conflicting or contradictory information.
**Facet of (DQ Dimension):** Uniqueness

#### DQ Metric: Contradiction-Free Record Ratio  
**Purpose:** Proportion of entity representations without conflicting information.  
**Granularity:** Entity  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** No-contradiction



## DQ Dimension: Freshness
**Semantic:** Refers to the temporal validity of the data, indicating how current, timely, or stable the data is with respect to its use and the real world.

### DQ Factor: Currency
**Semantic:** Indicates how up-to-date the data is with respect to the real-world entities or source systems it represents.
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Update Delay Ratio  
**Purpose:** Proportion of data whose time since last update is within the acceptable threshold.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Currency

#### DQ Metric: Data Update Age Validity  
**Purpose:** Indicates whether the data was updated within an acceptable age threshold.  
**Granularity:** Cell  
**Result Domain:** Boolean  
**Measures (DQ Factor):** Currency  



### DQ Factor: Timeliness
**Semantic:** Indicates whether data is available in time to support its intended use.
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: On-Time Availability Ratio  
**Purpose:** Proportion of data available before the required usage time.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Timeliness


### DQ Factor: Volatility
**Semantic:** Describes the frequency or rate at which the data changes over time.
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Validity Interval Ratio  
**Purpose:** Proportion of data values that remain valid for the expected period.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Volatility