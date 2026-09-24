# Crane Stability Model

This project simulates the **braking dynamics of a crawler crane** to determine the **maximum safe speed before tipping**.  
It uses real-case-inspired data to model the behavior during emergency braking and explore the margins allowed by international standards.

---

## 🚧 Purpose

> **Main Goal:**  
To compute the maximum speed at which a crane can brake **without tipping over**, depending on its configuration and radius.

This project also helps **evaluate the conservatism** of the ISO 4305 norm, which limits crawler cranes to a travel speed of **1.1 km/h**, while simulations suggest they can safely move at **up to 5 km/h** or more.

---

## 📊 Context

- Based on **real-world engineering work** conducted during an internship at **Tadano**.
- For confidentiality reasons, all data (COG, radius, masses, etc.) used in the code are **synthetic and anonymized**.

---

## 🧮 Physics & Parameters

### Key Definitions:
- `x_cog`, `z_cog` → center of gravity coordinates  
- `radius` → outreach of the load  
- `width` → crane base width  
- `mass_total` → total system mass (structure + load)  
- `IT = m*r²` → inertia (assuming `IG = 0`)  
- `phi_model` → angle computed during braking  
- `phi_phys` → final physical tipping angle  
- Moments are **positive clockwise**

### Motion:
- The crane moves **right to left**
- `0` is the **center of the crane** (`width / 2`)
- Tipping point is at the **front** of the crane

---

## 🧪 Features

- **Braking simulation** with RK4 solver
- **Tipping detection** logic
- **Monte Carlo simulations** to assess speed uncertainty
- **Database generation** of safe speeds (`.sqlite`)
- **Data visualization** of results

---

## 📂 Project Structure

```bash
.
├── main.py              # User interface for running simulations
├── parameters.py        # Contains crane configuration (COG, mass, etc.)
├── forces.py            # Computes braking force & dynamics
├── monte_carlo_sim.py   # Monte Carlo simulation logic
├── create_database.py   # Computes vmax per config (tables `analysis` by s_brake, `analysis_time` by t_brake)
├── plotting.py          # Visualization functions
├── crane_vmax.sqlite    # SQLite database of results
└── README.md            # This file
📈 Sample Output
text
Copy code
i=0, R=10.0 m, s_brake=1.0 : vmax=1.613 m/s (5.81 km/h)
i=1, R=11.0 m, s_brake=1.0 : vmax=1.583 m/s (5.70 km/h)
...
⚙️ Requirements
Python 3.x

NumPy

Pandas

Matplotlib

SQLite3 (standard library)

Install packages:

bash
Copy code
pip install numpy pandas matplotlib
📌 Notes
This is a non-commercial academic/research project.

ISO 4305 provides a high safety margin, but our simulations show significant dynamic headroom.

Do not use this tool for real crane certification or operational decision
