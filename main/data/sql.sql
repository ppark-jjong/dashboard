-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS TEST;

-- Core entities
CREATE TABLE TEST.RECIPIENT (
    recipient_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50) NOT NULL
);

CREATE TABLE TEST.DEPARTURE (
    departure_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50) NOT NULL
);

CREATE TABLE TEST.SLA (
    sla_id VARCHAR(20) PRIMARY KEY,
    cost INT NOT NULL
);

CREATE TABLE TEST.ZIPCODE (
    zipcode CHAR(6) PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    distance INT NOT NULL
);

CREATE TABLE TEST.ORDER (
    order_id INT PRIMARY KEY,
    recipient_id INT NOT NULL,
    sla_id VARCHAR(20) NOT NULL,
    departure_id INT NOT NULL,
    zipcode CHAR(6) NOT NULL,
    item VARCHAR(200) NOT NULL,
    qty INT NOT NULL,
    created_time TIMESTAMP NOT NULL,
    address VARCHAR(200) NOT NULL,
    FOREIGN KEY (recipient_id) REFERENCES TEST.RECIPIENT(recipient_id),
    FOREIGN KEY (sla_id) REFERENCES TEST.SLA(sla_id),
    FOREIGN KEY (departure_id) REFERENCES TEST.DEPARTURE(departure_id),
    FOREIGN KEY (zipcode) REFERENCES TEST.ZIPCODE(zipcode)
);

-- Tracking related entities
CREATE TABLE TEST.RETURN_REQUEST (
    return_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    departure_id INT NOT NULL,
    requested_date TIMESTAMP NOT NULL,
    scheduled_pickup TIMESTAMP NOT NULL,
    FOREIGN KEY (order_id) REFERENCES TEST.ORDER(order_id),
    FOREIGN KEY (departure_id) REFERENCES TEST.DEPARTURE(departure_id)
);

CREATE TABLE TEST.DRIVER (
    driver_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL
);

CREATE TABLE TEST.STATUS_REASON_CODE (
    reason_code VARCHAR(20) PRIMARY KEY,
    reason_type VARCHAR(50) NOT NULL,
    reason_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL
);

CREATE TABLE TEST.REALTIME_DASHBOARD (
    realtime_dashboard_id INT PRIMARY KEY,
    order_id INT,
    return_id INT,
    driver_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    eta_initial_time TIMESTAMP,
    eta_current_time TIMESTAMP,
    eta_update_reason VARCHAR(200),
    eta_last_updated TIMESTAMP,
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP,
    status_change_time TIMESTAMP NOT NULL,
    reason_code VARCHAR(20),
    FOREIGN KEY (order_id) REFERENCES TEST.ORDER(order_id),
    FOREIGN KEY (return_id) REFERENCES TEST.RETURN_REQUEST(return_id),
    FOREIGN KEY (driver_id) REFERENCES TEST.DRIVER(driver_id),
    FOREIGN KEY (reason_code) REFERENCES TEST.STATUS_REASON_CODE(reason_code)
);

-- Add indexes for frequently accessed columns and foreign keys
CREATE INDEX idx_order_created_time ON TEST.ORDER(created_time);
CREATE INDEX idx_return_scheduled_pickup ON TEST.RETURN_REQUEST(scheduled_pickup);
CREATE INDEX idx_realtime_status ON TEST.REALTIME_DASHBOARD(status);
CREATE INDEX idx_realtime_eta ON TEST.REALTIME_DASHBOARD(eta_current_time);