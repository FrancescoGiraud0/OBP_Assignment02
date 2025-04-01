import unittest
from system import System  # Assuming the class is saved in system_model.py

class TestSystemModel(unittest.TestCase):
    # Tolerance for comparing analytical vs simulation results
    TOLERANCE = 0.02  # 2% difference allowed
    
    # Define multiple test cases as (n, k, num_repairmen, failure_rate, repair_rate)
    TEST_CASES = [
        # Basic case
        (5, 3, 2, 2.0, 3.0),
        # More repairmen than needed
        (5, 3, 4, 2.0, 3.0),
        (5, 3, 5, 2.0, 3.0),
        # Few repairmen, high load
        (5, 3, 1, 2.0, 3.0),
        # Large system
        (10, 7, 3, 1.5, 2.5),
        # High reliability components
        (5, 3, 2, 1.0, 5.0),
        # Low reliability components
        (5, 3, 2, 5.0, 1.0),
    ]

    def test_warm_standby_consistency(self):
        """Test that analytical and simulation results are consistent for various parameter sets."""
        for case_idx, (n, k, num_repairmen, failure_rate, repair_rate) in enumerate(self.TEST_CASES):
            with self.subTest(case=f"Case {case_idx+1}: n={n}, k={k}, s={num_repairmen}, λ={failure_rate}, μ={repair_rate}"):
                # Create system instance
                system = System(
                    n=n,
                    k=k,
                    num_repairmen=num_repairmen,
                    failure_rate=failure_rate,
                    repair_rate=repair_rate,
                    cold_standby=False
                )
                
                # Get analytical result
                analytical_result = system.active_time_fraction()
                
                # Get simulation result (with large number of cycles for accuracy)
                simulation_result = system.sim(cycles=10000000, warmup_cycles=10000)
                
                # Calculate relative difference
                if analytical_result > 0:
                    relative_difference = abs(analytical_result - simulation_result) / analytical_result
                else:
                    relative_difference = abs(analytical_result - simulation_result)
                
                print(f"\nTest Case {case_idx+1}: n={n}, k={k}, s={num_repairmen}, λ={failure_rate}, μ={repair_rate}")
                print(f"Analytical active time: {analytical_result:.6f}")
                print(f"Simulation active time: {simulation_result:.6f}")
                print(f"Relative difference: {relative_difference*100:.2f}%")
                
                # Assert that relative difference is within tolerance
                self.assertLessEqual(
                    relative_difference, 
                    self.TOLERANCE,
                    f"Case {case_idx+1}: Analytical ({analytical_result}) and simulation ({simulation_result}) "
                    f"results differ by {relative_difference*100:.2f}% (> {self.TOLERANCE*100}% tolerance)"
                )

    def test_stationary_distribution_sanity(self):
        """Test that stationary distribution sums to 1 for all test cases."""
        for case_idx, (n, k, num_repairmen, failure_rate, repair_rate) in enumerate(self.TEST_CASES):
            with self.subTest(case=f"Case {case_idx+1}"):
                system = System(
                    n=n,
                    k=k,
                    num_repairmen=num_repairmen,
                    failure_rate=failure_rate,
                    repair_rate=repair_rate,
                    cold_standby=False
                )
                distribution = system.stationary_distribution()
                total_prob = sum(distribution)
                
                self.assertAlmostEqual(
                    total_prob, 
                    1.0,
                    places=6,
                    msg=f"Case {case_idx+1}: Stationary distribution sums to {total_prob} instead of 1"
                )

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)