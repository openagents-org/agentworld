#!/usr/bin/env node
/**
 * Kaetram API Test Main Runner - JavaScript Version
 */
const { program } = require('commander');
const chalk = require('chalk');
const { TestConfig } = require('../utils/test_utils');
const ServerAPITests = require('./test_server_api');

async function runServerTests(config) {
    console.log(chalk.blue('Running game server API tests...'));
    const tests = new ServerAPITests(config);
    await tests.runAllTests();
    
    return {
        suite_name: 'ServerAPI',
        total_tests: tests.suite.results.length,
        passed_tests: tests.suite.results.filter(r => r.success).length,
        failed_tests: tests.suite.results.filter(r => !r.success).length,
        duration: (tests.suite.endTime - tests.suite.startTime) / 1000
    };
}

function printSummary(results, totalDuration) {
    console.log('\n' + '='.repeat(80));
    console.log(chalk.bold('🎮 Kaetram API Test Summary'));
    console.log('='.repeat(80));
    
    const totalTests = results.reduce((sum, r) => sum + r.total_tests, 0);
    const totalPassed = results.reduce((sum, r) => sum + r.passed_tests, 0);
    const totalFailed = results.reduce((sum, r) => sum + r.failed_tests, 0);
    
    results.forEach(result => {
        const suiteName = result.suite_name.padEnd(20);
        const status = result.failed_tests === 0 ? 
            chalk.green('✅ PASSED') : chalk.red('❌ FAILED');
        const testCount = `${result.passed_tests.toString().padStart(3)}/${result.total_tests.toString().padStart(3)}`;
        const duration = `${result.duration.toFixed(2)}s`.padStart(8);
        
        console.log(`${suiteName} | ${status} | ${testCount} | ${duration}`);
    });
    
    console.log('-'.repeat(80));
    const totalStatus = totalFailed === 0 ? 
        chalk.green('✅ PASSED') : chalk.red('❌ FAILED');
    const totalCount = `${totalPassed.toString().padStart(3)}/${totalTests.toString().padStart(3)}`;
    const totalDur = `${totalDuration.toFixed(2)}s`.padStart(8);
    
    console.log(`${'TOTAL'.padEnd(20)} | ${totalStatus} | ${totalCount} | ${totalDur}`);
    
    if (totalFailed > 0) {
        console.log(chalk.red(`\n⚠️  ${totalFailed} tests failed. Check the logs for details.`));
    } else {
        console.log(chalk.green(`\n🎉 All tests passed! (${totalTests} tests)`));
    }
    
    console.log('='.repeat(80));
}

async function main() {
    program
        .name('kaetram-api-test')
        .description('Kaetram API Test Runner')
        .version('1.0.0')
        .option('--config <file>', 'Configuration file path', 'config.json')
        .option('--server', 'Run only server API tests')
        .option('--hub', 'Run only Hub API tests')
        .option('--ai', 'Run only AI agent workflow tests')
        .option('--verbose', 'Enable verbose output')
        .option('--parallel', 'Run tests in parallel')
        .option('--cleanup', 'Clean up test data after execution')
        .parse();

    const options = program.opts();

    try {
        // Load configuration
        const config = new TestConfig(options.config);
        
        // Determine which tests to run
        let runServer = options.server || (!options.hub && !options.ai);
        let runHub = options.hub || (!options.server && !options.ai);
        let runAi = options.ai || (!options.server && !options.hub);
        
        // If specific tests are requested, only run those
        if (options.server || options.hub || options.ai) {
            runServer = options.server;
            runHub = options.hub;
            runAi = options.ai;
        }

        const results = [];
        const startTime = Date.now();

        console.log(chalk.bold('🚀 Starting Kaetram API Tests'));
        console.log(`Configuration: ${options.config}`);
        console.log(`Server URL: ${config.get('server.base_url')}`);
        console.log(`Hub URL: ${config.get('hub.base_url')}`);
        console.log('-'.repeat(50));

        // Run tests
        if (runServer) {
            console.log(chalk.blue('Running Server API Tests...'));
            try {
                const result = await runServerTests(config);
                results.push(result);
                console.log(chalk.green(`Server API tests completed: ${result.passed_tests}/${result.total_tests} passed`));
            } catch (error) {
                console.error(chalk.red(`Server API tests failed: ${error.message}`));
                results.push({
                    suite_name: 'ServerAPI',
                    total_tests: 0,
                    passed_tests: 0,
                    failed_tests: 1,
                    duration: 0
                });
            }
        }

        if (runHub) {
            console.log(chalk.blue('Running Hub API Tests...'));
            try {
                // Note: Hub tests would be implemented here
                console.log(chalk.yellow('Hub API tests not yet implemented in JavaScript version'));
                results.push({
                    suite_name: 'HubAPI',
                    total_tests: 0,
                    passed_tests: 0,
                    failed_tests: 0,
                    duration: 0
                });
            } catch (error) {
                console.error(chalk.red(`Hub API tests failed: ${error.message}`));
                results.push({
                    suite_name: 'HubAPI',
                    total_tests: 0,
                    passed_tests: 0,
                    failed_tests: 1,
                    duration: 0
                });
            }
        }

        if (runAi) {
            console.log(chalk.blue('Running AI Agent Workflow Tests...'));
            try {
                // Note: AI agent tests would be implemented here
                console.log(chalk.yellow('AI Agent workflow tests not yet implemented in JavaScript version'));
                results.push({
                    suite_name: 'AIAgentFlow',
                    total_tests: 0,
                    passed_tests: 0,
                    failed_tests: 0,
                    duration: 0
                });
            } catch (error) {
                console.error(chalk.red(`AI Agent tests failed: ${error.message}`));
                results.push({
                    suite_name: 'AIAgentFlow',
                    total_tests: 0,
                    passed_tests: 0,
                    failed_tests: 1,
                    duration: 0
                });
            }
        }

        // Calculate total duration
        const totalDuration = (Date.now() - startTime) / 1000;

        // Print summary
        printSummary(results, totalDuration);

        // Save combined report
        const fs = require('fs');
        const path = require('path');
        
        const reportDir = path.join(__dirname, '..', 'test_reports');
        if (!fs.existsSync(reportDir)) {
            fs.mkdirSync(reportDir, { recursive: true });
        }

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const reportFile = path.join(reportDir, `combined_report_${timestamp}.json`);

        fs.writeFileSync(reportFile, JSON.stringify(combinedReport, null, 2));
        console.log(chalk.cyan(`\n📊 Combined report saved to: ${reportFile}`));

        // Exit with error code if any tests failed
        const totalFailed = results.reduce((sum, r) => sum + r.failed_tests, 0);
        if (totalFailed > 0) {
            process.exit(1);
        }

    } catch (error) {
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { runServerTests, printSummary }; 