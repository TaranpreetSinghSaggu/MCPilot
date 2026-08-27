from sqlalchemy import create_engine, text

from backend.app.config import DATABASE_URL


engine = create_engine(DATABASE_URL)


with engine.connect() as connection:
    users = connection.execute(
        text("SELECT COUNT(*) FROM users")
    ).scalar()

    repositories = connection.execute(
        text("SELECT COUNT(*) FROM repositories")
    ).scalar()

    services = connection.execute(
        text("SELECT COUNT(*) FROM services")
    ).scalar()

    commits = connection.execute(
        text("SELECT COUNT(*) FROM commits")
    ).scalar()

    pull_requests = connection.execute(
        text("SELECT COUNT(*) FROM pull_requests")
    ).scalar()

    issues = connection.execute(
        text("SELECT COUNT(*) FROM issues")
    ).scalar()

    build_runs = connection.execute(
        text("SELECT COUNT(*) FROM build_runs")
    ).scalar()

    deployments = connection.execute(
        text("SELECT COUNT(*) FROM deployments")
    ).scalar()

    incidents = connection.execute(
        text("SELECT COUNT(*) FROM incidents")
    ).scalar()


print(f"Users: {users}")
print(f"Repositories: {repositories}")
print(f"Services: {services}")
print(f"Commits: {commits}")
print(f"Pull Requests: {pull_requests}")
print(f"Issues: {issues}")
print(f"Build Runs: {build_runs}")
print(f"Deployments: {deployments}")
print(f"Incidents: {incidents}")