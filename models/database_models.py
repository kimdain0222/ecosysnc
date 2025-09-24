#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Energy Management System - Database Models
에너지 관리 시스템 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import uuid

# =============================================================================
# 사용자 및 인증 관련 모델
# =============================================================================

class Tenant(Base):
    """테넌트 (고객사) 모델"""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True)
    subscription_plan = Column(String(50), default='basic')
    status = Column(String(20), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    users = relationship("User", back_populates="tenant")
    buildings = relationship("Building", back_populates="tenant")
    notifications = relationship("Notification", back_populates="tenant")
    event_logs = relationship("EventLog", back_populates="tenant")
    subscriptions = relationship("TenantSubscription", back_populates="tenant")

class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default='user')
    status = Column(String(20), default='active')
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    tenant = relationship("Tenant", back_populates="users")

# =============================================================================
# 건물 및 센서 관련 모델
# =============================================================================

class Building(Base):
    """건물 모델"""
    __tablename__ = "buildings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    building_type = Column(String(50))
    total_floors = Column(Integer)
    total_area = Column(Float)
    construction_year = Column(Integer)
    status = Column(String(20), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    tenant = relationship("Tenant", back_populates="buildings")
    floors = relationship("Floor", back_populates="building")
    sensors = relationship("Sensor", back_populates="building")
    settings = relationship("BuildingSetting", back_populates="building")
    notifications = relationship("Notification", back_populates="building")
    event_logs = relationship("EventLog", back_populates="building")

class Floor(Base):
    """층 모델"""
    __tablename__ = "floors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"))
    floor_number = Column(Integer, nullable=False)
    floor_name = Column(String(100))
    area = Column(Float)
    room_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    building = relationship("Building", back_populates="floors")
    rooms = relationship("Room", back_populates="floor")

class Room(Base):
    """방 모델"""
    __tablename__ = "rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    floor_id = Column(UUID(as_uuid=True), ForeignKey("floors.id", ondelete="CASCADE"))
    room_number = Column(String(50))
    room_name = Column(String(100))
    room_type = Column(String(50))
    area = Column(Float)
    capacity = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    floor = relationship("Floor", back_populates="rooms")
    sensors = relationship("Sensor", back_populates="room")

class SensorType(Base):
    """센서 타입 모델"""
    __tablename__ = "sensor_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    unit = Column(String(20))
    data_type = Column(String(20))
    min_value = Column(Float)
    max_value = Column(Float)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    sensors = relationship("Sensor", back_populates="sensor_type")

class Sensor(Base):
    """센서 모델"""
    __tablename__ = "sensors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="SET NULL"))
    sensor_type_id = Column(UUID(as_uuid=True), ForeignKey("sensor_types.id"))
    sensor_id = Column(String(100), nullable=False)
    name = Column(String(255))
    location_description = Column(Text)
    mqtt_topic = Column(String(255))
    http_endpoint = Column(String(255))
    update_interval = Column(Integer, default=60)
    status = Column(String(20), default='active')
    last_reading = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    building = relationship("Building", back_populates="sensors")
    room = relationship("Room", back_populates="sensors")
    sensor_type = relationship("SensorType", back_populates="sensors")
    thresholds = relationship("SensorThreshold", back_populates="sensor")
    notifications = relationship("Notification", back_populates="sensor")

# =============================================================================
# 설정 및 메타데이터 모델
# =============================================================================

class BuildingSetting(Base):
    """건물 설정 모델"""
    __tablename__ = "building_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"))
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(JSON)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    building = relationship("Building", back_populates="settings")

class SensorThreshold(Base):
    """센서 임계값 모델"""
    __tablename__ = "sensor_thresholds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id", ondelete="CASCADE"))
    threshold_type = Column(String(50), nullable=False)
    min_value = Column(Float)
    max_value = Column(Float)
    severity = Column(String(20), default='warning')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    sensor = relationship("Sensor", back_populates="thresholds")

# =============================================================================
# 알림 및 이벤트 모델
# =============================================================================

class Notification(Base):
    """알림 모델"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"))
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id", ondelete="SET NULL"))
    notification_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default='info')
    status = Column(String(20), default='unread')
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    
    # 관계
    tenant = relationship("Tenant", back_populates="notifications")
    building = relationship("Building", back_populates="notifications")
    sensor = relationship("Sensor", back_populates="notifications")

class EventLog(Base):
    """이벤트 로그 모델"""
    __tablename__ = "event_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"))
    event_type = Column(String(50), nullable=False)
    event_source = Column(String(100))
    description = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    tenant = relationship("Tenant", back_populates="event_logs")
    building = relationship("Building", back_populates="event_logs")

# =============================================================================
# 구독 및 결제 관련 모델
# =============================================================================

class SubscriptionPlan(Base):
    """구독 플랜 모델"""
    __tablename__ = "subscription_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price_monthly = Column(Float)
    price_yearly = Column(Float)
    max_buildings = Column(Integer)
    max_sensors = Column(Integer)
    max_users = Column(Integer)
    features = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    subscriptions = relationship("TenantSubscription", back_populates="plan")

class TenantSubscription(Base):
    """테넌트 구독 모델"""
    __tablename__ = "tenant_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"))
    status = Column(String(20), default='active')
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    tenant = relationship("Tenant", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
