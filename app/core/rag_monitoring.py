# rag_monitoring.py - Sistema de monitoramento e métricas para RAG
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
from pathlib import Path
import threading
from contextlib import contextmanager

@dataclass
class QueryMetrics:
    """Métricas de uma query individual"""
    query_id: str
    query_text: str
    timestamp: float
    
    # Search metrics
    search_time: float
    num_results_found: int
    avg_relevance_score: float
    collections_searched: List[str]
    
    # Context metrics
    context_optimization_time: float
    context_length: int
    context_tokens: int
    
    # Generation metrics
    generation_time: float
    response_length: int
    response_tokens: int
    model_used: str
    temperature: float
    
    # Quality metrics
    query_complexity: str
    query_intents: List[str]
    response_validation_passed: bool
    user_feedback: Optional[str] = None
    
    @property
    def total_time(self) -> float:
        return self.search_time + self.context_optimization_time + self.generation_time

@dataclass
class SystemMetrics:
    """Métricas do sistema em um período"""
    period_start: float
    period_end: float
    
    # Query statistics
    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_response_time: float
    
    # Search performance
    avg_search_time: float
    avg_results_per_query: float
    avg_relevance_score: float
    
    # Context optimization
    avg_context_optimization_time: float
    avg_context_length: int
    avg_context_tokens: int
    
    # Generation performance
    avg_generation_time: float
    avg_response_length: int
    avg_response_tokens: int
    
    # Quality metrics
    validation_success_rate: float
    query_complexity_distribution: Dict[str, int]
    intent_distribution: Dict[str, int]
    
    # Resource usage
    peak_memory_usage: float
    avg_memory_usage: float
    cache_hit_rate: float

