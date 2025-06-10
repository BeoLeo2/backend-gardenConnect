"""
Driver pour le module LoRa SX1278 sur Raspberry Pi
Gère la communication SPI et les GPIO pour le module LoRa
"""
import asyncio
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SX1278Config:
    """Configuration pour le module SX1278"""
    # Pins GPIO (BCM)
    reset_pin: int = 22
    dio0_pin: int = 18
    dio1_pin: int = 23
    
    # Configuration SPI
    spi_bus: int = 0
    spi_device: int = 0
    
    # Paramètres LoRa
    frequency: int = 868000000  # 868 MHz pour l'Europe
    tx_power: int = 14  # dBm
    spreading_factor: int = 7
    bandwidth: int = 125000  # 125 kHz
    coding_rate: int = 5  # 4/5
    preamble_length: int = 8
    sync_word: int = 0x12

class SX1278Driver:
    def __init__(self, config: SX1278Config = None):
        self.config = config or SX1278Config()
        self.spi = None
        self.gpio = None
        self.is_initialized = False
        self.last_rssi = 0
        self.last_snr = 0
        
        # Statistiques
        self.stats = {
            "packets_sent": 0,
            "packets_received": 0,
            "crc_errors": 0,
            "timeouts": 0
        }
    
    async def initialize(self):
        """Initialise le module SX1278"""
        try:
            # Import des bibliothèques (optionnel si pas sur Raspberry Pi)
            try:
                import spidev
                import RPi.GPIO as GPIO
                self.spi = spidev.SpiDev()
                self.gpio = GPIO
            except ImportError:
                logger.warning("RPi.GPIO or spidev not available - using mock mode")
                self.spi = MockSPI()
                self.gpio = MockGPIO()
            
            # Configuration GPIO
            self.gpio.setmode(self.gpio.BCM)
            self.gpio.setup(self.config.reset_pin, self.gpio.OUT)
            self.gpio.setup(self.config.dio0_pin, self.gpio.IN)
            self.gpio.setup(self.config.dio1_pin, self.gpio.IN)
            
            # Configuration SPI
            self.spi.open(self.config.spi_bus, self.config.spi_device)
            self.spi.max_speed_hz = 500000
            self.spi.mode = 0
            
            # Reset du module
            await self._reset_module()
            
            # Configuration du module LoRa
            await self._configure_lora()
            
            self.is_initialized = True
            logger.info("SX1278 driver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SX1278 driver: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Vérifie si le driver est prêt"""
        return self.is_initialized
    
    async def _reset_module(self):
        """Reset matériel du module SX1278"""
        logger.debug("Resetting SX1278 module")
        self.gpio.output(self.config.reset_pin, self.gpio.LOW)
        await asyncio.sleep(0.01)  # 10ms
        self.gpio.output(self.config.reset_pin, self.gpio.HIGH)
        await asyncio.sleep(0.01)  # 10ms
    
    async def _configure_lora(self):
        """Configure le module en mode LoRa"""
        try:
            # Mise en mode sleep
            await self._write_register(0x01, 0x00)
            
            # Mode LoRa
            await self._write_register(0x01, 0x80)
            
            # Fréquence
            await self._set_frequency(self.config.frequency)
            
            # Puissance TX
            await self._write_register(0x09, self.config.tx_power)
            
            # Configuration LoRa
            await self._write_register(0x1D, 
                (self.config.bandwidth << 4) | 
                (self.config.coding_rate << 1) | 
                0x00)
            
            await self._write_register(0x1E, 
                (self.config.spreading_factor << 4) | 
                0x04)  # CRC on
            
            # Preamble
            await self._write_register(0x20, (self.config.preamble_length >> 8) & 0xFF)
            await self._write_register(0x21, self.config.preamble_length & 0xFF)
            
            # Sync word
            await self._write_register(0x39, self.config.sync_word)
            
            # Mode RX continu
            await self._write_register(0x01, 0x85)
            
            logger.debug("SX1278 configured for LoRa mode")
            
        except Exception as e:
            logger.error(f"Failed to configure SX1278: {e}")
            raise
    
    async def _write_register(self, address: int, value: int):
        """Écrit dans un registre SX1278"""
        try:
            response = self.spi.xfer2([address | 0x80, value])
            await asyncio.sleep(0.001)  # Petit délai
        except Exception as e:
            logger.error(f"Failed to write register 0x{address:02X}: {e}")
            raise
    
    async def _read_register(self, address: int) -> int:
        """Lit un registre SX1278"""
        try:
            response = self.spi.xfer2([address & 0x7F, 0x00])
            await asyncio.sleep(0.001)
            return response[1]
        except Exception as e:
            logger.error(f"Failed to read register 0x{address:02X}: {e}")
            raise
    
    async def _set_frequency(self, frequency: int):
        """Configure la fréquence"""
        frf = int((frequency << 19) / 32000000)
        await self._write_register(0x06, (frf >> 16) & 0xFF)
        await self._write_register(0x07, (frf >> 8) & 0xFF)
        await self._write_register(0x08, frf & 0xFF)
    
    async def send_message(self, message: bytes) -> bool:
        """Envoie un message LoRa"""
        try:
            if len(message) > 255:
                logger.error("Message too long for LoRa transmission")
                return False
            
            # Mode standby
            await self._write_register(0x01, 0x81)
            
            # Reset FIFO TX pointer
            await self._write_register(0x0E, 0x00)
            await self._write_register(0x0D, 0x00)
            
            # Longueur du payload
            await self._write_register(0x22, len(message))
            
            # Écriture des données dans la FIFO
            for i, byte in enumerate(message):
                await self._write_register(0x00, byte)
            
            # Mode TX
            await self._write_register(0x01, 0x83)
            
            # Attendre la fin de transmission (DIO0)
            timeout = 5.0  # 5 secondes
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.gpio.input(self.config.dio0_pin):
                    break
                await asyncio.sleep(0.01)
            else:
                logger.error("TX timeout")
                self.stats["timeouts"] += 1
                return False
            
            # Retour en mode RX
            await self._write_register(0x01, 0x85)
            
            self.stats["packets_sent"] += 1
            logger.debug(f"LoRa message sent: {len(message)} bytes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send LoRa message: {e}")
            return False
    
    async def receive_message(self, timeout: float = 1.0) -> Optional[bytes]:
        """Reçoit un message LoRa (non-bloquant)"""
        try:
            # Vérifier si un paquet est disponible (DIO0)
            if not self.gpio.input(self.config.dio0_pin):
                return None
            
            # Lire les flags d'interruption
            irq_flags = await self._read_register(0x12)
            
            # Vérifier RX done
            if not (irq_flags & 0x40):
                return None
            
            # Vérifier CRC
            if irq_flags & 0x20:
                logger.warning("LoRa packet CRC error")
                self.stats["crc_errors"] += 1
                # Clear IRQ flags
                await self._write_register(0x12, 0xFF)
                return None
            
            # Lire la position actuelle et la longueur
            current_addr = await self._read_register(0x10)
            packet_length = await self._read_register(0x13)
            
            if packet_length == 0:
                return None
            
            # Réinitialiser le pointeur FIFO
            await self._write_register(0x0D, current_addr)
            
            # Lire les données
            message = bytearray()
            for _ in range(packet_length):
                byte = await self._read_register(0x00)
                message.append(byte)
            
            # Lire RSSI et SNR
            self.last_rssi = await self._read_register(0x1A) - 164
            self.last_snr = (await self._read_register(0x19)) / 4.0
            
            # Clear IRQ flags
            await self._write_register(0x12, 0xFF)
            
            self.stats["packets_received"] += 1
            logger.debug(f"LoRa message received: {len(message)} bytes, RSSI: {self.last_rssi}dBm")
            
            return bytes(message)
            
        except Exception as e:
            logger.error(f"Failed to receive LoRa message: {e}")
            return None
    
    async def get_rssi(self) -> int:
        """Retourne le RSSI du dernier paquet reçu"""
        return self.last_rssi
    
    async def get_snr(self) -> float:
        """Retourne le SNR du dernier paquet reçu"""
        return self.last_snr
    
    async def cleanup(self):
        """Nettoie les ressources"""
        try:
            if self.spi:
                self.spi.close()
            
            if self.gpio and hasattr(self.gpio, 'cleanup'):
                self.gpio.cleanup()
            
            self.is_initialized = False
            logger.info("SX1278 driver cleaned up")
            
        except Exception as e:
            logger.error(f"Error during SX1278 cleanup: {e}")

# Classes mock pour le développement sans Raspberry Pi
class MockSPI:
    def open(self, bus, device): pass
    def close(self): pass
    def xfer2(self, data): return [0, 0]
    max_speed_hz = 500000
    mode = 0

class MockGPIO:
    BCM = 11
    OUT = 0
    IN = 1
    LOW = 0
    HIGH = 1
    
    def setmode(self, mode): pass
    def setup(self, pin, mode): pass
    def output(self, pin, value): pass
    def input(self, pin): return False  # Simule aucun signal
    def cleanup(self): pass