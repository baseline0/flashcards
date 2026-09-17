# Wawanesa Interview Prep - Glossary & Learning Plan

**Target Role**: Senior Architect - Data & AI  
**Date Prepared**: 2026-09-17  
**Scope**: Build targeted flashcard glossaries (~50 terms max per topic)

---

## I. Job Requirements Analysis

### From Job Postings:

**Primary Tech Stack:**
1. **Databricks Platform** - Lakehouse architecture, medallion pattern (Bronze/Silver/Gold)
2. **Enterprise Semantic Layer** - Cube, dbt Semantic Layer, MetricFlow
3. **MLOps & Mosaic AI** - MLflow, Databricks Model Serving, Feature Stores
4. **Data Integration** - CDC (Debezium, Fivetran), managed connectors, data sharing
5. **Responsible AI** - SHAP, LIME, bias detection, explainability
6. **BI Tools** - Power BI, Tableau
7. **AWS Services** - SageMaker Pipelines, Bedrock
8. **Insurance Domain** - P&C, loss ratios, claims processing, underwriting

**Business Context:**
- Hub-and-spoke analytics model
- Multi-tenant data governance
- Cross-cloud consumption
- Regulatory compliance (financial services)
- Real-time claims processing
- Model explainability and auditability

---

## II. Current Glossary Inventory

### Existing Glossaries (9 total):

| Domain | File | Terms | Status |
|--------|------|-------|--------|
| Data Engineering | databricks_concepts.json | 16 | ✓ Solid foundation |
| Insurance | underwriting_and_claims.json | 15 | ✓ Good coverage |
| Insurance | property_and_casualty.json | 15 | ✓ Good coverage |
| Cloud Computing | aws_databases_and_analytics.json | 10 | ⚠ Needs expansion for SageMaker/Bedrock |
| Cloud Computing | aws_terminology.json | 6 | ⚠ Minimal coverage |
| Machine Learning | fundamentals.json | 8 | ⚠ Limited for ML responsibilities |
| Software Engineering | model_context_protocol.json | 16 | ⚠ Out of scope for interview |
| Software Engineering | design_patterns.json | 5 | ⚠ Out of scope for interview |
| HPC | parallel_computing.json | 6 | ⚠ Out of scope for interview |

**Total Current Terms**: ~96 terms across 9 glossaries

---

## III. Gap Analysis & New Glossaries Needed

### Priority 1 - High Impact (Required for Interview)

1. **Enterprise Semantic Layer & Metrics** ❌ MISSING
   - Cube.dev, dbt Semantic Layer, MetricFlow
   - Metric centralization, headless BI
   - Federation patterns
   - ~40-50 terms needed

2. **MLOps & Model Serving** ⚠ PARTIAL
   - MLflow concepts (experiments, runs, models, registry)
   - Databricks Model Serving
   - Mosaic AI Platform
   - Feature stores (Tecton, Databricks Feature Store)
   - Model monitoring, drift detection
   - ~40-50 terms needed

3. **Data Integration Patterns** ❌ MISSING
   - Change Data Capture (CDC)
   - Fivetran, Debezium
   - Data sharing, Delta Sharing
   - Real-time ingestion patterns
   - ~30-40 terms needed

4. **Responsible AI & Governance** ❌ MISSING
   - Model explainability (SHAP, LIME)
   - Bias detection and fairness
   - PII masking, data privacy
   - RBAC/ABAC patterns
   - Regulatory compliance in ML
   - ~40-50 terms needed

5. **AWS ML & Analytics** ⚠ PARTIAL
   - SageMaker Pipelines
   - Bedrock (GenAI/LLM)
   - AWS Lambda, DynamoDB
   - Specific database services (RDS, Redshift)
   - ~30-40 terms needed

### Priority 2 - Medium Impact (Good to Have)

6. **Medallion Architecture Deep Dive** ⚠ PARTIAL
   - Expand existing Databricks glossary
   - Bronze/Silver/Gold patterns
   - Delta Lake specifics
   - Schema management
   - ~20-30 terms

7. **BI & Analytics Tools** ❌ MISSING
   - Power BI concepts
   - Tableau architecture
   - DAX, MDX
   - ~20-30 terms

---

## IV. Scraper & Data Collection Strategy

### Phase 1: Authoritative Sources (No Scraper Needed)

**Trusted Public Sources with CC License or Fair Use:**

1. **Databricks Official Docs**
   - URL: https://docs.databricks.com/
   - License: Databricks documentation (check terms)
   - Method: Extract from official tutorials and API docs
   - Attribution: "Databricks Official Documentation"

