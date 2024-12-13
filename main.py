import asyncio
import json
import base64
import datetime
import threading
from solders.pubkey import Pubkey
from websockets.sync.client import connect
from websockets.frames import Opcode
from construct import Bytes, Int64ul, BytesInteger
from construct import Struct as cStruct
from config import settings

LIQUIDITY_STATE_LAYOUT_V4 = cStruct(
    "status" / Int64ul,
    "nonce" / Int64ul,
    "orderNum" / Int64ul,
    "depth" / Int64ul,
    "coinDecimals" / Int64ul,
    "pcDecimals" / Int64ul,
    "state" / Int64ul,
    "resetFlag" / Int64ul,
    "minSize" / Int64ul,
    "volMaxCutRatio" / Int64ul,
    "amountWaveRatio" / Int64ul,
    "coinLotSize" / Int64ul,
    "pcLotSize" / Int64ul,
    "minPriceMultiplier" / Int64ul,
    "maxPriceMultiplier" / Int64ul,
    "systemDecimalsValue" / Int64ul,
    "minSeparateNumerator" / Int64ul,
    "minSeparateDenominator" / Int64ul,
    "tradeFeeNumerator" / Int64ul,
    "tradeFeeDenominator" / Int64ul,
    "pnlNumerator" / Int64ul,
    "pnlDenominator" / Int64ul,
    "swapFeeNumerator" / Int64ul,
    "swapFeeDenominator" / Int64ul,
    "needTakePnlCoin" / Int64ul,
    "needTakePnlPc" / Int64ul,
    "totalPnlPc" / Int64ul,
    "totalPnlCoin" / Int64ul,
    "poolOpenTime" / Int64ul,
    "punishPcAmount" / Int64ul,
    "punishCoinAmount" / Int64ul,
    "orderbookToInitTime" / Int64ul,
    "swapCoinInAmount" / BytesInteger(16, signed=False, swapped=True),
    "swapPcOutAmount" / BytesInteger(16, signed=False, swapped=True),
    "swapCoin2PcFee" / Int64ul,
    "swapPcInAmount" / BytesInteger(16, signed=False, swapped=True),
    "swapCoinOutAmount" / BytesInteger(16, signed=False, swapped=True),
    "swapPc2CoinFee" / Int64ul,
    "poolCoinTokenAccount" / Bytes(32),
    "poolPcTokenAccount" / Bytes(32),
    "coinMintAddress" / Bytes(32),
    "pcMintAddress" / Bytes(32),
    "lpMintAddress" / Bytes(32),
    "ammOpenOrders" / Bytes(32),
    "serumMarket" / Bytes(32),
    "serumProgramId" / Bytes(32),
    "ammTargetOrders" / Bytes(32),
    "poolWithdrawQueue" / Bytes(32),
    "poolTempLpTokenAccount" / Bytes(32),
    "ammOwner" / Bytes(32),
    "pnlOwner" / Bytes(32),
)

account = {
  "jsonrpc": "2.0",
  "id": 1,
  "method": "programSubscribe",
  "params": [
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    {
      "encoding": "jsonParsed"
    }
  ]
}

class PoolListener:
    def __init__(self):
        self.pools = []
    
    def add_pool(self, pool: str):
        if pool in self.pools:
            return
        self.pools.append(pool)
        
    def delete_pool(self, pool: str):
        if pool not in self.pools:
            return
        self.pools.remove(pool)
    
    def parse_message(self, message: str):
        data = message["params"]["result"]["value"]["account"]["data"][0]
        pubkey = message["params"]["result"]["value"]["pubkey"]
                
        if pubkey in self.pools:
            paresd_data = LIQUIDITY_STATE_LAYOUT_V4.parse(base64.b64decode(data))
            print(datetime.datetime.now())
            print(pubkey)
            print(Pubkey.from_bytes(paresd_data.poolCoinTokenAccount))
            print(Pubkey.from_bytes(paresd_data.poolPcTokenAccount))
            print("Base mint:", Pubkey.from_bytes(paresd_data.coinMintAddress))
            print("Quote mint:", Pubkey.from_bytes(paresd_data.pcMintAddress))
            print()

            
            
    def run(self):
        thread = threading.Thread(target=self._run_ws)
        thread.start()
        
    def _start_event_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_ws())
            
    def _run_ws(self):
        with connect(settings.RPC_WEBSOCKET) as websocket:
            websocket.send(json.dumps(account))
            message = websocket.recv()
            print(message)
            while True:
                try:
                    frame = websocket.recv_messages.frames.get()
                    print(frame.opcode)
                    if frame.opcode == Opcode.CLOSE:
                        print("restart connenction")
                        self._run_ws()
                    message = json.loads(websocket.recv())
                    self.parse_message(message)
                except Exception as e:
                    print(e)
                    
listener = PoolListener()
listener.add_pool("HobaNfHNrDcFP8z8T9n3j6K4UF5jSDmdpdxXQpyC83o")
listener.run()