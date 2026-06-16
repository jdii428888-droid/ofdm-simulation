#!/usr/bin/env python3
"""
OFDM Link-Level Simulator
Basic point-to-point OFDM communication system with AWGN channel
"""

import numpy as np
from scipy import signal
from scipy.special import erfc
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List


class OFDMTransmitter:
    """OFDM Transmitter Module"""
    
    def __init__(self, num_subcarriers: int = 64, cp_length: int = 16, 
                 modulation: str = 'qam16'):
        """
        Initialize OFDM Transmitter
        
        Args:
            num_subcarriers: Number of OFDM subcarriers
            cp_length: Cyclic prefix length
            modulation: Modulation scheme ('qam4', 'qam16', 'qam64')
        """
        self.num_subcarriers = num_subcarriers
        self.cp_length = cp_length
        self.modulation = modulation
        self.bits_per_symbol = self._get_bits_per_symbol()
        
    def _get_bits_per_symbol(self) -> int:
        """Get bits per symbol for given modulation"""
        mod_dict = {'qam4': 2, 'qam16': 4, 'qam64': 6}
        return mod_dict.get(self.modulation, 4)
    
    def generate_bit_stream(self, num_symbols: int) -> np.ndarray:
        """Generate random bit stream"""
        num_bits = num_symbols * self.num_subcarriers * self.bits_per_symbol
        return np.random.randint(0, 2, num_bits)
    
    def qam_modulate(self, bits: np.ndarray) -> np.ndarray:
        """QAM Modulation"""
        if self.modulation == 'qam4':
            constellation = np.array([1+1j, 1-1j, -1+1j, -1-1j]) / np.sqrt(2)
        elif self.modulation == 'qam16':
            real_part = np.array([-3, -1, 1, 3]) / np.sqrt(10)
            imag_part = np.array([-3, -1, 1, 3]) / np.sqrt(10)
            constellation = np.zeros(16, dtype=complex)
            for i in range(4):
                for j in range(4):
                    constellation[i*4 + j] = real_part[i] + 1j*imag_part[j]
        elif self.modulation == 'qam64':
            real_part = np.linspace(-7, 7, 8) / np.sqrt(42)
            imag_part = np.linspace(-7, 7, 8) / np.sqrt(42)
            constellation = np.zeros(64, dtype=complex)
            for i in range(8):
                for j in range(8):
                    constellation[i*8 + j] = real_part[i] + 1j*imag_part[j]
        
        num_bits_per_symbol = self.bits_per_symbol
        num_symbols = len(bits) // num_bits_per_symbol
        symbols = np.zeros(num_symbols, dtype=complex)
        
        for i in range(num_symbols):
            bit_index = bits[i*num_bits_per_symbol:(i+1)*num_bits_per_symbol]
            symbol_index = int(''.join(map(str, bit_index)), 2)
            symbols[i] = constellation[symbol_index]
        
        return symbols
    
    def ofdm_modulate(self, symbols: np.ndarray) -> np.ndarray:
        """OFDM Modulation: QAM -> IFFT -> Add CP"""
        num_symbols = len(symbols) // self.num_subcarriers
        time_domain = np.zeros((num_symbols, self.num_subcarriers + self.cp_length), 
                               dtype=complex)
        
        for n in range(num_symbols):
            subcarrier_data = symbols[n*self.num_subcarriers:(n+1)*self.num_subcarriers]
            
            # IFFT
            ifft_out = np.fft.ifft(subcarrier_data, self.num_subcarriers)
            
            # Add Cyclic Prefix
            time_domain[n, :self.cp_length] = ifft_out[-self.cp_length:]
            time_domain[n, self.cp_length:] = ifft_out
        
        # Flatten to 1D signal
        return time_domain.flatten()


