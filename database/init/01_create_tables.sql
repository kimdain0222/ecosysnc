-- =============================================================================
-- Energy Management System - Database Schema
-- 에너지 관리 시스템 데이터베이스 스키마
-- =============================================================================

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- 사용자 및 인증 관련 테이블
-- =============================================================================

-- 테넌트 (고객사) 테이블
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 사용자 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- 건물 및 센서 관련 테이블
-- =============================================================================

-- 건물 테이블
CREATE TABLE buildings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    building_type VARCHAR(50),
    total_floors INTEGER,
    total_area DECIMAL(10,2),
    construction_year INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 층 테이블
CREATE TABLE floors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    floor_number INTEGER NOT NULL,
    floor_name VARCHAR(100),
    area DECIMAL(10,2),
    room_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(building_id, floor_number)
);

-- 방 테이블
CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    floor_id UUID REFERENCES floors(id) ON DELETE CASCADE,
    room_number VARCHAR(50),
    room_name VARCHAR(100),
    room_type VARCHAR(50),
    area DECIMAL(10,2),
    capacity INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 센서 타입 테이블
CREATE TABLE sensor_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20),
    data_type VARCHAR(20),
    min_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 센서 테이블
CREATE TABLE sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    room_id UUID REFERENCES rooms(id) ON DELETE SET NULL,
    sensor_type_id UUID REFERENCES sensor_types(id),
    sensor_id VARCHAR(100) NOT NULL,
    name VARCHAR(255),
    location_description TEXT,
    mqtt_topic VARCHAR(255),
    http_endpoint VARCHAR(255),
    update_interval INTEGER DEFAULT 60,
    status VARCHAR(20) DEFAULT 'active',
    last_reading TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(building_id, sensor_id)
);

-- =============================================================================
-- 설정 및 메타데이터 테이블
-- =============================================================================

-- 건물 설정 테이블
CREATE TABLE building_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(building_id, setting_key)
);

-- 센서 임계값 테이블
CREATE TABLE sensor_thresholds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id UUID REFERENCES sensors(id) ON DELETE CASCADE,
    threshold_type VARCHAR(50) NOT NULL,
    min_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    severity VARCHAR(20) DEFAULT 'warning',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- 알림 및 이벤트 테이블
-- =============================================================================

-- 알림 테이블
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    sensor_id UUID REFERENCES sensors(id) ON DELETE SET NULL,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    status VARCHAR(20) DEFAULT 'unread',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- 이벤트 로그 테이블
CREATE TABLE event_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_source VARCHAR(100),
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- 구독 및 결제 관련 테이블
-- =============================================================================

-- 구독 플랜 테이블
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2),
    price_yearly DECIMAL(10,2),
    max_buildings INTEGER,
    max_sensors INTEGER,
    max_users INTEGER,
    features JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 테넌트 구독 테이블
CREATE TABLE tenant_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES subscription_plans(id),
    status VARCHAR(20) DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    auto_renew BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- 인덱스 생성
-- =============================================================================

-- 사용자 관련 인덱스
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);

-- 건물 관련 인덱스
CREATE INDEX idx_buildings_tenant_id ON buildings(tenant_id);
CREATE INDEX idx_buildings_status ON buildings(status);
CREATE INDEX idx_floors_building_id ON floors(building_id);
CREATE INDEX idx_rooms_floor_id ON rooms(floor_id);

-- 센서 관련 인덱스
CREATE INDEX idx_sensors_building_id ON sensors(building_id);
CREATE INDEX idx_sensors_room_id ON sensors(room_id);
CREATE INDEX idx_sensors_sensor_type_id ON sensors(sensor_type_id);
CREATE INDEX idx_sensors_status ON sensors(status);
CREATE INDEX idx_sensors_last_reading ON sensors(last_reading);

-- 알림 관련 인덱스
CREATE INDEX idx_notifications_tenant_id ON notifications(tenant_id);
CREATE INDEX idx_notifications_building_id ON notifications(building_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- 이벤트 로그 인덱스
CREATE INDEX idx_event_logs_tenant_id ON event_logs(tenant_id);
CREATE INDEX idx_event_logs_building_id ON event_logs(building_id);
CREATE INDEX idx_event_logs_event_type ON event_logs(event_type);
CREATE INDEX idx_event_logs_created_at ON event_logs(created_at);

-- =============================================================================
-- 트리거 함수 (updated_at 자동 업데이트)
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- updated_at 트리거 적용
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_buildings_updated_at BEFORE UPDATE ON buildings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sensors_updated_at BEFORE UPDATE ON sensors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_building_settings_updated_at BEFORE UPDATE ON building_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sensor_thresholds_updated_at BEFORE UPDATE ON sensor_thresholds FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tenant_subscriptions_updated_at BEFORE UPDATE ON tenant_subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 초기 데이터 삽입
-- =============================================================================

-- 기본 센서 타입 삽입
INSERT INTO sensor_types (name, unit, data_type, min_value, max_value, description) VALUES
('temperature', 'celsius', 'float', -50, 100, '온도 센서'),
('humidity', 'percent', 'float', 0, 100, '습도 센서'),
('power_consumption', 'kwh', 'float', 0, 10000, '전력 사용량 센서'),
('occupancy', 'percent', 'float', 0, 100, '공실률 센서'),
('light_level', 'lux', 'float', 0, 100000, '조도 센서'),
('co2', 'ppm', 'float', 0, 5000, 'CO2 농도 센서');

-- 기본 구독 플랜 삽입
INSERT INTO subscription_plans (name, description, price_monthly, price_yearly, max_buildings, max_sensors, max_users, features) VALUES
('Basic', '소규모 건물용 기본 플랜', 29.99, 299.99, 5, 100, 5, '{"real_time_monitoring": true, "basic_analytics": true, "email_support": true}'),
('Professional', '중규모 건물용 전문 플랜', 99.99, 999.99, 25, 500, 25, '{"real_time_monitoring": true, "advanced_analytics": true, "predictive_analytics": true, "priority_support": true, "api_access": true}'),
('Enterprise', '대규모 건물용 엔터프라이즈 플랜', 299.99, 2999.99, 100, 2000, 100, '{"real_time_monitoring": true, "advanced_analytics": true, "predictive_analytics": true, "custom_integrations": true, "dedicated_support": true, "api_access": true, "white_label": true}');

-- 기본 테넌트 생성 (개발용)
INSERT INTO tenants (name, domain, subscription_plan) VALUES
('Energy Management Demo', 'demo.energy.com', 'Professional');

-- 기본 사용자 생성 (개발용)
INSERT INTO users (tenant_id, email, password_hash, first_name, last_name, role) 
SELECT 
    t.id,
    'admin@energy.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK', -- 'password123' 해시
    'Admin',
    'User',
    'admin'
FROM tenants t WHERE t.name = 'Energy Management Demo';

COMMIT;
