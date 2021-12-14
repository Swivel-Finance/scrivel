```
                             ____
                            / . .\
        SCRIpted swiVEL     \  ---<
                             \  /
                      _______/ /
                -=:___________/    (luk at de snaek)    
```

# scrivel
Scripting the Swivel Finance Protocol with Python

### psa
We suggest you create a virtual environment for this and every python project. 
Regardless of your environment, your `PRIVATE_KEY` must be set as an environment variable.

#### assure you have python available
This is a python project, i'm just going to assume you have a python available. If not, do that first.
Scrivel expects at least a Python version of 3.7.3

#### assure you have pip available
`which pip`. Depending on your system it may be aliased with ...3 so, `which pip3`. If not present install it.

#### with virtualenv
Once you have pip available use `pip install --upgrade virtualenv` (sudo it if you must...).

Now you are free to place the virtual environment for this project anywhere you want. This author uses a `~/python/` top level directory
to house all virtualenvs (which this author makes for each python project).

    virtualenv -p python3 ~/python/scrivel

With the env made, source it.

    source ~/python/scrivel/bin/activate

Now you can move to installing things...

## installation
Clone the repo, cd into the rood dir, (activate your virtual env if you have not) then

    pip install -r requirements.txt

### before you run the examples
Each of the files in `/scrivel/examples` needs its `shebang` modified to point to the python executable you created with virtualenv.
For example if you followed the path above
    
    #!/home/<your_user_name>/python/scrivel/bin/python

If not, just make it match wherever you put it.

#### Constants
You'll need to modify the constants located in `/scrivel/constants/__init__.py`:

* HTTP_PROVIDER: (string) A suitable URL for a Web3.py HTTP Provider
* WS_PROVIDER: (string) A suitable URL for a Web3.py WSS Provider
* PUB_KEY: (string) Your public key you wish to use
* MARKET_PLACE_ADDRESS: (string) The address of the deployed MarketPlace smart contract you want to interct with
* SWIVEL_ADDRESS: (string) The address of the deployed Swivel smart contract you want to interct with
* DAI_UNDERLYING: (string) Address for the underlying token of an active DAI market
* DAI_MATURITY: (int) Maturity timestap (unix epoch in seconds) for the above active DAI market
* VAULT_ADDRESS: (string) Address of the vault associated with the above active DAI market

##### note on the above DAI market
As an example, you could use the addresses from the currently deployed contracts on Rinkeby:

    DAI_UNDERLYING = '0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa'
    DAI_MATURITY = 1669957199
    VAULT_ADDRESS = '0xaEC3322CE4092a45b3B1B999c79B9F780E057BA5'

This is just one example market, it could, of course, be any other active market. USDC, etc... Feel free to make
any constants you want for others obviously.

## run the examples
The example files can then be run by (assuming you are in the repo root dir)

    python scrivel/examples/<foo>_<bar>.py

# todo
Profit.
