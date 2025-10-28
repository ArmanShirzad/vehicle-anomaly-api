#!/bin/bash

echo "Setting up PostgreSQL for Vehicle Anomaly API..."

# Install PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Set password (change 'your_password' to your secure password)
PASSWORD='your_secure_password'

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE vehicleapi;
CREATE USER vehicleapi_user WITH PASSWORD '$PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE vehicleapi TO vehicleapi_user;
\q
EOF

# Connect to database and grant schema privileges
sudo -u postgres psql -d vehicleapi << EOF
GRANT ALL ON SCHEMA public TO vehicleapi_user;
\q
EOF

# Update pg_hba.conf for password authentication
sudo sed -i "s/local\s*all\s*all\s*peer/local   all             all                                     md5/" /etc/postgresql/*/main/pg_hba.conf

# Restart PostgreSQL
sudo systemctl restart postgresql

echo "PostgreSQL setup complete!"
echo "Now update your .env file with:"
echo "DATABASE_URL=postgresql+asyncpg://vehicleapi_user:$PASSWORD@localhost:5432/vehicleapi"