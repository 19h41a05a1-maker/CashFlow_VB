"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List, Any
from decimal import Decimal


# ==================== Base Schemas ====================

class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = Field("asc", regex="^(asc|desc)$")


class StandardResponse(BaseModel):
    """Standard API response wrapper."""
    status: str
    message: str
    data: Optional[Any] = None
    errors: Optional[List[Any]] = None
    meta: Optional[dict] = None


class PaginatedResponse(StandardResponse):
    """Paginated response wrapper."""
    pagination: Optional[dict] = None


# ==================== Authentication Schemas ====================

class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """User registration request schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=12)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    status: str
    role_id: int
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== Account Schemas ====================

class AccountCreateRequest(BaseModel):
    """Account creation request schema."""
    account_number: str = Field(..., min_length=5, max_length=50)
    customer_name: str = Field(..., min_length=1, max_length=255)
    mmi_id: str = Field(..., min_length=1, max_length=50)
    account_type: str = Field(..., min_length=1, max_length=50)
    currency: str = Field("USD", min_length=3, max_length=3)
    
    @validator('account_number')
    def validate_account_number(cls, v):
        """Validate account number format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Account number must be alphanumeric')
        return v


class AccountUpdateRequest(BaseModel):
    """Account update request schema."""
    customer_name: Optional[str] = None
    mmi_id: Optional[str] = None
    account_type: Optional[str] = None
    status: Optional[str] = None


class AccountResponse(BaseModel):
    """Account response schema."""
    id: int
    account_number: str
    customer_name: str
    mmi_id: str
    account_type: str
    currency: str
    status: str
    current_balance: float
    pending_hold_amount: float
    created_at: datetime
    modified_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AccountDetailResponse(AccountResponse):
    """Detailed account response with relationships."""
    total_credits_month: float = 0.0
    total_debits_month: float = 0.0
    active_holds_count: int = 0
    next_hold_expiry: Optional[datetime] = None


# ==================== Credit Schemas ====================

class CreditRecordRequest(BaseModel):
    """Credit recording request schema."""
    account_number: str = Field(..., min_length=5, max_length=50)
    amount: float = Field(..., gt=0)
    transaction_type: str = Field(..., regex="^(ACH_CREDIT|CHEQUE_CREDIT|WIRE_CREDIT|OTHER_CREDIT)$")
    credit_date: datetime
    reference_number: Optional[str] = None
    description: Optional[str] = None


class CreditResponse(BaseModel):
    """Credit response schema."""
    id: int
    transaction_id: str
    account_id: int
    amount: float
    transaction_type: str
    transaction_date: datetime
    status: str
    reference_number: Optional[str]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditWithHoldResponse(CreditResponse):
    """Credit response with hold information."""
    hold_id: Optional[str] = None
    hold_status: Optional[str] = None
    hold_expiry_date: Optional[datetime] = None
    days_remaining: Optional[int] = None


# ==================== Hold Schemas ====================

class HoldWaiverRequest(BaseModel):
    """Hold waiver request schema."""
    waiver_reason: str = Field(..., min_length=10, max_length=500)


class HoldEarlyReleaseRequest(BaseModel):
    """Hold early release request schema."""
    early_release_reason: str = Field(..., min_length=10, max_length=500)


class HoldResponse(BaseModel):
    """Hold response schema."""
    id: int
    hold_id: str
    account_id: int
    hold_amount: float
    hold_start_date: datetime
    hold_expiry_date: datetime
    hold_status: str
    business_days_count: int
    days_remaining: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class HoldDetailResponse(HoldResponse):
    """Detailed hold response."""
    credit_transaction_id: int
    hold_reason: Optional[str]
    waiver_reason: Optional[str]
    waiver_at: Optional[datetime]
    early_release_reason: Optional[str]
    early_release_at: Optional[datetime]


# ==================== Debit Schemas ====================

class DebitRequestCreateRequest(BaseModel):
    """Debit request creation schema."""
    account_number: str = Field(..., min_length=5, max_length=50)
    debit_amount: float = Field(..., gt=0)
    debit_type: str = Field(..., regex="^(ACH_DEBIT|WIRE_TRANSFER|CHEQUE_PAYMENT|MANUAL_DEBIT)$")
    beneficiary_name: Optional[str] = None
    beneficiary_account: Optional[str] = None
    purpose: Optional[str] = None
    priority: str = Field("NORMAL", regex="^(NORMAL|URGENT|ROUTINE)$")


class DebitApprovalRequest(BaseModel):
    """Debit approval request schema."""
    hold_check_passed: bool = True


class DebitRejectionRequest(BaseModel):
    """Debit rejection request schema."""
    rejection_reason: str = Field(..., min_length=10, max_length=500)


class HoldCheckResponse(BaseModel):
    """Hold check response for debit."""
    account_id: int
    has_active_holds: bool
    active_holds_count: int
    pending_hold_amount: float
    available_balance: float
    hold_status: str
    hold_expiry_date: Optional[datetime]
    can_process_debit: bool
    message: str


class DebitResponse(BaseModel):
    """Debit response schema."""
    id: int
    debit_id: str
    account_id: int
    debit_amount: float
    debit_type: str
    status: str
    beneficiary_name: Optional[str]
    beneficiary_account: Optional[str]
    priority: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DebitDetailResponse(DebitResponse):
    """Detailed debit response."""
    purpose: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejected_by: Optional[int]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]
    hold_check_passed: bool


# ==================== Report Schemas ====================

class AccountStatusReportRequest(BaseModel):
    """Account status report request."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    account_numbers: Optional[List[str]] = None
    status_filter: Optional[str] = None


class HoldStatusReportRequest(BaseModel):
    """Hold status report request."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    hold_status: Optional[str] = None
    expiring_within_days: Optional[int] = None


class DebitProcessingReportRequest(BaseModel):
    """Debit processing report request."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status_filter: Optional[str] = None


class ComplianceReportRequest(BaseModel):
    """Compliance report request."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_waivers: bool = True
    include_audit_trail: bool = True


class ReportExportRequest(BaseModel):
    """Report export request."""
    report_type: str = Field(..., regex="^(CSV|EXCEL|PDF)$")
    report_data: dict


# ==================== Audit Log Schemas ====================

class AuditLogResponse(BaseModel):
    """Audit log response schema."""
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: Optional[int]
    old_values: Optional[dict]
    new_values: Optional[dict]
    ip_address: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Analytics Schemas ====================

class AnalyticsMetrics(BaseModel):
    """Analytics metrics schema."""
    total_credits_ytd: float
    total_debits_ytd: float
    active_holds_count: int
    pending_hold_amount: float
    average_hold_duration_days: float
    hold_waiver_rate_percent: float
    debit_approval_rate_percent: float
    total_transactions_processed: int
    processing_time_avg_seconds: float


class DashboardMetrics(BaseModel):
    """Dashboard metrics schema."""
    total_accounts: int
    total_credits: float
    total_debits: float
    active_holds: int
    pending_hold_amount: float
    processing_debits: int
    average_response_time_ms: float
    system_health: str


# ==================== Error Schemas ====================

class ErrorDetail(BaseModel):
    """Error detail schema."""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    status: str = "ERROR"
    message: str
    errors: List[ErrorDetail]
    request_id: Optional[str] = None
