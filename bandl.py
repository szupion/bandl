from web3 import Web3
from flashbots import Flashbots

# ���������
RPC_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"  # �������� �� ���� Infura Project ID
PRIVATE_KEY = "YOUR_PRIVATE_KEY"  # ��������� ���� ������ ��������, ������� �������� ������
GAS_WALLET_PRIVATE_KEY = "GAS_WALLET_PRIVATE_KEY"  # ��������� ���� ��������, � �������� ����������� ���
RECIPIENT_ADDRESS = "0xRecipientAddress"  # ����� ����������
TOKEN_CONTRACT_ADDRESS = "0xYourTokenContractAddress"  # ����� ��������� ������
FLASHBOTS_ENDPOINT = "https://relay.flashbots.net"

# ����� ����, ������������ � ������� �������� (� ETH)
GAS_AMOUNT = 0.01  # ������� ������ ����� ��� �������� ����

# ����������� � Web3
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# �������� �����������
if not web3.isConnected():
    print("�� ������� ������������ � Ethereum")
    exit()

# �������� Flashbots-��������
flashbots = Flashbots(web3, private_key=PRIVATE_KEY, endpoint=FLASHBOTS_ENDPOINT)

# ���������� ����������
def create_bundle():
    account = web3.eth.account.privateKeyToAccount(PRIVATE_KEY)
    gas_account = web3.eth.account.privateKeyToAccount(GAS_WALLET_PRIVATE_KEY)

    nonce = web3.eth.getTransactionCount(account.address)
    gas_nonce = web3.eth.getTransactionCount(gas_account.address)

    # ������� ���� � ������� ��������
    gas_tx = {
        'to': account.address,  # ��������� ��� �� ���� �������
        'value': web3.toWei(GAS_AMOUNT, 'ether'),  # ����� �������� ����
        'gas': 21000,
        'gasPrice': web3.toWei(50, 'gwei'),  # �������� gwei (����� ������������)
        'nonce': gas_nonce,
        'chainId': 1  # Ethereum Mainnet
    }

    # ������ ������ ���������� (����� ������� �� ��������)
    tx2 = {
        'to': TOKEN_CONTRACT_ADDRESS,
        'data': web3.toHex(b'\x0a' + b'\x01'),  # ������ ��� ������ ������� ������ (������)
        'gas': 100000,
        'gasPrice': web3.toWei(50, 'gwei'),  # �������� gwei (����� ������������)
        'nonce': nonce,
        'chainId': 1  # Ethereum Mainnet
    }

    # ������ ���������� (������� ������� ����������)
    token_amount = web3.toHex(web3.toWei(0.01, 'ether'))  # ������� ������ ����� ������� ��� ��������
    token_tx = {
        'to': RECIPIENT_ADDRESS,
        'data': web3.toHex(b'\x0a' + token_amount),  # ������ ��� �������� �������
        'gas': 100000,
        'gasPrice': web3.toWei(50, 'gwei'),  # �������� gwei (����� ������������)
        'nonce': nonce + 1,
        'chainId': 1  # Ethereum Mainnet
    }

    return [gas_tx, tx2, token_tx]  # ���������� ������ ���������� ��� ������

# �������� ������� ��� �������� ������
def send_bundle():
    bundle = create_bundle()

    # ���������� ����� ����� Flashbots
    response = flashbots.send_bundle(bundle, target_block_number='latest')

    if response['status'] == 'success':
        print("����� ������� ���������!")
    else:
        print("������ ��� �������� ������:", response)

# ������ �������
send_bundle()
