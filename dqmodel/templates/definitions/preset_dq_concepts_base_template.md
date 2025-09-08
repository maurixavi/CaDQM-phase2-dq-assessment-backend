# DQ Model: Preset Template

## DQ Dimension: Accuracy
**Semantic:** Indicates the degree to which data is accurate. Refers to how well data correctly represents real-world objects or events.

### DQ Factor: Semantic Accuracy  
**Semantic:** Indicates the degree to which data correctly represents real-world entities or states.
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Real-world Matching Ratio
**Purpose:** Proportion of data matching real-world entities or states.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Semantic Accuracy

##### DQ Method: calculateRealWorldMatching    
**Input data type:** Array<Column<any>>
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT COUNT(*) * 1.0 / (SELECT COUNT(*) FROM {{ table_name }}) AS matching_ratio
  FROM {{ table_name }}
  WHERE {{ column_name }} IN (SELECT value FROM {{ condition }});
	```
**Implements (DQ Metric):** Non-Null Values Ratio


### DQ Factor: Syntactic Accuracy  
**Semantic:** Indicates the degree to which data conforms to expected structural formats, patterns, or data types.
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Format Compliance Ratio  
**Purpose:** Proportion of values conforming to the expected structural format, pattern, or type.  
**Granularity:** Column  
**Result Domain:** [0, 1] 
**Measures (DQ Factor):** Syntactic Accuracy

##### DQ Method: calculateFormatComplianceRatio    
**Input data type:** Column<any>
**Output data type:** Float  
**Algorithm:**  
	```sql
  SELECT 
      SUM(CASE WHEN {{ column_name }} {{ condition }} THEN 1 ELSE 0 END)::float 
      / NULLIF(COUNT(*), 0) AS {{ metric_name }}
  FROM {{ table_name }};

	```
**Implements (DQ Metric):** Format Compliance Ratio



### DQ Factor: Precision
**Semantic:** Refers to the level of detail in which data is captured or expressed.
**Facet of (DQ Dimension):** Accuracy

#### DQ Metric: Detail Level Ratio  
**Purpose:** Proportion of data values captured with the required level of granularity or precision.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Precision

#### DQ Metric: Decimal Precision Ratio
**Purpose:** Measures the proportion of numeric values that have at least the required number of decimal places.
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Precision

##### DQ Method: calculateDecimalPrecisionRatio
**Input data type:** Column<numeric>
**Output data type:** Float  
**Algorithm:**
```sql
  SELECT 
      SUM(CASE WHEN LENGTH(SPLIT_PART(CAST({{ column_name }} AS TEXT), '.', 2)) >= {{ min_decimals }} THEN 1 ELSE 0 END)::float
      / NULLIF(COUNT(*),0) AS decimal_precision_ratio
  FROM {{ table_name }};
	```
**Implements (DQ Metric):** Decimal Precision Ratio


#### DQ Metric: Text Detail Ratio
**Purpose:** Measures the proportion of text values that meet a minimum length requirement.
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Precision

##### DQ Method: calculateTextDetailRatio
**Input data type:** Column<text>
**Output data type:** Float  
**Algorithm:**
```sql
  SELECT 
    SUM(CASE WHEN LENGTH({{ column_name }}) >= {{ min_length }} THEN 1 ELSE 0 END)::float
    / NULLIF(COUNT(*),0) AS text_detail_ratio
  FROM {{ table_name }};
	```
**Implements (DQ Metric):** Text Detail Ratio


#### DQ Metric: Row-Level Detail Compliance
**Purpose:** Measures whether each row has the required detail across multiple attributes.
**Granularity:** Tuple  
**Result Domain:** Boolean
**Measures (DQ Factor):** Precision

##### DQ Method: validateRowDetailCompliance
**Input data type:** Array<Column<any>>
**Output data type:** Boolean  
**Algorithm:**
```sql
  SELECT 
  CASE WHEN {{ column1_name }} {{ condition1 }} 
       AND {{ column2_name }} {{ condition2 }} 
       /* ... repeat for required columns */
       THEN TRUE ELSE FALSE END AS row_detail_compliance
  FROM {{ table_name }};

	```
**Implements (DQ Metric):** Row-Level Detail Compliance



## DQ Dimension: Completeness
**Semantic:** Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.

### DQ Factor: Density  
**Semantic:** Describes the proportion of actual data entries compared to the total number of expected entries.
**Facet of (DQ Dimension):** Completeness

#### DQ Metric: Non-Null Values Ratio  
**Purpose:** Proportion of non-null values in a column relative to its total number of expected values.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

##### DQ Method: calculateNonNullValuesRatio
**Input data type:** Column<any>
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
    SUM(CASE WHEN {{ column_name }} IS NOT NULL THEN 1 ELSE 0 END) * 1.0 
    / COUNT(*) AS non_null_ratio
  FROM 
    {{table_name}};
	```
