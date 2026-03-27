# 🛡️ Web Server Log Analysis

A fully dockerised, end-to-end streaming pipeline that simulates web server access logs, processes them through Apache Kafka, enriches and aggregates with Faust, stores in Apache Pinot, and visualises DDoS-pattern attacks in Apache Superset.

---

## 🏗️ Architecture Overview

```
logs_generator.py
       │
       ▼ (writes to file)
  Filebeat
       │
       ▼ (ships to)
 Kafka Topic: `success`
       │
       ▼ (consumed by)
  Faust Worker
  (access_log_parser.py)
       │
       ▼ (produces to)
 Kafka Topic: `enriched-logs`
       │
       ▼ (ingested by)
 Apache Pinot
       │
       ▼ (visualised in)
 Apache Superset
```

---

## 🧰 Tech Stack

| Component | Role |
|---|---|
| **Python** | Log generation & stream processing |
| **Filebeat** | Log shipping agent |
| **Apache Kafka** | Message broker / event streaming |
| **Faust** | Stream processing & log enrichment |
| **Apache Pinot** | OLAP datastore for real-time analytics |
| **Apache Superset** | Dashboarding & DDoS visualisation |
| **Docker / Docker Compose** | Container orchestration |
| **ngrok** | Tunnel for remote access |

---

## 🚀 Getting Started

### 1. Start the Docker Stack

From the project root, spin up all services:

```bash
docker compose up -d
```

---

### 2. Generate Access Logs

From the `logs-generator` directory, start producing synthetic web server access logs:

```bash
python logs_generator.py -o LOG
```

---

### 3. Verify Kafka is Receiving Logs

**Option A — from your host machine:**

```bash
/opt/homebrew/opt/kafka/bin/kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic success \
  --from-beginning
```

**Option B — from inside the Kafka container:**

```bash
docker exec --interactive --tty kafka \
  kafka-console-consumer \
  --bootstrap-server kafka:29092 \
  --topic success \
  --from-beginning
```

---

### 4. Test the Log Parser

Pipe a single Kafka message through the parser to verify enrichment:

```bash
kcat -C -b localhost:9092 -t success -c 1 \
  | jq '.message' \
  | python access_log_parser.py \
  | jq '.'
```

---

### 5. Start the Faust Stream Processor

From the `faust` directory, start the Faust worker:

```bash
faust -A faust_app worker -l info
```

**Verify enriched logs are being produced:**

```bash
kcat -C -b localhost:9092 -t enriched-logs -c 1 | jq '.expandedMessage'
```

---

### 6. Add Tables to Apache Pinot

Register the schema and table config with the Pinot controller:

```bash
docker run \
  -v $PWD/pinot-config:/config \
  --network efps-stack_default \
  apachepinot/pinot:latest AddTable \
  -schemaFile /config/schema.json \
  -tableConfigFile /config/table.json \
  -controllerHost pinot-controller \
  -exec
```

**Inspect Pinot via browser:**

```
http://localhost:9000
```

---

### 7. Set Up Apache Superset Dashboard

#### Step 1 — One-time initialisation

Run these commands once to create the admin user and set up the database:

```bash
docker exec -it superset superset fab create-admin \
  --username admin \
  --firstname Superset \
  --lastname Admin \
  --email admin@superset.com \
  --password admin

docker exec -it superset superset db upgrade
docker exec -it superset superset init
```

> ⚠️ **Known fix:** If you encounter Redis errors, run this inside the `superset` container:
> ```bash
> pip install redis==4.5.4
> ```

#### Step 2 — Open Superset

Navigate to [http://localhost:8088](http://localhost:8088) and log in with the credentials you just created.

#### Step 3 — Connect Apache Pinot as a Database

In Superset, add a new database connection using the following SQLAlchemy URI:

```
pinot+http://pinot-controller:8000/query/sql?controller=http://pinot-controller:9000/
```

---

## 🌐 Remote Access with ngrok

To expose your Superset dashboard externally:

```bash
ngrok http 8088
```

---

## 📁 Project Structure

```
.
├── docker-compose.yml
├── logs-generator/
│   └── logs_generator.py
├── faust/
│   ├── faust_app.py
│   └── access_log_parser.py
└── pinot-config/
    ├── schema.json
    └── table.json
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| Superset won't start with Redis errors | Run `pip install redis==4.5.4` inside superset container |
| Kafka not receiving messages | Check Filebeat config & ensure `docker compose up -d` is healthy |
| Pinot table not found | Re-run the `AddTable` command and verify the controller is up at `:9000` |
| Faust worker crashes | Ensure the `success` topic exists and Kafka is reachable at `localhost:9092` |

---

## 📊 What It Detects

The pipeline is designed to identify **DDoS-type traffic patterns** including:

- Abnormally high request rates from a single IP
- Unusual spikes in specific HTTP status codes (e.g. floods of `200`, `404`, `503`)
- Repeated hits on the same endpoint within a short time window
- Traffic anomalies by user-agent or geographic region

---

## 📝 License

MIT — feel free to fork, extend, and adapt.
