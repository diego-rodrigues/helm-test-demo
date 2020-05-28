# Helm Test Demo Project

This project was created to demonstrate how to use helm test.

## Example projects

### awesome_app

This is my awesome application that reads a message from a Redis PubSub and 
adds it 10 to its value. It assumes messages are integer numbers.

### tester_helm

This is the application used to make sure that every new version of 
`awesome_app` is correct before going into production environment.

### redis-service

This is just used to deploy a container with Redis on it.

## Required Resources

* minikube: [Install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)

* helm: [Install Helm](https://helm.sh/docs/intro/install/)

* docker: [Install Docker](https://docs.docker.com/get-docker/)

## How to run the demo

1. Set up local k8s and connect it to local Docker registry
    
    * Create local k8s cluster: `minikube start`

    * Point docker commands to the docker registry inside k8s: `minikube docker-env` 
(run the commands shown by this command, this will point docker commands to 
the docker registry inside k8s. All docker commands should be executed in the 
current terminal.)

    * [optional] `minikube dashboard`  (starts a dashboard for the local k8s, do it
if you want to see pods on the web browser, otherwise use `kubectl` commands
on terminal.)

2. Create a configmap on the k8s cluster.

    `kubectl create configmap redishost --from-literal=REDIS_HOST=redis  --from-literal=REDIS_PORT=6379`

    (this creates environment variables on k8s)

3. Deploy Redis on k8s.

    (on `redis-service folder`)
    ```
    cd redis-service
    docker build -t redis-local .
    kubectl apply -f deployment-service.yaml
    cd ..
    ```

4. Create images for the projects
    ```
    cd tester_helm
    docker build -t helm-tester:0.0.1 .
    cd ../awesome_app
    docker build -t awesome-app:0.0.1 .
    ```

5. Deploy `awesome_app` using helm
    ```
    helm install awesome-app awesome-chart
    ```

    The test should pass and the application installed. Check with:
    ```
    helm test awesome-app --logs
    ```

    Check the version deployed with:
    ```
    helm list
    ```

6. Modify `awesome_app` to be incorrect.
    * On [app.py](awesome_app/app.py), modify the value `10` on line 36:
    ```
    result_message = (int)(message) + 10
    ```

    * Update the version on the [helm chart](awesome_app/charts/Chart.yaml) (lines 17 and 21):
    ```
    version: 0.0.2
    appVersion: 0.0.2
    ```

7. Create image for the new version of the `awesome_app`:
    ```
    docker build -t awesome-app:0.0.2 .
    ```

    If you check the images, you should see both versions on docker:
    ```
    docker image ls
    ```

8. Deploy `awesome_app` update using helm
    ```
    helm upgrade --install awesome-app awesome-chart
    ```

    Check the version deployed with:
    ```
    helm list
    ```
    You should see that version 0.0.2 is deployed.

9. Test the new version of the awesome_app:
    ```
    helm test awesome-app --logs
    ```
    
    The test should return an error. [Signal 1]

10. Rollback to the previous version
    ```
    helm rollback awesome-app
    ```

11. Check the deployed version is now the old 0.0.1:
    ```
    helm list
    ```

12. To uninstall the application use:
    ```
    helm uninstall awesome-app
    ```

