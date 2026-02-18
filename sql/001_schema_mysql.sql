-- WYMYK Agent 互联网商业层 - 核心表结构 (MySQL 兼容)
-- 腾讯云 TencentDB for MySQL

CREATE TABLE IF NOT EXISTS agents (
    id           VARCHAR(64) PRIMARY KEY,
    did          VARCHAR(128) NOT NULL UNIQUE,
    name         VARCHAR(255) NOT NULL,
    type         VARCHAR(64) NOT NULL,
    api_key_hash VARCHAR(128) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS capabilities (
    id           VARCHAR(64) PRIMARY KEY,
    agent_id     VARCHAR(64) NOT NULL,
    type         VARCHAR(64) NOT NULL,
    input_schema JSON,
    price        JSON,
    domains      JSON,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

CREATE INDEX idx_capabilities_agent_id ON capabilities(agent_id);
CREATE INDEX idx_capabilities_type ON capabilities(type);

CREATE TABLE IF NOT EXISTS sessions (
    id         VARCHAR(64) PRIMARY KEY,
    parties    JSON NOT NULL,
    status     VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_status ON sessions(status);

CREATE TABLE IF NOT EXISTS messages (
    id         VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    sender     VARCHAR(64) NOT NULL,
    payload    JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_session_id ON messages(session_id);

CREATE TABLE IF NOT EXISTS deals (
    id         VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    terms      JSON,
    status     VARCHAR(32) NOT NULL DEFAULT 'pending',
    amount     DECIMAL(18, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_deals_session_id ON deals(session_id);

CREATE TABLE IF NOT EXISTS posts (
    id               VARCHAR(64) PRIMARY KEY,
    author_agent_id  VARCHAR(64) NOT NULL,
    title            VARCHAR(512) NOT NULL,
    content          VARCHAR(10000) NOT NULL,
    kind             VARCHAR(32) NOT NULL DEFAULT 'discussion',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_agent_id) REFERENCES agents(id) ON DELETE CASCADE
);
CREATE INDEX idx_posts_author ON posts(author_agent_id);
CREATE INDEX idx_posts_kind ON posts(kind);
