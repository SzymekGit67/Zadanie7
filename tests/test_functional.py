from src.models import Bill, Parameters, TenantSettlement, ApartmentSettlement, Transfer
from src.manager import Manager


def test_settlement_due_between_tanants_and_apartment():
    manager = Manager(Parameters())

    settlement: ApartmentSettlement = manager.get_settlement('apart-polanka', 2025, 1)
    
    tenants_settlements: list[TenantSettlement] = manager.create_tenants_settlements(settlement)
    assert len(tenants_settlements) == 3

    total_due = sum([tenant_settlement.total_due_pln for tenant_settlement in tenants_settlements])
    assert total_due == settlement.total_due_pln

def test_debtors_calculation():
    manager = Manager(Parameters())

    debtors = manager.get_debtors('apart-polanka', 2025, 1)
    assert len(debtors) == 0

    debtors = manager.get_debtors('apart-polanka', 2025, 2)
    assert len(debtors) == 3


def test_tax_calculation():
    manager = Manager(Parameters())
    
    tax = manager.calculate_tax(2025, 1, 0.085)
    assert tax == 638 

    tax = manager.calculate_tax(2025, 2, 0.085)
    assert tax == 0

def test_deposits_calculation():
    manager = Manager(Parameters())
    
    deposit_balance = manager.check_deposits()
    assert deposit_balance == -8700.0 

    manager.transfers.append(Transfer(
        tenant='tenant-1',
        date='2025-01-01',
        settlement_year=None,
        settlement_month=None,
        amount_pln=1000.0,
        type='deposit'
    ))

    deposit_balance = manager.check_deposits()
    assert deposit_balance == -7700.0 

def test_annual_balance_calculation():
    manager = Manager(Parameters())
    
    annual_balance = manager.get_annual_balance(2025)
    assert annual_balance == 6490.0 

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-02-15',
        settlement_year=2025,
        settlement_month=5,
        amount_pln=500.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-02-15',
        settlement_year=2025,
        settlement_month=5,
        amount_pln=4500.0,
        type='renovation'
    ))

    annual_balance = manager.get_annual_balance(2025)
    assert annual_balance == 1490.0 

def test_apartment_has_any_bills():
    manager = Manager(Parameters())
    
    has_bills = manager.has_any_bills('apart-polanka', 2025, 1)
    assert has_bills == True

    has_bills = manager.has_any_bills('apart-polanka', 2025, 3)
    assert has_bills == False


import pytest

def test_blacklist_tenant_verification():
    """
    Test dla Funkcjonalności B (Czarna lista najemców).
    Osoba implementująca kod (Osoba 1) musi:
    1. Utworzyć model `BlacklistEntry` w `src.models` z polami `name` i `reason`.
    2. Dodać obsługę tego modelu w klasie `Manager` (np. wczytywanie do `self.blacklist`).
    3. Napisać metodę `is_tenant_blacklisted(name: str) -> bool` w klasie `Manager`.
    """
    from src.manager import Manager
    from src.models import Parameters
    
    manager = Manager(Parameters())


    try:
        from src.models import BlacklistEntry
    except ImportError:
        pytest.fail("Nie zaimplementowano jeszcze modelu BlacklistEntry w src/models.py")

    manager.blacklist = [
        BlacklistEntry(name="Janusz Niesolidny", reason="Zaległości w czynszu"),
        BlacklistEntry(name="Anna Zła", reason="Zniszczenie mieszkania")
    ]

    
    try:
        assert manager.is_tenant_blacklisted("Janusz Niesolidny") is True, "System powinien wykryć najemcę na czarnej liście"
        assert manager.is_tenant_blacklisted("Anna Zła") is True, "System powinien wykryć najemcę na czarnej liście"
        assert manager.is_tenant_blacklisted("Zwykły Kowalski") is False, "Zwykły najemca nie powinien być na czarnej liście"
    except AttributeError:
        pytest.fail("Brak metody `is_tenant_blacklisted` w klasie Manager")