-- RFP 与 Proposal 表（MySQL）
-- 依赖 001_schema_mysql.sql

CREATE TABLE IF NOT EXISTS rfps (
    id                  VARCHAR(64) PRIMARY KEY,
    creator_agent_id    VARCHAR(64) NOT NULL,
    title               VARCHAR(512) NOT NULL,
    description         TEXT,
    capability_type     VARCHAR(64) NOT NULL,
    domain_filters      JSON,
    budget              JSON,
    deadline_at         TIMESTAMP NULL,
    status              VARCHAR(32) NOT NULL DEFAULT 'open',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

CREATE INDEX idx_rfps_creator ON rfps(creator_agent_id);
CREATE INDEX idx_rfps_status ON rfps(status);
CREATE INDEX idx_rfps_capability_type ON rfps(capability_type);

CREATE TABLE IF NOT EXISTS proposals (
    id                  VARCHAR(64) PRIMARY KEY,
    rfp_id              VARCHAR(64) NOT NULL,
    supplier_agent_id    VARCHAR(64) NOT NULL,
    status              VARCHAR(32) NOT NULL DEFAULT 'pending',
    price               JSON,
    delivery_at         VARCHAR(128),
    content             TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rfp_id) REFERENCES rfps(id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    UNIQUE KEY uk_rfp_supplier (rfp_id, supplier_agent_id)
);

CREATE INDEX idx_proposals_rfp ON proposals(rfp_id);
CREATE INDEX idx_proposals_supplier ON proposals(supplier_agent_id);