**Implements (DQ Metric):** Non-Null Values Ratio



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

##### DQ Method: calculateValidValueRatio
**Input data type:** Column<any>  
**Output data type:** Float  
**Algorithm:**  
  ```sql
  SELECT 
      SUM(CASE WHEN {{ column_name }} {{ validation_rule }} THEN 1 ELSE 0 END) * 1.0 / COUNT(*) 
  FROM 
      {{table_name}};
  ```
**Implements (DQ Metric):** Valid Values Ratio



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

##### DQ Method: calculateValueRangeComplianceRatio
**Input data type:** Column<numeric>
**Output data type:** Float  
**Algorithm:**  
  ```sql
    WITH limits AS (
      SELECT {{ lower_limit }} AS lower_limit, {{ upper_limit }} AS upper_limit
    )
    SELECT 
        SUM(CASE WHEN {{ column_name }} >= limits.lower_limit 
                      AND {{ column_name }} <= limits.upper_limit THEN 1 ELSE 0 END)::float
        / NULLIF(COUNT(*),0) AS value_range_compliance_ratio
    FROM {{ table_name }} 
    CROSS JOIN limits;
  ```
**Implements (DQ Metric):** Domain Constraint Compliance Ratio 

##### DQ Method: calculatePatternComplianceRatio
**Input data type:** Column<text>
**Output data type:** Float  
**Algorithm:**  
  ```sql
    SELECT 
      SUM(CASE WHEN {{ column_name }} ~ '{{ regex_pattern }}' THEN 1 ELSE 0 END)::float
      / NULLIF(COUNT(*),0) AS pattern_compliance_ratio
    FROM {{ table_name }};
  ```
**Implements (DQ Metric):** Domain Constraint Compliance Ratio 

##### DQ Method: calculateListComplianceRatio
**Input data type:** Column<any>
**Output data type:** Float  
**Algorithm:**  
  ```sql
    SELECT 
      SUM(CASE WHEN {{ column_name }} IN ({{ valid_values_list }}) THEN 1 ELSE 0 END)::float
      / NULLIF(COUNT(*),0) AS list_compliance_ratio
    FROM {{ table_name }};
  ```
**Implements (DQ Metric):** Domain Constraint Compliance Ratio 


### DQ Factor: Intra-relationship Integrity
**Semantic:** Indicates whether values across multiple attributes within the same table satisfy logical rules or dependencies.
**Facet of (DQ Dimension):** Consistency

#### DQ Metric: Intra-relational Rule Compliance Ratio  
**Purpose:** Proportion of records that satisfy intra-attribute logical rules or dependencies.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Intra-relationship Integrity

##### DQ Method: calculateIntraRuleComplianceRatio
**Input data type:** Array<Column<any>>
**Output data type:** Float  
**Algorithm:**  
  ```sql
  SELECT 
      SUM(CASE 
              WHEN {{ column1_name }} {{ subrule1 }} 
                  AND {{ column2_name }} {{ subrule2 }} 
                  /* ... repeat for all required columns/subrules */
              THEN 1 ELSE 0 
          END)::float 
      / NULLIF(COUNT(*),0) AS intra_relational_rule_ratio
  FROM {{ table_name }};
  ```
**Implements (DQ Metric):** Intra-relational Rule Compliance Ratio 


### DQ Factor: Inter-relationship Integrity
**Semantic:** Indicates whether data relationships across different tables or entities satisfy expected referential and semantic rules.
**Facet of (DQ Dimension):** Consistency

#### DQ Metric: Referential Integrity Compliance Ratio  
**Purpose:** Proportion of table records whose foreign keys correctly reference existing records in the corresponding reference tables.
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Inter-relationship Integrity

##### DQ Method: calculateReferentialIntegrityComplianceRatio 
**Input data type:** Array<Column<any>>
**Output data type:** Float  
**Algorithm:**  
  ```sql
  SELECT 
    SUM(CASE 
        WHEN {{ fk_column1 }} IN (SELECT {{ pk_column1 }} FROM {{ ref_table1 }})
         AND {{ fk_column2 }} IN (SELECT {{ pk_column2 }} FROM {{ ref_table2 }})
         /* ... repeat for additional foreign keys */
        THEN 1 ELSE 0
    END)::float / COUNT(*) AS ref_integrity_compliance_ratio
  FROM {{ table_name }};
  ```
**Implements (DQ Metric):** Referential Integrity Compliance Ratio  



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

