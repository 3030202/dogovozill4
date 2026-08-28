"""Contract Registry and Modular Document Assembler."""

from __future__ import annotations
from typing import Dict, Any, Type, List
from pydantic import BaseModel
from core.models.base import (
    BaseContract, Party, BankRequisites, ContractMetadata,
    PaymentTerms, PenaltyTerms, DisputeResolution, PartyType
)
from core.models.supply import SupplyContract, SupplyItem, DeliveryTerms
from core.models.services import ServiceContract, ServiceItem, ServiceTerms
from core.models.work import WorkContract, WorkStage, WorkTerms
from core.models.nda import NDAContract, NDAScope, NDATerms

from core.templates.clauses.preamble import build_preamble_clauses
from core.templates.clauses.subject import build_subject_clauses
from core.templates.clauses.payment import build_payment_clauses
from core.templates.clauses.delivery_acceptance import build_delivery_acceptance_clauses
from core.templates.clauses.liability import build_liability_clauses
from core.templates.clauses.force_majeure import build_force_majeure_clauses
from core.templates.clauses.confidentiality import build_confidentiality_clauses
from core.templates.clauses.dispute_resolution import build_dispute_resolution_clauses
from core.templates.clauses.term_termination import build_term_termination_clauses
from core.templates.clauses.signatures import build_signatures_block


class ContractTypeInfo(BaseModel):
    key: str
    title: str
    category: str
    law_reference: str
    description: str
    icon: str
    model_class_name: str


