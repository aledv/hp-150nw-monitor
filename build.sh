#!/bin/bash

IMAGE_NAME="hp-150nw-monitor"

# Controlla se il flag --force è stato passato
FORCE_BUILD=false
if [[ "$1" == "--force" ]]; then
    FORCE_BUILD=true
fi

# Verifica se l'immagine esiste
IMAGE_EXISTS=$(docker images -q "$IMAGE_NAME")

if [[ -n "$IMAGE_EXISTS" && "$FORCE_BUILD" == false ]]; then
    echo "L'immagine '$IMAGE_NAME' esiste già. Usa '--force' per forzare il rebuild."
    exit 0
fi

echo "Costruzione immagine Docker '$IMAGE_NAME'..."
docker build --no-cache -t "$IMAGE_NAME" .
