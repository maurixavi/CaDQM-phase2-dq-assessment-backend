# DQ Model: Preset Template

## DQ Dimension: Accuracy
**Semantic:** Indicates that the data is correct and precise.

### DQ Factor: Semantic Accuracy  
**Semantic:** The data correctly represents entities or states of the real world.  
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Real-world Matching Ratio
**Purpose:** Proportion of data matching real-world entities or states.  
**Granularity:** Tuple  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Semantic Accuracy

##### DQ Method: Real-world Matching Ratio Validation
**Name:** validateRealWorldMatching  
**Input data type:** List<Record>  
**Output data type:** Float  
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
**Granularity:** Row  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Semantic Accuracy

##### DQ Method: Entity Accuracy Validation  
**Name:** calculateEntityAccuracy  
**Input data type:** List<Entity>  
**Output data type:** Float  
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
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Syntactic Accuracy

##### DQ Method: Syntax Error Detection  
**Name:** detectSyntaxErrors  
**Input data type:** List<Record>  
**Output data type:** Float  
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
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Syntactic Accuracy

##### DQ Method: Syntactic Conformance Validation
**Name:** validateSyntacticConformance  
**Input data type:** List<Record>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS conformance_score
	FROM 
			dataset d
	WHERE 
			d.value MATCHES predefined_syntax_rules;
	```
**Implements (DQ Metric):** Conformance Score


### DQ Factor: Precision  
**Semantic:** The data has an adequate level of detail.  
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Detail Level Score  
**Purpose:** Measures whether the level of detail in the data is appropriate for its purpose.  
**Granularity:** Column  
**Result Domain:** Boolean  
**Measures (DQ Factor):** Precision

##### DQ Method: Validate Detail Level
**Name:** checkDetailLevel  
**Input data type:** List<Record>  
**Output data type:** Boolean  
**Algorithm:**  
	```sql
	SELECT 
			CASE WHEN AVG(LENGTH(value)) >= minimum_detail_threshold 
			THEN TRUE ELSE FALSE END AS detail_sufficient
	FROM 
			dataset;
	```
**Implements (DQ Metric):** Detail Level Score


#### DQ Metric: Rounding Error Rate  
**Purpose:** Proportion of errors caused by rounding in numeric values.  
**Granularity:** Column 
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Precision

##### DQ Method: Calculate Rounding Error
**Name:** calculateRoundingErrors  
**Input data type:** List<NumericRecord>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS rounding_error_rate
	FROM 
			dataset d
	WHERE 
			ABS(d.original_value - ROUND(d.original_value, precision)) > tolerance;
	```
**Implements (DQ Metric):** Rounding Error Rate


## DQ Dimension: Completeness
**Semantic:** Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.

### DQ Factor: Density  
**Semantic:** The proportion of actual data entries compared to the total possible entries.  
**Facet of (DQ Dimension):** Completeness

#### DQ Metric: Data Density Ratio  
**Purpose:** Proportion of data entries present compared to the total possible.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

##### DQ Method: Calculate Data Density
**Name:** calculateDataDensity  
**Input data type:** List<Record>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(DISTINCT value) * 1.0 / (SELECT COUNT(*) FROM all_possible_entries) AS density_ratio
	FROM 
			dataset;
	```
**Implements (DQ Metric):** Data Density Ratio


#### DQ Metric: Null Value Percentage  
**Purpose:** Proportion of null values in the dataset.  
**Granularity:** Table
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

##### DQ Method: Null Value Percentage Calculation  
**Name:** calculateNullValuePercentage  
**Input data type:** List<Record>  
**Output data type:** Float  
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
**Granularity:** Table 
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Coverage

##### DQ Method: Domain Coverage Validation  
**Name:** validateDomainCoverage  
**Input data type:** List<Record>  
**Output data type:** Float  
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
**Purpose:** Proportion of populated attributes.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures:** Coverage

##### DQ Method: Calculate Attribute Coverage
**Name:** calculateAttributeCoverage  
**Input data type:** List<Record>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(NOT NULL value) * 1.0 / (SELECT COUNT(*) FROM dataset) AS attribute_coverage
	FROM 
			dataset;
	```
