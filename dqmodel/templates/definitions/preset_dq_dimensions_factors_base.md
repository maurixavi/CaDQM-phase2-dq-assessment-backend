# DQ Model: Preset Template

## DQ Dimension: Accuracy
**Semantic:** Indicates the degree to which data is accurate. Refers to how well data correctly represents real-world objects or events.

### DQ Factor: Semantic Accuracy  
**Semantic:** Indicates the degree to which data correctly represents real-world entities or states.
**Facet of (DQ Dimension):** Accuracy

### DQ Factor: Syntactic Accuracy  
**Semantic:** Indicates the degree to which data conforms to expected structural formats, patterns, or data types.
**Facet of (DQ Dimension):** Accuracy

### DQ Factor: Precision
**Semantic:** Refers to the level of detail in which data is captured or expressed.
**Facet of (DQ Dimension):** Accuracy

## DQ Dimension: Completeness
**Semantic:** Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.

### DQ Factor: Density  
**Semantic:** Describes the proportion of actual data entries compared to the total number of expected entries.
**Facet of (DQ Dimension):** Completeness

### DQ Factor: Coverage  
**Semantic:** Indicates the extent to which the data covers the required scope, domain, or entities.
**Facet of (DQ Dimension):** Completeness


## DQ Dimension: Consistency
**Semantic:** Indicates the satisfaction of semantic rules defined on the data.

### DQ Factor: Domain Integrity
**Semantic:** Indicates whether individual attribute values comply with defined constraints, rules, or value domains.
**Facet of (DQ Dimension):** Consistency

### DQ Factor: Intra-relationship Integrity
**Semantic:** Indicates whether values across multiple attributes within the same record or table satisfy logical rules or dependencies.
**Facet of (DQ Dimension):** Consistency

### DQ Factor: Inter-relationship Integrity
**Semantic:** Indicates whether data relationships across different tables or entities satisfy expected referential and semantic rules.
**Facet of (DQ Dimension):** Consistency


## DQ Dimension: Uniqueness
**Semantic:** Indicates the degree to which a real-world entity is represented only once in the information system, without duplication or contradiction.

### DQ Factor: No-duplication
**Semantic:** Indicates the absence of duplicate records within the dataset.
**Facet of (DQ Dimension):** Uniqueness

### DQ Factor: No-contradiction
**Semantic:** Ensures that logically related records do not contain conflicting or contradictory information.
**Facet of (DQ Dimension):** Uniqueness


## DQ Dimension: Freshness
**Semantic:** Refers to the temporal validity of the data, indicating how current, timely, or stable the data is with respect to its use and the real world.

### DQ Factor: Currency
**Semantic:** Indicates how up-to-date the data is with respect to the real-world entities or source systems it represents.
**Facet of (DQ Dimension):** Freshness

### DQ Factor: Timeliness
**Semantic:** Indicates whether data is available in time to support its intended use.
**Facet of (DQ Dimension):** Freshness

### DQ Factor: Volatility
**Semantic:** Describes the frequency or rate at which the data changes over time.
**Facet of (DQ Dimension):** Freshness