class PerformanceMonitor:
    """Monitor de performance para componentes individuais"""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.metrics = defaultdict(list)
        self.active_operations = {}
        self.lock = threading.Lock()
    
    @contextmanager
    def measure_operation(self, operation_name: str, metadata: Optional[Dict] = None):
        """Context manager para medir operações"""
        operation_id = f"{operation_name}_{time.time()}"
        start_time = time.time()
        
        with self.lock:
            self.active_operations[operation_id] = {
                "start_time": start_time,
                "metadata": metadata or {}
            }
        
        try:
            yield operation_id
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            with self.lock:
                if operation_id in self.active_operations:
                    op_data = self.active_operations.pop(operation_id)
                    self.metrics[operation_name].append({
                        "duration": duration,
                        "timestamp": start_time,
                        "metadata": op_data["metadata"]
                    })
    
    def get_operation_stats(self, operation_name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Obtém estatísticas de uma operação em uma janela de tempo"""
        cutoff_time = time.time() - (window_minutes * 60)
        
        with self.lock:
            recent_metrics = [
                m for m in self.metrics[operation_name] 
                if m["timestamp"] >= cutoff_time
            ]
        
        if not recent_metrics:
            return {
                "count": 0,
                "avg_duration": 0.0,
                "min_duration": 0.0,
                "max_duration": 0.0,
                "p95_duration": 0.0
            }
        
        durations = [m["duration"] for m in recent_metrics]
        
        return {
            "count": len(durations),
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "p95_duration": statistics.quantiles(durations, n=20)[18] if len(durations) > 1 else durations[0],
            "total_time": sum(durations)
        }

class RAGMonitor:
    """Monitor principal do sistema RAG"""
    
    def __init__(self, 
                 max_stored_queries: int = 1000,
                 metrics_window_hours: int = 24,
                 log_file: Optional[str] = None):
        
        self.max_stored_queries = max_stored_queries
        self.metrics_window_hours = metrics_window_hours
        self.log_file = log_file
        
        # Storage for metrics
        self.query_metrics = deque(maxlen=max_stored_queries)
        self.system_metrics_history = []
        
        # Performance monitors for components
        self.search_monitor = PerformanceMonitor("search")
        self.context_monitor = PerformanceMonitor("context")
        self.generation_monitor = PerformanceMonitor("generation")
        
        # Current session tracking
        self.session_start = time.time()
        self.current_query_data = {}
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Cache for computed metrics
        self._metrics_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for monitoring"""
        logger = logging.getLogger("rag_monitor")
        logger.setLevel(logging.INFO)
        
        if self.log_file:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def start_query_tracking(self, query_id: str, query_text: str) -> str:
        """Inicia o tracking de uma nova query"""
        self.current_query_data[query_id] = {
            "query_id": query_id,
            "query_text": query_text,
            "timestamp": time.time(),
            "search_time": 0.0,
            "context_optimization_time": 0.0,
            "generation_time": 0.0,
            "num_results_found": 0,
            "collections_searched": [],
            "avg_relevance_score": 0.0,
            "context_length": 0,
            "context_tokens": 0,
            "response_length": 0,
            "response_tokens": 0,
            "model_used": "",
            "temperature": 0.0,
            "query_complexity": "unknown",
            "query_intents": [],
            "response_validation_passed": True
        }
        
        self.logger.info(f"Started tracking query: {query_id}")
        return query_id
    
    def update_search_metrics(self, query_id: str, 
                            search_time: float,
                            num_results: int,
                            avg_relevance: float,
                            collections: List[str]):
        """Atualiza métricas de busca"""
        if query_id in self.current_query_data:
            self.current_query_data[query_id].update({
                "search_time": search_time,
                "num_results_found": num_results,
                "avg_relevance_score": avg_relevance,
                "collections_searched": collections
            })
    
    def update_context_metrics(self, query_id: str,
                             optimization_time: float,
                             context_length: int,
                             context_tokens: int):
        """Atualiza métricas de contexto"""
        if query_id in self.current_query_data:
            self.current_query_data[query_id].update({
                "context_optimization_time": optimization_time,
                "context_length": context_length,
                "context_tokens": context_tokens
            })
    
    def update_generation_metrics(self, query_id: str,
                                generation_time: float,
                                response_length: int,
                                response_tokens: int,
                                model_used: str,
                                temperature: float):
        """Atualiza métricas de geração"""
        if query_id in self.current_query_data:
            self.current_query_data[query_id].update({
                "generation_time": generation_time,
                "response_length": response_length,
                "response_tokens": response_tokens,
                "model_used": model_used,
                "temperature": temperature
            })
    
    def update_quality_metrics(self, query_id: str,
                             complexity: str,
                             intents: List[str],
                             validation_passed: bool):
        """Atualiza métricas de qualidade"""
        if query_id in self.current_query_data:
            self.current_query_data[query_id].update({
                "query_complexity": complexity,
                "query_intents": intents,
                "response_validation_passed": validation_passed
            })
    
    def finish_query_tracking(self, query_id: str, user_feedback: Optional[str] = None) -> QueryMetrics:
        """Finaliza o tracking de uma query e armazena as métricas"""
        if query_id not in self.current_query_data:
            raise ValueError(f"Query {query_id} not found in tracking")
        
        query_data = self.current_query_data.pop(query_id)
        query_data["user_feedback"] = user_feedback
        
        # Create metrics object
        metrics = QueryMetrics(**query_data)
        
        # Store metrics
        self.query_metrics.append(metrics)
        
        # Log completion
        self.logger.info(
            f"Query {query_id} completed - "
            f"Total time: {metrics.total_time:.3f}s, "
            f"Results: {metrics.num_results_found}, "
            f"Avg relevance: {metrics.avg_relevance_score:.3f}"
        )
        
        return metrics
    
    def get_recent_metrics(self, hours: int = 1) -> List[QueryMetrics]:
        """Obtém métricas das últimas N horas"""
        cutoff_time = time.time() - (hours * 3600)
        return [m for m in self.query_metrics if m.timestamp >= cutoff_time]
    
    def compute_system_metrics(self, hours: int = 1) -> SystemMetrics:
        """Computa métricas do sistema para um período"""
        
        # Check cache
        cache_key = f"system_metrics_{hours}"
        if (time.time() - self._cache_timestamp < self._cache_ttl and 
            cache_key in self._metrics_cache):
            return self._metrics_cache[cache_key]
        
        recent_queries = self.get_recent_metrics(hours)
        
        if not recent_queries:
            return SystemMetrics(
                period_start=time.time() - (hours * 3600),
                period_end=time.time(),
                total_queries=0,
                successful_queries=0,
                failed_queries=0,
                avg_response_time=0.0,
                avg_search_time=0.0,
                avg_results_per_query=0.0,
                avg_relevance_score=0.0,
                avg_context_optimization_time=0.0,
                avg_context_length=0,
                avg_context_tokens=0,
                avg_generation_time=0.0,
                avg_response_length=0,
                avg_response_tokens=0,
                validation_success_rate=0.0,
                query_complexity_distribution={},
                intent_distribution={},
                peak_memory_usage=0.0,
                avg_memory_usage=0.0,
                cache_hit_rate=0.0
            )
        
        # Calculate metrics
        total_queries = len(recent_queries)
        successful_queries = sum(1 for q in recent_queries if q.response_validation_passed)
        failed_queries = total_queries - successful_queries
        
        # Performance metrics
        response_times = [q.total_time for q in recent_queries]
        search_times = [q.search_time for q in recent_queries]
        context_times = [q.context_optimization_time for q in recent_queries]
        generation_times = [q.generation_time for q in recent_queries]
        
        # Content metrics
        results_per_query = [q.num_results_found for q in recent_queries]
        relevance_scores = [q.avg_relevance_score for q in recent_queries if q.avg_relevance_score > 0]
        context_lengths = [q.context_length for q in recent_queries]
        context_tokens = [q.context_tokens for q in recent_queries]
        response_lengths = [q.response_length for q in recent_queries]
        response_tokens = [q.response_tokens for q in recent_queries]
        
        # Quality distributions
        complexity_dist = defaultdict(int)
        intent_dist = defaultdict(int)
        
        for query in recent_queries:
            complexity_dist[query.query_complexity] += 1
            for intent in query.query_intents:
                intent_dist[intent] += 1
        
        metrics = SystemMetrics(
            period_start=min(q.timestamp for q in recent_queries),
            period_end=max(q.timestamp for q in recent_queries),
            total_queries=total_queries,
            successful_queries=successful_queries,
            failed_queries=failed_queries,
            avg_response_time=statistics.mean(response_times),
            avg_search_time=statistics.mean(search_times),
            avg_results_per_query=statistics.mean(results_per_query),
            avg_relevance_score=statistics.mean(relevance_scores) if relevance_scores else 0.0,
            avg_context_optimization_time=statistics.mean(context_times),
            avg_context_length=int(statistics.mean(context_lengths)),
            avg_context_tokens=int(statistics.mean(context_tokens)),
            avg_generation_time=statistics.mean(generation_times),
            avg_response_length=int(statistics.mean(response_lengths)),
            avg_response_tokens=int(statistics.mean(response_tokens)),
            validation_success_rate=(successful_queries / total_queries) * 100,
            query_complexity_distribution=dict(complexity_dist),
            intent_distribution=dict(intent_dist),
            peak_memory_usage=0.0,  # Would need psutil integration
            avg_memory_usage=0.0,   # Would need psutil integration
            cache_hit_rate=0.0      # Would need cache integration
        )
        
        # Cache result
        self._metrics_cache[cache_key] = metrics
        self._cache_timestamp = time.time()
        
        return metrics
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Gera relatório de performance detalhado"""
        
        system_metrics = self.compute_system_metrics(hours)
        recent_queries = self.get_recent_metrics(hours)
        
        # Component performance
        search_stats = self.search_monitor.get_operation_stats("search", hours * 60)
        context_stats = self.context_monitor.get_operation_stats("context_optimization", hours * 60)
        generation_stats = self.generation_monitor.get_operation_stats("generation", hours * 60)
        
        # Performance trends
        if len(recent_queries) >= 10:
            # Split into buckets for trend analysis
            bucket_size = len(recent_queries) // 5
            buckets = [recent_queries[i:i+bucket_size] for i in range(0, len(recent_queries), bucket_size)]
            
            response_time_trend = [statistics.mean(q.total_time for q in bucket) for bucket in buckets if bucket]
            relevance_trend = [statistics.mean(q.avg_relevance_score for q in bucket if q.avg_relevance_score > 0) 
                             for bucket in buckets if bucket and any(q.avg_relevance_score > 0 for q in bucket)]
        else:
            response_time_trend = []
            relevance_trend = []
        
        # Quality analysis
        quality_issues = []
        
        # Check for performance issues
        if system_metrics.avg_response_time > 10.0:
            quality_issues.append("High average response time")
        
        if system_metrics.validation_success_rate < 90.0:
            quality_issues.append("Low validation success rate")
        
        if system_metrics.avg_relevance_score < 0.6:
            quality_issues.append("Low average relevance score")
        
        # Top performing queries
        top_queries = sorted(recent_queries, key=lambda q: q.avg_relevance_score, reverse=True)[:5]
        
        # Problematic queries
        problematic_queries = [q for q in recent_queries if not q.response_validation_passed or q.total_time > 15.0]
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period_hours": hours,
            "system_metrics": asdict(system_metrics),
            "component_performance": {
                "search": search_stats,
                "context_optimization": context_stats,
                "generation": generation_stats
            },
            "trends": {
                "response_time_trend": response_time_trend,
                "relevance_trend": relevance_trend
            },
            "quality_analysis": {
                "issues_identified": quality_issues,
                "top_performing_queries": [
                    {
                        "query_text": q.query_text[:100] + "..." if len(q.query_text) > 100 else q.query_text,
                        "relevance_score": q.avg_relevance_score,
                        "response_time": q.total_time
                    }
                    for q in top_queries
                ],
                "problematic_queries": [
                    {
                        "query_text": q.query_text[:100] + "..." if len(q.query_text) > 100 else q.query_text,
                        "response_time": q.total_time,
                        "validation_passed": q.response_validation_passed,
                        "issues": []
                    }
                    for q in problematic_queries[:10]
                ]
            },
            "recommendations": self._generate_recommendations(system_metrics, quality_issues)
        }
    
    def _generate_recommendations(self, metrics: SystemMetrics, issues: List[str]) -> List[str]:
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        # Performance recommendations
        if metrics.avg_response_time > 10.0:
            recommendations.append("Consider reducing context size or using a faster model")
        
        if metrics.avg_search_time > 2.0:
            recommendations.append("Optimize search parameters or increase ChromaDB HNSW ef setting")
        
        if metrics.avg_context_optimization_time > 1.0:
            recommendations.append("Consider reducing max_results_per_collection or optimizing context selection")
        
        # Quality recommendations
        if metrics.avg_relevance_score < 0.6:
            recommendations.append("Review embedding quality and reranking strategies")
        
        if metrics.validation_success_rate < 90.0:
            recommendations.append("Review response validation criteria and prompt strategies")
        
        # Resource recommendations
        if metrics.avg_context_tokens > 12000:
            recommendations.append("Consider implementing more aggressive context truncation")
        
        if metrics.total_queries > 0 and metrics.successful_queries / metrics.total_queries < 0.95:
            recommendations.append("Investigate and fix frequent failure causes")
        
        # Usage pattern recommendations
        complexity_dist = metrics.query_complexity_distribution
        if complexity_dist.get("complex", 0) > complexity_dist.get("simple", 0):
            recommendations.append("Consider optimizing for complex queries or providing query simplification")
        
        return recommendations
    
    def export_metrics(self, file_path: str, hours: int = 24):
        """Exporta métricas para arquivo JSON"""
        report = self.generate_performance_report(hours)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Metrics exported to {file_path}")
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Obtém dados para dashboard em tempo real"""
        recent_1h = self.compute_system_metrics(1)
        recent_5m_queries = self.get_recent_metrics(hours=5/60)  # Last 5 minutes
        
        # Current system status
        current_load = len(self.current_query_data)  # Active queries
        
        # Recent performance
        if recent_5m_queries:
            recent_avg_time = statistics.mean(q.total_time for q in recent_5m_queries)
            recent_success_rate = sum(1 for q in recent_5m_queries if q.response_validation_passed) / len(recent_5m_queries) * 100
        else:
            recent_avg_time = 0.0
            recent_success_rate = 100.0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": {
                "active_queries": current_load,
                "uptime_hours": (time.time() - self.session_start) / 3600,
                "recent_avg_response_time": recent_avg_time,
                "recent_success_rate": recent_success_rate
            },
            "hourly_metrics": {
                "total_queries": recent_1h.total_queries,
                "avg_response_time": recent_1h.avg_response_time,
                "avg_relevance_score": recent_1h.avg_relevance_score,
                "validation_success_rate": recent_1h.validation_success_rate
            },
            "alerts": self._check_alerts(recent_1h, recent_5m_queries)
        }
    
    def _check_alerts(self, hourly_metrics: SystemMetrics, recent_queries: List[QueryMetrics]) -> List[Dict[str, Any]]:
        """Verifica condições de alerta"""
        alerts = []
        
        # Performance alerts
        if hourly_metrics.avg_response_time > 15.0:
            alerts.append({
                "type": "performance",
                "severity": "high",
                "message": f"High average response time: {hourly_metrics.avg_response_time:.2f}s",
                "threshold": 15.0,
                "current_value": hourly_metrics.avg_response_time
            })
        
        # Quality alerts
        if hourly_metrics.validation_success_rate < 85.0:
            alerts.append({
                "type": "quality",
                "severity": "medium",
                "message": f"Low validation success rate: {hourly_metrics.validation_success_rate:.1f}%",
                "threshold": 85.0,
                "current_value": hourly_metrics.validation_success_rate
            })
        
        # Relevance alerts
        if hourly_metrics.avg_relevance_score < 0.5:
            alerts.append({
                "type": "relevance",
                "severity": "medium", 
                "message": f"Low average relevance score: {hourly_metrics.avg_relevance_score:.3f}",
                "threshold": 0.5,
                "current_value": hourly_metrics.avg_relevance_score
            })
        
        # Recent failure spike
        if recent_queries and len(recent_queries) >= 5:
            recent_failures = sum(1 for q in recent_queries[-5:] if not q.response_validation_passed)
            if recent_failures >= 3:
                alerts.append({
                    "type": "failure_spike",
                    "severity": "high",
                    "message": f"Multiple recent failures: {recent_failures}/5 queries failed",
                    "threshold": 2,
                    "current_value": recent_failures
                })
        
        return alerts

