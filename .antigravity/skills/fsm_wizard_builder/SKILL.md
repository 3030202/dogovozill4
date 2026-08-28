---
name: fsm_wizard_builder
description: FSM Wizard pattern for Telegram Bot and CLI interactive step-by-step contract builders
version: 1.0.0
---

# FSM Wizard Builder Specification

## 1. Core Principles
- **Schema-Driven**: Steps and questions are generated from the underlying Pydantic contract model.
- **State Serialization**: Wizard draft state is stored as a JSON object (`storage/drafts/<draft_id>.json`).
- **Interactive Inline Selectors**:
  - Contract Type (Supply, Services, Work, NDA)
  - Party Type (OOO, IP, Self-Employed, Physical Person)
  - VAT Mode (20%, 10%, Without VAT / USN)
  - Payment Terms (100% Prepayment, 50/50 Advance, Postpayment within N business days)
- **Instant Validation**: Check INN, BIK, and dates at each input step. Provide actionable error messages immediately.
- **Immediate Generation**: Generate and send `.docx` and `.pdf` files as telegram attachments upon completing the wizard.
