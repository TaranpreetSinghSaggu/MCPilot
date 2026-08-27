from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False)
    team = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    commits = relationship("Commit", back_populates="author")
    pull_requests = relationship("PullRequest", back_populates="author")
    reported_issues = relationship(
        "Issue",
        foreign_keys="Issue.reported_by",
        back_populates="reporter",
    )
    assigned_issues = relationship(
        "Issue",
        foreign_keys="Issue.assignee_id",
        back_populates="assignee",
    )
    deployments = relationship(
        "Deployment",
        foreign_keys="Deployment.deployed_by",
        back_populates="deployer",
    )


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text)
    language = Column(String(50), nullable=False)
    team = Column(String(100), nullable=False)
    visibility = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    commits = relationship("Commit", back_populates="repository")
    pull_requests = relationship("PullRequest", back_populates="repository")
    issues = relationship("Issue", back_populates="repository")
    services = relationship("Service", back_populates="repository")
    builds = relationship("BuildRun", back_populates="repository")


class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True)
    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False,
    )
    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    commit_hash = Column(String(40), unique=True, nullable=False)
    message = Column(Text, nullable=False)
    lines_added = Column(Integer, nullable=False)
    lines_deleted = Column(Integer, nullable=False)
    committed_at = Column(DateTime, nullable=False)

    repository = relationship("Repository", back_populates="commits")
    author = relationship("User", back_populates="commits")


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True)
    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False,
    )
    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)
    merged_at = Column(DateTime)
    review_count = Column(Integer, default=0, nullable=False)
    changed_files = Column(Integer, default=0, nullable=False)
    lines_added = Column(Integer, default=0, nullable=False)
    lines_deleted = Column(Integer, default=0, nullable=False)

    repository = relationship("Repository", back_populates="pull_requests")
    author = relationship("User", back_populates="pull_requests")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False,
    )
    reported_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    assignee_id = Column(
        Integer,
        ForeignKey("users.id"),
    )
    title = Column(String(255), nullable=False)
    priority = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime)

    repository = relationship("Repository", back_populates="issues")
    reporter = relationship(
        "User",
        foreign_keys=[reported_by],
        back_populates="reported_issues",
    )
    assignee = relationship(
        "User",
        foreign_keys=[assignee_id],
        back_populates="assigned_issues",
    )


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False,
    )
    name = Column(String(150), unique=True, nullable=False)
    environment = Column(String(30), nullable=False)
    team = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    repository = relationship("Repository", back_populates="services")
    deployments = relationship("Deployment", back_populates="service")
    incidents = relationship("Incident", back_populates="service")


class BuildRun(Base):
    __tablename__ = "build_runs"

    id = Column(Integer, primary_key=True)
    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False,
    )
    commit_id = Column(
        Integer,
        ForeignKey("commits.id"),
        nullable=False,
    )
    triggered_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    status = Column(String(20), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=False)

    repository = relationship("Repository", back_populates="builds")


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True)
    service_id = Column(
        Integer,
        ForeignKey("services.id"),
        nullable=False,
    )
    commit_id = Column(
        Integer,
        ForeignKey("commits.id"),
        nullable=False,
    )
    environment = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False)
    version = Column(String(100), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    deployed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=False)

    service = relationship("Service", back_populates="deployments")
    deployer = relationship(
        "User",
        foreign_keys=[deployed_by],
        back_populates="deployments",
    )


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    service_id = Column(
        Integer,
        ForeignKey("services.id"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(10), nullable=False)
    status = Column(String(30), nullable=False)
    detected_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime)
    root_cause = Column(Text)

    service = relationship("Service", back_populates="incidents")