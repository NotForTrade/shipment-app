## runninc locally

    py app.py

## building container image

    docker build -t shipment-app:latest .

## running image with docker

    docker run -d -p 5000:5000 shipment-app

## kubernetes deployment
    
    kind create cluster --config kind-cluster.yml

## verify the clusters are working properly
    
    kubectl get node

## see all the namespaces

    kubectl get ns


## see all pods on any namespace

    kubectl get po -A


## Execute the manifest to deploy redis

    kubectl apply -f deploy/redis-deployment.yml


## Execute the manifest to deploy all the other services

    kubectl apply -f deploy/shipment-app.yml


## load locally the docker image with kind

    kind load docker-image shipment-app:latest


## create the nginx environment
    
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml



## Delete a pod

    kubectl -n NAMESPACE delete po POD_NAME


## restart a pod

    kubectl -n NAMESPACE rollout restart deploy/redis-pop-deployment


## restart shipment-app pod

    kubectl -n shipment-app rollout restart deploy/shipment-app-deployement


## restart brontosaurus-pop pod

    kubectl -n shipment-app rollout restart deploy/brontosaurus-pop


## get the logs

    kubectl -n shipment-app logs deploy/redis-pop-deployment


## edit the scale of a service

    kubectl -n shipment-app scale --replicas=0 deploy/brontosaurus-pop

