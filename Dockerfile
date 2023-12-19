# Utilisez une image de base Python officielle
FROM python:3.9-slim

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez les fichiers de dépendances et installez-les
# Assurez-vous d'avoir un fichier requirements.txt à la racine de votre projet
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste des fichiers de votre application dans le conteneur
COPY . .

# Commande pour exécuter votre application
# Remplacez `your_script.py` par le nom de votre script principal
CMD ["python", "./main.py"]
