# DQ Model: Preset Template

## DQ Dimension: Accuracy
**Semantic:** Indicates that the data is correct and precise.

### DQ Factor: Semantic Accuracy  
**Semantic:** The data correctly represents entities or states of the real world.  
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Real-world Matching Ratio  
**Purpose:** Proportion of data matching real-world entities or states.  
**Granularity:** Record or attribute  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Semantic Accuracy

##### DQ Method: Real-world Matching Ratio  
**Name:** validateRealWorldMatching  
**Input data type:** Dataset (list of records)  
**Output data type:** Float (ratio)  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS matching_ratio
	FROM 
			dataset d
	WHERE 
			d.value IN (SELECT value FROM real_world_entities);
	```
**Implements (DQ Metric):** Real-world Matching Ratio


#### DQ Metric: Entity Accuracy Score  
**Purpose:** Measure how accurate data is in representing specific entities.  
**Granularity:** Entity  
**Result Domain:** Numeric range  
**Measures (DQ Factor):** Semantic Accuracy

##### DQ Method: Entity Accuracy Validation  
**Name:** calculateEntityAccuracy  
**Input data type:** Dataset (list of entities)  
**Output data type:** Float (score)  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS accuracy_score
	FROM 
			dataset d
	WHERE 
			d.entity IN (SELECT entity FROM gold_standard_entities);
	```
**Implements (DQ Metric):** Entity Accuracy Score


### DQ Factor: Syntactic Accuracy  
**Semantic:** The data is free from syntactic errors.  
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Syntax Error Rate  
**Purpose:** Proportion of syntactic errors detected in the data.  
**Granularity:** Attribute or record  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Syntactic Accuracy

##### DQ Method: Syntax Error Detection  
**Name:** detectSyntaxErrors  
**Input data type:** Dataset (list of records)  
**Output data type:** Float (error rate)  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS error_rate
	FROM 
			dataset d
	WHERE 
			NOT REGEXP_LIKE(d.value, '^[a-zA-Z0-9_\-]+$'); 
	```
**Implements (DQ Metric):** Syntax Error Rate


#### DQ Metric: Conformance Score  
**Purpose:** Degree of data conformance with defined syntactic rules.  
**Granularity:** Entire dataset  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Syntactic Accuracy

##### DQ Methods:



### DQ Factor: Precision  
**Semantic:** The data has an adequate level of detail.  
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Detail Level Score  
**Purpose:** Measures whether the level of detail in the data is appropriate for its purpose.  
**Granularity:** Attribute  
**Result Domain:** Boolean  
**Measures (DQ Factor):** Precision

##### DQ Methods:


#### DQ Metric: Rounding Error Rate  
**Purpose:** Proportion of errors caused by rounding in numeric values.  
**Granularity:** Attribute or value  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Precision

##### DQ Methods:


## DQ Dimension: Completeness
**Semantic:** Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.

### DQ Factor: Density  
**Semantic:** The proportion of actual data entries compared to the total possible entries.  
**Facet of (DQ Dimension):** Completeness

#### DQ Metric: Data Density Ratio  
**Purpose:** Proportion of data entries present compared to the total possible.  
**Granularity:** Dataset or table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

##### DQ Methods:


#### DQ Metric: Null Value Percentage  
**Purpose:** Proportion of null values in the dataset.  
**Granularity:** Dataset or column.  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

##### DQ Method: Null Value Percentage Calculation  
**Name:** calculateNullValuePercentage  
**Input data type:** Dataset (list of records)  
**Output data type:** Float (percentage)  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS null_percentage
	FROM 
			dataset d
	WHERE 
			d.value IS NULL;
	```
**Implements (DQ Metric):** Null Value Percentage


### DQ Factor: Coverage  
**Semantic:** The extent to which the data covers the required scope or domain.  
**Facet of (DQ Dimension):** Completeness

#### DQ Metric: Domain Coverage Ratio  
**Purpose:** Proportion of data entries present compared to the total possible.  
**Granularity:** Dataset or table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Coverage

