"""
IdentityNumber Value Object - Domain Layer
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityNumber:
    """
    TC Identity Number Value Object.
    
    Domain Rules:
    - Must be exactly 11 digits
    - Cannot start with 0
    - Must pass TC Kimlik No validation algorithm
    - Value is immutable
    """
    value: str
    
    def __post_init__(self):
        """Validate TC identity number on creation."""
        if not self._is_valid_tc_number():
            raise ValueError(f"Invalid TC Identity Number: {self.value}")
    
    def _is_valid_tc_number(self) -> bool:
        """Validate TC identity number using Turkish algorithm."""
        if not self.value or len(self.value) != 11:
            return False
        
        # Must be all digits
        if not self.value.isdigit():
            return False
        
        # Cannot start with 0
        if self.value[0] == '0':
            return False
        
        # TC Kimlik No validation algorithm
        digits = [int(d) for d in self.value]
        
        # Check sum of first 10 digits
        odd_sum = sum(digits[i] for i in range(0, 9, 2))  # 1st, 3rd, 5th, 7th, 9th
        even_sum = sum(digits[i] for i in range(1, 8, 2))  # 2nd, 4th, 6th, 8th
        
        # 10th digit check
        check_digit_10 = ((odd_sum * 7) - even_sum) % 10
        if digits[9] != check_digit_10:
            return False
        
        # 11th digit check
        check_digit_11 = sum(digits[:10]) % 10
        if digits[10] != check_digit_11:
            return False
        
        return True
    
    @classmethod
    def create(cls, value: str) -> 'IdentityNumber':
        """Factory method to create IdentityNumber."""
        cleaned_value = value.strip() if value else ""
        return cls(cleaned_value)
    
    def get_masked_value(self) -> str:
        """Get masked version for logging/display."""
        if len(self.value) != 11:
            return "***"
        return f"{self.value[:3]}****{self.value[7:]}"
    
    def __str__(self) -> str:
        return self.value 