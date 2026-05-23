# Cash Management - 5 Days Hold Checking System
## Complete End-to-End Requirements Document

**Project Name:** Cash Management - 5 Days Hold Checking System  
**Version:** 1.0.0  
**Date:** May 23, 2026  
**Team:** Production Team - Cash Management Division  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Problem Statement](#business-problem-statement)
3. [Business Objectives](#business-objectives)
4. [Functional Requirements](#functional-requirements)
5. [Non-Functional Requirements](#non-functional-requirements)
6. [Technical Architecture](#technical-architecture)
7. [Technology Stack](#technology-stack)
8. [Database Requirements](#database-requirements)
9. [API Requirements](#api-requirements)
10. [Frontend Requirements](#frontend-requirements)
11. [Security Requirements](#security-requirements)
12. [Authentication & Authorization](#authentication--authorization)
13. [Logging & Auditing](#logging--auditing)
14. [Testing Requirements](#testing-requirements)
15. [Performance Requirements](#performance-requirements)
16. [Production Readiness](#production-readiness)
17. [Integration Requirements](#integration-requirements)
18. [Compliance & Regulatory](#compliance--regulatory)
19. [Data Management](#data-management)
20. [Error Handling & Recovery](#error-handling--recovery)
21. [Deployment & DevOps](#deployment--devops)
22. [Success Criteria](#success-criteria)
23. [Project Deliverables](#project-deliverables)

---

## Executive Summary

This document outlines the complete requirements for building an **automated Cash Management - 5 Days Hold Checking System** that monitors account credits and enforces mandatory five-day hold periods before debit/disbursement processing. The system will replace manual verification processes with an automated, real-time solution that improves efficiency, reduces errors, ensures compliance, and provides production-ready enterprise-grade capabilities.

---

## Business Problem Statement

### Current State
- **Manual Verification Process:** Production team manually verifies account credits for every disbursement request
- **Operational Delays:** Manual checks cause transaction processing delays
- **Error Risk:** High potential for human error in credit verification
- **Compliance Issues:** No automated audit trail for regulatory compliance
- **Resource Overhead:** Significant manual effort required from production team

### Required Change
Implement an automated system that:
- Monitors all account credits (ACH, Cheques, etc.) in real-time
- Automatically verifies the 5-day business day hold period
- Prevents debit/disbursement processing during the hold period
- Provides real-time dashboard visibility
- Maintains complete audit trail
- Integrates with existing accounting systems

### Business Impact
- **Efficiency:** 90% reduction in manual verification time
- **Accuracy:** 100% automated verification with zero human error
- **Compliance:** Complete audit trail for regulatory requirements
- **Speed:** Real-time processing after hold period completion
- **Cost Reduction:** Reduced operational overhead and staff time

---

## Business Objectives

### Primary Objectives
1. **Automate Credit Verification:** Eliminate manual credit verification process
2. **Enforce Hold Period:** Automatically enforce 5 business day hold on all credits
3. **Prevent Unauthorized Debits:** Block disbursement requests during hold period
4. **Real-time Visibility:** Provide production team with real-time account status
5. **Compliance & Audit:** Maintain complete audit trail for regulatory compliance

### Secondary Objectives
1. **System Integration:** Seamlessly integrate with existing accounting systems
2. **User Experience:** Provide intuitive dashboard for production team
3. **Scalability:** Support current and future transaction volumes
4. **Maintainability:** Enterprise-grade codebase for long-term support
5. **Performance:** Sub-second response times for all critical operations

---

## Functional Requirements

### 1. Account Management

#### FR1.1 Account Registration
- **Requirement:** System shall allow authorized users to register new accounts
- **Input:** Account Number, Customer Name, MMI ID, Account Type, Currency
- **Validation:** 
  - Account Number must be unique
  - Account Number format validation (alphanumeric, length constraints)
  - Customer Name required and non-empty
  - MMI ID must follow business format
- **Output:** Account registered with status "ACTIVE"
- **Error Handling:** Duplicate account detection, validation errors

#### FR1.2 Account Information Retrieval
- **Requirement:** System shall retrieve complete account information
- **Input:** Account Number or Account ID
- **Output:** Account details including:
  - Account Number
  - Customer Name
  - MMI ID
  - Account Status
  - Created Date
  - Last Modified Date
  - Current Balance
  - Pending Hold Amount
- **Query Performance:** < 100ms response time

#### FR1.3 Account Status Management
- **Requirement:** System shall manage account status (ACTIVE, INACTIVE, SUSPENDED, CLOSED)
- **Status Transitions:** 
  - ACTIVE → INACTIVE (authorized users only)
  - ACTIVE → SUSPENDED (compliance hold)
  - Any Status → CLOSED (after hold period completion)
- **Audit:** All status changes logged with timestamp and user information

#### FR1.4 Account Deactivation
- **Requirement:** System shall allow deactivation of accounts
- **Conditions:** Can only deactivate if no pending holds
- **Process:** Mark account as INACTIVE, archive related transactions

### 2. Credit Management

#### FR2.1 Credit Transaction Recording
- **Requirement:** System shall record all credit transactions (ACH, Cheques, etc.)
- **Input Fields:**
  - Account Number
  - Credit Amount
  - Transaction Type (ACH_CREDIT, CHEQUE_CREDIT, WIRE_CREDIT, OTHER)
  - Credit Date
  - Reference Number
  - Description
- **Processing:**
  1. Validate credit amount (> 0)
  2. Validate account exists and is ACTIVE
  3. Create Credit transaction record
  4. Calculate hold expiry date (5 business days)
  5. Create Hold record
  6. Update account pending hold amount
  7. Generate audit log entry
- **Transaction Status:** PENDING_HOLD initially

#### FR2.2 Credit Amount Validation
- **Requirement:** System shall validate all credit amounts
- **Rules:**
  - Amount must be positive number (> 0)
  - Amount must not exceed maximum transaction limit
  - Amount precision: 2 decimal places
  - Amount format: Currency-specific validation
- **Error Handling:** Reject invalid amounts with clear error message

#### FR2.3 Business Day Hold Period Calculation
- **Requirement:** System shall accurately calculate 5 business day hold period
- **Business Days Definition:**
  - Monday to Friday (exclude weekends)
  - Exclude public holidays (configurable list)
  - US Federal holidays supported
- **Calculation Method:**
  - Credit received date = Day 0
  - Count 5 business days forward
  - Ignore weekends and holidays
  - Hold expiry = End of Day 5 (11:59:59 PM)
- **Example:**
  - Credit received: Friday, May 23
  - Hold Period: May 23 (Fri), May 24 (Sat-skip), May 25 (Sun-skip), May 26 (Mon), May 27 (Tue), May 28 (Wed), May 29 (Thu), May 30 (Fri)
  - Hold Expiry: Friday, May 30, 11:59:59 PM

#### FR2.4 Hold Period Status Tracking
- **Requirement:** System shall track hold period status in real-time
- **Status States:**
  - PENDING_HOLD: Credit received, hold period active
  - HOLD_COMPLETED: Hold period expired, credit released
  - HOLD_WAIVED: Hold period waived by authorized user (audit required)
  - HOLD_RELEASED_EARLY: Approved early release (with reason)
- **Transitions:**
  - PENDING_HOLD → HOLD_COMPLETED (automatic on Day 5)
  - PENDING_HOLD → HOLD_WAIVED (manual, authorized only)
  - PENDING_HOLD → HOLD_RELEASED_EARLY (manual, with approval)

#### FR2.5 Credit Inquiry
- **Requirement:** System shall provide detailed credit inquiry capabilities
- **Query Parameters:**
  - Account Number (required)
  - Date Range (optional)
  - Transaction Type (optional)
  - Hold Status (optional)
- **Output:** List of credits with:
  - Transaction ID
  - Amount
  - Credit Date
  - Hold Status
  - Hold Expiry Date
  - Days Remaining in Hold
- **Sorting/Filtering:** By amount, date, status
- **Pagination:** Support for large result sets

### 3. Hold Management

#### FR3.1 Automatic Hold Creation
- **Requirement:** System shall automatically create holds for all credits
- **Process:**
  1. Upon credit transaction creation
  2. Calculate hold expiry date
  3. Create HOLD record with status ACTIVE
  4. Link to credit transaction
  5. Update account pending amounts
- **Attributes Tracked:**
  - Hold ID (unique)
  - Credit Transaction ID
  - Account Number
  - Hold Amount
  - Hold Start Date
  - Hold Expiry Date
  - Days Remaining
  - Hold Reason
  - Hold Status

#### FR3.2 Automatic Hold Expiration
- **Requirement:** System shall automatically expire holds on expiry date
- **Process:**
  1. Automated job (scheduled nightly or real-time check)
  2. Check all ACTIVE holds with expiry_date <= today
  3. Update hold status to HOLD_COMPLETED
  4. Release hold amount
  5. Update account available balance
  6. Generate audit log entry
- **Performance:** Process 100,000+ holds daily within SLA

#### FR3.3 Hold Waiver Request
- **Requirement:** System shall allow authorized users to waive holds (emergency situations)
- **Input:** 
  - Hold ID
  - Waiver Reason (required)
  - Approver ID
  - Approval Comments
- **Validation:**
  - User must have WAIVER_APPROVER role
  - Reason must be documented
  - Approval logged
- **Process:**
  1. Validate user authorization
  2. Update hold status to HOLD_WAIVED
  3. Record waiver reason and approver
  4. Update account balance immediately
  5. Generate compliance audit log
  6. Send notification to compliance team
- **Audit Trail:** Complete tracking of waiver decision

#### FR3.4 Early Release Request
- **Requirement:** System shall allow early hold release with approval
- **Conditions:**
  - Only by HOLD_RELEASE_APPROVER role
  - Must provide business justification
  - Manager/Compliance approval required
- **Process:**
  1. Submit early release request with reason
  2. Route to approval queue
  3. Approver reviews and approves/rejects
  4. Update hold status
  5. Release funds if approved
  6. Audit log entry
- **SLA:** Approval decision within 4 business hours

#### FR3.5 Hold Dashboard View
- **Requirement:** Production team dashboard showing all holds
- **Information Displayed:**
  - Account Number
  - Customer Name
  - Hold Amount
  - Hold Status
  - Days Remaining in Hold
  - Hold Start Date
  - Hold Expiry Date
  - Percentage Completion (visual progress bar)
  - Action Buttons (view details, waive if authorized)
- **Filtering:** By account, status, date range
- **Sorting:** By expiry date, amount, days remaining
- **Real-time Updates:** Auto-refresh every 60 seconds

### 4. Debit/Disbursement Processing

#### FR4.1 Debit Request Submission
- **Requirement:** System shall accept debit/disbursement requests
- **Input Fields:**
  - Account Number
  - Debit Amount
  - Debit Type (ACH_DEBIT, WIRE_TRANSFER, CHEQUE_PAYMENT, etc.)
  - Beneficiary Information
  - Purpose/Description
  - Requested Date
  - Priority (NORMAL, URGENT, ROUTINE)
- **Initial Status:** SUBMITTED
- **Validation:**
  - Account exists and is ACTIVE
  - Debit amount positive
  - Debit amount ≤ account balance
  - Account not suspended

#### FR4.2 Hold Verification for Debit
- **Requirement:** System shall verify hold status before processing debit
- **Verification Logic:**
  ```
  IF (Account has ACTIVE holds) THEN
    IF (Debit Amount > (Account Balance - Pending Hold Amount)) THEN
      REJECT debit request
      Return error: "Insufficient funds available. Account has pending holds."
    ELSE IF (Recent credit received within 5 business days) THEN
      REJECT debit request
      Return error: "Cannot process debit. Credit hold period active until [DATE]."
    ELSE
      PROCEED with debit validation
  ELSE
    PROCEED with normal debit validation
  ```
- **Return Information:**
  - Hold Status (ACTIVE/COMPLETED)
  - Hold Expiry Date
  - Minimum Days to Wait
  - Hold Amount

#### FR4.3 Debit Request Approval
- **Requirement:** System shall route debit requests to appropriate approvers
- **Approval Workflow:**
  1. Amount ≤ $10,000: Auto-approved if hold verified
  2. Amount $10,001-$100,000: Requires DEBIT_APPROVER review
  3. Amount > $100,000: Requires MANAGER + DEBIT_APPROVER approval
- **Approval Process:**
  - Route to approver queue
  - Timeout if no action within 24 hours (escalate)
  - Approver reviews hold status, account balance, customer info
  - Approve or reject with reason
- **Notifications:**
  - Approval request notifications
  - Decision notifications
  - Status updates

#### FR4.4 Debit Request Processing
- **Requirement:** System shall process approved debits
- **Process:**
  1. Final hold verification check
  2. Final balance verification
  3. Create debit transaction record
  4. Update account balance (atomic transaction)
  5. If attached to hold, update hold status
  6. Generate audit log
  7. Send confirmation notification
  8. Update account status in dashboard
- **Status:** PROCESSED
- **Failure Handling:** Rollback transaction if any step fails

#### FR4.5 Debit Request Rejection
- **Requirement:** System shall reject debits if holds are active
- **Rejection Reasons:**
  - HOLD_PERIOD_ACTIVE: Credit hold still in effect
  - INSUFFICIENT_FUNDS: Balance insufficient
  - ACCOUNT_INACTIVE: Account not active
  - ACCOUNT_SUSPENDED: Account suspended
  - VALIDATION_FAILED: Request validation failed
- **Notification:** Send rejection reason to requester
- **Retry:** Allow retry once hold is cleared

### 5. Transaction Management

#### FR5.1 Transaction Recording
- **Requirement:** System shall record all transactions with complete details
- **Transaction Types:**
  - CREDIT (ACH, CHEQUE, WIRE_CREDIT, OTHER_CREDIT)
  - DEBIT (ACH_DEBIT, WIRE_TRANSFER, CHEQUE_PAYMENT, MANUAL_DEBIT)
  - HOLD (automatic holds created)
  - WAIVER (hold waivers)
  - RELEASE (early hold releases)
- **Fields Captured:**
  - Transaction ID (unique)
  - Account Number
  - Transaction Type
  - Amount
  - Transaction Date
  - Processing Date
  - Status
  - Reference Number
  - Description
  - Related Hold ID (if applicable)
  - Created By (user ID)
  - Created At (timestamp)
  - Modified By
  - Modified At

#### FR5.2 Transaction History
- **Requirement:** System shall maintain complete transaction history
- **Capabilities:**
  - Retrieve all transactions for an account
  - Filter by date range, type, status, amount
  - Sort by date, amount, type
  - Pagination support
  - Export to CSV/Excel
- **Data Integrity:** Immutable transaction records
- **Retention:** Minimum 7 years retention (regulatory requirement)

#### FR5.3 Transaction Status Tracking
- **Requirement:** System shall track transaction status through lifecycle
- **Status Workflow:**
  - DEBIT: SUBMITTED → APPROVED/REJECTED → PROCESSED/FAILED
  - CREDIT: SUBMITTED → HOLD_CREATED → HOLD_COMPLETED/WAIVED
  - HOLD: ACTIVE → COMPLETED/WAIVED/RELEASED_EARLY
- **Status Transition Logging:** Log all status changes with timestamp

### 6. Reporting & Analytics

#### FR6.1 Account Status Report
- **Requirement:** System shall generate account status reports
- **Report Contents:**
  - Account Number
  - Customer Name
  - Current Balance
  - Pending Hold Amount
  - Available Balance (Current - Pending Holds)
  - Total Credits This Month
  - Total Debits This Month
  - Number of Active Holds
  - Next Hold Expiry Date
- **Format:** PDF, CSV, Excel
- **Scheduling:** On-demand, daily, weekly, monthly

#### FR6.2 Hold Status Report
- **Requirement:** System shall generate hold status reports
- **Report Contents:**
  - Total Active Holds
  - Total Hold Amount
  - Holds by Status (ACTIVE, COMPLETED, WAIVED)
  - Holds by Expiry Date Range
  - Holds expiring in next 1, 2, 3, 5 days
  - Hold waivers this month (with reasons)
  - Hold release approvals
- **Format:** PDF, CSV, Excel
- **Filtering:** By date range, account, status
- **Visualization:** Charts showing hold trends, distribution

#### FR6.3 Debit Processing Report
- **Requirement:** System shall generate debit processing reports
- **Report Contents:**
  - Total Debits Submitted
  - Total Debits Approved
  - Total Debits Rejected
  - Rejection Reasons (count by reason)
  - Average Time to Approval
  - Debits held by credit restriction
  - Compliance with hold policy
- **Format:** PDF, CSV, Excel
- **KPIs:** Processing time, approval rate, hold effectiveness

#### FR6.4 Compliance Report
- **Requirement:** System shall generate compliance audit reports
- **Report Contents:**
  - All credit transactions with hold details
  - All hold waivers with approvers and reasons
  - All early releases with justification
  - All rejected debits due to holds
  - System activity audit log
  - Failed transactions and reasons
- **Format:** PDF with signature block for compliance team
- **Retention:** 7-year archival capability

#### FR6.5 Analytics Dashboard
- **Requirement:** System shall provide analytics dashboard
- **Widgets:**
  - Total Credits (YTD)
  - Total Debits (YTD)
  - Active Holds Count
  - Pending Hold Amount
  - Average Hold Duration
  - Hold Waiver Rate
  - Debit Approval Rate
  - Processing Efficiency Metrics
- **Refresh Rate:** Real-time, with 60-second update cycle
- **Drill-down:** Ability to drill into details from summary metrics

---

## Non-Functional Requirements

### 1. Performance Requirements

#### NFR1.1 Response Time
- **API Response Time (p95):** < 500ms
- **API Response Time (p99):** < 1000ms
- **Dashboard Load Time:** < 2 seconds
- **Report Generation:** < 30 seconds for standard reports
- **Hold Verification:** < 100ms
- **Database Query:** < 200ms for standard queries

#### NFR1.2 Throughput
- **Concurrent Users:** Support 500 concurrent users
- **Transactions Per Second:** 1,000 TPS during peak hours
- **Batch Processing:** 100,000+ transactions per job
- **Report Generation:** 10 concurrent report generations

#### NFR1.3 Scalability
- **Horizontal Scaling:** Backend can scale to 10 servers
- **Load Balancing:** Implement load balancer for API
- **Database Scaling:** Read replicas for reporting
- **Cache Strategy:** Redis caching for frequently accessed data

#### NFR1.4 Resource Utilization
- **CPU:** < 70% utilization under normal load
- **Memory:** < 4GB per API server instance
- **Disk:** Database size < 50GB for initial 5 years of data
- **Network:** Optimized queries to minimize bandwidth

### 2. Reliability & Availability

#### NFR2.1 System Availability
- **Uptime:** 99.9% (43.2 minutes downtime/month allowed)
- **Business Hours:** 99.95% (8:00 AM - 6:00 PM EST, Mon-Fri)
- **RTO (Recovery Time Objective):** < 4 hours
- **RPO (Recovery Point Objective):** < 1 hour (max data loss)

#### NFR2.2 Data Integrity
- **ACID Compliance:** All database transactions must be ACID compliant
- **Backup Strategy:**
  - Full backup: Daily at 2:00 AM EST
  - Incremental backup: Every 4 hours
  - Backup retention: 90 days
  - Geographic redundancy: Backup to secondary location
- **Backup Testing:** Monthly restore tests
- **Data Validation:** Checksums for all critical data

#### NFR2.3 Fault Tolerance
- **Database Failover:** Automatic failover to standby (< 2 minutes)
- **API Failover:** Load balancer automatically routes to healthy instances
- **Circuit Breaker Pattern:** Prevent cascading failures
- **Graceful Degradation:** Continue with reduced functionality if necessary

#### NFR2.4 Disaster Recovery
- **Disaster Recovery Plan:** Documented and tested quarterly
- **Backup Location:** Geographically separated (minimum 100 miles)
- **Recovery Procedures:** Documented and validated
- **Communication Plan:** Notification procedures for outages

### 3. Security Requirements

#### NFR3.1 Data Security
- **Data at Rest:** AES-256 encryption for sensitive data
- **Data in Transit:** TLS 1.2+ for all communications
- **Key Management:** Secure key storage using system key vault
- **Sensitive Fields:** Account numbers, customer names, amounts encrypted
- **PII Protection:** Special handling for personally identifiable information

#### NFR3.2 Access Control
- **Authentication:** JWT-based authentication
- **Authorization:** Role-Based Access Control (RBAC)
- **Session Management:** 
  - Session timeout: 30 minutes of inactivity
  - Maximum session duration: 8 hours
  - Force logout on suspicious activity
- **Audit Trail:** All access logged with user, action, timestamp, IP

#### NFR3.3 Input Validation
- **All Inputs:** Validated at entry point
- **Whitelist Approach:** Only allow expected values
- **Length Limits:** Enforce maximum input lengths
- **Type Validation:** Ensure correct data types
- **Format Validation:** Account numbers, dates, amounts formats
- **SQL Injection Prevention:** Parameterized queries only
- **XSS Prevention:** HTML encoding of user input

#### NFR3.4 API Security
- **Rate Limiting:** 100 requests/minute per user
- **API Key Validation:** Each API call requires valid authentication
- **CORS:** Whitelist allowed origins
- **Request Validation:** Validate all API request parameters
- **Response Sanitization:** Remove sensitive data from responses
- **API Versioning:** Support multiple API versions

#### NFR3.5 File Security
- **File Upload Validation:**
  - Maximum file size: 50MB
  - Allowed extensions: .csv, .xlsx, .xls, .pdf
  - Scan uploaded files for malware
  - Store in secure, isolated directory
- **File Download:** Implement download limits to prevent abuse
- **Temporary Files:** Clean up temporary files after processing

#### NFR3.6 Infrastructure Security
- **Network Security:**
  - Firewall rules to restrict access
  - VPN required for admin access
  - Network segmentation
  - DDoS protection
- **Server Security:**
  - Operating system patches current
  - Unnecessary services disabled
  - SSH key-based access only
  - Intrusion detection system
- **Regular Security Testing:**
  - Quarterly vulnerability scans
  - Annual penetration testing
  - Static code analysis
  - Dependency vulnerability scanning

### 4. Maintainability

#### NFR4.1 Code Quality
- **Code Standards:**
  - PEP 8 compliance for Python
  - Type hints on all functions
  - Docstrings for all public methods
  - Maximum cyclomatic complexity: 10
- **Code Reviews:** 
  - Minimum 2 reviewer approval
  - Review checklist verification
  - Architecture review for major changes
- **Documentation:**
  - API documentation with examples
  - Architecture diagrams
  - Database schema documentation
  - Deployment guide
  - Troubleshooting guide

#### NFR4.2 Logging
- **Structured Logging:** JSON-formatted logs
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Retention:** 90 days in log files, 1 year in database
- **Log Content:**
  - Request/response logging
  - Error stack traces
  - Audit events
  - Performance metrics
- **Centralized Logging:** ElasticSearch/Splunk integration capability

#### NFR4.3 Monitoring
- **Health Checks:**
  - API health check endpoint
  - Database connectivity check
  - External service connectivity check
  - Scheduled every 5 minutes
- **Alerting:**
  - High CPU/Memory usage alerts
  - Database connection pool exhaustion
  - API error rate thresholds
  - Response time degradation
  - Backup failure notifications
- **Dashboards:** Real-time monitoring dashboard for ops team

#### NFR4.4 Version Control
- **Git Repository:** All code in Git with branching strategy
- **Branching:** main, develop, feature/*, hotfix/* branches
- **Commit Messages:** Descriptive commit messages with ticket references
- **Release Management:** Semantic versioning (major.minor.patch)

---

## Technical Architecture

### 1. Layered Architecture

```
┌─────────────────────────────────────┐
│   Presentation Layer (Streamlit)    │
│  ┌─────────────────────────────────┐│
│  │ UI Components │ Forms │ Dashboard││
│  │ Authentication │ Navigation       ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   API Layer (FastAPI)               │
│  ┌─────────────────────────────────┐│
│  │ REST Endpoints │ Request/Response││
│  │ Validation     │ Authentication  ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Service Layer                     │
│  ┌─────────────────────────────────┐│
│  │ Business Logic │ Orchestration   ││
│  │ Validation     │ Processing      ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Repository Layer                  │
│  ┌─────────────────────────────────┐│
│  │ Data Access │ Query Building    ││
│  │ Transactions │ Caching          ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Data Layer (SQLite)               │
│  ┌─────────────────────────────────┐│
│  │ Tables │ Indexes │ Constraints  ││
│  │ Views  │ Stored Procedures      ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### 2. Module Organization

```
cash-management-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app initialization
│   │   ├── config.py                  # Configuration management
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── accounts.py        # Account endpoints
│   │   │   │   ├── credits.py         # Credit endpoints
│   │   │   │   ├── debits.py          # Debit endpoints
│   │   │   │   ├── holds.py           # Hold endpoints
│   │   │   │   ├── reports.py         # Report endpoints
│   │   │   │   ├── auth.py            # Auth endpoints
│   │   │   │   └── health.py          # Health check endpoint
│   │   │   └── responses.py           # Standard API responses
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── account_service.py
│   │   │   ├── credit_service.py
│   │   │   ├── debit_service.py
│   │   │   ├── hold_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── report_service.py
│   │   │   └── business_day_service.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py
│   │   │   ├── account_repository.py
│   │   │   ├── transaction_repository.py
│   │   │   ├── hold_repository.py
│   │   │   ├── user_repository.py
│   │   │   └── audit_repository.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── domain/
│   │   │   │   ├── account.py
│   │   │   │   ├── transaction.py
│   │   │   │   ├── hold.py
│   │   │   │   ├── user.py
│   │   │   │   └── audit.py
│   │   │   └── schemas/
│   │   │       ├── account_schema.py
│   │   │       ├── transaction_schema.py
│   │   │       ├── hold_schema.py
│   │   │       ├── request_schema.py
│   │   │       └── response_schema.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── db.py                  # Database configuration
│   │   │   ├── session.py             # Session management
│   │   │   ├── base.py                # Base model
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── account_model.py
│   │   │       ├── transaction_model.py
│   │   │       ├── hold_model.py
│   │   │       ├── user_model.py
│   │   │       ├── audit_model.py
│   │   │       └── enum.py
│   │   ├── migrations/                # Alembic migrations
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt_handler.py
│   │   │   ├── password_handler.py
│   │   │   ├── rbac.py                # Role-based access control
│   │   │   └── token_manager.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py
│   │   │   ├── request_logging.py
│   │   │   ├── error_handler.py
│   │   │   ├── rate_limit.py
│   │   │   └── cors_middleware.py
│   │   ├── validators/
│   │   │   ├── __init__.py
│   │   │   ├── account_validator.py
│   │   │   ├── transaction_validator.py
│   │   │   ├── hold_validator.py
│   │   │   └── input_validator.py
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   ├── base_exception.py
│   │   │   ├── business_exception.py
│   │   │   ├── validation_exception.py
│   │   │   └── auth_exception.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── business_day.py        # Business day calculations
│   │   │   ├── date_utils.py
│   │   │   ├── encryption.py
│   │   │   ├── constants.py
│   │   │   └── helpers.py
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   └── audit_logger.py
│   │   └── background_tasks/
│   │       ├── __init__.py
│   │       ├── hold_expiry_job.py     # Auto-expire holds
│   │       ├── report_job.py
│   │       └── cleanup_job.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── test_account_service.py
│   │   │   ├── test_credit_service.py
│   │   │   ├── test_hold_service.py
│   │   │   ├── test_debit_service.py
│   │   │   ├── test_validators.py
│   │   │   └── test_auth.py
│   │   ├── integration/
│   │   │   ├── test_account_api.py
│   │   │   ├── test_credit_api.py
│   │   │   ├── test_hold_api.py
│   │   │   ├── test_debit_api.py
│   │   │   └── test_auth_flow.py
│   │   ├── fixtures/
│   │   │   ├── account_fixtures.py
│   │   │   ├── user_fixtures.py
│   │   │   └── transaction_fixtures.py
│   │   └── mocks/
│   │       └── mock_database.py
│   ├── logs/
│   │   └── .gitkeep
│   ├── uploads/
│   │   └── .gitkeep
│   ├── reports/
│   │   └── .gitkeep
│   ├── requirements.txt
│   ├── .env.example
│   ├── .env.production
│   ├── pytest.ini
│   ├── setup.py
│   └── README.md
├── frontend/
│   ├── app.py                         # Streamlit main app
│   ├── pages/
│   │   ├── 1_📊_Dashboard.py
│   │   ├── 2_📋_Accounts.py
│   │   ├── 3_💳_Credits.py
│   │   ├── 4_💰_Debits.py
│   │   ├── 5_🔒_Holds.py
│   │   ├── 6_📈_Reports.py
│   │   ├── 7_⚙️_Settings.py
│   │   └── 8_📝_Audit_Log.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   ├── cards.py
│   │   ├── forms.py
│   │   ├── tables.py
│   │   ├── charts.py
│   │   └── dialogs.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── auth_handler.py
│   │   ├── constants.py
│   │   ├── formatters.py
│   │   └── validators.py
│   ├── styles/
│   │   └── custom.css
│   ├── requirements.txt
│   └── .env.example
├── playwright/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_login_flow.py
│   │   ├── test_account_workflow.py
│   │   ├── test_hold_workflow.py
│   │   ├── test_debit_workflow.py
│   │   └── test_reports.py
│   ├── fixtures/
│   │   └── test_data.py
│   └── requirements.txt
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   ├── SETUP_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── SECURITY.md
├── scripts/
│   ├── startup.sh
│   ├── shutdown.sh
│   ├── backup.sh
│   ├── restore.sh
│   └── migrate.sh
└── README.md
```

---

## Technology Stack

### Backend
- **Framework:** FastAPI 0.100.0+
- **Language:** Python 3.10+
- **ORM:** SQLAlchemy 2.0+
- **Database Driver:** sqlite3 (built-in) / aiosqlite for async
- **Authentication:** PyJWT, python-jose, passlib, bcrypt
- **Validation:** Pydantic v2
- **Async:** asyncio, httpx
- **Logging:** Python logging module, structlog
- **Testing:** pytest, pytest-cov, pytest-asyncio, pytest-mock
- **API Documentation:** FastAPI (built-in Swagger UI)
- **Database Migrations:** Alembic
- **Environment:** python-dotenv

### Frontend
- **Framework:** Streamlit 1.28.0+
- **Language:** Python 3.10+
- **HTTP Client:** requests
- **Data Processing:** pandas, numpy
- **Visualization:** plotly, matplotlib, seaborn
- **File Handling:** openpyxl, python-csv

### Testing
- **Unit Testing:** pytest 7.4+
- **Integration Testing:** pytest 7.4+
- **End-to-End Testing:** Playwright 1.40+
- **Code Coverage:** pytest-cov
- **Mocking:** unittest.mock, pytest-mock, faker

### DevOps & Infrastructure
- **Web Server:** Uvicorn (production ASGI server)
- **Reverse Proxy:** Nginx (optional)
- **Containerization:** Docker (optional)
- **CI/CD:** GitHub Actions (optional)
- **Monitoring:** (Optional) Prometheus, Grafana
- **Logging:** (Optional) ELK Stack, Splunk

### Development Tools
- **Code Formatter:** Black
- **Linter:** Ruff, Flake8
- **Type Checker:** mypy
- **Git:** Version control
- **IDE:** VS Code, PyCharm

---

## Database Requirements

### 1. Entity-Relationship Model

#### Accounts Table
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    mmi_id VARCHAR(50) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'ACTIVE',
    current_balance DECIMAL(15,2) DEFAULT 0,
    pending_hold_amount DECIMAL(15,2) DEFAULT 0,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by INTEGER,
    modified_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (modified_by) REFERENCES users(id)
);
CREATE INDEX idx_account_number ON accounts(account_number);
CREATE INDEX idx_status ON accounts(status);
```

#### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    account_id INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    processing_date TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    reference_number VARCHAR(100),
    description VARCHAR(500),
    related_hold_id INTEGER,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by INTEGER,
    modified_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (related_hold_id) REFERENCES holds(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (modified_by) REFERENCES users(id)
);
CREATE INDEX idx_account_transaction ON transactions(account_id);
CREATE INDEX idx_transaction_type ON transactions(transaction_type);
CREATE INDEX idx_transaction_date ON transactions(transaction_date);
CREATE INDEX idx_transaction_status ON transactions(status);
```

#### Holds Table
```sql
CREATE TABLE holds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hold_id VARCHAR(50) UNIQUE NOT NULL,
    credit_transaction_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    hold_amount DECIMAL(15,2) NOT NULL,
    hold_start_date TIMESTAMP NOT NULL,
    hold_expiry_date TIMESTAMP NOT NULL,
    hold_status VARCHAR(20) DEFAULT 'ACTIVE',
    hold_reason VARCHAR(500),
    business_days_count INTEGER DEFAULT 5,
    waiver_reason VARCHAR(500),
    waiver_by INTEGER,
    waiver_at TIMESTAMP,
    early_release_reason VARCHAR(500),
    early_release_by INTEGER,
    early_release_at TIMESTAMP,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by INTEGER,
    modified_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (credit_transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (waiver_by) REFERENCES users(id),
    FOREIGN KEY (early_release_by) REFERENCES users(id)
);
CREATE INDEX idx_hold_status ON holds(hold_status);
CREATE INDEX idx_hold_expiry ON holds(hold_expiry_date);
CREATE INDEX idx_account_holds ON holds(account_id);
```

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP,
    last_login TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);
```

#### Roles Table
```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(500),
    permissions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

#### Audit Log Table
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    status VARCHAR(20),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at);
```

#### Business Holidays Table
```sql
CREATE TABLE business_holidays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    holiday_date DATE UNIQUE NOT NULL,
    holiday_name VARCHAR(100) NOT NULL,
    country VARCHAR(50) DEFAULT 'US',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_holiday_date ON business_holidays(holiday_date);
```

#### System Configuration Table
```sql
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value VARCHAR(500),
    data_type VARCHAR(20),
    is_encrypted BOOLEAN DEFAULT FALSE,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP
);
```

### 2. Database Constraints
- Foreign key constraints enabled
- NOT NULL constraints on required fields
- UNIQUE constraints on unique fields (account_number, transaction_id, hold_id)
- CHECK constraints on amounts (> 0 for credits/debits)
- CHECK constraints on statuses (enum values)

### 3. Indexing Strategy
- Primary key indexes (auto-created)
- Foreign key indexes
- Composite indexes for frequently filtered combinations
- Partial indexes on active records (WHERE is_deleted = FALSE)

### 4. Performance Optimizations
- Proper index usage for common queries
- Lazy loading of relationships
- Query result pagination
- Connection pooling
- Read replicas for reporting

---

## API Requirements

### API Endpoint Architecture

#### Authentication Endpoints

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh-token
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
GET  /api/v1/auth/me
```

#### Account Management Endpoints

```
POST   /api/v1/accounts                    # Create account
GET    /api/v1/accounts                    # List accounts (paginated, filtered)
GET    /api/v1/accounts/{account_id}       # Get account details
PUT    /api/v1/accounts/{account_id}       # Update account
DELETE /api/v1/accounts/{account_id}       # Soft delete account
GET    /api/v1/accounts/{account_id}/status # Get account status
POST   /api/v1/accounts/{account_id}/deactivate # Deactivate account
```

#### Credit Management Endpoints

```
POST   /api/v1/credits                     # Record new credit
GET    /api/v1/credits                     # List credits (paginated, filtered)
GET    /api/v1/credits/{credit_id}         # Get credit details
GET    /api/v1/accounts/{account_id}/credits # Get credits for account
GET    /api/v1/accounts/{account_id}/hold-status # Check hold status
```

#### Hold Management Endpoints

```
GET    /api/v1/holds                       # List holds (paginated, filtered)
GET    /api/v1/holds/{hold_id}             # Get hold details
GET    /api/v1/accounts/{account_id}/holds # Get holds for account
POST   /api/v1/holds/{hold_id}/waive       # Request hold waiver
POST   /api/v1/holds/{hold_id}/release-early # Request early release
GET    /api/v1/holds/expiring-soon         # Get holds expiring soon
```

#### Debit/Disbursement Endpoints

```
POST   /api/v1/debits                      # Submit debit request
GET    /api/v1/debits                      # List debit requests (paginated)
GET    /api/v1/debits/{debit_id}           # Get debit details
POST   /api/v1/debits/{debit_id}/approve   # Approve debit (if authorized)
POST   /api/v1/debits/{debit_id}/reject    # Reject debit (if authorized)
GET    /api/v1/debits/{debit_id}/hold-check # Check hold status for debit
```

#### Report Endpoints

```
GET    /api/v1/reports/account-status      # Account status report
GET    /api/v1/reports/hold-status         # Hold status report
GET    /api/v1/reports/debit-processing    # Debit processing report
GET    /api/v1/reports/compliance          # Compliance audit report
POST   /api/v1/reports/export              # Export report to file
GET    /api/v1/reports/analytics           # Analytics data
```

#### Health & System Endpoints

```
GET    /api/v1/health                      # Health check
GET    /api/v1/status                      # System status
```

### API Response Format

#### Standard Success Response
```json
{
  "status": "SUCCESS",
  "message": "Operation completed successfully",
  "data": {
    // Response data
  },
  "meta": {
    "timestamp": "2026-05-23T14:30:00Z",
    "request_id": "req_123456",
    "api_version": "v1"
  }
}
```

#### Paginated Response
```json
{
  "status": "SUCCESS",
  "message": "Records retrieved successfully",
  "data": [
    // Array of records
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_records": 150,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  },
  "meta": {
    "timestamp": "2026-05-23T14:30:00Z",
    "request_id": "req_123456"
  }
}
```

#### Error Response
```json
{
  "status": "ERROR",
  "message": "Operation failed",
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Invalid account number format",
      "field": "account_number"
    }
  ],
  "meta": {
    "timestamp": "2026-05-23T14:30:00Z",
    "request_id": "req_123456"
  }
}
```

### API Specifications

#### Pagination Parameters
- **Query Parameters:**
  - `page` (default: 1): Page number
  - `page_size` (default: 20, max: 100): Records per page
  - `sort_by` (optional): Field to sort by
  - `sort_order` (default: asc): Sort direction (asc/desc)

#### Filtering Parameters
- Flexible filter support by any field
- Multiple filter operators: eq, ne, gt, gte, lt, lte, contains, in
- Example: `/api/v1/accounts?status=ACTIVE&created_at__gte=2026-01-01`

#### Authentication
- All endpoints (except /auth/login, /auth/register, /health) require JWT token
- Token in Authorization header: `Authorization: Bearer <token>`
- Token expiration: 24 hours
- Refresh token expiration: 7 days

---

## Frontend Requirements

### Streamlit Application Structure

#### Pages & Navigation

1. **Login Page** (`app.py`)
   - Username/password input
   - Remember me option
   - Forgot password link
   - Login error handling
   - Session initialization

2. **Dashboard Page** (`pages/1_📊_Dashboard.py`)
   - Key metrics cards:
     - Total Accounts
     - Active Holds
     - Pending Hold Amount
     - Processed Debits Today
   - Charts:
     - Credit trends (last 30 days)
     - Hold distribution by status
     - Debit approval rate
   - Real-time notifications
   - Quick actions

3. **Accounts Page** (`pages/2_📋_Accounts.py`)
   - Account list with pagination
   - Search/filter by account number, customer name
   - Account details modal
   - Create new account form
   - Edit account form
   - View account transactions
   - Status indicators

4. **Credits Page** (`pages/3_💳_Credits.py`)
   - Credit transaction list
   - Filter by account, date, amount
   - Record new credit form
   - Credit details view
   - Hold information display
   - Bulk credit import

5. **Debits Page** (`pages/4_💰_Debits.py`)
   - Debit request list
   - Filter by account, status, date
   - Submit debit request form
   - Hold verification indicator
   - Approval status tracking
   - Rejection reasons display

6. **Holds Page** (`pages/5_🔒_Holds.py`)
   - All active holds list
   - Filter by status, expiry date
   - Hold details view
   - Days remaining progress bar
   - Waive hold form (if authorized)
   - Early release request form
   - Hold history

7. **Reports Page** (`pages/6_📈_Reports.py`)
   - Report type selector
   - Date range picker
   - Filter options
   - Report preview
   - Export buttons (CSV, Excel, PDF)
   - Scheduled reports management

8. **Settings Page** (`pages/7_⚙️_Settings.py`)
   - User profile management
   - Password change
   - Notification preferences
   - Display preferences
   - API key management (for developers)

9. **Audit Log Page** (`pages/8_📝_Audit_Log.py`)
   - Complete audit log view
   - Filter by user, action, date
   - Detailed change tracking
   - Export audit report

### UI Components

#### Sidebar Navigation
```python
# Components showing:
- App logo/title
- User name and role
- Navigation menu with icons
- Logout button
- Help/Support link
```

#### Reusable Components
1. **Cards** - Metric display cards with icons
2. **Forms** - Form components with validation
3. **Tables** - Data tables with sorting/filtering
4. **Charts** - Visualization components
5. **Modals** - Dialog boxes for confirmations
6. **Alerts** - Error/success/warning messages
7. **Progress Bars** - Hold progress indicators
8. **Date Pickers** - Calendar components
9. **Multi-select** - Tag/select components
10. **File Upload** - Drag-drop file upload

### UI/UX Requirements

#### Design Principles
- Clean, professional enterprise design
- Consistent color scheme and typography
- Responsive layout (works on different screen sizes)
- Accessibility compliance (WCAG 2.1 Level AA)
- Intuitive navigation
- Clear visual hierarchy

#### Layout
- Sidebar navigation (collapsible)
- Main content area with full width
- Header with user info and notifications
- Footer with help/support
- Responsive breakpoints for mobile devices

#### Themes
- Light theme (default)
- Dark theme option
- Company branded colors
- Custom CSS styling

#### Forms & Validation
- Real-time input validation
- Clear error messages
- Required field indicators
- Field-level help text
- Disabled state for pending operations

#### Data Presentation
- Table pagination with record count
- Data sorting and filtering
- Search functionality
- Empty state messages
- Loading skeletons
- Success/error messages

#### Performance
- Lazy loading of pages
- Component memoization
- Efficient state management
- Session caching
- API response caching

---

## Security Requirements

### 1. Authentication

#### JWT Implementation
- **Token Structure:**
  - Header: Algorithm (HS256)
  - Payload: User ID, roles, expiration
  - Signature: Secret key signed
- **Token Expiration:** 24 hours
- **Refresh Token:** 7 days
- **Issued At:** Timestamp included
- **Token Validation:** Signature verification, expiration check

#### Password Security
- **Hashing Algorithm:** bcrypt with salt
- **Minimum Length:** 12 characters
- **Complexity Requirements:**
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 number
  - At least 1 special character (!@#$%^&*)
- **Password History:** Prevent reuse of last 5 passwords
- **Password Expiration:** 90 days (optional, configurable)
- **Account Lockout:** After 5 failed login attempts, lock for 30 minutes

#### Session Management
- **Session Timeout:** 30 minutes of inactivity
- **Maximum Session Duration:** 8 hours
- **Session Validation:** Check database on each request
- **Concurrent Sessions:** Maximum 3 sessions per user
- **Logout:** Invalidate all active sessions

### 2. Authorization (RBAC)

#### Role Definitions

1. **Admin**
   - Manage users and roles
   - System configuration
   - View all accounts and transactions
   - Approve hold waivers
   - View audit logs
   - System settings

2. **Production Manager**
   - Manage production team
   - Approve debit requests (high amounts)
   - Manage hold waivers
   - View team reports
   - Operational settings

3. **Production Team Member**
   - View assigned accounts
   - Record credits
   - Submit debit requests
   - View hold status
   - Generate reports

4. **Compliance Officer**
   - View all transactions and holds
   - Generate compliance reports
   - Manage audit logs
   - Approval of waiver requests
   - Compliance settings

5. **Finance Officer**
   - View all accounts
   - View all transactions
   - Generate financial reports
   - Export data
   - No modification permissions

#### Permission Model
- Role-based permissions (user → role → permissions)
- Resource-level permissions (who can access what)
- Action-level permissions (who can perform what action)
- Permission inheritance: Admin > Manager > Team Member

### 3. Input Validation & Sanitization

#### Input Validation Rules
- **All inputs** validated at API endpoint level
- **Type validation:** Ensure correct data types
- **Length validation:** Enforce maximum input lengths
- **Format validation:** 
  - Account numbers: Alphanumeric, 10-20 characters
  - Amounts: Numeric, 2 decimal places, positive
  - Email: RFC 5322 compliant
  - Phone: E.164 format
  - Dates: ISO 8601 format
- **Range validation:** Amount limits, date ranges
- **Whitelist validation:** Only allow expected values

#### Input Sanitization
- **HTML encoding:** Prevent XSS attacks
- **URL encoding:** For parameters
- **SQL parameterization:** Prevent SQL injection
- **File upload validation:**
  - File size limit: 50MB
  - Allowed extensions: .csv, .xlsx, .xls, .pdf
  - Virus scan before processing
  - Filename sanitization

### 4. API Security

#### Rate Limiting
- **Global rate limit:** 10,000 requests/hour per IP
- **User rate limit:** 1,000 requests/hour per user
- **Endpoint-specific:**
  - Login: 10 attempts/hour
  - Password reset: 5 attempts/hour
  - File upload: 100 uploads/hour
- **Rate limit headers:** X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

#### CORS Configuration
- **Allowed Origins:** Whitelist production domains
- **Allowed Methods:** GET, POST, PUT, DELETE
- **Allowed Headers:** Content-Type, Authorization
- **Credentials:** Allow credentials in cross-origin requests
- **Preflight:** Support OPTIONS requests

#### API Versioning
- **Version in URL:** /api/v1/, /api/v2/
- **Backward Compatibility:** Maintain previous versions
- **Deprecation:** 6-month notice before version sunset
- **Version Header:** Also support Accept-Version header

### 5. Data Encryption

#### Data at Rest
- **Encryption Algorithm:** AES-256
- **Sensitive Fields Encrypted:**
  - Account numbers (searchable encryption)
  - Customer names
  - MMI IDs
  - Amount values (optional)
- **Encryption Key Management:**
  - Keys stored in system key vault
  - Regular key rotation (annually)
  - Master key separation

#### Data in Transit
- **TLS Version:** 1.2 minimum, TLS 1.3 preferred
- **Cipher Suites:** Only strong ciphers
- **Certificate:** Valid SSL/TLS certificate
- **HSTS:** Enforce HTTPS with Strict-Transport-Security header
- **Certificate Pinning:** Consider for API clients

### 6. Error Handling Security

#### Secure Error Responses
- **No Information Disclosure:** Generic error messages to users
- **Detailed Logging:** Log full error details server-side
- **Stack Trace:** Never return stack traces to client
- **Database Errors:** Translate to generic messages
- **Example:**
  - User sees: "Operation failed. Please try again."
  - Server logs: "Database connection timeout at 14:30:05"

#### Exception Handling
- **Try-catch all endpoints:** Prevent unhandled exceptions
- **Global exception handler:** Catch all unhandled errors
- **Logging:** Log all errors with context
- **Monitoring:** Alert on error rate thresholds

### 7. Audit & Monitoring

#### Audit Trail
- **Who:** User ID
- **What:** Action performed
- **When:** Timestamp
- **Where:** IP address, user agent
- **Why:** Reason/comment
- **Result:** Success/failure

#### Monitored Actions
- Login/logout
- Account creation/modification
- Credit/debit recording
- Hold creation/waiver/release
- User/permission changes
- Configuration changes
- Report generation
- File uploads/downloads
- API access (all requests)
- Authentication failures
- Authorization failures
- High-value transactions (> $100,000)

#### Alerting
- Failed login attempts (5+)
- Unauthorized access attempts
- Unusual transaction patterns
- System errors
- Performance degradation
- Database issues

---

## Authentication & Authorization

### 1. JWT Implementation

#### Token Generation
```python
# Payload
{
  "user_id": 123,
  "username": "user@company.com",
  "roles": ["PRODUCTION_TEAM"],
  "permissions": ["VIEW_ACCOUNTS", "CREATE_CREDIT"],
  "exp": 1716547800,  # 24 hours from now
  "iat": 1716461400,
  "jti": "unique_token_id"
}
```

#### Token Validation
- Signature verification using secret key
- Expiration check
- Issued at validation
- Not before validation
- Token in database (for revocation)

#### Refresh Token Flow
- User requests new access token with refresh token
- Refresh token must be valid and not expired
- Generate new access token with same claims
- Refresh token expiration: 7 days
- Revoke old refresh token (optional)

### 2. Password Management

#### Password Requirements
- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character
- Not contain username

#### Password Hashing
- Algorithm: bcrypt
- Cost factor: 12 (takes ~250ms to hash)
- Salt: Auto-generated per bcrypt

#### Password Reset Flow
1. User requests password reset
2. Send reset link to email (valid for 1 hour)
3. Validate reset token
4. Set new password (must meet complexity)
5. Invalidate all sessions
6. Confirm via email

### 3. Session Management

#### Session Storage
- Session data in database (secure)
- Session ID in JWT token
- Cross-reference token and session
- Session invalidation on logout

#### Session Properties
- User ID
- Login timestamp
- Last activity timestamp
- IP address
- User agent
- Active status

#### Session Timeout
- Idle timeout: 30 minutes
- Absolute timeout: 8 hours
- Warn user before timeout (at 25 minutes)
- Auto-logout after timeout

### 4. Role-Based Access Control (RBAC)

#### Role-Permission Matrix

| Role | View Accounts | Create Credit | Record Debit | Approve Debit | Waive Hold | Admin |
|------|---|---|---|---|---|---|
| Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Production Manager | ✓ | ✓ | ✓ | ✓ (high) | ✓ | ✗ |
| Production Team | ✓ (assigned) | ✓ | ✓ | ✗ | ✗ | ✗ |
| Compliance Officer | ✓ | ✓ | ✓ | ✓ (waiver) | ✓ | ✗ |
| Finance Officer | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

#### Permission Enforcement
- Check user role on each API call
- Check specific permission for action
- Verify resource ownership (if applicable)
- Log authorization failures
- Return 403 Forbidden if unauthorized

### 5. Secure Login Flow

#### Login Process
1. User submits username and password
2. Validate input (not null, correct format)
3. Rate limit check (max 10 attempts/hour)
4. Query user from database
5. Verify password using bcrypt
6. If failed, increment failed attempt counter
7. If locked (5+ failures), return "Account locked"
8. Generate JWT access token
9. Generate refresh token
10. Create session record
11. Return tokens and user info
12. Log successful login

#### Logout Process
1. Validate JWT token
2. Invalidate all active sessions
3. Remove refresh tokens
4. Clear session data
5. Log logout event
6. Return success

### 6. Multi-Factor Authentication (Optional)

#### 2FA Implementation
- Optional per user
- Methods: OTP via email, SMS, authenticator app
- Enable via settings page
- Required on login if enabled
- Fallback codes for account recovery

---

## Logging & Auditing

### 1. Structured Logging

#### Log Format
```json
{
  "timestamp": "2026-05-23T14:30:00.123Z",
  "level": "INFO",
  "logger": "app.services.credit_service",
  "message": "Credit recorded successfully",
  "request_id": "req_123456",
  "user_id": 42,
  "action": "RECORD_CREDIT",
  "data": {
    "account_id": 1,
    "amount": 5000.00,
    "transaction_type": "ACH_CREDIT"
  },
  "duration_ms": 150,
  "status": "SUCCESS"
}
```

#### Log Levels
- **DEBUG:** Detailed information for debugging (disabled in production)
- **INFO:** General informational messages (application events)
- **WARNING:** Warning messages (potential issues)
- **ERROR:** Error messages (errors that need attention)
- **CRITICAL:** Critical errors (system down, data loss)

#### Log Configuration
- Log to file (rotating, max 100MB per file, keep 30 days)
- Log to database (audit_logs table)
- Log to console (development only)
- JSON format for structured parsing
- Include request ID for tracing

### 2. Request/Response Logging

#### Request Logging
```json
{
  "timestamp": "2026-05-23T14:30:00Z",
  "request_id": "req_123456",
  "method": "POST",
  "path": "/api/v1/credits",
  "query_params": {},
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer [REDACTED]"
  },
  "user_id": 42,
  "ip_address": "192.168.1.1"
}
```

#### Response Logging
```json
{
  "timestamp": "2026-05-23T14:30:00.150Z",
  "request_id": "req_123456",
  "status_code": 201,
  "response_time_ms": 150,
  "response_size_bytes": 245,
  "result": "SUCCESS"
}
```

### 3. Audit Logging

#### Audit Log Fields
- User ID
- Action (CREATE, READ, UPDATE, DELETE, APPROVE, REJECT, WAIVE)
- Entity Type (ACCOUNT, CREDIT, HOLD, DEBIT)
- Entity ID
- Old Values (before change)
- New Values (after change)
- Timestamp
- IP Address
- User Agent
- Status (SUCCESS, FAILURE)
- Remarks

#### Audit Events to Log
- **User Management:**
  - User registration
  - User login/logout
  - Password change
  - Permission changes
  - User deactivation

- **Account Management:**
  - Account creation
  - Account modification
  - Account deactivation
  - Account status changes

- **Credit Management:**
  - Credit recording
  - Credit modification (if allowed)
  - Credit deletion (soft delete)

- **Hold Management:**
  - Hold creation (automatic)
  - Hold waiver approval
  - Hold early release approval
  - Hold status changes

- **Debit Management:**
  - Debit request submission
  - Debit approval
  - Debit rejection
  - Debit processing

- **System Actions:**
  - Configuration changes
  - Report generation
  - File uploads
  - System errors

### 4. Log Retention & Archival

#### Retention Policy
- **Log Files:** 90 days
- **Database Audit Logs:** 7 years (regulatory requirement)
- **API Logs:** 30 days
- **Error Logs:** 180 days

#### Log Archival
- Archive logs to compressed format (.gz)
- Store in secure, immutable storage
- Quarterly archival process
- Maintain searchability for compliance queries

### 5. Monitoring & Alerting

#### Key Metrics to Monitor
- API response time (p50, p95, p99)
- Error rate (per endpoint, global)
- Request count (per endpoint, total)
- Failed login attempts
- Database connection pool utilization
- CPU and memory usage
- Disk space utilization
- Backup success/failure

#### Alert Thresholds
- Error rate > 5% in 5 minutes
- Response time p99 > 5 seconds
- Failed login attempts > 20 in 1 hour per IP
- Database connection pool utilization > 80%
- CPU usage > 80% for 10 minutes
- Memory usage > 85% for 10 minutes
- Disk space < 10% available
- Backup failure

#### Alert Channels
- Email notifications
- Slack/Teams integration (optional)
- SMS for critical alerts (optional)
- PagerDuty/On-call integration (optional)

---

## Testing Requirements

### 1. Unit Testing

#### Coverage Requirements
- Minimum 85% code coverage
- Services layer: 95% coverage
- Repository layer: 90% coverage
- Validators: 100% coverage
- Utilities: 90% coverage
- Controllers/APIs: 80% coverage

#### Test Structure
```
tests/
├── unit/
│   ├── test_account_service.py
│   ├── test_credit_service.py
│   ├── test_hold_service.py
│   ├── test_debit_service.py
│   ├── test_business_day_service.py
│   ├── test_auth_service.py
│   ├── test_validators.py
│   ├── test_password_handler.py
│   └── test_utils.py
├── integration/
│   ├── test_account_api.py
│   ├── test_credit_api.py
│   ├── test_hold_api.py
│   ├── test_debit_api.py
│   ├── test_auth_api.py
│   └── test_end_to_end_workflows.py
└── fixtures/
    ├── account_fixtures.py
    ├── user_fixtures.py
    └── transaction_fixtures.py
```

#### Unit Test Examples

**Test Credit Service**
- Create credit with valid data
- Reject credit with invalid amount
- Calculate hold expiry date correctly
- Verify hold creation
- Reject duplicate credit
- Test business day calculation with holidays

**Test Hold Service**
- Auto-expire hold on expiry date
- Waive hold with valid reason
- Prevent early release without approval
- Update hold status correctly
- Calculate days remaining

**Test Debit Service**
- Block debit when hold is active
- Approve debit when hold expired
- Verify amount against balance
- Check hold status before processing
- Reject debit during hold period

**Test Validators**
- Account number validation
- Amount validation (positive, precision)
- Email validation
- Phone validation
- Date range validation

### 2. Integration Testing

#### Test Coverage
- API endpoint integration
- Database integration
- Authentication flow
- Authorization enforcement
- Hold verification flow
- Complete debit workflow

#### Integration Test Examples

**Test Credit & Hold Workflow**
1. Record credit in account
2. Verify hold created automatically
3. Check hold status
4. Wait until hold expires
5. Verify hold completed automatically
6. Verify account balance available

**Test Debit Request Workflow**
1. Submit debit request
2. Verify hold status check
3. If hold active, verify rejection
4. If hold expired, verify approval routing
5. Approve debit
6. Verify account balance updated
7. Verify transaction recorded

**Test Hold Waiver Workflow**
1. Create active hold
2. Request hold waiver
3. Verify waiver logged in audit
4. Approve waiver
5. Verify hold status updated
6. Verify funds available

### 3. API Testing

#### Test Scenarios

**Authentication Tests**
- Valid login succeeds
- Invalid password fails
- Invalid username fails
- Account lockout after 5 failures
- Token expiration
- Refresh token works
- Logout invalidates session

**Account Tests**
- Create account with valid data
- Reject duplicate account number
- Update account information
- Deactivate account
- List accounts with pagination
- Filter accounts by status

**Credit Tests**
- Record credit with valid data
- Reject invalid amount
- Verify hold created automatically
- Query credits for account
- Filter credits by date range

**Hold Tests**
- List active holds
- Get hold details
- Request waiver
- Request early release
- Filter holds by status
- Sort holds by expiry date

**Debit Tests**
- Submit debit request
- Check hold status before processing
- Approve debit (if authorized)
- Reject debit (if authorized)
- Verify hold blocks debit

### 4. Playwright End-to-End Tests

#### Test Structure
```
playwright/
├── tests/
│   ├── conftest.py
│   ├── test_login_flow.py
│   ├── test_account_workflow.py
│   ├── test_credit_workflow.py
│   ├── test_hold_workflow.py
│   ├── test_debit_workflow.py
│   └── test_reports.py
├── fixtures/
│   └── test_data.py
└── requirements.txt
```

#### E2E Test Scenarios

**Test Login Flow**
1. Navigate to login page
2. Enter invalid credentials
3. Verify error message
4. Enter valid credentials
5. Verify successful login
6. Verify dashboard loads
7. Verify user name displayed

**Test Account Management Workflow**
1. Login as production team member
2. Navigate to Accounts page
3. Create new account with valid data
4. Verify account appears in list
5. Click account to view details
6. Update account information
7. Verify changes saved
8. Search for account by number
9. Verify search results correct

**Test Credit & Hold Workflow**
1. Login as production team
2. Navigate to Credits page
3. Record new credit transaction
4. Verify credit recorded
5. Navigate to Holds page
6. Verify hold created automatically
7. Check hold expiry date
8. Verify hold status "PENDING_HOLD"
9. Mock time passage (or check next day)
10. Verify hold status updated to "HOLD_COMPLETED"

**Test Debit Processing Workflow**
1. Record credit in account
2. Wait for hold period (or use test account with no holds)
3. Submit debit request for amount
4. Verify hold status check
5. If hold active, verify error message
6. If hold expired, verify approval routing
7. Approve debit as manager
8. Verify debit status updated
9. Verify account balance reduced
10. Verify transaction recorded

**Test Hold Waiver Request**
1. Create active hold
2. Navigate to Holds page
3. Request waiver for hold
4. Enter waiver reason
5. Verify waiver request created
6. Login as compliance officer
7. Navigate to waiver requests
8. Approve waiver
9. Verify hold status updated to "HOLD_WAIVED"
10. Verify funds available

### 5. Performance Testing

#### Load Testing Scenarios
- 500 concurrent users
- 1000 TPS during peak hours
- Large batch credit uploads (100,000 records)
- Report generation under load
- Database query performance

#### Performance Metrics
- API response time < 500ms (p95)
- API response time < 1000ms (p99)
- CPU < 70% under normal load
- Memory < 4GB per server
- Database queries < 200ms

### 6. Security Testing

#### Security Test Coverage
- SQL injection attempts
- XSS injection attempts
- CSRF token validation
- Authentication bypass attempts
- Authorization bypass attempts
- Input validation gaps
- Rate limit enforcement
- Session timeout enforcement
- Password policy enforcement

#### Penetration Testing
- Quarterly penetration testing
- Vulnerability scanning
- Dependency vulnerability scanning
- OWASP Top 10 compliance check

### 7. Test Fixtures & Mocks

#### Mock Database
- In-memory SQLite for tests
- Test data setup/teardown
- Transaction isolation per test
- Database state verification

#### Test Fixtures
- User fixtures (different roles)
- Account fixtures
- Transaction fixtures
- Hold fixtures

#### Mock External Services
- Mock banking system integration
- Mock notification service
- Mock external APIs

---

## Performance Requirements

### 1. Response Time Targets

#### API Response Times
- **p50 (median):** < 100ms
- **p95:** < 500ms
- **p99:** < 1000ms
- **Max:** < 2000ms (error budget exhausted)

#### Endpoint-Specific
- Hold verification check: < 100ms
- Account balance check: < 100ms
- Debit request submission: < 200ms
- Report generation: < 30 seconds
- Dashboard load: < 2 seconds

### 2. Throughput & Capacity

#### Transaction Capacity
- **Transactions Per Second:** 1,000 TPS during peak
- **Concurrent Users:** 500 concurrent
- **Batch Processing:** 100,000 transactions/job
- **File Upload:** 100 uploads/hour

#### Database Capacity
- **Connections:** Pool of 50 connections
- **Queries Per Second:** 5,000 queries/second
- **Database Size:** < 50GB for 5 years data

### 3. Resource Utilization

#### Server Resources
- **CPU:** < 70% utilization under normal load
- **Memory:** < 4GB per API server
- **Disk:** SSD for database, adequate space
- **Network:** Bandwidth provisioned for 1,000 Mbps

#### Database Resources
- **Query Optimization:** Index on all frequently filtered columns
- **Connection Pooling:** Reuse connections
- **Query Caching:** Cache common queries
- **Lazy Loading:** Load related data on demand

### 4. Caching Strategy

#### Caching Layers
1. **Application Cache (Redis, optional):**
   - Cache frequently accessed accounts
   - Cache user permissions
   - Cache business holidays
   - TTL: 5-60 minutes

2. **Database Query Cache:**
   - Cache SELECT query results
   - Invalidate on INSERT/UPDATE/DELETE
   - TTL: 5-15 minutes

3. **Frontend Cache:**
   - Browser cache for static assets
   - API response caching
   - Session data caching

#### Cache Invalidation Strategy
- Time-based expiration
- Event-based invalidation (on data change)
- Manual cache clear (for admin)

### 5. Database Optimization

#### Indexing Strategy
- Primary key indexes (auto-created)
- Foreign key indexes (for joins)
- Composite indexes for common filters
- Partial indexes on active records

#### Query Optimization
- Use SELECT * only when needed
- Pagination for large result sets
- Batch queries where appropriate
- Avoid N+1 query problems
- Parameterized queries

#### Schema Design
- Normalized schema (3NF)
- Proper data types
- Constraints for data integrity
- Soft delete for audit trail

---

## Production Readiness

### 1. Deployment Checklist

#### Pre-Deployment
- [ ] Code review completed
- [ ] All tests passing (unit, integration, E2E)
- [ ] Code coverage > 85%
- [ ] Security scan passed
- [ ] Performance testing completed
- [ ] Backup tested and verified
- [ ] Disaster recovery plan updated
- [ ] Documentation updated
- [ ] Staging environment testing passed
- [ ] Load testing passed

#### Deployment Steps
1. Backup production database
2. Create new application version
3. Update dependencies
4. Run database migrations
5. Deploy to load balancer (blue-green deployment)
6. Smoke tests
7. Monitor error rates and performance
8. Rollback if necessary

#### Post-Deployment
- [ ] Verify all systems operational
- [ ] Check error logs for issues
- [ ] Monitor performance metrics
- [ ] Verify data integrity
- [ ] Notify stakeholders
- [ ] Schedule post-mortem if needed

### 2. Configuration Management

#### Environment Configuration
- **Development:** debug logging, mock services, test database
- **Staging:** minimal logging, real services (test), replica database
- **Production:** error logging only, real services, production database

#### Configuration Files
```
.env                          # Local development
.env.staging                  # Staging configuration
.env.production               # Production configuration
config/development.py         # Development config class
config/staging.py             # Staging config class
config/production.py          # Production config class
```

#### Sensitive Data Management
- Store in environment variables
- Never commit secrets to git
- Use .env.example as template
- Rotate secrets regularly
- Audit secret access

### 3. Startup & Shutdown

#### Startup Script
```bash
#!/bin/bash
# startup.sh

# Load environment
source .env.production

# Create necessary directories
mkdir -p logs uploads reports

# Run database migrations
python -m alembic upgrade head

# Start background jobs
python scripts/start_background_jobs.py &

# Start API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Start Streamlit frontend
streamlit run frontend/app.py --server.port 8501
```

#### Shutdown Script
```bash
#!/bin/bash
# shutdown.sh

# Stop Streamlit
pkill -f "streamlit run"

# Stop background jobs
pkill -f "start_background_jobs.py"

# Stop Uvicorn
pkill -f "uvicorn app.main:app"

# Cleanup temporary files
rm -rf uploads/temp/*

echo "Application shutdown complete"
```

### 4. Monitoring & Alerting

#### Health Checks
- **API Health:** /api/v1/health (every 5 minutes)
- **Database Health:** Connection test (every 5 minutes)
- **Disk Space:** Check available space (every 30 minutes)
- **Backup Health:** Verify recent backup (daily)

#### Key Metrics to Monitor
- API response time (p95, p99)
- Error rate (per endpoint, global)
- Request throughput
- CPU and memory usage
- Database connection pool
- Disk space utilization
- Failed login attempts
- Number of active holds
- Pending debit requests

#### Alerting Thresholds
- Error rate > 5% in 5 minutes → Page on-call
- API response time p99 > 5 seconds → Alert
- CPU > 80% for 10 minutes → Alert
- Memory > 85% → Alert
- Disk space < 10% → Critical alert
- Backup failure → Critical alert
- Database connection failure → Critical alert

### 5. Backup & Disaster Recovery

#### Backup Strategy
- **Frequency:** Daily full backup, 4-hour incremental backup
- **Retention:** 90-day retention, 7-year archive
- **Location:** Geographically separated (minimum 100 miles)
- **Encryption:** AES-256 encryption for backups

#### Backup Verification
- Monthly restore test to verify backup integrity
- Test on non-production environment
- Document recovery process
- Ensure team trained on recovery procedures

#### Disaster Recovery Plan
- **RTO (Recovery Time Objective):** < 4 hours
- **RPO (Recovery Point Objective):** < 1 hour
- **Failover Process:** Documented and tested quarterly
- **Communication Plan:** Notification procedures
- **Escalation:** Contact chain for emergency situations

### 6. Logging & Log Management

#### Log Storage
- **Application Logs:** `/app/logs/` directory
- **Log Rotation:** Daily rotation, keep 30 days
- **Database Logs:** audit_logs table
- **Archive:** Compress and store old logs

#### Log Levels in Production
- INFO: Application events
- WARNING: Potential issues
- ERROR: Errors requiring attention
- CRITICAL: System-critical errors
- DEBUG: Disabled in production

#### Log Analysis
- Search by request ID for tracing
- Filter by user ID for user activity
- Filter by action for compliance reporting
- Dashboard for log visualization

### 7. Requirements.txt Generation

#### Backend Requirements
```
FastAPI==0.100.0
uvicorn[standard]==0.23.0
sqlalchemy==2.0.20
alembic==1.12.0
pydantic==2.1.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
requests==2.31.0
pytest==7.4.0
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-mock==3.11.1
black==23.9.1
ruff==0.10.0
mypy==1.5.1
faker==19.6.1
```

#### Frontend Requirements
```
streamlit==1.28.0
requests==2.31.0
pandas==2.0.3
numpy==1.24.3
plotly==5.16.1
matplotlib==3.8.0
seaborn==0.12.2
openpyxl==3.1.2
python-csv==1.0.0
```

#### Testing Requirements (Playwright)
```
playwright==1.40.0
pytest-playwright==0.4.0
```

---

## Integration Requirements

### 1. Existing System Integration

#### Accounting System Integration
- **Export account status reports** to accounting system
- **Export transaction logs** for reconciliation
- **Import account master data** from accounting system
- **Real-time sync** of account balances
- **API Integration:** REST API or message queue

#### Banking System Integration
- **Query account balances** from banking system
- **Import credit transactions** from banking system
- **Submit debit requests** to banking system
- **Track transaction status** in banking system
- **API Integration:** Bank-provided API

#### Notification System Integration
- **Email notifications:** Credit recorded, hold expires, debit approved
- **SMS notifications:** (optional) Hold expiring soon
- **Slack/Teams:** (optional) Daily summary, high-value transactions
- **In-app notifications:** Alerts and messages

### 2. Data Exchange Format

#### CSV Import Format (for bulk credits)
```
Account Number,Customer Name,MMI ID,Amount,Transaction Type,Reference Number,Description
ACC-001,ABC Corp,MMI-123,5000.00,ACH_CREDIT,REF-001,Monthly credit
ACC-002,XYZ Inc,MMI-124,3000.00,CHEQUE_CREDIT,CHECK-001,Check deposit
```

#### CSV Export Format (for reports)
```
Account Number,Customer Name,Current Balance,Pending Hold Amount,Available Balance,Total Credits This Month,Total Debits This Month
ACC-001,ABC Corp,25000.00,5000.00,20000.00,10000.00,2000.00
```

#### API Integration
- RESTful API with JSON payloads
- API versioning support
- Pagination for large datasets
- Filtering and sorting capabilities
- Rate limiting

---

## Compliance & Regulatory

### 1. Regulatory Compliance

#### Financial Regulations
- **Sarbanes-Oxley (SOX):** Audit trails for financial transactions
- **Know Your Customer (KYC):** Customer verification
- **Anti-Money Laundering (AML):** Transaction monitoring
- **Payment Card Industry (PCI):** If processing cards
- **Federal Reserve:** Clearing and settlement rules

#### Data Protection
- **GDPR:** If EU customers (data protection and privacy)
- **CCPA:** If California residents (data privacy)
- **State Privacy Laws:** Compliance as applicable
- **PII Protection:** Secure handling of personal data

#### Audit Requirements
- **Annual audits** of financial system
- **Quarterly compliance reviews**
- **Audit trail** for all transactions
- **Evidence of controls** in place

### 2. Internal Controls

#### Segregation of Duties
- Recording credits separate from approving debits
- Hold waivers approved by different role than recording
- Manager approval for high-value transactions
- Admin separate from operational users

#### Authorization Controls
- Hierarchical approval for different amounts
- Two-factor authentication for high-risk actions
- Role-based access control
- Permission validation on each action

#### Account Controls
- Account reconciliation procedures
- Regular balance verification
- Hold status verification
- Duplicate transaction prevention

---

## Data Management

### 1. Data Classification

#### Data Sensitivity Levels

**Level 1 - Public**
- Company branding
- Public documentation
- Non-sensitive reports

**Level 2 - Internal**
- Account numbers (partially masked)
- Transaction descriptions
- Non-sensitive audit logs

**Level 3 - Confidential**
- Full account numbers
- Customer names
- MMI IDs
- Transaction amounts

**Level 4 - Highly Confidential**
- Passwords
- API keys
- Encryption keys
- Full audit trails

### 2. Data Retention

#### Retention Policies
- **Transaction Records:** 7 years (regulatory requirement)
- **Audit Logs:** 7 years
- **System Logs:** 90 days
- **Backup Copies:** 90 days minimum
- **Archived Data:** 7 years total

#### Data Purging
- Automated purging of old data
- Verification before deletion
- Log purged records
- Retention of purging audit trail

### 3. Data Quality

#### Data Validation
- Real-time validation of inputs
- Referential integrity checks
- Business rule validation
- Reconciliation procedures

#### Data Cleansing
- Identify duplicate accounts
- Correct invalid data
- Standardize formats
- Document data corrections

---

## Error Handling & Recovery

### 1. Exception Handling

#### Exception Hierarchy
```
Exception (base)
├── BusinessException
│   ├── AccountNotFoundException
│   ├── InsufficientFundsException
│   ├── HoldPeriodActiveException
│   ├── InvalidTransactionException
│   └── ...
├── ValidationException
│   ├── InvalidAccountNumberException
│   ├── InvalidAmountException
│   └── ...
├── AuthenticationException
│   ├── InvalidCredentialsException
│   ├── TokenExpiredException
│   └── ...
├── AuthorizationException
│   ├── InsufficientPermissionException
│   └── ...
└── SystemException
    ├── DatabaseException
    ├── ConfigurationException
    └── ExternalServiceException
```

#### Global Exception Handler
- Catch all unhandled exceptions
- Log with full context
- Return standard error response
- Send alerts for critical errors
- Track error metrics

### 2. Failure Recovery

#### Transaction Rollback
- ACID compliance ensures atomicity
- Rollback on validation failure
- Rollback on business rule violation
- Log rollback reason

#### Retry Mechanism
- Automatic retry for transient failures
- Exponential backoff strategy
- Maximum retry attempts (3)
- Log retry attempts

#### Circuit Breaker Pattern
- Detect failing external services
- Open circuit to prevent cascading failures
- Gradual recovery (half-open state)
- Fallback options

### 3. Graceful Degradation

#### Reduced Functionality Mode
- If external service unavailable, accept requests but queue processing
- If cache unavailable, query database directly
- If reporting service down, still allow operational transactions
- Notify users of reduced functionality

#### User Notification
- Clear error messages
- Guidance on next steps
- Estimated time to resolution
- Support contact information

---

## Deployment & DevOps

### 1. Deployment Strategy

#### Blue-Green Deployment
- Maintain two identical production environments
- Deploy to inactive environment (green)
- Run smoke tests
- Switch traffic from blue to green
- Keep blue as rollback option
- Minimal downtime (< 1 minute)

#### Rolling Deployment (Alternative)
- Deploy to one server at a time
- Gradual traffic shift
- Monitor for issues
- Rollback individual servers if needed

### 2. Infrastructure

#### Server Requirements
- **API Server:** Dual-core CPU, 4GB RAM minimum
- **Database Server:** Quad-core CPU, 8GB RAM minimum
- **Load Balancer:** High-availability setup
- **Backup Storage:** Geographically separated

#### Network Configuration
- Private network for database
- Firewall rules for API access
- VPN for admin access
- DDoS protection

### 3. Container Management (Optional)

#### Docker Configuration
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Kubernetes Deployment (Optional)
- Pod configuration for API
- Pod configuration for scheduler
- Service for load balancing
- ConfigMap for configuration
- Secrets for sensitive data

---

## Success Criteria

### 1. Functional Success Criteria

- ✓ All 5-day hold verification automated and accurate
- ✓ Zero manual hold verification process
- ✓ 100% debit request hold validation
- ✓ Real-time hold status visibility
- ✓ Complete audit trail of all transactions
- ✓ Successful integration with existing systems
- ✓ All API endpoints functional and tested
- ✓ Dashboard displays accurate information

### 2. Performance Success Criteria

- ✓ API response times < 500ms (p95)
- ✓ System supports 500 concurrent users
- ✓ Hold verification < 100ms
- ✓ Process 1,000 TPS during peak hours
- ✓ Report generation < 30 seconds

### 3. Quality Success Criteria

- ✓ Code coverage > 85%
- ✓ Zero critical security vulnerabilities
- ✓ All tests passing (unit, integration, E2E)
- ✓ Zero SQL injection vulnerabilities
- ✓ Zero XSS vulnerabilities
- ✓ Compliance with all security standards

### 4. Reliability Success Criteria

- ✓ System uptime 99.9%
- ✓ RTO < 4 hours
- ✓ RPO < 1 hour
- ✓ Zero data loss incidents
- ✓ All backups verified monthly
- ✓ Disaster recovery tested quarterly

### 5. User Adoption Success Criteria

- ✓ 100% of production team trained
- ✓ Zero manual hold verification requests
- ✓ 100% compliance with new process
- ✓ Positive user feedback (NPS > 70)
- ✓ Zero support tickets for basic functionality

---

## Project Deliverables

### Phase 1: Foundation (Week 1-2)
1. ✓ Complete project setup and folder structure
2. ✓ Database schema and migrations
3. ✓ Authentication and authorization system
4. ✓ Basic API endpoints (CRUD operations)
5. ✓ Unit tests for core services
6. ✓ Documentation: Architecture, Database Schema

### Phase 2: Core Functionality (Week 3-4)
1. ✓ Credit management with automatic hold creation
2. ✓ Hold expiry automation (scheduled job)
3. ✓ Debit request with hold verification
4. ✓ Hold waiver and early release workflow
5. ✓ Integration tests
6. ✓ Documentation: API Reference

### Phase 3: Frontend & Reporting (Week 5-6)
1. ✓ Streamlit frontend with all pages
2. ✓ Dashboard with real-time metrics
3. ✓ Report generation and export
4. ✓ File upload capability
5. ✓ Audit log viewer
6. ✓ Documentation: User Guide, Admin Guide

### Phase 4: Testing & Security (Week 7)
1. ✓ Playwright E2E tests
2. ✓ Security testing and penetration testing
3. ✓ Performance testing and optimization
4. ✓ Code coverage analysis
5. ✓ Security audit
6. ✓ Documentation: Security Guide, Testing Guide

### Phase 5: Deployment & Training (Week 8)
1. ✓ Production deployment
2. ✓ Backup and disaster recovery setup
3. ✓ Monitoring and alerting configuration
4. ✓ Production team training
5. ✓ Go-live support
6. ✓ Documentation: Deployment Guide, Troubleshooting Guide

### Final Deliverables
1. ✓ Source code repository (with Git history)
2. ✓ Complete technical documentation
3. ✓ API documentation (Swagger/OpenAPI)
4. ✓ Database documentation
5. ✓ Deployment and setup guides
6. ✓ Test coverage reports
7. ✓ Security audit report
8. ✓ Performance benchmark report
9. ✓ Training materials and videos
10. ✓ Support procedures and escalation paths

---

## Summary

This comprehensive requirements document covers all aspects of the **Cash Management - 5 Days Hold Checking System**. The system will:

1. **Automate** the 5-day hold verification process
2. **Eliminate** manual intervention and errors
3. **Provide** real-time visibility through intuitive dashboard
4. **Ensure** compliance with complete audit trails
5. **Integrate** seamlessly with existing systems
6. **Maintain** enterprise-grade security and reliability
7. **Scale** to support current and future transaction volumes
8. **Support** long-term maintenance and evolution

The technical implementation will follow enterprise-level standards with clean architecture, comprehensive testing, robust security, and production-ready operations.

**Document Version:** 1.0.0  
**Last Updated:** May 23, 2026  
**Status:** Approved for Development
