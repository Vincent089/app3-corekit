# setup
``kubectl create namespace observability``

``helm repo add grafana https://grafana.github.io/helm-charts && helm repo update``

``helm upgrade --install loki grafana/loki -n observability --values loki-values.yaml --wait``

``helm upgrade --install alloy grafana/alloy --namespace observability --values alloy-values.yaml --wait``

``helm upgrade --install grafana grafana/grafana -n observability --values grafana-values.yaml --wait``


# interface
open grafana ui

``kubectl port-forward svc/grafana 3000:80 -n observability``

open alloy pipeline graph ui to validate connectivity between Alloy and Loki

``kubectl port-forward svc/alloy 12345:12345 -n observability``

open loki pipeline ui

``kubectl port-forward svc/loki 3100:3100 -n observability``


# tshoot

### Docker desktop initChown error
this is only needed on Docker desktop because it may create a race between local PV and the deployment

``
helm upgrade grafana grafana/grafana --namespace observability --values grafana-values.yaml --set initChwnData.enabled=false --wait
``

### Alloy label update

Loki cached its parsing keys, so if you update alloy label collectors Loki is going to not pick them up because it cached the first map
Cleaning its pod forcing a reload clears that issue

#### 1. Stop Alloy by making it unschedulable
kubectl patch daemonset alloy -n observability -p '{"spec":{"template":{"spec":{"nodeSelector":{"non-existing-key":"true"}}}}}'

Windows version: kubectl patch daemonset alloy -n observability -p '{\"spec\":{\"template\":{\"spec\":{\"nodeSelector\":{\"non-existing-key\":\"true\"}}}}}'

#### 2. Wait for allow the pod to terminate
kubectl get pods -n observability -w

#### 3. Delete Loki pod to clear in-memory state
kubectl delete pod -n observability -l app.kubernetes.io/name=loki --wait

#### 4. Delete Loki PVC
``kubectl delete pvc -n observability -l app.kubernetes.io/name=loki``

#### 4. Wait for Loki to come back healthy
kubectl get pods -n observability -w

#### 6. Bring Alloy back by removing the fake node selector
kubectl patch daemonset alloy -n observability -p '[{"op":"remove","path":"/spec/template/spec/nodeSelector"}]'

Windows version: kubectl patch daemonset alloy -n observability --type=json -p='[{\"op\":\"remove\",\"path\":\"/spec/template/spec/nodeSelector\"}]'

#### 7. Confirm the Alloy pod is back and running
kubectl get pods -n observability -w