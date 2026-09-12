from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PricingModel(str, Enum):
    FREE = "FREE"
    FREEMIUM = "FREEMIUM"
    PAID = "PAID"
    ENTERPRISE = "ENTERPRISE"


class Source(BaseModel):
    name: str
    url: str


class StartupContent(BaseModel):
    entityName: str
    employeeCount: Optional[int] = None


class Startup(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "STARTUP"
    source: Source
    content: StartupContent
    collectedAt: datetime


class ProductContent(BaseModel):
    startupName: str
    pricingModel: PricingModel


class Product(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "PRODUCT"
    source: Source
    content: ProductContent
    collectedAt: datetime


class ResearchPaperContent(BaseModel):
    title: str
    authors: List[str]
    paper_url: str
    github_url: Optional[str] = None
    github_stars: Optional[int] = None
    published_date: datetime


class ResearchPaper(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "RESEARCH_PAPER"
    content: ResearchPaperContent
    collectedAt: datetime


class JobContent(BaseModel):
    company: str
    date: datetime
    is_remote: bool
    role_family: str


class Job(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "JOB"
    content: JobContent
    collectedAt: datetime


class NewsContent(BaseModel):
    title: str
    text: str
    date: datetime


class News(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "NEWS"
    source: Source
    content: NewsContent
    collectedAt: datetime