class ContractRegistry:
    """Central registry of deterministic contract models, schemas, and clause generators."""

    _models: Dict[str, Type[BaseContract]] = {
        "supply": SupplyContract,
        "services": ServiceContract,
        "work": WorkContract,
        "nda": NDAContract,
    }

    _metadata: Dict[str, Dict[str, str]] = {
        "supply": {
            "title": "Договор поставки товаров",
            "category": "Коммерческие договоры",
            "law_reference": "ГК РФ гл. 30 §3",
            "description": "Поставка оборудования, материалов и товаров с детальной спецификацией и условиями приемки.",
            "icon": "truck",
        },
        "services": {
            "title": "Договор возмездного оказания услуг",
            "category": "Услуги и B2B",
            "law_reference": "ГК РФ гл. 39",
            "description": "Консультационные, маркетинговые, IT или агентские услуги с передачей прав на РИД.",
            "icon": "briefcase",
        },
        "work": {
            "title": "Договор подряда",
            "category": "Работы и производство",
            "law_reference": "ГК РФ гл. 37",
            "description": "Выполнение строительных, проектных, ремонтных работ с календарным планом и гарантией.",
            "icon": "hammer",
        },
        "nda": {
            "title": "Соглашение о конфиденциальности (NDA)",
            "category": "Безопасность и право",
            "law_reference": "ФЗ № 98-ФЗ «О коммерческой тайне»",
            "description": "Охрана коммерческой тайны, исходного кода, клиентских баз и штрафы за разглашение.",
            "icon": "shield-check",
        },
    }

    @classmethod
    def list_types(cls) -> List[ContractTypeInfo]:
        """Return list of all registered contract types with metadata."""
        result = []
        for key, meta in cls._metadata.items():
            model_cls = cls._models.get(key)
            result.append(
                ContractTypeInfo(
                    key=key,
                    title=meta["title"],
                    category=meta["category"],
                    law_reference=meta["law_reference"],
                    description=meta["description"],
                    icon=meta["icon"],
                    model_class_name=model_cls.__name__ if model_cls else "",
                )
            )
        return result

    @classmethod
    def get_model_class(cls, contract_type: str) -> Type[BaseContract]:
        """Get Pydantic model class for contract type."""
        if contract_type not in cls._models:
            raise KeyError(f"Неизвестный тип договора: '{contract_type}'. Доступны: {list(cls._models.keys())}")
        return cls._models[contract_type]

    @classmethod
    def parse_contract(cls, contract_type: str, data: Dict[str, Any]) -> BaseContract:
        """Parse dictionary payload into validated Pydantic contract instance."""
        model_cls = cls.get_model_class(contract_type)
        return model_cls.model_validate(data)

    @classmethod
    def assemble_document_structure(cls, contract: BaseContract) -> Dict[str, Any]:
        """Assemble full structured legal document with numbered sections and paragraphs."""
        contract_type = getattr(contract, "contract_type", "supply")
        meta = cls._metadata.get(contract_type, {"title": "Договор"})
        title = meta["title"]

        preamble = build_preamble_clauses(
            metadata=contract.metadata,
            client=contract.client,
            vendor=contract.vendor,
            contract_type=contract_type,
            contract_title=title,
        )

        sections = []

        # Section 1: Subject
        sections.append({
            "section_num": "1",
            "title": "ПРЕДМЕТ ДОГОВОРА",
            "clauses": build_subject_clauses(contract),
        })

        # Section 2: Price & Payments
        sections.append({
            "section_num": "2",
            "title": "ЦЕНА ДОГОВОРА И ПОРЯДОК РАСЧЕТОВ" if contract_type != "nda" else "ФИНАНСОВЫЕ УСЛОВИЯ",
            "clauses": build_payment_clauses(contract),
        })

        # Section 3: Delivery / Acceptance / Execution
        if contract_type == "supply":
            s3_title = "УСЛОВИЯ И СРОКИ ПОСТАВКИ ТОВАРА"
        elif contract_type == "services":
            s3_title = "ПОРЯДОК ОКАЗАНИЯ И СДАЧИ-ПРИЕМКИ УСЛУГ"
        elif contract_type == "work":
            s3_title = "ПОРЯДОК ВЫПОЛНЕНИЯ И ПРИЕМКИ РАБОТ"
        else:
            s3_title = "ПОРЯДОК ПЕРЕДАЧИ И ОБРАЩЕНИЯ С ИНФОРМАЦИЕЙ"

        sections.append({
            "section_num": "3",
            "title": s3_title,
            "clauses": build_delivery_acceptance_clauses(contract),
        })

        # Section 4: Liability
        sections.append({
            "section_num": "4",
            "title": "ОТВЕТСТВЕННОСТЬ СТОРОН",
            "clauses": build_liability_clauses(contract),
        })

        # Section 5: Force Majeure
        sections.append({
            "section_num": "5",
            "title": "ОБСТОЯТЕЛЬСТВА НЕПРЕОДОЛИМОЙ СИЛЫ (ФОРС-МАЖОР)",
            "clauses": build_force_majeure_clauses(contract),
        })

        # Section 6: Confidentiality (for commercial contracts)
        conf_clauses = build_confidentiality_clauses(contract)
        if conf_clauses:
            sections.append({
                "section_num": "6",
                "title": "КОНФИДЕНЦИАЛЬНОСТЬ",
                "clauses": conf_clauses,
            })

        # Section 7: Dispute Resolution
        sections.append({
            "section_num": str(len(sections) + 1),
            "title": "ПОРЯДОК РАЗРЕШЕНИЯ СПОРОВ",
            "clauses": build_dispute_resolution_clauses(contract),
        })

        # Section 8: Term & Termination
        sections.append({
            "section_num": str(len(sections) + 1),
            "title": "СРОК ДЕЙСТВИЯ И ПОРЯДОК РАСТОРЖЕНИЯ",
            "clauses": build_term_termination_clauses(contract),
        })

        # Signatures
        signatures = build_signatures_block(contract)

        return {
            "metadata": contract.metadata.model_dump(),
            "header": preamble,
            "sections": sections,
            "signatures": signatures,
            "contract": contract,
        }

    @classmethod
    def get_sample_contract(cls, contract_type: str) -> BaseContract:
        """Create sample contract data with valid Russian requisites for tests and defaults."""
        meta = ContractMetadata(
            contract_number="2025/П-01",
            contract_date="2025-02-15",
            city="г. Москва",
            valid_until="до 31 декабря 2025 года",
        )

        client = Party(
            party_type=PartyType.OOO,
            full_name="ООО «АЛЬФА ТЕХНОЛОДЖИС»",
            short_name="ООО «Альфа»",
            inn="7707083893",  # Valid Russian Tax Entity INN (Sberbank / standard LE format)
            kpp="770701001",
            ogrn="1027700132195",
            legal_address="119049, г. Москва, ул. Шаболовка, д. 10, корп. 2, оф. 401",
            actual_address="119049, г. Москва, ул. Шаболовка, д. 10, корп. 2, оф. 401",
            signatory_position="Генеральный директор",
            signatory_name="Алексеев Алексей Алексеевич",
            signatory_basis="Устава",
            bank_requisites=BankRequisites(
                bik="044525225",
                bank_name="ПАО СБЕРБАНК г. Москва",
                account="40702810438000012345",
                corr_account="30101810400000000225",
            ),
            phone="+7 (495) 123-45-67",
            email="info@alpha-tech.ru",
        )

        vendor = Party(
            party_type=PartyType.OOO,
            full_name="ООО «ВЕКТОР РЕШЕНИЙ»",
            short_name="ООО «Вектор»",
            inn="7728168971",  # Valid LE INN
            kpp="772801001",
            ogrn="1027739062860",
            legal_address="117342, г. Москва, ул. Бутлерова, д. 17, оф. 512",
            actual_address="117342, г. Москва, ул. Бутлерова, д. 17, оф. 512",
            signatory_position="Генеральный директор",
            signatory_name="Смирнов Сергей Сергеевич",
            signatory_basis="Устава",
            bank_requisites=BankRequisites(
                bik="044525593",
                bank_name="АО «АЛЬФА-БАНК» г. Москва",
                account="40702810901400005678",
                corr_account="30101810200000000593",
            ),
            phone="+7 (495) 987-65-43",
            email="sales@vector-solutions.ru",
        )

        if contract_type == "supply":
            return SupplyContract(
                metadata=meta,
                client=client,
                vendor=vendor,
                vat_rate=20,
                vat_included=True,
                items=[
                    SupplyItem(name="Серверный шкаф 42U 600x1000", unit="шт.", quantity=2, price_per_unit=45000.0),
                    SupplyItem(name="Источник бесперебойного питания 3000VA", unit="шт.", quantity=2, price_per_unit=65000.0),
                    SupplyItem(name="Патч-панель 24 порта Cat 6", unit="шт.", quantity=10, price_per_unit=2500.0),
                ],
                delivery_terms=DeliveryTerms(
                    destination_address="119049, г. Москва, ул. Шаболовка, д. 10, склад №2",
                    delivery_timeframe_days=7,
                    acceptance_days=3,
                ),
            )

        elif contract_type == "services":
            return ServiceContract(
                metadata=meta,
                client=client,
                vendor=vendor,
                vat_rate=20,
                vat_included=True,
                services=[
                    ServiceItem(
                        name="Аудит информационной безопасности сетевой инфраструктуры",
                        description="Комплексный анализ уязвимостей, тестирование на проникновение и отчет с рекомендациями",
                        price=180000.0,
                    ),
                    ServiceItem(
                        name="Настройка системы мониторинга и резервного копирования",
                        description="Развертывание кластера Prometheus/Grafana и политик бэкапа",
                        price=120000.0,
                    ),
                ],
                service_terms=ServiceTerms(
                    service_start_date="2025-03-01",
                    service_end_date="2025-04-15",
                    act_review_days=5,
                    ip_rights_transfer=True,
                ),
            )

        elif contract_type == "work":
            return WorkContract(
                metadata=meta,
                client=client,
                vendor=vendor,
                vat_rate=20,
                vat_included=True,
                work_object_name="Серверная комната и кабельная трасса этажа 4",
                work_location="г. Москва, ул. Шаболовка, д. 10, корп. 2",
                stages=[
                    WorkStage(
                        stage_number=1,
                        title="Монтаж кабельных трасс и серверных шкафов",
                        start_date="2025-03-01",
                        end_date="2025-03-15",
                        cost=150000.0,
                        deliverable_result="Установленные стойки и проложенные лотки",
                    ),
                    WorkStage(
                        stage_number=2,
                        title="Прокладка и расшивка витой пары, сертификация Fluke",
                        start_date="2025-03-16",
                        end_date="2025-03-31",
                        cost=250000.0,
                        deliverable_result="Готовая структурированная кабельная сеть с протоколами тестирования",
                    ),
                ],
                work_terms=WorkTerms(
                    materials_by_contractor=True,
                    warranty_months=24,
                    acceptance_days=5,
                ),
            )

        elif contract_type == "nda":
            return NDAContract(
                metadata=meta,
                client=client,
                vendor=vendor,
                scope=NDAScope(
                    purpose="Обсуждение и разработка совместной архитектуры программного обеспечения",
                ),
                nda_terms=NDATerms(
                    is_bilateral=True,
                    confidentiality_years=3,
                    disclosure_penalty_rubles=500000.0,
                ),
            )

        raise ValueError(f"Unknown contract type: {contract_type}")
