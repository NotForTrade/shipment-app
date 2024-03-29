@echo off

docker build -t shipment-app:latest .

kind create cluster --config kind-cluster.yml

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s

kubectl apply -f deploy/redis.yml

kind load docker-image shipment-app:latest

kubectl apply -f deploy/shipment-app.yml

kubectl -n shipment-app rollout restart deploy/shipment-app-deployment

kubectl -n shipment-app rollout restart deploy/brontosaurus-pop

echo Done.
pause