# Classifying causes for Active Scanning using Machine Learning Techniques

## Data Collection Scripts

### Beacon Loss - BL
Scripts for collecting data for `Beacon Loss` AS cause.  
When a client does not receive beacons from an associated Access Point at an expected regular interval, `Beacon Loss` cause is said to occur.

#### Simulation Explanation
We use `hostapd` [https://w1.fi/hostapd/] to create an Access Point. All the client devices connect to the access point. After successful connection, the Access Point is turned off. This injects `Beacon Loss`.

1. Start Access Point on an interface
2. Connect all client devices to the said Access Point (using wpa_supplicant)
3. Once connection establishment is done, start the capture
4. Turn off the Access Point
5. Wait for the scan and stop the capture
6. Rinse and Repeat

#### Run
1. Download and configure `hostapd`. A configured version is already provided in repository. You may need to adjust it according to your environment
2. Configure the following:
    - `interface` on which the Access Point will be created
    - `channel`
    - `ssid`
    - `wpa2` security
3. Create a `wpa_supplicant` configuration file. A configured version is already provided in repository. You may need to adjust it according to your environment
4. Create a `env.py` by copying  `sample_env.py`. Provide values for each global variable defined in `env.py`
5. Run `main.py`

#### Caveats
- Run `main.py` with superuser privileges
- If running without IDE (preferred):
    - `source` the `venv`
    - Add project root (`src`) to `$PYTHONPATH`
- To log the entire collection session use `script` command
