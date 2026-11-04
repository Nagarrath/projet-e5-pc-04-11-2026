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