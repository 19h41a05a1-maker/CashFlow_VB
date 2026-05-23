"""
SQLAlchemy ORM models for the database layer.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum


Base = declarative_base()


class TransactionTypeEnum(str, enum.Enum):
    """Enumeration for transaction types."""
    ACH_CREDIT = "ACH_CREDIT"
    CHEQUE_CREDIT = "CHEQUE_CREDIT"
    WIRE_CREDIT = "WIRE_CREDIT"
    OTHER_CREDIT = "OTHER_CREDIT"
    ACH_DEBIT = "ACH_DEBIT"
    WIRE_TRANSFER = "WIRE_TRANSFER"
    CHEQUE_PAYMENT = "CHEQUE_PAYMENT"
    MANUAL_DEBIT = "MANUAL_DEBIT"


class HoldStatusEnum(str, enum.Enum):
    """Enumeration for hold statuses."""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    WAIVED = "WAIVED"
    RELEASED_EARLY = "RELEASED_EARLY"


class AccountStatusEnum(str, enum.Enum):
    """Enumeration for account statuses."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class TransactionStatusEnum(str, enum.Enum):
    """Enumeration for transaction statuses."""
    SUBMITTED = "SUBMITTED"
    PENDING_HOLD = "PENDING_HOLD"
    HOLD_COMPLETED = "HOLD_COMPLETED"
    HOLD_WAIVED = "HOLD_WAIVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class DebitStatusEnum(str, enum.Enum):
    """Enumeration for debit request statuses."""
    SUBMITTED = "SUBMITTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    HOLD_VERIFICATION = "HOLD_VERIFICATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class UserStatusEnum(str, enum.Enum):
    """Enumeration for user statuses."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
    DELETED = "DELETED"


class RoleEnum(str, enum.Enum):
    """Enumeration for user roles."""
    ADMIN = "ADMIN"
    PRODUCTION_MANAGER = "PRODUCTION_MANAGER"
    PRODUCTION_TEAM = "PRODUCTION_TEAM"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    FINANCE_OFFICER = "FINANCE_OFFICER"


class Account(Base):
    """
    Account model representing customer accounts.
    """
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    mmi_id = Column(String(50), nullable=False)
    account_type = Column(String(50), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), default=AccountStatusEnum.ACTIVE.value, index=True)
    current_balance = Column(Float, default=0.0)
    pending_hold_amount = Column(Float, default=0.0)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(Integer, ForeignKey("users.id"))
    modified_at = Column(DateTime, onupdate=datetime.utcnow)
    
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    holds = relationship("Hold", back_populates="account", cascade="all, delete-orphan")
    debits = relationship("DebitRequest", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Account(account_number={self.account_number}, customer_name={self.customer_name})>"


class User(Base):
    """
    User model representing system users.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    status = Column(String(20), default=UserStatusEnum.ACTIVE.value)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    is_deleted = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"


class Role(Base):
    """
    Role model for RBAC.
    """
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    permissions = Column(Text)  # JSON string of permissions
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    def __repr__(self) -> str:
        return f"<Role(role_name={self.role_name})>"


class Transaction(Base):
    """
    Transaction model representing all account transactions.
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False, index=True)
    processing_date = Column(DateTime)
    status = Column(String(20), nullable=False, index=True)
    reference_number = Column(String(100))
    description = Column(String(500))
    related_hold_id = Column(Integer, ForeignKey("holds.id"))
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(Integer, ForeignKey("users.id"))
    modified_at = Column(DateTime, onupdate=datetime.utcnow)
    
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    hold = relationship("Hold", back_populates="transaction")
    
    def __repr__(self) -> str:
        return f"<Transaction(transaction_id={self.transaction_id}, amount={self.amount})>"


class Hold(Base):
    """
    Hold model representing credit holds.
    """
    __tablename__ = "holds"
    
    id = Column(Integer, primary_key=True, index=True)
    hold_id = Column(String(50), unique=True, nullable=False, index=True)
    credit_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    hold_amount = Column(Float, nullable=False)
    hold_start_date = Column(DateTime, nullable=False)
    hold_expiry_date = Column(DateTime, nullable=False, index=True)
    hold_status = Column(String(20), default=HoldStatusEnum.ACTIVE.value, index=True)
    hold_reason = Column(String(500))
    business_days_count = Column(Integer, default=5)
    
    # Waiver information
    waiver_reason = Column(String(500))
    waiver_by = Column(Integer, ForeignKey("users.id"))
    waiver_at = Column(DateTime)
    
    # Early release information
    early_release_reason = Column(String(500))
    early_release_by = Column(Integer, ForeignKey("users.id"))
    early_release_at = Column(DateTime)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(Integer, ForeignKey("users.id"))
    modified_at = Column(DateTime, onupdate=datetime.utcnow)
    
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="hold")
    account = relationship("Account", back_populates="holds")
    
    def __repr__(self) -> str:
        return f"<Hold(hold_id={self.hold_id}, status={self.hold_status})>"


class DebitRequest(Base):
    """
    Debit request model for debit/disbursement requests.
    """
    __tablename__ = "debit_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    debit_id = Column(String(50), unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    debit_amount = Column(Float, nullable=False)
    debit_type = Column(String(50), nullable=False)
    status = Column(String(20), default=DebitStatusEnum.SUBMITTED.value)
    beneficiary_name = Column(String(255))
    beneficiary_account = Column(String(100))
    purpose = Column(String(500))
    requested_date = Column(DateTime)
    priority = Column(String(20), default="NORMAL")
    
    # Approval information
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(String(500))
    rejected_by = Column(Integer, ForeignKey("users.id"))
    rejected_at = Column(DateTime)
    
    # Hold verification
    hold_check_required = Column(Boolean, default=True)
    hold_check_passed = Column(Boolean, default=False)
    hold_check_details = Column(Text)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(Integer, ForeignKey("users.id"))
    modified_at = Column(DateTime, onupdate=datetime.utcnow)
    
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    account = relationship("Account", back_populates="debits")
    
    def __repr__(self) -> str:
        return f"<DebitRequest(debit_id={self.debit_id}, status={self.status})>"


class AuditLog(Base):
    """
    Audit log model for compliance and auditing.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer)
    old_values = Column(Text)  # JSON
    new_values = Column(Text)  # JSON
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    status = Column(String(20))
    remarks = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(user_id={self.user_id}, action={self.action})>"


class Session(Base):
    """
    Session model for session management.
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<Session(user_id={self.user_id}, session_id={self.session_id})>"


class BusinessHoliday(Base):
    """
    Business holiday model for hold calculation.
    """
    __tablename__ = "business_holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    holiday_date = Column(String(10), unique=True, nullable=False, index=True)  # YYYY-MM-DD
    holiday_name = Column(String(100), nullable=False)
    country = Column(String(50), default="US")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<BusinessHoliday(holiday_date={self.holiday_date}, holiday_name={self.holiday_name})>"


class SystemConfig(Base):
    """
    System configuration model.
    """
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(String(500))
    data_type = Column(String(20))
    is_encrypted = Column(Boolean, default=False)
    description = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<SystemConfig(config_key={self.config_key})>"
