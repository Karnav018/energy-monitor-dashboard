# Smart Home Energy Monitor 🏠⚡

A real-time IoT energy monitoring dashboard for smart homes, built with Streamlit and featuring realistic device simulation.

## Features

### 🏠 Room-based Device Monitoring
- **Living Room**: Smart TV, Air Conditioner, LED Lights
- **Kitchen**: Smart Refrigerator, Microwave, Dishwasher  
- **Bedroom**: AC Unit, Bedside Lamp
- **Solar System**: Rooftop Solar Panels, Inverter
- **Utility**: Smart Electricity Meter, Battery Storage

### ⚡ Real-time Energy Tracking
- Current house power consumption
- Solar power generation
- Grid import/export monitoring
- Battery charge level and status
- Net energy usage calculations

### 📊 Visual Analytics
- 24-hour energy consumption patterns
- Real-time power flow visualization
- Energy source distribution (Solar vs Grid)
- Device status monitoring by room
- Battery level gauge with charging rate

### 🚨 Smart Alerts
- Offline device notifications
- High power consumption warnings
- Temperature anomalies
- System efficiency alerts

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd gyanostav
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv gyan
   source gyan/bin/activate  # On Windows: gyan\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the dashboard**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Explore the dashboard**
   - View real-time energy metrics in the sidebar
   - Monitor device status by room
   - Analyze 24-hour energy patterns
   - Check system alerts and insights

## Dashboard Sections

### 📊 Main Overview
- Real-time energy consumption and generation
- Grid usage (import/export)
- Battery status and charging rate
- System efficiency metrics

### 🏠 Device Management
- Room-by-room device listing
- Individual device power consumption
- Device status monitoring (Online/Offline/Warning)
- Last seen timestamps
- Device-specific parameters (temperature, brightness, etc.)

### 📈 Analytics
- 24-hour energy consumption patterns
- Solar generation vs house consumption
- Energy source distribution
- Daily summary and cost estimates

### 🔍 Insights & Alerts
- Energy efficiency recommendations
- Cost savings calculations
- Device health monitoring
- System performance alerts

## Mock Data

The dashboard uses realistic mock data that simulates:
- **Daily energy patterns** (higher consumption during day/evening)
- **Solar generation cycles** (peak at midday, zero at night)
- **Device behaviors** (appliances turning on/off, varying consumption)
- **Environmental factors** (temperature, efficiency variations)

## Customization

### Adding New Devices
Modify the `HouseIoTSimulator.get_house_devices()` method to add new devices:

```python
"New Room": [
    {
        "id": "ROOM_DEVICE_001", 
        "name": "Device Name", 
        "type": "Device Type",
        "power_consumption": 100,  # Watts
        "status": "Online",
        # Add device-specific parameters
        "last_seen": datetime.now()
    }
]
```

### Modifying Energy Patterns
Update the `generate_hourly_consumption()` method to change:
- Daily consumption patterns
- Solar generation profiles
- Seasonal variations
- Peak usage hours

## Architecture

```
app.py
├── HouseIoTSimulator          # Mock data generation
│   ├── get_house_devices()    # Device inventory by room
│   ├── generate_hourly_consumption()  # Energy usage patterns
│   └── get_current_metrics()  # Real-time calculations
├── Dashboard Layout
│   ├── Sidebar (House Overview)
│   ├── Main KPIs
│   ├── Energy Flow Charts
│   ├── Room Device Details
│   └── Insights & Alerts
└── Styling (CSS)
```

## Technologies Used

- **Streamlit**: Web dashboard framework
- **Plotly**: Interactive data visualization
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Python**: Core application logic

## Future Enhancements

- [ ] Real IoT device integration via MQTT/REST APIs
- [ ] Historical data storage (SQLite/PostgreSQL)
- [ ] Machine learning for usage prediction
- [ ] Mobile responsive design
- [ ] User authentication and multi-home support
- [ ] Integration with smart home platforms (Home Assistant, etc.)
- [ ] Cost optimization recommendations
- [ ] Carbon footprint tracking
- [ ] Weather data integration for solar predictions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

---

**Smart Home Energy Monitor** - Making energy consumption visible and actionable! 🏠⚡📊