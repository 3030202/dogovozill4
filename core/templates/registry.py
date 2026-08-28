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
from core.models.lease import LeaseContract, LeaseObject, LeaseTerms
from core.models.license_sw import LicenseSWContract, SoftwareDeliverable, LicenseTerms, LicenseType
from core.models.freelance import FreelanceContract, FreelanceTask, FreelanceTerms

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
from core.templates.clauses.lease_subject import build_lease_subject_clauses, build_lease_terms_clauses
from core.templates.clauses.license_subject import build_license_subject_clauses
from core.templates.clauses.freelance_subject import build_freelance_subject_clauses


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
        "lease": LeaseContract,
        "license_sw": LicenseSWContract,
        "freelance": FreelanceContract,
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
        "lease": {
            "title": "Договор аренды имущества / оборудования",
            "category": "Аренда и недвижимость",
            "law_reference": "ГК РФ гл. 34 (ст. 606–670)",
            "description": "Передача оборудования, офисных, складских или производственных помещений во временное пользование с актом приёма-передачи и обеспечительным платежом.",
            "icon": "key",
        },
        "license_sw": {
            "title": "Лицензионный договор на ПО / SaaS-оферта",
            "category": "IT и интеллектуальная собственность",
            "law_reference": "ГК РФ ч. IV, ст. 1235–1238",
            "description": "Предоставление прав на использование ПО, облачных сервисов, SaaS-платформ с условиями SLA и техподдержки.",
            "icon": "code-bracket",
        },
        "freelance": {
            "title": "Договор ГПХ с самозанятым / ИП (фриланс)",
            "category": "Фриланс и самозанятые",
            "law_reference": "ГК РФ гл. 39, ФЗ № 422-ФЗ",
            "description": "Договор ГПХ с защитой от переквалификации, чеком НПД (ФЗ 422-ФЗ) и автоматической передачей исключительных прав.",
            "icon": "user-circle",
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
        if isinstance(contract, LeaseContract):
            subject_clauses = build_lease_subject_clauses(contract)
        elif isinstance(contract, LicenseSWContract):
            subject_clauses = build_license_subject_clauses(contract)
        elif isinstance(contract, FreelanceContract):
            subject_clauses = build_freelance_subject_clauses(contract)
        else:
            subject_clauses = build_subject_clauses(contract)

        sections.append({
            "section_num": "1",
            "title": "ПРЕДМЕТ ДОГОВОРА",
            "clauses": subject_clauses,
        })

        # Section 2: Price & Payments
        sections.append({
            "section_num": "2",
            "title": "ЦЕНА ДОГОВОРА И ПОРЯДОК РАСЧЕТОВ" if contract_type not in ("nda",) else "ФИНАНСОВЫЕ УСЛОВИЯ",
            "clauses": build_payment_clauses(contract),
        })

        # Section 3: Delivery / Acceptance / Execution
        s3_titles = {
            "supply": "УСЛОВИЯ И СРОКИ ПОСТАВКИ ТОВАРА",
            "services": "ПОРЯДОК ОКАЗАНИЯ И СДАЧИ-ПРИЕМКИ УСЛУГ",
            "work": "ПОРЯДОК ВЫПОЛНЕНИЯ И ПРИЕМКИ РАБОТ",
            "lease": "УСЛОВИЯ ПЕРЕДАЧИ, ПОЛЬЗОВАНИЯ И ВОЗВРАТА ИМУЩЕСТВА",
            "license_sw": "ПОРЯДОК ПРЕДОСТАВЛЕНИЯ ДОСТУПА И ТЕХНИЧЕСКОЙ ПОДДЕРЖКИ",
            "freelance": "ПОРЯДОК ВЫПОЛНЕНИЯ ЗАДАНИЙ И СДАЧИ-ПРИЕМКИ РЕЗУЛЬТАТОВ",
        }
        s3_title = s3_titles.get(contract_type, "ПОРЯДОК ПЕРЕДАЧИ И ОБРАЩЕНИЯ С ИНФОРМАЦИЕЙ")

        # For lease, delivery_acceptance clauses come from lease_terms_clauses
        if isinstance(contract, LeaseContract):
            s3_clauses = build_lease_terms_clauses(contract)
        else:
            s3_clauses = build_delivery_acceptance_clauses(contract)

        sections.append({
            "section_num": "3",
            "title": s3_title,
            "clauses": s3_clauses,
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
                account="40702810938000012345",
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
                account="40702810401400005678",
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

        elif contract_type == "lease":
            return LeaseContract(
                metadata=ContractMetadata(
                    contract_number="2025/А-07",
                    contract_date="2025-03-01",
                    city="г. Москва",
                    valid_until="до 28 февраля 2026 года",
                ),
                client=client,
                vendor=vendor,
                vat_rate=20,
                vat_included=True,
                lease_object=LeaseObject(
                    name="Сервер HPE ProLiant DL380 Gen10 (2x Xeon Gold 6230, 256GB RAM, 10TB NVMe)",
                    inventory_number="ИНВ-00128",
                    location="117342, г. Москва, ул. Бутлерова, д. 17, серверная комната 2Б",
                    condition="исправное, полностью работоспособное, соответствующее паспортным характеристикам",
                    market_value_rubles=850000.0,
                ),
                lease_terms=LeaseTerms(
                    rent_period_months=12,
                    monthly_rent_rubles=25000.0,
                    security_deposit_months=2.0,
                    utilities_by_tenant=True,
                    sublease_allowed=False,
                ),
            )

        elif contract_type == "license_sw":
            return LicenseSWContract(
                metadata=ContractMetadata(
                    contract_number="2025/Л-03",
                    contract_date="2025-04-01",
                    city="г. Москва",
                    valid_until="до 31 марта 2026 года",
                ),
                client=client,
                vendor=vendor,
                vat_rate=0,
                is_exempt_vat=True,
                license_fee=180000.0,
                fee_type="единовременно",
                software=[
                    SoftwareDeliverable(
                        name="DocGen Enterprise Platform",
                        version="2.0",
                        registration_number="2025611234",
                        delivery_method="облачный доступ (SaaS)",
                    ),
                ],
                license_terms=LicenseTerms(
                    license_type=LicenseType.SIMPLE,
                    territory="Российская Федерация",
                    period_months=12,
                    allowed_users=50,
                    source_code_included=False,
                    modification_allowed=False,
                    sla_uptime_percent=99.5,
                    support_included=True,
                    support_response_hours=8,
                ),
            )

        elif contract_type == "freelance":
            return FreelanceContract(
                metadata=ContractMetadata(
                    contract_number="2025/ГПХ-12",
                    contract_date="2025-05-01",
                    city="г. Москва",
                    valid_until="до 31 мая 2025 года",
                ),
                client=client,
                vendor=Party(
                    party_type=PartyType.SELF_EMPLOYED,
                    full_name="Петров Иван Сергеевич",
                    short_name="Петров И.С.",
                    inn="770708389324",  # Valid 12-digit individual INN
                    legal_address="г. Москва, ул. Тверская, д. 1, кв. 10",
                    signatory_position="Самозанятый",
                    signatory_name="Петров Иван Сергеевич",
                    signatory_basis="лично",
                    bank_requisites=BankRequisites(
                        bik="044525225",
                        bank_name="ПАО СБЕРБАНК г. Москва",
                        account="40817810938000012346",
                        corr_account="30101810400000000225",
                    ),
                    email="ivan.petrov@gmail.com",
                ),
                vat_rate=0,
                is_exempt_vat=True,
                tasks=[
                    FreelanceTask(
                        name="Разработка REST API на FastAPI (10 эндпоинтов)",
                        description="Проектирование и реализация OpenAPI-совместимого бэкенда с тестами",
                        cost=80000.0,
                        deadline_days=14,
                    ),
                    FreelanceTask(
                        name="Написание технической документации (Swagger + README)",
                        description="Оформление документации по ГОСТ 19.505-79",
                        cost=20000.0,
                        deadline_days=5,
                    ),
                ],
                freelance_terms=FreelanceTerms(
                    is_self_employed=True,
                    check_receipt_required=True,
                    ip_rights_transfer=True,
                    no_employment_relations=True,
                    act_review_days=3,
                ),
            )

        raise ValueError(f"Unknown contract type: {contract_type}")
