# Securing DeFi-IoT Ecosystems: A Multi-Layered Trusted Oracle Architecture

A robust, multi-layered trusted oracle architecture designed to bridge the gap between Internet of Things (IoT) hardware edge devices and Decentralized Finance (DeFi) smart contracts, mitigating data manipulation attacks using statistical anomaly filtering and secure middleware.

---

## 📌 Features

- **IoT Edge Sensing**: Real-time telemetry ingestion using ESP32 microcontrollers.
- **Lightweight Messaging**: High-throughput message queue implementation via MQTT broker (Mosquitto).
- **Middleware Anomaly Detection**: Statistical $Z$-score filtering to flag and reject malicious, corrupted, or out-of-bounds telemetry payload before on-chain submission.
- **Decentralized Oracle Integration**: Web3 middleware layer processing validated feeds and updating smart contract states.
- **Smart Contract Security**: Circuit breaker logic and emergency pause controls deployed on Solidity smart contracts to protect DeFi protocols against oracle manipulation attacks.

---

## 🏗️ Architecture Overview
## 🛠️ Tech Stack

- **Hardware & Protocols**: ESP32, MQTT (Mosquitto), Serial Communication (pySerial)
- **Backend & Middleware**: Python 3.x, Web3.py, NumPy / SciPy
- **Blockchain & Smart Contracts**: Solidity, Hardhat / Truffle, Ganache / Sepolia Testnet
- **Frontend / Dashboard**: React, Tailwind CSS

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js & npm
- Mosquitto MQTT Broker running locally or on a server
- Ganache CLI or local Ethereum testnet node

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/msganesh79/IoT-Defi-Dashboard.git](https://github.com/msganesh79/IoT-Defi-Dashboard.git)
   cd IoT-Defi-Dashboard
Middleware SetupBashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Smart Contract DeploymentBashcd contracts
npm install
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
Run the Oracle ServiceBashpython oracle_service.py
🛡️ Anomaly Detection LogicData feeds are evaluated using standard $Z$-score thresholding:$$Z = \frac{x - \mu}{\sigma}$$Where:$x$: incoming telemetry data point$\mu$: rolling historical mean$\sigma$: rolling standard deviationData points exceeding the defined threshold ($\vert{}Z\vert{} > T$) are dropped and logged to prevent manipulative state changes in downstream DeFi contracts.
