#!/bin/bash
set -e

# Update system
yum update -y

# Install Docker
amazon-linux-extras install docker -y || yum install docker -y
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
COMPOSE_VERSION="v2.29.2"
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install Git
yum install git -y

# Install PostgreSQL client (for DB initialization)
yum install postgresql15 -y || amazon-linux-extras install postgresql15 -y || yum install postgresql -y

echo "=== EC2 setup complete ==="
