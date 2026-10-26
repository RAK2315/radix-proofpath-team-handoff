FROM python:3.10-slim-bookworm
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 RADIX_ENV=production RADIX_DATA_DIR=/tmp/proofpath
RUN useradd --create-home --uid 1000 proofpath
WORKDIR /home/proofpath/app
COPY requirements.runtime.lock.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.runtime.lock.txt
COPY --chown=1000:1000 apps ./apps
COPY --chown=1000:1000 shared ./shared
COPY --chown=1000:1000 jd_analytics ./jd_analytics
COPY --chown=1000:1000 resume_parsing ./resume_parsing
COPY --chown=1000:1000 profile_builder ./profile_builder
COPY --chown=1000:1000 talent_check ./talent_check
COPY --chown=1000:1000 skill_matching ./skill_matching
COPY --chown=1000:1000 scripts ./scripts
COPY --chown=1000:1000 data/synthetic/benchmarks.json ./data/synthetic/benchmarks.json
RUN pip install --no-cache-dir --no-deps .
USER 1000
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/api/health', timeout=4)"
CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
