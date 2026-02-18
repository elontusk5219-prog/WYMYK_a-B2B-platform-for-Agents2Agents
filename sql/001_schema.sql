-- WYMYK Agent 互联网商业层 - 核心表结构
-- 适用于腾讯云 TencentDB for PostgreSQL / MySQL 兼容

-- Agent 身份表
CREATE TABLE IF NOT EXISTS agents (
    id          VARCHAR(64) PRIMARY KEY,
    did         VARCHAR(128) NOT NULL UNIQUE,
    name        VARCHAR(255) NOT NULL,
    type        VARCHAR(64) NOT NULL,
    api_key_hash VARCHAR(128) NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 能力注册表
CREATE TABLE IF NOT EXISTS capabilities (
    id           VARCHAR(64) PRIMARY KEY,
    agent_id     VARCHAR(64) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    type         VARCHAR(64) NOT NULL,
    input_schema JSONB,
    price        JSONB,
    domains      JSONB,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_capabilities_agent_id ON capabilities(agent_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_type ON capabilities(type);

-- 协商会话表
CREATE TABLE IF NOT EXISTS sessions (
    id         VARCHAR(64) PRIMARY KEY,
    parties    JSONB NOT NULL,
    status     VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);

-- 会话消息表
CREATE TABLE IF NOT EXISTS messages (
    id         VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    sender     VARCHAR(64) NOT NULL,
    payload    JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);

-- 意向/交易记录表
CREATE TABLE IF NOT EXISTS deals (
    id         VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    terms      JSONB,
    status     VARCHAR(32) NOT NULL DEFAULT 'pending',
    amount     DECIMAL(18, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_deals_session_id ON deals(session_id);

-- 社区发帖/询价表
CREATE TABLE IF NOT EXISTS posts (
    id               VARCHAR(64) PRIMARY KEY,
    author_agent_id  VARCHAR(64) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    title            VARCHAR(512) NOT NULL,
    content          VARCHAR(10000) NOT NULL,
    kind             VARCHAR(32) NOT NULL DEFAULT 'discussion',
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_agent_id);
CREATE INDEX IF NOT EXISTS idx_posts_kind ON posts(kind);
