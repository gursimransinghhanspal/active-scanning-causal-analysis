# Classifying causes for Active Scanning using Machine Learning Techniques

## Data Collection Scripts

### Beacon Loss - BL
Scripts for collecting data for `Beacon Loss` AS cause.

#### Explanation
We use `hostapd` [https://w1.fi/hostapd/] to create an Access Point. All the client devices connect to the access point. After successful connection, the Access Point is turned off. This injects the `BL` cause.

#### Steps
1. Start Access Point on an interface
2. Connect all client devices to the said Access Point (using wpa_supplicant)
3. Once connection establishment is done, start the capture
4. Turn off the Access Point
5. Wait for the scan and stop the capture

#### Run
1. Configure `hostapd.conf` file 
