-- Green Certification Database Initialization

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if not exists (this will be handled by Docker env vars)
-- The database 'green_certification' will be created by the Docker container

-- Create a simple health check function
CREATE OR REPLACE FUNCTION database_health_check()
RETURNS TEXT AS $$
BEGIN
    RETURN 'Database is healthy at ' || NOW();
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Log initialization
INSERT INTO information_schema.sql_features (feature_id, feature_name) 
VALUES ('GREEN_CERT_INIT', 'Green Certification Database Initialized') 
ON CONFLICT DO NOTHING;
