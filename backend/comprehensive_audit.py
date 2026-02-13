#!/usr/bin/env python3
"""
Comprehensive Audit Script for Days 1, 2, and 3
"""
import os
import sys
from pathlib import Path

print('=' * 80)
print('COMPREHENSIVE AUDIT: DAYS 1, 2, AND 3')
print('=' * 80)

# DAY 1 CHECKS
print('\n[DAY 1] PROJECT SKELETON + DATABASE')
print('-' * 80)

# Check project structure
required_dirs = {
    'app/api': 'API routes',
    'app/core': 'Core config',
    'app/models': 'Database models',
    'app/schemas': 'Pydantic schemas',
    'app/services': 'Business logic',
    'app/integrations': 'Plugin system',
    'app/workers': 'Celery tasks',
    '../frontend/src': 'React frontend',
}

print('\nProject Structure:')
all_dirs_exist = True
for dir_path, desc in required_dirs.items():
    exists = os.path.exists(dir_path)
    status = '[OK]' if exists else '[MISSING]'
    print(f'  {status} {dir_path} ({desc})')
    if not exists:
        all_dirs_exist = False

# Check Docker Compose
docker_compose_exists = os.path.exists('../docker-compose.yml')
print(f'\nDocker Compose:')
print(f'  {"[OK]" if docker_compose_exists else "[MISSING]"} docker-compose.yml exists')

# Check main.py
main_exists = os.path.exists('app/main.py')
print(f'\nBackend Entry Point:')
print(f'  {"[OK]" if main_exists else "[MISSING]"} app/main.py exists')

# Check Alembic
alembic_exists = os.path.exists('alembic.ini') and os.path.exists('alembic/versions')
print(f'\nDatabase Migrations:')
print(f'  {"[OK]" if alembic_exists else "[MISSING]"} Alembic configured')

# Check models
model_files = ['user.py', 'connection.py', 'workflow.py', 'workflow_step.py', 'workflow_run.py', 'step_run.py']
print(f'\nDatabase Models:')
all_models_exist = True
for model_file in model_files:
    exists = os.path.exists(f'app/models/{model_file}')
    status = '[OK]' if exists else '[MISSING]'
    print(f'  {status} {model_file}')
    if not exists:
        all_models_exist = False

# Check schemas
schema_files = ['user.py', 'connection.py', 'workflow.py', 'workflow_step.py', 'workflow_run.py', 'step_run.py']
print(f'\nPydantic Schemas:')
all_schemas_exist = True
for schema_file in schema_files:
    exists = os.path.exists(f'app/schemas/{schema_file}')
    status = '[OK]' if exists else '[MISSING]'
    print(f'  {status} {schema_file}')
    if not exists:
        all_schemas_exist = False

day1_pass = all_dirs_exist and docker_compose_exists and main_exists and alembic_exists and all_models_exist and all_schemas_exist

# DAY 2 CHECKS
print('\n' + '=' * 80)
print('[DAY 2] AUTHENTICATION SYSTEM')
print('-' * 80)

# Check auth endpoints
auth_exists = os.path.exists('app/api/auth.py')
print(f'\nAuth Endpoints:')
print(f'  {"[OK]" if auth_exists else "[MISSING]"} app/api/auth.py exists')

if auth_exists:
    with open('app/api/auth.py', 'r', encoding='utf-8') as f:
        auth_content = f.read()
        has_register = 'register' in auth_content.lower()
        has_login = 'login' in auth_content.lower()
        has_jwt = 'jwt' in auth_content.lower() or 'token' in auth_content.lower()
        
        print(f'  {"[OK]" if has_register else "[MISSING]"} Registration endpoint')
        print(f'  {"[OK]" if has_login else "[MISSING]"} Login endpoint')
        print(f'  {"[OK]" if has_jwt else "[MISSING]"} JWT token generation')

# Check security module
security_exists = os.path.exists('app/core/security.py')
print(f'\nSecurity Module:')
print(f'  {"[OK]" if security_exists else "[MISSING]"} app/core/security.py exists')

if security_exists:
    with open('app/core/security.py', 'r', encoding='utf-8') as f:
        security_content = f.read()
        has_hash = 'hash' in security_content.lower() or 'bcrypt' in security_content.lower()
        has_verify = 'verify' in security_content.lower()
        has_create_token = 'create' in security_content.lower() and 'token' in security_content.lower()
        
        print(f'  {"[OK]" if has_hash else "[MISSING]"} Password hashing')
        print(f'  {"[OK]" if has_verify else "[MISSING]"} Password verification')
        print(f'  {"[OK]" if has_create_token else "[MISSING]"} Token creation')

# Check frontend auth pages
frontend_pages = ['Login.tsx', 'Signup.tsx', 'Dashboard.tsx']
print(f'\nFrontend Auth Pages:')
all_frontend_exist = True
for page in frontend_pages:
    exists = os.path.exists(f'../frontend/src/pages/{page}')
    status = '[OK]' if exists else '[MISSING]'
    print(f'  {status} {page}')
    if not exists:
        all_frontend_exist = False

