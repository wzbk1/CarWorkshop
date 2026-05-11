$key = "c:\Users\Administrator\ProjektCloud\carworkshop-key.pem"
$host = "ec2-user@63.177.137.197"

# Create .dockerignore files on EC2
ssh -o StrictHostKeyChecking=no -i $key $host "cd /home/ec2-user/ProjektCloud; for svc in user-service service-management booking-service review-service api-gateway; do echo '.env' > `$svc/.dockerignore; done; echo DOCKERIGNORE_DONE"

# Upload new docker-compose.yml
scp -o StrictHostKeyChecking=no -i $key c:\Users\Administrator\ProjektCloud\docker-compose.yml ${host}:/home/ec2-user/ProjektCloud/docker-compose.yml

# Rebuild and restart
ssh -o StrictHostKeyChecking=no -i $key $host "cd /home/ec2-user/ProjektCloud; sudo docker-compose down; sudo docker-compose up -d --build 2>&1 | tail -20"

# Wait and check
Start-Sleep -Seconds 20
ssh -o StrictHostKeyChecking=no -i $key $host "sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'"
