-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- =========================
-- Employees Table
-- =========================
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    employee_name TEXT NOT NULL,
    department TEXT,
    role_title TEXT,
    hire_date DATE,
    employment_status TEXT CHECK (
        employment_status IN ('active', 'terminated', 'on_leave')
    )
);

-- =========================
-- Contracts Table
-- =========================
CREATE TABLE contracts (
    contract_id SERIAL PRIMARY KEY,
    contract_name TEXT NOT NULL,
    vendor_name TEXT NOT NULL,
    employee_id INTEGER REFERENCES employees(employee_id),
    start_date DATE,
    end_date DATE,
    renewal_date DATE,
    contract_value NUMERIC(12,2),
    contract_status TEXT CHECK (
        contract_status IN ('active', 'expired', 'pending_renewal')
    )
);

-- =========================
-- Policy Embeddings Table
-- =========================
CREATE TABLE policy_embeddings (
    id SERIAL PRIMARY KEY,
    document_name TEXT,
    section_title TEXT,
    content TEXT,
    embedding vector(1536)
);

-- =========================
-- Seed Sample Employees
-- =========================
INSERT INTO employees (employee_name, department, role_title, hire_date, employment_status)
VALUES
('Alice Johnson', 'IT', 'Systems Engineer', '2020-01-15', 'active'),
('Mark Chen', 'Finance', 'Procurement Lead', '2019-03-10', 'active'),
('Rachel Adams', 'Legal', 'Compliance Officer', '2018-06-01', 'active'),
('David Patel', 'Operations', 'Infrastructure Manager', '2021-09-20', 'terminated'),
('Sarah Lewis', 'Facilities', 'Facilities Director', '2017-04-12', 'active');

-- =========================
-- Seed Sample Contracts
-- =========================
INSERT INTO contracts (
    contract_name,
    vendor_name,
    employee_id,
    start_date,
    end_date,
    renewal_date,
    contract_value,
    contract_status
)
VALUES
('VMware Support Agreement', 'VMware', 1, '2023-01-01', '2026-01-01', '2026-12-01', 125000.00, 'pending_renewal'),
('Oracle Database License', 'Oracle', 2, '2022-06-01', '2026-06-01', '2026-05-01', 210000.00, 'pending_renewal'),
('Legal Research Platform', 'LexisNexis', 3, '2024-03-15', '2027-03-15', '2027-02-15', 45000.00, 'active'),
('Backup & DR Services', 'Veeam', 4, '2022-09-01', '2025-09-01', '2025-08-01', 78000.00, 'expired'),
('Facilities Maintenance Contract', 'ABM Industries', 5, '2023-01-01', '2025-01-01', '2025-12-01', 32000.00, 'expired');
