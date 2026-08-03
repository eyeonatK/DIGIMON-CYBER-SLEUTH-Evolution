# DIGIMON-CYBER-SLEUTH-Evolution Router

A dynamic shortest-path evolution & devolution calculator for **Digimon Story: Cyber Sleuth**.
Uses **Dijkstra's Algorithm** with effort-cost weights to find the most efficient level-up & ABI farming route.

## ⚡ Features
- **Effort-Cost Dijkstra Routing:** Prioritizes regressing through lower stages (In-Training / Rookie) over high-cost grinding.
- **Dynamic Rerouting ([BAN] System):** Click `[BAN 🚫]` on any devolution step to instantly exclude undiscovered Digimon.
- **Full Evolution Requirements:** Displays Level, HP, SP, ATK, DEF, INT, SPD, ABI, CAM & special item conditions.

## 🚀 How to Run Locally
1. Clone this repository:
   '''bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   
2. Install dependencies:
   pip install -r requirements.txt

3. Launch Streamlit app:
   streamlit run app.py


## 📊 Data Source & Credits
The Digimon stats, evolution trees, and requirement datasets used in this project are sourced from:
- **Kaggle Dataset:** [Digimon Cyber Sleuth Complete Database](https://www.kaggle.com/datasets/lianebrisebois/digimon-cyber-sleuth-dataset)
- **DigiDB:** [DigiDB.io](http://digidb.io/) (Digimon Cyber Sleuth Database)

*All Digimon characters and intellectual property belong to Bandai Namco Entertainment.*
