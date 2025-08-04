// MongoDB初始化脚本
db = db.getSiblingDB('agent_system');

// 创建用户
db.createUser({
    user: 'agent_user',
    pwd: 'agent_password',
    roles: [
        {
            role: 'readWrite',
            db: 'agent_system'
        }
    ]
});

// 创建集合
db.createCollection('users');
db.createCollection('agents');
db.createCollection('conversations');
db.createCollection('messages');
db.createCollection('plugins');
db.createCollection('workflows');
db.createCollection('models');
db.createCollection('knowledge_bases');
db.createCollection('knowledge_documents');
db.createCollection('training_history');
db.createCollection('dashboard_stats');
db.createCollection('activities');

print('MongoDB初始化完成'); 