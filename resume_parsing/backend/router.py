from resume_parsing.backend.service import extract
from shared.integrations.extraction_routes import extraction_router

router = extraction_router("/api/resumes", "resume", extract)
