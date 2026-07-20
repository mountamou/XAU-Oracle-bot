# 📱 Générer l'APK XAU ORACLE (via GitHub Actions)

Comme Windows ne peut pas compiler un APK Kivy, on utilise le cloud gratuit de GitHub.
**Aucun logiciel à installer** — tout se fait dans le navigateur.

---

## Étape 1 — Créer un compte GitHub (si pas déjà fait)
1. Aller sur https://github.com/signup
2. Créer un compte (gratuit).

## Étape 2 — Créer un dépôt (repository)
1. Cliquer sur **+** en haut à droite → **New repository**.
2. Nom : `xau-oracle`
3. Choisir **Public** (ou Private).
4. Cliquer **Create repository**.

## Étape 3 — Envoyer les fichiers du projet
1. Sur la page du dépôt vide, cliquer **uploading an existing file**.
2. Glisser-déposer **TOUS** ces fichiers/dossiers du projet :
   - `main.py`
   - `connexion_broker.py`
   - `buildozer.spec`
   - `requirements.txt`
   - `README.md`
   - le dossier `.github` (⚠️ le plus important — contient le workflow de build)
3. Cliquer **Commit changes**.

> 💡 Si le dossier `.github` n'apparaît pas au glisser-déposer (dossier caché) :
> créez le fichier manuellement sur GitHub → **Add file** → **Create new file** →
> nommez-le `.github/workflows/build-apk.yml` → collez le contenu du fichier local.

## Étape 4 — Lancer la compilation
1. Onglet **Actions** du dépôt.
2. Le build **"Build XAU ORACLE APK"** démarre automatiquement après l'upload.
   (Sinon : clic sur le workflow → **Run workflow**.)
3. Attendre **20 à 40 minutes** (premier build = téléchargement du SDK/NDK Android).

## Étape 5 — Télécharger l'APK
1. Quand le build est ✅ vert, cliquer dessus.
2. En bas, section **Artifacts** → télécharger **`XAU-ORACLE-apk`**.
3. Décompresser le `.zip` → vous obtenez **`xau_oracle-1.0-...-debug.apk`**.

## Étape 6 — Installer sur Android
1. Copier l'APK sur le téléphone.
2. Autoriser **"Sources inconnues"** dans Paramètres.
3. Ouvrir l'APK → Installer → l'app **XAU ORACLE** apparaît.

---

---

## 🔐 (Optionnel) APK SIGNÉ pour distribution / Play Store

Le build ci-dessus donne un APK **debug** (suffisant pour l'installer soi-même).
Pour un APK **signé** (Play Store, distribution large), suivez ceci **une seule fois** :

### A. Créer une clé de signature (keystore)
Il faut Java (`keytool`). Le plus simple : le faire dans **Google Colab** ou une machine avec Java.
Commande :
```bash
keytool -genkey -v -keystore xau-oracle.keystore \
  -alias xauoracle -keyalg RSA -keysize 2048 -validity 10000
```
Notez bien le **mot de passe** choisi et l'**alias** (`xauoracle`).

### B. Convertir le keystore en texte (base64)
```bash
base64 xau-oracle.keystore > keystore.txt        # Linux/Mac/Colab
```
Copiez tout le contenu de `keystore.txt`.

### C. Ajouter les secrets sur GitHub
Dépôt → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
Créez ces 4 secrets :
| Nom | Valeur |
|-----|--------|
| `KEYSTORE_BASE64` | le contenu de `keystore.txt` |
| `KEY_ALIAS` | `xauoracle` |
| `KEYSTORE_PASSWORD` | votre mot de passe |
| `KEY_PASSWORD` | votre mot de passe (souvent le même) |

### D. Lancer le build signé
Onglet **Actions** → workflow **"Build XAU ORACLE APK (Signe / Release)"** → **Run workflow**.
À la fin → artifact **`XAU-ORACLE-apk-signe`** → APK signé prêt à distribuer.

> ⚠️ **Gardez précieusement le keystore et les mots de passe.** Sans eux, vous ne
> pourrez plus publier de mise à jour de l'app sur le Play Store.

---

## ⚠️ Notes importantes
- Le build par défaut (onglet Actions) donne un APK **debug** — parfait pour tester/installer soi-même.
- L'**icône XAU ORACLE** (fond sombre + anneau doré) est générée automatiquement à chaque build.
- Le bot utilise un **simulateur de marché** par défaut. Pour des données réelles,
  il faut brancher `connexion_broker.py` sur un vrai broker (OANDA, etc.).
- ⚠️ Le trading comporte des risques. Outil éducatif — testez sur compte démo.
