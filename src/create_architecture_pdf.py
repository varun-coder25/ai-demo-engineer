import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


OUTPUT_FILE = "architecture.pdf"


def build_pdf():
    os.makedirs("data/output", exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=13 * mm,
        bottomMargin=13 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=19,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=14,
        spaceBefore=6,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
        spaceAfter=4
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=9.5,
        spaceAfter=2
    )

    story = []

    story.append(
        Paragraph(
            "AI Intelligence Graph — Production Architecture",
            title_style
        )
    )

    story.append(
        Paragraph(
            "<b>Goal:</b> Build a fault-tolerant ingestion platform that "
            "can scale from the demonstrated 1K+ entity datasets to "
            "500K+ records without application-code changes.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "1. End-to-End Architecture",
            heading_style
        )
    )

    architecture = [
        ["Layer", "Design"],
        [
            "Discovery",
            "Source registry stores crawl targets, source type, "
            "priority, rate limits and freshness policy."
        ],
        [
            "Crawlers",
            "Async asyncio/aiohttp workers for feeds and APIs; "
            "Playwright Async workers for JS-heavy sources."
        ],
        [
            "Queue",
            "Kafka/SQS-style durable queue separates discovery, "
            "fetching, extraction and enrichment."
        ],
        [
            "Raw storage",
            "Object storage keeps immutable HTML, API responses and "
            "crawl metadata for replay and audit."
        ],
        [
            "Extraction",
            "Deterministic parsers first; LLM extraction only where "
            "unstructured text requires semantic normalization."
        ],
        [
            "Validation",
            "Pydantic schemas, URL validation, timestamp checks, "
            "freshness checks and record-level rejection."
        ],
        [
            "Primary DB",
            "PostgreSQL stores canonical entities, source lineage, "
            "timestamps, deduplication keys and relationships."
        ],
        [
            "Graph / Vector",
            "Neo4j for complex entity relationships; pgvector for "
            "semantic retrieval when needed."
        ]
    ]

    table = Table(
        architecture,
        colWidths=[34 * mm, 140 * mm],
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("LEADING", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3)
        ])
    )

    story.append(table)

    story.append(
        Paragraph(
            "2. Scaling to 500K+ Records",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "The crawler and extraction workers are stateless. A durable "
            "queue partitions work by source and record ID, allowing worker "
            "replicas to scale horizontally. Each job has an idempotency key "
            "and checkpoint so failures do not require restarting the entire "
            "crawl. Raw responses are written to object storage before "
            "downstream processing, allowing extraction workers to scale "
            "independently from network crawlers.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "<b>500K execution model:</b> partition source URLs across "
            "workers → asynchronously fetch with bounded concurrency → "
            "persist raw payload → parse/LLM extract → validate → upsert "
            "canonical record. Increasing queue partitions and worker "
            "replicas increases throughput without changing application "
            "logic.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "3. LLM Reliability: 413 and 429",
            heading_style
        )
    )

    llm_table = [
        ["Failure", "Strategy"],
        [
            "413 Payload Too Large",
            "Split input by semantic paragraphs. Start with an 8K "
            "character chunk and halve the chunk size after a 413, "
            "down to a safe minimum. Process smaller chunks independently "
            "and merge validated outputs."
        ],
        [
            "429 Rate Limit",
            "Retry up to 3 times using exponential backoff plus random "
            "jitter: 2^attempt + random(0,1). After retry exhaustion, "
            "fall through to the next provider."
        ],
        [
            "Provider failure",
            "Gemini Flash is primary, Groq is secondary, and DeepSeek "
            "is configured as an optional tertiary provider."
        ],
        [
            "Invalid JSON",
            "Reject the response and fall through/retry rather than "
            "accepting malformed or fabricated data."
        ]
    ]

    llm_table_obj = Table(
        llm_table,
        colWidths=[38 * mm, 136 * mm],
        repeatRows=1
    )

    llm_table_obj.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("LEADING", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3)
        ])
    )

    story.append(llm_table_obj)

    story.append(PageBreak())

    story.append(
        Paragraph(
            "4. Freshness, Deduplication and Distributed Crawling",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Every source record receives a deterministic identity based "
            "on normalized source URL plus a content hash. A distributed "
            "deduplication store such as Redis prevents multiple workers "
            "from processing the same URL simultaneously. PostgreSQL "
            "enforces unique constraints on canonical identifiers and "
            "source URLs.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "For news and jobs, the published timestamp is normalized to "
            "UTC. Records are accepted only when their publication time is "
            "within the configured 24-hour freshness window. When a source "
            "does not expose a strict timestamp, the system records the "
            "heuristic used rather than silently claiming precision.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "<b>Idempotency:</b> source URL + normalized title/content hash "
            "→ deterministic deduplication key → transactional upsert. "
            "This makes retries safe and prevents duplicate records across "
            "distributed crawler nodes.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "5. Anti-Bot and JavaScript-Heavy Sources",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Use direct HTTP requests for APIs/RSS and lightweight HTML "
            "sources. Escalate only blocked or JS-rendered sources to a "
            "bounded Playwright Async browser pool. Respect per-domain "
            "concurrency and delays, reuse browser contexts, and cache "
            "successful responses. Cloudflare/Datadome-protected sources "
            "should be handled through compliant browser automation or "
            "official feeds/APIs rather than attempting to bypass access "
            "controls.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "6. Entity Resolution",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Entity resolution is deterministic: Unicode normalization, "
            "lowercasing, punctuation cleanup and removal of legal suffixes "
            "are followed by lookup against a canonical seed dictionary. "
            "Examples such as OpenAI, OpenAI Inc. and Open AI resolve to "
            "OpenAI. Unmatched values remain unresolved instead of being "
            "guessed. Every mapping retains the raw value, canonical value, "
            "method and source URL for auditability.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "7. Data Quality and Observability",
            heading_style
        )
    )

    quality_points = [
        "Pydantic validation before canonical persistence.",
        "Source URL retained for every record.",
        "Structured retry/error logging.",
        "Freshness checks for jobs and news.",
        "Live GitHub star collection for research repositories.",
        "Dead-letter queue for records that repeatedly fail extraction.",
        "Metrics: fetch latency, status codes, retry counts, extraction "
        "success rate, freshness rejection rate and duplicate rate."
    ]

    for point in quality_points:
        story.append(
            Paragraph(
                "• " + point,
                small_style
            )
        )

    story.append(
        Paragraph(
            "8. Production Storage Choice",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "PostgreSQL is the system of record because the canonical "
            "schemas are relational, require constraints and need reliable "
            "upserts. Object storage preserves raw evidence and enables "
            "reprocessing. Neo4j is appropriate when traversing company ↔ "
            "product ↔ founder ↔ paper relationships becomes a core query "
            "pattern. pgvector can provide semantic search without "
            "introducing a separate vector service at smaller scale.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "Current demonstrated pipeline: 1,000 startups, 1,202 products, "
            "1,000 research papers, 43 fresh jobs and 15 fresh news records. "
            "The architecture separates ingestion, extraction, validation "
            "and storage so these workloads can scale independently.",
            body_style
        )
    )

    doc.build(story)

    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_pdf()