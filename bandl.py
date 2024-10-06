from web3 import Web3
from flashbots import Flashbots

# Настройки
RPC_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"  # Замените на свой Infura Project ID
PRIVATE_KEY = "YOUR_PRIVATE_KEY"  # Приватный ключ вашего кошелька, который получает токены
GAS_WALLET_PRIVATE_KEY = "GAS_WALLET_PRIVATE_KEY"  # Приватный ключ кошелька, с которого переводится газ
RECIPIENT_ADDRESS = "0xRecipientAddress"  # Адрес получателя
TOKEN_CONTRACT_ADDRESS = "0xYourTokenContractAddress"  # Адрес контракта токена
FLASHBOTS_ENDPOINT = "https://relay.flashbots.net"

# Сумма газа, переводимого с другого кошелька (в ETH)
GAS_AMOUNT = 0.01  # Укажите нужную сумму для перевода газа

# Подключение к Web3
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Проверка подключения
if not web3.isConnected():
    print("Не удалось подключиться к Ethereum")
    exit()

# Создание Flashbots-инстанса
flashbots = Flashbots(web3, private_key=PRIVATE_KEY, endpoint=FLASHBOTS_ENDPOINT)

# Подготовка транзакций
def create_bundle():
    account = web3.eth.account.privateKeyToAccount(PRIVATE_KEY)
    gas_account = web3.eth.account.privateKeyToAccount(GAS_WALLET_PRIVATE_KEY)

    nonce = web3.eth.getTransactionCount(account.address)
    gas_nonce = web3.eth.getTransactionCount(gas_account.address)

    # Перевод газа с другого кошелька
    gas_tx = {
        'to': account.address,  # Переводим газ на свой кошелек
        'value': web3.toWei(GAS_AMOUNT, 'ether'),  # Сумма перевода газа
        'gas': 21000,
        'gasPrice': web3.toWei(50, 'gwei'),  # Указание gwei (можно регулировать)
        'nonce': gas_nonce,
        'chainId': 1  # Ethereum Mainnet
    }

    # Пример второй транзакции (клейм токенов из вестинга)
    tx2 = {
        'to': TOKEN_CONTRACT_ADDRESS,
        'data': web3.toHex(b'\x0a' + b'\x01'),  # Данные для вызова функции клейма (пример)
        'gas': 100000,
        'gasPrice': web3.toWei(50, 'gwei'),  # Указание gwei (можно регулировать)
        'nonce': nonce,
        'chainId': 1  # Ethereum Mainnet
    }

    # Третья транзакция (перевод токенов получателя)
    token_amount = web3.toHex(web3.toWei(0.01, 'ether'))  # Укажите нужную сумму токенов для перевода
    token_tx = {
        'to': RECIPIENT_ADDRESS,
        'data': web3.toHex(b'\x0a' + token_amount),  # Данные для перевода токенов
        'gas': 100000,
        'gasPrice': web3.toWei(50, 'gwei'),  # Указание gwei (можно регулировать)
        'nonce': nonce + 1,
        'chainId': 1  # Ethereum Mainnet
    }

    return [gas_tx, tx2, token_tx]  # Возвращаем список транзакций для бандла

# Основная функция для отправки бандла
def send_bundle():
    bundle = create_bundle()

    # Отправляем бандл через Flashbots
    response = flashbots.send_bundle(bundle, target_block_number='latest')

    if response['status'] == 'success':
        print("Бандл успешно отправлен!")
    else:
        print("Ошибка при отправке бандла:", response)

# Запуск функции
send_bundle()
