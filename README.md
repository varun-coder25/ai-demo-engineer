# AI Intelligence Data Pipeline

A fault-tolerant data ingestion pipeline for collecting and normalizing AI startups, products, research papers, jobs, and news.

The project is designed around a simple idea: collect data from real sources, preserve the source information, normalize it into consistent schemas, and avoid inventing information when a source does not provide it.

## What the pipeline does

The pipeline currently demonstrates:

- 1,000+ AI startups
- 1,000+ AI products
- 1,000 research papers
- GitHub repository and star metrics for research papers where available
- Fresh AI jobs from 5 different job sources
- Fresh AI news from 5 different news sources
- LLM-based extraction and normalization
- LLM provider fallback
- Exponential backoff with jitter for rate limits
- Chunking for large LLM requests
- Deterministic entity resolution
- Async crawling with bounded concurrency
- Pydantic-based data validation
- Excel export with the required six submission tabs

## Project structure

```text
ai-demo-engineer/
│
├── src/
│   ├── crawler.py
│   ├── parser.py
│   ├── models.py
│   ├── startup_scraper.py
│   ├── paper_scraper.py
│   ├── paper_code_mapping.py
│   ├── github_client.py
│   ├── job_scraper.py
│   ├── merge_jobs.py
│   ├── news_scraper.py
│   ├── news_scraper_verge.py
│   ├── news_scraper_mit.py
│   ├── news_scraper_infoq.py
│   ├── news_scraper_bbc.py
│   ├── merge_news.py
│   ├── process_news_llm.py
│   ├── llm_orchestrator.py
│   ├── test_fallback.py
│   ├── entity_resolution.py
│   ├── normalize_products.py
│   ├── create_submission.py
│   └── create_architecture_pdf.py
│
├── architecture.pdf
├── requirements.txt
├── .gitignore
└── README.md