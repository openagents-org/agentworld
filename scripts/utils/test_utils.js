/**
 * Kaetram API Test Utility Functions - JavaScript Version
 */
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const chalk = require('chalk');
const { table } = require('table');
const winston = require('winston');

class TestConfig {
    constructor(configFile = 'config.json') {
        this.configPath = path.join(__dirname, '..', configFile);
        this.config = this.loadConfig();
    }

    loadConfig() {
        try {
            const configData = fs.readFileSync(this.configPath, 'utf8');
            return JSON.parse(configData);
        } catch (error) {
            if (error.code === 'ENOENT') {
                throw new Error(`Configuration file ${this.configPath} not found`);
            }
            throw new Error(`Configuration file format error: ${error.message}`);
        }
    }

    get(key, defaultValue = null) {
        const keys = key.split('.');
        let value = this.config;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }
        
        return value;
    }
}

class Logger {
    constructor(config) {
        this.config = config;
        this.logger = this.setupLogger();
    }

    setupLogger() {
        const logger = winston.createLogger({
            level: this.config.get('logging.level', 'info'),
            format: winston.format.combine(
                winston.format.timestamp(),
                winston.format.colorize(),
                winston.format.printf(({ timestamp, level, message }) => {
                    return `${timestamp} - ${level}: ${message}`;
                })
            ),
            transports: []
        });

        // Console transport
        if (this.config.get('logging.console', true)) {
            logger.add(new winston.transports.Console());
        }

        // File transport
        const logFile = this.config.get('logging.file', 'test_reports/test.log');
        const logDir = path.dirname(logFile);
        
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        
        logger.add(new winston.transports.File({ 
            filename: logFile,
            format: winston.format.combine(
                winston.format.timestamp(),
                winston.format.uncolorize(),
                winston.format.json()
            )
        }));

        return logger;
    }

    info(message) {
        this.logger.info(message);
    }

    error(message) {
        this.logger.error(message);
    }

    warning(message) {
        this.logger.warn(message);
    }

    debug(message) {
        this.logger.debug(message);
    }
}