class OFDMReceiver:
    """OFDM Receiver Module"""
    
    def __init__(self, num_subcarriers: int = 64, cp_length: int = 16, 
                 modulation: str = 'qam16'):
        """
        Initialize OFDM Receiver
        
        Args:
            num_subcarriers: Number of OFDM subcarriers
            cp_length: Cyclic prefix length
            modulation: Modulation scheme
        """
        self.num_subcarriers = num_subcarriers
        self.cp_length = cp_length
        self.modulation = modulation
        self.bits_per_symbol = self._get_bits_per_symbol()
    
    def _get_bits_per_symbol(self) -> int:
        """Get bits per symbol for given modulation"""
        mod_dict = {'qam4': 2, 'qam16': 4, 'qam64': 6}
        return mod_dict.get(self.modulation, 4)
    
    def ofdm_demodulate(self, signal_in: np.ndarray) -> np.ndarray:
        """OFDM Demodulation: Remove CP -> FFT -> Extract subcarriers"""
        symbol_length = self.num_subcarriers + self.cp_length
        num_symbols = len(signal_in) // symbol_length
        
        symbols = np.zeros((num_symbols, self.num_subcarriers), dtype=complex)
        
        for n in range(num_symbols):
            start_idx = n * symbol_length
            # Remove CP
            symbol_with_cp = signal_in[start_idx:start_idx + symbol_length]
            symbol_no_cp = symbol_with_cp[self.cp_length:]
            
            # FFT
            symbols[n, :] = np.fft.fft(symbol_no_cp, self.num_subcarriers)
        
        return symbols.flatten()
    
    def qam_demodulate(self, symbols: np.ndarray) -> np.ndarray:
        """QAM Demodulation: Nearest neighbor detection"""
        if self.modulation == 'qam4':
            constellation = np.array([1+1j, 1-1j, -1+1j, -1-1j]) / np.sqrt(2)
        elif self.modulation == 'qam16':
            real_part = np.array([-3, -1, 1, 3]) / np.sqrt(10)
            imag_part = np.array([-3, -1, 1, 3]) / np.sqrt(10)
            constellation = np.zeros(16, dtype=complex)
            for i in range(4):
                for j in range(4):
                    constellation[i*4 + j] = real_part[i] + 1j*imag_part[j]
        elif self.modulation == 'qam64':
            real_part = np.linspace(-7, 7, 8) / np.sqrt(42)
            imag_part = np.linspace(-7, 7, 8) / np.sqrt(42)
            constellation = np.zeros(64, dtype=complex)
            for i in range(8):
                for j in range(8):
                    constellation[i*8 + j] = real_part[i] + 1j*imag_part[j]
        
        num_symbols = len(symbols)
        bits = np.zeros(num_symbols * self.bits_per_symbol, dtype=int)
        
        for i in range(num_symbols):
            # Find nearest constellation point
            distances = np.abs(symbols[i] - constellation)
            symbol_index = np.argmin(distances)
            
            # Convert to bits
            bit_string = format(symbol_index, f'0{self.bits_per_symbol}b')
            bits[i*self.bits_per_symbol:(i+1)*self.bits_per_symbol] = \
                np.array([int(b) for b in bit_string])
        
        return bits


class AWGNChannel:
    """AWGN Channel Model"""
    
    @staticmethod
    def add_noise(signal_in: np.ndarray, snr_db: float) -> np.ndarray:
        """Add AWGN noise at given SNR"""
        signal_power = np.mean(np.abs(signal_in)**2)
        snr_linear = 10**(snr_db / 10)
        noise_power = signal_power / snr_linear
        noise = np.sqrt(noise_power / 2) * (np.random.randn(len(signal_in)) + 
                                            1j*np.random.randn(len(signal_in)))
        return signal_in + noise


