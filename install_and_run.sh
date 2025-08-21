docker build . -t osigris
docker run -d --name osigris-api -p 8000:8000 osigris:latest