day2_pass = auth_exists and security_exists and all_frontend_exist

# DAY 3 CHECKS
print('\n' + '=' * 80)
print('[DAY 3] INTEGRATION PLUGIN ARCHITECTURE')
print('-' * 80)

# Check base classes
base_exists = os.path.exists('app/integrations/base.py')
print(f'\nBase Classes:')
print(f'  {"[OK]" if base_exists else "[MISSING]"} app/integrations/base.py exists')

if base_exists:
    with open('app/integrations/base.py', 'r', encoding='utf-8') as f:
        base_content = f.read()
        has_base_action = 'BaseAction' in base_content
        has_base_trigger = 'BaseTrigger' in base_content
        has_integration_def = 'IntegrationDefinition' in base_content
        
        print(f'  {"[OK]" if has_base_action else "[MISSING]"} BaseAction class')
        print(f'  {"[OK]" if has_base_trigger else "[MISSING]"} BaseTrigger class')
        print(f'  {"[OK]" if has_integration_def else "[MISSING]"} IntegrationDefinition class')

# Check registry
registry_exists = os.path.exists('app/integrations/registry.py')
print(f'\nIntegration Registry:')
print(f'  {"[OK]" if registry_exists else "[MISSING]"} app/integrations/registry.py exists')

if registry_exists:
    with open('app/integrations/registry.py', 'r', encoding='utf-8') as f:
        registry_content = f.read()
        has_get_all = 'get_all' in registry_content.lower()
        has_get_integration = 'get_integration' in registry_content.lower()
        has_register = 'register' in registry_content.lower()
        
        print(f'  {"[OK]" if has_get_all else "[MISSING]"} get_all_integrations method')
        print(f'  {"[OK]" if has_get_integration else "[MISSING]"} get_integration method')
        print(f'  {"[OK]" if has_register else "[MISSING]"} register method')

# Check webhook integration
webhook_files = {
    'app/integrations/webhook/__init__.py': 'Init file',
    'app/integrations/webhook/definition.py': 'Definition',
    'app/integrations/webhook/triggers.py': 'Triggers',
    'app/integrations/webhook/actions.py': 'Actions'
}
print(f'\nWebhook Integration:')
all_webhook_exist = True
for file_path, desc in webhook_files.items():
    exists = os.path.exists(file_path)
    status = '[OK]' if exists else '[MISSING]'
    print(f'  {status} {desc}')
    if not exists:
        all_webhook_exist = False

# Check discord integration
discord_files = {
    'app/integrations/discord/__init__.py': 'Init file',
    'app/integrations/discord/definition.py': 'Definition',
    'app/integrations/discord/triggers.py': 'Triggers',
    'app/integrations/discord/actions.py': 'Actions'
}
print(f'\nDiscord Integration:')
all_discord_exist = True
for file_path, desc in discord_files.items():
    exists = os.path.exists(file_path)
    status = '[OK]' if exists else '[MISSING]'
    print(f'  {status} {desc}')
    if not exists:
        all_discord_exist = False

# Check if integrations are registered
if registry_exists:
    print(f'\nIntegration Registration:')
    try:
        sys.path.insert(0, os.path.abspath('.'))
        from app.integrations.registry import registry
        
        all_integrations = registry.get_all_integrations()
        print(f'  [INFO] Total integrations registered: {len(all_integrations)}')
        
        for integration in all_integrations:
            print(f'    - {integration.id}: {integration.name}')
            print(f'      Triggers: {len(integration.triggers)}')
            print(f'      Actions: {len(integration.actions)}')
        
        has_webhook = any(i.id == 'webhook' for i in all_integrations)
        has_discord = any(i.id == 'discord' for i in all_integrations)
        
        print(f'  {"[OK]" if has_webhook else "[MISSING]"} Webhook integration registered')
        print(f'  {"[OK]" if has_discord else "[MISSING]"} Discord integration registered')
    except Exception as e:
        print(f'  [ERROR] Failed to load registry: {e}')

day3_pass = base_exists and registry_exists and all_webhook_exist and all_discord_exist

# FINAL SUMMARY
print('\n' + '=' * 80)
print('FINAL AUDIT RESULTS')
print('=' * 80)
print(f'\nDAY 1 - Project Skeleton + Database: {"[PASS]" if day1_pass else "[FAIL]"}')
print(f'DAY 2 - Authentication System:       {"[PASS]" if day2_pass else "[FAIL]"}')
print(f'DAY 3 - Integration Architecture:    {"[PASS]" if day3_pass else "[FAIL]"}')

if day1_pass and day2_pass and day3_pass:
    print(f'\n*** ALL DAYS COMPLETE! ***\n')
    sys.exit(0)
else:
    print(f'\n*** SOME REQUIREMENTS MISSING ***\n')
    sys.exit(1)
