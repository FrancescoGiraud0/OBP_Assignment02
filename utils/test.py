import unittest
from system import System  # Assuming the class is saved in system.py

class TestSystemModel(unittest.TestCase):
    # Tolerance for comparing analytical vs simulation results
    TOLERANCE = 0.05  # 5% difference allowed
    
    # Define multiple test cases as (n, k, num_repairmen, failure_rate, repair_rate)
    TEST_CASES = [
        # Basic case
        (5, 3, 1, 2.0, 3.0),
        (5, 3, 2, 2.0, 3.0),
        (5, 3, 3, 2.0, 3.0),
        (5, 3, 4, 2.0, 3.0),
        (5, 3, 5, 2.0, 3.0),
        # Large system
        (10, 7, 3, 1.5, 2.5),
        # High reliability components
        (5, 3, 2, 1.0, 5.0),
        # Low reliability components
        (5, 3, 2, 5.0, 1.0),
    ]

    def test_warm_standby_consistency(self):
        """Test that analytical and simulation results are consistent for warm standby systems."""
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
                analytical_result = round(system.active_time_fraction(), 4)
                
                # Get simulation result (with large number of cycles for accuracy)
                simulation_result = round(system.sim(cycles=5000000, warmup_cycles=10000), 4)
                
                absolute_difference = abs(analytical_result - simulation_result)

                # Calculate relative difference
                if analytical_result > 0:
                    relative_difference = absolute_difference / analytical_result
                else:
                    relative_difference = absolute_difference
                
                print(f"\nWarm Standby Test Case {case_idx+1}: n={n}, k={k}, s={num_repairmen}, λ={failure_rate}, μ={repair_rate}")
                print(f"Analytical active time: {analytical_result:.4f}")
                print(f"Simulation active time: {simulation_result:.4f}")
                print(f"Absolute difference: {absolute_difference:.4f}")
                print(f"Relative difference: {relative_difference*100:.2f}%")
                
                # Check that relative difference is within tolerance
                self.assertLess(
                    relative_difference, 
                    self.TOLERANCE,
                    f"Warm standby case {case_idx+1}: Relative difference {relative_difference*100:.2f}% exceeds tolerance of {self.TOLERANCE*100}%"
                )

    def test_cold_standby_consistency(self):
        """Test that analytical and simulation results are consistent for cold standby systems."""
        for case_idx, (n, k, num_repairmen, failure_rate, repair_rate) in enumerate(self.TEST_CASES):
            with self.subTest(case=f"Case {case_idx+1}: n={n}, k={k}, s={num_repairmen}, λ={failure_rate}, μ={repair_rate}"):
                # Create system instance
                system = System(
                    n=n,
                    k=k,
                    num_repairmen=num_repairmen,
                    failure_rate=failure_rate,
                    repair_rate=repair_rate,
                    cold_standby=True
                )
                
                # Get analytical result
                analytical_result = round(system.active_time_fraction(), 4)
                
                # Get simulation result (with large number of cycles for accuracy)
                simulation_result = round(system.sim(cycles=5000000, warmup_cycles=10000), 4)
                
                absolute_difference = abs(analytical_result - simulation_result)

                # Calculate relative difference
                if analytical_result > 0:
                    relative_difference = absolute_difference / analytical_result
                else:
                    relative_difference = absolute_difference
                
                print(f"\nCold Standby Test Case {case_idx+1}: n={n}, k={k}, s={num_repairmen}, λ={failure_rate}, μ={repair_rate}")
                print(f"Analytical active time: {analytical_result:.4f}")
                print(f"Simulation active time: {simulation_result:.4f}")
                print(f"Absolute difference: {absolute_difference:.4f}")
                print(f"Relative difference: {relative_difference*100:.2f}%")
                
                # Check that relative difference is within tolerance
                self.assertLess(
                    relative_difference, 
                    self.TOLERANCE,
                    f"Cold standby case {case_idx+1}: Relative difference {relative_difference*100:.2f}% exceeds tolerance of {self.TOLERANCE*100}%"
                )

    def test_stationary_distribution_sanity(self):
        """Test that stationary distribution sums to 1 for all test cases in both warm and cold standby."""
        for standby_mode in [False, True]:  # False = warm standby, True = cold standby
            standby_type = "Cold" if standby_mode else "Warm"
            for case_idx, (n, k, num_repairmen, failure_rate, repair_rate) in enumerate(self.TEST_CASES):
                with self.subTest(case=f"{standby_type} Standby Case {case_idx+1}"):
                    system = System(
                        n=n,
                        k=k,
                        num_repairmen=num_repairmen,
                        failure_rate=failure_rate,
                        repair_rate=repair_rate,
                        cold_standby=standby_mode
                    )
                    distribution = system.stationary_distribution()
                    total_prob = sum(distribution)
                    
                    self.assertAlmostEqual(
                        total_prob, 
                        1.0,
                        places=6,
                        msg=f"{standby_type} Standby Case {case_idx+1}: Stationary distribution sums to {total_prob} instead of 1"
                    )

    def test_cold_vs_warm_reliability(self):
        """Test that cold standby systems generally have higher reliability than warm standby systems."""
        for case_idx, (n, k, num_repairmen, failure_rate, repair_rate) in enumerate(self.TEST_CASES):
            if n > k:  # Only compare if there are standby components
                with self.subTest(case=f"Case {case_idx+1}: n={n}, k={k}, s={num_repairmen}, λ={failure_rate}, μ={repair_rate}"):
                    # Create warm standby system
                    warm_system = System(
                        n=n,
                        k=k,
                        num_repairmen=num_repairmen,
                        failure_rate=failure_rate,
                        repair_rate=repair_rate,
                        cold_standby=False
                    )
                    
                    # Create cold standby system
                    cold_system = System(
                        n=n,
                        k=k,
                        num_repairmen=num_repairmen,
                        failure_rate=failure_rate,
                        repair_rate=repair_rate,
                        cold_standby=True
                    )
                    
                    # Get reliability metrics (active time fraction)
                    warm_reliability = warm_system.active_time_fraction()
                    cold_reliability = cold_system.active_time_fraction()
                    
                    print(f"\nCase {case_idx+1}: n={n}, k={k}, s={num_repairmen}, λ={failure_rate}, μ={repair_rate}")
                    print(f"Warm standby reliability: {warm_reliability:.6f}")
                    print(f"Cold standby reliability: {cold_reliability:.6f}")
                    
                    # Cold standby should generally be more reliable than warm standby
                    # because standby components don't fail
                    self.assertGreaterEqual(
                        cold_reliability,
                        warm_reliability,
                        f"Case {case_idx+1}: Cold standby reliability ({cold_reliability:.6f}) is not greater than or equal to warm standby reliability ({warm_reliability:.6f})"
                    )

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)