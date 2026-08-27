import argparse
import random
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.config import DATABASE_URL
from backend.app.models import (
    BuildRun,
    Commit,
    Deployment,
    Incident,
    Issue,
    PullRequest,
    Repository,
    Service,
    User,
)


random.seed(42)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def reset_seed_data(session):
    """Remove existing demo data before reseeding."""

    tables = [
        "incidents",
        "deployments",
        "build_runs",
        "issues",
        "pull_requests",
        "commits",
        "services",
        "repositories",
        "users",
    ]

    for table in tables:
        session.execute(text(f"DELETE FROM {table}"))

    session.commit()

    print("Existing seed data removed.")


def seed_database(reset=False):
    session = SessionLocal()

    try:
        print("Starting database seeding...")

        if reset:
            reset_seed_data(session)

        # -------------------------
        # Users
        # -------------------------

        users = [
            User(
                username="alice",
                email="alice@mcpilot.dev",
                name="Alice Johnson",
                role="Senior Engineer",
                team="Platform",
            ),
            User(
                username="bob",
                email="bob@mcpilot.dev",
                name="Bob Smith",
                role="Software Engineer",
                team="Backend",
            ),
            User(
                username="charlie",
                email="charlie@mcpilot.dev",
                name="Charlie Brown",
                role="DevOps Engineer",
                team="Platform",
            ),
            User(
                username="diana",
                email="diana@mcpilot.dev",
                name="Diana Wilson",
                role="Software Engineer",
                team="Backend",
            ),
            User(
                username="ethan",
                email="ethan@mcpilot.dev",
                name="Ethan Davis",
                role="Software Engineer",
                team="Payments",
            ),
            User(
                username="fiona",
                email="fiona@mcpilot.dev",
                name="Fiona Miller",
                role="QA Engineer",
                team="Quality",
            ),
            User(
                username="george",
                email="george@mcpilot.dev",
                name="George Taylor",
                role="Software Engineer",
                team="Frontend",
            ),
            User(
                username="hannah",
                email="hannah@mcpilot.dev",
                name="Hannah Anderson",
                role="Engineering Manager",
                team="Platform",
            ),
            User(
                username="ivan",
                email="ivan@mcpilot.dev",
                name="Ivan Thomas",
                role="Software Engineer",
                team="Payments",
            ),
            User(
                username="julia",
                email="julia@mcpilot.dev",
                name="Julia Martin",
                role="Security Engineer",
                team="Security",
            ),
        ]

        session.add_all(users)
        session.flush()

        # -------------------------
        # Repositories
        # -------------------------

        repositories = [
            Repository(
                name="mcpilot-api",
                description="Core API and agent backend for MCPilot.",
                language="Python",
                team="Platform",
                visibility="private",
            ),
            Repository(
                name="payment-service",
                description="Handles payment processing and transaction workflows.",
                language="Python",
                team="Payments",
                visibility="private",
            ),
            Repository(
                name="checkout-platform",
                description="Customer checkout and order processing platform.",
                language="TypeScript",
                team="Backend",
                visibility="private",
            ),
            Repository(
                name="observability-agent",
                description="Collects application metrics and operational signals.",
                language="Go",
                team="Platform",
                visibility="private",
            ),
            Repository(
                name="web-dashboard",
                description="Internal engineering dashboard and monitoring UI.",
                language="TypeScript",
                team="Frontend",
                visibility="private",
            ),
        ]

        session.add_all(repositories)
        session.flush()

        # -------------------------
        # Services
        # -------------------------

        services = [
            Service(
                name="mcpilot-api",
                repository_id=repositories[0].id,
                environment="production",
                team="Platform",
            ),
            Service(
                name="payment-api",
                repository_id=repositories[1].id,
                environment="production",
                team="Payments",
            ),
            Service(
                name="payment-worker",
                repository_id=repositories[1].id,
                environment="production",
                team="Payments",
            ),
            Service(
                name="checkout-api",
                repository_id=repositories[2].id,
                environment="production",
                team="Backend",
            ),
            Service(
                name="checkout-worker",
                repository_id=repositories[2].id,
                environment="staging",
                team="Backend",
            ),
            Service(
                name="observability-agent",
                repository_id=repositories[3].id,
                environment="production",
                team="Platform",
            ),
            Service(
                name="web-dashboard",
                repository_id=repositories[4].id,
                environment="production",
                team="Frontend",
            ),
            Service(
                name="web-dashboard-staging",
                repository_id=repositories[4].id,
                environment="staging",
                team="Frontend",
            ),
        ]

        session.add_all(services)
        session.flush()

        # -------------------------
        # Commits
        # -------------------------

        commit_actions = [
            "Add",
            "Fix",
            "Improve",
            "Update",
            "Refactor",
            "Optimize",
            "Remove",
        ]

        commit_components = [
            "API validation",
            "database connection handling",
            "deployment pipeline",
            "authentication middleware",
            "error handling",
            "logging",
            "health checks",
            "configuration management",
            "request processing",
            "service monitoring",
        ]

        commits = []

        for commit_number in range(50):
            repository = random.choice(repositories)
            author = random.choice(users)

            committed_at = datetime.utcnow() - timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            action = random.choice(commit_actions)
            component = random.choice(commit_components)

            commits.append(
                Commit(
                    repository_id=repository.id,
                    author_id=author.id,
                    commit_hash=f"{commit_number + 1:040x}",
                    message=f"{action} {component}",
                    lines_added=random.randint(5, 250),
                    lines_deleted=random.randint(0, 100),
                    committed_at=committed_at,
                )
            )

        session.add_all(commits)
        session.flush()

        # -------------------------
        # Pull Requests
        # -------------------------

        pull_request_titles = [
            "Add deployment health checks",
            "Improve API error handling",
            "Fix database connection timeout",
            "Update authentication flow",
            "Refactor service configuration",
            "Improve CI pipeline reliability",
            "Add request validation",
            "Optimize database queries",
            "Update monitoring configuration",
            "Fix production deployment issue",
            "Improve logging and diagnostics",
            "Add service health endpoint",
        ]

        pull_requests = []

        for _ in range(30):
            repository = random.choice(repositories)
            author = random.choice(users)

            created_at = datetime.utcnow() - timedelta(
                days=random.randint(0, 60),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            status = random.choices(
                ["merged", "open", "closed"],
                weights=[60, 25, 15],
                k=1,
            )[0]

            merged_at = None

            if status == "merged":
                merged_at = created_at + timedelta(
                    hours=random.randint(2, 120)
                )

            pull_requests.append(
                PullRequest(
                    repository_id=repository.id,
                    author_id=author.id,
                    title=random.choice(pull_request_titles),
                    status=status,
                    created_at=created_at,
                    merged_at=merged_at,
                    review_count=random.randint(1, 6),
                    changed_files=random.randint(1, 20),
                    lines_added=random.randint(5, 400),
                    lines_deleted=random.randint(0, 200),
                )
            )

        session.add_all(pull_requests)
        session.flush()

        # -------------------------
        # Issues
        # -------------------------

        issue_titles = [
            "Production API returning elevated 5xx errors",
            "Database connection pool exhausted",
            "Checkout requests timing out",
            "Deployment health check failing",
            "Authentication token expiration issue",
            "Slow payment processing",
            "Missing monitoring alerts",
            "CI pipeline intermittently failing",
            "Incorrect environment configuration",
            "Service memory usage increasing",
            "Dashboard metrics not updating",
            "Retry logic causing duplicate requests",
            "Logging missing request identifiers",
            "Unexpected increase in API latency",
            "Failed background jobs",
        ]

        priorities = [
            "critical",
            "high",
            "medium",
            "low",
        ]

        statuses = [
            "open",
            "in_progress",
            "resolved",
            "closed",
        ]

        issues = []

        for _ in range(30):
            repository = random.choice(repositories)
            reporter = random.choice(users)
            assignee = random.choice(users + [None])

            created_at = datetime.utcnow() - timedelta(
                days=random.randint(0, 75),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            priority = random.choices(
                priorities,
                weights=[10, 25, 45, 20],
                k=1,
            )[0]

            status = random.choices(
                statuses,
                weights=[30, 25, 30, 15],
                k=1,
            )[0]

            resolved_at = None

            if status in ["resolved", "closed"]:
                resolved_at = created_at + timedelta(
                    hours=random.randint(4, 168)
                )

            issues.append(
                Issue(
                    repository_id=repository.id,
                    reported_by=reporter.id,
                    assignee_id=assignee.id if assignee else None,
                    title=random.choice(issue_titles),
                    priority=priority,
                    status=status,
                    created_at=created_at,
                    resolved_at=resolved_at,
                )
            )

        session.add_all(issues)
        session.flush()

        # -------------------------
        # Build Runs
        # -------------------------

        build_runs = []

        for _ in range(60):
            commit = random.choice(commits)

            started_at = commit.committed_at + timedelta(
                minutes=random.randint(2, 180)
            )

            duration_seconds = random.randint(60, 1800)

            finished_at = started_at + timedelta(
                seconds=duration_seconds
            )

            status = random.choices(
                ["success", "failed", "cancelled"],
                weights=[75, 20, 5],
                k=1,
            )[0]

            build_runs.append(
                BuildRun(
                    repository_id=commit.repository_id,
                    commit_id=commit.id,
                    triggered_by=random.choice(users).id,
                    status=status,
                    duration_seconds=duration_seconds,
                    started_at=started_at,
                    finished_at=finished_at,
                )
            )

        session.add_all(build_runs)
        session.flush()

        # -------------------------
        # Deployments
        # -------------------------

        deployments = []

        production_services = [
            service
            for service in services
            if service.environment == "production"
        ]

        successful_builds = [
            build
            for build in build_runs
            if build.status == "success"
        ]

        for _ in range(35):
            build = random.choice(successful_builds)

            matching_services = [
                service
                for service in production_services
                if service.repository_id == build.repository_id
            ]

            if not matching_services:
                continue

            service = random.choice(matching_services)

            started_at = build.finished_at + timedelta(
                minutes=random.randint(5, 120)
            )

            duration_seconds = random.randint(60, 1200)

            completed_at = started_at + timedelta(
                seconds=duration_seconds
            )

            status = random.choices(
                ["success", "failed", "rolled_back"],
                weights=[80, 12, 8],
                k=1,
            )[0]

            deployments.append(
                Deployment(
                    service_id=service.id,
                    commit_id=build.commit_id,
                    environment=service.environment,
                    status=status,
                    version=f"v{random.randint(1, 8)}."
                    f"{random.randint(0, 20)}."
                    f"{random.randint(0, 50)}",
                    duration_seconds=duration_seconds,
                    deployed_by=random.choice(users).id,
                    started_at=started_at,
                    completed_at=completed_at,
                )
            )

        session.add_all(deployments)
        session.flush()

        # -------------------------
        # Incidents
        # -------------------------

        incident_titles = [
            "Elevated API error rate",
            "Checkout latency spike",
            "Payment processing degradation",
            "Production deployment failure",
            "Database connection failures",
            "Service health check failures",
            "Background worker backlog",
            "Unexpected service restart",
            "Increased request latency",
            "Monitoring alert triggered",
        ]

        incident_descriptions = [
            "Monitoring detected abnormal service behaviour.",
            "Error rates increased above the normal operating range.",
            "The service experienced elevated latency.",
            "A production change caused degraded service behaviour.",
            "Automated monitoring detected repeated failures.",
        ]

        root_causes = [
            "Configuration change",
            "Database connection exhaustion",
            "Application regression",
            "Infrastructure issue",
            "Dependency failure",
            "Resource saturation",
            "Unknown",
        ]

        incidents = []

        for _ in range(20):
            service = random.choice(services)

            detected_at = datetime.utcnow() - timedelta(
                days=random.randint(0, 45),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            status = random.choices(
                ["open", "investigating", "resolved"],
                weights=[20, 25, 55],
                k=1,
            )[0]

            severity = random.choices(
                ["critical", "high", "medium", "low"],
                weights=[10, 25, 50, 15],
                k=1,
            )[0]

            resolved_at = None

            if status == "resolved":
                resolved_at = detected_at + timedelta(
                    minutes=random.randint(30, 720)
                )

            incidents.append(
                Incident(
                    service_id=service.id,
                    title=random.choice(incident_titles),
                    description=random.choice(incident_descriptions),
                    severity=severity,
                    status=status,
                    detected_at=detected_at,
                    resolved_at=resolved_at,
                    root_cause=random.choice(root_causes),
                )
            )

        session.add_all(incidents)
        session.flush()

        # -------------------------
        # Save everything
        # -------------------------

        session.commit()

        print("Seed data completed.")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed the MCPilot development database."
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove existing seed data before inserting fresh data.",
    )

    args = parser.parse_args()

    seed_database(reset=args.reset)