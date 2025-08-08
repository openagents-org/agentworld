#!/usr/bin/env python3
"""
Kaetram AI Agent Benchmark Runner
AI代理能力基准测试运行器
"""

import time
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .scenarios import ScenarioManager
from .evaluators import EvaluatorSuite
from .metrics import MetricsCollector
from .reports import ReportGenerator
from ..utils.test_utils import TestConfig, Logger, APIClient


@dataclass
class BenchmarkConfig:
    """基准测试配置"""
    agent_id: str
    test_environment: str = "local"
    scenarios: List[str] = None
    time_limit: int = 300  # 5分钟默认限制
    parallel_tests: bool = False
    detailed_logging: bool = True
    auto_cleanup: bool = True


class BenchmarkResult:
    """基准测试结果"""
    
    def __init__(self, agent_id: str, session_id: str):
        self.agent_id = agent_id
        self.session_id = session_id
        self.start_time = datetime.now()
        self.end_time = None
        self.scenarios = {}
        self.metrics = {
            'basic_operations': 0.0,
            'combat_capability': 0.0, 
            'resource_management': 0.0,
            'skill_development': 0.0,
            'social_interaction': 0.0,
            'adaptability': 0.0
        }
        self.overall_score = 0.0
        self.rating = 'D'
        self.detailed_logs = []
        
    def add_scenario_result(self, scenario_name: str, result: Dict[str, Any]):
        """添加场景测试结果"""
        self.scenarios[scenario_name] = result
        
    def calculate_final_score(self):
        """计算最终得分"""
        weights = {
            'basic_operations': 0.20,
            'combat_capability': 0.25,
            'resource_management': 0.20,
            'skill_development': 0.15,
            'social_interaction': 0.10,
            'adaptability': 0.10
        }
        
        self.overall_score = sum(
            self.metrics[key] * weights[key] 
            for key in weights.keys()
        )
        
        # 确定评级
        if self.overall_score >= 90:
            self.rating = 'S'
        elif self.overall_score >= 80:
            self.rating = 'A'
        elif self.overall_score >= 70:
            self.rating = 'B'
        elif self.overall_score >= 60:
            self.rating = 'C'
        else:
            self.rating = 'D'
            
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'agent_id': self.agent_id,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'scenarios': self.scenarios,
            'metrics': self.metrics,
            'overall_score': self.overall_score,
            'rating': self.rating,
            'detailed_logs': self.detailed_logs
        }


