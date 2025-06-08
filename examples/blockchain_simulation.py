"""
Blockchain Simulation Example
Demonstrates distributed systems and cryptographic patterns with potential issues
for comprehensive code review testing.
"""

import hashlib
import json
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import random
import threading
from collections import defaultdict
import uuid
from datetime import datetime
import pickle
import os

# ISSUE: Weak cryptographic configuration
HASH_ALGORITHM = "sha256"  # ISSUE: Algorithm should be configurable
DIFFICULTY_TARGET = 4  # ISSUE: Fixed difficulty, not adaptive
BLOCK_SIZE_LIMIT = 1000000  # ISSUE: Hardcoded limit
MINING_REWARD = 50  # ISSUE: Fixed reward amount


@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    fee: float = 0.0
    timestamp: float = field(default_factory=time.time)
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "fee": self.fee,
            "timestamp": self.timestamp,
            "transaction_id": self.transaction_id,
            "signature": self.signature,
        }

    def calculate_hash(self) -> str:
        """Calculate transaction hash - ISSUE: No salt/nonce"""
        transaction_string = (
            f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        )
        return hashlib.sha256(transaction_string.encode()).hexdigest()


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: Optional[str] = None
    merkle_root: Optional[str] = None

    def calculate_merkle_root(self) -> str:
        """Calculate Merkle root - ISSUE: Simplified implementation"""
        if not self.transactions:
            return "0" * 64

        # ISSUE: Not a proper Merkle tree implementation
        tx_hashes = [tx.calculate_hash() for tx in self.transactions]
        combined = "".join(tx_hashes)
        return hashlib.sha256(combined.encode()).hexdigest()

    def calculate_hash(self) -> str:
        """Calculate block hash"""
        self.merkle_root = self.calculate_merkle_root()
        block_string = f"{self.index}{self.timestamp}{self.merkle_root}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int):
        """Mine block with proof of work - ISSUE: CPU-intensive on main thread"""
        target = "0" * difficulty

        # ISSUE: No mining progress indicators
        while not self.hash or not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

            # ISSUE: No upper limit on mining attempts
            if self.nonce % 1000000 == 0:
                print(f"Mining... nonce: {self.nonce}")


class Wallet:
    """Simple wallet implementation - MULTIPLE SECURITY ISSUES"""

    def __init__(self, address: str):
        self.address = address
        self.balance = 0.0
        # ISSUE: Private key stored as simple string
        self.private_key = self._generate_private_key()
        self.transaction_history = []

    def _generate_private_key(self) -> str:
        """Generate private key - ISSUE: Weak randomness"""
        # ISSUE: Using time-based randomness
        random.seed(int(time.time()) + hash(self.address))
        return "".join([hex(random.randint(0, 15))[2:] for _ in range(64)])

    def sign_transaction(self, transaction: Transaction) -> str:
        """Sign transaction - ISSUE: Fake signature implementation"""
        # ISSUE: Not using proper cryptographic signatures
        message = f"{transaction.sender}{transaction.receiver}{transaction.amount}"
        signature_hash = hashlib.sha256(
            (message + self.private_key).encode()
        ).hexdigest()
        return signature_hash

    def create_transaction(
        self, receiver: str, amount: float, fee: float = 0.1
    ) -> Optional[Transaction]:
        """Create new transaction"""

        # ISSUE: No input validation
        if amount + fee > self.balance:
            print(f"Insufficient balance: {self.balance}")
            return None

        transaction = Transaction(
            sender=self.address, receiver=receiver, amount=amount, fee=fee
        )

        # ISSUE: Signature not properly validated
        transaction.signature = self.sign_transaction(transaction)
        return transaction