2. **dbt Documentation** (Apache 2.0 compatible)
   - URL: https://docs.getdbt.com/
   - License: Creative Commons + Dbt Project
   - Method: Extract glossary and tutorial content
   - Attribution: "dbt Project Documentation"

3. **MLflow Documentation** (Apache 2.0)
   - URL: https://mlflow.org/docs/
   - License: MLflow (Apache 2.0)
   - Method: Direct extraction from docs
   - Attribution: "MLflow Official Documentation"

4. **Cube.dev Docs**
   - URL: https://cube.dev/docs/
   - License: Check docs site
   - Method: Curated extraction
   - Attribution: "Cube.dev Official Documentation"

5. **AWS Official Documentation**
   - URL: https://docs.aws.amazon.com/
   - License: Check AWS licensing terms
   - Method: Extract SageMaker, Bedrock sections
   - Attribution: "AWS Official Documentation"

6. **Power BI Documentation**
   - URL: https://learn.microsoft.com/en-us/power-bi/
   - License: Microsoft Learn
   - Method: Extract from tutorials
   - Attribution: "Microsoft Learn Power BI Documentation"

7. **Wikipedia API** (CC BY-SA 3.0)
   - Topics: Machine Learning, Data Science, Insurance concepts
   - License: CC BY-SA 3.0
   - Method: API extraction with proper attribution
   - Attribution: "Wikipedia, The Free Encyclopedia"

### Phase 2: Scraper Tool (if needed)

Build a **lightweight Python scraper** that:

```python
# Pseudocode structure
class GlossaryScraper:
    def scrape_databricks_api_docs(url):
        # Extract API endpoint definitions
        # Parse method signatures, parameters, returns
        # Extract code examples
        return glossary_entries
    
    def scrape_dbt_docs(url):
        # Extract jinja2 functions, SQL utilities
        # Parse command reference
        # Extract examples
        return glossary_entries
    
    def scrape_wikipedia_concepts(topic):
        # Use Wikipedia API (public, CC-licensed)
        # Extract definition + see also links
        # Build concept network
        return glossary_entries
    
    def generate_metadata(entry):
        # Add source URL, access date
        # Add license info
        # Add difficulty level
        # Add category tags
        return enriched_entry
```

### Phase 3: Metadata Requirements (Creative Commons Compliance)

Every glossary entry must have:

```json
{
  "title": "Concept Name",
  "body": "Definition/explanation",
  "metadata": {
    "source": "Source Name",
    "source_url": "URL",
    "license": "CC BY 4.0 / Apache 2.0 / proprietary",
    "attribution": "Author/Company Name",
    "access_date": "2026-09-17",
    "difficulty": "beginner|intermediate|advanced",
    "category": "domain_specific_tag",
    "keywords": ["keyword1", "keyword2"],
    "related_concepts": ["concept1", "concept2"]
  }
}
```

---

## V. Implementation Roadmap

### Week 1: Manual Curation (Best ROI)
1. Review existing glossaries for gaps
2. Manually curate ~50 terms from Databricks official docs
3. Build ~40 terms for MLOps & Model Serving
4. Build ~30 terms for Data Integration Patterns
5. **Estimate**: 8-10 hours, ~120 new quality terms

### Week 2: Scraper Build (if time permits)
1. Build Wikipedia concept scraper (CC-licensed)
2. Build Databricks API docs parser
3. Build dbt docs glossary extractor
4. Automated metadata enrichment
5. **Estimate**: 6-8 hours, ~100+ scraped terms with proper attribution

### Week 3: Gap Filling
1. Add BI tools glossary (Power BI, Tableau)
2. Expand AWS ML services
3. Review and validate all entries
4. Cross-reference between glossaries
5. **Estimate**: 4-6 hours, polish + testing

---

## VI. Quality Checkpoints

- [ ] Every term has proper attribution and source URL
- [ ] License compliance verified for all sources
- [ ] ~50 terms max per glossary file (digestible study sets)
- [ ] Metadata complete (difficulty, category, keywords)
- [ ] Cross-references between related concepts
- [ ] Examples and use cases included where applicable
- [ ] Review against actual job posting keywords

---

## VII. Integration with Study Workflow

**After glossaries are built:**
1. Generate flashcards from glossaries
2. Organize by interview prep sequence
3. Tag with interview question categories
4. Create spaced-repetition schedule
5. Build quiz mode for self-assessment

---

## Notes

- **Focus on breadth first**: Ensure all critical concepts are covered at beginner level
- **Quality over quantity**: Better to have 30 well-explained terms than 100 shallow ones
- **Attribution matters**: Proper source attribution ensures compliance + builds credibility
- **Contextualize to Wawanesa**: Include insurance-specific examples in technical glossaries
