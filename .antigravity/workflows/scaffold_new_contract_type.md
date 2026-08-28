# Workflow: SCAFFOLD_NEW_CONTRACT_TYPE

Protocol for introducing a new contract type to the platform (e.g. Lease / Аренда, Employment / Трудовой договор).

## Steps:
1. **Model Definition (`core/models/<type>.py`)**:
   - Create Pydantic model inheriting from `BaseContract`.
   - Define custom items (e.g., property description, stages, salary, deliverables).
   - Define custom terms and validation constraints.
2. **Clause Generation (`core/templates/clauses/<type>.py`)**:
   - Implement legal clause text blocks conforming to Russian Civil Code (ГК РФ).
3. **Registry Registration (`core/templates/registry.py`)**:
   - Register the new model, metadata, display name, and clause factory in `ContractRegistry`.
4. **Rendering Support**:
   - Ensure `docx_engine.py` and `typst_engine.py` handle custom tables and specific clauses.
5. **Adapter Synchronization**:
   - API automatically exposes new type via `/api/contracts/types` and `/api/contracts/schema/<type>`.
   - Web UI & Desktop UI automatically add the contract type to selectors.
   - Telegram Bot adds inline button and FSM wizard handlers.
6. **Automated Tests (`tests/test_contracts_models.py`)**:
   - Add unit test verifying full schema generation, calculations, and docx/pdf output.