class TransactionPool:
    """Transaction pool/mempool - ISSUES: No proper concurrency control"""

    def __init__(self):
        self.pending_transactions = []  # ISSUE: Not thread-safe
        self.lock = threading.Lock()  # ISSUE: Basic locking strategy

    def add_transaction(self, transaction: Transaction) -> bool:
        """Add transaction to pool"""

        # ISSUE: No transaction validation
        # ISSUE: No duplicate checking
        # ISSUE: No fee prioritization

        with self.lock:
            self.pending_transactions.append(transaction)
            return True

    def get_transactions_for_block(
        self, max_transactions: int = 100
    ) -> List[Transaction]:
        """Get transactions for new block"""

        with self.lock:
            # ISSUE: No proper transaction ordering (fees, timestamp)
            selected = self.pending_transactions[:max_transactions]
            self.pending_transactions = self.pending_transactions[max_transactions:]
            return selected

    def remove_transactions(self, transaction_ids: List[str]):
        """Remove transactions from pool"""

        with self.lock:
            # ISSUE: Inefficient removal process
            self.pending_transactions = [
                tx
                for tx in self.pending_transactions
                if tx.transaction_id not in transaction_ids
            ]


class Blockchain:
    """Main blockchain implementation - MULTIPLE ARCHITECTURAL ISSUES"""

    def __init__(self):
        self.chain = [self._create_genesis_block()]
        self.difficulty = DIFFICULTY_TARGET
        self.transaction_pool = TransactionPool()
        self.wallets = {}  # ISSUE: Centralized wallet storage
        self.balances = defaultdict(float)  # ISSUE: In-memory balance tracking

        # ISSUE: No proper consensus mechanism
        self.is_mining = False
        self.mining_thread = None

    def _create_genesis_block(self) -> Block:
        """Create the genesis block"""
        genesis_transaction = Transaction(
            sender="genesis", receiver="genesis", amount=0, timestamp=time.time()
        )

        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[genesis_transaction],
            previous_hash="0",
        )

        # ISSUE: Genesis block should be pre-mined
        genesis_block.hash = genesis_block.calculate_hash()
        return genesis_block

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def create_wallet(self, address: str) -> Wallet:
        """Create new wallet - ISSUE: No address validation"""

        if address in self.wallets:
            return self.wallets[address]

        wallet = Wallet(address)
        self.wallets[address] = wallet

        # ISSUE: Give initial balance for testing (unrealistic)
        self.balances[address] = 100.0
        wallet.balance = 100.0

        return wallet

    def add_transaction(self, transaction: Transaction) -> bool:
        """Add transaction to pool"""

        # ISSUE: Minimal transaction validation
        if not self._validate_transaction(transaction):
            return False

        return self.transaction_pool.add_transaction(transaction)

    def _validate_transaction(self, transaction: Transaction) -> bool:
        """Validate transaction - ISSUE: Incomplete validation"""

        # ISSUE: No signature verification
        # ISSUE: No double-spending check
        # ISSUE: No balance verification

        if transaction.amount <= 0:
            return False

        if transaction.sender == transaction.receiver:
            return False

        # ISSUE: Balance check is unreliable
        sender_balance = self.balances.get(transaction.sender, 0)
        if sender_balance < transaction.amount + transaction.fee:
            print(f"Invalid transaction: insufficient balance")
            return False

        return True

    def mine_pending_transactions(self, mining_reward_address: str):
        """Mine a new block - ISSUE: Synchronous mining"""

        if self.is_mining:
            print("Already mining...")
            return

        self.is_mining = True

        try:
            # Get transactions from pool
            transactions = self.transaction_pool.get_transactions_for_block()

            if not transactions:
                print("No transactions to mine")
                return

            # Add mining reward transaction
            reward_transaction = Transaction(
                sender="system",
                receiver=mining_reward_address,
                amount=MINING_REWARD,
                timestamp=time.time(),
            )
            transactions.append(reward_transaction)

            # Create new block
            new_block = Block(
                index=len(self.chain),
                timestamp=time.time(),
                transactions=transactions,
                previous_hash=self.get_latest_block().hash,
            )

            print(f"Mining block {new_block.index}...")
            start_time = time.time()

            # ISSUE: Mining blocks the entire application
            new_block.mine_block(self.difficulty)

            mining_time = time.time() - start_time
            print(
                f"Block mined in {mining_time:.2f} seconds with nonce {new_block.nonce}"
            )

            # Add block to chain
            self.chain.append(new_block)

            # Update balances
            self._update_balances(transactions)

        finally:
            self.is_mining = False

    def _update_balances(self, transactions: List[Transaction]):
        """Update wallet balances - ISSUE: Not atomic"""

        for transaction in transactions:
            if transaction.sender != "system":
                self.balances[transaction.sender] -= (
                    transaction.amount + transaction.fee
                )
                if transaction.sender in self.wallets:
                    self.wallets[transaction.sender].balance = self.balances[
                        transaction.sender
                    ]

            self.balances[transaction.receiver] += transaction.amount
            if transaction.receiver in self.wallets:
                self.wallets[transaction.receiver].balance = self.balances[
                    transaction.receiver
                ]

    def get_balance(self, address: str) -> float:
        """Get balance for address"""
        return self.balances.get(address, 0.0)

    def validate_chain(self) -> bool:
        """Validate the entire blockchain - ISSUE: Expensive operation"""

        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # ISSUE: No proper hash verification
            if current_block.hash != current_block.calculate_hash():
                print(f"Invalid hash at block {i}")
                return False

            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash at block {i}")
                return False

        return True

    def save_blockchain(self, filename: str):
        """Save blockchain to file - ISSUE: Using pickle (security risk)"""

        try:
            with open(filename, "wb") as f:
                # ISSUE: Pickle is not secure for untrusted data
                pickle.dump(self.chain, f)
            print(f"Blockchain saved to {filename}")
        except Exception as e:
            print(f"Failed to save blockchain: {e}")

    def load_blockchain(self, filename: str) -> bool:
        """Load blockchain from file - ISSUE: No validation"""

        try:
            if not os.path.exists(filename):
                return False

            with open(filename, "rb") as f:
                # ISSUE: Loading untrusted pickle data
                loaded_chain = pickle.load(f)

            # ISSUE: No validation of loaded data
            self.chain = loaded_chain
            print(f"Blockchain loaded from {filename}")
            return True

        except Exception as e:
            print(f"Failed to load blockchain: {e}")
            return False


