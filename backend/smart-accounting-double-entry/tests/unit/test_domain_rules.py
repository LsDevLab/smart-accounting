from domain.rules import AccountingValidationRules

def test_balanced_double_entry_validation():
    assert AccountingValidationRules.validate_double_entry(150.0, 150.0) is True
