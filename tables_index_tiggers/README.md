# Tests et déploiement - Base Bibliothèque

Instructions pour appliquer les scripts SQL et exécuter les tests.

Ordre recommandé d'exécution (en local / sur base de test) :

1. Créer les tables (exécuter `table.sql`).

   psql -h <host> -U <user> -d <db> -f tables_index_tiggers/table.sql

2. Créer les triggers et fonctions :

   psql -h <host> -U <user> -d <db> -f tables_index_tiggers/tiggers.sql

3. Créer les vues :

   psql -h <host> -U <user> -d <db> -f tables_index_tiggers/vu.sql

4. Appliquer les permissions (attention aux placeholders de mot de passe) :

   psql -h <host> -U <user> -d <db> -f tables_index_tiggers/permission.sql

   Remplacez `<<SET_AGENT_PASSWORD>>` et `<<SET_API_PASSWORD>>` par des secrets sécurisés
   ou provisionnez les users via un mécanisme sécurisé (vault, script d'init sûr).

5. Créer les index **séparément** (ils utilisent `CREATE INDEX CONCURRENTLY` et ne
   doivent pas être exécutés dans une transaction). Exécuter ce fichier **après**
   la création des tables et triggers.

   psql -h <host> -U <user> -d <db> -f tables_index_tiggers/index.sql

6. Exécuter les tests d'intégration fournis :

   psql -h <host> -U <user> -d <db> -f tables_index_tiggers/test_workflow.sql

Notes et précautions :
- Exécutez tout ceci sur une base de test; sauvegardez votre base réelle.
- `CREATE INDEX CONCURRENTLY` échoue si exécuté dans une transaction.
- Vérifiez la configuration full-text (`french`) si vous comptez utiliser l'index GIN.
- Les scripts `test_workflow.sql` contiennent des blocs `DO` qui lèveront des
  exceptions si quelque chose ne fonctionne pas — utile pour déboguer.

Si vous voulez, je peux:
- exécuter ces commandes pour vous si vous me fournissez une chaîne de connexion
  (host, port, db, user) et autorisez l'exécution ici, ou
- adapter `test_workflow.sql` pour laisser tout dans une transaction et rollback automatique.
