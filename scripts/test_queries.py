from sqlalchemy import create_engine, text

from backend.app.config import DATABASE_URL


engine = create_engine(DATABASE_URL)


queries = {
    "Repositories with most commits": """
        SELECT
            r.name,
            COUNT(c.id) AS commit_count
        FROM repositories r
        LEFT JOIN commits c
            ON c.repository_id = r.id
        GROUP BY r.id, r.name
        ORDER BY commit_count DESC;
    """,

    "Unresolved high priority issues": """
        SELECT
            r.name AS repository,
            i.title,
            i.priority,
            i.status
        FROM issues i
        JOIN repositories r
            ON r.id = i.repository_id
        WHERE i.priority IN ('critical', 'high')
          AND i.status IN ('open', 'in_progress')
        ORDER BY
            CASE i.priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
            END,
            i.created_at DESC;
    """,

    "Failed builds by repository": """
        SELECT
            r.name,
            COUNT(b.id) AS failed_builds
        FROM build_runs b
        JOIN repositories r
            ON r.id = b.repository_id
        WHERE b.status = 'failed'
        GROUP BY r.id, r.name
        ORDER BY failed_builds DESC;
    """,

    "Failed deployments by service": """
        SELECT
            s.name,
            COUNT(d.id) AS failed_deployments
        FROM deployments d
        JOIN services s
            ON s.id = d.service_id
        WHERE d.status IN ('failed', 'rolled_back')
        GROUP BY s.id, s.name
        ORDER BY failed_deployments DESC;
    """,

    "Currently unresolved incidents": """
        SELECT
            s.name AS service,
            i.title,
            i.severity,
            i.status,
            i.detected_at
        FROM incidents i
        JOIN services s
            ON s.id = i.service_id
        WHERE i.status IN ('open', 'investigating')
        ORDER BY i.detected_at DESC;
    """,

    "Build success rate by repository": """
        SELECT
            r.name,
            COUNT(*) AS total_builds,
            COUNT(*) FILTER (
                WHERE b.status = 'success'
            ) AS successful_builds,
            ROUND(
                100.0 *
                COUNT(*) FILTER (
                    WHERE b.status = 'success'
                ) / COUNT(*),
                2
            ) AS success_rate
        FROM build_runs b
        JOIN repositories r
            ON r.id = b.repository_id
        GROUP BY r.id, r.name
        ORDER BY success_rate DESC;
    """,
}


with engine.connect() as connection:

    for title, query in queries.items():

        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)

        result = connection.execute(text(query))

        rows = result.fetchall()

        if not rows:
            print("No results.")
            continue

        for row in rows:
            print(dict(row._mapping))