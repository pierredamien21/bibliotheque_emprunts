#!/usr/bin/env bash
set -euo pipefail

BASE=${BASE_URL:-http://127.0.0.1:8000}
TS=$(date +%s)
VENV_PYTHON=${VENV_PYTHON:-./env1/bin/python}

echo "Running complete API tests against $BASE"

echo "1) Create category"
res=$(curl -sS -L -X POST "$BASE/categories/" -H "Content-Type: application/json" -d '{"nom_categorie":"TestCat_'$TS'","description":"desc"}')
echo "  response: $res"
cat_id=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('id_categorie'))" <<< "$res")
echo "  category id: $cat_id"

echo "2) Create author"
res=$(curl -sS -L -X POST "$BASE/auteurs/" -H "Content-Type: application/json" -d '{"nom":"Auth'$TS'","prenom":"Aut"}')
echo "  response: $res"
auth_id=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('id_auteur'))" <<< "$res")
echo "  auteur id: $auth_id"

echo "3) Create membre"
email="test.user.$TS@example.com"
res=$(curl -sS -L -X POST "$BASE/membres/" -H "Content-Type: application/json" -d '{"numero_carte":"CARD'$TS'","nom":"Test","prenom":"User","email":"'$email'","id_type_membre":1}')
echo "  response: $res"
mem_id=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('id_membre'))" <<< "$res")
echo "  membre id: $mem_id"

echo "4) Create bibliothecaire"
res=$(curl -sS -L -X POST "$BASE/bibliothecaires/" -H "Content-Type: application/json" -d '{"matricule":"BIB'$TS'","nom":"Bib","prenom":"User","email":"bib'$TS'@example.com","login":"bib'$TS'","mot_de_passe_hash":"hash","role":"Agent"}')
echo "  response: $res"
bib_id=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('id_bibliotecaire'))" <<< "$res")
echo "  bibliothecaire id: $bib_id"

echo "5) Create livre"
res=$(curl -sS -L -X POST "$BASE/livres/" -H "Content-Type: application/json" -d '{"titre":"Livre Test '$TS'","id_categorie":'$cat_id'}')
echo "  response: $res"
livre_id=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('id_livre'))" <<< "$res")
echo "  livre id: $livre_id"

echo "6) Create exemplaire"
res=$(curl -sS -L -X POST "$BASE/exemplaires/" -H "Content-Type: application/json" -d '{"code_barre":"CB-'$TS'","etat":"Disponible","statut_logique":"Actif","id_livre":'$livre_id'}')
echo "  response: $res"
ex_id=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('id_exemplaire'))" <<< "$res")
echo "  exemplaire id: $ex_id"

echo "7) Create emprunt"
res=$(curl -sS -L -X POST "$BASE/emprunts/" -H "Content-Type: application/json" -d '{"statut":"En cours","id_membre":'$mem_id',"id_exemplaire":'$ex_id',"id_bibliotecaire":'$bib_id'}')
echo "  response: $res"
emprunt_id=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('id_emprunt'))" <<< "$res")
echo "  emprunt id: $emprunt_id"

echo "8) Check exemplaire etat"
res=$(curl -sS -L "$BASE/exemplaires/$ex_id/")
echo "  response: $res"
etat=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('etat'))" <<< "$res")
echo "  exemplaire etat: $etat"

if [ "$etat" != "Emprunte" ]; then
  echo "ERROR: exemplaire should be 'Emprunte' after emprunt creation"; exit 1
fi

echo "9) Create reservation"
res=$(curl -sS -L -X POST "$BASE/reservations/" -H "Content-Type: application/json" -d '{"statut":"En attente","priorite":1,"id_membre":'$mem_id',"id_livre":'$livre_id',"id_bibliothecaire":'$bib_id'}')
echo "  response: $res"
resv_id=$($VENV_PYTHON -c "import sys,json;print(json.load(sys.stdin).get('id_reservation'))" <<< "$res")
echo "  reservation id: $resv_id"

echo "API complete tests passed."
