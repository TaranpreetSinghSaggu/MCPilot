from sqlalchemy import create_engine, text

from backend.app.config import DATABASE_URL


engine = create_engine(DATABASE_URL)


checks = [
    (
        "Commits with invalid repository",
        """
        SELECT COUNT(*)
        FROM commits c
        LEFT JOIN repositories r ON r.id = c.repository_id
        WHERE r.id IS NULL
        """,
    ),
    (
        "Commits with invalid author",
        """
        SELECT COUNT(*)
        FROM commits c
        LEFT JOIN users u ON u.id = c.author_id
        WHERE u.id IS NULL
        """,
    ),
    (
        "Pull requests with invalid repository",
        """
        SELECT COUNT(*)
        FROM pull_requests p
        LEFT JOIN repositories r ON r.id = p.repository_id
        WHERE r.id IS NULL
        """,
    ),
    (
        "Pull requests with invalid author",
        """
        SELECT COUNT(*)
        FROM pull_requests p
        LEFT JOIN users u ON u.id = p.author_id
        WHERE u.id IS NULL
        """,
    ),
    (
        "Issues with invalid repository",
        """
        SELECT COUNT(*)
        FROM issues i
        LEFT JOIN repositories r ON r.id = i.repository_id
        WHERE r.id IS NULL
        """,
    ),
    (
        "Issues with invalid reporter",
        """
        SELECT COUNT(*)
        FROM issues i
        LEFT JOIN users u ON u.id = i.reported_by
        WHERE u.id IS NULL
        """,
    ),
    (
        "Issues with invalid assignee",
        """
        SELECT COUNT(*)
        FROM issues i
        LEFT JOIN users u ON u.id = i.assignee_id
        WHERE i.assignee_id IS NOT NULL
          AND u.id IS NULL
        """,
    ),
    (
        "Build runs with invalid commit",
        """
        SELECT COUNT(*)
        FROM build_runs b
        LEFT JOIN commits c ON c.id = b.commit_id
        WHERE c.id IS NULL
        """,
    ),
    (
        "Build runs with invalid repository",
        """
        SELECT COUNT(*)
        FROM build_runs b
        LEFT JOIN repositories r ON r.id = b.repository_id
        WHERE r.id IS NULL
        """,
    ),
    (
        "Deployments with invalid service",
        """
        SELECT COUNT(*)
        FROM deployments d
        LEFT JOIN services s ON s.id = d.service_id
        WHERE s.id IS NULL
        """,
    ),
    (
        "Deployments with invalid commit",
        """
        SELECT COUNT(*)
        FROM deployments d
        LEFT JOIN commits c ON c.id = d.commit_id
        WHERE c.id IS NULL
        """,
    ),
    (
        "Incidents with invalid service",
        """
        SELECT COUNT(*)
        FROM incidents i
        LEFT JOIN services s ON s.id = i.service_id
        WHERE s.id IS NULL
        """,
    ),
]


business_rules = [
    (
        "Resolved issues missing resolved_at",
        """
        SELECT COUNT(*)
        FROM issues
        WHERE status IN ('resolved', 'closed')
          AND resolved_at IS NULL
        """,
    ),
    (
        "Open issues incorrectly have resolved_at",
        """
        SELECT COUNT(*)
        FROM issues
        WHERE status IN ('open', 'in_progress')
          AND resolved_at IS NOT NULL
        """,
    ),
    (
        "Resolved incidents missing resolved_at",
        """
        SELECT COUNT(*)
        FROM incidents
        WHERE status = 'resolved'
          AND resolved_at IS NULL
        """,
    ),
    (
        "Open incidents incorrectly have resolved_at",
        """
        SELECT COUNT(*)
        FROM incidents
        WHERE status IN ('open', 'investigating')
          AND resolved_at IS NOT NULL
        """,
    ),
]


with engine.connect() as connection:
    print("Running database integrity checks...\n")

    failed = False

    for name, query in checks + business_rules:
        result = connection.execute(text(query)).scalar()

        if result == 0:
            print(f"PASS  {name}")
        else:
            print(f"FAIL  {name}: {result}")
            failed = True

    print()

    if failed:
        print("Integrity checks failed.")
        raise SystemExit(1)

    print("All integrity checks passed.")