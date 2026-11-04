# Erreurs rencontrées - Projet E5 - PONCHIN Gauthier / CULJKAR Mathéo

## 1. Multipass : « cannot connect to the multipass socket »
- **Date :** 2026-11-04
- **Objectif :** ajouter une carte réseau en pont (Wi-Fi) à la VM `tp-e5-pc-04-11-2026`, pour qu'elle ait une IP sur le réseau local (192.168.1.x) et soit joignable en SSH depuis VS Code.
- **Commandes :**
  ```
  multipass stop tp-e5-pc-04-11-2026
  multipass set local.bridged-network=Wi-Fi
  multipass set local.tp-e5-pc-04-11-2026.bridged=true
  multipass start tp-e5-pc-04-11-2026
  ```
- **Erreur affichée :**
  ```
  set failed: cannot connect to the multipass socket
  start failed: cannot connect to the multipass socket
  ```
- **Logs / diagnostic :**
  ```
  > multipass get local.bridged-network
  Wi-Fi
  > multipass info tp-e5-pc-04-11-2026
  State:          Suspended
  IPv4:           --
  ```
  La carte de pont était déjà réglée sur `Wi-Fi`. La VM était dans un état incohérent (`Suspended` au lieu de `Stopped`).
- **Cause :** modifier un paramètre `local.*` avec `multipass set` redémarre le service Multipass (multipassd). Les commandes lancées juste après ne trouvaient plus le service, d'où l'échec de connexion au socket. La commande `set local.bridged-network=Wi-Fi` était en plus inutile, puisque la valeur était déjà `Wi-Fi`.
- **Solution :** attendre environ 30 s que le service redémarre (vérifié avec `multipass list`), puis remettre la VM dans un état propre (`multipass start`, puis `multipass stop`), et relancer `multipass set local.tp-e5-pc-04-11-2026.bridged=true` puis `multipass start`. Vérification dans la VM :
  ```
  > multipass exec tp-e5-pc-04-11-2026 -- ip -4 -br addr
  eth0   UP   10.0.2.15/24
  eth1   UP   192.168.1.19/24
  ```
  La VM a obtenu l'IP 192.168.1.19 sur la carte pontée `eth1`.
- **À retenir :** après un `multipass set local.*`, attendre que le service soit revenu avant d'enchaîner, et toujours vérifier la valeur actuelle avec `multipass get` avant de la changer.


## 2. Docker Hub : push refusé (« insufficient_scope » puis « incorrect username or password »)
- **Date :** 2026-11-04
- **Objectif :** pousser l'image `stripe-shop-pc-04-11-2026:v1` sur Docker Hub, pour que Kubernetes puisse la télécharger (exigence du sujet).
- **Commandes :**
  ```
  docker tag stripe-shop-pc-04-11-2026:v1 nagarrath/stripe-shop-pc-04-11-2026:v1
  docker push nagarrath/stripe-shop-pc-04-11-2026:v1
  docker login -u nagarrath
  ```
- **Erreurs affichées :**
  ```
  push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
  Error response from daemon: Get "https://registry-1.docker.io/v2/": unauthorized: incorrect username or password
  ```
- **Logs / diagnostic :** le push échouait car Docker n'était connecté à aucun compte (`docker login` jamais fait dans la VM). Ensuite, `docker login` refusait le token saisi. Le pseudo `nagarrath` a été vérifié dans l'URL du profil Docker Hub (`hub.docker.com/repositories/nagarrath`), il était correct.
- **Cause :** le token utilisé avait été créé sur **GitHub** (pour le `git push`) et non sur **Docker Hub**. Ce sont deux comptes et deux systèmes d'authentification séparés : un token GitHub n'est pas valable sur le registre Docker.
- **Solution :** création d'un Personal Access Token sur Docker Hub (app.docker.com > Account settings > Personal access tokens, permission Read & Write), puis :
  ```
  docker login -u nagarrath      -> Login Succeeded
  docker push nagarrath/stripe-shop-pc-04-11-2026:v1
  v1: digest: sha256:1adfd30d822da62459294589b7d98568ff54b98727e4bb4b417d516e629ff8d4 size: 2053
  ```
- **À retenir :** un token par service (GitHub pour git, Docker Hub pour les images), avec les droits minimum nécessaires. Le token Docker est stocké en clair dans `~/.docker/config.json` (avertissement affiché au login) : ne jamais copier ce fichier dans le repo.


## 3. Accès à l'appli : commandes lancées sur Windows au lieu de la VM
- **Date :** 2026-11-04
- **Objectif :** vérifier que l'appli stripe-shop déployée dans Kubernetes répond sur son Service NodePort (port 31850).
- **Commandes (tapées dans l'invite de commandes Windows) :**
  ```
  C:\Users\ponch> minikube ip
  C:\Users\ponch> curl 192.168.49.2:31850
  ```
- **Erreurs affichées :**
  ```
  'minikube' n'est pas reconnu en tant que commande interne ou externe, un programme exécutable ou un fichier de commandes.
  curl: (28) Failed to connect to 192.168.49.2:31850 after 21118 ms: Could not connect to server
  ```
- **Diagnostic :** le prompt `C:\Users\ponch>` montre que les commandes ont été lancées sur le PC Windows, et non dans la VM `tp-e5-pc-04-11-2026`.
- **Cause :**
  - `minikube` n'est installé que dans la VM Ubuntu, pas sur Windows.
  - `192.168.49.2` est l'IP du nœud minikube sur le réseau Docker **interne à la VM** (driver docker). Ce réseau n'est pas routé jusqu'au PC, d'où le timeout. Un NodePort minikube n'est donc pas joignable directement depuis l'extérieur de la VM.
- **Solution :**
  - lancer les commandes dans le terminal VS Code connecté en SSH à la VM (`ubuntu@tp-e5-pc-04-11-2026`) :
    ```
    $ minikube ip
    192.168.49.2
    $ curl 192.168.49.2:31850
    <h1>Boutique PC-04-11-2026</h1> ...
    ```
  - pour y accéder depuis le navigateur Windows : redirection de port VS Code (onglet Ports > Ajouter un port > `192.168.49.2:31850`), puis ouverture de l'adresse locale fournie (`localhost:31850`).
- **À retenir :** toujours vérifier le prompt avant de taper une commande (Windows ou VM). Avec minikube en driver docker, l'accès externe passe par une redirection de port (VS Code, `kubectl port-forward` ou `minikube service`).