class RAGMetricsCollector:
    """Collector para integrar métricas com sistemas de monitoramento externos"""
    
    def __init__(self, monitor: RAGMonitor):
        self.monitor = monitor
        self.prometheus_metrics = {}
        
    def get_prometheus_metrics(self) -> str:
        """Retorna métricas no formato Prometheus"""
        metrics = self.monitor.compute_system_metrics(1)
        
        prometheus_lines = [
            f"# HELP rag_queries_total Total number of queries processed",
            f"# TYPE rag_queries_total counter",
            f"rag_queries_total {metrics.total_queries}",
            f"",
            f"# HELP rag_response_time_seconds Average response time",
            f"# TYPE rag_response_time_seconds gauge", 
            f"rag_response_time_seconds {metrics.avg_response_time}",
            f"",
            f"# HELP rag_relevance_score Average relevance score",
            f"# TYPE rag_relevance_score gauge",
            f"rag_relevance_score {metrics.avg_relevance_score}",
            f"",
            f"# HELP rag_validation_success_rate Validation success rate percentage",
            f"# TYPE rag_validation_success_rate gauge",
            f"rag_validation_success_rate {metrics.validation_success_rate}",
        ]
        
        return "\n".join(prometheus_lines)
    
    def get_datadog_metrics(self) -> List[Dict[str, Any]]:
        """Retorna métricas no formato DataDog"""
        metrics = self.monitor.compute_system_metrics(1)
        timestamp = int(time.time())
        
        return [
            {
                "metric": "rag.queries.total",
                "points": [[timestamp, metrics.total_queries]],
                "type": "count"
            },
            {
                "metric": "rag.response_time.avg",
                "points": [[timestamp, metrics.avg_response_time]],
                "type": "gauge"
            },
            {
                "metric": "rag.relevance.avg",
                "points": [[timestamp, metrics.avg_relevance_score]],
                "type": "gauge"
            },
            {
                "metric": "rag.validation.success_rate",
                "points": [[timestamp, metrics.validation_success_rate]],
                "type": "gauge"
            }
        ]

