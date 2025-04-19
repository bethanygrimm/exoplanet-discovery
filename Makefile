stop:
	docker compose down
start:
	docker build -t bethanygrimm/exoplanet_api:1.0 ./
	docker compose up -d
curl:
	sleep 1
	curl 127.0.0.1:5000/debug	
all: stop start curl
