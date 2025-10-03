"""
Validation service for contract constraints and business rules.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

from ..models.contract import Contract, DayStatus

class ValidationService:
    """Service for validating contract constraints and business rules."""
    
    @staticmethod
    def validate_contract(contract: Contract) -> Dict[str, Any]:
        """
        Validate a contract and return validation results.
        
        Returns:
            Dict containing validation results with keys:
            - is_valid: bool
            - violations: List of violation messages
            - warnings: List of warning messages
            - suggestions: List of improvement suggestions
        """
        violations = []
        warnings = []
        suggestions = []
        
        # Check working days balance
        working_balance_result = ValidationService._validate_working_days_balance(contract)
        violations.extend(working_balance_result['violations'])
        warnings.extend(working_balance_result['warnings'])
        suggestions.extend(working_balance_result['suggestions'])
        
        # Check holiday constraints
        holiday_result = ValidationService._validate_holiday_constraints(contract)
        violations.extend(holiday_result['violations'])
        warnings.extend(holiday_result['warnings'])
        suggestions.extend(holiday_result['suggestions'])
        
        # Check contract period
        period_result = ValidationService._validate_contract_period(contract)
        violations.extend(period_result['violations'])
        warnings.extend(period_result['warnings'])
        suggestions.extend(period_result['suggestions'])
        
        # Check day allocations
        allocation_result = ValidationService._validate_day_allocations(contract)
        violations.extend(allocation_result['violations'])
        warnings.extend(allocation_result['warnings'])
        suggestions.extend(allocation_result['suggestions'])
        
        return {
            'is_valid': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    @staticmethod
    def _validate_working_days_balance(contract: Contract) -> Dict[str, List[str]]:
        """Validate working days balance against contract total."""
        violations = []
        warnings = []
        suggestions = []
        
        working_count = contract.working_days_count
        total_allowed = contract.total_days
        
        if working_count > total_allowed:
            violations.append(
                f"Too many working days allocated: {working_count} > {total_allowed}. "
                f"Please reduce by {working_count - total_allowed} days."
            )
        elif working_count < total_allowed:
            remaining = total_allowed - working_count
            if remaining <= 5:
                warnings.append(
                    f"Only {remaining} working days remaining to allocate. "
                    f"Contract must have exactly {total_allowed} working days."
                )
            else:
                warnings.append(
                    f"{remaining} working days still need to be allocated. "
                    f"Contract requires exactly {total_allowed} working days."
                )
            
            suggestions.append(
                f"Consider using the suggestion service to auto-allocate the remaining {remaining} days."
            )
        
        return {
            'violations': violations,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    @staticmethod
    def _validate_holiday_constraints(contract: Contract) -> Dict[str, List[str]]:
        """Validate holiday constraints and rules."""
        violations = []
        warnings = []
        suggestions = []
        
        holiday_periods = contract.get_holiday_periods()
        
        # Check for periods longer than 2 weeks
        max_period_length = 14
        for period in holiday_periods:
            start_date = datetime.strptime(period['start'], '%Y-%m-%d')
            end_date = datetime.strptime(period['end'], '%Y-%m-%d')
            period_length = (end_date - start_date).days + 1
            
            if period_length > max_period_length:
                violations.append(
                    f"Holiday period too long: {period['start']} to {period['end']} "
                    f"({period_length} days). Maximum allowed is {max_period_length} days."
                )
        
        
        # Note: Holiday day warnings removed - holidays are automatically determined 
        # by contract requirements (total_days - working_days), so warning about 
        # holiday days is not relevant as they cannot be controlled by the user.
        
        return {
            'violations': violations,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    @staticmethod
    def _validate_contract_period(contract: Contract) -> Dict[str, List[str]]:
        """Validate contract period and dates."""
        violations = []
        warnings = []
        suggestions = []
        
        start_date = contract.start_datetime
        end_date = contract.end_datetime
        
        # Check if end date is after start date
        if end_date <= start_date:
            violations.append(
                f"Contract end date ({contract.end_date}) must be after start date ({contract.start_date})."
            )
        
        # Check contract duration
        duration_days = (end_date - start_date).days + 1
        if duration_days < contract.total_days:
            violations.append(
                f"Contract period ({duration_days} days) is shorter than required working days ({contract.total_days})."
            )
        
        # Check if contract period is reasonable
        if duration_days > 365:
            warnings.append(
                f"Contract period is very long ({duration_days} days). "
                "Consider breaking into multiple contracts."
            )
        
        # Check for weekend-heavy allocations
        weekend_working_days = 0
        for day_allocation in contract.get_working_days():
            if day_allocation.is_weekend:
                weekend_working_days += 1
        
        if weekend_working_days > 0:
            warnings.append(
                f"{weekend_working_days} working days are allocated to weekends. "
                "This may affect billing and client expectations."
            )
        
        return {
            'violations': violations,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    @staticmethod
    def _validate_day_allocations(contract: Contract) -> Dict[str, List[str]]:
        """Validate individual day allocations."""
        violations = []
        warnings = []
        suggestions = []
        
        # Check for duplicate allocations
        dates_with_allocations = set()
        duplicate_dates = set()
        
        for date_str, day_allocation in contract.days.items():
            if date_str in dates_with_allocations:
                duplicate_dates.add(date_str)
            dates_with_allocations.add(date_str)
        
        if duplicate_dates:
            violations.append(
                f"Duplicate day allocations found for dates: {', '.join(sorted(duplicate_dates))}"
            )
        
        # Check for allocations outside contract period
        out_of_period_dates = []
        for date_str in contract.days.keys():
            date = datetime.strptime(date_str, '%Y-%m-%d')
            if date < contract.start_datetime or date > contract.end_datetime:
                out_of_period_dates.append(date_str)
        
        if out_of_period_dates:
            violations.append(
                f"Day allocations found outside contract period: {', '.join(sorted(out_of_period_dates))}"
            )
        
        # Check for missing allocations in key periods
        working_days = contract.get_working_days()
        if working_days:
            # Check for gaps in working days
            working_dates = [day.date for day in working_days]
            working_dates.sort()
            
            gaps = []
            for i in range(len(working_dates) - 1):
                current_date = datetime.strptime(working_dates[i], '%Y-%m-%d')
                next_date = datetime.strptime(working_dates[i + 1], '%Y-%m-%d')
                gap_days = (next_date - current_date).days - 1
                
                if gap_days > 14:  # Gap of more than 2 weeks
                    gaps.append(f"{working_dates[i]} to {working_dates[i + 1]} ({gap_days} days)")
            
            if gaps:
                warnings.append(
                    f"Large gaps between working periods: {', '.join(gaps)}. "
                    "Consider if this affects project continuity."
                )
        
        return {
            'violations': violations,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    @staticmethod
    def can_save_contract(contract: Contract) -> Tuple[bool, List[str]]:
        """
        Check if a contract can be saved (i.e., meets minimum requirements).
        
        Returns:
            Tuple of (can_save, reasons)
        """
        validation_result = ValidationService.validate_contract(contract)
        
        # Contract can be saved if there are no violations
        can_save = validation_result['is_valid']
        
        if not can_save:
            reasons = validation_result['violations']
        else:
            reasons = []
        
        return can_save, reasons
    
    @staticmethod
    def get_contract_health_score(contract: Contract) -> Dict[str, Any]:
        """
        Get a health score for the contract based on various metrics.
        
        Returns:
            Dict containing health score and breakdown
        """
        validation_result = ValidationService.validate_contract(contract)
        
        # Calculate base score
        base_score = 100
        
        # Deduct points for violations (10 points each)
        score_deduction = len(validation_result['violations']) * 10
        
        # Deduct points for warnings (5 points each)
        score_deduction += len(validation_result['warnings']) * 5
        
        final_score = max(0, base_score - score_deduction)
        
        # Determine health status
        if final_score >= 90:
            health_status = 'Excellent'
        elif final_score >= 80:
            health_status = 'Good'
        elif final_score >= 70:
            health_status = 'Fair'
        elif final_score >= 50:
            health_status = 'Poor'
        else:
            health_status = 'Critical'
        
        return {
            'score': final_score,
            'status': health_status,
            'violations_count': len(validation_result['violations']),
            'warnings_count': len(validation_result['warnings']),
            'suggestions_count': len(validation_result['suggestions']),
            'details': validation_result
        }
