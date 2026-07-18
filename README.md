# AxpertEMS

Intégration Home Assistant native pour onduleurs Axpert/Voltronic compatibles PI30 (clones type Victor, Must, Easun, PowMr...), avec un système de gestion d'énergie ("Brain") en automations YAML.

## Architecture

- `custom_components/axpertems/` — le driver : communication série (PI30), capteurs, sélecteurs. Aucune logique de décision énergétique ici.
- `packages/` — le "Brain" : automations YAML qui décident du mode de sortie, du délestage, de la priorité de charge, etc. À copier dans votre dossier `packages/` Home Assistant.

## Installation du composant

### Manuelle
1. Copiez `custom_components/axpertems/` dans `/config/custom_components/axpertems/`.
2. Redémarrez Home Assistant.
3. Allez dans **Paramètres > Appareils et services > Ajouter une intégration**, cherchez "AxpertEMS".
4. Renseignez le port série (ex: `/dev/ttyUSB0`) et la vitesse (2400 bauds par défaut).

### Via HACS (dépôt personnalisé)
1. HACS > Intégrations > ⋮ > Dépôts personnalisés.
2. URL : `https://github.com/claudemav/App_Axpertems`, catégorie "Intégration".
3. Installez "AxpertEMS", redémarrez, puis suivez les étapes manuelles ci-dessus à partir de l'étape 3.

## Accès au port série (Docker / HAOS)

Si Home Assistant tourne en conteneur Docker, le port série doit être monté explicitement :
```yaml
devices:
  - /dev/ttyUSB0:/dev/ttyUSB0
```
Vérifiez aussi que l'utilisateur du conteneur a les droits d'accès au périphérique (groupe `dialout` sur l'hôte, ou `privileged: true` en dernier recours).

Sur Home Assistant OS, le port série est généralement accessible sans configuration additionnelle via **Paramètres > Système > Matériel**.

## Installation du Brain (packages YAML)

1. Copiez tous les fichiers de `packages/` dans votre dossier `/config/packages/`.
2. Si les packages ne sont pas encore activés, ajoutez dans `configuration.yaml` :
```yaml
   homeassistant:
     packages: !include_dir_named packages
```
3. Créez les **labels** Home Assistant suivants (Paramètres > Étiquettes) et assignez-les aux entités `switch.*` que vous voulez piloter :
   - `delestage_tier1` — coupées en premier (ex: frigo)
   - `delestage_tier2` — coupées seulement si tout le tier1 est déjà éteint
   - `delestage_tier3` — réservé, coupé en dernier
4. Pour chaque charge labellisée, créez manuellement les deux helpers `input_boolean` correspondants (voir `axpert_brain_manual_lock.yaml` pour l'exemple frigo/télé) :
   - `input_boolean.axpert_manual_lock_<object_id>`
   - `input_boolean.axpert_command_in_progress_<object_id>`

   *(Limite connue : sans ces deux helpers, la charge est délestée/restaurée normalement mais sans verrou manuel ni détection fiable d'action manuelle sur cette charge précise.)*
5. Redémarrez Home Assistant.

## Entités attendues par le Brain

Le Brain YAML référence des entity_id avec le préfixe `debarras_maison_` (ex: `sensor.debarras_maison_puissance_pv`, `select.debarras_maison_mode_de_sortie`) — c'est la convention utilisée sur l'installation d'origine. Si vos entités portent un autre préfixe, adaptez les références dans les fichiers `packages/axpert_brain_*.yaml` et `packages/axpert_derived.yaml` avant de les déposer.

## Migration depuis une ancienne installation (shell_command/MQTT)

Ce composant remplace une chaîne `mpp-solar` + SSH + fichier JSON par une communication série directe. Les entity_id des capteurs natifs sont volontairement identiques à l'ancien système pour éviter de casser les automations/dashboards existants — vérifiez simplement qu'aucune ancienne intégration/automation ne parle encore au même port série en parallèle (risque de collision).

## Licence / Support

Pas de licence formelle définie pour l'instant. Pour signaler un problème : [Issues](https://github.com/claudemav/App_Axpertems/issues).