class NetworkNode:
    """Network node simulation - ISSUE: Simplified networking"""

    def __init__(self, node_id: str, blockchain: Blockchain):
        self.node_id = node_id
        self.blockchain = blockchain
        self.peers = []  # ISSUE: Simple peer list
        self.message_queue = []  # ISSUE: No proper message handling

    def add_peer(self, peer_node: "NetworkNode"):
        """Add peer node"""
        if peer_node not in self.peers:
            self.peers.append(peer_node)
            peer_node.peers.append(self)  # ISSUE: Bidirectional without checks

    def broadcast_transaction(self, transaction: Transaction):
        """Broadcast transaction to peers - ISSUE: No flood control"""

        message = {
            "type": "transaction",
            "data": transaction.to_dict(),
            "sender": self.node_id,
            "timestamp": time.time(),
        }

        # ISSUE: Synchronous broadcasting
        for peer in self.peers:
            peer.receive_message(message)

    def broadcast_block(self, block: Block):
        """Broadcast new block to peers"""

        message = {
            "type": "block",
            "data": {
                "index": block.index,
                "timestamp": block.timestamp,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "transactions": [tx.to_dict() for tx in block.transactions],
            },
            "sender": self.node_id,
            "timestamp": time.time(),
        }

        for peer in self.peers:
            peer.receive_message(message)

    def receive_message(self, message: Dict[str, Any]):
        """Receive message from peer - ISSUE: No validation"""

        # ISSUE: Messages processed immediately, no queuing
        if message["type"] == "transaction":
            # ISSUE: No verification of transaction origin
            transaction_data = message["data"]
            transaction = Transaction(**transaction_data)
            self.blockchain.add_transaction(transaction)

        elif message["type"] == "block":
            # ISSUE: No block validation before accepting
            print(f"Received new block from {message['sender']}")
            # ISSUE: Should implement consensus mechanism here


# ISSUE: Global configuration for simulation
SIMULATION_CONFIG = {
    "num_nodes": 3,
    "initial_balance": 100.0,
    "simulation_duration": 60,  # seconds
    "transaction_frequency": 2,  # transactions per second
}


