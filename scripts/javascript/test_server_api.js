#!/usr/bin/env node
/**
 * Kaetram Game Server API Test Script - JavaScript Version
 */
const path = require('path');
const { TestConfig, TestSuite, validateResponse, cleanupTestAgents, generateTestUsername } = require('../utils/test_utils');

class ServerAPITests {
    constructor(config) {
        this.config = config;
        this.suite = new TestSuite('ServerAPI', config);
        this.baseUrl = config.get('server.base_url');
        this.testTokens = [];
    }

    async testServerInfo() {
        const response = await this.suite.client.get(`${this.baseUrl}/`);
        const data = validateResponse(response);

        // Validate returned fields
        const requiredFields = ['name', 'port', 'gameVersion', 'maxPlayers', 'playerCount'];
        for (const field of requiredFields) {
            if (!(field in data)) {
                throw new Error(`Missing required field: ${field}`);
            }
        }

        return data;
    }

    async testAICreateAgent() {
        const username = generateTestUsername();
        const password = 'testpass123';

        const response = await this.suite.client.post(`${this.baseUrl}/ai/create`, {
            data: { username, password }
        });
        const data = validateResponse(response);

        if (data.status !== 'success') {
            throw new Error(`Agent creation failed: ${data.message || 'Unknown error'}`);
        }

        if (!data.token) {
            throw new Error('Missing token field in response');
        }

        // Save token for cleanup
        this.testTokens.push(data.token);

        return { username, password, token: data.token };
    }

    async testAILogin() {
        // First create an agent
        const agentData = await this.testAICreateAgent();

        const response = await this.suite.client.post(`${this.baseUrl}/ai/login`, {
            data: {
                username: agentData.username,
                password: agentData.password
            }
        });
        const data = validateResponse(response);

        if (data.status !== 'success') {
            throw new Error(`Login failed: ${data.message || 'Unknown error'}`);
        }

        if (!data.token) {
            throw new Error('Missing token field in response');
        }

        // Update token
        this.testTokens.push(data.token);

        return { token: data.token };
    }

    async testAILogout() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        const response = await this.suite.client.post(`${this.baseUrl}/ai/logout`, {
            data: { token }
        });
        const data = validateResponse(response);

        if (data.status !== 'success') {
            throw new Error(`Logout failed: ${data.message || 'Unknown error'}`);
        }

        // Remove token from cleanup list
        const tokenIndex = this.testTokens.indexOf(token);
        if (tokenIndex > -1) {
            this.testTokens.splice(tokenIndex, 1);
        }

