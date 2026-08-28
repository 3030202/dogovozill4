"""Unit tests for DOCX (GOST) and Typst rendering engines."""

import io
import pytest
from core.templates.registry import ContractRegistry
from core.rendering.docx_engine import DocxEngine
from core.rendering.typst_engine import TypstEngine
from core.models.supply import SupplyContract
from core.models.services import ServiceContract
from core.models.work import WorkContract
from core.models.nda import NDAContract


class TestRenderingEngines:
    @pytest.mark.parametrize("contract_type", ["supply", "services", "work", "nda"])
    def test_docx_generation(self, contract_type):
        sample = ContractRegistry.get_sample_contract(contract_type)
        buf = DocxEngine.generate(sample)
        assert isinstance(buf, io.BytesIO)
        content = buf.getvalue()
        # Check ZIP / DOCX magic bytes (PK\x03\x04)
        assert content.startswith(b"PK\x03\x04")
        assert len(content) > 10000

    @pytest.mark.parametrize("contract_type", ["supply", "services", "work", "nda"])
    def test_typst_markup_generation(self, contract_type):
        sample = ContractRegistry.get_sample_contract(contract_type)
        markup = TypstEngine.generate_typst_markup(sample)
        assert isinstance(markup, str)
        assert '#set page(' in markup
        assert 'Liberation Serif' in markup
        assert sample.client.full_name in markup
        assert sample.vendor.full_name in markup

    def test_document_structure_assembly(self):
        sample = ContractRegistry.get_sample_contract("supply")
        doc_struct = ContractRegistry.assemble_document_structure(sample)
        assert "header" in doc_struct
        assert "sections" in doc_struct
        assert "signatures" in doc_struct
        assert len(doc_struct["sections"]) >= 7
