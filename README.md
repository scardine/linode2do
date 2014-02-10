linode2do
=========

How to transfer DNS domains from Linode DNS manager to Digital Ocean

Raison d'être
-------------

I prefer to use the ISP DNS servers than run my own, so I had a dozen domains served by the excelent Linod DNS manager.

Digital Ocean also has a DNS manager, but migrating all domains manualy would be painful - so I wrote this script.

Pre-requisites
--------------

 - Python
 - Python requests library
 - Git
 - Linode API key
 - Digital Ocean client ID and API key

1. Install Linode API bindings
------------------------------

Looks like `linode-python` is not on the [Cheese Shop](https://pypi.python.org/pypi), so you have to clone the repo:

    git clone https://github.com/tjfontaine/linode-python
    
Install:

    pip install linode-python
    
2. Install Requests
-------------------

Requests is a Python library for making HTTP requests.

    pip install requests
    
    
3. Get your Linode API key
--------------------------

Use your Linode username and password to get an API key:

    linode-python/linode/shell.py --user_getapikey --username=jdoe --password=thisisasecret
    
Replace `jdoe` and `thisisasecret` with your username and password and the result should be like:

    {
        "USERNAME": "jdoe",
        "API_KEY": "ArbPtegl213ltegj32eegy1FrTfg7nS1kgVSQjwwJaBZb93bu9Pr3c6DgWc"
    }

4. Get your client ID and API key for Digital Ocean
---------------------------------------------------

Go to https://cloud.digitalocean.com/api_access

5. Run the script
-----------------

Download this script at https://github.com/scardine/linode2do/ and run it.

Example:

    $ python linode2do.py
    Enter your Linode API key: ArbPtegl213ltegj32eegy1FrTfg7nS1kgVSQjwwJaBZb93bu9Pr3c6DgWc
    Enter your DigitalOcean client: BscQufhm213mufhk32ffhz1Gs
    Enter your DigitalOcean API key: 8860836ac947c9bcec862ec119df3464
    
          Transfering example.com
              Record: MX ASPMX5.GOOGLEMAIL.COM
              Record: MX ASPMX.L.GOOGLE.COM
              Record: A 173.255.238.47
              Record: MX ASPMX2.GOOGLEMAIL.COM
              Record: MX ALT2.ASPMX.L.GOOGLE.COM
              Record: MX ALT1.ASPMX.L.GOOGLE.COM
              Record: MX ASPMX3.GOOGLEMAIL.COM
              Record: MX ASPMX4.GOOGLEMAIL.COM
              
              ...

6. Go grab a coffee
-------------------

Get yourself a drink while the script copy all your domains from Linode DNS manager to Digital Ocean.

It should be easy enough to modify this script to change the IP addresses from the Linode host for the Digital Ocean one, but I prefer to do this step by hand.

