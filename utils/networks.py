class Network:
    def __init__(
            self,
            name: str,
            rpc: list,
            chain_id: int,
            eip1559_support: bool,
            token: str,
            explorer: str,
            decimals: int = 18,
            input_chain_name: str = ""
    ):
        self.name = name
        self.input_chain_name = name.lower() if input_chain_name == "" else input_chain_name
        self.rpc = rpc
        self.chain_id = chain_id
        self.eip1559_support = eip1559_support
        self.token = token
        self.explorer = explorer
        self.decimals = decimals

    def __repr__(self):
        return f"{self.name}"

    
Ethereum = Network(
    name="Ethereum",
    rpc=[
        "https://rpc.ankr.com/eth",
        "https://eth.drpc.org",
        "https://ethereum-rpc.publicnode.com",
    ],
    chain_id=1,
    eip1559_support=True,
    token="ETH",
    explorer="https://etherscan.io/"
)

ZkSync = Network(
    name="ZkSync Era",
    input_chain_name="zksync-era",
    rpc=[
        "https://mainnet.era.zksync.io",
    ],
    chain_id=324,
    eip1559_support=True,
    token="ETH",
    explorer="https://era.zksync.network/",
)

Optimism = Network(
    name="Optimism",
    rpc=[
        "https://rpc.ankr.com/optimism/",
        "https://optimism.drpc.org",
        "https://optimism.meowrpc.com",
    ],
    chain_id=10,
    eip1559_support=True,
    token="ETH",
    explorer="https://optimistic.etherscan.io/",
)

Base = Network(
    name="Base",
    rpc=[
        "https://mainnet.base.org",
        "https://base.meowrpc.com",
        "https://base.drpc.org",

    ],
    chain_id=8453,
    eip1559_support=False,
    token="ETH",
    explorer="https://basescan.org/"
)

Arbitrum = Network(
    name="Arbitrum",
    rpc=[
        "https://rpc.ankr.com/arbitrum/",
        "https://arbitrum.drpc.org",
        "https://arbitrum.meowrpc.com",
    ],
    chain_id=42161,
    eip1559_support=True,
    token="ETH",
    explorer="https://arbiscan.io/",
)
