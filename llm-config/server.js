const express = require('express');
const cors = require('cors');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const CONFIG_PATH = path.join(__dirname, '..', '.llm_settings.json');

app.use(cors());
app.use(express.json());
app.use(express.static('.'));

let config = {
    base_url: '',
    api_key: '',
    model: ''
};

function loadConfig() {
    try {
        if (fs.existsSync(CONFIG_PATH)) {
            const data = fs.readFileSync(CONFIG_PATH, 'utf-8');
            config = JSON.parse(data);
            console.log('✅ LLM配置已加载');
            console.log(`   Base URL: ${config.base_url}`);
            console.log(`   Model: ${config.model}`);
            return true;
        } else {
            console.log('⚠️ 配置文件不存在: ' + CONFIG_PATH);
            return false;
        }
    } catch (e) {
        console.error('❌ 加载配置失败:', e.message);
        return false;
    }
}

loadConfig();

app.get('/api/config', (req, res) => {
    if (config.api_key && config.base_url && config.model) {
        res.json({
            configured: true,
            base_url: config.base_url,
            model: config.model
        });
    } else {
        res.json({
            configured: false,
            error: '缺少必要配置项'
        });
    }
});

app.post('/api/config/reload', (req, res) => {
    loadConfig();
    res.json({ status: 'ok' });
});

app.post('/api/chat', async (req, res) => {
    try {
        const { messages } = req.body;

        if (!config.api_key || !config.base_url || !config.model) {
            return res.status(400).json({
                error: {
                    message: 'LLM未配置。请在配置文件 .llm_settings.json 中设置 base_url、api_key 和 model',
                    type: 'configuration_error'
                }
            });
        }

        const endpoint = config.base_url.replace(/\/$/, '') + '/chat/completions';

        const response = await axios.post(endpoint, {
            model: config.model,
            messages,
            temperature: 0.7
        }, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.api_key}`
            },
            timeout: 60000
        });

        res.json(response.data);
    } catch (error) {
        console.error('API Error:', error.message);

        if (error.response) {
            return res.status(error.response.status).json({
                error: {
                    message: error.response.data?.error?.message || error.message,
                    type: error.response.data?.error?.type || 'api_error'
                }
            });
        }

        res.status(500).json({
            error: {
                message: error.message || '服务器内部错误',
                type: 'server_error'
            }
        });
    }
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        configured: !!(config.api_key && config.base_url && config.model),
        timestamp: Date.now()
    });
});

app.listen(PORT, () => {
    console.log(`🚀 LLM代理服务已启动: http://localhost:${PORT}`);
    console.log(`📝 配置文件: ${CONFIG_PATH}`);
    if (config.api_key && config.base_url && config.model) {
        console.log(`✅ LLM配置已就绪`);
    } else {
        console.log(`⚠️ 请配置 .llm_settings.json 文件`);
    }
});
