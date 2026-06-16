#!/usr/bin/env python3
"""
Example usage of OFDM Simulator
Demonstrates various scenarios and customization options
"""

import numpy as np
import matplotlib.pyplot as plt
from ofdm_simulator import OFDMSimulator, theoretical_ber_qam


def example_1_basic_simulation():
    """
    Example 1: Basic BER simulation with default parameters
    """
    print("\n" + "="*70)
    print("Example 1: Basic BER Simulation")
    print("="*70)
    
    # Create simulator with default parameters
    simulator = OFDMSimulator(num_subcarriers=64, cp_length=16, modulation='qam16')
    
    # Define SNR points
    snr_range = np.array([0, 5, 10, 15])
    
    # Run simulation
    snr_out, ber_sim = simulator.run_ber_simulation(
        snr_range, 
        num_symbols=200, 
        num_trials=10
    )
    
    # Calculate theoretical BER
    ber_theo = theoretical_ber_qam(snr_out, m=16)
    
    # Print results
    print("\n{:<12} {:<18} {:<18} {:<12}".format(
        "SNR (dB)", "Simulated BER", "Theoretical BER", "Error (%)"
    ))
    print("-" * 60)
    for snr, ber_s, ber_t in zip(snr_out, ber_sim, ber_theo):
        error = abs(ber_s - ber_t) / ber_t * 100
        print("{:<12.1f} {:<18.6e} {:<18.6e} {:<12.1f}".format(
            snr, ber_s, ber_t, error
        ))


def example_2_different_modulations():
    """
    Example 2: Compare different modulation schemes
    """
    print("\n" + "="*70)
    print("Example 2: Modulation Comparison (QPSK vs 16-QAM vs 64-QAM)")
    print("="*70)
    
    snr_range = np.linspace(0, 20, 5)
    modulations = ['qam4', 'qam16', 'qam64']
    results = {}
    
    for mod in modulations:
        print(f"\nTesting {mod.upper()}...")
        simulator = OFDMSimulator(modulation=mod)
        _, ber = simulator.run_ber_simulation(snr_range, num_symbols=100, num_trials=5)
        results[mod] = ber
    
    # Plot comparison
    plt.figure(figsize=(10, 6))
    for mod in modulations:
        label = {'qam4': 'QPSK', 'qam16': '16-QAM', 'qam64': '64-QAM'}[mod]
        plt.semilogy(snr_range, results[mod], 'o-', label=label, linewidth=2, markersize=8)
    
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    plt.title('OFDM Performance: Modulation Comparison', fontsize=14, fontweight='bold')
    plt.grid(True, which='both', alpha=0.3)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig('modulation_comparison.png', dpi=300)
    print("\n✓ Comparison plot saved as 'modulation_comparison.png'")
    plt.show()


def example_3_single_point_analysis():
    """
    Example 3: Detailed analysis at single SNR point
    """
    print("\n" + "="*70)
    print("Example 3: Detailed Analysis at SNR = 10 dB")
    print("="*70)
    
    simulator = OFDMSimulator(num_subcarriers=64, cp_length=16, modulation='qam16')
    
    snr_target = 10
    num_trials = 20
    ber_list = []
    
    print(f"\nRunning {num_trials} independent trials at SNR = {snr_target} dB:\n")
    
    for trial in range(num_trials):
        result = simulator.simulate(num_symbols=500, snr_db=snr_target)
        ber_list.append(result['ber'])
        print(f"Trial {trial+1:2d}: BER = {result['ber']:.6e}, Errors = {result['num_errors']:4d}/{result['num_bits']:6d}")
    
    ber_array = np.array(ber_list)
    print("\n" + "-"*70)
    print(f"Mean BER:        {np.mean(ber_array):.6e}")
    print(f"Std Dev:         {np.std(ber_array):.6e}")
    print(f"Min BER:         {np.min(ber_array):.6e}")
    print(f"Max BER:         {np.max(ber_array):.6e}")
    print(f"Theoretical:     {theoretical_ber_qam(np.array([snr_target]), m=16)[0]:.6e}")
    print("-"*70)


