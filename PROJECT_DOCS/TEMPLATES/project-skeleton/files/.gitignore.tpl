target/
build/
tmp/
exports/
.env
.env.*
!.env.example
*.class
*.jar
*.war
*.zip
*.tar
*.gz
__pycache__/
**/__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
.idea/
*.iml
.DS_Store

patches/runtime/
patches/logs/accept/
patches/logs/validation/

# Keep the generated bootstrap provenance, ignore later local patch archives.
patches/archives/*
!patches/archives/000001_project_new_bootstrap/
!patches/archives/000001_project_new_bootstrap/manifest.json
!patches/archives/000001_project_new_bootstrap/patch-log.json