class BlockchainSimulation:
    """Blockchain network simulation - MULTIPLE ISSUES"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.blockchain = Blockchain()
        self.nodes = []
        self.wallets = []
        self.running = False

    def setup_network(self):
        """Setup network of nodes"""

        # Create nodes
        for i in range(self.config["num_nodes"]):
            node_id = f"node_{i}"
            node = NetworkNode(node_id, self.blockchain)
            self.nodes.append(node)

        # ISSUE: Full mesh network (doesn't scale)
        for i, node in enumerate(self.nodes):
            for j, other_node in enumerate(self.nodes):
                if i != j:
                    node.add_peer(other_node)

        # Create wallets
        for i in range(5):  # ISSUE: Fixed number of wallets
            address = f"wallet_{i}"
            wallet = self.blockchain.create_wallet(address)
            self.wallets.append(wallet)

        print(
            f"Network setup complete: {len(self.nodes)} nodes, {len(self.wallets)} wallets"
        )

    def generate_random_transaction(self) -> Optional[Transaction]:
        """Generate random transaction for simulation"""

        if len(self.wallets) < 2:
            return None

        # ISSUE: Simple random selection
        sender_wallet = random.choice(self.wallets)
        receiver_wallet = random.choice([w for w in self.wallets if w != sender_wallet])

        # ISSUE: Random amount without proper validation
        max_amount = min(sender_wallet.balance * 0.5, 10.0)
        if max_amount <= 0:
            return None

        amount = random.uniform(0.1, max_amount)
        fee = amount * 0.01  # 1% fee

        return sender_wallet.create_transaction(receiver_wallet.address, amount, fee)

    def simulation_loop(self):
        """Main simulation loop - ISSUE: Blocking implementation"""

        print("Starting blockchain simulation...")
        start_time = time.time()

        while (
            self.running
            and (time.time() - start_time) < self.config["simulation_duration"]
        ):
            try:
                # Generate random transactions
                for _ in range(self.config["transaction_frequency"]):
                    transaction = self.generate_random_transaction()
                    if transaction:
                        # ISSUE: Add to first node only
                        self.nodes[0].broadcast_transaction(transaction)

                # Mine blocks periodically
                if random.random() < 0.1:  # 10% chance per iteration
                    miner_address = random.choice(self.wallets).address
                    print(f"Mining new block for {miner_address}")
                    self.blockchain.mine_pending_transactions(miner_address)

                # ISSUE: Fixed simulation timestep
                time.sleep(1)

            except KeyboardInterrupt:
                print("Simulation interrupted")
                break
            except Exception as e:
                # ISSUE: Generic exception handling
                print(f"Simulation error: {e}")
                continue

        self.running = False
        print("Simulation completed")

    def run_simulation(self):
        """Run the complete simulation"""

        self.setup_network()
        self.running = True

        try:
            self.simulation_loop()
        finally:
            self.print_simulation_results()

    def print_simulation_results(self):
        """Print simulation results"""

        print("\n" + "=" * 50)
        print("BLOCKCHAIN SIMULATION RESULTS")
        print("=" * 50)

        print(f"Blockchain length: {len(self.blockchain.chain)} blocks")
        print(f"Chain valid: {self.blockchain.validate_chain()}")

        print("\nWallet Balances:")
        for wallet in self.wallets:
            balance = self.blockchain.get_balance(wallet.address)
            print(f"  {wallet.address}: {balance:.2f}")

        print(
            f"\nPending transactions: {len(self.blockchain.transaction_pool.pending_transactions)}"
        )

        # ISSUE: No comprehensive metrics
        total_transactions = sum(
            len(block.transactions) for block in self.blockchain.chain
        )
        print(f"Total transactions processed: {total_transactions}")


def main():
    """Main function - MULTIPLE ISSUES"""

    # ISSUE: No command line argument parsing
    # ISSUE: No configuration file support

    print("Starting Blockchain Simulation...")

    simulation = BlockchainSimulation(SIMULATION_CONFIG)

    try:
        simulation.run_simulation()

        # ISSUE: Optional blockchain persistence
        save_choice = input("\nSave blockchain to file? (y/n): ")
        if save_choice.lower() == "y":
            filename = f"blockchain_{int(time.time())}.pkl"
            simulation.blockchain.save_blockchain(filename)

    except Exception as e:
        # ISSUE: Generic top-level exception handling
        print(f"Simulation failed: {e}")

    print("Program completed")


if __name__ == "__main__":
    # ISSUE: No proper error handling for main execution
    main()