def example_4_cp_length_effect():
    """
    Example 4: Impact of cyclic prefix length
    """
    print("\n" + "="*70)
    print("Example 4: Effect of Cyclic Prefix Length")
    print("="*70)
    
    snr_range = np.array([0, 5, 10, 15])
    cp_lengths = [8, 16, 32]
    
    plt.figure(figsize=(10, 6))
    
    for cp_len in cp_lengths:
        print(f"\nTesting CP length = {cp_len}...")
        simulator = OFDMSimulator(num_subcarriers=64, cp_length=cp_len, modulation='qam16')
        _, ber = simulator.run_ber_simulation(snr_range, num_symbols=150, num_trials=8)
        plt.semilogy(snr_range, ber, 'o-', label=f'CP={cp_len}', linewidth=2, markersize=8)
    
    # Add theoretical curve
    ber_theo = theoretical_ber_qam(snr_range, m=16)
    plt.semilogy(snr_range, ber_theo, 'k^--', label='Theoretical', linewidth=2, markersize=8)
    
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    plt.title('OFDM Performance: Cyclic Prefix Length Effect', fontsize=14, fontweight='bold')
    plt.grid(True, which='both', alpha=0.3)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig('cp_length_effect.png', dpi=300)
    print("\n✓ CP length comparison plot saved as 'cp_length_effect.png'")
    plt.show()


def example_5_high_resolution_ber():
    """
    Example 5: High-resolution BER curve for publication-quality plot
    """
    print("\n" + "="*70)
    print("Example 5: High-Resolution BER Curve")
    print("="*70)
    
    print("\nGenerating high-resolution curve (this may take a minute)...")
    
    simulator = OFDMSimulator(num_subcarriers=64, cp_length=16, modulation='qam16')
    
    # Fine SNR grid
    snr_range = np.linspace(0, 15, 16)
    
    # Run with more trials for smoothness
    snr_out, ber_sim = simulator.run_ber_simulation(
        snr_range, 
        num_symbols=500, 
        num_trials=30
    )
    
    ber_theo = theoretical_ber_qam(snr_out, m=16)
    
    # High-quality plot
    plt.figure(figsize=(12, 7))
    plt.semilogy(snr_out, ber_sim, 'bo-', label='Simulated', 
                linewidth=2.5, markersize=10, markerfacecolor='lightblue')
    plt.semilogy(snr_out, ber_theo, 'r^--', label='Theoretical (16-QAM)', 
                linewidth=2.5, markersize=10, markerfacecolor='lightcoral')
    
    plt.xlabel('Signal-to-Noise Ratio (dB)', fontsize=13, fontweight='bold')
    plt.ylabel('Bit Error Rate', fontsize=13, fontweight='bold')
    plt.title('OFDM System Performance in AWGN Channel\n64 Subcarriers, 16-QAM, CP=16', 
             fontsize=15, fontweight='bold')
    
    plt.grid(True, which='major', alpha=0.5, linestyle='-')
    plt.grid(True, which='minor', alpha=0.2, linestyle=':')
    plt.legend(fontsize=12, loc='best')
    
    # Add text annotation
    plt.text(0.02, 0.98, 'Configuration:\n• Subcarriers: 64\n• Modulation: 16-QAM\n• CP Length: 16\n• Channel: AWGN',
            transform=plt.gca().transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('ber_curve_publication.png', dpi=300, bbox_inches='tight')
    print("\n✓ Publication-quality plot saved as 'ber_curve_publication.png'")
    plt.show()


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#  OFDM Simulator - Example Usage Demonstrations" + " "*22 + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    # Run examples
    try:
        example_1_basic_simulation()
        example_3_single_point_analysis()
        # Uncomment to run additional examples (these take longer)
        # example_2_different_modulations()
        # example_4_cp_length_effect()
        # example_5_high_resolution_ber()
        
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "#"*70)
    print("Examples completed!")
    print("#"*70)