class BenchmarkRunner:
    """基准测试运行器"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.logger = Logger("BenchmarkRunner")
        self.api_client = APIClient(TestConfig())
        
        # 初始化组件
        self.scenario_manager = ScenarioManager()
        self.evaluator_suite = EvaluatorSuite()
        self.metrics_collector = MetricsCollector()
        self.report_generator = ReportGenerator()
        
        # 创建输出目录
        self.output_dir = Path(f"benchmark_results/{self.config.agent_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def run_benchmark(self) -> BenchmarkResult:
        """运行完整的基准测试"""
        session_id = f"bench_{int(time.time())}"
        result = BenchmarkResult(self.config.agent_id, session_id)
        
        self.logger.info(f"开始为Agent {self.config.agent_id} 运行基准测试")
        self.logger.info(f"会话ID: {session_id}")
        
        try:
            # 环境初始化
            await self._setup_environment()
            
            # 运行测试场景
            scenarios = self.config.scenarios or [
                'beginner_tutorial',
                'survival_challenge', 
                'team_dungeon',
                'economic_simulation'
            ]
            
            for scenario_name in scenarios:
                self.logger.info(f"运行场景: {scenario_name}")
                scenario_result = await self._run_scenario(scenario_name)
                result.add_scenario_result(scenario_name, scenario_result)
                
                # 更新指标
                self._update_metrics(result, scenario_result)
                
            # 计算最终得分
            result.calculate_final_score()
            result.end_time = datetime.now()
            
            # 生成报告
            await self._generate_reports(result)
            
            self.logger.info(f"基准测试完成! 最终得分: {result.overall_score:.2f} (等级: {result.rating})")
            
        except Exception as e:
            self.logger.error(f"基准测试失败: {str(e)}")
            result.detailed_logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'ERROR',
                'message': f"测试失败: {str(e)}"
            })
        finally:
            # 清理环境
            if self.config.auto_cleanup:
                await self._cleanup_environment()
                
        return result
        
    async def _setup_environment(self):
        """设置测试环境"""
        self.logger.info("初始化测试环境...")
        
        # 检查服务器状态
        server_info = await self.api_client.get_server_info()
        if not server_info:
            raise Exception("无法连接到游戏服务器")
            
        # 创建测试用AI代理
        agent_data = await self.api_client.create_ai_agent(
            self.config.agent_id,
            f"password_{self.config.agent_id}"
        )
        
        if not agent_data:
            raise Exception("无法创建AI代理")
            
        self.logger.info("测试环境初始化完成")
        
    async def _run_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """运行单个测试场景"""
        scenario = self.scenario_manager.get_scenario(scenario_name)
        if not scenario:
            raise Exception(f"未找到场景: {scenario_name}")
            
        start_time = time.time()
        
        try:
            # 执行场景
            scenario_result = await scenario.execute(
                self.api_client, 
                self.config.agent_id,
                self.metrics_collector
            )
            
            # 评估结果
            evaluation = await self.evaluator_suite.evaluate_scenario(
                scenario_name, 
                scenario_result
            )
            
            execution_time = time.time() - start_time
            
            return {
                'scenario_name': scenario_name,
                'execution_time': execution_time,
                'status': 'completed',
                'raw_results': scenario_result,
                'evaluation': evaluation,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"场景 {scenario_name} 执行失败: {str(e)}")
            
            return {
                'scenario_name': scenario_name,
                'execution_time': execution_time,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _update_metrics(self, result: BenchmarkResult, scenario_result: Dict[str, Any]):
        """更新性能指标"""
        if scenario_result['status'] != 'completed':
            return
            
        evaluation = scenario_result['evaluation']
        scenario_name = scenario_result['scenario_name']
        
        # 根据场景类型更新相应指标
        if scenario_name == 'beginner_tutorial':
            result.metrics['basic_operations'] = evaluation.get('score', 0)
        elif scenario_name == 'survival_challenge':
            result.metrics['resource_management'] = evaluation.get('score', 0)
            result.metrics['adaptability'] = evaluation.get('adaptability_score', 0)
        elif scenario_name == 'team_dungeon':
            result.metrics['combat_capability'] = evaluation.get('score', 0)
            result.metrics['social_interaction'] = evaluation.get('teamwork_score', 0)
        elif scenario_name == 'economic_simulation':
            result.metrics['skill_development'] = evaluation.get('score', 0)
            
    async def _generate_reports(self, result: BenchmarkResult):
        """生成测试报告"""
        self.logger.info("生成测试报告...")
        
        # JSON报告
        json_report = result.to_dict()
        json_path = self.output_dir / f"benchmark_report_{result.session_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, ensure_ascii=False, indent=2)
            
        # HTML报告
        html_report = await self.report_generator.generate_html_report(result)
        html_path = self.output_dir / f"benchmark_report_{result.session_id}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
            
        # 简要控制台报告
        self._print_summary_report(result)
        
        self.logger.info(f"报告已生成: {json_path}, {html_path}")
        
    def _print_summary_report(self, result: BenchmarkResult):
        """打印简要报告到控制台"""
        print("\n" + "="*60)
        print(f"AI Agent基准测试报告 - {result.agent_id}")
        print("="*60)
        print(f"测试会话: {result.session_id}")
        print(f"总体评级: {result.rating}")
        print(f"总体得分: {result.overall_score:.2f}/100")
        print("\n详细指标:")
        
        metric_names = {
            'basic_operations': '基础操作',
            'combat_capability': '战斗能力',
            'resource_management': '资源管理',
            'skill_development': '技能发展',
            'social_interaction': '社交互动',
            'adaptability': '适应性'
        }
        
        for key, value in result.metrics.items():
            name = metric_names.get(key, key)
            print(f"  {name}: {value:.2f}/100")
            
        print(f"\n场景完成情况:")
        for scenario_name, scenario_result in result.scenarios.items():
            status = "✅" if scenario_result['status'] == 'completed' else "❌"
            print(f"  {scenario_name}: {status}")
            
        print("="*60)
        
    async def _cleanup_environment(self):
        """清理测试环境"""
        self.logger.info("清理测试环境...")
        try:
            # 注销AI代理
            await self.api_client.logout_ai_agent(self.config.agent_id)
            self.logger.info("环境清理完成")
        except Exception as e:
            self.logger.warning(f"环境清理警告: {str(e)}")


async def main():
    """主函数 - 示例用法"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kaetram AI Agent Benchmark')
    parser.add_argument('--agent-id', required=True, help='AI代理ID')
    parser.add_argument('--scenarios', nargs='+', help='要运行的场景')
    parser.add_argument('--time-limit', type=int, default=300, help='时间限制(秒)')
    parser.add_argument('--environment', default='local', help='测试环境')
    
    args = parser.parse_args()
    
    config = BenchmarkConfig(
        agent_id=args.agent_id,
        test_environment=args.environment,
        scenarios=args.scenarios,
        time_limit=args.time_limit
    )
    
    runner = BenchmarkRunner(config)
    result = await runner.run_benchmark()
    
    print(f"\n基准测试完成! 查看完整报告: benchmark_results/{config.agent_id}/")


if __name__ == "__main__":
    asyncio.run(main()) 