class APIClient {
    constructor(config, logger) {
        this.config = config;
        this.logger = logger;
        this.timeout = config.get('test_settings.timeout', 30000);
        
        // Setup axios instance
        this.client = axios.create({
            timeout: this.timeout,
            headers: {
                'User-Agent': 'Kaetram-API-Test/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
    }

    async get(url, options = {}) {
        this.logger.debug(`GET ${url}`);
        return await this.client.get(url, options);
    }

    async post(url, options = {}) {
        this.logger.debug(`POST ${url}`);
        return await this.client.post(url, options.data, options);
    }

    async put(url, options = {}) {
        this.logger.debug(`PUT ${url}`);
        return await this.client.put(url, options.data, options);
    }

    async delete(url, options = {}) {
        this.logger.debug(`DELETE ${url}`);
        return await this.client.delete(url, options);
    }
}

class TestResult {
    constructor(testName, success, message, data = null, duration = 0) {
        this.testName = testName;
        this.success = success;
        this.message = message;
        this.data = data;
        this.duration = duration;
        this.timestamp = new Date();
    }

    toObject() {
        return {
            testName: this.testName,
            success: this.success,
            message: this.message,
            data: this.data,
            duration: this.duration,
            timestamp: this.timestamp.toISOString()
        };
    }
}

class TestSuite {
    constructor(suiteName, config) {
        this.suiteName = suiteName;
        this.config = config;
        this.logger = new Logger(config);
        this.client = new APIClient(config, this.logger);
        this.results = [];
        this.startTime = null;
        this.endTime = null;
    }

    async runTest(testName, testFunc) {
        this.logger.info(`Running test: ${testName}`);
        const startTime = Date.now();

        try {
            const result = await testFunc();
            const duration = Date.now() - startTime;
            
            const testResult = new TestResult(
                testName,
                true,
                'Test passed',
                result,
                duration
            );
            
            this.logger.info(`Test ${testName} passed in ${duration}ms`);
            this.results.push(testResult);
            return testResult;
            
        } catch (error) {
            const duration = Date.now() - startTime;
            
            const testResult = new TestResult(
                testName,
                false,
                error.message,
                null,
                duration
            );
            
            this.logger.error(`Test ${testName} failed in ${duration}ms: ${error.message}`);
            this.results.push(testResult);
            return testResult;
        }
    }

    generateReport() {
        if (!this.startTime) {
            return {};
        }

        const totalDuration = this.endTime ? (this.endTime - this.startTime) : 0;
        const passedTests = this.results.filter(r => r.success);
        const failedTests = this.results.filter(r => !r.success);

        return {
            suiteName: this.suiteName,
            totalTests: this.results.length,
            passedTests: passedTests.length,
            failedTests: failedTests.length,
            successRate: this.results.length > 0 ? (passedTests.length / this.results.length * 100) : 0,
            totalDuration: totalDuration,
            startTime: this.startTime,
            endTime: this.endTime,
            results: this.results.map(r => r.toObject())
        };
    }

    saveReport(outputFile = null) {
        if (!outputFile) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            outputFile = path.join('test_reports', `${this.suiteName}_${timestamp}.json`);
        }

        const outputDir = path.dirname(outputFile);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        const report = this.generateReport();
        
        fs.writeFileSync(outputFile, JSON.stringify(report, null, 2));
        this.logger.info(`Test report saved to ${outputFile}`);
    }

    printSummary() {
        if (this.results.length === 0) {
            console.log('No tests have been run');
            return;
        }

        const report = this.generateReport();
        
        console.log('\n' + '='.repeat(60));
        console.log(chalk.bold(`Test Suite: ${this.suiteName}`));
        console.log('='.repeat(60));
        
        // Summary table
        const tableData = [];
        const headers = ['Test Name', 'Status', 'Duration', 'Message'];
        
        for (const result of this.results) {
            const status = result.success ? chalk.green('✅ PASS') : chalk.red('❌ FAIL');
            const duration = `${result.duration}ms`;
            const message = result.message.length > 50 ? result.message.substring(0, 50) + '...' : result.message;
            
            tableData.push([result.testName, status, duration, message]);
        }
        
        console.log(table([headers, ...tableData]));
        
        // Summary statistics
        console.log('\nSummary:');
        console.log(`Total Tests: ${report.totalTests}`);
        console.log(`Passed: ${chalk.green(report.passedTests)}`);
        console.log(`Failed: ${chalk.red(report.failedTests)}`);
        console.log(`Success Rate: ${report.successRate.toFixed(1)}%`);
        console.log(`Total Duration: ${report.totalDuration}ms`);
    }
}

// Utility functions
function validateResponse(response) {
    if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}: ${response.data}`);
    }
    
    return response.data;
}

function generateTestUsername(prefix = 'test') {
    const timestamp = Date.now();
    return `${prefix}_${timestamp}`;
}

async function cleanupTestAgents(config, tokens) {
    if (!tokens || tokens.length === 0) {
        return;
    }
    
    const logger = new Logger(config);
    const client = new APIClient(config, logger);
    const baseUrl = config.get('server.base_url');
    
    for (const token of tokens) {
        try {
            const response = await client.post(`${baseUrl}/ai/logout`, {
                data: { token }
            });
            
            if (response.status === 200) {
                logger.info(`Successfully logged out token: ${token.substring(0, 10)}...`);
            } else {
                logger.warning(`Failed to logout token: ${token.substring(0, 10)}...`);
            }
        } catch (error) {
            logger.error(`Error during cleanup: ${error.message}`);
        }
    }
}

async function retryOperation(operation, maxRetries = 3, delay = 1000) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await operation();
        } catch (error) {
            if (attempt === maxRetries - 1) {
                throw error;
            }
            await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt)));
        }
    }
}

async function waitForCondition(condition, timeout = 10000, interval = 500) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
        if (await condition()) {
            return true;
        }
        await new Promise(resolve => setTimeout(resolve, interval));
    }
    
    return false;
}

module.exports = {
    TestConfig,
    Logger,
    APIClient,
    TestResult,
    TestSuite,
    validateResponse,
    generateTestUsername,
    cleanupTestAgents,
    retryOperation,
    waitForCondition
}; 