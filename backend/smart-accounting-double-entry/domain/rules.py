class AccountingValidationRules:
    @staticmethod
    def validate_double_entry(debits_sum: float, credits_sum: float) -> bool:
        return abs(debits_sum - credits_sum) < 0.01
