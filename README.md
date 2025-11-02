# HP 150nw Printer Monitor per Raspberry Pi

Monitor per stampante HP 150nw che espone API REST per monitorare stato, livelli toner e pagine stampate.

## 🚀 Installazione Rapida

### Prerequisiti
- Raspberry Pi 5 con Raspberry Pi OS
- Docker e Docker Compose installati
- Stampante HP 150nw connessa alla rete

### Installazione Docker (se non presente)
```bash
# Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installa Docker Compose
sudo apt-get update
sudo apt-get install docker compose-plugin
```

### Deploy dell'applicazione

1. **Scarica i file del progetto**
2. **Rendi eseguibile lo script di build**
   ```bash
   chmod +x build.sh
   ```

3. **Avvia il build**
   ```bash
   ./build.sh
   ```
4. **Avvia il deploy**
   ```bash
   docker compose up -d
   ```

## 📡 API Disponibili

### Stato Stampante e Livelli Toner
```bash
GET /printer/{ip}
```
Verifica lo stato del servizio:
```json
{
	"status": "inPowerSave",
	"toner_levels": {
		"Black": {
			"level": "100%",
			"product_number": "W2070A",
			"state": "ok"
		},
		"Cyan": {
			"level": "100%",
			"product_number": "W2071A",
			"state": "ok"
		},
		"Magenta": {
			"level": "100%",
			"product_number": "W2073A",
			"state": "ok"
		},
		"Yellow": {
			"level": "100%",
			"product_number": "W2072A",
			"state": "ok"
		}
	}
}
```

## 🛠️ Comandi Utili

### Visualizza logs
```bash
docker compose logs -f
```

### Riavvia il servizio
```bash
docker compose restart
```

### Ferma il servizio
```bash
docker compose down
```

### Ricostruisci l'immagine
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Stato del container
```bash
docker compose ps
```

## 🔍 Troubleshooting

### Stampante non trovata
1. Verifica che la stampante sia accesa e connessa alla rete
2. Controlla l'IP della stampante nel pannello di controllo

### Servizio non raggiungibile
1. Verifica che il container sia in esecuzione: `docker compose ps`
2. Controlla i logs: `docker compose logs`
3. Verifica la porta: `netstat -tlnp | grep 5001`

## 🆘 Supporto

Se riscontri problemi:
1. Verifica i logs: `docker compose logs`
2. Controlla la connettività alla stampante
3. Verifica la configurazione dell'IP

## 📝 Note

- Il servizio è ottimizzato per Raspberry Pi 5 (ARM64)
- Compatibile con stampanti HP 150nw
- Può essere adattato per altri modelli HP modificando main.py