class OFDMSimulator:
    """OFDM System Simulator"""
    
    def __init__(self, num_subcarriers: int = 64, cp_length: int = 16, 
                 modulation: str = 'qam16'):
        """Initialize OFDM Simulator"""
        self.transmitter = OFDMTransmitter(num_subcarriers, cp_length, modulation)
        self.receiver = OFDMReceiver(num_subcarriers, cp_length, modulation)
        self.channel = AWGNChannel()
    
    def simulate(self, num_symbols: int, snr_db: float) -> Dict:
        """Run single simulation"""
        # Transmit
        bits_tx = self.transmitter.generate_bit_stream(num_symbols)
        qam_symbols = self.transmitter.qam_modulate(bits_tx)
        tx_signal = self.transmitter.ofdm_modulate(qam_symbols)
        
        # Channel
        rx_signal = self.channel.add_noise(tx_signal, snr_db)
        
        # Receive
        rx_symbols = self.receiver.ofdm_demodulate(rx_signal)
        bits_rx = self.receiver.qam_demodulate(rx_symbols)
        
        # Calculate BER
        num_errors = np.sum(bits_tx[:len(bits_rx)] != bits_rx)
        ber = num_errors / len(bits_rx)
        
        return {
            'ber': ber,
            'num_errors': num_errors,
            'num_bits': len(bits_rx),
            'snr_db': snr_db
        }
    
    def run_ber_simulation(self, snr_range: np.ndarray, num_symbols: int = 100, 
                          num_trials: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Run BER simulation over SNR range"""
        ber_results = np.zeros_like(snr_range, dtype=float)
        
        for i, snr_db in enumerate(snr_range):
            ber_list = []
            for _ in range(num_trials):
                result = self.simulate(num_symbols, snr_db)
                ber_list.append(result['ber'])
            ber_results[i] = np.mean(ber_list)
        
        return snr_range, ber_results


def theoretical_ber_qam(snr_db: np.ndarray, m: int = 16) -> np.ndarray:
    """Calculate theoretical BER for M-QAM in AWGN"""
    snr_linear = 10**(snr_db / 10)
    
    if m == 4:  # QPSK
        ber = erfc(np.sqrt(snr_linear))
    elif m == 16:  # 16-QAM
        ber = (3/8) * erfc(np.sqrt(snr_linear / 5))
    elif m == 64:  # 64-QAM
        ber = (7/24) * erfc(np.sqrt(snr_linear / 21))
    else:
        ber = np.zeros_like(snr_db)
    
    return ber / 2  # Account for I/Q channels


if __name__ == "__main__":
    # Simulation parameters
    NUM_SUBCARRIERS = 64
    CP_LENGTH = 16
    MODULATION = 'qam16'
    SNR_RANGE = np.arange(0, 15, 2)
    
    print("=" * 60)
    print("OFDM Link-Level Simulator")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  - Subcarriers: {NUM_SUBCARRIERS}")
    print(f"  - CP Length: {CP_LENGTH}")
    print(f"  - Modulation: {MODULATION}")
    print(f"  - SNR Range: {SNR_RANGE[0]} to {SNR_RANGE[-1]} dB")
    print("=" * 60)
    
    # Run simulation
    simulator = OFDMSimulator(NUM_SUBCARRIERS, CP_LENGTH, MODULATION)
    snr_range, ber_simulated = simulator.run_ber_simulation(SNR_RANGE, 
                                                             num_symbols=200,
                                                             num_trials=20)
    
    # Calculate theoretical BER
    ber_theoretical = theoretical_ber_qam(snr_range, m=16)
    
    # Print results
    print("\nBER Results:")
    print(f"{'SNR (dB)':<12} {'Simulated BER':<18} {'Theoretical BER':<18}")
    print("-" * 48)
    for snr, ber_sim, ber_theo in zip(snr_range, ber_simulated, ber_theoretical):
        print(f"{snr:<12.1f} {ber_sim:<18.6e} {ber_theo:<18.6e}")
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.semilogy(snr_range, ber_simulated, 'bo-', label='Simulated', linewidth=2, markersize=8)
    plt.semilogy(snr_range, ber_theoretical, 'r^--', label='Theoretical', linewidth=2, markersize=8)
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    plt.title('OFDM System Performance in AWGN Channel (16-QAM)', fontsize=14, fontweight='bold')
    plt.grid(True, which='both', alpha=0.3)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig('ber_curve.png', dpi=300)
    print("\nBER curve saved as 'ber_curve.png'")
    plt.show()