##### DQ Method: calculateNonDuplicateEntryRatio 
**Input data type:** Array<Column<any>>
**Output data type:** Float  
**Algorithm:**  
  ```sql
  SELECT 
      1.0 - (COUNT(*) - COUNT(DISTINCT {{ column_list }}))::float / COUNT(*) AS non_duplicate_ratio
  FROM {{ table_name }};
  /* {{ column_list }}: list of columns that define the uniqueness of a row. e.g., key_column1, key_column2, ... */
  ```
**Implements (DQ Metric):** Non-Duplicate Entry Ratio  


### DQ Factor: No-contradiction
**Semantic:** Ensures that logically related records do not contain conflicting or contradictory information.
**Facet of (DQ Dimension):** Uniqueness

#### DQ Metric: Contradiction-Free Record  
**Purpose:** Indicates whether each record (tuple) in the table does not contain conflicting information across specified columns. 
**Granularity:** Tuple  
**Result Domain:** Boolean 
**Measures (DQ Factor):** No-contradiction

##### DQ Method: validateContradictionFree
**Input data type:** Array<Column<any>>
**Output data type:** Boolean  
**Algorithm:**  
  ```sql
  SELECT 
    CASE 
        WHEN {{ column1_name }} {{ condition1 }}
         AND {{ column2_name }} {{ condition1 }}
         /* ... repeat for additional columns/conditions */
        THEN 1 ELSE 0 
    END AS tuple_contradiction_free
  FROM {{ table_name }}
```
**Implements (DQ Metric):** Contradiction-Free Record  


## DQ Dimension: Freshness
**Semantic:** Refers to the temporal validity of the data, indicating how current, timely, or stable the data is with respect to its use and the real world.

### DQ Factor: Currency
**Semantic:** Indicates how up-to-date the data is with respect to the real-world entities or source systems it represents.
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Acceptance Data Age Ratio
**Purpose:** Proportion of records in a column  updated within an acceptable age threshold.
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Currency

##### DQ Method: calculateAcceptableDataAgeRatio
**Input data type:** Column<date>
**Output data type:** Float  
**Algorithm:**  
  ```sql
  SELECT 
    SUM(CASE 
            WHEN {{ date_column }} > {{ threshold_date }} 
            THEN 1 ELSE 0 
        END)::float 
    / COUNT(*) AS column_update_valid_ratio
  FROM {{ table_name }};
```
**Implements (DQ Metric):** Acceptance Data Age Ratio

#### DQ Metric: Acceptance Data Age  
**Purpose:** Indicates whether each data record was updated within an acceptable age threshold.
**Granularity:** Cell  
**Result Domain:** Boolean  
**Measures (DQ Factor):** Currency  

##### DQ Method: validateAcceptableDataAge
**Input data type:** Column<date>
**Output data type:** Boolean  
**Algorithm:**  
  ```sql
  SELECT 
    CASE 
        WHEN {{ date_column }} > {{ threshold_date }} 
        THEN 1 ELSE 0 
    END AS cell_update_validity
  FROM {{ table_name }};
```
**Implements (DQ Metric):** Acceptance Data Age  



### DQ Factor: Timeliness
**Semantic:** Indicates whether data is available in time to support its intended use.
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: On-Time Availability Ratio  
**Purpose:** Proportion of data available before the required usage time.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Timeliness

##### DQ Method: calculateOnTimeAvailabilityRatio
**Input data type:** Column<date>
**Output data type:** Float  
**Algorithm:**  
  ```sql
  SELECT 
    SUM(CASE 
            WHEN {{ date_column }} <= {{ required_usage_date }} 
            THEN 1 ELSE 0 
        END)::float 
    / COUNT(*) AS on_time_availability_ratio
  FROM {{ table_name }};
```
**Implements (DQ Metric):** On-Time Availability Ratio  



### DQ Factor: Volatility
**Semantic:** Describes the frequency or rate at which the data changes over time.
**Facet of (DQ Dimension):** Freshness

#### DQ Metric: Data Change Ratio 
**Purpose:** Proportion of records in a table that have changed at least once within a specified period.
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Volatility

##### DQ Method: calculateOnTimeAvailabilityRatio
**Input data type:** Array<Column<type>>
**Output data type:** Float  
**Algorithm:**  
  ```sql
  SELECT COUNT(DISTINCT {{ pk_column }})::float 
        / (SELECT COUNT(*) FROM {{ table_name }}) AS data_change_ratio
  FROM {{ table_name }}
  WHERE {{ date_column }} >= {{ start_date }} 
    AND {{ date_column }} <= {{ end_date }};
```
**Implements (DQ Metric):** Data Change Ratio