# Drogon-Twitter (French translation)
Drogon-Twitter est un robot pour twitter écrit en python, utilisant principalement le dictionnaire offert par twython pour communiquer avec l'API de Twitter. Ce bot est simplement écrit dans un cadre d'usage personnel. Je trouve ça amusant, et puis ça peut toujours être utile pour certaines tâches, qui sait. En effet, Drogon-Twitter a pour le moment, la principale tâche de faire du monitoring. Mais ce serait négliger d'autres possibilités ! Je ne m'y connais pas plus que ça en Python, mais j'ai essayé de faire quelque chose de potable et de marrant. C'est plus un défi personnel d'aboutir à quelque chose d'original qu'autre chose, pour le moment.

### Requirements
Drogon-Twitter nécessite pour le moment une version de Python 2.7 fonctionnelle sur votre système d'exploitation. Vous pouvez installer les modules nécessaires à l'aide de 'pip install module' :
- twython
- psutil
- speedtest-cli
- apscheduler==2.1.2 (je n'ai pas cherché à faire fonctionner la version 3 pour le moment)

### How to
Avant de lancer quoique ce soit, vérifiez que les variables correspondent bien à votre configuration actuelle. Vous devrez certainement créer une application Twitter pour compléter apiKey, apiSecret, accessToken et acessTokenSecret. Vous ne devriez avoir aucun mal à utiliser le reste. Les variables doivent pointer vers des dossiers et des fichiers EXISTANTS même s'ils sont vides.

___NOTE___ : le script est adapté à mon usage personnel, c'est-à-dire que j'apprécie par exemple séparer Transmission de Owncloud, et j'utilise rkhunter avec cron.daily.

___NOTE___ : veuillez utiliser un compte réservé à votre bot. Le script est destiné à cet usage, avec une interaction avec votre compte principal. De plus, le script supprime tous vos tweets dans un délai de 24h pour nettoyer le compte bot et éviter l'accumulation de tweets. Désactivez le scheduler si vous utilisez votre compte personnel...

Lancez le script (pour la première fois, mieux vaut le contrôler ainsi), si rien ne s'affiche, c'est tout à fait normal. Si vous avez veillé à bien remplir les variables, vous aurez un fichier log dans lequel sont enregistrés les tweets "reçus" par le bot auxquels il a répondu. Les erreurs sont également affichées dans le log en cas de soucis. Le log est nettoyé toutes les 24h en même temps que la suppression automatique des tweets. Vous pouvez désactiver ce que vous voulez en commentant correctement les fonctions que vous ne voulez pas utiliser.

Par défaut, le bot répond à une action (cf. le script) quand le compte 'master' envoie un tweet mentionnant (@) le compte 'bot'. Pour savoir si tout fonctionne correctement, envoyez @bot toast. Le bot devra répondre en tweetant "Tell me what I've to do...".

___NOTE___: certains tweets contiennent des nombres aléatoirement générés entre 1 et 9999 (modifiable, évidemment). C'est simplement pour contourner la limitation de Twitter qui restreint les tweets identiques à un temps... indéfini. Pour que le bot puisse fonctionner correctement et dans la durée, ce fut nécessaire.

### LICENSE
Ce logiciel est modestement mis à disposition sous la license WTFPL. Faites-en ce que vous en voulez. Je m'en tape, vraiment, et c'est pas comme si ce script allait révolutionner le monde du monitoring.