**Implements (DQ Metric):** Attribute Coverage Score


## DQ Dimension: Freshness
**Semantic:** Refers to the recency and update status of the data, indicating whether the data is current and up-to-date.

### DQ Factor: Currency  
**Semantic:** Indicates how up-to-date the data is.  
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Data Age  
**Purpose:** Average time since the last update of the data.  
**Granularity:** Row  
**Result Domain:** Integer  
**Measures (DQ Factor):** Currency

##### DQ Method: Calculate Data Age
**Name:** calculateDataAge  
**Input data type:** List<Record>  
**Output data type:** Integer  
**Algorithm:**  
	```sql
	SELECT 
			AVG(DATEDIFF(CURRENT_DATE, last_update_date)) AS average_data_age
	FROM 
			dataset;
	```
**Implements (DQ Metric):** Data Age


#### DQ Metric: Update Frequency  
**Purpose:** Frequency of updates made to the data.  
**Granularity:** Table  
**Result Domain:** Integer  
**Measures (DQ Factor):** Currency

##### DQ Method: Calculate Update Frequency
**Name:** calculateUpdateFrequency  
**Input data type:** List<Record>  
**Output data type:** Integer  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(DISTINCT last_update_date) AS update_frequency
	FROM 
			dataset;
	```
**Implements (DQ Metric):** Update Frequency


### DQ Factor: Timeliness  
**Semantic:** The data is available when needed.  
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Availability Delay  
**Purpose:** Time from need to availability of data.  
**Granularity:** Row  
**Result Domain:** Integer  
**Measures (DQ Factor):** Timeliness

##### DQ Method: Calculate Availability Delay
**Name:** calculateAvailabilityDelay  
**Input data type:** List<Record>  
**Output data type:** Integer  
**Algorithm:**  
	```sql
	SELECT 
			AVG(DATEDIFF(availability_date, request_date)) AS average_delay
	FROM 
			dataset;
	```
**Implements (DQ Metric):** Availability Delay


#### DQ Metric: On-time Data Ratio  
**Purpose:** Proportion of data available on time relative to the total.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Timeliness

##### DQ Method: On-time Data Validation  
**Name:** validateOnTimeData  
**Input data type:** List<Record>  
**Output data type:** Float  
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
**Granularity:** Column
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Volatility

##### DQ Method: Calculate Change Rate
**Name:** calculateChangeRate  
**Input data type:** List<TimeSeries>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	WITH changes AS (
			SELECT 
					COUNT(DISTINCT value) AS unique_values,
					COUNT(*) AS total_records
			FROM 
					dataset
	)
	SELECT 
			unique_values * 1.0 / total_records AS change_rate
	FROM 
			changes;
	```
**Implements (DQ Metric):** Change Rate


#### DQ Metric: Stability Index  
**Purpose:** Index measuring data stability over a period.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Volatility

##### DQ Method: Stability Index Calculation  
**Name:** calculateStabilityIndex  
**Input data type:** List<TimeSeries>  
**Output data type:** Float  
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
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Domain Integrity

##### DQ Method: Calculate Range Conformance
**Name:** calculateRangeConformance  
**Input data type:** List<NumericRecord>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS range_conformance
	FROM 
			dataset d
	WHERE 
			d.value BETWEEN min_value AND max_value;
	```
**Implements (DQ Metric):** Range Conformance Ratio


#### DQ Metric: Outlier Percentage  
**Purpose:** Proportion of values outside the defined range.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Domain Integrity

##### DQ Method: Outlier Detection  
**Name:** detectOutliers  
**Input data type:** List<NumericRecord>  
**Output data type:** Float  
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
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Intra-relationship Integrity

##### DQ Method: Calculate Constraint Satisfaction
**Name:** calculateConstraintSatisfaction  
**Input data type:** List<Record>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM dataset) AS constraint_satisfaction
	FROM 
			dataset d
	WHERE 
			d.value SATISFIES ALL predefined_constraints;
	```
**Implements (DQ Metric):** Constraint Satisfaction Ratio


