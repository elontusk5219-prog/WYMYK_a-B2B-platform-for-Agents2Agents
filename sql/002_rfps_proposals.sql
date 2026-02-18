-- RFP（需求单）与 Proposal（提案）表，用于定向、结构化信息交换
-- 依赖 001_schema.sql（agents 等）

-- 需求单：买方 Agent 创建，用于能力匹配与提案收集
CREATE TABLE IF NOT EXISTS rfps (
    id                  VARCHAR(64) PRIMARY KEY,
    creator_agent_id    VARCHAR(64) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    title               VARCHAR(512) NOT NULL,
    description         TEXT,
    capability_type     VARCHAR(64) NOT NULL,
    domain_filters      JSONB,
    budget              JSONB,
    deadline_at         TIMESTAMP WITH TIME ZONE,
    status              VARCHAR(32) NOT NULL DEFAULT 'open',
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rfps_creator ON rfps(creator_agent_id);
CREATE INDEX IF NOT EXISTS idx_rfps_status ON rfps(status);
CREATE INDEX IF NOT EXISTS idx_rfps_capability_type ON rfps(capability_type);

-- 提案：供应方 Agent 针对某 RFP 提交
CREATE TABLE IF NOT EXISTS proposals (
    id                  VARCHAR(64) PRIMARY KEY,
    rfp_id              VARCHAR(64) NOT NULL REFERENCES rfps(id) ON DELETE CASCADE,
    supplier_agent_id    VARCHAR(64) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    status              VARCHAR(32) NOT NULL DEFAULT 'pending',
    price               JSONB,
    delivery_at         VARCHAR(128),
    content             TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_proposals_rfp ON proposals(rfp_id);
CREATE INDEX IF NOT EXISTS idx_proposals_supplier ON proposals(supplier_agent_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_proposals_rfp_supplier ON proposals(rfp_id, supplier_agent_id);

-- 可选：会话关联 RFP/提案，便于溯源
-- ALTER TABLE sessions ADD COLUMN IF NOT EXISTS rfp_id VARCHAR(64) REFERENCES rfps(id) ON DELETE SET NULL;
-- ALTER TABLE sessions ADD COLUMN IF NOT EXISTS proposal_id VARCHAR(64) REFERENCES proposals(id) ON DELETE SET NULL;

-- 可选：Deal 关联提案
-- ALTER TABLE deals ADD COLUMN IF NOT EXISTS proposal_id VARCHAR(64) REFERENCES proposals(id) ON DELETE SET NULL;
