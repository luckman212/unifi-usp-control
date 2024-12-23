<img src=usp-plug.png width=200>

## unifi-usp-control

Simple Python wrapper around the Unifi API to control or retrieve status of a [USP-Plug][1] device.

### Setup and Usage

Requires a semi-recent Python with the `requests` module installed.

Edit the script to adjust the variables at the top such as default device MAC, site id, Unifi controller hostname, and API login credentials.

Run with `-h` or `--help` for help on the commandline arguments.

```
$ ./usp_power.py -h
usage: usp_power.py [--site SITE] [--mac MAC] [{get,on,off,toggle}]

Control UniFi USP-Plug outlet power state

positional arguments:
  {get,on,off,toggle}  Get or Set desired power state

options:
  --site, -s SITE      Site ID (as shown in Unifi web interface)
  --mac, -m MAC        MAC address of USP-Plug
```

### List of program variables

- `HOST` the hostname and port of your Unifi controller e.g. `unifi.foo.com:8443`
- `USER` a user to authenticate with for API calls (typically `admin`)
- `PASS` password (yes I know it's not a good idea to store passwords in the clear! Please fork the script and improve the security by using environment vars, password managers, cryptography or whatever other method you see fit!)
- `DEFAULT_MAC` = 'aa:bb:cc:dd:ee:ff'
- `DEFAULT_SITE` = The site ID where your USP-Plug resides (you will see this if you navigate to your Unifi controller, it is the part after the `/manage/` in the URL)
```

### Can this program do _xyz_ ?

I wrote this to scratch my own itch. I've tested it fairly extensively on my own setup, but YMMV. I am running UNA version 9.0.106 as of this writing. Bugreports or PRs to add features welcome!


[1]: https://store.ui.com/us/en/products/unifi-smart-power