#### DQ Metric: Error Count  
**Purpose:** Number of violations of intra-relational constraints.  
**Granularity:** Table  
**Result Domain:** Integer  
**Measures (DQ Factor):** Intra-relationship Integrity

##### DQ Method: Count Constraint Violations
**Name:** countConstraintViolations  
**Input data type:** List<Record>  
**Output data type:** Integer  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) AS constraint_violation_count
	FROM 
			dataset d
	WHERE 
			d.value VIOLATES ANY predefined_constraints;
	```
**Implements (DQ Metric):** Error Count


### DQ Factor: Inter-relationship Integrity  
**Semantic:** Ensures that data across multiple datasets is consistent.  
**Facet of (DQ Dimension):** Consistency


#### DQ Metric: Cross-dataset Consistency Ratio  
**Purpose:** Proportion of inter-dataset relationships that are consistent.  
**Granularity:** Tuple  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Inter-relationship Integrity

##### DQ Method: Validate Cross-dataset Consistency
**Name:** validateCrossDatasetConsistency  
**Input data type:** List<CrossDatasetRecord>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) * 1.0 / (SELECT COUNT(*) FROM cross_dataset_comparison) AS consistency_ratio
	FROM 
			cross_dataset_comparison cdc
	WHERE 
			cdc.dataset1_value = cdc.dataset2_value;
	```
**Implements (DQ Metric):** Cross-dataset Consistency Ratio


#### DQ Metric: Inter-dataset Error Count  
**Purpose:** Number of inconsistencies between datasets.  
**Granularity:** Tuple  
**Result Domain:** Integer  
**Measures (DQ Factor):** Inter-relationship Integrity

##### DQ Method: Count Inter-dataset Inconsistencies
**Name:** countInterDatasetInconsistencies  
**Input data type:** List<CrossDatasetRecord>  
**Output data type:** Integer  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) AS inter_dataset_error_count
	FROM 
			cross_dataset_comparison cdc
	WHERE 
			cdc.dataset1_value != cdc.dataset2_value;
	```
**Implements (DQ Metric):** Inter-dataset Error Count


## DQ Dimension: Uniqueness
**Semantic:** Indicates that each data entry must be unique, with no duplicates present in the dataset.


### DQ Factor: No-duplication  
**Semantic:** Ensures that there are no duplicate entries in the dataset.  
**Facet of (DQ Dimension):** Uniqueness


#### DQ Metric: Duplicate Entry Count  
**Purpose:** Number of duplicate entries in the dataset.  
**Granularity:** Table  
**Result Domain:** Integer  
**Measures (DQ Factor):** No-duplication

##### DQ Method: Duplicate Detection 
**Name:** detectDuplicateEntries  
**Input data type:** List<Record>  
**Output data type:** Integer  
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
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** No-duplication

##### DQ Method: Calculate Unique Entry Ratio
**Name:** calculateUniqueEntryRatio  
**Input data type:** List<Record>  
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(DISTINCT value) * 1.0 / (SELECT COUNT(*) FROM dataset) AS unique_ratio
	FROM 
			dataset;
	```
**Implements (DQ Metric):** Unique Entry Ratio


### DQ Factor: No-contradiction  
**Semantic:** Ensures that there are no conflicting entries within the dataset.  
**Facet of (DQ Dimension):** Uniqueness


#### DQ Metric: Contradiction Detection Count  
**Purpose:** Number of contradictions detected in the data.  
**Granularity:** Table  
**Result Domain:** Integer  
**Measures (DQ Factor):** No-contradiction

##### DQ Method: Detect Contradictions
**Name:** detectContradictions  
**Input data type:** List<Record>  
**Output data type:** Integer  
**Algorithm:**  
	```sql
	SELECT 
			COUNT(*) AS contradiction_count
	FROM 
			dataset d1
	JOIN 
			dataset d2 ON d1.id = d2.id AND d1.value != d2.value;
	```
**Implements (DQ Metric):** Contradiction Detection Count


#### DQ Metric: Consistency Ratio  
**Purpose:** Proportion of data free from contradictions relative to the total.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** No-contradiction

##### DQ Method: Check Data Consistency
**Name:** checkDataConsistency  
**Input data type:** List<Record>  
**Output data type:** Float  
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