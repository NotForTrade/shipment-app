@echo off

docker build -t shipment-app:latest .

kind load docker-image shipment-app:latest

kubectl apply -f deploy/redis.yml

kubectl apply -f deploy/shipment-app.yml

kubectl -n shipment-app rollout restart deploy/shipment-app-deployment

kubectl -n shipment-app rollout restart deploy/brontosaurus-pop

kubectl -n shipment-app rollout restart deploy/raptor

kubectl -n shipment-app rollout restart deploy/shipment-event-worker

echo Done.
pause