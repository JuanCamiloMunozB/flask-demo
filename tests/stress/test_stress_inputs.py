import time
import random
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import os
import json
import threading
import concurrent.futures
import psutil
import gc

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.betting_adviser import BettingAdviser

class ExpertSystemStressTester:
    """Stress tester for the expert systems."""
    
    def __init__(self):
        self.basketball_adviser = BettingAdviser("basketball")
        self.soccer_adviser = BettingAdviser("soccer")
        self.results = {
            "basketball": {"response_times": [], "success_rate": 0, "errors": []},
            "soccer": {"response_times": [], "success_rate": 0, "errors": []}
        }
        
        # Create results directories
        self.results_dir = os.path.join(os.path.dirname(__file__), 'results')
        self.volume_dir = os.path.join(self.results_dir, 'volume_tests')
        self.concurrency_dir = os.path.join(self.results_dir, 'concurrency_tests')
        self.memory_dir = os.path.join(self.results_dir, 'memory_tests')
        self.performance_dir = os.path.join(self.results_dir, 'performance_report')
        
        for directory in [self.results_dir, self.volume_dir, self.concurrency_dir, self.memory_dir, self.performance_dir]:
            os.makedirs(directory, exist_ok=True)
        
    def generate_random_basketball_facts(self):
        """Generate random facts for basketball with correct field names"""
        team_form = random.choice(['bueno', 'regular', 'malo'])
        player_injuries = random.choice(['ninguna', 'menor', 'mayor'])
        home_advantage = random.choice(['sí', 'no'])
        betting_odds = random.choice(['bajas', 'medias', 'altas'])
        rest_days = str(random.randint(0, 7))
        opponent_strength = random.choice(['fuerte', 'promedio', 'débil'])
        recent_head_to_head = random.choice(['victoria', 'empate', 'derrota'])
        match_importance = random.choice(['alta', 'media', 'baja'])
        
        facts = [
            {"team_form": team_form},
            {"player_injuries": player_injuries},
            {"home_advantage": home_advantage},
            {"betting_odds": betting_odds},
            {"rest_days": rest_days},
            {"opponent_strength": opponent_strength},
            {"recent_head_to_head": recent_head_to_head},
            {"match_importance": match_importance}
        ]
        return facts
        
    def generate_random_soccer_facts(self):
        """Generate random facts for soccer with correct field names"""
        home_advantage = random.choice(['sí', 'no'])
        injuries = random.choice(['sí', 'no'])
        performance = random.choice(['bajo', 'medio', 'alto'])
        weather = random.choice(['sí', 'no'])
        rivalry = random.choice(['sí', 'no'])
        league_position = random.choice(['alta', 'media', 'baja'])
        recent_streak = random.choice(['ganadora', 'neutral', 'perdedora'])
        match_importance = random.choice(['alta', 'media', 'baja'])
        physical_condition = random.choice(['descansado', 'normal', 'fatigado'])
        head_to_head = random.choice(['ventaja local', 'equilibrado', 'ventaja visitante'])
        
        facts = [
            {"home_advantage": home_advantage},
            {"injuries": injuries},
            {"performance": performance},
            {"weather": weather},
            {"rivalry": rivalry},
            {"league_position": league_position},
            {"recent_streak": recent_streak},
            {"match_importance": match_importance},
            {"physical_condition": physical_condition},
            {"head_to_head": head_to_head}
        ]
        return facts
   
    def test_single_advice(self, sport, facts):
        """Test a single advice request"""
        try:
            start_time = time.time()
            if sport == "basketball":
                response = self.basketball_adviser.get_betting_advice(facts)
            else:
                response = self.soccer_adviser.get_betting_advice(facts)
            end_time = time.time()
            
            response_time = end_time - start_time
            success = "message" in response
            
            return {
                "response_time": response_time,
                "success": success,
                "response": response
            }
        except Exception as e:
            return {
                "response_time": 0,
                "success": False,
                "error": str(e)
            }
    
    def run_volume_test(self, sport, num_tests=100):
        """Run volume test with random facts"""
        print(f"Running volume test for {sport} with {num_tests} requests...")
        response_times = []
        successes = 0
        errors = []
        test_results = []
        
        for i in tqdm(range(num_tests)):
            if sport == "basketball":
                facts = self.generate_random_basketball_facts()
            else:
                facts = self.generate_random_soccer_facts()
                
            result = self.test_single_advice(sport, facts)
            
            # Store detailed results for each test
            test_result = {
                "test_number": i+1,
                "facts": facts,
                "response_time": result["response_time"],
                "success": result["success"],
                "response": result.get("response", {}),
                "error": result.get("error", None)
            }
            test_results.append(test_result)
            
            if result["success"]:
                response_times.append(result["response_time"])
                successes += 1
            else:
                errors.append(result.get("error", "Unknown error"))
        
        success_rate = (successes / num_tests) * 100
        
        self.results[sport]["response_times"].extend(response_times)
        self.results[sport]["success_rate"] = success_rate
        self.results[sport]["errors"].extend(errors)
        
        # Create summary
        summary = {
            "sport": sport,
            "num_tests": num_tests,
            "success_rate": success_rate,
            "avg_response_time": sum(response_times)/len(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "error_count": len(errors),
            "sample_errors": errors[:5],
            "detailed_results": test_results
        }
        
        # Save to volume_tests directory
        volume_file = os.path.join(self.volume_dir, f"{sport}_volume_test_results.json")
        with open(volume_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"{sport.capitalize()} volume test completed:")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  Average response time: {sum(response_times)/len(response_times) if response_times else 0:.5f} seconds")
        print(f"  Number of errors: {len(errors)}")
        print(f"  Results saved to {volume_file}")
        
        if errors:
            print("  Sample errors:")
            for error in errors[:5]:
                print(f"    - {error}")
        
        return summary
    
    def run_concurrent_test(self, sport, concurrent_users=[2, 5, 10], requests_per_user=20):
        """
        Test concurrent users accessing the system simultaneously
        
        Args:
            sport (str): "basketball" or "soccer"
            concurrent_users (list): Different numbers of concurrent users to test
            requests_per_user (int): Number of requests each user makes
        """
        print(f"Running concurrency test for {sport}...")
        
        all_concurrent_results = []
        
        for num_users in concurrent_users:
            print(f"  Testing with {num_users} concurrent users, {requests_per_user} requests each...")
            
            def user_session(user_id):
                """Simulate a user session with multiple requests"""
                user_results = {
                    "user_id": user_id,
                    "results": [],
                    "total_time": 0,
                    "success_count": 0,
                    "error_count": 0
                }
                
                session_start = time.time()
                
                for request_num in range(requests_per_user):
                    if sport == "basketball":
                        facts = self.generate_random_basketball_facts()
                    else:
                        facts = self.generate_random_soccer_facts()
                    
                    result = self.test_single_advice(sport, facts)
                    user_results["results"].append({
                        "request_num": request_num + 1,
                        "response_time": result["response_time"],
                        "success": result["success"],
                        "error": result.get("error", None)
                    })
                    
                    if result["success"]:
                        user_results["success_count"] += 1
                    else:
                        user_results["error_count"] += 1
                
                session_end = time.time()
                user_results["total_time"] = session_end - session_start
                
                return user_results
            
            # Execute concurrent user sessions
            concurrent_start = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
                future_to_user = {executor.submit(user_session, user_id): user_id 
                                for user_id in range(num_users)}
                
                user_sessions = []
                for future in concurrent.futures.as_completed(future_to_user):
                    user_id = future_to_user[future]
                    try:
                        user_result = future.result()
                        user_sessions.append(user_result)
                    except Exception as exc:
                        print(f"User {user_id} generated an exception: {exc}")
                        user_sessions.append({
                            "user_id": user_id,
                            "error": str(exc),
                            "total_time": 0,
                            "success_count": 0,
                            "error_count": requests_per_user
                        })
            
            concurrent_end = time.time()
            total_concurrent_time = concurrent_end - concurrent_start
            
            # Analyze results for this concurrency level
            all_response_times = []
            total_requests = num_users * requests_per_user
            total_successes = 0
            total_errors = 0
            
            for session in user_sessions:
                total_successes += session.get("success_count", 0)
                total_errors += session.get("error_count", 0)
                if "results" in session:
                    for result in session["results"]:
                        if result["success"]:
                            all_response_times.append(result["response_time"])
            
            # Calculate metrics
            success_rate = (total_successes / total_requests) * 100
            avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
            throughput = total_requests / total_concurrent_time  # requests per second
            
            concurrent_result = {
                "concurrent_users": num_users,
                "requests_per_user": requests_per_user,
                "total_requests": total_requests,
                "total_time": total_concurrent_time,
                "success_rate": success_rate,
                "total_successes": total_successes,
                "total_errors": total_errors,
                "avg_response_time": avg_response_time,
                "min_response_time": min(all_response_times) if all_response_times else 0,
                "max_response_time": max(all_response_times) if all_response_times else 0,
                "throughput": throughput,
                "user_sessions": user_sessions
            }
            
            all_concurrent_results.append(concurrent_result)
            
            print(f"    {num_users} users completed in {total_concurrent_time:.2f} seconds")
            print(f"    Success rate: {success_rate:.2f}%")
            print(f"    Average response time: {avg_response_time:.5f} seconds")
            print(f"    Throughput: {throughput:.2f} requests/second")
        
        # Create visualization
        plt.figure(figsize=(15, 10))
        
        # Extract data for plots
        users = [r["concurrent_users"] for r in all_concurrent_results]
        success_rates = [r["success_rate"] for r in all_concurrent_results]
        avg_times = [r["avg_response_time"] for r in all_concurrent_results]
        throughputs = [r["throughput"] for r in all_concurrent_results]
        
        # Success rate vs concurrent users
        plt.subplot(2, 2, 1)
        plt.plot(users, success_rates, 'o-', linewidth=2, markersize=8, color='green')
        plt.xlabel('Usuarios Concurrentes')
        plt.ylabel('Tasa de Éxito (%)')
        plt.title(f'Concurrencia: Tasa de Éxito vs Usuarios\n{sport.capitalize()}')
        plt.grid(True)
        for i, v in enumerate(success_rates):
            plt.text(users[i], v + 1, f"{v:.1f}%", ha="center")
        
        # Response time vs concurrent users
        plt.subplot(2, 2, 2)
        plt.plot(users, avg_times, 'o-', linewidth=2, markersize=8, color='blue')
        plt.xlabel('Usuarios Concurrentes')
        plt.ylabel('Tiempo Promedio de Respuesta (segundos)')
        plt.title(f'Concurrencia: Tiempo de Respuesta vs Usuarios\n{sport.capitalize()}')
        plt.grid(True)
        
        # Throughput vs concurrent users
        plt.subplot(2, 2, 3)
        plt.plot(users, throughputs, 'o-', linewidth=2, markersize=8, color='red')
        plt.xlabel('Usuarios Concurrentes')
        plt.ylabel('Throughput (solicitudes/segundo)')
        plt.title(f'Concurrencia: Throughput vs Usuarios\n{sport.capitalize()}')
        plt.grid(True)
        
        # Response time distribution for highest concurrency
        plt.subplot(2, 2, 4)
        if all_concurrent_results:
            highest_concurrency = all_concurrent_results[-1]
            all_times = []
            for session in highest_concurrency["user_sessions"]:
                if "results" in session:
                    for result in session["results"]:
                        if result["success"]:
                            all_times.append(result["response_time"])
            
            if all_times:
                plt.hist(all_times, bins=20, alpha=0.7, color='purple')
                plt.xlabel('Tiempo de Respuesta (segundos)')
                plt.ylabel('Frecuencia')
                plt.title(f'Distribución de Tiempos - {highest_concurrency["concurrent_users"]} usuarios')
        
        plt.tight_layout()
        
        # Save to concurrency_tests directory
        concurrency_plot = os.path.join(self.concurrency_dir, f"{sport}_concurrency_test.png")
        plt.savefig(concurrency_plot)
        print(f"Concurrency graph saved to {concurrency_plot}")
        
        # Save results to JSON
        concurrency_data = {
            "sport": sport,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_parameters": {
                "concurrent_users_tested": concurrent_users,
                "requests_per_user": requests_per_user
            },
            "results": all_concurrent_results
        }
        
        concurrency_file = os.path.join(self.concurrency_dir, f"{sport}_concurrency_results.json")
        with open(concurrency_file, "w", encoding="utf-8") as f:
            json.dump(concurrency_data, f, indent=2, ensure_ascii=False)
        
        print(f"Concurrency data saved to {concurrency_file}")
        
        return all_concurrent_results
    
    def run_memory_usage_test(self, sport, num_tests=200, sample_interval=10):
        """
        Monitor memory usage during extended testing
        
        Args:
            sport (str): "basketball" or "soccer"
            num_tests (int): Number of tests to run
            sample_interval (int): Take memory sample every N tests
        """
        print(f"Running memory usage test for {sport} with {num_tests} requests...")
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_samples = []
        response_times = []
        successes = 0
        errors = 0
        
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        for i in tqdm(range(num_tests)):
            # Generate random facts
            if sport == "basketball":
                facts = self.generate_random_basketball_facts()
            else:
                facts = self.generate_random_soccer_facts()
            
            # Test advice request
            result = self.test_single_advice(sport, facts)
            
            if result["success"]:
                response_times.append(result["response_time"])
                successes += 1
            else:
                errors += 1
            
            # Sample memory usage at intervals
            if i % sample_interval == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append({
                    "test_number": i,
                    "memory_usage_mb": current_memory,
                    "memory_delta_mb": current_memory - initial_memory
                })
        
        # Force garbage collection and get final memory
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Calculate statistics
        success_rate = (successes / num_tests) * 100
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        memory_growth = final_memory - initial_memory
        max_memory = max([sample["memory_usage_mb"] for sample in memory_samples])
        
        # Create memory usage visualization
        plt.figure(figsize=(12, 8))
        
        # Memory usage over time
        plt.subplot(2, 2, 1)
        test_numbers = [sample["test_number"] for sample in memory_samples]
        memory_values = [sample["memory_usage_mb"] for sample in memory_samples]
        
        plt.plot(test_numbers, memory_values, 'o-', linewidth=2, markersize=4)
        plt.xlabel('Número de Prueba')
        plt.ylabel('Uso de Memoria (MB)')
        plt.title(f'Uso de Memoria a lo Largo del Tiempo\n{sport.capitalize()}')
        plt.grid(True)
        
        # Memory delta over time
        plt.subplot(2, 2, 2)
        memory_deltas = [sample["memory_delta_mb"] for sample in memory_samples]
        plt.plot(test_numbers, memory_deltas, 'o-', linewidth=2, markersize=4, color='red')
        plt.xlabel('Número de Prueba')
        plt.ylabel('Cambio en Memoria (MB)')
        plt.title(f'Crecimiento de Memoria\n{sport.capitalize()}')
        plt.grid(True)
        plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Memory usage histogram
        plt.subplot(2, 2, 3)
        plt.hist(memory_values, bins=20, alpha=0.7, color='green')
        plt.xlabel('Uso de Memoria (MB)')
        plt.ylabel('Frecuencia')
        plt.title('Distribución del Uso de Memoria')
        
        # Summary statistics
        plt.subplot(2, 2, 4)
        stats_text = f"""Estadísticas de Memoria:
        
Memoria Inicial: {initial_memory:.2f} MB
Memoria Final: {final_memory:.2f} MB
Memoria Máxima: {max_memory:.2f} MB
Crecimiento: {memory_growth:.2f} MB

Estadísticas de Rendimiento:
Tasa de Éxito: {success_rate:.1f}%
Tiempo Promedio: {avg_response_time:.5f}s
Total de Pruebas: {num_tests}
"""
        plt.text(0.1, 0.5, stats_text, fontsize=10, verticalalignment='center', 
                transform=plt.gca().transAxes, family='monospace')
        plt.axis('off')
        
        plt.tight_layout()
        
        # Save to memory_tests directory
        memory_plot = os.path.join(self.memory_dir, f"{sport}_memory_usage_test.png")
        plt.savefig(memory_plot)
        print(f"Memory usage graph saved to {memory_plot}")
        
        # Prepare detailed results
        memory_results = {
            "sport": sport,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_parameters": {
                "num_tests": num_tests,
                "sample_interval": sample_interval
            },
            "memory_statistics": {
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "max_memory_mb": max_memory,
                "memory_growth_mb": memory_growth,
                "avg_memory_mb": sum(memory_values) / len(memory_values)
            },
            "performance_statistics": {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "total_successes": successes,
                "total_errors": errors
            },
            "memory_samples": memory_samples
        }
        
        # Save to memory_tests directory
        memory_file = os.path.join(self.memory_dir, f"{sport}_memory_usage_results.json")
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memory_results, f, indent=2, ensure_ascii=False)
        
        print(f"{sport.capitalize()} memory test completed:")
        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Memory growth: {memory_growth:.2f} MB")
        print(f"  Max memory: {max_memory:.2f} MB")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  Results saved to {memory_file}")
        
        return memory_results
    
    def generate_performance_report(self):
        """Generate a performance report with charts"""
        report_data = {
            "basketball": {
                "response_times": self.results["basketball"]["response_times"],
                "success_rate": self.results["basketball"]["success_rate"],
                "errors": len(self.results["basketball"]["errors"])
            },
            "soccer": {
                "response_times": self.results["soccer"]["response_times"],
                "success_rate": self.results["soccer"]["success_rate"],
                "errors": len(self.results["soccer"]["errors"])
            }
        }
        
        # Create performance charts
        plt.figure(figsize=(12, 8))
        
        # Response time histogram
        plt.subplot(2, 2, 1)
        plt.hist(report_data["basketball"]["response_times"], alpha=0.7, label="Basketball", bins=20)
        plt.hist(report_data["soccer"]["response_times"], alpha=0.7, label="Soccer", bins=20)
        plt.xlabel("Response Time (seconds)")
        plt.ylabel("Frecuencia")
        plt.title("Response Time Distribution")
        plt.legend()
        
        # Success rate comparison
        plt.subplot(2, 2, 2)
        sports = ["Basketball", "Soccer"]
        success_rates = [report_data["basketball"]["success_rate"], report_data["soccer"]["success_rate"]]
        plt.bar(sports, success_rates)
        plt.ylabel("Success Rate (%)")
        plt.title("Success Rate Comparison")
        for i, v in enumerate(success_rates):
            plt.text(i, v + 1, f"{v:.1f}%", ha="center")
        
        # Error count comparison
        plt.subplot(2, 2, 3)
        error_counts = [report_data["basketball"]["errors"], report_data["soccer"]["errors"]]
        plt.bar(sports, error_counts)
        plt.ylabel("Number of Errors")
        plt.title("Error Count Comparison")
        for i, v in enumerate(error_counts):
            plt.text(i, v + 1, str(v), ha="center")
        
        # Response time statistics
        plt.subplot(2, 2, 4)
        basket_times = report_data["basketball"]["response_times"]
        soccer_times = report_data["soccer"]["response_times"]
        
        stats = {
            "Basketball Avg": sum(basket_times) / len(basket_times) if basket_times else 0,
            "Soccer Avg": sum(soccer_times) / len(soccer_times) if soccer_times else 0,
            "Basketball Max": max(basket_times) if basket_times else 0,
            "Soccer Max": max(soccer_times) if soccer_times else 0,
            "Basketball Min": min(basket_times) if basket_times else 0,
            "Soccer Min": min(soccer_times) if soccer_times else 0,
        }
        
        x = list(stats.keys())
        y = list(stats.values())
        plt.bar(x, y)
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Time (seconds)")
        plt.title("Response Time Statistics")
        for i, v in enumerate(y):
            plt.text(i, v + 0.001, f"{v:.4f}", ha="center")
        
        plt.tight_layout()
        
        # Save to performance_report directory
        performance_plot = os.path.join(self.performance_dir, "expert_system_performance_report.png")
        plt.savefig(performance_plot)
        print(f"Performance report generated: {performance_plot}")
        
        # Create stats dataframe for detailed reporting
        basketball_times = report_data["basketball"]["response_times"]
        soccer_times = report_data["soccer"]["response_times"]
        
        time_stats = {
            "Metric": ["Count", "Min", "Max", "Mean", "Median", "95th Percentile"],
            "Basketball": [
                len(basketball_times),
                min(basketball_times) if basketball_times else 0,
                max(basketball_times) if basketball_times else 0,
                sum(basketball_times) / len(basketball_times) if basketball_times else 0,
                sorted(basketball_times)[len(basketball_times)//2] if basketball_times else 0,
                sorted(basketball_times)[int(len(basketball_times)*0.95)] if basketball_times else 0
            ],
            "Soccer": [
                len(soccer_times),
                min(soccer_times) if soccer_times else 0,
                max(soccer_times) if soccer_times else 0,
                sum(soccer_times) / len(soccer_times) if soccer_times else 0,
                sorted(soccer_times)[len(soccer_times)//2] if soccer_times else 0,
                sorted(soccer_times)[int(len(soccer_times)*0.95)] if soccer_times else 0
            ]
        }
        
        stats_df = pd.DataFrame(time_stats)
        print("\nDetailed Response Time Statistics (seconds):")
        print(stats_df)
        
        # Save to performance_report directory
        stats_file = os.path.join(self.performance_dir, "expert_system_performance_stats.csv")
        stats_df.to_csv(stats_file, index=False)
        print(f"Detailed statistics saved to {stats_file}")
        
        # Additional step: Save performance metrics to JSON
        performance_metrics = {
            "basketball": {
                "response_times_stats": {
                    "count": len(basketball_times),
                    "min": min(basketball_times) if basketball_times else 0,
                    "max": max(basketball_times) if basketball_times else 0,
                    "mean": sum(basketball_times) / len(basketball_times) if basketball_times else 0,
                    "median": sorted(basketball_times)[len(basketball_times)//2] if basketball_times else 0,
                    "percentile_95": sorted(basketball_times)[int(len(basketball_times)*0.95)] if basketball_times else 0
                },
                "success_rate": self.results["basketball"]["success_rate"],
                "error_count": len(self.results["basketball"]["errors"])
            },
            "soccer": {
                "response_times_stats": {
                    "count": len(soccer_times),
                    "min": min(soccer_times) if soccer_times else 0,
                    "max": max(soccer_times) if soccer_times else 0,
                    "mean": sum(soccer_times) / len(soccer_times) if soccer_times else 0,
                    "median": sorted(soccer_times)[len(soccer_times)//2] if soccer_times else 0,
                    "percentile_95": sorted(soccer_times)[int(len(soccer_times)*0.95)] if soccer_times else 0
                },
                "success_rate": self.results["soccer"]["success_rate"],
                "error_count": len(self.results["soccer"]["errors"])
            }
        }
        
        # Save to performance_report directory
        metrics_file = os.path.join(self.performance_dir, "performance_metrics.json")
        with open(metrics_file, "w") as f:
            json.dump(performance_metrics, f, indent=2)
            
        print(f"Performance metrics saved to {metrics_file}")
    
    def run_all_tests(self):
        """Run all stress tests"""
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "volume_tests": {},
            "concurrency_tests": {},
            "memory_tests": {}
        }
        
        # Volume tests
        print("\n=== RUNNING VOLUME TESTS ===")
        basketball_volume = self.run_volume_test("basketball", 100)
        soccer_volume = self.run_volume_test("soccer", 100)
        all_results["volume_tests"]["basketball"] = basketball_volume
        all_results["volume_tests"]["soccer"] = soccer_volume
        
        # Concurrency tests
        print("\n=== RUNNING CONCURRENCY TESTS ===")
        basketball_concurrency = self.run_concurrent_test("basketball", [2, 5, 10], 20)
        soccer_concurrency = self.run_concurrent_test("soccer", [2, 5, 10], 20)
        all_results["concurrency_tests"]["basketball"] = basketball_concurrency
        all_results["concurrency_tests"]["soccer"] = soccer_concurrency
        
        # Memory usage tests
        print("\n=== RUNNING MEMORY USAGE TESTS ===")
        basketball_memory = self.run_memory_usage_test("basketball", 200, 10)
        soccer_memory = self.run_memory_usage_test("soccer", 200, 10)
        all_results["memory_tests"]["basketball"] = basketball_memory
        all_results["memory_tests"]["soccer"] = soccer_memory
        
        # Generate report
        print("\n=== GENERATING PERFORMANCE REPORTS ===")
        self.generate_performance_report()
        
        # Save comprehensive results to main results directory
        all_results_file = os.path.join(self.results_dir, "all_test_results.json")
        with open(all_results_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"All test results saved to {all_results_file}")

if __name__ == "__main__":
    tester = ExpertSystemStressTester()
    tester.run_all_tests()