# Context managers para facilitar o uso
@contextmanager
def track_query(monitor: RAGMonitor, query_text: str):
    """Context manager para tracking automático de queries"""
    query_id = f"query_{int(time.time() * 1000)}"
    monitor.start_query_tracking(query_id, query_text)
    
    try:
        yield query_id
    except Exception as e:
        monitor.logger.error(f"Query {query_id} failed: {str(e)}")
        # Mark as failed
        if query_id in monitor.current_query_data:
            monitor.current_query_data[query_id]["response_validation_passed"] = False
        raise
    finally:
        if query_id in monitor.current_query_data:
            monitor.finish_query_tracking(query_id)

@contextmanager  
def track_component_operation(monitor: RAGMonitor, component: str, operation: str, metadata: Optional[Dict] = None):
    """Context manager para tracking de operações de componentes"""
    component_monitor = getattr(monitor, f"{component}_monitor", None)
    if not component_monitor:
        yield
        return
    
    with component_monitor.measure_operation(operation, metadata) as operation_id:
        yield operation_id

# Utility functions
def create_monitoring_setup(log_file: Optional[str] = None) -> RAGMonitor:
    """Cria setup completo de monitoramento"""
    
    # Ensure logs directory exists
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    monitor = RAGMonitor(
        max_stored_queries=2000,
        metrics_window_hours=48,
        log_file=log_file
    )
    
    return monitor

def setup_periodic_reporting(monitor: RAGMonitor, 
                           report_interval_minutes: int = 60,
                           export_path: str = "logs/rag_metrics"):
    """Setup de relatórios periódicos"""
    import threading
    
    def generate_periodic_report():
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"{export_path}__{timestamp}.json"
            monitor.export_metrics(report_file, hours=1)
        except Exception as e:
            monitor.logger.error(f"Failed to generate periodic report: {e}")
        
        # Schedule next report
        timer = threading.Timer(report_interval_minutes * 60, generate_periodic_report)
        timer.daemon = True
        timer.start()
    
    # Start initial report
    timer = threading.Timer(report_interval_minutes * 60, generate_periodic_report)
    timer.daemon = True
    timer.start()
    
    return timer

# Export principais
__all__ = [
    "RAGMonitor",
    "QueryMetrics", 
    "SystemMetrics",
    "PerformanceMonitor",
    "RAGMetricsCollector",
    "track_query",
    "track_component_operation", 
    "create_monitoring_setup",
    "setup_periodic_reporting"
]