        return data;
    }

    async testAIMove() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test movement
        const response = await this.suite.client.post(`${this.baseUrl}/ai/move`, {
            data: {
                token,
                x: 100,
                y: 100
            }
        });
        const data = validateResponse(response);

        if (data.status !== 'success') {
            throw new Error(`Movement failed: ${data.message || 'Unknown error'}`);
        }

        return data;
    }

    async testAIStop() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test stop
        const response = await this.suite.client.post(`${this.baseUrl}/ai/stop`, {
            data: { token }
        });
        const data = validateResponse(response);

        if (data.status !== 'success') {
            throw new Error(`Stop failed: ${data.message || 'Unknown error'}`);
        }

        return data;
    }

    async testAIChat() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test chat
        const response = await this.suite.client.post(`${this.baseUrl}/ai/chat`, {
            data: {
                token,
                message: 'Hello, this is a test message!'
            }
        });
        const data = validateResponse(response);

        if (data.status !== 'success') {
            throw new Error(`Chat failed: ${data.message || 'Unknown error'}`);
        }

        return data;
    }

    async testAIObserve() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test observe
        const response = await this.suite.client.get(`${this.baseUrl}/ai/observe`, {
            params: { token }
        });
        const data = validateResponse(response);

        // Validate response structure
        const expectedFields = ['location', 'map', 'entities', 'inventory', 'player'];
        for (const field of expectedFields) {
            if (!(field in data)) {
                throw new Error(`Missing expected field in observation: ${field}`);
            }
        }

        return data;
    }

    async testAIAttack() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test attack (using a test target ID)
        const response = await this.suite.client.post(`${this.baseUrl}/ai/attack`, {
            data: {
                token,
                target: 'test_target_id'
            }
        });
        const data = validateResponse(response);

        // Attack may fail due to no target, but should still return valid response
        if (!['success', 'error'].includes(data.status)) {
            throw new Error(`Invalid attack response: ${JSON.stringify(data)}`);
        }

        return data;
    }

    async testAIEquip() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test equip (using a test item index)
        const response = await this.suite.client.post(`${this.baseUrl}/ai/equip`, {
            data: {
                token,
                index: 0
            }
        });
        const data = validateResponse(response);

        // Equip may fail due to no item, but should still return valid response
        if (!['success', 'error'].includes(data.status)) {
            throw new Error(`Invalid equip response: ${JSON.stringify(data)}`);
        }

        return data;
    }

    async testAICollect() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test collect (using a test resource ID)
        const response = await this.suite.client.post(`${this.baseUrl}/ai/collect`, {
            data: {
                token,
                resource: 'test_resource_id'
            }
        });
        const data = validateResponse(response);

        // Collect may fail due to no resource, but should still return valid response
        if (!['success', 'error'].includes(data.status)) {
            throw new Error(`Invalid collect response: ${JSON.stringify(data)}`);
        }

        return data;
    }

    async testAICraft() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test craft (using a test item key)
        const response = await this.suite.client.post(`${this.baseUrl}/ai/craft`, {
            data: {
                token,
                item: 'test_item_key'
            }
        });
        const data = validateResponse(response);

        // Craft may fail due to no materials, but should still return valid response
        if (!['success', 'error'].includes(data.status)) {
            throw new Error(`Invalid craft response: ${JSON.stringify(data)}`);
        }

        return data;
    }

    async testAIEnter() {
        // First login
        const loginData = await this.testAILogin();
        const token = loginData.token;

        // Test enter (portal/warp)
        const response = await this.suite.client.post(`${this.baseUrl}/ai/enter`, {
            data: { token }
        });
        const data = validateResponse(response);

        // Enter may fail due to no portal, but should still return valid response
        if (!['success', 'error'].includes(data.status)) {
            throw new Error(`Invalid enter response: ${JSON.stringify(data)}`);
        }

        return data;
    }

    async runAllTests() {
        this.suite.startTime = Date.now();

        // Define test methods
        const testMethods = [
            ['server_info', () => this.testServerInfo()],
            ['ai_create_agent', () => this.testAICreateAgent()],
            ['ai_login', () => this.testAILogin()],
            ['ai_logout', () => this.testAILogout()],
            ['ai_move', () => this.testAIMove()],
            ['ai_stop', () => this.testAIStop()],
            ['ai_chat', () => this.testAIChat()],
            ['ai_observe', () => this.testAIObserve()],
            ['ai_attack', () => this.testAIAttack()],
            ['ai_equip', () => this.testAIEquip()],
            ['ai_collect', () => this.testAICollect()],
            ['ai_craft', () => this.testAICraft()],
            ['ai_enter', () => this.testAIEnter()]
        ];

        // Run each test
        for (const [testName, testFunc] of testMethods) {
            try {
                await this.suite.runTest(testName, testFunc);
            } catch (error) {
                this.suite.logger.error(`Error running test ${testName}: ${error.message}`);
            }
        }

        this.suite.endTime = Date.now();

        // Cleanup
        if (this.testTokens.length > 0) {
            await cleanupTestAgents(this.config, this.testTokens);
        }

        // Generate report
        this.suite.saveReport();
        this.suite.printSummary();
    }
}

async function main() {
    try {
        const config = new TestConfig();
        const tests = new ServerAPITests(config);
        await tests.runAllTests();
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = ServerAPITests; 