##### DQ Method: Domain Coverage Validation  
**Name:** validateDomainCoverage  
**Input data type:** Dataset (list of values)  
**Output data type:** Float (coverage ratio)  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS domain_coverage_ratio
	FROM 
			dataset d
	WHERE 
			d.value IN (SELECT value FROM domain_values);
	```
**Implements (DQ Metric):** Domain Coverage Ratio


#### DQ Metric: Attribute Coverage Score  
**Purpose:** Proportion of null values in the dataset.  
**Granularity:** Dataset or column  
**Result Domain:** [0, 1]  
**Measures:** Coverage

##### DQ Methods:


## DQ Dimension: Freshness
**Semantic:** Refers to the recency and update status of the data, indicating whether the data is current and up-to-date.

### DQ Factor: Currency  
**Semantic:** Indicates how up-to-date the data is.  
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Data Age  
**Purpose:** Average time since the last update of the data.  
**Granularity:** Record  
**Result Domain:** Numeric range (in days, hours, etc.)  
**Measures (DQ Factor):** Currency

##### DQ Methods:


#### DQ Metric: Update Frequency  
**Purpose:** Frequency of updates made to the data.  
**Granularity:** Dataset  
**Result Domain:** Integer  
**Measures (DQ Factor):** Currency

##### DQ Methods:


### DQ Factor: Timeliness  
**Semantic:** The data is available when needed.  
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Availability Delay  
**Purpose:** Time from need to availability of data.  
**Granularity:** Record  
**Result Domain:** Numeric range  
**Measures (DQ Factor):** Timeliness

##### DQ Methods:


#### DQ Metric: On-time Data Ratio  
**Purpose:** Proportion of data available on time relative to the total.  
**Granularity:** Dataset  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Timeliness

##### DQ Method: On-time Data Validation  
**Name:** validateOnTimeData  
**Input data type:** Dataset (list of timestamps)  
**Output data type:** Float (ratio)  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS on_time_ratio
	FROM 
			dataset d
	WHERE 
			d.timestamp <= TO_DATE('YYYY-MM-DD', 'YYYY-MM-DD'); -- Expiring date
	```
**Implements (DQ Metric):** On-time Data Ratio


### DQ Factor: Volatility  
**Semantic:** The rate at which the data changes over time.  
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Change Rate  
**Purpose:** Rate of change in the data over time.  
**Granularity:** Attribute or record  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Volatility

##### DQ Methods:



#### DQ Metric: Stability Index  
**Purpose:** Index measuring data stability over a period. Average time since the last update of the data.  
**Granularity:** Dataset  
**Result Domain:** Numeric range  
**Measures (DQ Factor):** Volatility

##### DQ Method: Stability Index Calculation  
**Name:** calculateStabilityIndex  
**Input data type:** Dataset (list of values over time)  
**Output data type:** Float (stability index)  
**Algorithm:**  
	```sql
	WITH changes AS (
			SELECT 
					value, 
					LAG(value) OVER (ORDER BY timestamp) AS previous_value
			FROM 
					dataset
	)
	SELECT 
			1 - (COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset)) AS stability_index
	FROM 
			changes
	WHERE 
			value != previous_value;
	```
**Implements (DQ Metric):** Stability Index

## DQ Dimension: Consistency  
**Semantic:** Ensures that the data is coherent across different sources and over time, maintaining integrity and reliability.


### DQ Factor: Domain Integrity  
**Semantic:** Indicates how up-to-date the data is.  
**Facet of (DQ Dimension):** Consistency


#### DQ Metric: Range Conformance Ratio  
**Purpose:** Proportion of values falling within the defined range.  
**Granularity:** Attribute or value  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Domain Integrity

##### DQ Methods:



#### DQ Metric: Outlier Percentage  
**Purpose:** Proportion of values outside the defined range.  
**Granularity:** Attribute or value  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Domain Integrity

