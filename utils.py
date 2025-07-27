def calculate_net_salary(basic_salary, deductions=0):
    """
    Calculate net salary after deductions
    """
    return basic_salary - deductions

def format_currency(amount):
    """
    Format amount as currency
    """
    return f"{amount:,.2f} ريال"

def calculate_leave_days(start_date, end_date):
    """
    Calculate number of leave days between two dates
    """
    from datetime import timedelta
    return (end_date - start_date).days + 1

def generate_employee_id():
    """
    Generate unique employee ID
    """
    import random
    import string
    return "EMP" + ''.join(random.choices(string.digits, k=3))

def validate_date_range(start_date, end_date):
    """
    Validate that end date is after start date
    """
    return end_date >= start_date