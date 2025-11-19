# Refactoring & Organization Guidelines

## The "Hot/Cold" Rule
When deciding whether to delete a script:
1. Check `git log --oneline -n 1 <filename>`
2. If last edit > 1 year ago: Move to `archive/`.
3. If last edit < 1 week ago: It is critical. Move to `scripts/` and document it.

## The Import Rule
Never move a file without checking what imports it.
- Search: `grep -r "filename_without_extension" .`
- If you move `utils.py` to `src/utils.py`, you must update all `import utils` to `from src import utils`.

## The Documentation Hierarchy
- `README.md`: High level map. How to start.
- `.ai/CONTEXT.md`: For LLMs. Why things exist.
- `docs/`: Detailed human guides.