##### DQ Method: Outlier Detection  
**Name:** detectOutliers  
**Input data type:** Dataset (list of numerical values)  
**Output data type:** Integer (outlier percentage)  
**Algorithm:**  
	```sql
	WITH stats AS (
			SELECT 
					PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) AS q1,
					PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) AS q3
			FROM 
					dataset
	), 
	limits AS (
			SELECT 
					q1, q3, 
					q1 - 1.5 * (q3 - q1) AS lower_limit,
					q3 + 1.5 * (q3 - q1) AS upper_limit
			FROM 
					stats
	)
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS outlier_percentage
	FROM 
			dataset d, limits l
	WHERE 
			d.value < l.lower_limit OR d.value > l.upper_limit;

	```
**Implements (DQ Metric):** Outlier Percentage


### DQ Factor: Intra-relationship Integrity  
**Semantic:** Ensures that data within a single dataset is consistent.  
**Facet of (DQ Dimension):** Consistency


#### DQ Metric: Constraint Satisfaction Ratio  
**Purpose:** Proportion of intra-relational constraints satisfied.  
**Granularity:** Dataset  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Intra-relationship Integrity

##### DQ Methods:



#### DQ Metric: Error Count  
**Purpose:** Number of violations of intra-relational constraints.  
**Granularity:** Dataset  
**Result Domain:** Integer  
**Measures (DQ Factor):** Intra-relationship Integrity

##### DQ Methods:



### DQ Factor: Inter-relationship Integrity  
**Semantic:** Ensures that data across multiple datasets is consistent.  
**Facet of (DQ Dimension):** Consistency


#### DQ Metric: Cross-dataset Consistency Ratio  
**Purpose:** Proportion of inter-dataset relationships that are consistent.  
**Granularity:** Multiple datasets  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Inter-relationship Integrity

##### DQ Methods:



#### DQ Metric: Inter-dataset Error Count  
**Purpose:** Number of inconsistencies between datasets.  
**Granularity:** Dataset or record  
**Result Domain:** Integer  
**Measures (DQ Factor):** Inter-relationship Integrity

##### DQ Methods:



## DQ Dimension: Uniqueness
**Semantic:** Indicates that each data entry must be unique, with no duplicates present in the dataset.


### DQ Factor: No-duplication  
**Semantic:** Ensures that there are no duplicate entries in the dataset.  
**Facet of (DQ Dimension):** Uniqueness


#### DQ Metric: Duplicate Entry Count  
**Purpose:** Number of duplicate entries in the dataset.  
**Granularity:** Dataset  
**Result Domain:** Integer  
**Measures (DQ Factor):** No-duplication

##### DQ Method: Duplicate Detection 
**Name:** detectDuplicateEntries  
**Input data type:** Dataset (list of records)  
**Output data type:** Integer (duplicate count)  
**Algorithm:**  
	```sql
	SELECT 
			value, COUNT(*) AS duplicate_count
	FROM 
			dataset
	GROUP BY 
			value
	HAVING 
			COUNT(*) > 1;

	```
**Implements (DQ Metric):** Duplicate Entry Count


#### DQ Metric: Unique Entry Ratio  
**Purpose:** Proportion of unique entries relative to the total.  
**Granularity:** Dataset  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** No-duplication

##### DQ Methods:



### DQ Factor: No-contradiction  
**Semantic:** Ensures that there are no conflicting entries within the dataset.  
**Facet of (DQ Dimension):** Uniqueness


#### DQ Metric: Contradiction Detection Count  
**Purpose:** Number of contradictions detected in the data.  
**Granularity:** Dataset or record  
**Result Domain:** Integer  
**Measures (DQ Factor):** No-contradiction

##### DQ Methods:



#### DQ Metric: Consistency Ratio  
**Purpose:** Proportion of data free from contradictions relative to the total.  
**Granularity:** Dataset  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** No-contradiction

##### DQ Method: Domain Coverage Validation  
**Name:** checkDataConsistency  
**Input data type:** Dataset (list of records)  
**Output data type:** Integer (consistency ratio)  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS consistency_ratio
	FROM 
			dataset d
	WHERE 
			d.value IN (SELECT value FROM consistency_rules);
	```
**Implements (DQ Metric):** Consistency Ratio









