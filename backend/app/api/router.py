from fastapi import APIRouter

from backend.app.api.builds import router as builds_router
from backend.app.api.deployments import router as deployments_router
from backend.app.api.incidents import router as incidents_router
from backend.app.api.issues import router as issues_router
from backend.app.api.repositories import router as repositories_router

from backend.app.api.agent import router as agent_router

router = APIRouter(prefix="/api")

router.include_router(repositories_router)
router.include_router(issues_router)
router.include_router(builds_router)
router.include_router(deployments_router)
router.include_router(incidents_router)
router.include_router(agent_router)