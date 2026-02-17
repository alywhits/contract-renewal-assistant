Database: contract_renewal_db (PostgreSQL)

Tables and schema definitions are authoritative. If a column or table is not listed here, it does not exist.

---

Table: employees
Description: Stores core employee records.

Columns:
- employee_id (integer, primary key)
- employee_name (text, not null)
- department (text)
- role_title (text)
- hire_date (date)
- employment_status (text; allowed values: active, terminated, on_leave)

Constraints:
- employment_status must be one of: active, terminated, on_leave

---

Table: contracts
Description: Stores vendor contracts associated with employees.

Columns:
- contract_id (integer, primary key)
- contract_name (text, not null)
- vendor_name (text, not null)
- employee_id (integer, foreign key → employees.employee_id)
- start_date (date)
- end_date (date)
- renewal_date (date)
- contract_value (numeric(12,2))
- contract_status (text; allowed values: active, expired, pending_renewal)

Constraints:
- contract_status must be one of: active, expired, pending_renewal
- employee_id must reference an existing employees.employee_id

---

Rules:
- The database is read-only.
- Only SELECT statements are allowed.
- Do not assume columns, tables, or relationships not defined above.
- Do not perform INSERT, UPDATE, DELETE, DROP, or ALTER operations.
- Do not infer business rules beyond the stored data.

